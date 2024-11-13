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
from flask import g

import job_config as config

from libs.job_threads import JobThreads
from libs.job_classes import JobClasses
from libs.job_queue_row import JobQueueRow

from common_libs.common.dbconnect.dbconnect_common import DBConnectCommon


class JubQueue():
    @classmethod
    def query_queue(cls, conn: DBConnectCommon) -> list[JobQueueRow]:
        exists_sql = False
        sqlstmt = "SELECT * FROM ("
        unionstml = ""

        for job_name in config.JOB_CONFIG.keys():
            stmtpart = JobClasses.get_job_executor_class(job_name).queue_query_stmt(conn)
            if stmtpart is not None and stmtpart.strip() != "":
                sqlstmt += unionstml + stmtpart
                exists_sql = True
                unionstml = " UNION ALL "

        if exists_sql:
            sqlstmt += f") IV ORDER BY IV.LAST_UPDATE_TIMESTAMP LIMIT {config.QUEUE_LOAD_ROWS}"
            # g.applogger.debug(f'query queue SQL:\n{sqlstmt}')
            conn.db_transaction_start()
            rows = conn.sql_execute(sqlstmt)
            conn.db_transaction_end(True)
            return [JobQueueRow(row) for row in rows]
        else:
            return []


    @classmethod
    def pop(cls, job_queue: list[JobQueueRow], job_threads: JobThreads):
        # TODO: 取得優先度の実装
        ret = job_queue[0]
        del job_queue[0]
        return ret

