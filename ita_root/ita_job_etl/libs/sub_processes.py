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
import ctypes
import datetime
import multiprocessing
from collections.abc import Callable

from flask import g

import job_config as config
from libs.sub_process import SubProcess, SubProcessStatus
from libs.clean_up_info import CleanUpInfo


class SubProcesses():

    def __init__(self):
        self.__sub_processes: list[SubProcess] = []

    def add(self, job_manager_sub_process: Callable, clean_up_info: CleanUpInfo):
        self.__sub_processes = [sub_process for sub_process in self.__sub_processes if sub_process.get_status() != SubProcessStatus.EXITED]

        for sub_process in self.__sub_processes:
            if sub_process.get_terminating_time() + datetime.timedelta(seconds=config.SUB_PROCESS_ACCEPTABLE_SECONDS) <= datetime.datetime.now():
                g.applogger.debug(f'Kill sub process: {sub_process.get_pid()}')
                sub_process.kill()

        sub_process = SubProcess(job_manager_sub_process, self.__get_next_terminating_time(), clean_up_info)
        self.__sub_processes.append(sub_process)

    def graceful_terminate(self):
        for process in self.__sub_processes:
            if process.get_status() != SubProcessStatus.EXITED:
                process.graceful_terminate()

        for process in self.__sub_processes:
            if process.get_status() != SubProcessStatus.EXITED:
                process.join()

    def immediately_terminate(self):
        for sub_process in self.__sub_processes:
            if sub_process.get_status() != SubProcessStatus.EXITED:
                sub_process.immediately_terminate()

            if sub_process.get_status() != SubProcessStatus.EXITED:
                sub_process.join()

    def count_acceptable(self) -> int:
        count = 0
        for sub_process in self.__sub_processes:
            if sub_process.get_status() == SubProcessStatus.ACCEPTABLE:
                count += 1

        return count

    def __get_next_terminating_time(self) -> datetime.datetime:
        count_acceptable = self.count_acceptable()
        if config.SUB_PROCESS_ACCEPTABLE > count_acceptable:
            return datetime.datetime.now() + datetime.timedelta(seconds=int(config.SUB_PROCESS_ACCEPTABLE_SECONDS / (config.SUB_PROCESS_ACCEPTABLE - count_acceptable)))
        else:
            return datetime.datetime.now() + datetime.timedelta(seconds=config.SUB_PROCESS_ACCEPTABLE_SECONDS)

    def is_acceptable(self, pid: int):
        for sub_process in self.__sub_processes:
            if sub_process.get_pid() == pid:
                if sub_process.get_status() == SubProcessStatus.ACCEPTABLE:
                    return True
                else:
                    return False
        return False

    def get_longest_acceptable_pid(self) -> int:
        max_terminating_time = datetime.datetime.min
        longest_acceptable_pid = None

        for sub_process in self.__sub_processes:
            if sub_process.get_status() == SubProcessStatus.ACCEPTABLE and sub_process.get_terminating_time() > max_terminating_time:
                longest_acceptable_pid = sub_process.get_pid()
                max_terminating_time = sub_process.get_terminating_time()

        return longest_acceptable_pid
