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
ダウンストリームAPI呼び出し用の共通ヘッダー組み立てモジュール

tools/*.py の各ツールがITA/Exastro Platformのダウンストリームapiを呼び出す際に
共通で必要となるヘッダー(User-Id / Roles / Org-Roles / Language)の組み立てを
ここに集約する。ツール個別のモジュール(例: tools/platform_user.py)には
依存しない、複数のツールから使い回せる共通処理として libs 配下に置く。

--------------------------------------------------------------------------
Common module for building the headers used when calling downstream APIs.

Centralizes the construction of the headers (User-Id / Roles / Org-Roles /
Language) that every tool under tools/*.py needs when it calls a downstream
ITA / Exastro Platform API. Placed under libs/ (rather than inside a
specific tool module such as tools/platform_user.py) so that it can be
shared across multiple tools.
"""
from flask import request


def build_forward_headers() -> dict:
    """
    ダウンストリームAPI呼び出し用のヘッダーを組み立てる。

    受信したリクエストの "User-Id" / "Roles" / "Org-Roles" ヘッダーを、
    そのままの値で転送する(認証プロキシが付与したものと同じ形式のまま渡す)。
    "Org-Roles" はワークスペースのロール("Roles")とは別に、組織レベルの
    ロールを表すヘッダーで、"Roles"と同様にBase64エンコードされた
    改行区切りのロール一覧が入っている。

    Build the headers used when calling a downstream API.

    Forwards the "User-Id" / "Roles" / "Org-Roles" headers of the incoming
    request as-is (kept in the exact same form as injected by the
    authentication proxy). "Org-Roles" carries the organization-level roles
    (as opposed to "Roles", which carries the workspace-level roles), and
    uses the same Base64-encoded, newline-separated format as "Roles".

    Returns:
        dict: 転送用ヘッダー / headers to forward
    """
    headers = {
        "Content-Type": "application/json",
        # 受信したリクエストヘッダーからそのまま取得して転送する
        # Read directly from the incoming request headers and forward as-is
        "User-Id": request.headers.get("User-Id"),
        "Roles": request.headers.get("Roles"),
        "Org-Roles": request.headers.get("Org-Roles"),
        # Language はリクエストの値を転送せず、常に "en" 固定で送る
        # (レスポンスのメッセージ言語をAPI呼び出し間で一定に保つため)
        # Language is not forwarded from the incoming request; it is always
        # fixed to "en" (to keep the response message language consistent
        # across API calls)
        "Language": "en",
    }

    return headers
