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
Path Traversal 対策のユニットテスト

対象:
    - common_libs.common.util.safe_path_join
    - common_libs.common.util.is_invalid_file_name
    - common_libs.common.util.raise_invalid_file_name_exception
    - common_libs.common.util.get_upload_file_path / get_tmp_file_path / get_upload_file_path_specify
    - common_libs.common.menu_maintenance_all.create_maintenance_parameters
      (maintenance/all の multipart/form-data で指定された filename の検証)

DB・ストレージ・Platformには接続しない。ファイルの書き込みはpytestのtmp_path配下のみ。
"""
import io
import json
import os
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from common_libs.common import menu_maintenance_all
from common_libs.common import util
from common_libs.common.exception import AppException


@pytest.fixture
def app_ctx():
    """
    g.appmsg / g.applogger / g.ORGANIZATION_ID を持つFlaskのアプリケーションコンテキスト。
    メッセージは「メッセージID と 引数」がそのまま分かる文字列で返す。
    """
    app = Flask(__name__)
    with app.app_context():
        g.ORGANIZATION_ID = "org1"
        g.WORKSPACE_ID = "ws1"
        g.applogger = MagicMock()
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda msg_id, args=None: f"{msg_id}:{args}"
        yield app


# --------------------------------------------------------------------------
# safe_path_join
# --------------------------------------------------------------------------
class TestSafePathJoin:

    def test_normal(self, app_ctx, tmp_path):
        """通常のパス要素は、そのまま結合される"""
        # 【正常系】org1/ws1/a.txt のような通常の要素が、baseの実パス配下にそのまま結合されること
        result = util.safe_path_join(str(tmp_path), "org1", "ws1", "a.txt")
        assert result == os.path.join(os.path.realpath(tmp_path), "org1", "ws1", "a.txt")

    def test_no_paths(self, app_ctx, tmp_path):
        """要素が無い場合は、baseそのものを返す"""
        assert util.safe_path_join(str(tmp_path)) == os.path.realpath(tmp_path)

    def test_none_and_empty_are_skipped(self, app_ctx, tmp_path):
        """None / 空文字の要素は無視される"""
        result = util.safe_path_join(str(tmp_path), None, "", "a.txt")
        assert result == os.path.join(os.path.realpath(tmp_path), "a.txt")

    # 【防御の確認】ディレクトリ区切りを含む要素は basename に潰される（例外にはならない）
    #   parent_dirs   : ../ を辿って外へ出ようとする
    #   other_workspace: 他ワークスペース(ws2)のパスを指す
    #   absolute_path : 絶対パス指定
    #   nested_dirs   : 複数階層の指定
    @pytest.mark.parametrize(
        "file_name, expected_name",
        [
            ("../../../tmp/poc.txt", "poc.txt"),
            ("../../ws2/datasheet_01.json", "datasheet_01.json"),
            ("/etc/passwd", "passwd"),
            ("a/b/c.txt", "c.txt"),
        ],
        ids=["parent_dirs", "other_workspace", "absolute_path", "nested_dirs"],
    )
    def test_directory_part_is_stripped(self, app_ctx, tmp_path, file_name, expected_name):
        """ディレクトリ区切りを含む要素は、basenameに潰されbase配下に閉じ込められる"""
        base = os.path.realpath(tmp_path)
        result = util.safe_path_join(str(tmp_path), "sub", file_name)
        # 結合結果が「base/sub/basename」になっていること
        assert result == os.path.join(base, "sub", expected_name)
        # かつ、base配下に閉じ込められていること
        assert result.startswith(base + os.sep)

    def test_bare_dotdot_escape_raises(self, app_ctx, tmp_path):
        """basenameでは潰せない裸の ".." でbaseの外に出る場合は ValueError"""
        with pytest.raises(ValueError):
            util.safe_path_join(str(tmp_path), "..")
        # 越境検知は警告ログに残る
        g.applogger.warning.assert_called()

    def test_dotdot_within_base_is_allowed(self, app_ctx, tmp_path):
        """base配下に留まる ".." は許可される（"sub/.." はbase自身）"""
        result = util.safe_path_join(str(tmp_path), "sub", "..")
        assert result == os.path.realpath(tmp_path)

    def test_symlink_in_path_is_not_resolved(self, app_ctx, tmp_path):
        """
        既存のシンボリックリンクは解決しない
        （アップロード機能が履歴ファイルへのリンクを差し替える処理と整合させるため）
        """
        real_file = tmp_path / "real.txt"
        real_file.write_text("x")
        link = tmp_path / "link.txt"
        link.symlink_to(real_file)

        result = util.safe_path_join(str(tmp_path), "link.txt")
        assert result == os.path.join(os.path.realpath(tmp_path), "link.txt")
        assert os.path.islink(result)


# --------------------------------------------------------------------------
# is_invalid_file_name
# --------------------------------------------------------------------------
# ファイル名の妥当性判定。正常な名前は False、パス要素・制御文字などを含む不正な名前は True を返すこと
#   正常: 英数字・日本語・空白・先頭/途中のドット(".." を含むが単独ではない名前)
#   不正: "/" や "\" を含む / ".." "." 単独 / 空文字 / None / NULL文字を含む
@pytest.mark.parametrize(
    "file_name, expected",
    [
        # 正常
        ("datasheet_01.json", False),
        ("日本語.txt", False),
        ("a b.txt", False),
        ("..hidden", False),
        ("a..b", False),
        (".gitignore", False),
        # 不正
        ("../../../tmp/poc.txt", True),
        ("../poc.txt", True),
        ("a/b.txt", True),
        ("/etc/passwd", True),
        ("a\\b.txt", True),
        ("..\\..\\poc.txt", True),
        ("..", True),
        (".", True),
        ("", True),
        (None, True),
        ("a\0b.txt", True),
    ],
)
def test_is_invalid_file_name(file_name, expected):
    assert util.is_invalid_file_name(file_name) is expected


# --------------------------------------------------------------------------
# raise_invalid_file_name_exception
# --------------------------------------------------------------------------
def test_raise_invalid_file_name_exception(app_ctx):
    """MSG-00036 を使った 499-00201 のAppExceptionに変換される"""
    with pytest.raises(AppException) as e:
        util.raise_invalid_file_name_exception("../poc.txt")

    status_code, log_args, api_args = e.value.args
    # ステータスコードが 499-00201 であること
    assert status_code == "499-00201"
    # APIメッセージに MSG-00036 と、不正だった値そのものが含まれること
    assert "MSG-00036" in api_args[0]
    assert "../poc.txt" in api_args[0]
    # メッセージ取得が MSG-00036 / 引数=[不正なファイル名] で呼ばれていること
    g.appmsg.get_api_message.assert_called_with("MSG-00036", ["../poc.txt"])


# --------------------------------------------------------------------------
# get_upload_file_path / get_tmp_file_path / get_upload_file_path_specify
# --------------------------------------------------------------------------
class TestUploadFilePath:

    @pytest.fixture(autouse=True)
    def _storage(self, monkeypatch, tmp_path):
        # 環境変数 STORAGEPATH を tmp_path 配下の一時ディレクトリに差し替える
        # （実ストレージには書き込まない）
        self.storage = tmp_path / "storage"
        self.storage.mkdir()
        monkeypatch.setenv("STORAGEPATH", str(self.storage))
        self.storage_real = os.path.realpath(self.storage)

    def test_get_upload_file_path_normal(self, app_ctx):
        # 【正常系】jnl_id指定あり: file_path と old_file_path(履歴用 old/{jnl_id}/ 配下)が
        #   {STORAGEPATH}/{org}/{ws}/uploadfiles/{menu}/{rest_key}/{uuid}/... になること
        result = util.get_upload_file_path("ws1", "menu1", "uuid1", "file_02", "a.txt", "jnl1")
        assert result["file_path"] == os.path.join(
            self.storage_real, "org1", "ws1", "uploadfiles", "menu1", "file_02", "uuid1", "a.txt")
        assert result["old_file_path"] == os.path.join(
            self.storage_real, "org1", "ws1", "uploadfiles", "menu1", "file_02", "uuid1", "old", "jnl1", "a.txt")

    def test_get_upload_file_path_without_jnl(self, app_ctx):
        # 【正常系】jnl_id が None の場合、old_file_path は空文字になること
        result = util.get_upload_file_path("ws1", "menu1", "uuid1", "file_02", "a.txt", None)
        assert result["old_file_path"] == ""

    def test_get_upload_file_path_traversal_in_file_name_stays_in_base(self, app_ctx):
        """file_name に ../ を含めても、保存先は同じ階層のファイル名に潰される"""
        # file_name に ../ を多数含む値を渡し、"passwd" というファイル名だけが
        # 通常の保存ディレクトリ(file_path / old_file_path)に採用されること
        result = util.get_upload_file_path("ws1", "menu1", "uuid1", "file_02", "../../../../../etc/passwd", "jnl1")
        expected_dir = os.path.join(self.storage_real, "org1", "ws1", "uploadfiles", "menu1", "file_02", "uuid1")
        assert result["file_path"] == os.path.join(expected_dir, "passwd")
        assert result["old_file_path"] == os.path.join(expected_dir, "old", "jnl1", "passwd")

    def test_get_upload_file_path_escape_raises_app_exception(self, app_ctx):
        """各要素が ".." でSTORAGEPATHの外に出る場合は、AppException(499-00201)に変換される"""
        # organization_id や各引数をすべて ".." にして、STORAGEPATH の外へ出ようとする
        g.ORGANIZATION_ID = ".."
        with pytest.raises(AppException) as e:
            util.get_upload_file_path("..", "..", "..", "..", "..", None)
        assert e.value.args[0] == "499-00201"
        # ValueError(内部の絶対パスを含む例外)が呼び出し元に漏れない
        assert str(self.storage_real) not in str(e.value.args[2])

    def test_get_tmp_file_path_normal(self, app_ctx):
        # 【正常系】一時ファイルの保存先が /tmp/{org}/{ws}/tmp/<ユニークID>/a.txt の形式になること
        result = util.get_tmp_file_path("ws1", "a.txt")
        assert result["file_path"].startswith(os.path.join(os.path.realpath("/tmp"), "org1", "ws1", "tmp") + os.sep)
        assert result["file_path"].endswith(os.sep + "a.txt")

    def test_get_tmp_file_path_traversal_in_file_name_stays_in_base(self, app_ctx):
        # 【防御の確認】file_name に ../ を含めても /tmp/{org}/{ws}/tmp/ 配下の
        #   "passwd" というファイル名に潰されること
        result = util.get_tmp_file_path("ws1", "../../../../../etc/passwd")
        assert result["file_path"].startswith(os.path.join(os.path.realpath("/tmp"), "org1", "ws1", "tmp") + os.sep)
        assert result["file_path"].endswith(os.sep + "passwd")

    # FILE_UPLOAD_PLACE（保存先を示す設定値）の形式ごとに保存先を確認する
    #   notification_log: 複数階層かつ末尾が "/"
    #   ansible_cfg     : 複数階層かつ末尾が "/" でない
    #   single          : 1階層のみ
    @pytest.mark.parametrize(
        "place",
        [
            "/uploadfiles/30108/notification_log/",  # 通知ログ（末尾が "/"）
            "/uploadfiles/10202/Ansible_cfg",        # Ansible cfg（末尾が "/" でない）
            "/place",
        ],
        ids=["notification_log", "ansible_cfg", "single"],
    )
    def test_get_upload_file_path_specify_normal(self, app_ctx, place):
        """
        FILE_UPLOAD_PLACE（複数階層を含む設定値）を指定した場合の保存先が、
        対策前の実装（文字列結合 + os.path.join）と変わらないこと（回帰テスト）
        """
        result = util.get_upload_file_path_specify("ws1", place, "uuid1", "a.txt", "jnl1")

        # 対策前の実装と同じ結果になること
        legacy_dir = os.path.normpath(os.path.join(self.storage_real, "org1", f"ws1{place}", "uuid1"))
        assert result["file_path"] == os.path.join(legacy_dir, "a.txt")
        assert result["old_file_path"] == os.path.join(legacy_dir, "old", "jnl1", "a.txt")

        # 具体的な保存先
        expected_dir = os.path.join(self.storage_real, "org1", "ws1", *[p for p in place.split("/") if p], "uuid1")
        assert result["file_path"] == os.path.join(expected_dir, "a.txt")

    def test_get_upload_file_path_specify_traversal_in_file_name_stays_in_dir(self, app_ctx):
        """file_name に ../ を含めても、保存先は同じ階層のファイル名に潰される"""
        # 通知ログの保存先(place)に対し、file_name へ ../ を含む値を渡しても、
        # 保存先ディレクトリ(uuid配下)の "passwd" になること
        result = util.get_upload_file_path_specify(
            "ws1", "/uploadfiles/30108/notification_log/", "uuid1", "../../../../etc/passwd", "jnl1")
        expected_dir = os.path.join(
            self.storage_real, "org1", "ws1", "uploadfiles", "30108", "notification_log", "uuid1")
        assert result["file_path"] == os.path.join(expected_dir, "passwd")

    def test_get_upload_file_path_specify_escape_raises_app_exception(self, app_ctx):
        # 【異常系】organization_id や各引数を ".." にして STORAGEPATH の外へ出ようとした場合、
        #   AppException(499-00201) に変換されること
        g.ORGANIZATION_ID = ".."
        with pytest.raises(AppException) as e:
            util.get_upload_file_path_specify("..", "", "..", "..", None)
        assert e.value.args[0] == "499-00201"


# --------------------------------------------------------------------------
# create_maintenance_parameters (maintenance/all の multipart/form-data)
# --------------------------------------------------------------------------
class TestCreateMaintenanceParameters:

    @pytest.fixture(autouse=True)
    def _no_disk_check(self, monkeypatch):
        """ディスク空き容量チェックは常にOKとする"""
        storage = MagicMock()
        storage.validate_disk_space.return_value = (True, 1024 ** 3)
        monkeypatch.setattr(menu_maintenance_all, "storage_base", lambda: storage)

    # 以下のヘルパーは、maintenance/all へのリクエスト作成と生成ファイルの一覧取得に使う
    @staticmethod
    def _post(app, file_name, content=b"payload"):
        """filename を指定した multipart/form-data のリクエストコンテキストを作る"""
        params = [{"type": "Register", "parameter": {"file_02": "datasheet_01.json"}}]
        data = {
            "json_parameters": json.dumps(params),
            "0.file_02": (io.BytesIO(content), file_name),
        }
        return app.test_request_context(
            "/maintenance/all/", method="POST", data=data, content_type="multipart/form-data")

    @staticmethod
    def _all_files(root):
        return sorted(
            os.path.join(d, f) for d, _, files in os.walk(root) for f in files)

    def test_normal_file_name(self, app_ctx, tmp_path):
        """通常のファイル名は tmp_path/{index}/{rest_key}/{filename} に保存される"""
        # 【正常系】パート名 "0.file_02" / filename "datasheet_01.json" の通常リクエストで、
        #   parameters・file_paths が期待通りに返り、ファイル内容が保存されていること
        tmp_dir = tmp_path / "work"
        tmp_dir.mkdir()
        with self._post(app_ctx, "datasheet_01.json") as ctx:
            ret, parameters, file_paths = menu_maintenance_all.create_maintenance_parameters(
                ctx.request, str(tmp_dir))

        expected = os.path.join(str(tmp_dir), "0", "file_02", "datasheet_01.json")
        assert ret is True
        assert len(parameters) == 1
        assert file_paths == {0: {"file_02": expected}}
        assert open(expected, "rb").read() == b"payload"

    # 【異常系】filename に不正なパス要素を含むケース
    #   to_tmp / to_code_dir / to_other_workspace: ../ による保存先外への越境
    #   absolute    : 絶対パス指定
    #   nested      : "/" を含むサブディレクトリ指定
    #   bare_dotdot : ".." のみ
    @pytest.mark.parametrize(
        "file_name",
        [
            "../../../tmp/datasheet_01.json",
            "../../../../exastro/config.py",
            "../../ws2/datasheet_01.json",
            "ABSOLUTE_PATH",  # テスト内でtmp_path配下の絶対パスに置き換える
            "a/b.txt",
            "..",
        ],
        ids=["to_tmp", "to_code_dir", "to_other_workspace", "absolute", "nested", "bare_dotdot"],
    )
    # 注: "\" を含む値は、werkzeugが引用符内のバックスラッシュをエスケープとして解釈するため、
    #     multipartでは "..\\..\\poc.txt" が "....poc.txt" として届く。"\" の判定は
    #     test_is_invalid_file_name で検証している。
    def test_malicious_file_name_is_rejected(self, app_ctx, tmp_path, file_name):
        """
        パス要素を含む filename は 499-00201 (MSG-00036) で拒否され、
        どこにもファイルが作られない
        """
        # 絶対パスのケースは、実在のシステム領域に書き込まないよう、tmp_path配下を指す
        if file_name == "ABSOLUTE_PATH":
            file_name = str(tmp_path / "escaped" / "poc.txt")

        # 作業ディレクトリの外に、越境の成否を確認するための領域を用意する
        sandbox = tmp_path / "sandbox"
        tmp_dir = sandbox / "a" / "b" / "c" / "work"
        tmp_dir.mkdir(parents=True)

        with self._post(app_ctx, file_name) as ctx:
            with pytest.raises(AppException) as e:
                menu_maintenance_all.create_maintenance_parameters(ctx.request, str(tmp_dir))

        status_code, _, api_args = e.value.args
        assert status_code == "499-00201"
        assert "MSG-00036" in api_args[0]

        # 何も書き込まれていない（作業ディレクトリ配下も、その外も）
        assert self._all_files(tmp_path) == []

    def test_error_response_does_not_leak_server_path(self, app_ctx, tmp_path):
        """エラー内容にサーバー内部の作業ディレクトリのパスが含まれない"""
        # 不正なfilenameで拒否された際のエラー情報(api_args)に、
        # サーバー内部の作業ディレクトリの絶対パスが漏れていないこと（情報漏えい対策）
        tmp_dir = tmp_path / "work"
        tmp_dir.mkdir()
        with self._post(app_ctx, "../../poc.txt") as ctx:
            with pytest.raises(AppException) as e:
                menu_maintenance_all.create_maintenance_parameters(ctx.request, str(tmp_dir))

        assert str(tmp_dir) not in json.dumps(e.value.args[2])

    def test_multiple_files_one_malicious(self, app_ctx, tmp_path):
        """複数ファイルのうち1つでも不正なら、リクエスト全体が拒否される"""
        # 0番目は正常(ok.txt)、1番目は不正(../../../ng.txt)なリクエストを送り、
        # 499-00201 で拒否され、不正なファイル(ng.txt)がどこにも作られないこと
        tmp_dir = tmp_path / "work"
        tmp_dir.mkdir()
        params = [
            {"type": "Register", "parameter": {"file_02": "ok.txt"}},
            {"type": "Register", "parameter": {"file_02": "ng.txt"}},
        ]
        data = {
            "json_parameters": json.dumps(params),
            "0.file_02": (io.BytesIO(b"ok"), "ok.txt"),
            "1.file_02": (io.BytesIO(b"ng"), "../../../ng.txt"),
        }
        with app_ctx.test_request_context(
                "/maintenance/all/", method="POST", data=data, content_type="multipart/form-data") as ctx:
            with pytest.raises(AppException) as e:
                menu_maintenance_all.create_maintenance_parameters(ctx.request, str(tmp_dir))

        assert e.value.args[0] == "499-00201"
        # 不正なファイルは、作業ディレクトリの外にも内にも作られない
        assert not any(f.endswith("ng.txt") for f in self._all_files(tmp_path))

    # 【異常系】filename ではなく、パート名 "{index}.{rest_key}" の rest_key 側に
    # ディレクトリ区切りを含むケース（保存先ディレクトリ名として使われるため）
    #   to_tmp / to_etc: 絶対パス指定、nested: "/" を含むサブディレクトリ指定
    @pytest.mark.parametrize(
        "part_name",
        [
            "0./tmp/escaped_dir",
            "0./etc/escaped_dir",
            "0.a/b",
        ],
        ids=["to_tmp", "to_etc", "nested"],
    )
    def test_malicious_part_name_rest_key_is_rejected(self, app_ctx, tmp_path, part_name):
        """
        パート名({index}.{rest_key})の rest_key 部分(_list_key)に
        ディレクトリ区切りを含めても、499-00201 (MSG-00036) で拒否され、
        どこにもディレクトリ/ファイルが作られない
        """
        tmp_dir = tmp_path / "work"
        tmp_dir.mkdir()
        params = [{"type": "Register", "parameter": {"file_02": "datasheet_01.json"}}]
        data = {
            "json_parameters": json.dumps(params),
            part_name: (io.BytesIO(b"payload"), "datasheet_01.json"),
        }
        with app_ctx.test_request_context(
                "/maintenance/all/", method="POST", data=data, content_type="multipart/form-data") as ctx:
            with pytest.raises(AppException) as e:
                menu_maintenance_all.create_maintenance_parameters(ctx.request, str(tmp_dir))

        status_code, _, api_args = e.value.args
        assert status_code == "499-00201"
        assert "MSG-00036" in api_args[0]

        # 何も書き込まれていない（ディレクトリも作られていない）
        assert self._all_files(tmp_path) == []
        assert not os.path.isdir(os.path.join(str(tmp_path), "escaped_dir"))
