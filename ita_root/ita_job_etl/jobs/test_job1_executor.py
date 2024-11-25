import time
from flask import g
import traceback

from libs.job_queue_row import JobQueueRow
from jobs.base_job_executor import BaseJobExecutor
from libs.job_exception import JobTimeoutException, JobTeminate

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format

class TestJob1Executor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        """JOB queueの取得用SQL

        Args:
            conn (DBConnectCommon): DB conntction

        Returns:
            str: JOB queueの取得用SQL
        """
        schemata = cls.get_view_schemata(conn, 'V_TEST_JOB1')
        query_stmt = ""
        union_stmt = ""
        for schema in schemata:
            query_stmt += (
                union_stmt +
                "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, LAST_UPDATE_TIMESTAMP, 'test_job1' AS JOB_NAME" +
                f" FROM `{schema}`.V_TEST_JOB1"
            )
            union_stmt = " UNION ALL "

        return query_stmt


    def __init__(self, queue: JobQueueRow, job_config: dict):
        """constructor

        Args:
            queue (JobQueueRow): job queue
            job_config (dict): job config
        """
        super().__init__(queue, job_config)
        self.__test_job1_row = None


    def db_connect(self, queue: JobQueueRow):
        """操作対象DBへの接続処理

        Args:
            queue (JobQueueRow): job queue

        Returns:
            DBConnectCommon: DB connection
        """
        return DBConnectWs(queue.workspace_id, queue.organization_id)


    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectWs) -> bool:
        """JOB起動確認

        Args:
            queue (JobQueueRow): job queue
            conn (DBConnectCommon): DB connection

        Returns:
            bool: True: 起動可 / False: 起動不可
        """
        try:
            conn.db_transaction_start()
            rows = conn.sql_execute("SELECT * FROM T_TEST_JOB1 WHERE DATA_KEY = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and  rows[0]['STATUS'] == 'NOT_PROCESSING':
                conn.table_update('T_TEST_JOB1',[{'DATA_KEY': queue.job_key, 'STATUS': 'EXECUTING'}], 'DATA_KEY', is_register_history=False)
                conn.db_transaction_end(True)
                self.__test_job1_row = rows[0]
                return True
            else:
                conn.db_transaction_end(False)
                return False
        except Exception:
            conn.db_transaction_end(False)
            return False


    def execute(self, conn: DBConnectWs):
        """JOB実行

        Args:
            conn (DBConnectCommon): DB connetion
        """
        try:
            g.JOB_KEY = self.queue.job_key

            if self.__test_job1_row['WAIT_SECONDS'] < 1:
                raise Exception('WAIT_SECONDS ERROR')

            for i in range(1, self.__test_job1_row['WAIT_SECONDS'] + 1):
                g.applogger.debug(self.log_format(f'TEST_JOB1 PROCESSING:{i}'))
                g.applogger.debug(self.log_format(f'{self.queue.organization_id=} {g.get("ORGANIZATION_ID")=}'))
                g.applogger.debug(self.log_format(f'{self.queue.workspace_id=} {g.get("WORKSPACE_ID")=}'))
                g.applogger.debug(self.log_format(f'{self.queue.job_key=} {g.get("JOB_KEY")=}'))
                time.sleep(1)

            conn.db_transaction_start()
            conn.table_update('T_TEST_JOB1',[{'DATA_KEY': self.queue.job_key, 'STATUS': 'SUCCEED'}], 'DATA_KEY', is_register_history=False)
            conn.db_transaction_end(True)

        except JobTimeoutException:
            conn.db_transaction_end(False)
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.table_update('T_TEST_JOB1',[{'DATA_KEY': self.queue.job_key, 'STATUS': 'FAILED'}], 'DATA_KEY', is_register_history=False)
            conn.db_transaction_end(False)
            raise

    def cancel(self, conn: DBConnectWs):
        """JOB cancel実行

        Args:
            conn (DBConnectCommon): DB connetion
        """
        try:
            conn.db_transaction_start()
            conn.table_update('T_TEST_JOB1',[{'DATA_KEY': self.queue.job_key, 'STATUS': 'TIMEOUT'}], 'DATA_KEY', is_register_history=False)
            conn.db_transaction_end(True)

            g.applogger.debug(self.log_format(f'TEST_JOB1 PROCESSING'))
            g.applogger.debug(self.log_format(f'{self.queue.organization_id=} {g.get("ORGANIZATION_ID")=}'))
            g.applogger.debug(self.log_format(f'{self.queue.workspace_id=} {g.get("WORKSPACE_ID")=}'))

        except JobTimeoutException:
            conn.db_transaction_end(False)
            raise
        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_end(False)
            raise

    @classmethod
    def clean_up(cls):
        """実行中のままで残ってしまったJOBステータスのゴミ掃除処理
        """
        try:
            g.applogger.info("test_job1 clean_up")
            for i in range(1, 10 + 1):
                g.applogger.debug(f"test_job1 clean_up : {i}")
                time.sleep(1)

        except JobTeminate:
            raise


# TEST-TABLE
"""
use `WS_DB`;

DROP TABLE if exists T_TEST_JOB1;

CREATE TABLE T_TEST_JOB1
(
    DATA_KEY VARCHAR(36),
    STATUS VARCHAR(16),
    WAIT_SECONDS INT,
    LAST_UPDATE_TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(DATA_KEY)
);


CREATE or REPLACE VIEW V_TEST_JOB1 AS
SELECT  'org1'  AS  ORGANIZATION_ID,
        'ws1'   AS  WORKSPACE_ID,
        DATA_KEY    AS  JOB_KEY,
        LAST_UPDATE_TIMESTAMP
    FROM T_TEST_JOB1
    WHERE   STATUS  =   'NOT_PROCESSING';

GRANT SELECT ON TABLE V_TEST_JOB1 TO ITA_USER;

"""
