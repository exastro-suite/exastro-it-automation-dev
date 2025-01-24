#   Copyright 2022 NEC Corporation
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
from _pytest.logging import LogCaptureFixture
from unittest import mock, TestCase
from unittest.mock import MagicMock

import os
import psutil
import threading
import multiprocessing
import signal
import datetime
import time
import copy
import random
import requests_mock
import re
import uuid
import importlib
from importlib import import_module, reload

import logging
from flask import g
from libs.job_logger import JobLogging
import job_manager
import job_config
from common import test_common
from tests.jobs.TestJobExecutor import TestExecuteStocker
from libs.sub_processes import SubProcesses
from libs.clean_up_info import CleanUpInfo
from common_libs.common import const
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon


def test_job_manager_main_sigterm_signal():
    """job manager main の終了動作(sigterm signal)
    """

    sub_process_count = 2
    with test_common.requsts_mocker_default() as requests_mocker, \
        mock.patch("job_config.SUB_PROCESS_ACCEPTABLE", sub_process_count):

        # 初期化 / Initialize
        reload(job_manager)
        g.initialize()

        # maintenance-modeをmock化
        requests_mocker.register_uri(
            requests_mock.GET,
            re.compile(rf'^{test_common.platform_api_origin()}/internal-api/platform/maintenance-mode-setting'),
            status_code=200,
            json={"data": {'data_update_stop': 0, 'backyard_execute_stop': 0}},
        )

        # main processの起動
        main_thread = threading.Thread(
            target=job_manager.job_manager_main_process,
            name="main_process",
            daemon=True
        )
        main_thread.start()

        try:
            # sub processの起動確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=sub_process_count)

        finally:
            job_manager.job_manager_process_sigterm_handler(None, None)

            # sub processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=0)

            # main processの終了確認
            assert not main_thread.is_alive()

            main_thread.join()


def test_job_manager_main_sigint_signal():
    """job manager main の終了動作(sigint signal)
    """

    sub_process_count = 2
    with test_common.requsts_mocker_default() as requests_mocker, \
        mock.patch("job_config.SUB_PROCESS_ACCEPTABLE", sub_process_count):

        # 初期化 / Initialize
        reload(job_manager)
        g.initialize()

        # maintenance-modeをmock化
        requests_mocker.register_uri(
            requests_mock.GET,
            re.compile(rf'^{test_common.platform_api_origin()}/internal-api/platform/maintenance-mode-setting'),
            status_code=200,
            json={"data": {'data_update_stop': 0, 'backyard_execute_stop': 0}},
        )

        # main processの起動
        main_thread = threading.Thread(
            target=job_manager.job_manager_main_process,
            name="main_process",
            daemon=True
        )
        main_thread.start()

        try:
            # sub processの起動確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=sub_process_count)

            job_manager.job_manager_process_sigint_handler(None, None)

            # sub processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=0)

            # 終了しているか確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : not main_thread.is_alive())


        finally:
            # sigterm signalの送信
            job_manager.job_manager_process_sigterm_handler(None, None)

            # main processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : not main_thread.is_alive())

            main_thread.join()


def test_db_connect_success():
    """
    Test successful database connection.
    """

    # 初期化 / Initialize
    reload(job_manager)
    g.initialize()

    conn = job_manager.db_connect(None)
    assert isinstance(conn, DBConnectCommon)


def test_db_connect_with_existing_conn():
    """
    Test database connection with existing connection.
    """

    # 初期化 / Initialize
    reload(job_manager)
    g.initialize()

    existing_conn = MagicMock()
    existing_conn.db_disconnect = MagicMock()

    conn = job_manager.db_connect(existing_conn)

    assert isinstance(conn, DBConnectCommon)
    existing_conn.db_disconnect.assert_called_once()


def test_reset_log_level_success():
    """
    Log level is reset successfully from database.
    """

    # 初期化 / Initialize
    reload(job_manager)
    JobLogging.initialize()
    g.initialize()

    with mock.patch.object(DBConnectCommon, "sql_execute", return_value=[{'LOG_LEVEL': 'DEBUG'}]):
        job_manager.reset_log_level()

        assert JobLogging.getLevel() ==  "DEBUG"

    JobLogging.terminate()


