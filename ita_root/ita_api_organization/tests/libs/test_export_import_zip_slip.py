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
Zip Slip 対策のユニットテスト（Excel一括インポートのzip展開）

対象:
    - ita_api_organization.libs.export_import.find_unsafe_zip_members
    - ita_api_organization.libs.export_import.unzip_file
    - ita_api_organization.libs.export_import.unzip_file_cmd

不正なエントリは、拒否ではなく「スキップして警告ログを出力」し、他のエントリは展開する。

アーカイブはテスト内で tmp_path に生成する（conftest.py の make_zip）。
DB・ストレージ・Platformには接続しない。ファイルの書き込みはpytestのtmp_path配下のみ。

越境の判定:
    tmp_path/work に zip を置き、tmp_path/work/up を展開先とする。
    展開先の1つ上（work）に zip 以外のファイルが作られていないことで「越境していないこと」を確認する。
"""
import os
from types import SimpleNamespace

import pytest

from libs import export_import


# --------------------------------------------------------------------------
# 共通フィクスチャ / ヘルパー
# --------------------------------------------------------------------------
ZIP_NAME = "x.zip"
UPLOAD_ID = "up"


def _files(root):
    # root配下の全ファイルの相対パス一覧
    return sorted(
        os.path.relpath(os.path.join(d, f), str(root))
        for d, _, files in os.walk(str(root)) for f in files)


def _read_all(root):
    # root配下の全ファイル(元のzipを除く)の中身を連結して返す（「不正な中身が残っていないこと」の確認用）
    data = b""
    for d, _, files in os.walk(str(root)):
        for f in files:
            if f == ZIP_NAME:
                continue
            with open(os.path.join(d, f), "rb") as fp:
                data += fp.read()
    return data


@pytest.fixture
def dirs(tmp_path):
    """
    work         : zip を置くディレクトリ (= tmp_dir_path)
    work/x.zip   : 生成したzip
    work/up      : 展開先 (= tmp_dir_path/upload_id)
    """
    work = tmp_path / "work"
    work.mkdir()
    up = work / UPLOAD_ID

    def outside():
        # 展開先(up)の外に作られたファイル (zip自身は除く)
        return [f for f in _files(work)
                if f != ZIP_NAME and not f.startswith(UPLOAD_ID + os.sep)]

    return SimpleNamespace(work=work, up=up, zip=work / ZIP_NAME, outside=outside)


def _warning_messages(app_ctx):
    from flask import g
    return [str(c.args[0]) for c in g.applogger.warning.call_args_list]


def _info_messages(app_ctx):
    from flask import g
    return [str(c.args[0]) for c in g.applogger.info.call_args_list]


# --------------------------------------------------------------------------
# E-1, E-2: find_unsafe_zip_members
# --------------------------------------------------------------------------
class TestFindUnsafeZipMembers:

    def test_returns_only_unsafe_names(self, app_ctx, tmp_path):
        """E-1: 不正なものだけを返し、不正1件につき警告ログが1回出る"""
        names = ["a.txt", "../x", "/abs.txt", "dir/b.txt", "xxx..txt", "a/../../y"]

        unsafe = export_import.find_unsafe_zip_members(names, os.path.realpath(tmp_path))

        assert unsafe == {"../x", "/abs.txt", "a/../../y"}
        assert len(_warning_messages(app_ctx)) == 3

    def test_no_unsafe_names_no_warning(self, app_ctx, tmp_path):
        """E-1: 不正なものが無ければ空で、警告ログも出ない"""
        unsafe = export_import.find_unsafe_zip_members(
            ["a.txt", "dir/b.txt", "xxx..txt", "..xxx.txt"], os.path.realpath(tmp_path))

        assert unsafe == set()
        assert _warning_messages(app_ctx) == []

    def test_warning_message_contents(self, app_ctx, tmp_path):
        """E-2: 警告ログに、エントリ名・理由・組織・ワークスペース・ユーザーが含まれる"""
        export_import.find_unsafe_zip_members(["../zipslip_escape.txt"], os.path.realpath(tmp_path))

        msgs = _warning_messages(app_ctx)
        assert len(msgs) == 1
        assert "Zip Slip detected" in msgs[0]
        assert "../zipslip_escape.txt" in msgs[0]
        assert "Path traversal in zip" in msgs[0]
        assert "organization_id=org1" in msgs[0]
        assert "workspace_id=ws1" in msgs[0]
        assert "user_id=user1" in msgs[0]


# --------------------------------------------------------------------------
# E-3〜E-6, E-11: unzip_file
# --------------------------------------------------------------------------
class TestUnzipFile:

    def test_unsafe_entry_is_skipped(self, app_ctx, dirs, make_zip):
        """E-3: 不正なエントリはスキップ、正常なエントリは展開、外には何も作られない"""
        make_zip(dirs.zip, {
            "MENU_LIST.txt": "m",
            "dir/a.xlsx": "x",
            "../zipslip_escape.txt": "evil",
        })

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is True

        assert _files(dirs.up) == ["MENU_LIST.txt", os.path.join("dir", "a.xlsx")]
        assert dirs.outside() == []
        assert b"evil" not in _read_all(dirs.work)
        assert len(_warning_messages(app_ctx)) == 1

    def test_dotdot_in_name_is_extracted(self, app_ctx, dirs, make_zip):
        """E-4: 名前の一部に「..」を含む正常なエントリは展開され、警告は出ない"""
        names = ["xxx..txt", "..xxx.txt", "xxx..", "xxx...txt", "dir..name/a..b.txt"]
        make_zip(dirs.zip, {n: "x" for n in names})

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is True

        assert _files(dirs.up) == sorted(n.replace("/", os.sep) for n in names)
        assert _warning_messages(app_ctx) == []

    def test_absolute_path_is_skipped(self, app_ctx, dirs, make_zip):
        """E-5: 絶対パスのエントリはスキップされ、警告が出る"""
        make_zip(dirs.zip, {"MENU_LIST.txt": "m", "/abs.txt": "evil"})

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is True

        # zipfile は先頭の「/」を除去して展開先の中に作ってしまうため、スキップされていることを確認する
        assert _files(dirs.up) == ["MENU_LIST.txt"]
        assert dirs.outside() == []
        assert len(_warning_messages(app_ctx)) == 1

    def test_japanese_name_utf8_flag_returns_false(self, app_ctx, dirs, make_zip):
        """E-6: UTF-8フラグ付きの日本語名は、cp437→cp932の変換で失敗して False を返す（既存の挙動）"""
        make_zip(dirs.zip, {"101_管理コンソール/システム設定.xlsx": "x"})

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is False

        assert _files(dirs.work) == [ZIP_NAME]

    def test_japanese_name_cp932(self, app_ctx, dirs, make_zip):
        """日本語名(cp932)は、名前変換後に検証・展開される"""
        make_zip(dirs.zip, {
            "101_管理コンソール/システム設定.xlsx": "x",
            "../zipslip_escape.txt": "evil",
        }, cp932=True)

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is True

        assert _files(dirs.up) == [os.path.join("101_管理コンソール", "システム設定.xlsx")]
        assert dirs.outside() == []
        assert len(_warning_messages(app_ctx)) == 1

    def test_only_unsafe_entries(self, app_ctx, dirs, make_zip):
        """E-11: 不正なエントリだけのzipでも例外にならず、何も展開されない"""
        make_zip(dirs.zip, {"../zipslip_escape.txt": "evil", "/abs.txt": "evil"})

        assert export_import.unzip_file(ZIP_NAME, str(dirs.work), UPLOAD_ID) is True

        assert _files(dirs.work) == [ZIP_NAME]
        assert len(_warning_messages(app_ctx)) == 2


# --------------------------------------------------------------------------
# E-7〜E-11: unzip_file_cmd (unzipコマンド)
# --------------------------------------------------------------------------
class TestUnzipFileCmd:

    def test_unsafe_entry_is_excluded(self, app_ctx, dirs, make_zip):
        """E-7: 不正なエントリは unzip -x で除外され、正常なエントリは展開される。警告も出る"""
        make_zip(dirs.zip, {
            "MENU_LIST.txt": "m",
            "dir/a.xlsx": "x",
            "../zipslip_escape.txt": "evil",
        })

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.up) == ["MENU_LIST.txt", os.path.join("dir", "a.xlsx")]
        assert dirs.outside() == []
        assert b"evil" not in _read_all(dirs.work)
        assert len(_warning_messages(app_ctx)) == 1

    def test_absolute_path_is_excluded(self, app_ctx, dirs, make_zip):
        """E-7: 絶対パスのエントリも除外される"""
        make_zip(dirs.zip, {"MENU_LIST.txt": "m", "/abs.txt": "evil"})

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.up) == ["MENU_LIST.txt"]
        assert dirs.outside() == []
        assert len(_warning_messages(app_ctx)) == 1

    def test_dotdot_in_name_is_extracted(self, app_ctx, dirs, make_zip):
        """名前の一部に「..」を含む正常なエントリは展開され、警告は出ない"""
        names = ["xxx..txt", "..xxx.txt", "xxx..", "xxx...txt", "dir..name/a..b.txt"]
        make_zip(dirs.zip, {n: "x" for n in names})

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.up) == sorted(n.replace("/", os.sep) for n in names)
        assert _warning_messages(app_ctx) == []

    def test_wildcard_characters_in_name(self, app_ctx, dirs, make_zip):
        """E-8: [ * ? を含む名前は、パターンとして解釈されず、正常なエントリが巻き添えにならない"""
        # 不正なエントリを先頭に置く。除外パターンのエスケープが無いと、除外されずに
        # 「../」を除去した名前で展開され、正常な「[wild]*.txt」の中身が不正なものになる
        make_zip(dirs.zip, {
            "../[wild]*.txt": "evil",     # 不正
            "[wild]*.txt": "normal",      # 正常
            "w.txt": "normal2",           # 正常 ([wild]* にマッチしうる名前)
        })

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.up) == sorted(["[wild]*.txt", "w.txt"])
        assert (dirs.up / "[wild]*.txt").read_bytes() == b"normal"
        assert dirs.outside() == []
        assert b"evil" not in _read_all(dirs.work)
        assert len(_warning_messages(app_ctx)) == 1

    def test_japanese_name_utf8_flag(self, app_ctx, dirs, make_zip):
        """E-9: UTF-8フラグ付きの日本語名は、unzipコマンドで展開される（実機でこの経路に落ちる）"""
        make_zip(dirs.zip, {
            "101_管理コンソール/システム設定.xlsx": "x",
            "MENU_LIST.txt": "m",
            "../zipslip_escape.txt": "evil",
        })

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.up) == [os.path.join("101_管理コンソール", "システム設定.xlsx"), "MENU_LIST.txt"]
        assert dirs.outside() == []
        assert len(_warning_messages(app_ctx)) == 1

    def test_unreadable_zip(self, app_ctx, dirs):
        """E-10: 読めないzipは、展開せずに return し、ログを出す"""
        dirs.zip.write_bytes(b"this is not a zip file")

        assert export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID) is None

        assert _files(dirs.work) == [ZIP_NAME]
        assert any("unreadable zip" in m for m in _info_messages(app_ctx))

    def test_only_unsafe_entries(self, app_ctx, dirs, make_zip):
        """E-11: 不正なエントリだけのzipでも例外にならず、何も展開されない"""
        make_zip(dirs.zip, {"../zipslip_escape.txt": "evil", "/abs.txt": "evil"})

        export_import.unzip_file_cmd(ZIP_NAME, str(dirs.work), UPLOAD_ID)

        assert _files(dirs.work) == [ZIP_NAME]
        assert len(_warning_messages(app_ctx)) == 2
