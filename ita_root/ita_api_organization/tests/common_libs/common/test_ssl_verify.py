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

import pytest

from common_libs.common.ssl_verify import (
    ENV_ANSIBLE_AAP,
    ENV_CONDUCTOR_NOTICE,
    ENV_AGENT,
    ENV_EVENT_COLLECTION,
    ENV_TERRAFORM,
    get_requests_verify,
    get_ssl_context,
    is_ssl_verify_enabled,
)

ENV_NAMES = [ENV_ANSIBLE_AAP, ENV_TERRAFORM, ENV_CONDUCTOR_NOTICE, ENV_EVENT_COLLECTION, ENV_AGENT]


def test_env_names():
    """環境変数名が Issue の定義と一致する"""
    assert ENV_NAMES == [
        "ANSIBLE_AAP_SSL_VERIFY_ENABLED",
        "TERRAFORM_SSL_VERIFY_ENABLED",
        "CONDUCTOR_NOTICE_SSL_VERIFY_ENABLED",
        "EVENT_COLLECTION_SSL_VERIFY_ENABLED",
        "AGENT_SSL_VERIFY_ENABLED",
    ]


@pytest.mark.parametrize("value, expected", [
    (None, False),        # 未設定
    ("", False),
    ("FALSE", False),
    ("false", False),
    ("TRUE", True),
    ("true", True),
    ("True", True),
    ("  TRUE  ", True),   # 前後の空白は無視
    ("1", False),         # 不正値は False
    ("yes", False),
    ("TRUEX", False),
])
@pytest.mark.parametrize("env_name", ENV_NAMES)
def test_is_ssl_verify_enabled(monkeypatch, env_name, value, expected):
    """TRUE のときだけ有効。未設定・不正値は False"""
    monkeypatch.delenv(env_name, raising=False)
    if value is not None:
        monkeypatch.setenv(env_name, value)
    assert is_ssl_verify_enabled(env_name) is expected


def test_get_ssl_context_disabled(monkeypatch):
    """オフ（既定）: 検証しない context（ssl._create_unverified_context と同じ設定）"""
    monkeypatch.delenv(ENV_ANSIBLE_AAP, raising=False)
    ctx = get_ssl_context(ENV_ANSIBLE_AAP)
    assert ctx.verify_mode == ssl.CERT_NONE
    assert ctx.check_hostname is False


def test_get_ssl_context_enabled(monkeypatch):
    """オン: 証明書とホスト名を検証する context"""
    monkeypatch.setenv(ENV_ANSIBLE_AAP, "TRUE")
    ctx = get_ssl_context(ENV_ANSIBLE_AAP)
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.check_hostname is True


def test_get_requests_verify(monkeypatch):
    """requests 用 verify 値: オフ=False / オン=True"""
    monkeypatch.delenv(ENV_AGENT, raising=False)
    assert get_requests_verify(ENV_AGENT) is False
    monkeypatch.setenv(ENV_AGENT, "TRUE")
    assert get_requests_verify(ENV_AGENT) is True
    monkeypatch.setenv(ENV_AGENT, "FALSE")
    assert get_requests_verify(ENV_AGENT) is False


def test_does_not_raise(monkeypatch):
    """例外を投げない（不正値でも）"""
    monkeypatch.setenv(ENV_AGENT, "あいう")
    assert is_ssl_verify_enabled(ENV_AGENT) is False
    assert get_requests_verify(ENV_AGENT) is False
    assert get_ssl_context(ENV_AGENT).verify_mode == ssl.CERT_NONE


# ---------------------------------------------------------------------------
# 証明書検証エラーの判定とログ出力 (MSG-00037)
# ---------------------------------------------------------------------------
import requests
import urllib3
from unittest.mock import Mock
from urllib.error import URLError

from flask import Flask, g

from common_libs.common.ssl_verify import is_cert_verify_error, log_cert_verify_error


def create_cert_error():
    return ssl.SSLCertVerificationError(1, "certificate verify failed: self-signed certificate")


def create_requests_cert_error():
    """requests が証明書検証失敗で投げる例外（MaxRetryError -> urllib3 SSLError -> SSLCertVerificationError と包まれる）"""
    ssl_error = urllib3.exceptions.SSLError(create_cert_error())
    max_retry = urllib3.exceptions.MaxRetryError(None, "https://dummy", reason=ssl_error)
    return requests.exceptions.SSLError(max_retry)


@pytest.mark.parametrize("exc, expected", [
    (create_cert_error(), True),
    (URLError(create_cert_error()), True),
    (create_requests_cert_error(), True),
    (ssl.SSLError(1, "handshake failure"), False),                       # 証明書検証以外の SSL エラー
    (requests.exceptions.SSLError(urllib3.exceptions.SSLError("x")), False),
    (requests.exceptions.ConnectionError("refused"), False),
    (URLError("timed out"), False),
    (Exception("other"), False),
    (None, False),
])
def test_is_cert_verify_error(exc, expected):
    """証明書検証失敗だけを判別する。他の SSL エラー・例外は False"""
    assert is_cert_verify_error(exc) is expected


@pytest.fixture
def mock_g():
    app = Flask(__name__)
    with app.app_context():
        g.applogger = Mock()
        g.appmsg = Mock()
        g.appmsg.get_log_message = Mock(side_effect=lambda msg_id, args=None: "{}:{}".format(msg_id, args))
        yield g


def test_log_cert_verify_error_outputs_msg_00037(mock_g):
    """証明書検証失敗なら MSG-00037 を（接続先、環境変数名）で出力する"""
    assert log_cert_verify_error(URLError(create_cert_error()), "https://aac.example.com/api", ENV_ANSIBLE_AAP) is True
    mock_g.appmsg.get_log_message.assert_called_once_with("MSG-00037", ["https://aac.example.com/api", ENV_ANSIBLE_AAP])
    mock_g.applogger.error.assert_called_once()


def test_log_cert_verify_error_ignores_other_errors(mock_g):
    """証明書検証失敗でなければ何も出力しない"""
    assert log_cert_verify_error(URLError("timed out"), "https://x", ENV_ANSIBLE_AAP) is False
    mock_g.applogger.error.assert_not_called()


def test_log_cert_verify_error_does_not_raise_without_flask_context():
    """flask の g が無くても（ログ出力に失敗しても）例外を投げない"""
    assert log_cert_verify_error(create_cert_error(), "https://x", ENV_ANSIBLE_AAP) is False
