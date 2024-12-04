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

# sub processの起動数（sub process交代のタイミングでこの数を超えることがあります）
SUB_PROCESS_ACCEPTABLE = 2

# メイン処理の実行間隔
# この間隔でprocessやthreadの状態の監視、および各種間隔実行の時間経過を確認する
# （他の間隔指定は本間隔単位以下にしても機能しません）
SUB_PROCESS_WATCH_INTERVAL_SECONDS = 1

# QUEUE監視のDBへの再接続間隔
SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS = 30

# 例外発生後の処理再開までの間隔（エラーログのラッシュ防止用）
EXCEPTION_RESTART_INTERVAL_SECONDS = 5

# sub process当たりの最大同時実行JOB数
MAX_JOB_PER_PROCESS = 10

# QUEUEの最大読み出し数
# JOBが長時間ためられてしまった時にメモリを食いつぶさないようにする処置
QUEUE_LOAD_ROWS = MAX_JOB_PER_PROCESS * (SUB_PROCESS_ACCEPTABLE * 2 + 1)

# QUEUEの読み出し間隔
QUEUE_WATCH_INTERVAL_SECONDS = 3

# メンテナンスモードのチェック間隔
MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS = 10

# CLEAN UPの呼び出し間隔
CLEANUP_INTERVAL_SECONDS = 3600
# CLEANUP_INTERVAL_SECONDS = 30

# JOBのCANCELのTimeout時間
JOB_CANCEL_TIMEOUT_SECONDS = 3

# Log Level 再設定の間隔 
RESET_LOG_LEVEL_INTERVAL_SECONDS = 10

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
        "timeout_seconds": 20,
        "module": "jobs.menu_create_executor",
        "class": "MenuCreateExecutor",
        "max_job_per_process": MAX_JOB_PER_PROCESS,
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