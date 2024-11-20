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
import time
from itertools import groupby

from flask import g

from libs.job_thread import JobThread, JobThreadStatus

import job_config as config


class JobThreads():
    """ Jobスレッド管理class / Job thread management class
    """
    def __init__(self):
        """ constructor
        """
        self.__job_threads : list[JobThread] = []

    def tick(self):
        """ Jobスレッド情報更新 / Job threads information updated
        """
        # 削除可能なJob thread情報は削除する / Delete job thread information that can be deleted
        self.__job_threads = [thread for thread in self.__job_threads if not thread.is_erasable()]

        for job_thread in self.__job_threads:
            status = job_thread.get_status()
            if status == JobThreadStatus.TIMEOUT:
                # JOBがtimeoutとなったらcancelする / Cancel when JOB times out
                job_thread.cancel()

            if status == JobThreadStatus.CANCELLATION_TIMEOUT:
                # JOBのcancelがtimeoutしたら、Jobのthreadにtimeoutを発行する
                # When JOB cancel times out, issue timeout to Job thread
                job_thread.send_thread_timeout()


    def start_job(self, job_thread: JobThread):
        """JOBのthreadを開始する / Start the JOB thread

        Args:
            job_thread (JobThread): _description_
        """
        job_thread.run()
        self.__job_threads.append(job_thread)


    def join(self):
        """全てのJob threadをjoinする / Join all Job threads
        """
        for job_thread in self.__job_threads:
            job_thread.join()


    def terminate(self):
        """全てのJob threadを強制終了する / Force quit all Job threads
        """
        while self.count_all_jobs() > 0:
            # job threadが全て無くなるまで繰り返す / Repeat until all job threads are exhausted

            for job_thread in self.__job_threads:
                # 全てのjob thread分繰り返す / Repeat for all job threads

                status = job_thread.get_status()
                if status in [JobThreadStatus.RUNNING, JobThreadStatus.TIMEOUT]:
                    # job threadの状態がRUNNINGかTIMEOUT(cancel未実施)の場合、cancelを行う
                    # If the job thread status is RUNNING or TIMEOUT (cancel not executed), cancel.
                    job_thread.cancel()

                elif status == JobThreadStatus.CANCELLATION_TIMEOUT:
                    # Threadが終わらないものは、うまくcancel処理ができてないので、timeout exceptionを送り続ける
                    # If the Thread does not end, the cancel processing is not performed properly, so it continues to send a timeout exception.
                    job_thread.send_thread_timeout()

            time.sleep(config.SUB_PROCESS_WATCH_INTERVAL_SECONDS)
            # job threadの状態を更新する / Update job thread state
            self.tick()


    def cancel_all(self):
        """全てのjob threadに取り消しを指示する / Instruct all job threads to cancel
        """
        for job_thread in self.__job_threads:
            # 全てのjob thread分繰り返す / Repeat for all job threads

            if job_thread.get_status() in [JobThreadStatus.RUNNING, JobThreadStatus.TIMEOUT]:
                # job threadの状態がRUNNINGかTIMEOUT(cancel未実施)の場合、cancelを行う
                # If the job thread status is RUNNING or TIMEOUT (cancel not executed), cancel.
                job_thread.cancel()


    def count_all_jobs(self) -> int:
        """Job threadの件数を返す / Return the number of Job threads

        Returns:
            int: number of Job threads
        """
        return len(self.__job_threads)


    def count_jobs_grouping_by_name(self) -> dict:
        """実行中jobのjob種類ごとの件数を返します / Returns the number of running jobs for each job type

        Returns:
            dict: {job_name, number of running jobs}
        """
        return { job_name: 0 for job_name in config.JOB_CONFIG.keys() }.update(
            { job_name: len(list(grp)) for job_name, grp in groupby(sorted(self.__job_threads, key=lambda x: x.get_job_name()), key=lambda x: x.get_job_name())}
        )


    def get_startable_job_name_list(self) -> list[str]:
        """起動可能なjob nameのlistを返します / Returns a list of job names that can be started

        Returns:
            list[str]: startable job names
        """
        counts = { job_name: job_config["max_job_per_process"] for job_name, job_config in config.JOB_CONFIG.items() }
        for job_tread in self.__job_threads:
            counts[job_tread.get_job_name()] -= 1

        return [ job_name for job_name, startable_count in counts.items() if startable_count >= 1 ]


    def count_jobs_grouping_by_organization(self) -> dict:
        """オーガナイゼーション毎のJOBの実行数を返します / Returns the number of JOB executions for each organization

        Returns:
            dict: {organization_id, number of running jobs}
        """
        return { organization_id: len(list(grp)) for organization_id, grp in groupby(sorted(self.__job_threads, key=lambda x: x.get_organization_id()), key=lambda x: x.get_organization_id())}
