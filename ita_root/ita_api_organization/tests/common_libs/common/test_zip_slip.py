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
Zip Slip 対策のユニットテスト（共通関数）

対象:
    - common_libs.common.util.check_zip_member_name
    - common_libs.common.util.retry_zip_extract
    - common_libs.common.util.safe_extractall_tar
    - common_libs.common.util.retry_extract

アーカイブはテスト内で tmp_path に生成する（conftest.py の make_zip / make_tar_gz）。
DB・ストレージ・Platformには接続しない。ファイルの書き込みはpytestのtmp_path配下のみ。

越境の判定:
    tmp_path/work/base を「展開先」とし、tmp_path/work 直下（= 展開先の1つ上）に
    ファイルが作られていないことで「展開先の外に出ていないこと」を確認する。
"""
import os
import tarfile
from types import SimpleNamespace

import pytest

from common_libs.common import util


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
    work/base : 展開先
    work      : 展開先の1つ上（ここにファイルが作られたら越境）
    archives  : 生成したアーカイブの置き場
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
# U-1〜U-4: check_zip_member_name
# --------------------------------------------------------------------------
class TestCheckZipMemberName:

    @pytest.mark.parametrize("name", ["a.txt", "dir/a.txt", "./a.txt"])
    def test_normal(self, dirs, name):
        """U-1: 正常な名前は通る"""
        util.check_zip_member_name(name, os.path.realpath(dirs.base))

    @pytest.mark.parametrize("name", [
        "xxx..txt",
        "..xxx.txt",
        "xxx..",
        "xxx...txt",
        "dir..name/a..b.txt",
    ])
    def test_dotdot_in_name_is_not_traversal(self, dirs, name):
        """U-2: 名前の一部に「..」を含むだけのものは誤検知しない"""
        util.check_zip_member_name(name, os.path.realpath(dirs.base))

    @pytest.mark.parametrize("name", [
        "../x",
        "a/../../x",
        "..\\x",
    ])
    def test_traversal_is_rejected(self, dirs, name):
        """U-3: 親ディレクトリへ出る名前は拒否する"""
        with pytest.raises(ValueError):
            util.check_zip_member_name(name, os.path.realpath(dirs.base))

    @pytest.mark.parametrize("name", [
        "/abs",
        "C:/x",
    ])
    def test_absolute_is_rejected(self, dirs, name):
        """U-4: 絶対パス・ドライブ指定は拒否する"""
        with pytest.raises(ValueError):
            util.check_zip_member_name(name, os.path.realpath(dirs.base))


# --------------------------------------------------------------------------
# U-5, U-6: retry_zip_extract
# --------------------------------------------------------------------------
class TestRetryZipExtract:

    def test_normal(self, app_ctx, dirs, make_zip):
        """U-5 / R-1: 通常のzipは展開される"""
        z = make_zip(dirs.archives / "a.zip", {"MENU_LIST.txt": "m", "dir/a.xlsx": "x"})

        util.retry_zip_extract(z, str(dirs.base))

        assert _files(dirs.base) == ["MENU_LIST.txt", os.path.join("dir", "a.xlsx")]
        assert dirs.outside() == []

    def test_dotdot_in_name_is_extracted(self, app_ctx, dirs, make_zip):
        """名前の一部に「..」を含むエントリは展開される"""
        names = ["xxx..txt", "..xxx.txt", "xxx..", "xxx...txt", "dir..name/a..b.txt"]
        z = make_zip(dirs.archives / "a.zip", {n: "x" for n in names})

        util.retry_zip_extract(z, str(dirs.base))

        assert _files(dirs.base) == sorted(n.replace("/", os.sep) for n in names)

    def test_unsafe_entry_rejects_whole_archive(self, app_ctx, dirs, make_zip):
        """U-6 / R-4: 不正なエントリが1件でもあれば、正常なエントリも含めて何も展開しない"""
        z = make_zip(dirs.archives / "a.zip", {
            "MENU_LIST.txt": "m",
            "../zipslip_escape.txt": "evil",
        })

        with pytest.raises(ValueError):
            util.retry_zip_extract(z, str(dirs.base))

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_empty_zip(self, app_ctx, dirs, make_zip):
        """R-2: 空のzipでも例外にならない"""
        z = make_zip(dirs.archives / "empty.zip", {})

        util.retry_zip_extract(z, str(dirs.base))

        assert _files(dirs.base) == []


# --------------------------------------------------------------------------
# U-7〜U-11: safe_extractall_tar
# --------------------------------------------------------------------------
class TestSafeExtractallTar:

    def test_normal(self, dirs, make_tar_gz):
        """U-7 / R-1: 通常のメンバと、名前に「..」を含むメンバは展開される"""
        names = ["MENU_LIST.txt", "dir/a.xlsx", "xxx..txt", "..xxx.txt", "dir..name/a..b.txt"]
        t = make_tar_gz(dirs.archives / "a.tar.gz", {n: "x" for n in names})

        with tarfile.open(t, "r:gz") as tar:
            util.safe_extractall_tar(tar, str(dirs.base))

        assert _files(dirs.base) == sorted(n.replace("/", os.sep) for n in names)
        assert dirs.outside() == []

    def test_traversal_is_rejected(self, dirs, make_tar_gz):
        """U-8 / R-3: 「../」を含むメンバは拒否し、正常なメンバも含めて何も展開しない"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {
            "MENU_LIST.txt": "m",
            "../zipslip_escape.txt": "evil",
        })

        with tarfile.open(t, "r:gz") as tar:
            # Pythonの展開フィルタが出す例外(OutsideDestinationError)ではなく、
            # アプリ側の検証が出す ValueError であること
            with pytest.raises(ValueError, match="Unsafe path in archive"):
                util.safe_extractall_tar(tar, str(dirs.base))

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_absolute_path_is_rejected(self, dirs, make_tar_gz):
        """U-9: 絶対パスのメンバは拒否する（万一検証をすり抜けても tmp_path 内に収まる名前を使う）"""
        abs_name = str(dirs.work / "abs_escape.txt")
        t = make_tar_gz(dirs.archives / "a.tar.gz", {abs_name: "evil"})

        with tarfile.open(t, "r:gz") as tar:
            with pytest.raises(ValueError, match="Unsafe path in archive"):
                util.safe_extractall_tar(tar, str(dirs.base))

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    @pytest.mark.skipif(not hasattr(tarfile, "data_filter"), reason="tarfileにdata_filterが無い")
    def test_symlink_outside_is_rejected(self, dirs, make_tar_gz):
        """U-10: 展開先の外を指すシンボリックリンクは拒否する"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {}, symlinks={"link": "../outside_target"})

        with tarfile.open(t, "r:gz") as tar:
            with pytest.raises(tarfile.FilterError):
                util.safe_extractall_tar(tar, str(dirs.base))

        assert not os.path.lexists(dirs.base / "link")
        assert dirs.outside() == []

    def test_members_subset(self, dirs, make_tar_gz):
        """U-11: members を指定した場合、渡したメンバだけを検証・展開する"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {
            "DP_INFO": "d",
            "other.txt": "o",
            "../zipslip_escape.txt": "evil",  # members に含めないので検証・展開されない
        })

        with tarfile.open(t, "r:gz") as tar:
            targets = [m for m in tar.getmembers() if m.name == "DP_INFO"]
            util.safe_extractall_tar(tar, str(dirs.base), members=targets)

        assert _files(dirs.base) == ["DP_INFO"]
        assert dirs.outside() == []

    def test_members_subset_with_unsafe_member_is_rejected(self, dirs, make_tar_gz):
        """members に不正なメンバを含めた場合は拒否する"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {
            "DP_INFO": "d",
            "../zipslip_escape.txt": "evil",
        })

        with tarfile.open(t, "r:gz") as tar:
            with pytest.raises(ValueError, match="Unsafe path in archive"):
                util.safe_extractall_tar(tar, str(dirs.base), members=tar.getmembers())

        assert _files(dirs.base) == []
        assert dirs.outside() == []

    def test_empty_tar(self, dirs, make_tar_gz):
        """R-2: 空のtarでも例外にならない"""
        t = make_tar_gz(dirs.archives / "empty.tar.gz", {})

        with tarfile.open(t, "r:gz") as tar:
            util.safe_extractall_tar(tar, str(dirs.base))

        assert _files(dirs.base) == []


# --------------------------------------------------------------------------
# retry_extract（tar.gzファイルを開いて safe_extractall_tar で展開する）
# --------------------------------------------------------------------------
class TestRetryExtract:

    def test_normal(self, app_ctx, dirs, make_tar_gz):
        """R-1: 通常のtar.gzは展開される"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {"MENU_LIST.txt": "m", "dir/a.xlsx": "x"})

        util.retry_extract(t, str(dirs.base))

        assert _files(dirs.base) == ["MENU_LIST.txt", os.path.join("dir", "a.xlsx")]

    def test_unsafe_member_is_rejected(self, app_ctx, dirs, make_tar_gz):
        """R-3: 不正なメンバを含むtar.gzは展開できない"""
        t = make_tar_gz(dirs.archives / "a.tar.gz", {
            "MENU_LIST.txt": "m",
            "../zipslip_escape.txt": "evil",
        })

        with pytest.raises(ValueError, match="Unsafe path in archive"):
            util.retry_extract(t, str(dirs.base))

        assert _files(dirs.base) == []
        assert dirs.outside() == []
