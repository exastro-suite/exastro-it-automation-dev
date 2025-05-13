#   Copyright 2025 NEC Corporation
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

import pytest
import os
import json
import shutil
import requests
import inspect

from importlib import import_module

from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv

from unittest.mock import patch
from tests.common import request_parameters

import pytest
from backyard_main import backyard_main
from common_libs.common.dbconnect import DBConnectWs


@pytest.fixture
def mock_environment_variables(monkeypatch):
    # monkeypatch.setenv("STORAGEPATH", "/mock/storage/path")
    return


@pytest.fixture
def mock_db_connection():
    mock_db = MagicMock()
    mock_db.table_select.return_value = []
    return mock_db


@patch("backyard_main.get_maintenance_mode_setting")
def test_backyard_main_menu_export_case(mock_get_maintenance_mode, app, set_g_variable, mocker, mock_environment_variables):
    """Pytest: メニューエクスポート 一括登録呼び出し / Pytest: Call menu export bulk registration
    """

    print(f'test_backyard_main_menu_export_case {inspect.currentframe().f_code.co_name=}')

    # Mock maintenance mode
    mock_get_maintenance_mode.return_value = {"data_update_stop": "0", "backyard_execute_stop": "0"}

    mock_get_log_message = mocker.patch("backyard_main.g.appmsg.get_log_message", return_value="Mocked log message")

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]
    print (f'test data {organization_id=} {workspace_id=}')

    g.ORGANIZATION_ID = organization_id
    g.WORKSPACE_ID = workspace_id

    print (f'{g.ORGANIZATION_ID=} {g.WORKSPACE_ID=}')

    # メニューエクスポート 一括登録呼び出しのデータ登録 / Menu Export Bulk Registration Call Data Registration
    body = sample_data_menu_bulk_export_execute()
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/menu/bulk/export/execute/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=body)

    print(f'{result.status_code=} {result.text=}')

    assert result.status_code == 200, "menu bulk export register success"

    execution_no = json.loads(result.text).get("data").get("execution_no")

    # Call the function
    backyard_main(organization_id, workspace_id)

    # Assertions

    # １度だけ呼ばれたかの確認
    # Check that it was called only once
    mock_get_maintenance_mode.assert_called_once()

    # １度でも呼ばれたかの確認
    # Verification of whether it was called at least once
    mock_get_log_message.assert_called()

    # 指定した引数で一度でも呼ばれたか確認
    # Verify that the function has been called at least once with the specified arguments
    mock_get_log_message.assert_any_call("BKY-20001", [])

    # 戻り値が正しいかを確認
    # Check if the return value is correct
    assert mock_get_log_message.return_value == "Mocked log message"

    # 最後に呼び出された引数が正しいかを確認
    # Check if the arguments of the last call are correct
    mock_get_log_message.assert_called_with("BKY-20002", [])

    # 正常終了までいったのであれば、出力された内容とステータスの更新が正常に終っているかの確認

    objdbca = DBConnectWs(workspace_id)
    ret = objdbca.table_select('T_MENU_EXPORT_IMPORT', 'WHERE STATUS = %s AND EXECUTION_NO = %s', [3, execution_no])
    # ステータスが正常終了になっているかの確認
    # Check if the status is normal completion
    assert len(ret) == 1, "menu export import status check"

    # 出力されたファイルの確認のため、該当のファイルパスを取得
    # Get the file path for the output file
    ret = objdbca.table_select("T_MENU_EXPORT_IMPORT", 'WHERE EXECUTION_NO = %s', [execution_no])
    print(f'{ret=}')

    strage_path = os.environ.get('STORAGEPATH')
    workspace_path = strage_path + "/".join([organization_id, workspace_id])
    export_menu_dir = workspace_path + "/tmp/driver/export_menu"

    # kymファイル名を取得
    # Get the kym file name
    str_path = os.path.join(export_menu_dir, ret[0]["FILE_NAME"])

    assert os.path.exists(str_path), "menu export import file check"


    # ret = objdbca.table_select("T_COMN_MENU", 'WHERE MENU_NAME_REST = %s', ['menu_export_import_list'])

    # print(f'{ret=}')


    # exec_result = objmenu.exec_maintenance(parameters, execution_no, "", False, False, True, False, True, record_file_paths=record_file_paths)  # noqa: E999

    objdbca.db_disconnect()


