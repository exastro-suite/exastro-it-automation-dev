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
from libs.job_exception import JobTimeoutException
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common import const


class TestExecuteStocker():
    call_queue_query_stmt_count = 0
    update_queue_to_start_queue = []
    executed_queue = []
    canceled_queue = []
    cancel_exited_queue = []
    call_clean_up_count = 0

    @classmethod
    def initalize(cls):
        cls.call_queue_query_stmt_count = 0
        cls.update_queue_to_start_queue = []
        cls.executed_queue = []
        cls.canceled_queue = []
        cls.cancel_exited_queue = []
        cls.call_clean_up_count = 0

    @classmethod
    def call_queue_query_stmt(cls):
        cls.call_queue_query_stmt_count += 1

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
        TestExecuteStocker.call_queue_query_stmt()
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        union_stmt = ""
        for schema in schemata:
            query_stmt += (
                union_stmt +
                "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, LAST_UPDATE_TIMESTAMP, 'menu_create' AS JOB_NAME" +
                f" FROM `{schema}`.V_MENU_CREATE_HISTORY"
            )
            union_stmt = " UNION ALL "
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestNormalJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        try:
            conn.db_transaction_start()
            rows = conn.sql_execute("SELECT * FROM T_MENU_CREATE_HISTORY WHERE HISTORY_ID = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and rows[0]['STATUS_ID'] == const.MENU_CREATE_UNEXEC:
                if self.exclusive_control() is False:
                    return False

                # 作業対象のステータスを「実行中」に変更
                conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': queue.job_key, 'STATUS_ID': const.MENU_CREATE_EXEC, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                conn.db_transaction_end(True)
                return True
            else:
                conn.db_transaction_end(False)
                return False
        except Exception as e:
            conn.db_transaction_end(False)
            return False
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)

        try:
            # パラメータシート作成機能実行
            conn.db_transaction_start()
            # 作業対象のステータスを「完了」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_COMP, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise


    def cancel(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.cancel")
        TestExecuteStocker.append_canceled_queue(self.queue)

        try:
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()


class TestExecuteTimeoutJobExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        TestExecuteStocker.call_queue_query_stmt()
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        union_stmt = ""
        for schema in schemata:
            query_stmt += (
                union_stmt +
                "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, LAST_UPDATE_TIMESTAMP, 'menu_create' AS JOB_NAME" +
                f" FROM `{schema}`.V_MENU_CREATE_HISTORY"
            )
            union_stmt = " UNION ALL "
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestNormalJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        try:
            conn.db_transaction_start()
            rows = conn.sql_execute("SELECT * FROM T_MENU_CREATE_HISTORY WHERE HISTORY_ID = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and rows[0]['STATUS_ID'] == const.MENU_CREATE_UNEXEC:
                if self.exclusive_control() is False:
                    return False

                # 作業対象のステータスを「実行中」に変更
                conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': queue.job_key, 'STATUS_ID': const.MENU_CREATE_EXEC, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                conn.db_transaction_end(True)
                return True
            else:
                conn.db_transaction_end(False)
                return False
        except Exception as e:
            conn.db_transaction_end(False)
            return False
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)

        try:
            for i in range(30):
                time.sleep(1.0)

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise


    def cancel(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.cancel")
        TestExecuteStocker.append_canceled_queue(self.queue)

        try:
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()


class TestCancelTimeoutJobExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        TestExecuteStocker.call_queue_query_stmt()
        schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
        query_stmt = ""
        union_stmt = ""
        for schema in schemata:
            query_stmt += (
                union_stmt +
                "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, LAST_UPDATE_TIMESTAMP, 'menu_create' AS JOB_NAME" +
                f" FROM `{schema}`.V_MENU_CREATE_HISTORY"
            )
            union_stmt = " UNION ALL "
        return query_stmt

    def __init__(self, queue: JobQueueRow, job_config: dict):
        super().__init__(queue, job_config)

    def db_connect(self, queue: JobQueueRow):
        return DBConnectWs(queue.workspace_id, queue.organization_id)

    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        g.applogger.debug("TestNormalJobExecutor.update_queue_to_start")
        TestExecuteStocker.append_update_queue_to_start_queue(self.queue)
        try:
            conn.db_transaction_start()
            rows = conn.sql_execute("SELECT * FROM T_MENU_CREATE_HISTORY WHERE HISTORY_ID = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and rows[0]['STATUS_ID'] == const.MENU_CREATE_UNEXEC:
                if self.exclusive_control() is False:
                    return False

                # 作業対象のステータスを「実行中」に変更
                conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': queue.job_key, 'STATUS_ID': const.MENU_CREATE_EXEC, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                conn.db_transaction_end(True)
                return True
            else:
                conn.db_transaction_end(False)
                return False
        except Exception as e:
            conn.db_transaction_end(False)
            return False
        return True

    def execute(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.execute")
        TestExecuteStocker.append_executed_queue(self.queue)

        try:
            for i in range(30):
                time.sleep(1.0)

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise


    def cancel(self, conn: DBConnectWs):
        g.applogger.debug("TestNormalJobExecutor.cancel")
        TestExecuteStocker.append_canceled_queue(self.queue)

        try:
            for i in range(30):
                time.sleep(1.0)

        except JobTimeoutException:
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_end(False)
            # 排他制御ロックを解除
            self.exclusive_control_commit()
            raise
        finally:
            TestExecuteStocker.append_cancel_exited_queue(self.queue)

    @classmethod
    def clean_up(cls):
        TestExecuteStocker.call_clean_up()

