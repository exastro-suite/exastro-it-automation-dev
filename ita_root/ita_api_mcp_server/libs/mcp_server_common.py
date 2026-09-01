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
#
"""
mcp_server common function module

ita_api_organization/libs/organization_common.py および
ita_api_admin/libs/admin_common.py の before_request_handler を参考に、
このサービス(ita_api_mcp_server)用の共通処理(ログ出力・メッセージ管理・
リクエストヘッダーチェック)を実装したモジュール。

ita_api_mcp_server は connexion を使わず、素の Flask で
MCP(Model Context Protocol)の JSON-RPC リクエストを直接受け付ける構成とする。

認証については、ita_api_mcp_server の前段に認証プロキシが配置され、
ita_api_organization / ita_api_admin と同様に "User-Id" と "Roles" が
HTTPヘッダーとして渡ってくる想定のため、ここでは Bearer JWT の検証は行わず、
organization/admin と同じヘッダーチェック方式を採用する。

--------------------------------------------------------------------------
This module implements the common processing (logging / message handling /
request header validation) for this service (ita_api_mcp_server), based on
the before_request_handler implementations found in
ita_api_organization/libs/organization_common.py and
ita_api_admin/libs/admin_common.py.

ita_api_mcp_server does not use connexion; it accepts MCP(Model Context
Protocol) JSON-RPC requests directly via plain Flask.

Regarding authentication: an authentication proxy sits in front of
ita_api_mcp_server, and just like ita_api_organization / ita_api_admin, the
"User-Id" and "Roles" values are injected as HTTP headers by that proxy.
Therefore this module does NOT verify a Bearer JWT itself; instead it reuses
the same header-based check used by organization/admin.
"""
import base64
import os
import re

from flask import request, g

# common_libs 配下のファイルは変更しない(既存の共通ライブラリをそのまま利用する)
# Files under common_libs are NOT modified; we simply reuse the existing common library.
from common_libs.common.exception import AppException
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate
from common_libs.api import set_api_timestamp, get_api_timestamp, app_exception_response, exception_response, check_request_body

# ヘルスチェック用URLかどうかを判定する正規表現
# (organization_common.py / admin_common.py と同じパターン)
#
# Regex used to detect health-check URLs.
# (Same pattern as organization_common.py / admin_common.py)
HEALTH_CHECK_URL_PATTERN = r"/internal-api/health-check/liveness$|/internal-api/health-check/readiness$"


