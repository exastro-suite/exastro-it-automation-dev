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

import os
import os.path
import shutil
import glob
import requests
import json
import subprocess
import multiprocessing
from contextlib import closing
import signal
import inspect
import base64
from importlib import import_module
from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv
import sys

from common import test_common
from common_libs.common import encrypt
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate

import backyard_main


class UserException(Exception):
    """ユーザー例外 User Exception

    Args:
        Exception (Exception): Exception
    """
    pass


@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    """pytest-docker docker-composeコマンド設定

    Returns:
        str: docker composeコマンド
    """
    if os.environ.get('DOCKER_COMPOSE_UP_UNITTEST_NODE', 'MANUAL') == 'AUTO':
        return "sudo docker compose "
    else:
        return ":"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig, autouse=True):
    """pytest-docker docker-compose.ymlファイル指定

    Args:
        pytestconfig (_type_): pytestconfig fixtureパラメータ
        autouse (bool, optional): fixture自動起動=true

    Returns:
        str: docker-compose.ymlファイルパス
    """
    return os.path.join(os.path.dirname(__file__), "docker-compose.yml")


@pytest.fixture(autouse=True)
def encrypt_key(mocker):
    """unit test用のencrypt key設定
        Encrypt key settings for unit test

    Args:
        mocker (_type_): _description_
    """
    testdata = import_module("tests.db.exports.testdata")
    mocker.patch.object(encrypt, 'ENCRYPT_KEY', new=base64.b64decode(testdata.ENCRYPT_KEY))


@pytest.fixture(autouse=True)
def flask_initialize():
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



@pytest.fixture(scope='function', autouse=True)
def data_initialize():
    """データー初期化 / Data initialization

    """
    testdata = import_module("tests.db.exports.testdata")

    #
    # データ初期化 / Data initialization
    #
    sql_file = os.path.join(os.path.dirname(__file__), "db", "exports", "pytest2_restore_databases.sql")
    db_user = os.environ.get('DB_ADMIN_USER')
    db_password = os.environ.get('DB_ADMIN_PASSWORD')
    db_host = os.environ.get('DB_HOST')

    # 環境変数が設定されていない場合のエラーチェック
    # Check for errors when environment variables are not set
    if not db_user or not db_password or not db_host:
        raise EnvironmentError("Database credentials (DB_ADMIN_USER, DB_ADMIN_PASSWORD, DB_HOST) are not set in environment variables.")

    # MySQLコマンドの実行
    # Executing MySQL commands
    result_command = subprocess.run(
        ["mysql", "-u", db_user, f"-p{db_password}", "-h", db_host, "-e", f"source {sql_file}"],
        shell=False  # セキュリティ向上のために shell=False を使用 / Use shell=False for increased security
    )

    if result_command.returncode != 0:
        raise UserException('FAILED : mysql command (tests/conftest.py data_initialize)')

    #
    # organization, workspace database drop
    #
    with closing(test_common.connect_admin()) as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME LIKE 'ita_%'")
        databases = [database['SCHEMA_NAME'] for database in cursor.fetchall() if database['SCHEMA_NAME'] not in testdata.DATABASES]
        for database in databases:
            cursor.execute(f"DROP DATABASE {database['SCHEMA_NAME']}")

        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME LIKE 'ita_%'")

    #
    # Initialize the storage directory
    #
    storage_path = os.environ.get("STORAGEPATH")
    if storage_path != "/storage/":
        # クリーンアップ / clean up
        files_dir = [f for f in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, f))]
        for delete_dir in files_dir:
            shutil.rmtree(storage_path + delete_dir)

        # org/wsディレクトリ作成およびtarの展開 / Create the org/ws directory and unpack the tar file
        for org_id, data in testdata.ORGANIZATIONS.items():
            org_path = storage_path + org_id
            os.makedirs(org_path)
            for ws_id in data.get("workspace_id"):
                ws_path = org_path + "/" + ws_id
                os.makedirs(ws_path)
                shutil.unpack_archive(os.getcwd() + "/tests/sample_files/workspace_dir.tar.gz", ws_path)


@pytest.fixture(autouse=True)
def signal_signal_mock(mocker):
    """mocked signal.signal

    Args:
        mocker (_type_): _description_
    """
    signal_signal = signal.signal

    def mocked_function(signum, handler):
        stack_functions = [s.function for s in inspect.stack()]

        if (backyard_main.backyard_main.__name__ in stack_functions):
            # main processから呼ばれたsub processの場合のみsingnal handerを設定する
            signal_signal(signum, handler)

    mocker.patch.object(signal, 'signal', mocked_function)