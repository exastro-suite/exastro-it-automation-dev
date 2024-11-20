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
import time
import datetime
# import sys
# import typing
# import multiprocessing
# from multiprocessing.sharedctypes import Synchronized
import signal
# import threading
import traceback
# import itertools
import random
# import ulid
# import os
# from contextlib import closing
# from importlib import import_module
# import pymysql.err

# from libs.job_logger import job_logger as logger
from libs.sub_processes import SubProcesses
# from libs.sub_process import SubProcess
from flask import g

from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format
from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon

import job_config as config
from libs.job_threads import JobThreads
from libs.job_thread import JobThread
from libs.job_queue import JubQueue
from libs.clean_up_job import CleanUpJob
from libs.clean_up_info import CleanUpInfo
from libs.interval_timer import IntervalTimer

# 終了指示のシグナル受信
process_terminate = False   # SIGTERM or SIGINT signal
process_sigterm = False     # SIGTERM signal (Jobを中断して終了する / Interrupt and end the job)
process_sigint = False      # SIGINT signal (Jobをやり終えて停止する / Finish the job and stop)


def job_manager_main_process():
    """main process
    """
    global process_terminate
    global process_sigterm
    global process_sigint

    # シグナルのハンドライベント設定 / Signal handler event settings
    signal.signal(signal.SIGTERM, job_manager_process_sigterm_handler)
    signal.signal(signal.SIGINT, job_manager_process_sigint_handler)

    # 初期化 / Initialize
    random.seed()
    g.initialize(is_main_process=True)

    # 開始メッセージ / Start message
    g.applogger.info(g.appmsg.get_log_message("BKY-00001", []))

    # sub_processesのインスタンス化 / Instance generation of sub_processes
    sub_processes = SubProcesses()
    # clean upの制御情報（共有メモリ）のインスタンス化 / Instance generation of clean up control information (shared memory)
    clean_up_info = CleanUpInfo()

    # シグナル受信までループ / Loop until signal reception
    while not process_terminate:
        try:
            # sub processを閾値まで起動する / Start sub process up to threshold
            for i in range(config.SUB_PROCESS_ACCEPTABLE - sub_processes.count_acceptable()):
                sub_processes.add(job_manager_sub_process, clean_up_info)

            # clean upを行うsub processのpidを更新する
            # * clean upは、main processの本処理で指名したsub processで実施する
            #
            # Update the pid of the sub process that performs clean up
            # * Clean up is executed in the sub process specified in the main process.
            CleanUpJob.update_execute_pid(clean_up_info, sub_processes)

        except Exception as ex:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            time.sleep(config.EXCEPTION_RESTART_INTERVAL_SECONDS)

        time.sleep(config.SUB_PROCESS_WATCH_INTERVAL_SECONDS)

    # 終了処理 / End processing
    g.applogger.info(g.appmsg.get_log_message("JBM-10002", []))

    if process_sigterm:
        # SIGTERMシグナル受信時
        # * 作業中のJOBを中断してsub processを終了する
        #
        # When receiving SIGTERM signal
        # * Interrupt the current JOB and end the sub process
        sub_processes.immediately_terminate()

    if process_sigint:
        # SIGINTシグナル受信時
        # * 作業中のJOBを完遂してsub processを終了する
        #
        # When receiving SIGINT signal
        # * Complete the current JOB and end the sub process
        sub_processes.graceful_terminate()

    # 終了メッセージ / Termination message
    g.applogger.info(g.appmsg.get_log_message("BKY-00002", []))
    g.terminate()
    return


