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
Path Traversal 対策のユニットテスト（単一レコード登録API, multipart/form-data）

対象:
    - ita_api_organization.libs.menu_maintenance.create_maintenance_parameters

検証手順2.md の検証2(a/b)に対応。
"""
import io
import json
import os
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from common_libs.common.exception import AppException
from libs import menu_maintenance


# --------------------------------------------------------------------------
# 共通フィクスチャ / ヘルパー
# --------------------------------------------------------------------------
@pytest.fixture
def app_ctx():
    # g.applogger / g.appmsg をMagicMockにしたFlaskアプリケーションコンテキスト。
    # メッセージは「ID:引数」の文字列で返す。DB・ストレージには接続しない。
    app = Flask(__name__)
    with app.app_context():
        g.applogger = MagicMock()
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda msg_id, args=None: f"{msg_id}:{args}"
        yield app


def _all_files(root):
    # root配下の全ファイルのパス一覧を返す（「何もファイルが作られていないこと」の確認用）
    return sorted(
        os.path.join(d, f) for d, _, files in os.walk(str(root)) for f in files)


def _post(app, file_key, file_name, content=b"payload"):
    """file_key(パート名) / file_name(filename) を指定した multipart/form-data のリクエストコンテキストを作る"""
    data = {
        "json_parameters": json.dumps({"parameter": {"file_02": "datasheet_01.json"}}),
        file_key: (io.BytesIO(content), file_name),
    }
    return app.test_request_context(
        "/maintenance/", method="POST", data=data, content_type="multipart/form-data")


def test_normal(app_ctx, tmp_path):
    """通常のパート名・filenameは tmp_path/{file_key}/{filename} に保存される"""
    # 【正常系】不正値を含まない通常のリクエストで、
    #   ret=True、file_paths が期待パスを指し、ファイル内容が保存されていること
    with _post(app_ctx, "file_02", "datasheet_01.json") as ctx:
        ret, parameters, file_paths = menu_maintenance.create_maintenance_parameters(
            ctx.request, "Register", str(tmp_path))

    expected = os.path.join(str(tmp_path), "file_02", "datasheet_01.json")
    assert ret is True
    assert file_paths == {"file_02": expected}
    assert open(expected, "rb").read() == b"payload"


# 【異常系】アップロードファイルの filename に不正なパス要素を含むケース
#   to_tmp      : ../ を辿って保存先の外(/tmp等)へ出ようとする
#   to_code_dir : ../ を辿ってアプリのコードディレクトリを上書きしようとする
#   nested      : "/" を含むサブディレクトリ指定
#   bare_dotdot : ".." のみ
@pytest.mark.parametrize(
    "file_name",
    [
        "../../../tmp/poc.txt",
        "../../../../exastro/config.py",
        "a/b.txt",
        "..",
    ],
    ids=["to_tmp", "to_code_dir", "nested", "bare_dotdot"],
)
def test_malicious_filename_is_rejected(app_ctx, tmp_path, file_name):
    """filename にパス要素を含めても AppException(499-00201) で拒否され、何も作られない"""
    # 作業ディレクトリ(sandbox/.../work)の外に越境して書き込まれても検知できるよう、
    # tmp_path 全体を確認対象にする
    sandbox = tmp_path / "sandbox" / "a" / "b" / "work"
    sandbox.mkdir(parents=True)

    with _post(app_ctx, "file_02", file_name) as ctx:
        with pytest.raises(AppException) as e:
            menu_maintenance.create_maintenance_parameters(ctx.request, "Register", str(sandbox))

    status_code = e.value.args[0]
    assert status_code == "499-00201"
    assert _all_files(tmp_path) == []


# 【異常系】filename ではなく、パート名(=保存先ディレクトリ名になる file_key)に
#   不正なパス要素を含むケース
#   absolute : 絶対パス指定
#   traversal: ../ による親ディレクトリ指定
#   nested   : "/" を含むサブディレクトリ指定
@pytest.mark.parametrize(
    "file_key",
    [
        "/tmp/escaped_dir",
        "../../../tmp/escaped_dir",
        "a/b",
    ],
    ids=["absolute", "traversal", "nested"],
)
def test_malicious_part_name_is_rejected(app_ctx, tmp_path, file_key):
    """パート名(_file_key)自体にパス要素を含めても AppException(499-00201) で拒否され、何も作られない"""
    sandbox = tmp_path / "sandbox" / "a" / "b" / "work"
    sandbox.mkdir(parents=True)

    with _post(app_ctx, file_key, "datasheet_01.json") as ctx:
        with pytest.raises(AppException) as e:
            menu_maintenance.create_maintenance_parameters(ctx.request, "Register", str(sandbox))

    status_code, _, api_args = e.value.args
    assert status_code == "499-00201"
    assert _all_files(tmp_path) == []
    # パート名に含まれていたディレクトリ(escaped_dir)も作られていないこと
    assert not os.path.isdir(os.path.join(str(tmp_path), "escaped_dir"))
    # メッセージには、実際に不正だった値(パート名)が含まれ、
    # クリーンな方の値(filename="datasheet_01.json")は含まれないこと
    assert file_key in api_args[0]
    assert "datasheet_01.json" not in api_args[0]
