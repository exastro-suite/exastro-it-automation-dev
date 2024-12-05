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

# sub processの起動数（sub process交代のタイミングでこの数を超えることがあります）
# Number of sub processes started (this number may be exceeded when sub processes are replaced)
SUB_PROCESS_ACCEPTABLE = int(os.environ['SUB_PROCESS_ACCEPTABLE'])

# メイン処理の実行間隔
# この間隔でprocessやthreadの状態の監視、および各種間隔実行の時間経過を確認する
# （他の間隔指定は本間隔単位以下にしても機能しません）
#
# Execution interval of main processing
# Monitor the status of processes and threads at this interval, and check the time elapsed for various interval executions
# (Other interval specifications will not work even if they are less than this interval unit)
SUB_PROCESS_WATCH_INTERVAL_SECONDS = int(os.environ['SUB_PROCESS_WATCH_INTERVAL_SECONDS'])

# QUEUE監視のDBへの再接続間隔
# Reconnection interval to DB for QUEUE monitoring
SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS = int(os.environ['SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS'])

# 例外発生後の処理再開までの間隔（エラーログのラッシュ防止用）
# Interval until processing resumes after an exception occurs (to prevent error log rush)
EXCEPTION_RESTART_INTERVAL_SECONDS = int(os.environ['EXCEPTION_RESTART_INTERVAL_SECONDS'])

# sub process当たりの最大同時実行JOB数
# Maximum number of concurrently executing jobs per sub process
MAX_JOB_PER_PROCESS = int(os.environ['MAX_JOB_PER_PROCESS'])

# QUEUEの最大読み出し数
# JOBが長時間ためられてしまった時にメモリを食いつぶさないようにする処置
# Maximum number of QUEUE reads
# Measures to prevent memory from being consumed when JOB is stored for a long time
QUEUE_LOAD_ROWS = MAX_JOB_PER_PROCESS * (SUB_PROCESS_ACCEPTABLE * 2 + 1)

# QUEUEの読み出し間隔
# QUEUE read interval
QUEUE_WATCH_INTERVAL_SECONDS = int(os.environ['QUEUE_WATCH_INTERVAL_SECONDS'])

# メンテナンスモードのチェック間隔
# Maintenance mode check interval
MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS = int(os.environ['MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS'])

# CLEAN UPの呼び出し間隔
# CLEAN UP call interval
CLEANUP_INTERVAL_SECONDS = int(os.environ['CLEANUP_INTERVAL_SECONDS'])

# JOBのCANCELのTimeout時間
# JOB CANCEL Timeout time
JOB_CANCEL_TIMEOUT_SECONDS = int(os.environ['JOB_CANCEL_TIMEOUT_SECONDS'])

# Log Level 再設定の間隔
# Log Level resetting interval
RESET_LOG_LEVEL_INTERVAL_SECONDS = int(os.environ['RESET_LOG_LEVEL_INTERVAL_SECONDS'])

JOB_CONFIG = {
    # "test_job1": {
    #     "timeout_seconds": 20,
    #     "module": "jobs.test_job1_executor",
    #     "class": "TestJob1Executor",
    #     "max_job_per_process": 10,
    #     "extra_config": {
    #     }
    # },
    "menu_create": {
        "timeout_seconds": int(os.environ['JOB_MENU_CREATE_TIMEOUT_SECONDS']),
        "module": "jobs.menu_create_executor",
        "class": "MenuCreateExecutor",
        "max_job_per_process": MAX_JOB_PER_PROCESS,
        "extra_config": {
        }
    },
    "ansible_legacy_vars_listup": {
        "timeout_seconds": int(os.environ['JOB_ANSIBLE_LEGACY_VARS_LISTUP_TIMEOUT_SECONDS']),
        "module": "jobs.ansible_legacy_vars_listup_executor",
        "class": "AnsibleLegacyVarsListupExecutor",
        "max_job_per_process": MAX_JOB_PER_PROCESS,
        "extra_config": {
        }
    },
    "ansible_pioneer_vars_listup": {
        "timeout_seconds": int(os.environ['JOB_ANSIBLE_PIONEER_VARS_LISTUP_TIMEOUT_SECONDS']),
        "module": "jobs.ansible_pioneer_vars_listup_executor",
        "class": "AnsiblePioneerVarsListupExecutor",
        "max_job_per_process": MAX_JOB_PER_PROCESS,
        "extra_config": {
        }
    },
    "ansible_legacy_role_vars_listup": {
        "timeout_seconds": int(os.environ['JOB_LEGACY_ROLE_VARS_LISTUP_TIMEOUT_SECONDS']),
        "module": "jobs.ansible_legacy_role_vars_listup_executor",
        "class": "AnsibleLegacyRoleVarsListupExecutor",
        "max_job_per_process": MAX_JOB_PER_PROCESS,
        "extra_config": {
        }
    }
}

# sub processの再起動（別の新プロセス起動）の間隔のデフォルト値
# Default value for restarting sub process (starting another new process) interval
SUB_PROCESS_ACCEPTABLE_SECONDS_DEFAULT =int(os.environ['SUB_PROCESS_ACCEPTABLE_SECONDS_DEFAULT'])

# sub processの再起動（別の新プロセス起動）の間隔
# JOBの最大のtimeout時間の1.5倍もしくはデフォルト値
# Interval between restarting sub process (starting another new process)
# 1.5 times the JOB maximum timeout time or default value
SUB_PROCESS_ACCEPTABLE_SECONDS = max([job_config["timeout_seconds"] for job_config in JOB_CONFIG.values() ]) * 1.5
if SUB_PROCESS_ACCEPTABLE_SECONDS < SUB_PROCESS_ACCEPTABLE_SECONDS_DEFAULT:
    SUB_PROCESS_ACCEPTABLE_SECONDS = SUB_PROCESS_ACCEPTABLE_SECONDS_DEFAULT
