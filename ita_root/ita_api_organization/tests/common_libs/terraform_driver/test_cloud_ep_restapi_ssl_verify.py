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

from common_libs.terraform_driver.cloud_ep import RestApiCaller as module_under_test
from common_libs.terraform_driver.cloud_ep.RestApiCaller import RestApiCaller

ENV = "TERRAFORM_SSL_VERIFY_ENABLED"

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
    caller = RestApiCaller("https", "tfe.example.com", None, None, {})
    caller.accessToken = "token"
    return caller


def call_rest_call(caller):
    caller.rest_call("GET", "/organizations")


def call_get_log_data(caller):
    caller.get_log_data("GET", "https://tfe.example.com/logs", True, False)


@pytest.mark.parametrize("call", [call_rest_call, call_get_log_data])
@pytest.mark.parametrize("env_value", [None, "FALSE", "abc"])
def test_without_verification_by_default(monkeypatch, mock_g, captured_context, call, env_value):
    """オフ（未設定・FALSE・不正値）: 証明書を検証しない context で接続する（rest_call / get_log_data の 2 箇所）"""
    monkeypatch.delenv(ENV, raising=False)
    if env_value is not None:
        monkeypatch.setenv(ENV, env_value)
    call(create_caller())
    assert len(captured_context) >= 1
    for ctx in captured_context:
        assert ctx.verify_mode == ssl.CERT_NONE
        assert ctx.check_hostname is False


@pytest.mark.parametrize("call", [call_rest_call, call_get_log_data])
def test_with_verification(monkeypatch, mock_g, captured_context, call):
    """オン（TRUE）: 証明書とホスト名を検証する context で接続する（rest_call / get_log_data の 2 箇所）"""
    monkeypatch.setenv(ENV, "TRUE")
    call(create_caller())
    assert len(captured_context) >= 1
    for ctx in captured_context:
        assert ctx.verify_mode == ssl.CERT_REQUIRED
        assert ctx.check_hostname is True


def raise_cert_error(req, context=None, timeout=None):
    import urllib.error
    raise urllib.error.URLError(ssl.SSLCertVerificationError(1, "certificate verify failed"))


def raise_other_error(req, context=None, timeout=None):
    import urllib.error
    raise urllib.error.URLError("connection refused")


@pytest.mark.parametrize("call", [call_rest_call, call_get_log_data])
def test_cert_verify_error_is_logged(monkeypatch, mock_g, call):
    """証明書検証エラーになると MSG-00037 が出力される（rest_call / get_log_data の 2 箇所）"""
    monkeypatch.setenv(ENV, "TRUE")
    monkeypatch.setattr(module_under_test.urllib.request, "urlopen", raise_cert_error)
    caller = create_caller()
    caller.apperrorloger = Mock()
    caller.appinfologer = Mock()
    call(caller)
    args_list = [c.args for c in mock_g.appmsg.get_log_message.call_args_list]
    assert any(a[0] == "MSG-00037" and a[1][1] == ENV for a in args_list)


@pytest.mark.parametrize("call", [call_rest_call, call_get_log_data])
def test_other_error_is_not_logged_as_cert_error(monkeypatch, mock_g, call):
    """証明書検証以外のエラーでは MSG-00037 を出力しない"""
    monkeypatch.setattr(module_under_test.urllib.request, "urlopen", raise_other_error)
    caller = create_caller()
    caller.apperrorloger = Mock()
    caller.appinfologer = Mock()
    call(caller)
    mock_g.appmsg.get_log_message.assert_not_called()
