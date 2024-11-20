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
import datetime
from collections.abc import Callable

from flask import g

import job_config as config
from libs.sub_process import SubProcess, SubProcessStatus
from libs.clean_up_info import CleanUpInfo


class SubProcesses():
    """sub processの管理class / sub process management class
    """

    def __init__(self):
        """constructor
        """
        self.__sub_processes: list[SubProcess] = []


    def add(self, job_manager_sub_process: Callable, clean_up_info: CleanUpInfo):
        """sub processの追加 / Add sub process

        Args:
            job_manager_sub_process (Callable): sub process main method
            clean_up_info (CleanUpInfo): clean up job制御クラスのインスタンス(共有メモリ)  / Instance of clean up job control class (shared memory)
        """
        # 終了したsub processの情報を削除する / Delete information about terminated sub processes
        self.__sub_processes = [sub_process for sub_process in self.__sub_processes if sub_process.get_status() != SubProcessStatus.EXITED]

        for sub_process in self.__sub_processes:
            if sub_process.get_terminating_time() + datetime.timedelta(seconds=config.SUB_PROCESS_ACCEPTABLE_SECONDS) <= datetime.datetime.now():
                # JOBの受付を終了して、終了すべきはずのsub processが一定時間(SUB_PROCESS_ACCEPTABLE_SECONDS)終了しなかった時にprocessをkillする
                # Finish accepting the JOB and kill the process when the sub process that should have finished does not finish for a certain period of time (SUB_PROCESS_ACCEPTABLE_SECONDS)
                g.applogger.debug(f'Kill sub process: {sub_process.get_pid()}')
                sub_process.kill()

        # sub processを起動しリストに追加する
        # Start sub process and add to list
        sub_process = SubProcess(job_manager_sub_process, self.__get_next_terminating_time(), clean_up_info)
        self.__sub_processes.append(sub_process)


    def graceful_terminate(self):
        """ sub processを正常に終了させる(JOBを完遂して終了する) / End the sub process normally (complete the JOB and end)
        """
        # 終了していないsub processに正常終了することを伝達する
        # Communicate normal termination to sub processes that have not terminated
        for process in self.__sub_processes:
            if process.get_status() != SubProcessStatus.EXITED:
                process.graceful_terminate()

        # sub processが終了するのを待つ
        # wait for sub process to finish
        for process in self.__sub_processes:
            if process.get_status() != SubProcessStatus.EXITED:
                process.join()

    def immediately_terminate(self):
        """ sub processを即時に終了させる / Immediately terminate sub process
        """
        # 終了していないsub processに即時に終了することを依頼する
        # Request an unterminated sub process to terminate immediately
        for sub_process in self.__sub_processes:
            if sub_process.get_status() != SubProcessStatus.EXITED:
                sub_process.immediately_terminate()

        # sub processが終了するのを待つ
        # wait for sub process to finish
        for sub_process in self.__sub_processes:
            if sub_process.get_status() != SubProcessStatus.EXITED:
                sub_process.join()


    def count_acceptable(self) -> int:
        """JOBの受け入れ可能なsub processの件数を返す / Returns the number of acceptable sub processes for JOB

        Returns:
            int: number of acceptable sub processes
        """
        count = 0
        for sub_process in self.__sub_processes:
            if sub_process.get_status() == SubProcessStatus.ACCEPTABLE:
                count += 1

        return count


    def __get_next_terminating_time(self) -> datetime.datetime:
        """次のsub processの終了時刻を返す / Returns the end time of the next sub process

        Returns:
            datetime.datetime: sub process terminating time
        """
        # sub processを同時に起動する件数に応じて、sub processの終了時間が同時に訪れないようにずらした終了時間を返す
        # Depending on the number of sub processes that are started at the same time, return the end time of the sub processes so that they do not arrive at the same time.
        count_acceptable = self.count_acceptable()
        if config.SUB_PROCESS_ACCEPTABLE > count_acceptable:
            return datetime.datetime.now() + datetime.timedelta(seconds=int(config.SUB_PROCESS_ACCEPTABLE_SECONDS / (config.SUB_PROCESS_ACCEPTABLE - count_acceptable)))
        else:
            return datetime.datetime.now() + datetime.timedelta(seconds=config.SUB_PROCESS_ACCEPTABLE_SECONDS)


    def is_acceptable(self, pid: int) -> bool:
        """JOBを受け入れ可能なsub processであるかを返す / Returns whether the JOB is a sub process that can accept it.

        Args:
            pid (int): process id

        Returns:
            bool: True: Acceptable / False: Not acceptable
        """
        for sub_process in self.__sub_processes:
            if sub_process.get_pid() == pid:
                if sub_process.get_status() == SubProcessStatus.ACCEPTABLE:
                    return True
                else:
                    return False
        return False


    def get_longest_acceptable_pid(self) -> int:
        """一番長い間JOBの受け入れ可能なsub processを返します / Returns the longest acceptable sub process of the JOB

        Returns:
            int: process id
        """
        max_terminating_time = datetime.datetime.min
        longest_acceptable_pid = None

        for sub_process in self.__sub_processes:
            if sub_process.get_status() == SubProcessStatus.ACCEPTABLE and sub_process.get_terminating_time() > max_terminating_time:
                longest_acceptable_pid = sub_process.get_pid()
                max_terminating_time = sub_process.get_terminating_time()

        return longest_acceptable_pid
