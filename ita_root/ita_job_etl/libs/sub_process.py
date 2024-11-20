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
import signal
import datetime
import multiprocessing
from multiprocessing.sharedctypes import Value
from enum import Enum, auto
from collections.abc import Callable

from libs.clean_up_info import CleanUpInfo


class SubProcessStatus(Enum):
    """sub process status
    """
    
    ACCEPTABLE = auto()
    """JOBを受け入れ可能な状態 / Ready to accept JOB
    """

    TERMINATING = auto()
    """終了中 / Terminating
    """

    EXITED = auto()
    """終了済み / exited
    """


class SubProcess():
    """sub process
    """
    def __init__(
        self,
        job_manager_sub_process: Callable,
        teminating_time: datetime.datetime,
        clean_up_info: CleanUpInfo
    ):
        """ constructor

        Args:
            job_manager_sub_process (Callable): sub process main method
            teminating_time (datetime.datetime): sub process terminating time
            clean_up_info (CleanUpInfo): clean up job制御クラスのインスタンス(共有メモリ)  / Instance of clean up job control class (shared memory)
        """
        # インスタンス変数初期化 / instance variable initialization
        self.__start_time = datetime.datetime.now()
        self.__teminating_time = teminating_time
        self.__process = multiprocessing.Process(
            target=job_manager_sub_process,
            args=(teminating_time, clean_up_info))
        self.__process.start()
        self.__terminating = False


    def __del__(self):
        """ destructor
        """
        self.__process.close()
        del self.__process
        self.__process = None


    def graceful_terminate(self):
        """ sub processを正常に終了させる(JOBを完遂して終了する) / End the sub process normally (complete the JOB and end)
        """
        if self.__process is not None:
            # sub processにSIGINTシグナルを送る / Send SIGINT signal to sub process
            os.kill(self.__process.pid, signal.SIGINT)

        self.__terminating = True


    def immediately_terminate(self):
        """ sub processを即時に終了させる / Immediately terminate sub process
        """
        if self.__process is not None:
            # sub processにSIGTERMシグナルを送る / Send SIGTERM signal to sub process
            self.__process.terminate()

        self.__terminating = True


    def kill(self):
        """ sub processをkillする / kill sub process
        """
        if self.__process is not None:
            self.__process.kill()

        self.__terminating = True


    def get_status(self) -> SubProcessStatus:
        """ sub processの状態を返す / returns the status of sub process

        Returns:
            SubProcessStatus: sub process status
        """
        if self.__process is None:
            # processがNoneにされている時はEXITEDのステータスを返す
            # When process is set to None, returns status of EXITED
            return SubProcessStatus.EXITED

        if not self.__process.is_alive():
            # processがaliveでない時はEXITEDのステータスを返す
            # Returns EXITED status when process is not alive
            return SubProcessStatus.EXITED

        if self.__teminating_time <= datetime.datetime.now() or self.__terminating:
            # sub processが終了時刻を過ぎているか終了指示が行われている場合、TERMINATINGのステータスを返す 
            # If the sub process has passed its termination time or has been instructed to terminate, it returns a status of TERMINATING.
            return SubProcessStatus.TERMINATING

        # 全ての条件を満たさない場合はACCEPTABLEの状態を返す
        # If all conditions are not met, return ACCEPTABLE status
        return SubProcessStatus.ACCEPTABLE


    def get_terminating_time(self) -> datetime.datetime:
        """終了時刻の取得 / Get terminating time

        Returns:
            datetime.datetime: 終了時刻 / terminating time
        """
        return self.__teminating_time


    def join(self):
        """join sub process
        """
        if self.__process is not None:
            self.__process.join()


    def get_pid(self):
        """get sub process process id

        Returns:
            int: sub process process id
        """
        if self.__process is not None:
            return self.__process.pid
        else:
            return None
