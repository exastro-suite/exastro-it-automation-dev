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

class JobTimeoutException(Exception):
    """JOBのtimeout例外 本例外を受け取った場合、速やかにJOBを終了（中断）すること
        JOB timeout exception If you receive this exception, immediately terminate (interrupt) the JOB.
    """
    pass

class JobTeminate(Exception):
    """clean upの中断例外 本例外を受け取った場合、速やかに終了（中断）すること
        Clean up interruption exception If you receive this exception, terminate (interrupt) immediately.
    """
    pass
