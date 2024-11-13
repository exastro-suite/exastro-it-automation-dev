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
import typing
import signal
import datetime
import multiprocessing
from multiprocessing.sharedctypes import Value
from enum import Enum, auto
from collections.abc import Callable

from libs.clean_up_info import CleanUpInfo


class SubProcessStatus(Enum):
    ACCEPTABLE = auto()
    TERMINATING = auto()
    EXITED = auto()


class SubProcess():
    def __init__(
        self, job_manager_sub_process: Callable,
        teminating_time: datetime.datetime,
        clean_up_info: CleanUpInfo
    ):
        self.__start_time = datetime.datetime.now()
        self.__teminating_time = teminating_time
        self.__process = multiprocessing.Process(
            target=job_manager_sub_process,
            args=(teminating_time, clean_up_info))
        self.__process.start()

    def __del__(self):
        self.__process.close()
        del self.__process
        self.__process = None

    def graceful_terminate(self):
        if self.__process is not None:
            os.kill(self.__process.pid, signal.SIGINT)

    def immediately_terminate(self):
        if self.__process is not None:
            self.__process.terminate()

    def kill(self):
        if self.__process is not None:
            self.__process.kill()

    def get_status(self) -> SubProcessStatus:
        if self.__process is None:
            return SubProcessStatus.EXITED

        if not self.__process.is_alive():
            return SubProcessStatus.EXITED

        if self.__teminating_time <= datetime.datetime.now():
            return SubProcessStatus.TERMINATING

        return SubProcessStatus.ACCEPTABLE

    def get_terminating_time(self):
        return self.__teminating_time

    def join(self):
        if self.__process is not None:
            self.__process.join()

    def get_pid(self):
        if self.__process is not None:
            return self.__process.pid
