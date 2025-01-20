#   Copyright 2024 NEC Corporation
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
from unittest import mock
from importlib import import_module

import job_config
from flask import g
from tests.common import request_parameters, test_common
from tests.libs import queries_test_menu_create
from jobs.menu_create_executor import MenuCreateExecutor
from libs.menu_create import backyard_main
from libs.job_queue_row import JobQueueRow
from libs.job_logger import JobLogging
from libs.job_exception import JobTimeoutException
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common import const


def test_menu_create_execute_nomally():
    """menu create execute 正常系 / menu create execute nomally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # パラメータシート作成履歴にレコードを登録する(ステータスを「未実行」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_UNEXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # job queueの取得用SQLを発行
    job_queue_sql = executor.queue_query_stmt(conn)

    assert job_queue_sql != ""
    assert type(job_queue_sql) is str

    # ステータスを「実行中」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is True

    with mock.patch.object(backyard_main,  "backyard_main", return_value=True):
        # backyard main処理を実行
        executor.execute(conn)

        # 作業対象のステータスを取得
        ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

        # ステータスIDが3(完了)であること
        assert ret[0].get("STATUS_ID") == const.MENU_CREATE_COMP

    # DB切断
    conn.db_disconnect()


def test_menu_create_execute_error():
    """menu create execute 異常系 / menu create execute error pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # パラメータシート作成履歴にレコードを登録する(ステータスを「未実行」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_UNEXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # 排他制御ロックを起こすために別のインスタンスを作成
    executor_2 = MenuCreateExecutor(job_queue_row, config)

    # 排他制御ロックを通すために、レコードロックを実施
    conn.db_transaction_start()
    result = executor_2.exclusive_control()
    assert result is True

    # ステータスを「実行中」に変更（排他制御ロックのため失敗すること）
    result = executor.update_queue_to_start(job_queue_row, conn)
    assert result is False

    # レコードロックを解除
    executor_2.exclusive_control_commit()

    # update_queue_to_startを実行しステータスを「実行中」に変更
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
            # 作業対象のステータスを取得
            ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

            # ステータスIDが2(実行中)のままであること
            assert ret[0].get("STATUS_ID") == const.MENU_CREATE_EXEC

    # backyard_mainでFalseを返却
    with mock.patch.object(backyard_main, 'backyard_main', return_value=False):
        try:
            # backyard main処理を実行
            executor.execute(conn)

        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # 作業対象のステータスを取得
            ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

            # ステータスIDが4(完了(異常))であること
            assert ret[0].get("STATUS_ID") == const.MENU_CREATE_ERR

    # DB切断
    conn.db_disconnect()


def test_menu_create_execute_cancel_nomally():
    """menu create execute キャンセル 正常系 / menu create execute cancel nomally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # パラメータシート作成履歴にレコードを登録する(ステータスを「実行中」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_EXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # キャンセルを実行
    executor.cancel(conn)

    # 作業対象のステータスを取得
    ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

    # ステータスIDが4(完了(異常))であること
    assert ret[0].get("STATUS_ID") == const.MENU_CREATE_ERR

    # DB切断
    conn.db_disconnect()


def test_menu_create_execute_cancel_error():
    """menu create execute キャンセル 異常系 / menu create execute cancel error pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # パラメータシート作成履歴にレコードを登録する(ステータスを「実行中」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_EXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # db_transaction_start実行時にJobTimeoutExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=JobTimeoutException()):
        try:
            # キャンセルを実行
            executor.cancel(conn)
        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # 作業対象のステータスを取得
            ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

            # ステータスIDが2(実行中)のままであること
            assert ret[0].get("STATUS_ID") == const.MENU_CREATE_EXEC

    # db_transaction_start実行時にExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=Exception()):
        try:
            # キャンセルを実行
            executor.cancel(conn)
        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # 作業対象のステータスを取得
            ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

            # ステータスIDが2(実行中)のままであること
            assert ret[0].get("STATUS_ID") == const.MENU_CREATE_EXEC

    # DB切断
    conn.db_disconnect()