def test_job_manager_sub_execute_normal_job():
    """JOB正常終了
    """
    testdata = import_module("tests.db.exports.testdata")

    # パラメータシート作成履歴にレコードを登録する(ステータスを「未実行」とする)
    __make_menu_create_history(testdata)

    # Jobの実行classを試験用に切り替え
    process_kind="menu_create"
    job_config_jobs = {
        "menu_create": {
            "timeout_seconds": 30,
            "module": "tests.jobs.TestJobExecutor",
            "class": "TestNormalJobExecutor",
            "max_job_per_process": 1,
            "extra_config": {
            }
        },
    }

    job_executor_classes = getattr(importlib.import_module("tests.jobs.TestJobExecutor"), "TestNormalJobExecutor")
    with mock.patch('libs.job_threads.JobThreads.get_startable_job_name_list', return_value=["menu_create"]), \
        mock.patch('libs.job_classes.JobClasses.get_job_executor_class', return_value=job_executor_classes), \
        test_common.requsts_mocker_default() as requests_mocker, \
        mock.patch.dict(f"job_config.JOB_CONFIG", job_config_jobs):

        # maintenance-modeをmock化
        requests_mocker.register_uri(
            requests_mock.GET,
            re.compile(rf'^{test_common.platform_api_origin()}/internal-api/platform/maintenance-mode-setting'),
            status_code=200,
            json={"data": {'data_update_stop': 0, 'backyard_execute_stop': 0}},
        )

        # 初期化 / Initialize
        reload(job_manager)
        g.initialize()

        sub_processes = SubProcesses()
        clean_up_info = CleanUpInfo()
        teminating_time = datetime.datetime.now() + datetime.timedelta(seconds=30)

        TestExecuteStocker.initalize()

        try:

            # sub processの起動
            sub_process = threading.Thread(
                target=job_manager.job_manager_sub_process,
                name="sub_process",
                args=(teminating_time, clean_up_info),
                daemon=True
            )
            sub_process.start()

            # queue_query_stmtが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : TestExecuteStocker.call_queue_query_stmt_count > 0)

            # update_queue_to_startが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.update_queue_to_start_queue) == 1)

            # executeが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.executed_queue) == 1)

        finally:
            # sigterm signalの送信
            job_manager.job_manager_process_sigterm_handler(None, None)

            # main processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : not sub_process.is_alive())

            sub_process.join()


def test_job_manager_sub_execute_timeout_job():
    """JOB正常終了
    """
    testdata = import_module("tests.db.exports.testdata")

    # パラメータシート作成履歴にレコードを登録する(ステータスを「未実行」とする)
    __make_menu_create_history(testdata)

    # Jobの実行classを試験用に切り替え
    process_kind="menu_create"
    job_config_jobs = {
        "menu_create": {
            "timeout_seconds": 1,
            "module": "tests.jobs.TestJobExecutor",
            "class": "TestExecuteTimeoutJobExecutor",
            "max_job_per_process": 1,
            "extra_config": {
            }
        },
    }

    job_executor_classes = getattr(importlib.import_module("tests.jobs.TestJobExecutor"), "TestExecuteTimeoutJobExecutor")
    with mock.patch('libs.job_threads.JobThreads.get_startable_job_name_list', return_value=["menu_create"]), \
        mock.patch('libs.job_classes.JobClasses.get_job_executor_class', return_value=job_executor_classes), \
        test_common.requsts_mocker_default() as requests_mocker, \
        mock.patch.dict(f"job_config.JOB_CONFIG", job_config_jobs):

        # maintenance-mode
        requests_mocker.register_uri(
            requests_mock.GET,
            re.compile(rf'^{test_common.platform_api_origin()}/internal-api/platform/maintenance-mode-setting'),
            status_code=200,
            json={"data": {'data_update_stop': 0, 'backyard_execute_stop': 0}},
        )

        # 初期化 / Initialize
        reload(job_manager)
        g.initialize()

        sub_processes = SubProcesses()
        clean_up_info = CleanUpInfo()
        teminating_time = datetime.datetime.now() + datetime.timedelta(seconds=30)

        TestExecuteStocker.initalize()

        try:

            # sub processの起動
            sub_process = threading.Thread(
                target=job_manager.job_manager_sub_process,
                name="sub_process",
                args=(teminating_time, clean_up_info),
                daemon=True
            )
            sub_process.start()

            # queue_query_stmtが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : TestExecuteStocker.call_queue_query_stmt_count > 0)

            # update_queue_to_startが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.update_queue_to_start_queue) == 1)

            # executeが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.executed_queue) == 1)

            # cancelが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.canceled_queue) > 0)

        finally:
            # sigterm signalの送信
            job_manager.job_manager_process_sigterm_handler(None, None)

            # main processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : not sub_process.is_alive())

            sub_process.join()


