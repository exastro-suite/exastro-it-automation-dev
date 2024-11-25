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
import threading
import ctypes
import abc
import datetime
import traceback

from flask import g

from libs.job_queue_row import JobQueueRow
from libs.job_exception import JobTimeoutException

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon
from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format


class BaseJobExecutor(metaclass=abc.ABCMeta):
    """JOBベースclass
    """

    @classmethod
    @abc.abstractmethod
    def queue_query_stmt(cls, conn: DBConnectCommon) -> str:
        """JOB queueの取得用SQL

        Args:
            conn (DBConnectCommon): DB conntction

        Raises:
            NotImplementedError: 継承先classで未実装

        Returns:
            str: JOB queueの取得用SQL
        """
        raise NotImplementedError()


    @classmethod
    def get_view_schemata(cls, conn: DBConnectCommon, view_name: str) -> list[str]:
        """指定view名のDatabase名取得

        Args:
            conn (DBConnectCommon): DB conntction
            view_name (str): view name

        Returns:
            list[str]: database name list
        """
        rows = conn.sql_execute("SELECT TABLE_SCHEMA FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = %s",[view_name])
        return [row["TABLE_SCHEMA"] for row in rows]


    def __init__(self, queue: JobQueueRow, job_config: dict):
        """コンストラクタ

        Args:
            queue (JobQueueRow): job queue
            job_config (dict): job config
        """
        self.queue = queue
        self.job_config = job_config
        self.__conn = self.db_connect(queue)
        self.__execute_start_time = None
        self.__execute_thread_id = None
        self.__cancel_start_time = None
        self.__cancel_thread_id = None


    def __del__(self):
        """デストラクタ
        """
        self.__conn.db_disconnect()

    @abc.abstractmethod
    def db_connect(self, queue: JobQueueRow) -> DBConnectCommon:
        """操作対象DBへの接続処理

        Args:
            queue (JobQueueRow): job queue

        Raises:
            NotImplementedError: 継承先classで未実装

        Returns:
            DBConnectCommon: DB connection
        """
        raise NotImplementedError()

    def call_update_queue_to_start(self) -> bool:
        """JOB起動確認呼出

        Returns:
            bool: True: 起動可 / False: 起動不可
        """
        return self.update_queue_to_start(self.queue, self.__conn)

    @abc.abstractmethod
    def update_queue_to_start(self, queue: JobQueueRow, conn: DBConnectCommon) -> bool:
        """JOB起動確認

        Args:
            queue (JobQueueRow): job queue
            conn (DBConnectCommon): DB connection

        Raises:
            NotImplementedError: 継承先classで未実装

        Returns:
            bool: True: 起動可 / False: 起動不可
        """
        raise NotImplementedError()

    def call_execute(self):
        """JOB実行呼出
        """
        g.initialize()
        g.ORGANIZATION_ID = self.queue.organization_id
        g.WORKSPACE_ID = self.queue.workspace_id

        self.__execute_start_time = datetime.datetime.now()
        self.__execute_thread_id = ctypes.c_long(threading.get_ident())

        try:
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10003")))
            self.execute(self.__conn)
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10004")))

        except JobTimeoutException:
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10006")))
        except Exception as ex:
            g.applogger.error(self.log_format(g.appmsg.get_log_message("JBM-10005")))
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))


    @abc.abstractmethod
    def execute(self, conn: DBConnectCommon):
        """JOB実行 / Job execute
            JobTimeoutExceptionを受信したときは即時に処理を中断すること
            Immediately interrupt processing when receiving JobTimeoutException

        Args:
            conn (DBConnectCommon): DB connetion

        Raises:
            NotImplementedError: 継承先classで未実装
        """
        raise NotImplementedError()

    def call_cancel(self):
        """JOB cancel実行呼出
        """
        g.initialize()
        g.ORGANIZATION_ID = self.queue.organization_id
        g.WORKSPACE_ID = self.queue.workspace_id

        self.__cancel_start_time = datetime.datetime.now()
        self.__cancel_thread_id = ctypes.c_long(threading.get_ident())
        conn = None
        try:
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10007")))
            conn = self.db_connect(self.queue)
            self.cancel(conn)
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10008")))
        except JobTimeoutException:
            g.applogger.info(self.log_format(g.appmsg.get_log_message("JBM-10010")))
        except Exception as ex:
            g.applogger.error(self.log_format(g.appmsg.get_log_message("JBM-10009")))
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
        finally:
            if conn is not None:
                conn.db_disconnect()

    @abc.abstractmethod
    def cancel(self, conn: DBConnectCommon):
        """JOB cancel実行
            JobTimeoutExceptionを受信したときは即時に処理を中断すること
            Immediately interrupt processing when receiving JobTimeoutException

        Args:
            conn (DBConnectCommon): DB connetion

        Raises:
            NotImplementedError: 継承先classで未実装
        """
        raise NotImplementedError()

    def send_execute_timeout_exception(self):
        """raise JobTimeoutException to JOB execution thread
        """
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            self.__execute_thread_id,
            ctypes.py_object(JobTimeoutException))

    def send_cancel_timeout_exception(self):
        """raise JobTimeoutException to JOB cancel thread
        """
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            self.__cancel_thread_id,
            ctypes.py_object(JobTimeoutException))

    def log_format(self, message) -> str:
        """JOB実行ログのformat

        Args:
            message (str): ログメッセージ

        Returns:
            str: 整形済みログメッセージ
        """
        logline = f'[JOB={self.queue.job_name}]'
        if self.queue.organization_id is not None:
            logline += f'[ORG={self.queue.organization_id}]'

        if self.queue.workspace_id is not None:
            logline += f'[WS={self.queue.workspace_id}]'

        logline += f'[KEY={self.queue.job_key}]'
        return f'{logline} {message}'

    @classmethod
    @abc.abstractmethod
    def clean_up(self):
        """clean up
            JOBが中断などで残ったゴミを掃除する処理を行います
            本処理は定期的に呼び出されます
            JobTeminate exeptionを受信したときは即時に処理を中断すること
            
            Performs processing to clean up trash left behind due to job interruptions, etc.
            This process is called periodically
            Immediately interrupt processing when receiving JobTeminate exeption
        Raises:
            NotImplementedError: 継承先classで未実装
        """
        raise NotImplementedError()