def test_menu_create_execute_cleanup_nomally():
    """menu create execute クリーンアップ 正常系 / menu create execute cleanup nomally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # パラメータシート作成履歴にレコードを登録する(ステータスを「実行中」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_EXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # クリーンアップを実行
    executor.clean_up()

    # 作業対象のステータスを取得
    ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

    # ステータスIDが2(完了(実行中))のままであること
    assert ret[0].get("STATUS_ID") == const.MENU_CREATE_EXEC

    # 対象レコードのLAST_UPDATE_TIMESTAMPをjob_configのtimeout_secondsの値より過ぎた時刻に設定する
    timeout_seconds = config.get("timeout_seconds") * 10  # 念のため10倍の時間を設定する
    date_now = datetime.datetime.now()
    target_date = date_now - datetime.timedelta(seconds=timeout_seconds)
    sql = "UPDATE `{}` SET LAST_UPDATE_TIMESTAMP = '{}' WHERE `{}` = '{}'".format("T_MENU_CREATE_HISTORY", target_date, "HISTORY_ID", job_key)
    conn.db_transaction_start()
    conn.sql_execute(sql, [])
    conn.db_transaction_end(True)

    # クリーンアップを実行
    executor.clean_up()

    # 作業対象のステータスを取得
    ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

    # ステータスIDが4(完了(異常))であること
    assert ret[0].get("STATUS_ID") == const.MENU_CREATE_ERR

    # DB切断
    conn.db_disconnect()


def test_menu_create_execute_cleanup_error():
    """menu create execute クリーンアップ 異常系 / menu create execute cleanup error pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")
    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # パラメータシート作成履歴にレコードを登録する(ステータスを「実行中」とする)
    conn.db_transaction_start()
    result = make_menu_create_history(conn, const.MENU_CREATE_EXEC, "1")
    conn.db_transaction_end(True)

    # history_idをjob_keyとして使う
    job_key = result[0].get("HISTORY_ID")

    # 対象レコードのLAST_UPDATE_TIMESTAMPをjob_configのtimeout_secondsの値より過ぎた時刻に設定する
    timeout_seconds = config.get("timeout_seconds") * 10  # 念のため10倍の時間を設定する
    date_now = datetime.datetime.now()
    target_date = date_now - datetime.timedelta(seconds=timeout_seconds)
    sql = "UPDATE `{}` SET LAST_UPDATE_TIMESTAMP = '{}' WHERE `{}` = '{}'".format("T_MENU_CREATE_HISTORY", target_date, "HISTORY_ID", job_key)
    conn.db_transaction_start()
    conn.sql_execute(sql, [])
    conn.db_transaction_end(True)

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # clean_upでステータス更新処理時にExceptionに渡す
    with mock.patch.object(DBConnectWs, 'db_transaction_start', side_effect=Exception()):
        try:
            # クリーンアップを実行
            executor.clean_up()
        except Exception:
            # raiseされるためexceptを通る
            assert True

        finally:
            # 作業対象のステータスを取得
            ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

            # ステータスIDが2(実行中)のままであること
            assert ret[0].get("STATUS_ID") == const.MENU_CREATE_EXEC

    # DB切断
    conn.db_disconnect()


def test_menu_create_backyard_main():
    """menu create backyard main 正常系 / menu create backyard main nomally pattern
    """
    # 初期化 / Initialize
    JobLogging.initialize()
    g.initialize()

    testdata = import_module("tests.db.exports.testdata")

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]
    g.ORGANIZATION_ID = organization_id
    g.WORKSPACE_ID = workspace_id

    # パラメータシート定義・作成を実行し、パラメータシート作成ジョブが起動する条件を作成する（新規作成）。
    param_create_data_01 = sample_data_parametersheet_create_new()
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/create/define/execute/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=param_create_data_01)

    assert result.status_code == 200, "parameter sheet create response code"

    # 作成したパラメータシート作成のデータを取得
    result_json = result.json()

    # history_idをjob_keyとして使う
    job_key = result_json.get("data").get("history_id")

    # configの取得
    config = job_config.JOB_CONFIG["menu_create"]

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # データベースへ接続
    conn = DBConnectWs(workspace_id, organization_id)

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # ステータスを「実行中」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)

    # 成功を返すこと
    assert result == True

    # backyard main処理を実行
    executor.execute(conn)

    # 作業対象のステータスを取得
    ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

    # ステータスIDが3(完了)であること
    assert ret[0].get("STATUS_ID") == const.MENU_CREATE_COMP

    # パラメータシート定義・作成を実行し、パラメータシート作成ジョブが起動する条件を作成する（編集）。
    param_edit_data_01 = sample_data_parametersheet_create_edit(organization_id, workspace_id, param_create_data_01["menu"]["menu_name_rest"])
    result = requests.post(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/create/define/execute/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja"),
        json=param_edit_data_01)

    assert result.status_code == 200, "parameter sheet create response code"

    # 作成したパラメータシート作成のデータを取得
    result_json = result.json()

    # history_idをjob_keyとして使う
    job_key = result_json.get("data").get("history_id")

    # queueを生成する
    job_queue_row = make_queue(organization_id, workspace_id, job_key, datetime.datetime.now())

    # パラメータシート作成のExecutorをインスタンス化
    executor = MenuCreateExecutor(job_queue_row, config)

    # ステータスを「実行中」に変更
    result = executor.update_queue_to_start(job_queue_row, conn)

    # 成功を返すこと
    assert result == True

    # backyard main処理を実行
    executor.execute(conn)

    # 作業対象のステータスを取得
    ret = conn.sql_execute(queries_test_menu_create.SQL_SELECT_MENU_CREATE_HISTORY, {"history_id": job_key})

    # ステータスIDが3(完了)であること
    assert ret[0].get("STATUS_ID") == const.MENU_CREATE_COMP

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
        "JOB_NAME": "menu_create",
        "LAST_UPDATE_TIMESTAMP": str(last_update_timestamp),
    }

    return JobQueueRow(row)


