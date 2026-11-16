# Copyright 2026 NEC Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ssl
from unittest.mock import Mock

import pytest
from flask import Flask, g

from common_libs.ansible_driver.classes.ansibletowerlibs import RestApiCaller as module_under_test
from common_libs.ansible_driver.classes.ansibletowerlibs.RestApiCaller import RestApiCaller

ENV = "ANSIBLE_AAP_SSL_VERIFY_ENABLED"

class FakeResponse:
    """urllib.request.urlopen の戻り値の代役（with 文で使える）"""

    def __init__(self, body=b"{}"):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getcode(self):
        return 200

    def getheaders(self):
        return [("Content-Type", "application/json")]

    def read(self):
        return self.body


@pytest.fixture
def mock_g():
    app = Flask(__name__)
    with app.app_context():
        g.applogger = Mock()
        g.appmsg = Mock()
        g.appmsg.get_log_message = Mock(side_effect=lambda msg_id, args=None: (msg_id, args))
        g.AACRestAPITimout = 5
        yield g


@pytest.fixture
def captured_context(monkeypatch):
    """urlopen に渡された ssl context を記録する"""
    contexts = []

    def fake_urlopen(req, context=None, timeout=None):
        contexts.append(context)
        return FakeResponse()

    monkeypatch.setattr(module_under_test.urllib.request, "urlopen", fake_urlopen)
    return contexts


def create_caller():
    caller = RestApiCaller.__new__(RestApiCaller)
    caller.baseURI = "https://aac.example.com:443/api/v2/"
    caller.directURI = "https://aac.example.com:443"
    caller.proxySetting = {}
    caller.accessToken = "token"
    caller.RestResultList = []
    return caller


@pytest.mark.parametrize("env_value", [None, "FALSE", "abc"])
def test_rest_call_without_verification_by_default(monkeypatch, mock_g, captured_context, env_value):
    """オフ（未設定・FALSE・不正値）: 証明書を検証しない context で接続する"""
    monkeypatch.delenv(ENV, raising=False)
    if env_value is not None:
        monkeypatch.setenv(ENV, env_value)
    create_caller().restCall("GET", "projects/")
    assert len(captured_context) == 1
    assert captured_context[0].verify_mode == ssl.CERT_NONE
    assert captured_context[0].check_hostname is False


def test_rest_call_with_verification(monkeypatch, mock_g, captured_context):
    """オン（TRUE）: 証明書とホスト名を検証する context で接続する"""
    monkeypatch.setenv(ENV, "TRUE")
    create_caller().restCall("GET", "projects/")
    assert len(captured_context) == 1
    assert captured_context[0].verify_mode == ssl.CERT_REQUIRED
    assert captured_context[0].check_hostname is True


def test_cert_verify_error_is_logged(monkeypatch, mock_g):
    """オン時に証明書検証エラーになると MSG-00037 が出力され、戻り値は通信エラーになる"""
    import urllib.error

    def fake_urlopen(req, context=None, timeout=None):
        raise urllib.error.URLError(ssl.SSLCertVerificationError(1, "certificate verify failed"))

    monkeypatch.setattr(module_under_test.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setenv(ENV, "TRUE")
    caller = create_caller()
    caller.apperrorloger = Mock()
    result = caller.restCall("GET", "projects/")
    assert result["statusCode"] == -2
    assert result["responseContents"] == {"errorMessage": "HTTP access error "}
    mock_g.appmsg.get_log_message.assert_any_call("MSG-00037", ["https://aac.example.com:443/api/v2/projects/", ENV])


def test_other_url_error_is_not_logged_as_cert_error(monkeypatch, mock_g):
    """証明書検証以外の通信エラーでは MSG-00037 を出力しない"""
    import urllib.error

    def fake_urlopen(req, context=None, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(module_under_test.urllib.request, "urlopen", fake_urlopen)
    caller = create_caller()
    caller.apperrorloger = Mock()
    result = caller.restCall("GET", "projects/")
    assert result["statusCode"] == -2
    mock_g.appmsg.get_log_message.assert_not_called()
