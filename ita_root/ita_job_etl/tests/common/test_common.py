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


def requsts_mocker_default():
    """requstsのデフォルトmocker

    Returns:
        _type_: _description_
    """
    requests_mocker = requests_mock.Mocker()

    requests_mocker.register_uri(
        requests_mock.ANY,
        re.compile(rf'^{ita_api_admin_origin()}/'),
        status_code=200,
        json={"result": "000-00000", "message": ""})

    requests_mocker.register_uri(
        requests_mock.ANY,
        re.compile(rf'^{keycloak_origin()}/'),
        real_http=True)

    return requests_mocker
