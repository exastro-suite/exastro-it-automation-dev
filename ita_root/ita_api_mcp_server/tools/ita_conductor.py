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
ITA Conductorツール ("create-conductor" / "update-conductor" / "execute-conductor" / "get-conductor-class" / "get-conductor-instance" / "get-conductor-input-data" / "get-conductor-result-data")

ITAのConductorクラスの登録、更新、情報取得、および作業実行を行うツール。

  - create-conductor : menu(メニュー名)・conductor_data(Conductorの構成情報)を
    受け取り、Conductorクラスを新規登録する。
  - update-conductor : menu(メニュー名)・conductor_class_id(Conductor Class ID)・
    conductor_data(Conductorの構成情報)を受け取り、Conductorクラスを更新する。
  - get-conductor-class-info : menu(メニュー名)を受け取り、ConductorClassの
    基本情報を取得する。
  - execute-conductor : menu(メニュー名)・実行パラメータを受け取り、
    Conductor作業を実行する。
  - get-conductor-execution-info : menu(メニュー名)・conductor_instance_id
    を受け取り、Conductor作業の基本情報を取得する。
  - get-conductor-class : menu(メニュー名)・conductor_class_id(Conductor Class ID)を
    受け取り、Conductorクラスの情報を取得する。
  - get-conductor-instance : menu(メニュー名)・conductor_instance_idを
    受け取り、Conductor作業の詳細情報を取得する。
  - get-conductor-input-data : menu(メニュー名)・conductor_instance_idを
    受け取り、Conductor作業の投入データを取得する。
  - get-conductor-result-data : menu(メニュー名)・conductor_instance_idを
    受け取り、Conductor作業の結果データを取得する。

呼び出し先のITAのAPI(ita_api_organization)は、受け取った
menu(URLパスパラメータ)そのものに対してメニュー権限をチェックしている
(controllers/conductor_controll_controller.py の post_conductor_data および
patch_conductor_data が check_sheet_type(menu, ['14'], ...) および
check_auth_menu(menu, ...) を実行している)。このAPIに指定可能な
menu_name_restは、Conductorクラス編集メニューである conductor_class_edit
であるため、@tool デコレーターの required_menu にこれを指定する。

--------------------------------------------------------------------------
ITA Conductor tools ("create-conductor" / "update-conductor" / "execute-conductor" / "get-conductor-class" / "get-conductor-instance" / "get-conductor-input-data" / "get-conductor-result-data")

Registers, updates, retrieves information, and executes ITA Conductor classes.

  - create-conductor : accepts menu (menu name) and conductor_data (the
    Conductor configuration), and registers a new Conductor class.
  - update-conductor : accepts menu (menu name), conductor_class_id (Conductor Class ID),
    and conductor_data (the Conductor configuration), and updates an existing Conductor class.
  - get-conductor-class-info : accepts menu (menu name) and retrieves the
    basic information of a Conductor class.
  - execute-conductor : accepts menu (menu name) and execution parameters,
    and executes a Conductor operation.
  - get-conductor-execution-info : accepts menu (menu name) and conductor_instance_id,
    and retrieves the basic information of a Conductor execution.
  - get-conductor-class : accepts menu (menu name) and conductor_class_id (Conductor Class ID),
    and retrieves information about a Conductor class.
  - get-conductor-instance : accepts menu (menu name) and conductor_instance_id,
    and retrieves detailed information of a Conductor execution.
  - get-conductor-input-data : accepts menu (menu name) and conductor_instance_id,
    and retrieves the input data of a Conductor execution.
  - get-conductor-result-data : accepts menu (menu name) and conductor_instance_id,
    and retrieves the result data of a Conductor execution.

