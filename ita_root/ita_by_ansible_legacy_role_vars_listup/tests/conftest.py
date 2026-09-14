"""ita_by_ansible_legacy_role_vars_listup のテスト共通 fixture

当モジュールのテストは DB に接続しないため、DB コンテナは不要。
"""
import pytest
from unittest.mock import MagicMock
from flask import Flask, g

from tests.common import TEST_USER_ID
from tests.dummy_db import DummyDB


@pytest.fixture
def flask_app_context():
    """Flaskアプリケーションコンテキストを作成"""
    flask_app = Flask(__name__)
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def mock_g(flask_app_context):
    """グローバル変数gをモック化"""
    g.LANGUAGE = "ja"
    g.USER_ID = TEST_USER_ID
    g.SERVICE_NAME = "test_service"
    g.WORKSPACE_ID = "test_workspace_id"
    g.ORGANIZATION_ID = "test_org_id"

    g.applogger = MagicMock()
    g.appmsg = MagicMock()
    g.appmsg.get_log_message.return_value = "Mocked log message"

    return g


@pytest.fixture
def dummy_db():
    """DBConnectWs のダミー（中身は空）"""
    return DummyDB()
