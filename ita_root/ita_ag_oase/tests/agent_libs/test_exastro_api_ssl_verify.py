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

import importlib.util
import os

import pytest

ENV = "AGENT_SSL_VERIFY_ENABLED"

# agent/libs/exastro_api.py をファイルパスから読み込む（agent パッケージは ita_root 直下にあり、各モジュールの sys.path に無いため）
_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent", "libs", "exastro_api.py")
_spec = importlib.util.spec_from_file_location("exastro_api_under_test", os.path.abspath(_path))
exastro_api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exastro_api)


class DummyResponse:
    status_code = 200
    text = "{}"

    def json(self):
        return {"access_token": "dummy"}


@pytest.fixture
def captured(monkeypatch):
    """requests.request に渡された verify を記録する"""
    calls = []

    def dummy_request(*args, **kwargs):
        calls.append(kwargs)
        return DummyResponse()

    monkeypatch.setattr(exastro_api.requests, "request", dummy_request)
    return calls


def call_all(api):
    api.api_request("GET", "/x")
    api.api_request_formdata("POST", "/x")
    api.api_request_stream("POST", "/x")
    api.api_request_formdata_stream_file("POST", "/x", fields={"a": "b"})
    api.get_access_token("org")


@pytest.mark.parametrize("env_value, expected", [
    (None, False),      # 既定: 検証しない
    ("FALSE", False),
    ("TRUE", True),
    ("abc", False),     # 不正値は False
])
def test_verify_value_for_all_requests(monkeypatch, captured, env_value, expected):
    """5 つの API 呼び出しすべてで、環境変数に応じた verify が渡される"""
    monkeypatch.delenv(ENV, raising=False)
    if env_value is not None:
        monkeypatch.setenv(ENV, env_value)
    api = exastro_api.Exastro_API("http://dummy", username="u", password="p")
    call_all(api)
    assert len(captured) == 5
    assert [c["verify"] for c in captured] == [expected] * 5


def test_disable_warnings_kept():
    """警告抑止（urllib3.disable_warnings）はモジュール直下（読み込み時）に残っている"""
    with open(exastro_api.__file__, encoding="utf-8") as f:
        lines = f.read().split("\n")
    assert "urllib3.disable_warnings(InsecureRequestWarning)" in lines


def test_cert_verify_error_is_logged_and_exception_unchanged(monkeypatch):
    """証明書検証エラー時に MSG-00037 が出力され、例外は AppException(AGT-00004)"""
    import ssl
    from unittest.mock import Mock
    from flask import Flask, g
    from common_libs.common.exception import AppException
    import requests
    import urllib3

    def raise_cert_error(*args, **kwargs):
        ssl_error = urllib3.exceptions.SSLError(ssl.SSLCertVerificationError(1, "certificate verify failed"))
        raise requests.exceptions.SSLError(urllib3.exceptions.MaxRetryError(None, "https://dummy", reason=ssl_error))

    monkeypatch.setattr(exastro_api.requests, "request", raise_cert_error)
    monkeypatch.setenv(ENV, "TRUE")
    app = Flask(__name__)
    with app.app_context():
        g.applogger = Mock()
        g.appmsg = Mock()
        g.appmsg.get_log_message = Mock(side_effect=lambda msg_id, args=None: (msg_id, args))
        api = exastro_api.Exastro_API("https://dummy", username="u", password="p")
        with pytest.raises(AppException) as exc_info:
            api.api_request("GET", "/x")
        assert exc_info.value.args[0] == "AGT-00004"
        g.appmsg.get_log_message.assert_any_call("MSG-00037", ["https://dummy/x", ENV])


def test_other_error_is_not_logged_as_cert_error(monkeypatch):
    """証明書検証以外の例外では MSG-00037 を出力しない"""
    from unittest.mock import Mock
    from flask import Flask, g
    from common_libs.common.exception import AppException

    def raise_conn_error(*args, **kwargs):
        raise exastro_api.requests.exceptions.ConnectionError("refused")

    monkeypatch.setattr(exastro_api.requests, "request", raise_conn_error)
    app = Flask(__name__)
    with app.app_context():
        g.applogger = Mock()
        g.appmsg = Mock()
        api = exastro_api.Exastro_API("https://dummy", username="u", password="p")
        with pytest.raises(AppException):
            api.api_request("GET", "/x")
        g.appmsg.get_log_message.assert_not_called()
