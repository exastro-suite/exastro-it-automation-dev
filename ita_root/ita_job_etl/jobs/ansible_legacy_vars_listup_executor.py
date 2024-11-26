import time
import datetime
from flask import g
import traceback

from libs.job_queue_row import JobQueueRow
from jobs.base_job_executor import BaseJobExecutor
from libs.job_exception import JobTimeoutException, JobTeminate
from common_libs.common import const

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format
from libs.ansible_legacy_vars_listup.backyard_main import backyard_main

# import job_config as config

class AnsibleLegacyVarsListupExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        """JOB queueの取得用SQL

        Args:
            conn (DBConnectCommon): DB conntction

        Returns:
            str: JOB queueの取得用SQL
        """
        schemata = cls.get_view_schemata(conn, 'V_COMN_PROC_LOADED_LIST')
        query_stmt = ""
        union_stmt = ""
        for schema in schemata:
            query_stmt += (
                union_stmt +
                "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, LAST_UPDATE_TIMESTAMP, 'ansible_legacy_vars_listup' AS JOB_NAME" +
                f" FROM `{schema}`.V_COMN_PROC_LOADED_LIST" +
                f" WHERE JOB_KEY = {const.PROC_LOADED_ID_ANSIBLE_LEGACY}"
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
            rows = conn.sql_execute("SELECT * FROM T_COMN_PROC_LOADED_LIST WHERE ROW_ID = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and str(rows[0]['LOADED_FLG']) == '0':
                conn.table_update('T_COMN_PROC_LOADED_LIST',[{'ROW_ID': self.queue.job_key, 'LOADED_FLG': '1'}], 'ROW_ID', is_register_history=False)
                conn.db_transaction_end(True)
                return True
            else:
                conn.db_transaction_end(False)
                return False
        except Exception as e:
            conn.db_transaction_end(False)
            return False


    def execute(self, conn: DBConnectWs):
        """JOB実行

        Args:
            conn (DBConnectCommon): DB connetion
        """
        try:
            # メイン機能実行
            backyard_main(conn)

        except JobTimeoutException:
            conn.db_transaction_end(False)
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_start()
            # LOADED_FLGを0にして再度実行されるように
            conn.table_update('T_COMN_PROC_LOADED_LIST',[{'ROW_ID': self.queue.job_key, 'LOADED_FLG': '0'}], 'ROW_ID', is_register_history=False)
            conn.db_transaction_end(True)
            raise

    def cancel(self, conn: DBConnectWs):
        """JOB cancel実行

        Args:
            conn (DBConnectCommon): DB connetion
        """
        try:
            # LOADED_FLGを0にして再度実行されるように
            conn.db_transaction_start()
            conn.table_update('T_COMN_PROC_LOADED_LIST',[{'ROW_ID': self.queue.job_key, 'LOADED_FLG': '0'}], 'ROW_ID', is_register_history=False)
            conn.db_transaction_end(True)

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
            g.applogger.info("ansible legacy vars listup clean_up")
            for i in range(1, 10 + 1):
                g.applogger.debug(f"ansible legacy vars listup clean_up : {i}")
                time.sleep(1)

        except JobTeminate:
            raise


# TEST-VIEW
"""
USE `ITA_WS_xxxxxxxxxxx`;

CREATE or REPLACE VIEW V_COMN_PROC_LOADED_LIST AS
SELECT 'org1'         AS  ORGANIZATION_ID,
       'workspace-1'  AS  WORKSPACE_ID,
        ROW_ID        AS  JOB_KEY,
        LOADED_FLG,
        LAST_UPDATE_TIMESTAMP
FROM T_COMN_PROC_LOADED_LIST
WHERE LOADED_FLG = '0';

GRANT SELECT ON TABLE V_COMN_PROC_LOADED_LIST TO ITA_USER;

"""
