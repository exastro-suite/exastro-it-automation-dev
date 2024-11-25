import os
import ctypes
import datetime
import multiprocessing
import threading
import time
import random
import traceback

from flask import g
from common_libs.common.util import get_iso_datetime, arrange_stacktrace_format

import job_config as config
from libs.job_classes import JobClasses
from libs.job_exception import JobTeminate
from libs.sub_processes import SubProcesses
from libs.clean_up_info import CleanUpInfo

class CleanUpJob():
    def __init__(self, info: CleanUpInfo):
        self.__info = info
        self.__thread = None
        self.__thread_id = None

    def tick(self):
        if self.__thread is not None:
            if self.__thread.is_alive():
                self.__info.clean_up_time.value = (datetime.datetime.timestamp(
                    datetime.datetime.now() + datetime.timedelta(seconds=config.CLEANUP_INTERVAL_SECONDS)
                ))
                g.applogger.debug(f'change clean up execute time : start_time={datetime.datetime.fromtimestamp(self.__info.clean_up_time.value).isoformat()}')
            else:
                self.__thread.join()
                self.__thread = None

        elif os.getpid() == self.__info.clean_up_pid.value:
            if self.__info.clean_up_time.value <= datetime.datetime.timestamp(datetime.datetime.now()):
                self.__thread = threading.Thread(
                    name="CleanUpThread",
                    target=self.__clean_up,
                    daemon=True
                )
                self.__thread.start()

    def __clean_up(self):
        self.__thread_id = ctypes.c_long(threading.get_ident())
        g.initialize()
        for job_name in config.JOB_CONFIG.keys():
            try:
                (JobClasses.get_job_executor_class(job_name)).clean_up()
            except JobTeminate:
                g.applogger.info(f'clean up interrupted')
                raise
            except Exception:
                # エラーログを出力し処理継続する / Output error log and continue processing
                g.applogger.error("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(traceback.format_exc())))


    def terminate(self):
        if self.__thread is not None:
            while self.__thread.is_alive():
                # 終了するまでExceptionを送り続ける
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    self.__thread_id,
                    ctypes.py_object(JobTeminate))
                time.sleep(1)

            self.__thread.join()

    @classmethod
    def update_execute_pid(cls, info: CleanUpInfo, sub_processes: SubProcesses):
        if not sub_processes.is_acceptable(info.clean_up_pid.value):
            new_pid = sub_processes.get_longest_acceptable_pid()
            g.applogger.debug(f'change clean up execute process : {info.clean_up_pid.value} to {new_pid} / start_time={datetime.datetime.fromtimestamp(info.clean_up_time.value).isoformat()}')
            info.clean_up_pid.value = new_pid
