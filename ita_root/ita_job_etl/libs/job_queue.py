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
from typing import Optional
import random
from flask import g

import job_config as config

from libs.job_threads import JobThreads
from libs.job_classes import JobClasses
from libs.job_queue_row import JobQueueRow

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon


class JubQueue():
    """job queue処理class / job queue processing class
    """

    @classmethod
    def query_queue(cls, conn: DBConnectCommon, startable_jobs: list[str]) -> list[JobQueueRow]:
        """job queueとなるtableに対して検索を行う / Perform a search on the table that is the job queue

        Args:
            conn (DBConnectCommon): db connection (ita-user)
            startable_jobs (list[str]): startable job name list

        Returns:
            list[JobQueueRow]: job queue
        """
        exists_sql = False
        sqlstmt = "SELECT * FROM ("
        unionstml = ""

        for job_name in config.JOB_CONFIG.keys():
            if job_name not in startable_jobs:
                # 開始可能でないjobについては処理対象としない
                # Jobs that cannot be started are not processed.
                continue

            # job毎のqueueテーブルへのselect文を取得する
            # Get the select statement to the queue table for each job
            stmtpart = JobClasses.get_job_executor_class(job_name).queue_query_stmt(conn)

            if stmtpart is not None and stmtpart.strip() != "":
                # job毎のqueueテーブルへのselect文をunion allで結合する
                # Combine select statements to the queue table for each job using union all
                sqlstmt += unionstml + stmtpart
                exists_sql = True
                unionstml = " UNION ALL "

        if exists_sql:
            # LAST_UPDATE_TIMESTAMPでソートし先頭から規定行数取得するSQL文を付加する
            # Add a SQL statement to sort by LAST_UPDATE_TIMESTAMP and retrieve the specified number of rows from the beginning
            sqlstmt += f") IV ORDER BY IV.LAST_UPDATE_TIMESTAMP LIMIT {config.QUEUE_LOAD_ROWS}"

            # g.applogger.debug(f'query queue SQL:\n{sqlstmt}')
            conn.db_transaction_start()
            rows = conn.sql_execute(sqlstmt)
            conn.db_transaction_end(True)
            return [JobQueueRow(row) for row in rows]
        else:
            # SQLが全JOBで返されなかった場合は0件のlistを返す
            # If SQL is not returned for all JOBs, return a list of 0 items
            return []


    @classmethod
    def pop(cls, job_queue: list[JobQueueRow], job_threads: JobThreads) -> Optional[JobQueueRow]:
        """ job queueからのデータ取り出し / Retrieving data from job queue

        Args:
            job_queue (list[JobQueueRow]): job queue
            job_threads (JobThreads): job threads

        Returns:
            Optional[JobQueueRow]: job queue data
        """
        # 開始可能なJOBの一覧を取得する
        # Get a list of jobs that can be started
        startable_jobs = job_threads.get_startable_job_name_list()

        # 開始可能でないJOBをqueueから削除する
        # Remove JOBs that cannot be started from the queue
        for i in reversed(range(len(job_queue))):
            if job_queue[i].job_name not in startable_jobs:
                del job_queue[i]

        # queueの情報が無くなった場合はNoneを返す
        # Returns None if there is no queue information
        if len(job_queue) == 0:
            return None

        # JOBを開始する優先度を決定するためorganization毎の実行中のJOB件数を取得する
        # Obtain the number of running jobs for each organization to determine the priority for starting jobs
        count_jobs_grouping_by_organization = job_threads.count_jobs_grouping_by_organization()

        # organization毎の実行中のJOB件数、queueへの登録日時、乱数でソートする
        # Sort by number of running jobs for each organization, date and time of registration in queue, and random numbers
        job_queue.sort(key=lambda x: (count_jobs_grouping_by_organization.get(x.organization_id, 0), x.queue_time, random.randrange(999999)))

        # queueの先頭の情報を返して削除する
        # Return and delete information at the head of the queue
        ret = job_queue[0]
        del job_queue[0]

        return ret