def make_menu_create_history(conn: DBConnectWs, status_id, create_type):
    """テスト用共通
    Args:
        conn (DBConnectCommon): db connection (ita-user)
        status_id: status id (1: 未実行, 2: 実行中, 3: 完了, 4: 完了(異常))
        create_type: create_type (1: 新規作成, 2: 編集, 3: 初期化)
    """
    # timeout_seconds = config.get("timeout_seconds") * 2  # 念のため倍の時間を設定する
    date_now = datetime.datetime.now()
    target_date = date_now + datetime.timedelta(seconds=40)

    data = {
        "MENU_CREATE_ID": str(uuid.uuid4()),
        "STATUS_ID": status_id,
        "CREATE_TYPE": create_type,
        "DISUSE_FLAG": 0,
        "LAST_UPDATE_USER": "admin",
        "LAST_UPDATE_TIMESTAMP": target_date
    }
    ret = conn.table_insert("T_MENU_CREATE_HISTORY", data, "HISTORY_ID")

    return ret


def sample_data_parametersheet_create_new():
    """create workspace parameter
    Returns:
        dict: parametersheet create new bocy
    """
    body = {
        "group": {},
        "column": {
            "c1": {
                "item_name": "項目 1",
                "item_name_rest": "item_1",
                "required": "0",
                "uniqued": "0",
                "column_class": "SingleTextColumn",
                "column_class_id": "1",
                "description": "",
                "remarks": "",
                "column_group": None,
                "display_order": 0,
                "create_column_id": None,
                "single_string_maximum_bytes": "128",
                "single_string_regular_expression": "",
                "single_string_default_value": ""
            }
        },
        "menu": {
            "menu_create_id": None,
            "menu_name": "param_01",
            "menu_name_rest": "param_01",
            "display_order": "101",
            "description": None,
            "remarks": None,
            "sheet_type_id": "1",
            "sheet_type": "パラメータシート（ホスト/オペレーションあり）",
            "role_list": [
                "_ws1-admin"
            ],
            "unique_constraint": None,
            "hostgroup": "0",
            "vertical": "0",
            "menu_group_for_input": "入力用",
            "menu_group_for_input_id": "502",
            "menu_group_for_subst": "代入値自動登録用",
            "menu_group_for_subst_id": "503",
            "menu_group_for_ref": "参照用",
            "menu_group_for_ref_id": "504",
            "columns": [
                "c1"
            ]
        },
        "type": "create_new"
    }

    return body


def sample_data_parametersheet_create_edit(organization_id, workspace_id, menu_name_rest):
    """create workspace parameter
    Returns:
        dict: parametersheet create edit bocy
    """
    # 編集対象のデータを取得
    result = requests.get(
        f"http://{os.environ.get('ITA_API_ORGANIZATION_HOST')}:{os.environ.get("ITA_API_ORGANIZATION_PORT")}/api/{organization_id}/workspaces/{workspace_id}/ita/create/define/{menu_name_rest}/",
        headers=request_parameters.ita_api_organization_request_headers(user_id="admin", workspace_role=["_ws1-admin"], language="ja")
        )
    result_json = result.json()
    menu_info = result_json.get("data").get("menu_info")

    # 「編集」用のbocyを作成
    body = {
        "group": menu_info.get("group"),
        "column": menu_info.get("column"),
        "menu": menu_info.get("menu"),
        "type": "edit"
    }

    # column_classが空のため補完
    body["column"]["c1"]["column_class"] = "SingleTextColumn"

    return body