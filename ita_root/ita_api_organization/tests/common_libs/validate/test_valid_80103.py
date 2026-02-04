# Copyright 2025 NEC Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import random
import string
from typing import NotRequired, TypedDict
from urllib.parse import parse_qs, urlparse
import pytest

from common_libs.validate.valid_80103 import external_valid_menu_before

ExpectedType = TypedDict("ExpectedType", {"ret": bool, "msg_code": str})
OptionType = TypedDict(
    "OptionType",
    {
        "cmd_type": str,
        "tf_organization_name": NotRequired[str],
        "tf_project_name": NotRequired[str],
        "no_interface_info": NotRequired[bool],
    },
)


class TestConstants:
    NOT_EXISTS_ORG_ON_DB_UUID = "41842c9c-a3e0-4c8c-a7a2-4502a66437c3"
    VALID_ORG_UUID = "e6a2a790-a852-4e09-b33a-0c407605af25"
    NOT_EXISTS_ORG_ON_HCP_UUID = "3bb26fdb-22ab-4a3d-9329-e8a977231ced"
    INVALID_TOKEN_ORG_UUID = "3963f306-9405-427d-94a5-2385d37f78d1"
    RATE_LIMIT_ORG_UUID = "5a25ec7c-2b99-4f85-867d-76a8603c9cdf"

    VALID_ORG_NAME = "valid-organization"
    NOT_EXISTS_ORG_ON_HCP_NAME = "invalid-organization"
    INVALID_TOKEN_ORG_NAME = "invalid-token"
    RATE_LIMIT_ORG_NAME = "rate-limit"

    DEFAULT_PROJECT_NAME = "Default Project"
    DEFAULT_PROJECT_ID = "prj-W6k9K23oSXRHGpj3"

    PROJECT_NAME = "Some Project"
    NOT_EXISTS_PROJECT_NAME = "Nonexistent Project"

    mapping_org_uuid_to_name = {
        VALID_ORG_UUID: VALID_ORG_NAME,
        NOT_EXISTS_ORG_ON_HCP_UUID: NOT_EXISTS_ORG_ON_HCP_NAME,
        INVALID_TOKEN_ORG_UUID: INVALID_TOKEN_ORG_NAME,
        RATE_LIMIT_ORG_UUID: RATE_LIMIT_ORG_NAME,
    }

    upsert_commands = ("Register", "Update", "Restore")


@pytest.fixture
def mock_objdbca(mocker):
    """Fixture to mock objdbca."""
    return mocker.MagicMock()


@pytest.fixture
def mock_g(mocker):
    """Fixture to mock Flask's global object g."""
    mock_g_object = mocker.MagicMock()
    mock_g_object.appmsg = mocker.MagicMock()
    mock_g_object.appmsg.get_api_message.return_value = ""
    mock_g_object.applogger = mocker.MagicMock()

    # gオブジェクトを直接モックする
    mocker.patch("common_libs.validate.valid_80103.g", new=mock_g_object)
    # mocker.patch("common_libs.terraform_driver.cloud_ep.RestApiCaller.g", new=mock_g_object)

    return mock_g_object


def call_rest_mock(
    method: str,
    api_uri: str,
    content=None,
    header=None,
    module_upload_flag=False,
    direct_url="",
    get_log=False,
):
    """Mock function for RestApiCaller.call_rest method."""
    parsed_url = urlparse(api_uri)
    parsed_query = parse_qs(parsed_url.query)
    path_segments = parsed_url.path.split("/")
    match method, path_segments[1:], parsed_query, content:
        # List projects /organizations/:organization_name/projects
        case "GET", ["organizations", TestConstants.NOT_EXISTS_ORG_ON_HCP_NAME, "projects"], _, _:
            # Organizationが存在しない場合のレスポンスモック
            # https://developer.hashicorp.com/terraform/enterprise/api-docs#authentication
            # > forbidden requests with a valid token result in a 404.
            return {
                "statusCode": 404,
                "responseContents": json.dumps(
                    {
                        "errors": [
                            {
                                "detail": "Organization not found",
                                "status": 404,
                                "title": "Not Found",
                            }
                        ]
                    }
                ),
            }
        case (
            "GET",
            ["organizations", TestConstants.INVALID_TOKEN_ORG_NAME, "projects"],
            _,
            _,
        ):
            # Tokenが無効な場合のレスポンスモック
            # https://developer.hashicorp.com/terraform/enterprise/api-docs#authentication
            # > The 401 status code is reserved for problems with the authentication token;
            return {
                "statusCode": 401,
                "responseContents": json.dumps(
                    {
                        "errors": [
                            {
                                "detail": "Invalid authentication token",
                                "status": 401,
                                "title": "Unauthorized",
                            }
                        ]
                    }
                ),
            }
        case (
            "GET",
            ["organizations", TestConstants.RATE_LIMIT_ORG_NAME, "projects"],
            _,
            _,
        ):
            # Rate Limit超過の場合のレスポンスモック
            # https://developer.hashicorp.com/terraform/enterprise/api-docs#rate-limits
            return {
                "statusCode": 404,
                "responseContents": json.dumps(
                    {
                        "errors": [
                            {
                                "detail": "You have exceeded the API's rate limit.",
                                "status": 429,
                                "title": "Too many requests",
                            }
                        ]
                    }
                ),
            }
        case "GET", ["organizations", org_name, "projects"], {"page[number]": ["1"]}, _:
            # 正常系のレスポンスモック: 1ページ目
            return {
                "statusCode": 200,
                "responseContents": json.dumps(
                    get_project_list_response_mock(
                        total_pages=2, total_count=25, organization_name=org_name
                    )
                ),
            }
        case "GET", ["organizations", org_name, "projects"], {"page[number]": ["2"]}, _:
            # 正常系のレスポンスモック: 2ページ目
            return {
                "statusCode": 200,
                "responseContents": json.dumps(
                    get_project_list_response_mock(
                        page_number=2,
                        total_pages=2,
                        total_count=25,
                        organization_name=org_name,
                    )
                ),
            }
        case _:
            return {"statusCode": 404, "responseContents": {}}


