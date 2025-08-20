#   Copyright 2025 NEC Corporation
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

import pytest
from unittest.mock import MagicMock
import os
from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


class AppException(Exception):
    pass


@pytest.fixture(autouse=True)
def app():
    """unit test用のapp
    """
    # PYTHONPATHにパスが追加されてしまい、AppLog()のinitでコケる
    # そのため、手動設定して回避
    os.environ['PYTHONPATH'] = '/exastro/'
    # load environ variables
    load_dotenv(override=True)

    flask_app = Flask(__name__)

    with flask_app.app_context():

        g.LANGUAGE = os.environ.get("LANGUAGE")
        g.appmsg = MessageTemplate(g.LANGUAGE)
        
        # create app log instance and message class instance
        g.applogger = AppLog()

        g.USER_ID = os.environ.get("USER_ID")
        g.SERVICE_NAME = os.environ.get("SERVICE_NAME")
        
        # OASE Agent用
        g.AGENT_NAME = os.environ.get("AGENT_NAME", "unittest-agent-oase-01")
        yield app


@pytest.fixture()
def agent_info():
    g.AGENT_INFO = {'name': 'unittest-ita-oase-agent-01', 'version': '2.7.0'}
    return g


@pytest.fixture()
def setup_test_env(tmp_path, monkeypatch):
    """
    共通利用：一時ディレクトリと環境変数の設定
    """
    org_id = "unittest_org"
    ws_id = "unittest_ws"
    
    # 既存の環境に影響を与えないように、一時ディレクトリを使用
    storage_dir = tmp_path / "storage"
    tmp_dir = tmp_path / "tmp"
    
    # os.makedirs の動作を一時ディレクトリに向ける
    monkeypatch.setattr(os, 'makedirs', MagicMock(side_effect=lambda name, exist_ok: None))
    
    # 環境変数をモンキーパッチで設定
    monkeypatch.setenv("EXASTRO_URL", "http://unittest-pf-auth:8000")
    monkeypatch.setenv("EXASTRO_USERNAME", "unittest_user")
    monkeypatch.setenv("EXASTRO_PASSWORD", "unittest_password")
    monkeypatch.setenv("HOSTNAME", "unittest-ita-oase-agent-01")
    monkeypatch.setenv("EVENT_COLLECTION_SETTINGS_NAMES", "setting1,setting2")
    
    return org_id, ws_id, storage_dir, tmp_dir
