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

from importlib import import_module

from flask import Flask, g
from dotenv import load_dotenv  # python-dotenv

from unittest.mock import MagicMock, patch
from backyard_main import menu_export_exec, AppException
from tests.common import request_parameters, test_common
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs

import pytest
from unittest.mock import patch, MagicMock
from backyard_main import backyard_main
from common_libs.common.logger import AppLog
from common_libs.common.message_class import MessageTemplate


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
@patch("backyard_main.DBConnectWs")
def test_backyard_main_normal_case(mock_db_connect, mock_get_maintenance_mode, mock_environment_variables, mock_db_connection):
    # Mock maintenance mode
    mock_get_maintenance_mode.return_value = {"data_update_stop": "0", "backyard_execute_stop": "0"}
    mock_db_connect.return_value = mock_db_connection

    flask_app = Flask(__name__)

    # 初期化 / Initialize
    # g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # メニューエクスポート 一括登録呼び出し / Call menu export bulk registration
    body = sample_data_menu_bulk_export_execute()
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/menu/bulk/export/execute/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=body)

    assert result.status_code == 200, "menu bulk export register success"

    with flask_app.app_context():
        g.LANGUAGE = os.environ.get("LANGUAGE")
        g.appmsg = MessageTemplate(g.LANGUAGE)
        # create app log instance and message class instance
        g.applogger = AppLog()

        g.USER_ID = os.environ.get("USER_ID")
        g.SERVICE_NAME = os.environ.get("SERVICE_NAME")

        # Call the function
        backyard_main(organization_id, workspace_id)

    # Assertions
    mock_get_maintenance_mode.assert_called_once()
    mock_db_connect.assert_called_once_with("ws_id")
    mock_db_connection.table_select.assert_called()

@patch("backyard_main.get_maintenance_mode_setting")
def test_backyard_main_maintenance_mode(mock_get_maintenance_mode, mock_environment_variables):
    # Mock maintenance mode
    mock_get_maintenance_mode.return_value = {"data_update_stop": "1"}


    # Call the function
    backyard_main("org_id", "ws_id")

    # Assertions
    mock_get_maintenance_mode.assert_called_once()

@patch("backyard_main.get_maintenance_mode_setting")
@patch("backyard_main.DBConnectWs")
def test_backyard_main_exception_handling(mock_db_connect, mock_get_maintenance_mode, mock_environment_variables):
    # Mock maintenance mode
    mock_get_maintenance_mode.side_effect = Exception("Mocked exception")

    # Call the function
    backyard_main("org_id", "ws_id")

    # Assertions
    mock_get_maintenance_mode.assert_called_once()


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