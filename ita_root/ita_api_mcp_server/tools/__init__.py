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
MCP Server Tools (ita_api_mcp_server が提供するMCPツール群)

このパッケージをimportすると、配下の各モジュールに定義された
@tool デコレーター付き関数が libs.tools_decorator.TOOL_REGISTRY に登録される。

今回のスコープでは platform_user.py のツール(list-users / create-user)
のみを対象とするため、他のツールはまだ登録していない。
今後、別のツールを追加する場合はこのファイルにimport文を追加すること。

--------------------------------------------------------------------------
MCP Server Tools provided by ita_api_mcp_server.

Importing this package causes every @tool-decorated function defined in the
modules below to be registered into libs.tools_decorator.TOOL_REGISTRY.

The current scope only covers the platform_user.py tools (list-users /
create-user); other tools are not registered yet.
Add an import statement here when a new tool module is added in the future.
"""
# platform_user.py の @tool デコレーター付き関数を登録するためにimportする
# Import platform_user.py so that its @tool-decorated functions get registered
from . import platform_user

__all__ = [
    "platform_user"
]