def test_job_manager_sub_cancel_timeout_job():
    """JOB正常終了
    """
    testdata = import_module("tests.db.exports.testdata")

    # パラメータシート作成履歴にレコードを登録する(ステータスを「未実行」とする)
    __make_menu_create_history(testdata)

    # Jobの実行classを試験用に切り替え
    process_kind="menu_create"
    job_config_jobs = {
        "menu_create": {
            "timeout_seconds": 1,
            "module": "tests.jobs.TestJobExecutor",
            "class": "TestCancelTimeoutJobExecutor",
            "max_job_per_process": 1,
            "extra_config": {
            }
        },
    }

    job_executor_classes = getattr(importlib.import_module("tests.jobs.TestJobExecutor"), "TestCancelTimeoutJobExecutor")
    with mock.patch('libs.job_threads.JobThreads.get_startable_job_name_list', return_value=["menu_create"]), \
        mock.patch('libs.job_classes.JobClasses.get_job_executor_class', return_value=job_executor_classes), \
        test_common.requsts_mocker_default() as requests_mocker, \
        mock.patch.dict(f"job_config.JOB_CONFIG", job_config_jobs), \
        mock.patch("job_config.JOB_CANCEL_TIMEOUT_SECONDS", 1):

        # maintenance-mode
        requests_mocker.register_uri(
            requests_mock.GET,
            re.compile(rf'^{test_common.platform_api_origin()}/internal-api/platform/maintenance-mode-setting'),
            status_code=200,
            json={"data": {'data_update_stop': 0, 'backyard_execute_stop': 0}},
        )

        # 初期化 / Initialize
        reload(job_manager)
        g.initialize()

        sub_processes = SubProcesses()
        clean_up_info = CleanUpInfo()
        teminating_time = datetime.datetime.now() + datetime.timedelta(seconds=30)

        TestExecuteStocker.initalize()

        try:

            # sub processの起動
            sub_process = threading.Thread(
                target=job_manager.job_manager_sub_process,
                name="sub_process",
                args=(teminating_time, clean_up_info),
                daemon=True
            )
            sub_process.start()

            # queue_query_stmtが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : TestExecuteStocker.call_queue_query_stmt_count > 0)

            # update_queue_to_startが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.update_queue_to_start_queue) == 1)

            # executeが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.executed_queue) == 1)

            # cancelが実施されること
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : len(TestExecuteStocker.canceled_queue) > 0)

        finally:
            # sigterm signalの送信
            job_manager.job_manager_process_sigterm_handler(None, None)

            # main processの終了確認
            assert test_common.check_state(
                timeout=5.0, conditions=lambda : not sub_process.is_alive())

            sub_process.join()


def test_joblogging_success():
    """
    Log level is reset successfully from database.
    """

    # 初期化 / Initialize
    JobLogging.initialize()

    assert isinstance(JobLogging.getLogger(), logging.Logger)

    log_level = "DEBUG"
    JobLogging.setLevel(log_level)
    assert JobLogging.getLevel() == log_level

    log_level = "ERROR"
    log_message = "テストエラーメッセージ"
    with TestCase().assertLogs(level=log_level) as cm_err:
        JobLogging.error(log_message)

    assert len(cm_err.output) == 1
    assert cm_err.output[0] == f"{log_level}:root:{log_message}"

    log_level = "WARNING"
    log_message = "テストワーニングメッセージ"
    with TestCase().assertLogs(level=log_level) as cm_warn:
        JobLogging.warning(log_message)

    assert len(cm_warn.output) == 1
    assert cm_warn.output[0] == f"{log_level}:root:{log_message}"

    log_level = "INFO"
    log_message = "テストインフォメッセージ"
    with TestCase().assertLogs(level=log_level) as cm_info:
        JobLogging.info(log_message)

    assert len(cm_info.output) == 1
    assert cm_info.output[0] == f"{log_level}:root:{log_message}"

    log_level = "DEBUG"
    log_message = "テストデバッグメッセージ"
    with TestCase().assertLogs(level=log_level) as cm_debug:
        JobLogging.debug(log_message)

    assert len(cm_debug.output) == 1
    assert cm_debug.output[0] == f"{log_level}:root:{log_message}"

    JobLogging.terminate()


def __make_menu_create_history(testdata):
    """テスト用共通
    Args:
        testdata: testdata
    """

    organization_id = list(testdata.ORGANIZATIONS.keys())[0]
    workspace_id = testdata.ORGANIZATIONS[organization_id]["workspace_id"][0]

    date_now = datetime.datetime.now()
    target_date = date_now + datetime.timedelta(seconds=20)

    data = {
        "MENU_CREATE_ID": str(uuid.uuid4()),
        "STATUS_ID": const.MENU_CREATE_UNEXEC,
        "CREATE_TYPE": "1",
        "DISUSE_FLAG": 0,
        "LAST_UPDATE_USER": "admin",
        "LAST_UPDATE_TIMESTAMP": target_date
    }

    conn = DBConnectWs(workspace_id, organization_id)
    conn.db_transaction_start()
    ret = conn.table_insert("T_MENU_CREATE_HISTORY", data, "HISTORY_ID")
    conn.db_transaction_end(True)

    return

