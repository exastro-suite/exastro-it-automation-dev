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
ITA Conductorツール ("create-conductor" / "get-conductor-class-info")

ITAのConductorクラスの登録および情報取得を行うツール。

  - create-conductor : menu(メニュー名)・conductor_data(Conductorの構成情報)を
    受け取り、Conductorクラスを新規登録する。
  - get-conductor-class-info : menu(メニュー名)を受け取り、ConductorClassの
    基本情報を取得する。

呼び出し先のITAのAPI(ita_api_organization)は、受け取った
menu(URLパスパラメータ)そのものに対してメニュー権限をチェックしている
(controllers/conductor_controll_controller.py の post_conductor_data が
check_sheet_type(menu, ['14'], ...) および check_auth_menu(menu, ...) を
実行している)。このAPIに指定可能なmenu_name_restは、Conductorクラス編集
メニューである conductor_class_edit であるため、@tool デコレーターの
required_menu にこれを指定する。

--------------------------------------------------------------------------
ITA Conductor tools ("create-conductor" / "get-conductor-class-info")

Registers and retrieves information about ITA Conductor classes.

  - create-conductor : accepts menu (menu name) and conductor_data (the
    Conductor configuration), and registers a new Conductor class.
  - get-conductor-class-info : accepts menu (menu name) and retrieves the
    basic information of a Conductor class.

The downstream ITA API (ita_api_organization) checks menu permission against
the `menu` value itself (a URL path parameter): post_conductor_data in
controllers/conductor_controll_controller.py calls
check_sheet_type(menu, ['14'], ...) and check_auth_menu(menu, ...). The
menu_name_rest that may be passed as `menu` for this API is the Conductor
class edit menu, conductor_class_edit, so the @tool decorator's
required_menu specifies it.
"""
import os

import requests
from flask import g

from libs import tool, HTTPException, build_forward_headers

# create-conductorが対象とするmenuのmenu_name_rest
# menu_name_rest of the menu targeted by create-conductor
_REQUIRED_MENU_CONDUCTOR_EDIT = [
    "conductor_class_edit",
]


@tool(
    name="create-conductor",
    description=(
        "Register a new ITA Conductor class. conductor_data is the Conductor configuration JSON "
        "(the same format as the Conductor class edit screen), and must include a 'conductor' "
        "object with 'conductor_name' (and optionally 'note'), along with the node/line definitions. "
        "Before use, refer to `tool-reference/conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'conductor_class_edit'."
            },
            "conductor_data": {
                "type": "object",
                "description": "Conductor configuration to register"
            }
        },
        "required": ["menu", "conductor_data"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EDIT,
    profile=["AgenticAI"]
)
def tool_create_conductor(arguments: dict, payload: dict) -> dict:
    """
    Conductorクラスを新規登録する

    Register a new Conductor class.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_data (dict): 登録するConductorの構成情報
              / the Conductor configuration to register
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor登録結果
            - result: APIレスポンスの登録結果 / the registration result returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name

    Raises:
        Exception: menuまたはconductor_dataが指定されていない場合
            / if menu or conductor_data is not specified
        HTTPException: Conductorの登録に失敗した場合 / if registering the Conductor fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_data = arguments.get("conductor_data", {})

    if not menu:
        raise Exception("menu is required")
    if not conductor_data:
        raise Exception("conductor_data is required")

    g.applogger.info(f"Parameter menu={menu}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/class/maintenance/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/class/maintenance/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/class/maintenance/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu
    )

    # 転送用ヘッダーを組み立てる(POSTでボディを送るため"Content-Type"も付与する)
    # Build the headers to forward (also adds "Content-Type" since this is a POST with a body)
    headers = build_forward_headers(method="POST")

    # ITAのAPIへConductor新規登録のPOSTリクエストを送信する
    # Send a POST request to ITA's API to register the new Conductor
    req = requests.post(url, json=conductor_data, headers=headers)

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to create conductor: {} - {}".format(req.status_code, req.text))
        raise HTTPException("create-conductor", req)

    return {
        "result": req.json(),
        "message": "Conductor created successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu
    }