def before_request_handler():
    """
    called before each request is handled (Flask `before_request` hook)

    Flaskの `before_request` として登録されるフック関数。
    organization/admin と同様に、リクエストごとに以下を行う。
      1. APIタイムスタンプの設定
      2. AppLog(ログ出力クラス)・MessageTemplate(メッセージ管理クラス)の初期化
      3. リクエストボディの形式チェック
      4. ヘルスチェック用URL以外の場合、User-Id/Rolesヘッダーのチェックと
         organization_id/workspace_idの特定

    Registered as Flask's `before_request` hook.
    For every incoming request (mirrors organization/admin), this function:
      1. sets the API timestamp used in log output
      2. initializes AppLog (g.applogger) and MessageTemplate (g.appmsg)
      3. validates the request body content-type/format
      4. for non health-check URLs, validates the "User-Id"/"Roles" headers
         and resolves organization_id / workspace_id from the URL path
    """
    try:
        # APIタイムスタンプをセットする(ログ出力時刻の基準として使用)
        # Set the API timestamp (used as the reference time in log lines)
        set_api_timestamp()

        # デフォルト言語を環境変数から取得する
        # Read the default language from the environment variable
        g.LANGUAGE = os.environ.get("DEFAULT_LANGUAGE")

        # ログ出力クラス・メッセージ管理クラスのインスタンスを生成する
        # Create the log-output class instance and the message-template class instance
        g.applogger = AppLog()
        g.appmsg = MessageTemplate(g.LANGUAGE)

        # リクエストボディがContent-Typeに応じた正しい形式かどうかをチェックする
        # Check that the request body matches the format implied by its Content-Type
        check_request_body()

        # ヘルスチェック用のURLの場合は、User-Id/Rolesのチェックや
        # organization_id/workspace_idの特定を行わない(healthチェックには不要なため)
        #
        # For health-check URLs, skip the User-Id/Roles validation and the
        # organization_id/workspace_id resolution below (not needed for a health check).
        if re.search(HEALTH_CHECK_URL_PATTERN, request.url) is None:
            # MCPのエンドポイントは "/api/<organization_id>/workspaces/<workspace_id>/mcp" の
            # 形式(ita_api_organizationのURL設計を踏襲)なので、パスを"/"で分割して
            # organization_id(index=2)・workspace_id(index=4)を取得する。
            #
            # The MCP endpoint URL is shaped like
            # "/api/<organization_id>/workspaces/<workspace_id>/mcp"
            # (following ita_api_organization's URL design), so we split the path
            # by "/" and take organization_id at index 2 and workspace_id at index 4.
            organization_id = request.path.split("/")[2]
            g.ORGANIZATION_ID = organization_id
            workspace_id = request.path.split("/")[4]
            g.WORKSPACE_ID = workspace_id

            # 認証プロキシが付与する "User-Id" ヘッダーを取得する
            # Get the "User-Id" header injected by the authentication proxy
            user_id = request.headers.get("User-Id")

            # 認証プロキシが付与する "Roles" ヘッダー(Base64エンコード済み、
            # 改行区切りのロール一覧)を取得し、デコードする
            #
            # Get the "Roles" header injected by the authentication proxy
            # (Base64-encoded, newline-separated list of roles) and decode it
            roles_org = request.headers.get("Roles")
            try:
                roles_decode = base64.b64decode(roles_org.encode()).decode("utf-8")
            except Exception:
                # Base64デコードに失敗した場合はヘッダー不正としてエラーにする
                # If Base64 decoding fails, treat it as an invalid header and raise an error
                raise AppException("400-00001", ["Roles"], ["Roles"])
            roles = roles_decode.split("\n")

            # User-Id または Roles が取得できない場合はリクエストヘッダー不正とする
            # If either User-Id or Roles could not be resolved, the request header is invalid
            if user_id is None or roles is None or type(roles) is not list:
                raise AppException("400-00001", ["User-Id or Roles"], ["User-Id or Roles"])

            # 取得したUser-Id/Rolesをリクエストスコープ(g)に保存する
            # tools/*.py からダウンストリームAPIを呼び出す際にも、
            # 元のHTTPヘッダー(request.headers)から直接参照して転送する。
            #
            # Store the resolved User-Id/Roles on the request-scoped `g` object.
            # When tools/*.py calls a downstream API, it forwards the ORIGINAL
            # HTTP header values (read again from request.headers) as-is.
            g.USER_ID = user_id
            g.ROLES = roles

            # ログ出力の接頭辞([ORGANIZATION_ID:xxx]など)を設定する
            # Configure the log line prefix (e.g. "[ORGANIZATION_ID:xxx]")
            g.applogger.set_env_message()

            # APIリクエスト開始のログを出力する
            # Log that an API request has started
            debug_args = [request.method + ":" + request.url]
            g.applogger.info("[ts={}][api-start] url:{}".format(get_api_timestamp(), *debug_args))

        # リクエストヘッダーに言語指定がある場合、優先してその言語を使用する
        # If the request header specifies a language, prefer that language
        language = request.headers.get("Language")
        if language:
            g.LANGUAGE = language
            g.appmsg.set_lang(language)
            g.applogger.debug("LANGUAGE({}) is set".format(language))

        # NOTE:
        # organization_common.py / admin_common.py ではここで
        # 組織DB・ワークスペースDBへの接続確認(DBConnectOrg/DBConnectWs)や
        # メンテナンスモード確認(get_maintenance_mode_setting)、
        # サービス単位のログレベル設定(set_service_loglevel)を行っていますが、
        # ita_api_mcp_server の現在のスコープ(platform_user.pyツールのみ)では
        # ITAのデータベースに直接アクセスしないため、これらのDB接続処理は
        # 一旦組み込んでいません。
        # 今後、ITAのDB(MariaDB)を利用するツールを追加する場合は、
        # common_libs.common.dbconnect の DBConnectCommon 等を用いて
        # organization/admin と同様の接続処理を追加してください。
        #
        # organization_common.py / admin_common.py additionally connect to the
        # organization/workspace database (DBConnectOrg/DBConnectWs), check the
        # maintenance mode (get_maintenance_mode_setting), and configure the
        # per-service log level (set_service_loglevel) here.
        # Because the current scope of ita_api_mcp_server (the platform_user.py
        # tool only) does not access ITA's database directly, that
        # database-connection handling is intentionally left out for now.
        # When a future tool needs ITA's database (MariaDB), add the same
        # common_libs.common.dbconnect based connection handling used by
        # organization/admin.
    except AppException as e:
        # AppException(業務エラー)を捕捉し、ITA共通のエラーレスポンス形式に変換する
        # Catch AppException (business error) and convert it into ITA's common error response
        return app_exception_response(e)
    except Exception as e:
        # その他の予期しない例外を捕捉し、500エラーのレスポンスに変換する
        # Catch any other unexpected exception and convert it into a 500 error response
        return exception_response(e)


def log_api_end(status_code, is_success=True):
    """
    APIリクエスト終了のログを出力する

    before_request_handler で出力する [api-start] と対になるログ。
    ita_api_mcp_server は make_response (common_libs.api.util) を経由せず
    独自にレスポンスを組み立てているため、jsonrpc_handler 側の各応答生成箇所
    (api.py の create_error_response / 正常応答)から明示的に呼び出す。

    Log that an API request has finished ([api-end]).

    This pairs with the [api-start] log emitted by before_request_handler.
    Because ita_api_mcp_server builds its responses directly instead of going
    through common_libs.api.util.make_response, this must be called explicitly
    from each place api.py builds a response (create_error_response / the
    success response in jsonrpc_handler).
    """
    log_status = "SUCCESS" if is_success else "FAILURE"
    g.applogger.info("[ts={}][api-end][{}][status_code={}]".format(get_api_timestamp(), log_status, status_code))
