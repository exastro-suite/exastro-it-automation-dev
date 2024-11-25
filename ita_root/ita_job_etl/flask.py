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

from typing import Any
import threading
import os

from libs.job_logger import JobLogger

# Thread localの生成 / Generating Thread local
g_thread_local = threading.local()

class thread_local_object():
    """flask.gの模倣用のclass / class for imitating flask.g
    """
    def __init__(self):
        """constructor
        """
        global g_thread_local
        g_thread_local.dict = {}

        self.LANGUAGE = None
        self.appmsg = None
        self.applogger = None
        self.USER_ID = None
        self.SERVICE_NAME = None

    def initialize(self):
        """初期化（Threadの開始時にコールすること）/ Initialize (call when starting the Thread)
        """
        from common_libs.common.message_class import MessageTemplate
        global g_thread_local
        g_thread_local.dict = {}

        self.LANGUAGE = os.environ.get("LANGUAGE")
        self.appmsg = MessageTemplate(self.LANGUAGE)
        self.applogger = JobLogger
        self.USER_ID = os.environ.get("USER_ID")
        self.SERVICE_NAME = os.environ.get("SERVICE_NAME")

    def __setattr__(self, item: str, value: Any) -> None:
        """g.item = valueの処理 / Handling g.item = value

        Args:
            item (str): item name
            value (Any): item value
        """
        global g_thread_local
        g_thread_local.dict[item] = value

    def __setitem__(self, item: str, value: Any) -> None:
        """g[item] = valueの処理 / Handling g[item] = value

        Args:
            item (str): item name
            value (Any): item value
        """
        global g_thread_local
        g_thread_local.dict[item] = value

    def __contains__(self, item: str) -> bool:
        """item in gの処理 / Processing item in g

        Args:
            item (str): item name

        Returns:
            bool: True : in item / False not in item
        """
        global g_thread_local
        return item in g_thread_local.dict

    def __getattr__(self, item: str) -> Any:
        """get g.item

        Args:
            item (str): item name

        Returns:
            Any: g.item value
        """
        global g_thread_local
        return g_thread_local.dict[item]

    def __getitem__(self, item: str) -> Any:
        """get g[item]

        Args:
            item (str): item name

        Returns:
            Any: g.item value
        """
        global g_thread_local
        return g_thread_local.dict[item]

    def get(self, item: str, default: Any = None ) -> Any:
        """g.get(item)

        Args:
            item (str): item name
            default (Any, optional): Return value when item not in g. Defaults to None.

        Returns:
            Any: g.get(item) value
        """
        global g_thread_local
        return g_thread_local.dict.get(item, default)

# flask.gの模倣用のclassのインスタンス化 / Instantiating a class to imitate flask.g
g = thread_local_object()
