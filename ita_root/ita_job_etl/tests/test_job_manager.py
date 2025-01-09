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
from unittest import mock
from unittest.mock import MagicMock

import os
import psutil
import threading
import copy
from importlib import import_module

from flask import g
import job_manager
import job_config
from common import test_common
from tests.jobs.TestJobExecutor import TestExecuteStocker
from common_libs.common import const
from libs.sub_processes import SubProcesses
from libs.clean_up_info import CleanUpInfo

def test_job_manager_main_sigterm_signal():
    """job manager main の終了動作(sigterm signal)
    """
    sub_process_count = 2
    with mock.patch("job_config.SUB_PROCESS_ACCEPTABLE", sub_process_count):
        g.initialize()

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
                timeout=20.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=sub_process_count)

        finally:
            job_manager.job_manager_process_sigterm_handler(None, None)

            # sub processの終了確認
            assert test_common.check_state(
                timeout=20.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=0)

            # main processの終了確認
            assert not main_thread.is_alive()

            main_thread.join()


def test_job_manager_main_sigint_signal():
    """job manager main の終了動作(sigint → sigterm signal)
    """
    sub_process_count = 2
    with mock.patch("job_config.SUB_PROCESS_ACCEPTABLE", sub_process_count):
        g.initialize()

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
                timeout=20.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=sub_process_count)

            # sigint signalの送信
            job_manager.job_manager_process_sigint_handler(None, None)

            # sub processの終了確認
            assert test_common.check_state(
                timeout=20.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=0)

            # 終了しているか確認
            assert test_common.check_state(
                timeout=20.0, conditions=lambda : not main_thread.is_alive())

        finally:
            # sigterm signalの送信
            job_manager.job_manager_process_sigterm_handler(None, None)

            # main processの終了確認
            assert test_common.check_state(
                timeout=20.0, conditions=lambda : not main_thread.is_alive())

            main_thread.join()


def test_job_manager_sub_execute_normal_job():
    """JOB正常終了
    """
    testdata = import_module("tests.db.exports.testdata")

    TestExecuteStocker.initalize()

    # Jobの実行classを試験用に切り替え
    process_kind="menu_create"
    job_config_jobs = copy.deepcopy(job_config.JOB_CONFIG)
    job_config_jobs[process_kind]["timeout_seconds"] = 30
    job_config_jobs[process_kind]["module"] = "tests.jobs.TestJobExecutor"
    job_config_jobs[process_kind]["class"] = "TestNormalJobExecutor"
    job_config_jobs[process_kind]["max_job_per_process"] = 1

    with mock.patch.dict(f"job_config.JOB_CONFIG", job_config_jobs):
        g.initialize()

        sub_processes = SubProcesses()
        clean_up_info = CleanUpInfo()

        try:

            # sub processの起動
            sub_processes.add(job_manager.job_manager_sub_process, clean_up_info)

            # # executedに1件はいること
            # assert test_common.check_state(
            #     timeout=10.0, conditions=lambda : len(TestExecuteStocker.executed_queue) == 1)
            # # 実行したものがqueueに入れたものとおなじであること
            # assert test_common.equal_queue(queue_data[0], TestExecuteStocker.executed_queue[0])

        finally:
            # sub processの終了要求
            sub_processes.graceful_terminate()

            # # sub processの終了確認
            # assert test_common.check_state(
            #     timeout=3.0, conditions=lambda : not main_thread.is_alive())