def get_project_list_response_mock(
    page_number: int = 1,
    page_size: int = 20,
    total_pages: int = 1,
    total_count: int = 2,
    organization_name: str = TestConstants.VALID_ORG_NAME,
):
    return {
        "data": [
            get_project_data_mock(
                organization_name,
                (
                    "Default Project"
                    if i == 0
                    else (
                        f"Project {i+1}"
                        if i < total_count - 1
                        else TestConstants.PROJECT_NAME
                    )
                ),
            )
            for i in range(
                (page_number - 1) * page_size, min(page_number * page_size, total_count)
            )
        ],
        "links": {
            "self": create_list_project_url(page_number, page_size, organization_name),
            "first": create_list_project_url(1, page_size, organization_name),
            "prev": (
                None
                if page_number == 1
                else create_list_project_url(
                    page_number - 1, page_size, organization_name
                )
            ),
            "next": (
                None
                if page_number >= total_pages
                else create_list_project_url(
                    page_number + 1, page_size, organization_name
                )
            ),
            "last": create_list_project_url(total_pages, page_size, organization_name),
        },
        "meta": {
            "status-counts": {"total": total_count, "matching": total_count},
            "pagination": {
                "current-page": page_number,
                "page-size": page_size,
                "prev-page": None if page_number == 1 else page_number - 1,
                "next-page": None if page_number >= total_pages else page_number + 1,
                "total-pages": total_pages,
                "total-count": total_count,
            },
        },
    }


def create_list_project_url(page_number, page_size, organization_name):
    return f"https://app.terraform.io/api/v2/organizations/{organization_name}/projects?page%5Bnumber%5D={page_number}&page%5Bsize%5D={page_size}"


# Base62 character set: 0-9, A-Z, a-z
BASE62_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE = 62


def base62_encode(num: int) -> str:
    """
    Encode a non-negative integer into a Base62 string.
    """
    if not isinstance(num, int) or num < 0:
        raise ValueError("Input must be a non-negative integer.")
    if num == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while num > 0:
        num, rem = divmod(num, BASE)
        encoded.append(BASE62_ALPHABET[rem])
    return "".join(reversed(encoded))


def get_project_data_mock(
    organization_name: str = TestConstants.VALID_ORG_NAME,
    project_name: str = TestConstants.DEFAULT_PROJECT_NAME,
):
    """Mock function to get project data by project name."""
    if project_name == TestConstants.DEFAULT_PROJECT_NAME:
        project_id = TestConstants.DEFAULT_PROJECT_ID
    else:
        # Generate a random 96bits Base62 encoded project ID
        project_id = f"prj-{base62_encode(random.randint(1 << 95, (1 << 96) - 1))}"
    return {
        "id": project_id,
        "type": "projects",
        "attributes": {
            "name": project_name,
            "description": None,
            "workspace-count": 2,
            "team-count": 1,
            "default-execution-mode": "remote",
            "setting-overwrites": {"execution-mode": False},
            "permissions": {
                "can-update": True,
                "can-destroy": True,
                "can-create-workspace": True,
            },
        },
        "relationships": {
            "organization": {
                "data": {
                    "id": organization_name,
                    "type": "organizations",
                },
                "links": {"related": f"/api/v2/organizations/{organization_name}"},
            },
            "default-agent-pool": {"data": None},
            "tag-bindings": {
                "links": {"related": f"/api/v2/projects/{project_id}/tag-bindings"}
            },
            "effective-tag-bindings": {
                "links": {
                    "related": f"/api/v2/projects/{project_id}/effective-tag-bindings"
                }
            },
        },
        "links": {"self": f"/api/v2/projects/{project_id}"},
    }


