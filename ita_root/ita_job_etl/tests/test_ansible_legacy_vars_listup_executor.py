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
import os
import uuid
import datetime
import requests
# import shutil
import base64
from unittest import mock
from importlib import import_module

import job_config
from flask import g
from tests.common import request_parameters, test_common
from tests.libs import queries_test_common, queries_test_ansible_legacy_vars_listup
from jobs.ansible_legacy_vars_listup_executor import AnsibleLegacyVarsListupExecutor
from libs.ansible_legacy_vars_listup import backyard_main
from libs.job_queue_row import JobQueueRow
from libs.job_logger import JobLogging
from libs.job_exception import JobTimeoutException
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common import const


def test_ansible_legacy_vars_listup_execute_normally():
    """ ansible legacy vars listup execute 正常系 /  ansible legacy vars listup execute normally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # 起動フラグ管理テーブルのレコードを更新
    conn.db_transaction_start()
    result = set_loaded_flg(conn, const.PROC_LOADED_ID_ANSIBLE_LEGACY)
    conn.db_transaction_end(True)

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # job queueの取得用SQLを発行
    job_queue_sql = executor.queue_query_stmt(conn)

    assert job_queue_sql != ""
    assert type(job_queue_sql) is str

    # LOADED_FLGを「1」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    # LOADE_FLGが「1」であることを確認
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    with mock.patch.object(backyard_main,  "backyard_main", return_value=True):
        # backyard main処理を実行
        executor.execute(conn)

    # LOADE_FLGが「1」であることを確認
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    # DB切断
    conn.db_disconnect()


def test_ansible_legacy_vars_listup_execute_error():
    """ ansible legacy vars listup execute 異常系 /  ansible legacy vars listup execute error pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # 起動フラグ管理テーブルのレコードを更新
    conn.db_transaction_start()
    result = set_loaded_flg(conn, const.PROC_LOADED_ID_ANSIBLE_LEGACY)
    conn.db_transaction_end(True)

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # 排他制御ロックを起こすために別のインスタンスを作成
    executor_2 = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # 排他制御ロックを通すために、レコードロックを実施
    conn.db_transaction_start()
    result = executor_2.exclusive_control()
    assert result is True

    # LOADED_FLGを「1」に変更（排他制御ロックのため失敗すること）
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is False

    # レコードロックを解除
    executor_2.exclusive_control_commit()

    # update_queue_to_startを実行しLOADED_FLGを「1」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    # 再度update_queue_to_startを実行し、Falseを返却することを確認
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is False

    # db_transaction_start実行時にExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=Exception()):
        result = executor.update_queue_to_start(job_queue_row, conn)
        assert result is False

    # backyard_main処理でJobTimeoutExceptionに渡す
    with mock.patch.object(backyard_main, 'backyard_main', side_effect=JobTimeoutException()):
        try:
            # backyard main処理を実行
            executor.execute(conn)

        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # LOADE_FLGが「1」のままであること
            ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
            assert ret[0].get("LOADED_FLG") == "1"

    # backyard_mainでFalseを返却
    with mock.patch.object(backyard_main, 'backyard_main', return_value=False):
        try:
            # backyard main処理を実行
            executor.execute(conn)

        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # LOADE_FLGが「0」になっていること
            ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
            assert ret[0].get("LOADED_FLG") == "0"

    # DB切断
    conn.db_disconnect()


def test_ansible_legacy_vars_listup_execute_cancel_normally():
    """ ansible legacy vars listup execute キャンセル 正常系 /  ansible legacy vars listup execute cancel normally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # 起動フラグ管理テーブルのレコードを更新
    conn.db_transaction_start()
    result = set_loaded_flg(conn, const.PROC_LOADED_ID_ANSIBLE_LEGACY)
    conn.db_transaction_end(True)

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # update_queue_to_startを実行しLOADED_FLGを「1」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    # LOADE_FLGが「1」になっていること
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    # キャンセルを実行
    executor.cancel(conn)

    # LOADE_FLGが「0」になっていること
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "0"

    # DB切断
    conn.db_disconnect()


def test_ansible_legacy_vars_listup_execute_cancel_error():
    """ ansible legacy vars listup execute キャンセル 異常系 /  ansible legacy vars listup execute cancel error pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # 起動フラグ管理テーブルのレコードを更新
    conn.db_transaction_start()
    result = set_loaded_flg(conn, const.PROC_LOADED_ID_ANSIBLE_LEGACY)
    conn.db_transaction_end(True)

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # update_queue_to_startを実行しLOADED_FLGを「1」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    # LOADE_FLGが「1」になっていること
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    # db_transaction_start実行時にJobTimeoutExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=JobTimeoutException()):
        try:
            # キャンセルを実行
            executor.cancel(conn)
        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # LOADE_FLGが「1」のままであること
            ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
            assert ret[0].get("LOADED_FLG") == "1"

    # db_transaction_start実行時にExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=Exception()):
        try:
            # キャンセルを実行
            executor.cancel(conn)
        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # LOADE_FLGが「1」のままであること
            ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
            assert ret[0].get("LOADED_FLG") == "1"

    # DB切断
    conn.db_disconnect()