The downstream ITA API (ita_api_organization) checks menu permission against
the `menu` value itself (a URL path parameter): post_conductor_data and
patch_conductor_data in controllers/conductor_controll_controller.py call
check_sheet_type(menu, ['14'], ...) and check_auth_menu(menu, ...). The
menu_name_rest that may be passed as `menu` for this API is the Conductor
class edit menu, conductor_class_edit, so the @tool decorator's
required_menu specifies it.
"""
import os

import requests
from flask import g

from libs import tool, HTTPException, build_forward_headers, get_downstream_timeout

# create-conductorが対象とするmenuのmenu_name_rest
# menu_name_rest of the menu targeted by create-conductor
_REQUIRED_MENU_CONDUCTOR_EDIT = [
    "conductor_class_edit",
]

# execute-conductorが対象とするmenuのmenu_name_rest
# menu_name_rest of the menu targeted by execute-conductor
_REQUIRED_MENU_CONDUCTOR_EXECUTE = [
    "conductor_class_edit",
    "execution_list",
]


@tool(
    name="create-conductor",
    description=(
        "Register a new ITA Conductor class. conductor_data is the Conductor configuration JSON "
        "(the same format as the Conductor class edit screen), and must include a 'conductor' "
        "object with 'conductor_name' (and optionally 'note'), along with the node/line definitions. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
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
    req = requests.post(url, json=conductor_data, headers=headers, timeout=get_downstream_timeout())

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


@tool(
    name="update-conductor",
    description=(
        "Update an existing ITA Conductor class. conductor_class_id is the ID of the Conductor class "
        "to update, and conductor_data is the updated Conductor configuration JSON "
        "(the same format as the Conductor class edit screen), which must include a 'conductor' "
        "object with 'conductor_name' (and optionally 'note'), along with the node/line definitions. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'conductor_class_edit'."
            },
            "conductor_class_id": {
                "type": "string",
                "description": "Conductor Class ID to update"
            },
            "conductor_data": {
                "type": "object",
                "description": "Updated Conductor configuration"
            }
        },
        "required": ["menu", "conductor_class_id", "conductor_data"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EDIT,
    profile=["AgenticAI"]
)
def tool_update_conductor(arguments: dict, payload: dict) -> dict:
    """
    Conductorクラスを更新する

    Update an existing Conductor class.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_class_id (str): 更新するConductor Class ID
              / Conductor Class ID to update
            - conductor_data (dict): 更新するConductorの構成情報
              / the updated Conductor configuration
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor更新結果
            - result: APIレスポンスの更新結果 / the update result returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - conductor_class_id (str): Conductor Class ID

    Raises:
        Exception: menu、conductor_class_id、またはconductor_dataが指定されていない場合
            / if menu, conductor_class_id, or conductor_data is not specified
        HTTPException: Conductorの更新に失敗した場合 / if updating the Conductor fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_class_id = arguments.get("conductor_class_id", "")
    conductor_data = arguments.get("conductor_data", {})

    if not menu:
        raise Exception("menu is required")
    if not conductor_class_id:
        raise Exception("conductor_class_id is required")
    if not conductor_data:
        raise Exception("conductor_data is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_class_id={conductor_class_id}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/class/maintenance/{conductor_class_id}/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/class/maintenance/{conductor_class_id}/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/class/maintenance/{}/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu, conductor_class_id
    )

    # 転送用ヘッダーを組み立てる(PATCHでボディを送るため"Content-Type"も付与する)
    # Build the headers to forward (also adds "Content-Type" since this is a PATCH with a body)
    headers = build_forward_headers(method="PATCH")

    # ITAのAPIへConductor更新のPATCHリクエストを送信する
    # Send a PATCH request to ITA's API to update the Conductor
    req = requests.patch(url, json=conductor_data, headers=headers, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to update conductor: {} - {}".format(req.status_code, req.text))
        raise HTTPException("update-conductor", req)

    return {
        "result": req.json(),
        "message": "Conductor updated successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "conductor_class_id": conductor_class_id
    }


@tool(
    name="execute-conductor",
    description=(
        "Execute an ITA Conductor operation. Provide the menu name (REST name), conductor_class_name, "
        "operation_name, and optionally schedule_date (format: YYYY/MM/DD hh:mm) and conductor_data. "
        "This will start a Conductor job execution. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'execution_list' or 'conductor_class_edit'."
            },
            "conductor_class_name": {
                "type": "string",
                "description": "Name of the Conductor class to execute"
            },
            "operation_name": {
                "type": "string",
                "description": "Name of the operation to execute"
            },
            "schedule_date": {
                "type": "string",
                "description": "Scheduled execution date and time (format: YYYY/MM/DD hh:mm). Optional."
            },
            "conductor_data": {
                "type": "object",
                "description": "Additional Conductor configuration data. Optional."
            }
        },
        "required": ["menu", "conductor_class_name", "operation_name"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EXECUTE,
    profile=["AgenticAI"]
)
def tool_execute_conductor(arguments: dict, payload: dict) -> dict:
    """
    Conductor作業を実行する

    Execute a Conductor operation.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_class_name (str): 実行するConductorクラス名
              / Conductor class name to execute
            - operation_name (str): 実行するオペレーション名
              / operation name to execute
            - schedule_date (str, optional): 予約実行日時 (YYYY/MM/DD hh:mm)
              / scheduled execution date and time
            - conductor_data (dict, optional): Conductor構成データ
              / Conductor configuration data
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor実行結果
            - result: APIレスポンスの実行結果 / the execution result returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name

    Raises:
        Exception: 必須パラメータが指定されていない場合
            / if required parameters are not specified
        HTTPException: Conductorの実行に失敗した場合 / if executing the Conductor fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_class_name = arguments.get("conductor_class_name", "")
    operation_name = arguments.get("operation_name", "")
    schedule_date = arguments.get("schedule_date")
    conductor_data = arguments.get("conductor_data", {})

    if not menu:
        raise Exception("menu is required")
    if not conductor_class_name:
        raise Exception("conductor_class_name is required")
    if not operation_name:
        raise Exception("operation_name is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_class_name={conductor_class_name}, operation_name={operation_name}")

    # リクエストボディの組み立て
    # Build the request body
    request_body = {
        "conductor_class_name": conductor_class_name,
        "operation_name": operation_name
    }
    if schedule_date:
        request_body["schedule_date"] = schedule_date
    if conductor_data:
        request_body["conductor_data"] = conductor_data

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/execute/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/execute/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/execute/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu
    )

    # 転送用ヘッダーを組み立てる(POSTでボディを送るため"Content-Type"も付与する)
    # Build the headers to forward (also adds "Content-Type" since this is a POST with a body)
    headers = build_forward_headers(method="POST")

    # ITAのAPIへConductor実行のPOSTリクエストを送信する
    # Send a POST request to ITA's API to execute the Conductor
    req = requests.post(url, json=request_body, headers=headers, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to execute conductor: {} - {}".format(req.status_code, req.text))
        raise HTTPException("execute-conductor", req)

    return {
        "result": req.json(),
        "message": "Conductor execution started successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu
    }


@tool(
    name="get-conductor-instance",
    description=(
        "Retrieve detailed information about a specific ITA Conductor execution instance. "
        "Provide the menu name (REST name) and conductor_instance_id to get the current status, "
        "execution details, and results of a Conductor operation. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'execution_list' or 'conductor_class_edit'."
            },
            "conductor_instance_id": {
                "type": "string",
                "description": "Conductor instance ID to retrieve information for"
            }
        },
        "required": ["menu", "conductor_instance_id"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EXECUTE,
    profile=["AgenticAI"]
)
def tool_get_conductor_instance(arguments: dict, payload: dict) -> dict:
    """
    Conductor作業の詳細情報を取得する

    Retrieve detailed information about a Conductor execution instance.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_instance_id (str): ConductorインスタンスID
              / Conductor instance ID
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor実行情報
            - result: APIレスポンスの実行情報 / the execution information returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - conductor_instance_id (str): ConductorインスタンスID / Conductor instance ID

    Raises:
        Exception: 必須パラメータが指定されていない場合
            / if required parameters are not specified
        HTTPException: Conductor情報の取得に失敗した場合
            / if retrieving Conductor information fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_instance_id = arguments.get("conductor_instance_id", "")

    if not menu:
        raise Exception("menu is required")
    if not conductor_instance_id:
        raise Exception("conductor_instance_id is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_instance_id={conductor_instance_id}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/{conductor_instance_id}/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/{conductor_instance_id}/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/{}/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu, conductor_instance_id
    )

    # 転送用ヘッダーを組み立てる(GETリクエストのため"Content-Type"は不要)
    # Build the headers to forward (no "Content-Type" needed for GET request)
    headers = build_forward_headers(method="GET")

    # ITAのAPIへConductor情報取得のGETリクエストを送信する
    # Send a GET request to ITA's API to retrieve Conductor information
    req = requests.get(url, headers=headers, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to get conductor instance: {} - {}".format(req.status_code, req.text))
        raise HTTPException("get-conductor-instance", req)

    return {
        "result": req.json(),
        "message": "Conductor instance information retrieved successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "conductor_instance_id": conductor_instance_id
    }


@tool(
    name="get-conductor-class",
    description=(
        "Retrieve information about a specific ITA Conductor class. "
        "Provide the menu name (REST name) and conductor_class_id to get the configuration "
        "and details of a Conductor class. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'conductor_class_edit'."
            },
            "conductor_class_id": {
                "type": "string",
                "description": "Conductor Class ID to retrieve information for"
            }
        },
        "required": ["menu", "conductor_class_id"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EDIT,
    profile=["AgenticAI"]
)
def tool_get_conductor_class(arguments: dict, payload: dict) -> dict:
    """
    Conductorクラスの情報を取得する

    Retrieve information about a Conductor class.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_class_id (str): Conductor Class ID
              / Conductor Class ID
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductorクラス情報
            - result: APIレスポンスのConductorクラス情報 / the Conductor class information returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - conductor_class_id (str): Conductor Class ID

    Raises:
        Exception: 必須パラメータが指定されていない場合
            / if required parameters are not specified
        HTTPException: Conductorクラス情報の取得に失敗した場合
            / if retrieving Conductor class information fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_class_id = arguments.get("conductor_class_id", "")

    if not menu:
        raise Exception("menu is required")
    if not conductor_class_id:
        raise Exception("conductor_class_id is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_class_id={conductor_class_id}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/class/{conductor_class_id}/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/class/{conductor_class_id}/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/class/{}/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu, conductor_class_id
    )

    # 転送用ヘッダーを組み立てる(GETリクエストのため"Content-Type"は不要)
    # Build the headers to forward (no "Content-Type" needed for GET request)
    headers = build_forward_headers(method="GET")

    # ITAのAPIへConductorクラス情報取得のGETリクエストを送信する
    # Send a GET request to ITA's API to retrieve Conductor class information
    req = requests.get(url, headers=headers, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to get conductor class: {} - {}".format(req.status_code, req.text))
        raise HTTPException("get-conductor-class", req)

    return {
        "result": req.json(),
        "message": "Conductor class information retrieved successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "conductor_class_id": conductor_class_id
    }


@tool(
    name="get-conductor-input-data",
    description=(
        "Retrieve the input data of a specific ITA Conductor execution instance. "
        "Provide the menu name (REST name) and conductor_instance_id to get the input data "
        "used for the Conductor operation. Optionally specify 'file' parameter as 'binary' "
        "to get binary format data. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'execution_list' or 'conductor_class_edit'."
            },
            "conductor_instance_id": {
                "type": "string",
                "description": "Conductor instance ID to retrieve input data for"
            },
            "file": {
                "type": "string",
                "description": "File data format specification. Set 'binary' for binary format. Optional."
            }
        },
        "required": ["menu", "conductor_instance_id"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EXECUTE,
    profile=["AgenticAI"]
)
def tool_get_conductor_input_data(arguments: dict, payload: dict) -> dict:
    """
    Conductor作業の投入データを取得する

    Retrieve the input data of a Conductor execution instance.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_instance_id (str): ConductorインスタンスID
              / Conductor instance ID
            - file (str, optional): ファイルデータの形式指定 ('binary' or None)
              / file data format specification
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor投入データ
            - result: APIレスポンスの投入データ / the input data returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - conductor_instance_id (str): ConductorインスタンスID / Conductor instance ID

    Raises:
        Exception: 必須パラメータが指定されていない場合
            / if required parameters are not specified
        HTTPException: Conductor投入データの取得に失敗した場合
            / if retrieving Conductor input data fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_instance_id = arguments.get("conductor_instance_id", "")
    file_format = arguments.get("file")

    if not menu:
        raise Exception("menu is required")
    if not conductor_instance_id:
        raise Exception("conductor_instance_id is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_instance_id={conductor_instance_id}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/{conductor_instance_id}/input_data/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/{conductor_instance_id}/input_data/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/{}/input_data/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu, conductor_instance_id
    )

    # クエリパラメータの追加（fileが指定されている場合）
    # Add query parameter if file format is specified
    params = {}
    if file_format:
        params["file"] = file_format

    # 転送用ヘッダーを組み立てる(GETリクエストのため"Content-Type"は不要)
    # Build the headers to forward (no "Content-Type" needed for GET request)
    headers = build_forward_headers(method="GET")

    # ITAのAPIへConductor投入データ取得のGETリクエストを送信する
    # Send a GET request to ITA's API to retrieve Conductor input data
    req = requests.get(url, headers=headers, params=params, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to get conductor input data: {} - {}".format(req.status_code, req.text))
        raise HTTPException("get-conductor-input-data", req)

    return {
        "result": req.json(),
        "message": "Conductor input data retrieved successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "conductor_instance_id": conductor_instance_id
    }


@tool(
    name="get-conductor-result-data",
    description=(
        "Retrieve the result data of a specific ITA Conductor execution instance. "
        "Provide the menu name (REST name) and conductor_instance_id to get the result data "
        "generated by the Conductor operation. Optionally specify 'file' parameter as 'binary' "
        "to get binary format data. "
        "Before use, refer to `tool-reference/ita_conductor.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (REST name). Normally 'execution_list' or 'conductor_class_edit'."
            },
            "conductor_instance_id": {
                "type": "string",
                "description": "Conductor instance ID to retrieve result data for"
            },
            "file": {
                "type": "string",
                "description": "File data format specification. Set 'binary' for binary format. Optional."
            }
        },
        "required": ["menu", "conductor_instance_id"]
    },
    required_menu=_REQUIRED_MENU_CONDUCTOR_EXECUTE,
    profile=["AgenticAI"]
)
def tool_get_conductor_result_data(arguments: dict, payload: dict) -> dict:
    """
    Conductor作業の結果データを取得する

    Retrieve the result data of a Conductor execution instance.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(REST名) / menu name (REST name)
            - conductor_instance_id (str): ConductorインスタンスID
              / Conductor instance ID
            - file (str, optional): ファイルデータの形式指定 ('binary' or None)
              / file data format specification
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id

    Returns:
        dict: Conductor結果データ
            - result: APIレスポンスの結果データ / the result data returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - conductor_instance_id (str): ConductorインスタンスID / Conductor instance ID

    Raises:
        Exception: 必須パラメータが指定されていない場合
            / if required parameters are not specified
        HTTPException: Conductor結果データの取得に失敗した場合
            / if retrieving Conductor result data fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    menu = arguments.get("menu", "")
    conductor_instance_id = arguments.get("conductor_instance_id", "")
    file_format = arguments.get("file")

    if not menu:
        raise Exception("menu is required")
    if not conductor_instance_id:
        raise Exception("conductor_instance_id is required")

    g.applogger.info(f"Parameter menu={menu}, conductor_instance_id={conductor_instance_id}")

    # このツールが呼び出すのは "/ita/menu/{menu}/conductor/{conductor_instance_id}/result_data/" という
    # ITA自身のAPI(ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/conductor/{conductor_instance_id}/result_data/"
    # endpoint of ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/conductor/{}/result_data/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu, conductor_instance_id
    )

    # クエリパラメータの追加（fileが指定されている場合）
    # Add query parameter if file format is specified
    params = {}
    if file_format:
        params["file"] = file_format

    # 転送用ヘッダーを組み立てる(GETリクエストのため"Content-Type"は不要)
    # Build the headers to forward (no "Content-Type" needed for GET request)
    headers = build_forward_headers(method="GET")

    # ITAのAPIへConductor結果データ取得のGETリクエストを送信する
    # Send a GET request to ITA's API to retrieve Conductor result data
    req = requests.get(url, headers=headers, params=params, timeout=get_downstream_timeout())

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to get conductor result data: {} - {}".format(req.status_code, req.text))
        raise HTTPException("get-conductor-result-data", req)

    return {
        "result": req.json(),
        "message": "Conductor result data retrieved successfully.",
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "conductor_instance_id": conductor_instance_id
    }
