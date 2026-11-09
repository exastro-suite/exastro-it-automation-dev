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
tools/ita_conductor.py (create-conductor / update-conductor / execute-conductor /
get-conductor-class / get-conductor-instance / get-conductor-input-data /
get-conductor-result-data) のユニットテスト

異常系では、g.applogger.info の呼び出し回数はチェックしない
(ログ出力を増減しただけでテストが壊れるのは望ましくないため)。
代わりに、送出される例外のメッセージに元のエラー内容が含まれているかどうかで検証する。
ダウンストリームAPI呼び出しは requests_mock で全てモック化する。
"""

import pytest

from libs import HTTPException
from tools import ita_conductor

ORG_ID = "org1"
WS_ID = "ws1"
HOST = "ita-api-organization"
PORT = "8000"


@pytest.fixture(autouse=True)
def ita_env(monkeypatch):
    """ITA_API_ORAGANIZATION_HOST / PORT を固定値に設定する(呼び出しURLを決定的にするため)"""
    monkeypatch.setenv("ITA_API_ORAGANIZATION_HOST", HOST)
    monkeypatch.setenv("ITA_API_ORAGANIZATION_PORT", PORT)


class TestToolCreateConductor:
    """tool_create_conductor のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_create_conductor(
                {"conductor_data": {"conductor": {"conductor_name": "test"}}},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_data_raises(self, mock_flask_g):
        """異常系: conductor_dataが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_data is required"):
            ita_conductor.tool_create_conductor(
                {"menu": "conductor_class_edit"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_empty_conductor_data_raises(self, mock_flask_g):
        """異常系: conductor_dataが空の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_data is required"):
            ita_conductor.tool_create_conductor(
                {"menu": "conductor_class_edit", "conductor_data": {}},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_create_conductor(self, mock_flask_g, requests_mock):
        """正常系: Conductorクラスが正常に登録されること"""
        menu = "conductor_class_edit"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/maintenance/"
        conductor_data = {
            "conductor": {
                "conductor_name": "test_conductor",
                "note": "Test conductor"
            }
        }
        response_data = {
            "conductor_class_id": "1",
            "conductor_name": "test_conductor"
        }
        requests_mock.post(url, json=response_data, status_code=200)

        result = ita_conductor.tool_create_conductor(
            {"menu": menu, "conductor_data": conductor_data},
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor created successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert requests_mock.last_request.json() == conductor_data

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "conductor_class_edit"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/maintenance/"
        requests_mock.post(url, json={"message": "error", "result": "NG"}, status_code=500)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_create_conductor(
                {"menu": menu, "conductor_data": {"conductor": {"conductor_name": "test"}}},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "create-conductor"


class TestToolUpdateConductor:
    """tool_update_conductor のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_update_conductor(
                {
                    "conductor_class_id": "1",
                    "conductor_data": {"conductor": {"conductor_name": "test"}}
                },
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_class_id_raises(self, mock_flask_g):
        """異常系: conductor_class_idが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_class_id is required"):
            ita_conductor.tool_update_conductor(
                {
                    "menu": "conductor_class_edit",
                    "conductor_data": {"conductor": {"conductor_name": "test"}}
                },
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_data_raises(self, mock_flask_g):
        """異常系: conductor_dataが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_data is required"):
            ita_conductor.tool_update_conductor(
                {"menu": "conductor_class_edit", "conductor_class_id": "1"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_update_conductor(self, mock_flask_g, requests_mock):
        """正常系: Conductorクラスが正常に更新されること"""
        menu = "conductor_class_edit"
        conductor_class_id = "1"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/maintenance/{conductor_class_id}/"
        conductor_data = {
            "conductor": {
                "conductor_name": "updated_conductor",
                "note": "Updated conductor"
            }
        }
        response_data = {
            "conductor_class_id": conductor_class_id,
            "conductor_name": "updated_conductor"
        }
        requests_mock.patch(url, json=response_data, status_code=200)

        result = ita_conductor.tool_update_conductor(
            {
                "menu": menu,
                "conductor_class_id": conductor_class_id,
                "conductor_data": conductor_data
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor updated successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert result["conductor_class_id"] == conductor_class_id
        assert requests_mock.last_request.json() == conductor_data

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "conductor_class_edit"
        conductor_class_id = "1"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/maintenance/{conductor_class_id}/"
        requests_mock.patch(url, json={"message": "error", "result": "NG"}, status_code=404)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_update_conductor(
                {
                    "menu": menu,
                    "conductor_class_id": conductor_class_id,
                    "conductor_data": {"conductor": {"conductor_name": "test"}}
                },
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "update-conductor"


class TestToolExecuteConductor:
    """tool_execute_conductor のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_execute_conductor(
                {"conductor_class_name": "test_conductor", "operation_name": "test_operation"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_class_name_raises(self, mock_flask_g):
        """異常系: conductor_class_nameが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_class_name is required"):
            ita_conductor.tool_execute_conductor(
                {"menu": "execution_list", "operation_name": "test_operation"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_operation_name_raises(self, mock_flask_g):
        """異常系: operation_nameが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="operation_name is required"):
            ita_conductor.tool_execute_conductor(
                {"menu": "execution_list", "conductor_class_name": "test_conductor"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_without_optional_params(self, mock_flask_g, requests_mock):
        """正常系: オプションパラメータなしでConductorが正常に実行されること"""
        menu = "execution_list"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/execute/"
        response_data = {"conductor_instance_id": "100"}
        requests_mock.post(url, json=response_data, status_code=200)

        result = ita_conductor.tool_execute_conductor(
            {
                "menu": menu,
                "conductor_class_name": "test_conductor",
                "operation_name": "test_operation"
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor execution started successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu

        sent_body = requests_mock.last_request.json()
        assert sent_body["conductor_class_name"] == "test_conductor"
        assert sent_body["operation_name"] == "test_operation"
        assert "schedule_date" not in sent_body
        assert "conductor_data" not in sent_body

    def test_success_with_schedule_date(self, mock_flask_g, requests_mock):
        """正常系: schedule_dateを指定した場合、リクエストボディに含まれること"""
        menu = "execution_list"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/execute/"
        response_data = {"conductor_instance_id": "101"}
        requests_mock.post(url, json=response_data, status_code=200)

        result = ita_conductor.tool_execute_conductor(
            {
                "menu": menu,
                "conductor_class_name": "test_conductor",
                "operation_name": "test_operation",
                "schedule_date": "2026/12/31 23:59"
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        sent_body = requests_mock.last_request.json()
        assert sent_body["schedule_date"] == "2026/12/31 23:59"

    def test_success_with_conductor_data(self, mock_flask_g, requests_mock):
        """正常系: conductor_dataを指定した場合、リクエストボディに含まれること"""
        menu = "execution_list"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/execute/"
        response_data = {"conductor_instance_id": "102"}
        conductor_data = {"parameter1": "value1", "parameter2": "value2"}
        requests_mock.post(url, json=response_data, status_code=200)

        result = ita_conductor.tool_execute_conductor(
            {
                "menu": menu,
                "conductor_class_name": "test_conductor",
                "operation_name": "test_operation",
                "conductor_data": conductor_data
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        sent_body = requests_mock.last_request.json()
        assert sent_body["conductor_data"] == conductor_data

    def test_success_with_all_params(self, mock_flask_g, requests_mock):
        """正常系: 全てのパラメータを指定した場合、正常に実行されること"""
        menu = "execution_list"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/execute/"
        response_data = {"conductor_instance_id": "103"}
        conductor_data = {"parameter1": "value1"}
        requests_mock.post(url, json=response_data, status_code=200)

        result = ita_conductor.tool_execute_conductor(
            {
                "menu": menu,
                "conductor_class_name": "test_conductor",
                "operation_name": "test_operation",
                "schedule_date": "2026/12/31 23:59",
                "conductor_data": conductor_data
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        sent_body = requests_mock.last_request.json()
        assert sent_body["conductor_class_name"] == "test_conductor"
        assert sent_body["operation_name"] == "test_operation"
        assert sent_body["schedule_date"] == "2026/12/31 23:59"
        assert sent_body["conductor_data"] == conductor_data

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "execution_list"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/execute/"
        requests_mock.post(url, json={"message": "error", "result": "NG"}, status_code=400)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_execute_conductor(
                {
                    "menu": menu,
                    "conductor_class_name": "test_conductor",
                    "operation_name": "test_operation"
                },
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "execute-conductor"


class TestToolGetConductorInstance:
    """tool_get_conductor_instance のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_get_conductor_instance(
                {"conductor_instance_id": "100"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_instance_id_raises(self, mock_flask_g):
        """異常系: conductor_instance_idが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_instance_id is required"):
            ita_conductor.tool_get_conductor_instance(
                {"menu": "execution_list"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_get_conductor_instance(self, mock_flask_g, requests_mock):
        """正常系: Conductor実行情報が正常に取得されること"""
        menu = "execution_list"
        conductor_instance_id = "100"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/"
        response_data = {
            "conductor_instance_id": conductor_instance_id,
            "conductor_name": "test_conductor",
            "status": "completed"
        }
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_instance(
            {"menu": menu, "conductor_instance_id": conductor_instance_id},
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor instance information retrieved successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert result["conductor_instance_id"] == conductor_instance_id

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "execution_list"
        conductor_instance_id = "999"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/"
        requests_mock.get(url, json={"message": "not found", "result": "NG"}, status_code=404)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_get_conductor_instance(
                {"menu": menu, "conductor_instance_id": conductor_instance_id},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "get-conductor-instance"


class TestToolGetConductorClass:
    """tool_get_conductor_class のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_get_conductor_class(
                {"conductor_class_id": "1"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_class_id_raises(self, mock_flask_g):
        """異常系: conductor_class_idが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_class_id is required"):
            ita_conductor.tool_get_conductor_class(
                {"menu": "conductor_class_edit"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_get_conductor_class(self, mock_flask_g, requests_mock):
        """正常系: Conductorクラス情報が正常に取得されること"""
        menu = "conductor_class_edit"
        conductor_class_id = "1"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/{conductor_class_id}/"
        response_data = {
            "conductor_class_id": conductor_class_id,
            "conductor_name": "test_conductor",
            "note": "Test conductor class"
        }
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_class(
            {"menu": menu, "conductor_class_id": conductor_class_id},
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor class information retrieved successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert result["conductor_class_id"] == conductor_class_id

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "conductor_class_edit"
        conductor_class_id = "999"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/class/{conductor_class_id}/"
        requests_mock.get(url, json={"message": "not found", "result": "NG"}, status_code=404)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_get_conductor_class(
                {"menu": menu, "conductor_class_id": conductor_class_id},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "get-conductor-class"


class TestToolGetConductorInputData:
    """tool_get_conductor_input_data のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_get_conductor_input_data(
                {"conductor_instance_id": "100"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_instance_id_raises(self, mock_flask_g):
        """異常系: conductor_instance_idが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_instance_id is required"):
            ita_conductor.tool_get_conductor_input_data(
                {"menu": "execution_list"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_without_file_param(self, mock_flask_g, requests_mock):
        """正常系: fileパラメータなしでConductor投入データが正常に取得されること"""
        menu = "execution_list"
        conductor_instance_id = "100"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/input_data/"
        response_data = {
            "conductor_instance_id": conductor_instance_id,
            "input_data": {"param1": "value1"}
        }
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_input_data(
            {"menu": menu, "conductor_instance_id": conductor_instance_id},
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor input data retrieved successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert result["conductor_instance_id"] == conductor_instance_id
        # クエリパラメータがないことを確認
        assert requests_mock.last_request.query == ""

    def test_success_with_file_param(self, mock_flask_g, requests_mock):
        """正常系: fileパラメータを指定した場合、クエリパラメータに含まれること"""
        menu = "execution_list"
        conductor_instance_id = "100"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/input_data/"
        response_data = {"binary_data": "base64encodeddata"}
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_input_data(
            {
                "menu": menu,
                "conductor_instance_id": conductor_instance_id,
                "file": "binary"
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        # クエリパラメータが含まれることを確認
        assert requests_mock.last_request.query == "file=binary"

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "execution_list"
        conductor_instance_id = "999"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/input_data/"
        requests_mock.get(url, json={"message": "not found", "result": "NG"}, status_code=404)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_get_conductor_input_data(
                {"menu": menu, "conductor_instance_id": conductor_instance_id},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "get-conductor-input-data"


class TestToolGetConductorResultData:
    """tool_get_conductor_result_data のテストクラス"""

    def test_missing_menu_raises(self, mock_flask_g):
        """異常系: menuが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="menu is required"):
            ita_conductor.tool_get_conductor_result_data(
                {"conductor_instance_id": "100"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_missing_conductor_instance_id_raises(self, mock_flask_g):
        """異常系: conductor_instance_idが未指定の場合は例外が発生すること"""
        with pytest.raises(Exception, match="conductor_instance_id is required"):
            ita_conductor.tool_get_conductor_result_data(
                {"menu": "execution_list"},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )

    def test_success_without_file_param(self, mock_flask_g, requests_mock):
        """正常系: fileパラメータなしでConductor結果データが正常に取得されること"""
        menu = "execution_list"
        conductor_instance_id = "100"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/result_data/"
        response_data = {
            "conductor_instance_id": conductor_instance_id,
            "result_data": {"status": "success", "output": "result"}
        }
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_result_data(
            {"menu": menu, "conductor_instance_id": conductor_instance_id},
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        assert result["message"] == "Conductor result data retrieved successfully."
        assert result["organization_id"] == ORG_ID
        assert result["workspace_id"] == WS_ID
        assert result["menu"] == menu
        assert result["conductor_instance_id"] == conductor_instance_id
        # クエリパラメータがないことを確認
        assert requests_mock.last_request.query == ""

    def test_success_with_file_param(self, mock_flask_g, requests_mock):
        """正常系: fileパラメータを指定した場合、クエリパラメータに含まれること"""
        menu = "execution_list"
        conductor_instance_id = "100"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/result_data/"
        response_data = {"binary_data": "base64encodeddata"}
        requests_mock.get(url, json=response_data, status_code=200)

        result = ita_conductor.tool_get_conductor_result_data(
            {
                "menu": menu,
                "conductor_instance_id": conductor_instance_id,
                "file": "binary"
            },
            {"organization_id": ORG_ID, "workspace_id": WS_ID}
        )

        assert result["result"] == response_data
        # クエリパラメータが含まれることを確認
        assert requests_mock.last_request.query == "file=binary"

    def test_http_failure_raises_httpexception(self, mock_flask_g, requests_mock):
        """異常系: ダウンストリームAPIが200以外を返した場合、HTTPExceptionが発生すること"""
        menu = "execution_list"
        conductor_instance_id = "999"
        url = f"http://{HOST}:{PORT}/api/{ORG_ID}/workspaces/{WS_ID}/ita/menu/{menu}/conductor/{conductor_instance_id}/result_data/"
        requests_mock.get(url, json={"message": "not found", "result": "NG"}, status_code=404)

        with pytest.raises(HTTPException) as exc_info:
            ita_conductor.tool_get_conductor_result_data(
                {"menu": menu, "conductor_instance_id": conductor_instance_id},
                {"organization_id": ORG_ID, "workspace_id": WS_ID}
            )
        assert exc_info.value.tool_name == "get-conductor-result-data"
