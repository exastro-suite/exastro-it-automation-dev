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
import ctypes
import datetime
import threading
import time
import traceback

from flask import g
from common_libs.common.util import get_iso_datetime, arrange_stacktrace_format

import job_config as config

from libs.job_classes import JobClasses
from libs.job_exception import JobTeminate
from libs.sub_processes import SubProcesses
from libs.clean_up_info import CleanUpInfo

class CleanUpJob():
    """JOBのclean upを行う処理を定期的に起動する / Periodically start the process to clean up the JOB
    """

    def __init__(self, info: CleanUpInfo):
        """constructor

        Args:
            info (CleanUpInfo): clean upの起動を制御する共有メモリ / Shared memory that controls clean up startup
        """
        self.__info = info
        self.__thread = None
        self.__thread_id = None

    def tick(self):
        if self.__thread is not None:
            if self.__thread.is_alive():
                # clean upのThreadが実行中のとき / When the clean up Thread is running

                # 次回のclean upの起動開始時間を現在時刻から起動間隔秒後に設定する
                # Set the startup start time of the next clean up to be a startup interval seconds from the current time.
                self.__info.clean_up_time.value = (datetime.datetime.timestamp(
                    datetime.datetime.now() + datetime.timedelta(seconds=config.CLEANUP_INTERVAL_SECONDS)
                ))
            else:
                # clean upのThreadが完了したとき / When the clean up Thread completes

                self.__thread.join()
                self.__thread = None
                g.applogger.debug(f'next clean up execute time : start_time={datetime.datetime.fromtimestamp(self.__info.clean_up_time.value).isoformat()}')

        elif os.getpid() == self.__info.clean_up_pid.value:
            # 複数のsub processの中で、clean_up_pidのprocess idと合致するsub processがclean upを起動するprocessである
            # 自身のprocess idとclean_up_pidのprocess idを比較し、自身のprocessがclean upを起動するprocessかを判定
            # Among multiple sub processes, the sub process that matches the process id of clean_up_pid is the process that starts clean up
            # Compare own process id and clean_up_pid's process id to determine whether own process is the process that starts clean up


            if self.__info.clean_up_time.value <= datetime.datetime.timestamp(datetime.datetime.now()):
                # clean upの起動予定時間になったとき / When the scheduled start time for clean up is reached

                # clean upのThreadを起動する / Start clean up Thread
                self.__thread = threading.Thread(
                    name="CleanUpThread",
                    target=self.__clean_up,
                    daemon=True
                )
                self.__thread.start()

    def __clean_up(self):
        """clean upの処理 / clean up process
        """

        # 中断の処理用にThread idを保持する / Preserve Thread id for handling interruptions
        self.__thread_id = ctypes.c_long(threading.get_ident())

        # 初期化処理 / Initialization process
        g.initialize()

        g.applogger.info(g.appmsg.get_log_message("JBM-10012", []))

        # 全JOB classのclean upメソッドを順次呼び出す
        # Call the clean up method of all JOB classes sequentially
        for job_name in config.JOB_CONFIG.keys():
            try:
                g.applogger.debug(f'Call {job_name}.clean_up')
                (JobClasses.get_job_executor_class(job_name)).clean_up()
            except JobTeminate:
                # clean upの途中でsub processが終了するタイミングとなった場合に中断する
                # Interrupt when the sub process ends during clean up
                g.applogger.info(g.appmsg.get_log_message("JBM-10013", []))
                break
            except Exception:
                # エラーログを出力し処理継続する / Output error log and continue processing
                g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))

        g.applogger.info(g.appmsg.get_log_message("JBM-10014", []))


    def terminate(self):
        """terminate clean up
            sub process終了時に呼び出し、clean up処理を中断する
            Call when sub process ends to interrupt clean up processing
        """
        if self.__thread is not None:
            # Clean upのThreadが実行中のとき / When the Clean up Thread is running

            while self.__thread.is_alive():
                # clean upのThreadが終了するまでJobTeminate Exceptionを送り続ける
                # Keep sending JobTeminate Exception until the clean up Thread finishes
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    self.__thread_id,
                    ctypes.py_object(JobTeminate))
                time.sleep(1)

            # Threadが終了したらjoinする / Join when Thread finishes
            self.__thread.join()


    @classmethod
    def update_execute_pid(cls, info: CleanUpInfo, sub_processes: SubProcesses):
        """clean upするsub processのprocess idを更新する / Update the process id of the sub process to clean up

        Args:
            info (CleanUpInfo): _description_
            sub_processes (SubProcesses): _description_
        """
        if not sub_processes.is_acceptable(info.clean_up_pid.value):
            # 現在clean upを行うsub processがJOBを受け入れ可能でないとき（sub processが終了処理を開始している状態のとき）
            # When the sub process currently performing clean up is not able to accept JOB (when the sub process has started termination processing)

            # 現在動作中のsub processの中で一番長い間JOBを受け入れる予定のProcess idを、次にclean upを行うsub processに割り当てる
            # Assign the Process ID that is scheduled to accept JOB for the longest time among the currently running sub processes to the sub process that will be cleaned up next.
            new_pid = sub_processes.get_longest_acceptable_pid()

            g.applogger.debug(f'change clean up execute process : {info.clean_up_pid.value} to {new_pid} / start_time={datetime.datetime.fromtimestamp(info.clean_up_time.value).isoformat()}')
            info.clean_up_pid.value = new_pid
