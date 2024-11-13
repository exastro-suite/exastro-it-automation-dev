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

SUB_PROCESS_ACCEPTABLE = 2

SUB_PROCESS_WATCH_INTERVAL_SECONDS = 1
SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS = 30

EXCEPTION_RESTART_INTERVAL_SECONDS = 5

MAX_JOB_PER_PROCESS = 10

QUEUE_LOAD_ROWS = MAX_JOB_PER_PROCESS * (SUB_PROCESS_ACCEPTABLE + 1)
QUEUE_WATCH_INTERVAL_SECONDS = 3

MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS = 10
CLEANUP_INTERVAL_SECONDS = 3600
# CLEANUP_INTERVAL_SECONDS = 30

JOB_CANCEL_TIMEOUT_SECONDS = 3

JOB_CONFIG = {
    "test_job1": {
        "timeout_seconds": 20,
        "module": "jobs.test_job1_executor",
        "class": "TestJob1Executor",
        "max_job_per_process": 10,
        "extra_config": {
        }
    }
}

# sub processの再起動（別の新プロセス起動）の間隔
# JOBの最大のtimeout時間の1.5倍もしくは指定値（デフォルト2時間）
SUB_PROCESS_ACCEPTABLE_SECONDS = max([job_config["timeout_seconds"] for job_config in JOB_CONFIG.values() ]) * 1.5
if SUB_PROCESS_ACCEPTABLE_SECONDS < 7200:
    SUB_PROCESS_ACCEPTABLE_SECONDS = 7200

# SUB_PROCESS_ACCEPTABLE_SECONDS=60