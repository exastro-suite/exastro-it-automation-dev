#   Copyright 2026 NEC Corporation
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

"""
外部通信の SSL 証明書検証を環境変数で切り替える共通関数
Common functions to switch SSL certificate verification of external communication by environment variables

- 環境変数は <機能>_SSL_VERIFY_ENABLED （TRUE/FALSE）。既定は FALSE（検証しない）
"""
import os
import ssl

# 環境変数名 / environment variable names
ENV_ANSIBLE_AAP = "ANSIBLE_AAP_SSL_VERIFY_ENABLED"
ENV_TERRAFORM = "TERRAFORM_SSL_VERIFY_ENABLED"
ENV_CONDUCTOR_NOTICE = "CONDUCTOR_NOTICE_SSL_VERIFY_ENABLED"
ENV_EVENT_COLLECTION = "EVENT_COLLECTION_SSL_VERIFY_ENABLED"
ENV_AGENT = "AGENT_SSL_VERIFY_ENABLED"


def is_ssl_verify_enabled(env_name):
    """証明書検証が有効か / Whether certificate verification is enabled

    Args:
        env_name (str): 環境変数名 / environment variable name

    Returns:
        bool: TRUE（大文字小文字・前後空白は無視）のときのみ True。未設定・不正値は False
    """
    try:
        value = os.environ.get(env_name)
        if value is None:
            return False
        return str(value).strip().upper() == "TRUE"
    except Exception:
        return False


def get_ssl_context(env_name):
    """urllib 用の ssl context を返す / Return ssl context for urllib

    Args:
        env_name (str): 環境変数名

    Returns:
        ssl.SSLContext: 有効なら ssl.create_default_context()、無効なら ssl._create_unverified_context()
    """
    if is_ssl_verify_enabled(env_name):
        return ssl.create_default_context()
    return ssl._create_unverified_context()


def get_requests_verify(env_name):
    """requests 用の verify 値を返す / Return verify value for requests

    Args:
        env_name (str): 環境変数名

    Returns:
        bool: 有効なら True、無効なら False
    """
    return is_ssl_verify_enabled(env_name)


def is_cert_verify_error(exc):
    """証明書検証失敗によるエラーか判定する / Whether the exception is caused by certificate verification failure

    urllib の URLError(reason=SSLCertVerificationError) や、requests の SSLError
    （urllib3 の MaxRetryError → SSLError → SSLCertVerificationError と包まれる）のように、
    例外が別の例外を包んでいる場合も、包まれた例外をたどって判定する。
    証明書検証失敗以外の SSL エラー・他の例外は False。例外を投げない。

    Args:
        exc (BaseException): 判定対象の例外

    Returns:
        bool: 証明書検証失敗なら True
    """
    try:
        stack = [exc]
        visited = set()
        while stack and len(visited) < 20:
            current = stack.pop()
            if not isinstance(current, BaseException) or id(current) in visited:
                continue
            visited.add(id(current))
            if isinstance(current, ssl.SSLCertVerificationError):
                return True
            stack.append(current.__cause__)
            stack.append(current.__context__)
            stack.append(getattr(current, "reason", None))
            for arg in getattr(current, "args", ()):
                stack.append(arg)
    except Exception:
        return False
    return False


def log_cert_verify_error(exc, destination, env_name):
    """証明書検証失敗の場合に MSG-00037 をログ出力する / Output MSG-00037 log when certificate verification failed

    証明書検証失敗でない場合は何もしない。呼び出し元の既存の例外処理・戻り値は変えない。
    ログ出力自体が失敗しても例外を投げない。

    Args:
        exc (BaseException): 発生した例外
        destination (str): 接続先（URL またはホスト）
        env_name (str): 検証を切り替える環境変数名

    Returns:
        bool: 証明書検証失敗としてログ出力した場合 True
    """
    try:
        if not is_cert_verify_error(exc):
            return False
        from flask import g
        g.applogger.error(g.appmsg.get_log_message("MSG-00037", [destination, env_name]))
        return True
    except Exception:
        return False
