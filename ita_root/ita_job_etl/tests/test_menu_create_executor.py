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
import ulid
import json
import time
import datetime
import logging
import threading
from contextlib import closing
from _pytest.logging import LogCaptureFixture
from unittest import mock
from importlib import import_module
import copy

import job_manager
import job_config
from tests.common import test_common
from jobs.menu_create_executor import MenuCreateExecutor
from libs.menu_create.backyard_main import backyard_main
from libs.job_queue_row import JobQueueRow
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon


def test_execute_user_get_nomally():
    """ユーザー取得正常系 / User registration normal pattern
    """
    testdata = import_module("tests.db.exports.testdata")

    with test_common.requsts_mocker_default():

        # 処理用データ準備


        # que作成
        queue = JobQueueRow()

        # DB接続
        config = job_config.JOB_CONFIG[queue.job_name]
        executor = MenuCreateExecutor(queue, config)
        conn = executor.db_connect(queue)

        # ステータスを「実行中」に変更
        result = executor.update_queue_to_start(queue, conn)
        # 成功を返すこと
        assert result

        # backyard main処理をmock
        executor.execute(conn)

        # 作業対象のステータスが「完了」に変更
        t = select_T_MENU_CREATE_HISTORY(organization_id, workspace_id, queue.job_key)
        assert t["XXXXX"] == True




def make_queue(lang, organization_id, insert_queue=True) -> JobQueueRow:
    """テスト用共通:Queue情報生成

    Args:
        lang (_type_): _description_
        organization_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    process_id = ulid.new().str
    process_exec_id = ulid.new().str
    file_id = ulid.new().str

    queue={
        "PROCESS_ID": process_id,
        "PROCESS_KIND": const.PROCESS_KIND_USER_EXPORT,
        "PROCESS_EXEC_ID": process_exec_id,
        "ORGANIZATION_ID": organization_id,
        "WORKSPACE_ID": None,
        "LAST_UPDATE_USER": job_manager_const.SYSTEM_USER_ID,
        "LAST_UPDATE_TIMESTAMP": str(datetime.datetime.now()),
    }

    with closing(DBconnector().connect_orgdb(organization_id)) as conn,\
        conn.cursor() as cursor:

        cursor.execute('''
            INSERT INTO T_JOBS_USER_EXPORT
            (JOB_ID,
            JOB_TYPE,
            JOB_STATUS,
            LANGUAGE)
            VALUES
            (%(JOB_ID)s,
            %(JOB_TYPE)s,
            %(JOB_STATUS)s,
            %(LANGUAGE)s)
            ''',
            {"JOB_ID": process_exec_id,
            "JOB_TYPE": const.PROCESS_KIND_USER_IMPORT,
            "JOB_STATUS": const.JOB_USER_NOT_EXEC,
            "LANGUAGE": lang}
        )

        conn.commit()

    if insert_queue:
        test_common.insert_queue([queue])

    return queue