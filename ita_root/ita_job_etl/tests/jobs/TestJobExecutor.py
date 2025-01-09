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

import time
from flask import g
from jobs.base_job_executor import BaseJobExecutor
from libs.job_queue_row import JobQueueRow
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs


class TestExecuteStocker():
    update_queue_to_start_queue = []
    canceled_queue = []
    cancel_exited_queue = []
    call_force_update_status_count = 0

    @classmethod
    def initalize(cls):
        cls.update_queue_to_start_queue = []
        cls.executed_queue = []
        cls.canceled_queue = []
        cls.cancel_exited_queue = []
        cls.call_force_update_status_count = 0

    @classmethod
    def append_update_queue_to_start_queue(cls, queue):
        cls.update_queue_to_start_queue.append(queue)

    @classmethod
    def append_executed_queue(cls, queue):
        cls.executed_queue.append(queue)

    @classmethod
    def append_canceled_queue(cls, queue):
        cls.canceled_queue.append(queue)

    @classmethod
    def append_cancel_exited_queue(cls, queue):
        cls.cancel_exited_queue.append(queue)

    @classmethod
    def call_clean_up(cls):
        cls.call_clean_up_count += 1


class TestNormalJobExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestNormalJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        time.sleep(1.0)
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)
        time.sleep(1.0)
        return True

    def cancel(self, conn: DBConnectWs):
        try:
            g.applogger.debug("TestNormalJobExecutor.cancel")
            TestExecuteStocker.append_canceled_queue(self.queue)
            time.sleep(1.0)
            return True
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()


class TestTimeoutJobExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestTimeoutJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        time.sleep(1.0)
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestTimeoutJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)
        for i in range(30):
            time.sleep(1.0)
        return True

    def cancel(self, conn: DBConnectWs):
        try:
            g.applogger.debug("TestTimeoutJobExecutor.cancel")
            TestExecuteStocker.append_canceled_queue(self.queue)
            time.sleep(1.0)
            return True
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()


class TestCancelTimeoutJobExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestCancelTimeoutJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        time.sleep(1.0)
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestCancelTimeoutJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)
        for i in range(30):
            time.sleep(1.0)
        return True

    def cancel(self, conn: DBConnectWs):
        g.applogger.debug("TestCancelTimeoutJobExecutor.cancel")
        TestExecuteStocker.append_canceled_queue(self.queue)
        try:
            for i in range(30):
                time.sleep(1.0)
            return True
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()
