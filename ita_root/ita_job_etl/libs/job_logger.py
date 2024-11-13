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
import sys
import multiprocessing
import logging
import logging.handlers

class JobLogger():

    @classmethod
    def initialize(cls, main_process):
        cls.__logger = logging.getLogger()

        if main_process:
            log_queue = multiprocessing.Queue()
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter('[%(asctime)s] [%(process)06d:%(threadName)s] [%(levelname)-5s] %(message)s')
            console_handler.setFormatter(console_formatter)

            queue_handler = logging.handlers.QueueHandler(log_queue)
            cls.__logger.addHandler(queue_handler)
            cls.__logger.setLevel(os.environ.get('LOG_LEVEL', logging.INFO))

            cls.__log_listener = logging.handlers.QueueListener(log_queue, console_handler)
            cls.__log_listener.start()
        else:
            cls.__log_listener = None

    @classmethod
    def tick(cls):
        pass

    @classmethod
    def error(cls, message):
        cls.__logger.error(message)

    @classmethod
    def warning(cls, message):
        cls.__logger.warning(message)

    @classmethod
    def info(cls, message):
        cls.__logger.info(message)

    @classmethod
    def debug(cls, message):
        cls.__logger.debug(message)

    @classmethod
    def terminate(cls):
        try:
            if cls.__log_listener is not None:
                cls.__log_listener.stop()
        except Exception:
            pass