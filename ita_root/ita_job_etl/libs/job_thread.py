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
import datetime
from enum import Enum, auto

from libs.job_classes import JobClasses
from libs.job_queue_row import JobQueueRow
from jobs.base_job_executor import BaseJobExecutor

import job_config as config
import ulid

THREAD_NAME_MAX_LENGTH=15

class JobThreadStatus(Enum):
    NOT_RUNNING = auto()
    RUNNING = auto()
    FINISHED = auto()
    TIMEOUT = auto()
    CANCELING = auto()
    CANCELED = auto()
    CANCELLATION_TIMEOUT = auto()


class JobThread():
    def __init__(self, queue: JobQueueRow):
        self.__queue = queue
        self.__job_config = config.JOB_CONFIG[queue.job_name]
        self.__job_executor_class = JobClasses.get_job_executor_class(queue.job_name)
        self.__job_executor_instance = self.__job_executor_class(queue=queue, job_config=self.__job_config)
        self.__execute_thread = None
        self.__execute_start_time = None
        self.__execute_timeout_time = None
        self.__cancel_thread = None
        self.__cancel_start_time = None
        self.__cancel_timeout_time = None
        self.__ulid = ulid.new().str

    def update_queue_to_start(self):
        return self.__job_executor_instance.call_update_queue_to_start()

    def run(self):
        self.__execute_thread = threading.Thread(
                name=f'E-{self.__ulid}'[:THREAD_NAME_MAX_LENGTH+1],
                target=self.__job_executor_instance.call_execute,
                daemon=True
            )
        self.__execute_thread.start()
        self.__execute_start_time = datetime.datetime.now()
        self.__execute_timeout_time =  self.__execute_start_time + datetime.timedelta(seconds=self.__job_config["timeout_seconds"])


    def cancel(self):
        # timeout exceptionをthrow
        self.__job_executor_instance.send_execute_timeout_exception()

        # cancel処理を起動
        self.__cancel_thread = threading.Thread(
                name=f'C-{self.__ulid}'[:THREAD_NAME_MAX_LENGTH+1],
                target=self.__job_executor_instance.call_cancel,
                daemon=True
            )
        self.__cancel_thread.start()
        self.__cancel_start_time = datetime.datetime.now()
        self.__cancel_timeout_time = self.__execute_start_time + datetime.timedelta(seconds=config.JOB_CANCEL_TIMEOUT_SECONDS)


    def send_thread_timeout(self):
        if self.__execute_thread.is_alive():
            self.__job_executor_instance.send_execute_timeout_exception()

        if self.__cancel_thread is not None and self.__cancel_thread.is_alive():
            self.__job_executor_instance.send_cancel_timeout_exception()


    def join(self):
        self.__execute_thread.join()
        if self.__cancel_thread is not None:
            self.__cancel_thread.join()


    def is_erasable(self):
        if self.__execute_start_time is None:
            return False

        if self.__execute_thread.is_alive():
            return False

        if self.__cancel_thread is None:
            return True

        if self.__cancel_thread.is_alive():
            return False

        return True


    def get_status(self) -> JobThreadStatus:
        if self.__execute_start_time is None:
            return JobThreadStatus.NOT_RUNNING

        if self.__cancel_start_time is None:
            if self.__execute_thread.is_alive():
                if self.__execute_timeout_time <= datetime.datetime.now():
                    return JobThreadStatus.TIMEOUT
                else:
                    return JobThreadStatus.RUNNING
            else:
                return JobThreadStatus.FINISHED
        else:
            if self.__cancel_thread.is_alive():
                if self.__cancel_timeout_time <= datetime.datetime.now():
                    return JobThreadStatus.CANCELLATION_TIMEOUT
                else:
                    return JobThreadStatus.CANCELING
            else:
                if self.__execute_thread.is_alive():
                    return JobThreadStatus.CANCELING
                else:
                    return JobThreadStatus.CANCELED