def test_ansible_legacy_vars_listup_execute_cleanup_normally():
    """ ansible legacy vars listup execute クリーンアップ 正常系 /  ansible legacy vars listup execute cleanup normally pattern
    """
    # クリーンアップによって実行される処理が無いため、AnsibleLegacyVarsListupExecutorをインスタンス化してclean_up処理が通ることのみを確認して終了
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # 起動フラグ管理テーブルのレコードを更新
    conn.db_transaction_start()
    result = set_loaded_flg(conn, const.PROC_LOADED_ID_ANSIBLE_LEGACY)
    conn.db_transaction_end(True)

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # クリーンアップを実行
    executor.clean_up()

    # DB切断
    conn.db_disconnect()


def test_ansible_legacy_vars_listup_backyard_main():
    """ ansible legacy vars listup backyard main 正常系 /  ansible legacy vars listup backyard main normally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]
    g.ORGANIZATION_ID = organization_id
    g.WORKSPACE_ID = workspace_id

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # 登録情報
    movement_name = "ansl_mov_test_01"
    playbook_file = "sample_playbook"

    # Ansible-Legacy Mogement一覧にレコードを登録
    body_01 = sample_data_movement_register(movement_name)
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/menu/movement_list_ansible_legacy/maintenance/all/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=body_01)

    assert result.status_code == 200, "ansible legacy movement register success"

    # Playbook素材集への登録はRESTAPI経由だとファイルの格納がうまくいかないため、直接レコード登録とファイル格納を行う
    playbook_uuid = str(uuid.uuid4())
    parameter = {
        "PLAYBOOK_MATTER_ID": playbook_uuid,
        "PLAYBOOK_MATTER_NAME": playbook_file,
        "PLAYBOOK_MATTER_FILE": playbook_file + ".yml",
        "DISUSE_FLAG": "0",
        "LAST_UPDATE_TIMESTAMP": datetime.datetime.now(),
        "LAST_UPDATE_USER": "admin"
    }

    conn.db_transaction_start()
    ret = conn.sql_execute(queries_test_ansible_legacy_vars_listup.SQL_INSERT_ANSL_MATL_COLL, parameter)
    conn.db_transaction_end(True)

    # playbookファイルを格納するディレクトリを作成
    file_dir =  os.environ.get("STORAGEPATH") + "{org_id}/{ws_id}/uploadfiles/20202/playbook_file/{uuid}/".format(org_id=organization_id, ws_id=workspace_id, uuid=playbook_uuid)
    os.makedirs(file_dir)

    # playbookファイルを作成
    file_path = file_dir + playbook_file + ".yml"
    f = open(file_path, 'w')
    f.write('- command: echo {{ VAR_01 }}\n- command: echo {{ VAR_02 }}')
    f.close()

    assert os.path.isfile(file_path) is True

    # Ansible-Legacy Movement-Playbook紐付にレコードを登録
    body_02 = sample_data_movement_playbook_link_register(movement_name, playbook_file)
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/menu/movement_playbook_link/maintenance/all/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=body_02)

    assert result.status_code == 200, "ansible legacy movement playbook link register success"

    # job_keyをセット
    job_key = const.PROC_LOADED_ID_ANSIBLE_LEGACY

    # configの取得
    config = job_config.JOB_CONFIG["ansible_legacy_vars_listup"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # Ansible Legacy変数刈り取りのExecutorをインスタンス化
    executor = AnsibleLegacyVarsListupExecutor(job_queue_row, config)

    # job queueの取得用SQLを発行
    job_queue_sql = executor.queue_query_stmt(conn)

    assert job_queue_sql != ""
    assert type(job_queue_sql) is str

    # LOADED_FLGを「1」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    # LOADE_FLGが「1」であることを確認
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    # backyard main処理を実行
    executor.execute(conn)

    # LOADE_FLGが「1」であることを確認
    ret = conn.sql_execute(queries_test_common.SQL_SELECT_PROC_LOADED_LIST, {"row_id": const.PROC_LOADED_ID_ANSIBLE_LEGACY})
    assert ret[0].get("LOADED_FLG") == "1"

    # 変数刈り取り後に、登録したプレイブックの変数がテーブルに保存されていることを確認
    ret = conn.sql_execute("SELECT * FROM T_ANSL_MVMT_VAR_LINK WHERE VARS_NAME = %(vars_name)s", {"vars_name": "VAR_01"})
    assert len(ret) > 0

    ret = conn.sql_execute("SELECT * FROM T_ANSL_MVMT_VAR_LINK WHERE VARS_NAME = %(vars_name)s", {"vars_name": "VAR_02"})
    assert len(ret) > 0

    # DB切断
    conn.db_disconnect()


def make_queue(organization_id, workspace_id, job_key, last_update_timestamp) -> JobQueueRow:
    """テスト用共通:Queue情報生成

    Args:
        organization_id (str): organization id
        workspace_id (str): workspace id
        job_key (str): job key
        last_update_timestamp(datetime): last update timestamp

    Returns:
        JobQueueRow: job queue record
    """
    row = {
        "ORGANIZATION_ID": organization_id,
        "WORKSPACE_ID": workspace_id,
        "JOB_KEY": job_key,
        "JOB_NAME": "ansible_legacy_vars_listup",
        "LAST_UPDATE_TIMESTAMP": str(last_update_timestamp),
    }

    return JobQueueRow(row)


def set_loaded_flg(conn: DBConnectWs, row_id):
    """テスト用共通
    Args:
        conn (DBConnectCommon): db connection (ita-user)
        row_id: row id
    """
    data = {
        "ROW_ID": row_id,
        "LOADED_FLG": 0,
    }
    ret = conn.table_update("T_COMN_PROC_LOADED_LIST", data, "ROW_ID", False, True)

    return ret


def sample_data_movement_register(movement_name):
    """ movement register parameter
    Returns:
        dict: movement register body
    """

    body = [
        {
            "parameter": {
                "discard": "0",
                "movement_id": None,
                "movement_name": movement_name,
                "delay_timer": None,
                "host_specific_format": "IP",
                "winrm_connection": None,
                "header_section": "- hosts: all\n  remote_user: \"{{ __loginuser__ }}\"\n  gather_facts: no",
                "optional_parameter": None,
                "ansible_cfg": None,
                "ansible_agent_execution_environment": None,
                "ansibel_builder_options": None,
                "execution_environment": None,
                "remarks": None,
                "last_update_date_time": None,
                "last_updated_user": None
            },
            "type": "Register"
        }
    ]

    return body


def sample_data_playbook_register(playbook_name):
    """ playbook register parameter
    Returns:
        dict: playbook register body
    """
    target_file = os.getcwd() + "/tests/sample_files/" + playbook_name + ".yml"

    with open(target_file, mode="rb") as f:
        base64_str = base64.b64encode(f.read()).decode()

    body = [
        {
            "file": {
                "playbook_file": base64_str
            },
            "parameter": {
                "discard": "0",
                "item_no": None,
                "playbook_name": playbook_name,
                "playbook_file": playbook_name + ".yml",
                "target_linux": None,
                "target_windows": None,
                "target_other": None,
                "python_necessary": None,
                "description": None,
                "description_en": None,
                "remarks": None,
                "last_update_date_time": None,
                "last_updated_user": None
            },
            "type": "Register"
        }
    ]

    return body

def sample_data_movement_playbook_link_register(movement_name, playbook_file):
    """ movement playbook link register parameter
    Returns:
        dict: movement register body
    """

    body = [
        {
            "parameter": {
                "discard": "0",
                "associated_item_no": None,
                "movement": movement_name,
                "playbook_file": playbook_file,
                "include_order": "1",
                "remarks": None,
                "last_update_date_time": None,
                "last_updated_user": None
            },
            "type": "Register"
        }
    ]

    return body