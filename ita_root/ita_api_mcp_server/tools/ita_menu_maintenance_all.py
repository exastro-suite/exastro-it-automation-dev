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
ITAメニューメンテナンス一括操作ツール ("maintenance-all")

指定したメニューに対し、複数レコードの登録/更新/廃止/復活/物理削除を
一括で行う。ユーザー自身がアクセスできるメニューに対する操作であり、
実行に特別な権限は不要なため、@tool デコレーターの required_roles /
required_menu は指定していない(誰でも実行可能)。

各レコードで file 項目(FileUploadColumn)を指定する方法は2種類ある。
  - fileid : {column_name_rest: file_id} 形式。T_AI_ATTACHMENT_FILEに
    登録済みの添付ファイル(file_idはattachment_file.py・
    attachment_zip_file.pyなどのツールで発行したもの)を指定する。
    このツールが attachment_file.py の fetch_attachment_file() で
    ファイル本体を取得し、Base64エンコードした上で file 項目に
    変換してからダウンストリームAPIへ送信する。
  - file   : {column_name_rest: Base64文字列} 形式。呼び出し元が既に
    Base64エンコードした内容をそのまま指定する。

--------------------------------------------------------------------------
ITA menu bulk maintenance tool ("maintenance-all")

Bulk-registers/updates/discards/restores/physically-deletes multiple
records for a given menu. This operates on a menu the user can already
access, so no special permission is required to run it; the @tool
decorator's required_roles / required_menu are left unset (callable by
anyone).

Each record can specify a file item (FileUploadColumn) in one of two ways.
  - fileid : {column_name_rest: file_id} form. Refers to an attachment file
    already registered into T_AI_ATTACHMENT_FILE (a file_id issued by tools
    such as attachment_file.py / attachment_zip_file.py). This tool fetches
    the file content via attachment_file.py's fetch_attachment_file(),
    Base64-encodes it, converts it into a "file" entry, and sends that to
    the downstream API.
  - file   : {column_name_rest: Base64 string} form. The caller directly
    supplies content that has already been Base64-encoded.
