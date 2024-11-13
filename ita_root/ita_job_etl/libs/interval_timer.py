
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

import datetime

class IntervalTimer():
    """時間経過を管理するclass / A class that manages the passage of time
    """
    def __init__(self, interval_sec: int):
        """constructor

        Args:
            interval_sec (int): _description_
        """
        self.__interval_sec = interval_sec
        self.__set_next_time()

    def __set_next_time(self):
        """次の時間を設定する / Set next time
        """
        self.__next_time = datetime.datetime.now() + datetime.timedelta(seconds=self.__interval_sec)

    def is_passed(self):
        """時間が経過したか判定する / Determine if time has passed

        Returns:
            bool: True: time has passed
        """
        if datetime.datetime.now() >= self.__next_time:
            self.__set_next_time()
            return True
        else:
            return False