def job_manager_sub_process(teminating_time: datetime.datetime, clean_up_info: CleanUpInfo):
    """sub process

    Args:
        teminating_time (datetime.datetime): 終了処理開始時間
        clean_up_info (CleanUpInfo): clean upの制御情報（共有メモリ）
    """
    global process_terminate
    global process_sigterm
    global process_sigint

    # シグナルのハンドライベント設定 / Signal handler event settings
    signal.signal(signal.SIGTERM, job_manager_process_sigterm_handler)
    signal.signal(signal.SIGINT, job_manager_process_sigint_handler)

    # 初期化 / initialize
    random.seed()
    g.initialize(is_main_process=False)

    # 開始メッセージ / Start message
    g.applogger.info(g.appmsg.get_log_message("BKY-20001", []))
    g.applogger.debug(f"sub process terminating time: {teminating_time.isoformat()}")

    # JOBスレッド管理用のclassのインスタンス化 / Generate a class instance for JOB thread management
    job_threads = JobThreads()

    # ita-userへのDBの接続 / Connecting DB to ita-user
    conn = None
    # DB接続のインターバル管理用 / For DB connection interval management
    reconnect_interval = IntervalTimer(config.SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS)
    # queue監視のインターバル管理用 / For interval management of queue monitoring
    queue_watch_interval = IntervalTimer(config.QUEUE_WATCH_INTERVAL_SECONDS)
    # メンテナンスモードチェックインターバル管理用 / For maintenance mode check interval management
    maintenance_mode_check_interval = IntervalTimer(config.MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS)
    # メンテナンスモード / maintenance mode
    maintenance_mode = None

    # clean up job制御クラスのインスタンス化 / Instantiate clean up job control class
    clean_up_job = CleanUpJob(clean_up_info)

    while True:
        if process_sigterm:
            # SIGTERMシグナルを受信した際は、実行中の全てのJOBをCANCELしループを抜ける
            # When receiving the SIGTERM signal, CANCEL all running JOBs and exit the loop.
            job_threads.cancel_all()
            break

        if process_sigint or teminating_time <= datetime.datetime.now():
            if job_threads.count_all_jobs() <= 0:
                # SIGINTシグナルまたは終了予定時刻を過ぎて、実行中のJOBが全て終了したらループを抜ける
                # Exit the loop when the SIGINT signal or the scheduled end time has passed and all running JOBs have finished
                break

        try:
            if conn is None or reconnect_interval.is_passed():
                # 一定間隔でDB再接続 / Reconnect DB at regular intervals
                conn = db_connect(conn)

            # JOBの状態の最新化 / Update JOB status
            job_threads.tick()

            if maintenance_mode is None or maintenance_mode_check_interval.is_passed():
                # 一定時間毎にmaintenance_modeの状態を更新する
                priv_maintenance_mode = maintenance_mode if maintenance_mode is not None else {'data_update_stop': 0, 'backyard_execute_stop': 0}
                maintenance_mode = get_maintenance_mode_setting()

                if (str(priv_maintenance_mode['data_update_stop']) != "1" and str(maintenance_mode['data_update_stop']) == "1") or str(priv_maintenance_mode['backyard_execute_stop']) != "1" and str(maintenance_mode['backyard_execute_stop']) == "1":
                    # メンテナンスモード時へ切り替え時
                    g.applogger.info(g.appmsg.get_log_message("BKY-00005", []))

            if str(maintenance_mode['data_update_stop']) != "1" and str(maintenance_mode['backyard_execute_stop']) != "1" and queue_watch_interval.is_passed():
                # メンテナンスモード中ではなく、queueの取得インターバルになった時
                # When the queue acquisition interval is reached instead of in maintenance mode

                if job_threads.count_all_jobs() < config.MAX_JOB_PER_PROCESS:
                    # JOB実行数が上限に達していない時
                    # When the number of JOB executions has not reached the upper limit

                    # 開始可能なJOBの一覧を取得する
                    # Get a list of jobs that can be started
                    startable_jobs = job_threads.get_startable_job_name_list()

                    # job queueのデータを取得
                    # Get job queue data
                    job_queue = JubQueue.query_queue(conn, startable_jobs)
                    g.applogger.debug(f'get queue : {len(job_queue)=} / {job_threads.count_all_jobs()=}')

                    while len(job_queue) > 0 and job_threads.count_all_jobs() < config.MAX_JOB_PER_PROCESS:
                        # queueが残っているかつ、JOB実行数が上限に達していない間繰り返し
                        # Repeat as long as the queue remains and the number of JOB executions has not reached the upper limit.

                        # 一番優先度の高いjobを取得 / Get the highest priority job
                        job_queue_row = JubQueue.pop(job_queue, job_threads)

                        # 処理対象が見つからない場合はループを抜ける
                        # If the processing target is not found, exit the loop
                        if job_queue_row is None:
                            break

                        # JobThreadをインスタンス化 / Instantiate JobThread
                        job_thread = JobThread(job_queue_row)

                        # JOBが他のsub processで既に実行中で無いかをチェックし、未実行ならばJOBを起動する
                        # Check whether the JOB is already running in another sub process, and if it is not running, start the JOB
                        update_result = job_thread.update_queue_to_start()
                        if update_result:
                            job_threads.start_job(job_thread)

            if str(maintenance_mode['data_update_stop']) != "1":
                # clean up jobの処理をコール
                # Call the clean up job process
                clean_up_job.tick()

        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            time.sleep(config.EXCEPTION_RESTART_INTERVAL_SECONDS)
            # DBの再接続 / DB reconnection
            conn = db_connect(conn)

        time.sleep(config.SUB_PROCESS_WATCH_INTERVAL_SECONDS)

    # clean upの処理を終了する / Finish the clean up process
    clean_up_job.terminate()

    # job threadの終了を待つ（終わってないものはthreadにtimeout exceptionを送り続ける）
    # Wait for the job thread to finish (if it is not finished, keep sending a timeout exception to the thread)
    job_threads.terminate()

    g.applogger.info(g.appmsg.get_log_message("BKY-20002", []))
    g.terminate()
    return


def db_connect(conn:DBConnectCommon = None) -> DBConnectCommon:
    """DB再接続処理

    Args:
        conn (DBConnectCommon, optional): _description_. Defaults to None.

    Returns:
        DBConnectCommon: _description_
    """
    if conn is not None:
        # 既存の接続を切断 / Disconnect existing connection
        conn.db_disconnect()
        del conn

    while True:
        # 接続に成功するまで繰り返し / Repeat until connection is successful
        try:
            new_conn = DBConnectCommon()
            g.applogger.debug(f"sub process db reconnected")
            return new_conn
        except Exception:
            g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))
            time.sleep(config.EXCEPTION_RESTART_INTERVAL_SECONDS)


def job_manager_process_sigterm_handler(signum, frame):
    """processへの終了指示（SIGTERMシグナル受信） / Termination instruction to process (sigterm signal reception)

    Args:
        signum (_type_): signal handler parameter
        frame (_type_): signal handler parameter
    """
    global process_terminate
    global process_sigterm
    process_terminate = True
    process_sigterm = True
    g.applogger.info(g.appmsg.get_log_message("JBM-10001", ["SIGTERM"]))


def job_manager_process_sigint_handler(signum, frame):
    """processへの終了指示（SIGINTシグナル受信） / Termination instruction to process (sigint signal reception)

    Args:
        signum (_type_): signal handler parameter
        frame (_type_): signal handler parameter
    """
    global process_terminate
    global process_sigint
    process_terminate = True
    process_sigint = True
    g.applogger.info(g.appmsg.get_log_message("JBM-10001", ["SIGINT"]))


if __name__ == '__main__':
    # main processの起動 / Starting the main process
    job_manager_main_process()