def get_table_select_mock(no_interface_info: bool):
    """Return a mock function for objdbca.table_select method."""
    def table_select_mock(table_name: str, where_str: str, bind_values: list):
        match table_name, bind_values:
            case "T_TERE_ORGANIZATION", [TestConstants.NOT_EXISTS_ORG_ON_DB_UUID, 0]:
                return []
            case "T_TERE_ORGANIZATION", [org_uuid, 0]:
                org_name = TestConstants.mapping_org_uuid_to_name.get(org_uuid)
                return [{"ORGANIZATION_NAME": org_name}] if org_name else []
            case "T_TERE_IF_INFO", _ if no_interface_info:
                return []
            case "T_TERE_IF_INFO", _:
                return [{}]
            case _:
                return []
    return table_select_mock


@pytest.fixture
def patch_call_restapi_class(mocker):
    """Fixture to patch call_restapi_class function."""
    mock_rest_api_caller_obejct = mocker.MagicMock()
    mock_rest_api_caller_obejct.rest_call = call_rest_mock
    mock_call_restapi_class = mocker.patch(
        "common_libs.terraform_driver.cloud_ep.terraform_restapi.RestApiCaller",
        return_value=mock_rest_api_caller_obejct,
    )
    return mock_call_restapi_class


@pytest.mark.parametrize(
    "test_parameter,expected",
    [
        pytest.param(
            {"cmd_type": "Delete"}, {"ret": True, "msg_code": ""}, id="Delete command"
        ),
        pytest.param(
            {
                "cmd_type": "Discard",
                "tf_organization_name": TestConstants.VALID_ORG_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
            },
            {"ret": True, "msg_code": ""},
            id="Discard command",
        ),
        *(
            pytest.param(
                {
                    "cmd_type": cmd,
                    "tf_organization_name": TestConstants.VALID_ORG_UUID,
                    "tf_project_name": TestConstants.PROJECT_NAME,
                },
                {"ret": True, "msg_code": ""},
                id=f"{cmd} command: Project exists",
            )
            for cmd in TestConstants.upsert_commands
        ),
        *(
            pytest.param(
                {
                    "cmd_type": cmd,
                    "tf_organization_name": TestConstants.VALID_ORG_UUID,
                    "tf_project_name": TestConstants.NOT_EXISTS_PROJECT_NAME,
                },
                {"ret": False, "msg_code": "MSG-82043"},
                id=f"{cmd} command: Project not exists",
            )
            for cmd in TestConstants.upsert_commands
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.VALID_ORG_UUID,
            },
            {"ret": True, "msg_code": ""},
            id="Use default project, skip existence check",
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.NOT_EXISTS_ORG_ON_DB_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
            },
            {"ret": False, "msg_code": "MSG-82041"},
            id="Organization does not exist on DB",
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.NOT_EXISTS_ORG_ON_HCP_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
            },
            {"ret": False, "msg_code": "MSG-82042"},
            id="Organization does not exist on HCP Terraform",
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.NOT_EXISTS_ORG_ON_HCP_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
                "no_interface_info": True,
            },
            {"ret": False, "msg_code": "MSG-82001"},
            id="No interface info",
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.INVALID_TOKEN_ORG_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
            },
            {"ret": False, "msg_code": "MSG-82042"},
            id="Invalid token",
        ),
        pytest.param(
            {
                "cmd_type": "Register",
                "tf_organization_name": TestConstants.RATE_LIMIT_ORG_UUID,
                "tf_project_name": TestConstants.PROJECT_NAME,
            },
            {"ret": False, "msg_code": "MSG-82042"},
            id="Rate limit",
        ),
    ],
)
def test_external_valid_menu_before(
    patch_call_restapi_class,
    mock_objdbca,
    mock_g,
    test_parameter: OptionType,
    expected: ExpectedType,
):
    """Test external_valid_menu_before with parameterized inputs."""
    option = {
        "cmd_type": test_parameter["cmd_type"],
        "entry_parameter": {
            "parameter": {
                "tf_organization_name": test_parameter.get("tf_organization_name"),
                "tf_project_name": test_parameter.get("tf_project_name"),
            }
        },
    }

    # モックの設定
    mock_objdbca.table_select = get_table_select_mock(
        test_parameter.get("no_interface_info", False)
    )

    ret, msg, _ = external_valid_menu_before(mock_objdbca, None, option)

    assert (
        ret == expected["ret"]
    ), f"Expected ret: {expected['ret']}, but got: {ret}, message: {mock_g.appmsg.get_api_message.call_args.args[0]} {msg}"
    if expected["msg_code"]:
        assert mock_g.appmsg.get_api_message.call_args.args[0] == expected["msg_code"]
    else:
        assert len(msg) == 0
