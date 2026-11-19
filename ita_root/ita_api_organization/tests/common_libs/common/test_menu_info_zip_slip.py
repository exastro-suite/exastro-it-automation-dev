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
Zip Slip 対策のユニットテスト（メニュー情報のzip展開）

対象:
    - common_libs.common.menu_info.unzip_file

不正なエントリが1件でもあれば、展開前に全体を拒否する（False を返す）。
これは変更前から続く例外時の挙動（False を返す）を維持したもので、スキップへの変更はしない。

アーカイブはテスト内で tmp_path に生成する（conftest.py の make_zip）。
DB・ストレージ・Platformには接続しない。ファイルの書き込みはpytestのtmp_path配下のみ。

越境の判定:
    tmp_path/work/base を「展開先」とし、tmp_path/work 直下（= 展開先の1つ上）に
    ファイルが作られていないことで「展開先の外に出ていないこと」を確認する。
"""
import os
from types import SimpleNamespace

import pytest

from common_libs.common import menu_info


# --------------------------------------------------------------------------
# 共通フィクスチャ / ヘルパー
# --------------------------------------------------------------------------
def _files(root):
    # root配下の全ファイルの相対パス一覧
    return sorted(
        os.path.relpath(os.path.join(d, f), str(root))
        for d, _, files in os.walk(str(root)) for f in files)


@pytest.fixture
def dirs(tmp_path):
    """
    work/base : 展開先 (= uploadPath)
    work      : 展開先の1つ上（ここにファイルが作られたら越境）
    archives  : 生成したzipの置き場
    """
    work = tmp_path / "work"
    base = work / "base"
    base.mkdir(parents=True)
    archives = tmp_path / "archives"
    archives.mkdir()

    def outside():
        # 展開先(base)の外に作られたファイル
        return [f for f in _files(work) if not f.startswith("base" + os.sep)]

    return SimpleNamespace(work=work, base=base, archives=archives, outside=outside)


# --------------------------------------------------------------------------
# M-1〜M-6
# --------------------------------------------------------------------------
class TestUnzipFile:

    def test_normal(self, app_ctx, dirs, make_zip):
        """M-1: 正常なzipは True を返し、全エントリが展開される"""
        z = make_zip(dirs.archives / "a.zip", {"MENU_LIST.txt": "m", "dir/a.xlsx": "x"})

        assert menu_info.unzip_file(z, str(dirs.base)) is True

        assert _files(dirs.base) == ["MENU_LIST.txt", os.path.join("dir", "a.xlsx")]
        assert dirs.outside() == []

    def test_traversal_rejects_whole_archive(self, app_ctx, dirs, make_zip):
        """M-2: 越境エントリを含む場合は False を返し、正常なエントリも含めて何も展開しない"""
        z = make_zip(dirs.archives / "a.zip", {
            "MENU_LIST.txt": "m",
            "dir/a.xlsx": "x",
            "../zipslip_escape.txt": "evil",
        })

        assert menu_info.unzip_file(z, str(dirs.base)) is False

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_absolute_path_rejects_whole_archive(self, app_ctx, dirs, make_zip):
        """M-3: 絶対パスのエントリを含む場合は False を返し、何も展開しない"""
        z = make_zip(dirs.archives / "a.zip", {"MENU_LIST.txt": "m", "/abs.txt": "evil"})

        assert menu_info.unzip_file(z, str(dirs.base)) is False

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_dotdot_in_name_is_extracted(self, app_ctx, dirs, make_zip):
        """M-4: 名前の一部に「..」を含む正常なエントリは True を返し、展開される"""
        names = ["xxx..txt", "..xxx.txt", "xxx..", "xxx...txt", "dir..name/a..b.txt"]
        z = make_zip(dirs.archives / "a.zip", {n: "x" for n in names})

        assert menu_info.unzip_file(z, str(dirs.base)) is True

        assert _files(dirs.base) == sorted(n.replace("/", os.sep) for n in names)

    def test_japanese_name_cp932(self, app_ctx, dirs, make_zip):
        """M-5: 日本語名(cp932)は、名前変換後に検証・展開される"""
        z = make_zip(dirs.archives / "a.zip", {
            "101_管理コンソール/システム設定.xlsx": "x",
            "MENU_LIST.txt": "m",
        }, cp932=True)

        assert menu_info.unzip_file(z, str(dirs.base)) is True

        assert _files(dirs.base) == [os.path.join("101_管理コンソール", "システム設定.xlsx"), "MENU_LIST.txt"]

    def test_japanese_name_cp932_with_traversal(self, app_ctx, dirs, make_zip):
        """M-5: 日本語名(cp932)のzipでも、越境エントリは拒否される"""
        z = make_zip(dirs.archives / "a.zip", {
            "101_管理コンソール/システム設定.xlsx": "x",
            "../zipslip_escape.txt": "evil",
        }, cp932=True)

        assert menu_info.unzip_file(z, str(dirs.base)) is False

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_rejection_is_logged(self, app_ctx, dirs, make_zip):
        """M-6: 拒否した場合、理由（例外）が g.applogger.info に記録される"""
        from flask import g
        z = make_zip(dirs.archives / "a.zip", {"../zipslip_escape.txt": "evil"})

        assert menu_info.unzip_file(z, str(dirs.base)) is False

        msgs = [str(c.args[0]) for c in g.applogger.info.call_args_list]
        assert any("Path traversal in zip" in m and "../zipslip_escape.txt" in m for m in msgs)

    def test_empty_zip(self, app_ctx, dirs, make_zip):
        """R-2: 空のzipでも例外にならず True を返す"""
        z = make_zip(dirs.archives / "empty.zip", {})

        assert menu_info.unzip_file(z, str(dirs.base)) is True

        assert _files(dirs.base) == []