"""
import base64
import os

import requests
from flask import g

from libs import tool, HTTPException, build_forward_headers
from .attachment_file import fetch_attachment_file

# recordのtypeに指定可能な操作タイプ
# Valid operation types for a record's "type" field
_VALID_RECORD_TYPES = ["Register", "Update", "Discard", "Restore", "Delete"]


@tool(
    name="maintenance-all",
    description=(
        "Bulk register/update/discard/restore/physically delete records in an ITA menu."
        "Before use, refer to `documents-tools/maintenance-all.md` using the `get-document` tool."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "menu": {
                "type": "string",
                "description": "Menu name (menu_name_rest) (e.g. 'operation_list')"
            },
            "records": {
                "type": "array",
                "description": "Array of records to register/update/discard/restore/delete",
                "items": {
                    "type": "object",
                    "properties": {
                        "fileid": {
                            "type": "object",
                            "description": (
                                "Specify the file (by file_id, issued by an attachment file tool such as "
                                "create-attachment-text-file) to register in the FileUploadColumn. Each property "
                                "name is column_name_rest."
                            )
                        },
                        "file": {
                            "type": "object",
                            "description": (
                                "Specify the file data to register in the FileUploadColumn in Base64 format. "
                                "Each property name is column_name_rest."
                            )
                        },
                        "parameter": {
                            "type": "object",
                            "description": (
                                "Record parameters. Each property name is column_name_rest, and the value is the "
                                "record value (file name for FileUploadColumn)."
                            )
                        },
                        "type": {
                            "type": "string",
                            "description": "Operation type",
                            "enum": _VALID_RECORD_TYPES
                        }
                    },
                    "required": ["parameter", "type"]
                }
            }
        },
        "required": ["menu", "records"]
    }
)
def tool_maintenance_all(arguments: dict, payload: dict) -> dict:
    """
    レコードを一括で登録/更新/廃止/復活/物理削除する

    Bulk-register/update/discard/restore/physically-delete records in an ITA menu.

    Parameters:
        arguments (dict): ツールの引数
            - menu (str): メニュー名(menu_name_rest) / menu name (menu_name_rest)
            - records (list[dict]): 登録/更新/廃止/復活/削除するレコードの配列
                / array of records to register/update/discard/restore/delete
                - fileid (dict, optional): ファイル項目のfile_id
                    (column_name_rest: file_id) / the file item's file_id
                    (column_name_rest: file_id)
                - file (dict, optional): ファイル項目のBase64データ
                    (column_name_rest: Base64文字列) / the file item's
                    Base64 data (column_name_rest: Base64 string)
                - parameter (dict): レコードのパラメータ
                    (column_name_rest: 値) / record parameters
                    (column_name_rest: value)
                - type (str): 操作タイプ('Register', 'Update', 'Discard',
                    'Restore', 'Delete') / operation type
        payload (dict): 呼び出しコンテキスト情報
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - user_id (str): 呼び出しユーザーのID / calling user's id

    Returns:
        dict: メンテナンス結果
            - result: APIレスポンスの結果 / the result returned by the API
            - message (str): 処理結果メッセージ / result message
            - organization_id (str): オーガナイゼーションID / organization id
            - workspace_id (str): ワークスペースID / workspace id
            - menu (str): メニュー名 / menu name
            - record_count (int): 処理したレコード数 / number of records processed

    Raises:
        Exception: menu・recordsが未指定、recordsの各要素が不正、または
            fileidで指定したファイルの取得に失敗した場合 / if menu/records
            is missing, a records entry is invalid, or fetching a file
            referenced by fileid fails
        HTTPException: メンテナンス操作に失敗した場合 / if the maintenance operation fails
    """
    organization_id = payload.get("organization_id")
    workspace_id = payload.get("workspace_id")
    user_id = payload.get("user_id")
    menu = arguments.get("menu", "")
    records = arguments.get("records")

    if not menu:
        raise Exception("menu is required")

    if not records or not isinstance(records, list):
        raise Exception("records is required and must be a non-empty array")

    # 各レコードの内容を検証し、fileid(file_id参照)が指定されている場合は
    # 実ファイルを取得してBase64化した上でfile項目に変換する
    # Validate each record, and for any "fileid" (file_id reference) entries,
    # fetch the actual file content and convert it into a Base64 "file" entry
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            raise Exception("Record at index {} must be an object".format(idx))

        if "fileid" in record:
            if not isinstance(record["fileid"], dict):
                raise Exception("Record at index {} has invalid 'fileid' field. Must be an object".format(idx))

            for col_name, file_id in record["fileid"].items():
                if not isinstance(file_id, str):
                    raise Exception(
                        "Record at index {} has invalid file ID for column '{}'. Must be a string".format(idx, col_name)
                    )

                file_data = fetch_attachment_file(organization_id, workspace_id, user_id, file_id)
                if file_data is None:
                    g.applogger.info(
                        "maintenance-all: file not found (record_index={}, column={}, file_id={})".format(
                            idx, col_name, file_id
                        )
                    )
                    raise Exception("File not found for column '{}': {}".format(col_name, file_id))

                if "file" not in record:
                    record["file"] = {}
                record["file"][col_name] = base64.b64encode(file_data["content"]).decode("utf-8")

            del record["fileid"]

        if "parameter" not in record:
            raise Exception("Record at index {} is missing 'parameter' field".format(idx))
        if "type" not in record:
            raise Exception("Record at index {} is missing 'type' field".format(idx))

        if record["type"] not in _VALID_RECORD_TYPES:
            raise Exception(
                "Record at index {} has invalid type '{}'. Must be one of: {}".format(
                    idx, record["type"], ", ".join(_VALID_RECORD_TYPES)
                )
            )

    # このツールが呼び出すのは "/ita/menu/{menu}/maintenance/all/" というITA自身のAPI
    # (ita_api_organization)側のエンドポイントであるため、環境変数
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT を使用する
    #
    # This tool calls the "/ita/menu/{menu}/maintenance/all/" endpoint of
    # ITA's own API (ita_api_organization), so it uses the
    # ITA_API_ORAGANIZATION_HOST / ITA_API_ORAGANIZATION_PORT environment
    # variables
    ita_api_host = os.getenv("ITA_API_ORAGANIZATION_HOST")
    ita_api_port = os.getenv("ITA_API_ORAGANIZATION_PORT")
    # プロトコルは常にhttp固定とする(ITAサービス間通信はhttpを使用する)
    # Protocol is always fixed to http (inter-service communication within ITA uses http)
    url = "http://{}:{}/api/{}/workspaces/{}/ita/menu/{}/maintenance/all/".format(
        ita_api_host, ita_api_port, organization_id, workspace_id, menu
    )

    # 転送用ヘッダーを組み立てる(POSTでボディを送るため"Content-Type"も付与する)
    # Build the headers to forward (also adds "Content-Type" since this is a POST with a body)
    headers = build_forward_headers(method="POST")

    g.applogger.info(
        "Maintenance all: menu={}, record_count={}".format(menu, len(records))
    )

    # ITAのAPIへ一括メンテナンスのPOSTリクエストを送信する
    # Send a POST request to ITA's API to perform the bulk maintenance operation
    req = requests.post(url, json=records, headers=headers)

    # ステータスコードが200以外の場合は異常終了として例外を発生させる
    # If the status code is not 200, treat it as a failure and raise an exception
    if req.status_code != 200:
        g.applogger.info("Failed to perform maintenance all: {} - {}".format(req.status_code, req.text))
        raise HTTPException("maintenance-all", req)

    # 正常時はAPIのレスポンスをそのまま結果として返す
    # On success, return the API response as the result
    return {
        "result": req.json(),
        "message": "Maintenance all completed successfully for {} record(s).".format(len(records)),
        "organization_id": organization_id,
        "workspace_id": workspace_id,
        "menu": menu,
        "record_count": len(records)
    }
