import io
import os
import tarfile
import zipfile
import pytest
from unittest.mock import MagicMock
import connexion
from flask import Flask, g


@pytest.fixture(scope='session')
def app_context_with_mock_g():
    """
    Connexionで作成されたFlaskコンテキストとg.appmsgモックを生成するフィクスチャ
    """
    # Connexionを使ってFlaskアプリケーションインスタンスを作成
    app_root_dir = os.path.dirname(os.path.dirname(__file__))
    connexion_app = connexion.FlaskApp(__name__, specification_dir=f'{app_root_dir}/swagger/')
    connexion_app.add_api('swagger.yaml')

    # ここでbefore_request_handlerなどの設定を行う（必要に応じて）
    # from libs.organization_common import before_request_handler
    # connexion_app.app.before_request(before_request_handler)

    # Flaskアプリのコンテキストを作成
    ctx = connexion_app.app.app_context()
    ctx.push()

    # g.appmsgをモック化
    g.appmsg = MagicMock()

    yield  # ここでテスト関数を実行

    # テスト終了後にコンテキストをクリーンアップ
    ctx.pop()


# --------------------------------------------------------------------------
# Zip Slip 対策テスト用: アーカイブの生成ヘルパー / アプリケーションコンテキスト
#   実機の zip / kym は使わず、テスト内で tmp_path に生成する。
# --------------------------------------------------------------------------
class _Cp932ZipInfo(zipfile.ZipInfo):
    """ファイル名を cp932 でそのまま書き込む ZipInfo (UTF-8フラグを立てない)"""

    def _encodeFilenameFlags(self):
        return self.filename.encode('cp932'), self.flag_bits


def _to_bytes(content):
    return content.encode('utf-8') if isinstance(content, str) else content


@pytest.fixture
def make_zip():
    """
    zipを生成する関数を返す。

    make_zip(path, entries, cp932=False)
        entries: {名前: 中身} 。名前はそのまま書き込まれる ("../x" や "/abs.txt" も可)
        cp932:   True の場合、名前を cp932 で書き込む (UTF-8 フラグなし)
                 False の場合、ASCII以外はUTF-8フラグ付きで書き込まれる
    """
    def _make_zip(path, entries, cp932=False):
        with zipfile.ZipFile(str(path), "w") as z:
            for name, content in entries.items():
                if cp932:
                    z.writestr(_Cp932ZipInfo(name), _to_bytes(content))
                else:
                    z.writestr(name, _to_bytes(content))
        return str(path)
    return _make_zip


@pytest.fixture
def make_tar_gz():
    """
    tar.gz を生成する関数を返す。

    make_tar_gz(path, entries, symlinks=None)
        entries:  {名前: 中身} 。名前はそのまま書き込まれる ("../x" や "/abs.txt" も可)
        symlinks: {名前: リンク先} 。シンボリックリンクのメンバを追加する
    """
    def _make_tar_gz(path, entries, symlinks=None):
        with tarfile.open(str(path), "w:gz") as tar:
            for name, content in entries.items():
                data = _to_bytes(content)
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(data))
            for name, target in (symlinks or {}).items():
                info = tarfile.TarInfo(name)
                info.type = tarfile.SYMTYPE
                info.linkname = target
                tar.addfile(info)
        return str(path)
    return _make_tar_gz


@pytest.fixture
def app_ctx():
    """
    g.appmsg / g.applogger / g.ORGANIZATION_ID 等を持つFlaskのアプリケーションコンテキスト。
    DB・ストレージ・Platformには接続しない。
    """
    app = Flask(__name__)
    with app.app_context():
        g.ORGANIZATION_ID = "org1"
        g.WORKSPACE_ID = "ws1"
        g.USER_ID = "user1"
        g.applogger = MagicMock()
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda msg_id, args=None: f"{msg_id}:{args}"
        yield app
