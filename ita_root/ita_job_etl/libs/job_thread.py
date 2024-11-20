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
# from jobs.base_job_executor import BaseJobExecutor

import job_config as config
import ulid

THREAD_NAME_MAX_LENGTH=15

class JobThreadStatus(Enum):
    """Job threadの状態 / Job thread status
    """
    # status遷移 / status transition
    #
    #   NOT_RUNNING                                 new JobTread()
    #   ->   RUNNING                                CALL JobTread().run()
    #       ->  FINISHED                            When job finished
    #       ->  TIMEOUT                             jobを開始して所定のtimeout時間が経過した(cancel未実施) / The specified timeout time has passed since the job was started (cancellation has not been performed)
    #           ->  CANCELING                       jobのcancelを実施中 / Job is being canceled
    #               ->  CANCELED                    jobのcancelの完了 / finish of job cancellation
    #               ->  CANCELLATION_TIMEOUT        jobをキャンセルを開始して所定のtimeout時間が経過した / The specified timeout period has passed since the job was canceled.
    #                   -> CANCELED                 ジョブの取り消しの中止が完了 / Job cancellation abort completed
    NOT_RUNNING = auto()
    RUNNING = auto()
    FINISHED = auto()
    TIMEOUT = auto()
    CANCELING = auto()
    CANCELED = auto()
    CANCELLATION_TIMEOUT = auto()


class JobThread():
    """job thread
    """

    def __init__(self, queue: JobQueueRow):
        """constructor

        Args:
            queue (JobQueueRow): queue
        """
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


    def update_queue_to_start(self) -> bool:
        """queueを開始した状態に更新する / Update queue to started state

        Returns:
            bool:   True: 成功(job開始OK) / Success (job start OK)
                    False: 失敗(job開始NG) / Failure (job cannot start)
        """
        return self.__job_executor_instance.call_update_queue_to_start()


    def run(self):
        """job threadの起動 / Starting a job thread
        """
        self.__execute_thread = threading.Thread(
                name=f'E-{self.__ulid}'[:THREAD_NAME_MAX_LENGTH+1],
                target=self.__job_executor_instance.call_execute,
                daemon=True
            )
        self.__execute_thread.start()
        self.__execute_start_time = datetime.datetime.now()
        self.__execute_timeout_time =  self.__execute_start_time + datetime.timedelta(seconds=self.__job_config["timeout_seconds"])


    def cancel(self):
        """jobのキャンセル / Cancel job
        """
        # job threadにtimeout exceptionをthrowさせる / Make the job thread throw a timeout exception
        self.__job_executor_instance.send_execute_timeout_exception()

        # cancel処理を起動 / Start cancel processing
        self.__cancel_thread = threading.Thread(
                name=f'C-{self.__ulid}'[:THREAD_NAME_MAX_LENGTH+1],
                target=self.__job_executor_instance.call_cancel,
                daemon=True
            )
        self.__cancel_thread.start()
        self.__cancel_start_time = datetime.datetime.now()
        self.__cancel_timeout_time = self.__execute_start_time + datetime.timedelta(seconds=config.JOB_CANCEL_TIMEOUT_SECONDS)


    def send_thread_timeout(self):
        """thread timeoutの送信 / Sending thread timeout
        """
        if self.__execute_thread.is_alive():
            self.__job_executor_instance.send_execute_timeout_exception()

        if self.__cancel_thread is not None and self.__cancel_thread.is_alive():
            self.__job_executor_instance.send_cancel_timeout_exception()


    def join(self):
        """job threadをjoinする / join job thread
        """
        self.__execute_thread.join()
        if self.__cancel_thread is not None:
            # cancel threadがいる場合はcancel threadもjoinする / If there is a cancel thread, also join the cancel thread
            self.__cancel_thread.join()


    def is_erasable(self) -> bool:
        """job threadのインスタンスを消してよいかを返す / Returns whether the job thread instance can be deleted

        Returns:
            bool:   True: 削除可能 / erasable
                    False: 削除不可 / not erasable
        """
        if self.__execute_start_time is None:
            # 開始前の段階では削除不可とする
            # Cannot be deleted before starting
            return False

        if self.__execute_thread.is_alive():
            # job threadが実行中の場合は削除不可とする
            # Cannot be deleted if job thread is running
            return False

        if self.__cancel_thread is None:
            # job threadが完了していて、cancel threadがいない場合は削除可とする
            # If the job thread is completed and there is no cancel thread, it can be deleted
            return True

        if self.__cancel_thread.is_alive():
            # cancel threadが存在していて実行中の場合は削除不可とする
            # If a cancel thread exists and is running, it cannot be deleted.
            return False

        # job threadもcancel threadも完了している場合は削除可とする
        # Can be deleted if both job thread and cancel thread are completed
        return True


    def get_status(self) -> JobThreadStatus:
        """get job thread status

        Returns:
            JobThreadStatus: job thread status
        """
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


    def get_job_name(self) -> str:
        """get job name

        Returns:
            str: job name
        """
        return self.__queue.job_name


    def get_organization_id(self) -> str:
        """get organization id

        Returns:
            str: organization id
        """
        return self.__queue.organization_id

