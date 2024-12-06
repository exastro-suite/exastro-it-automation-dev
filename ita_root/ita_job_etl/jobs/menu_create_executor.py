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
import traceback

from libs.job_queue_row import JobQueueRow
from jobs.base_job_executor import BaseJobExecutor
from libs.job_exception import JobTimeoutException, JobTeminate
from common_libs.common import const

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.dbconnect.dbconnect_ws import DBConnectWs
from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format
from libs.menu_create.backyard_main import backyard_main

import job_config as config

class MenuCreateExecutor(BaseJobExecutor):

    @classmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        """JOB queueの取得用SQL

        Args:
            conn (DBConnectCommon): DB conntction

        Returns:
            str: JOB queueの取得用SQL
        """
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
        """constructor

        Args:
            queue (JobQueueRow): job queue
            job_config (dict): job config
        """
        super().__init__(queue, job_config)
        self.__menu_create_row = None


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
            rows = conn.sql_execute("SELECT * FROM T_MENU_CREATE_HISTORY WHERE HISTORY_ID = %s FOR UPDATE NOWAIT", [queue.job_key])
            if len(rows) > 0 and rows[0]['STATUS_ID'] == const.MENU_CREATE_UNEXEC:
                # 作業対象のステータスを「実行中」に変更
                conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': queue.job_key, 'STATUS_ID': const.MENU_CREATE_EXEC, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                conn.db_transaction_end(True)
                self.__menu_create_row = rows[0]
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
            # パラメータシート作成機能実行
            result = backyard_main(conn, self.__menu_create_row)
            if result:
                conn.db_transaction_start()
                # 作業対象のステータスを「完了」に変更
                conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_COMP, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                conn.db_transaction_end(True)
            else:
                raise Exception

        except JobTimeoutException:
            conn.db_transaction_end(False)
            raise

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
            conn.db_transaction_end(True)
            raise

    def cancel(self, conn: DBConnectWs):
        """JOB cancel実行

        Args:
            conn (DBConnectCommon): DB connetion
        """
        try:
            conn.db_transaction_start()
            # 作業対象のステータスを「完了(異常)」に変更
            conn.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': self.queue.job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
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
            g.applogger.info("menu_create clean_up")
            for i in range(1, 10 + 1):
                g.applogger.debug(f"menu_create clean_up : {i}")
                time.sleep(1)

            # DB接続
            while True:
                # 接続に成功するまで繰り返し
                try:
                    conn = DBConnectCommon()
                    g.applogger.debug(f"sub process db reconnected")
                    break
                except Exception:
                    g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
                    time.sleep(config.EXCEPTION_RESTART_INTERVAL_SECONDS)

            # job_configからtimeout_secondsを取得
            timeout_seconds = config.JOB_CONFIG['menu_create']['timeout_seconds']

            # ステータスが「実行中」かつ最終更新日時にtimeout_secondsを加算した日時が現在時刻を超えているレコードが対象
            schemata = cls.get_view_schemata(conn, 'V_MENU_CREATE_HISTORY')
            query_stmt = ""
            union_stmt = ""
            for schema in schemata:
                query_stmt += (
                    union_stmt +
                    "SELECT ORGANIZATION_ID, WORKSPACE_ID, JOB_KEY, JOB_STATUS, LAST_UPDATE_TIMESTAMP, 'menu_create' AS JOB_NAME" +
                    f" FROM `{schema}`.V_MENU_CREATE_HISTORY" +
                    f" WHERE JOB_STATUS = '{str(const.MENU_CREATE_EXEC)}' AND LAST_UPDATE_TIMESTAMP + INTERVAL {timeout_seconds} SECOND < now()"
                )
                union_stmt = " UNION ALL "

            try:
                # conn.db_transaction_start()
                rows = conn.sql_execute(query_stmt)

                # DBConnectCommonを切断
                conn.db_disconnect()
                del conn

                for row in rows:
                    organization_id = row['ORGANIZATION_ID']
                    workspace_id = row['WORKSPACE_ID']
                    job_key = row['JOB_KEY']
                    conn_ws = DBConnectWs(workspace_id, organization_id)

                    conn_ws.db_transaction_start()
                    # 作業対象のステータスを「完了(異常)」に変更
                    conn_ws.table_update('T_MENU_CREATE_HISTORY',[{'HISTORY_ID': job_key, 'STATUS_ID': const.MENU_CREATE_ERR, 'LAST_UPDATE_USER': const.MENU_CREATE_USER_ID}], 'HISTORY_ID', is_register_history=True)
                    conn_ws.db_transaction_end(True)

                    # DBConnectCommonを切断
                    conn_ws.db_disconnect()
                    del conn_ws

            except Exception:
                g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
                conn.db_transaction_end(False)

        except JobTeminate:
            raise


# TEST-TABLE
"""
USE `ITA_WS_xxxxxxxxxxx`;

CREATE or REPLACE VIEW V_MENU_CREATE_HISTORY AS
SELECT 'org1'         AS  ORGANIZATION_ID,
       'workspace-1'  AS  WORKSPACE_ID,
        HISTORY_ID    AS  JOB_KEY,
        STATUS_ID     AS  JOB_STATUS,
        LAST_UPDATE_TIMESTAMP
FROM T_MENU_CREATE_HISTORY
WHERE STATUS_ID = '1' or STATUS_ID = '2';

GRANT SELECT ON TABLE V_MENU_CREATE_HISTORY TO ITA_USER;

"""
