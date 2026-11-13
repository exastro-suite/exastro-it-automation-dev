#   Copyright 2026 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Path Traversal 対策のユニットテスト（Ansible実行結果 受信API）

対象:
    - libs.ansible_execution.create_file_path
    - libs.ansible_execution.create_file_path_aap

検証手順2.md の検証3に対応。
"""
import io
import json
import os
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from common_libs.common.exception import AppException
from libs import ansible_execution


# --------------------------------------------------------------------------
# 共通フィクスチャ / ヘルパー
# --------------------------------------------------------------------------
@pytest.fixture
def app_ctx(monkeypatch):
    # テスト用のFlaskアプリケーションコンテキストを用意する。
    #   - g.applogger / g.appmsg はMagicMockに差し替え（メッセージは「ID:引数」の文字列で返す）
    #   - storage_base() もMagicMockに差し替え、ディスク空き容量チェックは常にOKとする
    #   → DB・ストレージ・Platformには接続しない
    app = Flask(__name__)
    with app.app_context():
        g.applogger = MagicMock()
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda msg_id, args=None: f"{msg_id}:{args}"

        storage = MagicMock()
        storage.validate_disk_space.return_value = (True, 1024 ** 3)
        monkeypatch.setattr(ansible_execution, "storage_base", lambda: storage)

        yield app


def _all_files(root):
    # root配下の全ファイルのパス一覧を返す（「何もファイルが作られていないこと」の確認用）
    return sorted(
        os.path.join(d, f) for d, _, files in os.walk(str(root)) for f in files)


def _post(app, file_key, file_name, driver_id="legacy", content=b"payload"):
    # 実行結果受信APIへの multipart/form-data のPOSTリクエストコンテキストを作る
    #   file_key : ファイルのパート名（例: out_tar_data）
    #   file_name: アップロードファイルの filename（Path Traversal 文字列を指定する対象）
    data = {
        "json_parameters": json.dumps({"driver_id": driver_id, "status": "11"}),
        file_key: (io.BytesIO(content), file_name),
    }
    return app.test_request_context(
        "/result_data", method="POST", data=data, content_type="multipart/form-data",
        headers={"Content-Length": str(len(content))})


class TestCreateFilePath:
    """libs.ansible_execution.create_file_path"""

    def test_normal(self, app_ctx, tmp_path):
        # 【正常系】通常のファイル名(out.tar.gz)の場合、
        #   {base}/driver/ansible/{driver_id}/{execution_no}/out.tar.gz に保存され、
        #   戻り値(ret=True, file_paths)と保存内容が期待通りであること
        with _post(app_ctx, "out_tar_data", "out.tar.gz") as ctx:
            ret, parameters, file_paths = ansible_execution.create_file_path(
                ctx.request, str(tmp_path), "exec-no-1")

        expected = os.path.join(str(tmp_path), "driver", "ansible", "legacy", "exec-no-1", "out.tar.gz")
        assert ret is True
        assert file_paths == {"out_tar_data": expected}
        assert open(expected, "rb").read() == b"payload"

    # 【異常系】filename に不正なパス要素を含むケースを網羅する
    #   to_tmp      : ../ を辿って /tmp など保存先の外へ出ようとする
    #   to_code_dir : ../ を辿ってアプリのコードディレクトリを上書きしようとする
    #   nested      : "/" を含むサブディレクトリ指定
    #   bare_dotdot : ".." のみ
    @pytest.mark.parametrize(
        "file_name",
        [
            "../../../../../../tmp/poc.txt",
            "../../../../exastro/config.py",
            "a/b.txt",
            "..",
        ],
        ids=["to_tmp", "to_code_dir", "nested", "bare_dotdot"],
    )
    def test_malicious_filename_is_rejected(self, app_ctx, tmp_path, file_name):
        """filename にパス要素を含めても AppException(499-00201) で拒否され、何も作られない"""
        with _post(app_ctx, "out_tar_data", file_name) as ctx:
            with pytest.raises(AppException) as e:
                ansible_execution.create_file_path(ctx.request, str(tmp_path), "exec-no-1")

        assert e.value.args[0] == "499-00201"
        assert _all_files(tmp_path) == []


class TestCreateFilePathAap:
    """libs.ansible_execution.create_file_path_aap"""

    def test_normal(self, app_ctx, tmp_path):
        # 【正常系】通常のファイル名(out.tar.gz)の場合、
        #   {base}/driver/ansible/{driver_id}/{execution_no}_{作業ID}/out.tar.gz に保存され、
        #   戻り値(ret=True, file_paths)と保存内容が期待通りであること（AAP向け）
        content = b"payload"
        with app_ctx.test_request_context(
                "/result_data", method="POST",
                data={"out_tar_data": (io.BytesIO(content), "out.tar.gz")},
                content_type="multipart/form-data",
                headers={"Content-Length": str(len(content))}) as ctx:
            ret, parameters, file_paths = ansible_execution.create_file_path_aap(
                ctx.request, str(tmp_path), "exec-no-1", "legacy", "ab12")

        expected = os.path.join(str(tmp_path), "driver", "ansible", "legacy", "exec-no-1_ab12", "out.tar.gz")
        assert ret is True
        assert file_paths == {"out_tar_data": expected}
        assert open(expected, "rb").read() == b"payload"

    # 【異常系】AAP向けでも、filename に不正なパス要素(../ や "/" や "..")を含む場合は
    #   AppException(499-00201) で拒否され、ファイルが一切作られないこと
    @pytest.mark.parametrize(
        "file_name",
        [
            "../../../../tmp/poc.txt",
            "a/b.txt",
            "..",
        ],
        ids=["to_tmp", "nested", "bare_dotdot"],
    )
    def test_malicious_filename_is_rejected(self, app_ctx, tmp_path, file_name):
        content = b"payload"
        with app_ctx.test_request_context(
                "/result_data", method="POST",
                data={"out_tar_data": (io.BytesIO(content), file_name)},
                content_type="multipart/form-data",
                headers={"Content-Length": str(len(content))}) as ctx:
            with pytest.raises(AppException) as e:
                ansible_execution.create_file_path_aap(
                    ctx.request, str(tmp_path), "exec-no-1", "legacy", "ab12")

        assert e.value.args[0] == "499-00201"
        assert _all_files(tmp_path) == []