@patch("backyard_main.get_maintenance_mode_setting")
def test_backyard_main_maintenance_mode(mock_get_maintenance_mode, mock_environment_variables):

    print(f'test_backyard_main_maintenance_mode {inspect.currentframe().f_code.co_name=}')

    # Mock maintenance mode
    mock_get_maintenance_mode.return_value = {"data_update_stop": "1"}

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]
    print (f'test data {organization_id=} {workspace_id=}')

    g.ORGANIZATION_ID = organization_id
    g.WORKSPACE_ID = workspace_id

    # Call the function
    backyard_main(organization_id, workspace_id)

    # Assertions
    mock_get_maintenance_mode.assert_called_once()

@patch("backyard_main.get_maintenance_mode_setting")
@patch("backyard_main.DBConnectWs")
def test_backyard_main_exception_handling(mock_db_connect, mock_get_maintenance_mode, mocker, mock_environment_variables):

    print(f'test_backyard_main_exception_handling {inspect.currentframe().f_code.co_name=}')

    # Mock maintenance mode で 例外を発生させる
    # Mock maintenance mode to raise an exception
    mock_get_maintenance_mode.side_effect = Exception("Mocked exception")

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]
    print (f'test data {organization_id=} {workspace_id=}')

    g.ORGANIZATION_ID = organization_id
    g.WORKSPACE_ID = workspace_id

    # Call the function
    backyard_main(organization_id, workspace_id)

    # Assertions
    # 例外が発生したかどうかの確認
    # Check if an exception occurred
    mock_get_maintenance_mode.assert_called_once()

    # 次に処置中の例外が発生したかどうかの確認
    # Check if the next exception occurred
    mock_db_connect.side_effect = Exception("Mocked exception")

    # Mock maintenance mode
    mock_get_maintenance_mode.return_value = {"data_update_stop": "0"}

    mock_format_exc = mocker.patch("backyard_main.traceback.format_exc", return_value="Mocked traceback")

    # Call the function
    backyard_main(organization_id, workspace_id)

    # 戻り値が正しいかを確認
    # Check if the return value is correct
    assert mock_format_exc.return_value == "Mocked traceback"


def sample_data_menu_bulk_export_execute():
    """ menu_bulk_export_execute sample data

    Returns:
        list: sample data body
    """

    body = {
        "menu": [
            "system_settings",
            "menu_group_list",
            "menu_list",
            "role_menu_link_list",
            "operation_delete_list",
            "file_delete_list",
            "operation_list",
            "movement_list",
            "menu_table_link_list",
            "menu_column_link_list",
            "column_group_list",
            "menu_definition_list",
            "column_group_creation_info",
            "menu_item_creation_info",
            "unique_constraint_creation_info",
            "menu_role_creation_info",
            "menu_difinition_table_link",
            "other_menu_link",
            "reference_item_info",
            "execution_environment_parameter_definition_sheet",
            "hostgroup_management",
            "hostgroup_parent_child_link_list",
            "host_link_list",
            "hostgroup_split_target",
            "compare_list",
            "compare_detail",
            "device_list",
            "interface_info_ansible",
            "ansible_automation_controller_host_list",
            "global_variable_list",
            "global_variable_list_for_sensitiv",
            "file_list",
            "template_list",
            "common_variable_use_list",
            "not_managed_variable_list",
            "collected_item_value_list",
            "execution_environment_definition_template_list",
            "execution_environment_list",
            "agent list",
            "movement_list_ansible_legacy",
            "playbook_files",
            "movement_playbook_link",
            "movement_variable_assoc_list_ansible_legacy",
            "subst_value_auto_reg_setting_ansible_legacy",
            "movement_list_ansible_pioneer",
            "dialog_type_list",
            "os_type_master",
            "dialog_files",
            "movement_dialogue_type_link",
            "movement_variable_assoc_list_ansible_pioneer",
            "subst_value_auto_reg_setting_ansible_pioneer",
            "role_name_list",
            "movement_list_ansible_role",
            "role_package_list",
            "movement_role_link",
            "movement_variable_assoc_list_ansible_role",
            "nested_variable_list",
            "subst_value_auto_reg_setting_ansible_role",
            "nested_variable_member_list",
            "nested_variable_array_combination_list",
            "conductor_interface_information",
            "conductor_notice_definition",
            "conductor_class_list",
            "conductor_regularly_execution"
        ],
        "mode": "1",
        "abolished_type": "1",
        "journal_type": "1"
    }

    return body