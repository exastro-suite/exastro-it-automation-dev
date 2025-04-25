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
from unittest.mock import MagicMock, patch
from backyard_main import menu_export_exec, AppException


@pytest.fixture
def mock_objdbca():
    """Fixture to mock the DBConnectWs object."""
    mock = MagicMock()
    mock._db = "mock_db"
    return mock


@pytest.fixture
def mock_record():
    """Fixture to provide a mock record for menu_export_exec."""
    return {
        "EXECUTION_NO": "12345",
        "JSON_STORAGE_ITEM": json.dumps({
            "menu": ["menu1", "menu2"],
            "mode": "1",
            "abolished_type": "1",
            "specified_timestamp": None,
            "journal_type": "1"
        })
    }


@pytest.fixture
def mock_workspace_id():
    """Fixture to provide a mock workspace ID."""
    return "mock_workspace_id"


@pytest.fixture
def mock_export_menu_dir(tmp_path):
    """Fixture to provide a temporary export menu directory."""
    export_dir = tmp_path / "export_menu"
    export_dir.mkdir()
    return str(export_dir)


@pytest.fixture
def mock_uploadfiles_dir(tmp_path):
    """Fixture to provide a temporary uploadfiles directory."""
    upload_dir = tmp_path / "uploadfiles"
    upload_dir.mkdir()
    return str(upload_dir)


@patch("backyard_main.file_open_write_close")
@patch("backyard_main.load_table.bulkLoadTable")
@patch("backyard_main.shutil.move")
@patch("backyard_main.shutil.rmtree")
@patch("backyard_main.os.makedirs")
@patch("backyard_main.os.path.isdir")
@patch("backyard_main.os.path.isfile")
@patch("backyard_main.subprocess.run")
def test_menu_export_exec_success(
    mock_subprocess_run,
    mock_isfile,
    mock_isdir,
    mock_makedirs,
    mock_rmtree,
    mock_shutil_move,
    mock_bulkLoadTable,
    mock_file_open_write_close,
    mock_objdbca,
    mock_record,
    mock_workspace_id,
    mock_export_menu_dir,
    mock_uploadfiles_dir,
):
    """Test menu_export_exec for a successful execution."""
    # Mock subprocess.run to simulate mysqldump
    mock_subprocess_run.return_value = MagicMock(stdout="CREATE TABLE mock_table;", returncode=0)

    # Mock os.path.isfile and os.path.isdir
    mock_isfile.return_value = True
    mock_isdir.return_value = True

    # Mock bulkLoadTable to return a mock object
    mock_menu = MagicMock()
    mock_menu.rest_export_filter.return_value = ("000-00000", [{"parameter": {}, "file": {}, "file_path": {}}], None)
    mock_bulkLoadTable.return_value = mock_menu

    # Call the function
    result, msg, trace_msg = menu_export_exec(
        mock_objdbca,
        mock_record,
        mock_workspace_id,
        mock_export_menu_dir,
        mock_uploadfiles_dir,
    )

    # Assertions
    assert result is True
    assert msg is None
    assert trace_msg is None

    # Verify subprocess.run was called for mysqldump
    mock_subprocess_run.assert_called()

    # Verify file_open_write_close was called for writing files
    mock_file_open_write_close.assert_called()

    # Verify bulkLoadTable was called for each menu
    assert mock_bulkLoadTable.call_count == 2  # Two menus in the mock_record


@patch("backyard_main.file_open_write_close")
@patch("backyard_main.load_table.bulkLoadTable")
@patch("backyard_main.shutil.move")
@patch("backyard_main.shutil.rmtree")
@patch("backyard_main.os.makedirs")
@patch("backyard_main.os.path.isdir")
@patch("backyard_main.os.path.isfile")
@patch("backyard_main.subprocess.run")
def test_menu_export_exec_mysqldump_error(
    mock_subprocess_run,
    mock_isfile,
    mock_isdir,
    mock_makedirs,
    mock_rmtree,
    mock_shutil_move,
    mock_bulkLoadTable,
    mock_file_open_write_close,
    mock_objdbca,
    mock_record,
    mock_workspace_id,
    mock_export_menu_dir,
    mock_uploadfiles_dir,
):
    """Test menu_export_exec when mysqldump fails."""
    # Mock subprocess.run to simulate mysqldump failure
    mock_subprocess_run.return_value = MagicMock(stdout="", stderr="mysqldump error", returncode=1)

    # Mock os.path.isfile and os.path.isdir
    mock_isfile.return_value = True
    mock_isdir.return_value = True

    # Call the function
    result, msg, trace_msg = menu_export_exec(
        mock_objdbca,
        mock_record,
        mock_workspace_id,
        mock_export_menu_dir,
        mock_uploadfiles_dir,
    )

    # Assertions
    assert result is False
    assert "mysqldump error" in str(msg)
    assert trace_msg is not None

    # Verify subprocess.run was called for mysqldump
    mock_subprocess_run.assert_called()


@patch("backyard_main.file_open_write_close")
@patch("backyard_main.load_table.bulkLoadTable")
@patch("backyard_main.shutil.move")
@patch("backyard_main.shutil.rmtree")
@patch("backyard_main.os.makedirs")
@patch("backyard_main.os.path.isdir")
@patch("backyard_main.os.path.isfile")
@patch("backyard_main.subprocess.run")
def test_menu_export_exec_bulkLoadTable_error(
    mock_subprocess_run,
    mock_isfile,
    mock_isdir,
    mock_makedirs,
    mock_rmtree,
    mock_shutil_move,
    mock_bulkLoadTable,
    mock_file_open_write_close,
    mock_objdbca,
    mock_record,
    mock_workspace_id,
    mock_export_menu_dir,
    mock_uploadfiles_dir,
):
    """Test menu_export_exec when bulkLoadTable fails."""
    # Mock subprocess.run to simulate mysqldump
    mock_subprocess_run.return_value = MagicMock(stdout="CREATE TABLE mock_table;", returncode=0)

    # Mock os.path.isfile and os.path.isdir
    mock_isfile.return_value = True
    mock_isdir.return_value = True

    # Mock bulkLoadTable to raise an exception
    mock_bulkLoadTable.side_effect = AppException("499-00001", ["bulkLoadTable error"], ["bulkLoadTable error"])

    # Call the function
    result, msg, trace_msg = menu_export_exec(
        mock_objdbca,
        mock_record,
        mock_workspace_id,
        mock_export_menu_dir,
        mock_uploadfiles_dir,
    )

    # Assertions
    assert result is False
    assert "bulkLoadTable error" in str(msg)
    assert trace_msg is not None

    # Verify bulkLoadTable was called
    mock_bulkLoadTable.assert_called()