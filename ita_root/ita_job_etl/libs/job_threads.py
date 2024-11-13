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

from libs.job_thread import JobThread, JobThreadStatus
from libs.job_queue_row import JobQueueRow

class JobThreads():
    def __init__(self):
        self.__job_threads : list[JobThread] = []

    def tick(self):
        self.__job_threads = [thread for thread in self.__job_threads if not thread.is_erasable()]

        for job_thread in self.__job_threads:
            status = job_thread.get_status()
            if status == JobThreadStatus.TIMEOUT:
                job_thread.cancel()
            if status == JobThreadStatus.CANCELLATION_TIMEOUT:
                job_thread.send_thread_timeout()

    def start_job(self, job_thread: JobThread):
        job_thread.run()
        self.__job_threads.append(job_thread)

    def join(self):
        for job_thread in self.__job_threads:
            job_thread.join()

    def cancel_all(self):
        for job_thread in self.__job_threads:
            if job_thread.get_status() in [JobThreadStatus.RUNNING, JobThreadStatus.TIMEOUT]:
                job_thread.cancel()

    def count_all_jobs(self) -> int:
        return len(self.__job_threads)

    def count_jobs_grouping_by_name(self) -> dict:
        pass

    def count_jobs_grouping_by_organization(self) -> dict:
        pass

