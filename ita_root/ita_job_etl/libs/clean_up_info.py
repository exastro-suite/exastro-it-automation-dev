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

import ctypes
import datetime
import multiprocessing

import job_config as config

class CleanUpInfo():
    def __init__(self):
        self.clean_up_pid = multiprocessing.Value(ctypes.c_int)
        self.clean_up_pid.value = 0
        self.clean_up_time = multiprocessing.Value(ctypes.c_double)
        self.clean_up_time.value = (datetime.datetime.timestamp(
            datetime.datetime.now() + datetime.timedelta(seconds=config.CLEANUP_INTERVAL_SECONDS)
        ))

