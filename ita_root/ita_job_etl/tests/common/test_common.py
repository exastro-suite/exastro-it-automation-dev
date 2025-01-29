#   Copyright 2022 NEC Corporation
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
import requests_mock
from unittest import mock

import re
import os
import datetime
import time
import psutil
from contextlib import closing
import pymysql


TEST_HTTPCODE200_ORIGIN="http://mocked.httpcode200.test"
TEST_HTTPCODE500_ORIGIN="http://mocked.httpcode500.test"


def platform_api_origin():
    """platform url origin

    Returns:
        str: platform url origin
    """
    return f'http://{os.environ["PLATFORM_API_HOST"]}:{os.environ["PLATFORM_API_PORT"]}'

def ita_api_admin_origin():
    """it automation admin url origin

    Returns:
        str: it automation admin url origin
    """
    return f'http://{os.environ["ITA_API_ADMIN_HOST"]}:{os.environ["ITA_API_ADMIN_PORT"]}'

def ita_api_organization_origin():
    """it automation organization url origin

    Returns:
        str: it automation admin url origin
    """
    return f'http://{os.environ["ITA_API_ORGANIZATION_HOST"]}:{os.environ["ITA_API_ORGANIZATION_PORT"]}'


def check_state(timeout: float, conditions, conditions_value=True):
    """一定時間内に条件が成立するか判定する
        Determine if the condition is met within a certain amount of time

    Args:
        timeout (float): timeout seconds
        conditions (_type_): 条件関数 / condition function

    Returns:
        bool: True : 成立 / Established
    """
    timeout_time = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < timeout_time:
        result = conditions()
        if result == conditions_value:
            return True
        time.sleep(0.1)
    print(f"** check_state Last Value:{result}")
    return False


def requests_mocker_default():
    """requestsのデフォルトmocker

    Returns:
        _type_: _description_
    """
    requests_mocker = requests_mock.Mocker()

    requests_mocker.register_uri(
        requests_mock.ANY,
        re.compile(rf'^{platform_api_origin()}/'),
        status_code=200,
        json={"result": "000-00000", "message": ""})

    requests_mocker.register_uri(
        requests_mock.ANY,
        re.compile(rf'^{ita_api_admin_origin()}/'),
        status_code=200,
        json={"result": "000-00000", "message": ""})

    requests_mocker.register_uri(
        requests_mock.ANY,
        re.compile(rf'^{ita_api_organization_origin()}/'),
        status_code=200,
        json={"result": "000-00000", "message": ""})

    # requests_mocker.register_uri(
    #     requests_mock.ANY,
    #     re.compile(rf'^{keycloak_origin()}/'),
    #     real_http=True)

    return requests_mocker


def connect_admin() -> pymysql.connections.Connection:
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        database="",
        user=os.environ.get('DB_ADMIN_USER'),
        password=os.environ.get('DB_ADMIN_PASSWORD'),
        port=int(os.environ.get('DB_PORT')),
        charset='utf8mb4',
        collation='utf8mb4_general_ci',
        cursorclass=pymysql.cursors.DictCursor,
        max_allowed_packet=536_870_912  # 512MB
    )
    return conn
