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

# common_libraryを使うためのflaskのダミー
# flask dummy for using common_library


import os
from enum import Enum, EnumMeta

from libs.job_logger import JobLogger

class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        return item in cls.__members__.keys()


class BaseEnum(Enum, metaclass=MetaEnum):
    pass


class g(BaseEnum):
    @classmethod
    def initialize(cls, is_main_process = False):
        from common_libs.common.message_class import MessageTemplate
        # from common_libs.common.util import get_maintenance_mode_setting, get_iso_datetime, arrange_stacktrace_format

        cls.LANGUAGE = os.environ.get("LANGUAGE")
        cls.appmsg = MessageTemplate(g.LANGUAGE)
        JobLogger.initialize(is_main_process)
        cls.applogger = JobLogger
        cls.USER_ID = os.environ.get("USER_ID")
        cls.SERVICE_NAME = os.environ.get("SERVICE_NAME")
        cls.ORGANIZATION_ID = ""
        cls.WORKSPACE_ID = ""

    @classmethod
    def get(cls, name):
        return None

    @classmethod
    def tick(cls):
        cls.applogger.tick()

    @classmethod
    def terminate(cls):
        cls.applogger.terminate()
