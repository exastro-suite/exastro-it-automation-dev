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

class JobLogging():
    """JobLogging
    """
    # Logger instance
    __logger = logging.getLogger()
    # Log Queue Listener
    __listener = None
    # stream handler (For changing log level)
    __stream_handler = None
    # Log Level
    __level = None


    @classmethod
    def initialize(cls):
        """initialize - Call only in main process
        """
        # log queueへのログ送信設定 / Settings for sending logs to log queue
        log_queue = multiprocessing.Queue()
        log_queue_handler = logging.handlers.QueueHandler(log_queue)
        cls.__logger.addHandler(log_queue_handler)
        cls.__logger.setLevel(logging.NOTSET)

        # log queueからstdoutへログ出力する設定
        # Settings to output logs from log queue to stdout
        cls.__stream_handler = logging.StreamHandler(sys.stdout)
        cls.__stream_handler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(process)06d:%(threadName)s] [%(levelname)-5s] %(message)s"))
        cls.setLevel(os.environ.get('LOG_LEVEL','INFO'))

        # log queue listenerの開始 / Starting the log queue listener
        cls.__listener = logging.handlers.QueueListener(log_queue, cls.__stream_handler, respect_handler_level=True)
        cls.__listener.start()


    @classmethod
    def getLogger(cls) -> logging.Logger:
        """loggerインスタンス取得 / Get logger instance

        Returns:
            logging.Logger : logger instance
        """
        return cls.__logger


    @classmethod
    def getLevel(cls):
        """現在のログレベルを返す / returns the current log level

        Returns:
            str: log level
        """
        return cls.__level

    @classmethod
    def setLevel(cls, log_level):
        """ログレベルを変更します / Change log level

        Args:
            log_level (str): log level
        """
        cls.__level = log_level
        cls.__stream_handler.setLevel(log_level)

    @classmethod
    def error(cls, message):
        """error log

        Args:
            message (str): message
        """
        cls.__logger.error(message)

    @classmethod
    def warning(cls, message):
        """warning log

        Args:
            message (str): message
        """
        cls.__logger.warning(message)

    @classmethod
    def info(cls, message):
        """info log

        Args:
            message (str): message
        """
        cls.__logger.info(message)

    @classmethod
    def debug(cls, message):
        """debug log

        Args:
            message (str): message
        """
        cls.__logger.debug(message)

    @classmethod
    def terminate(cls):
        """terminate logger - Call only in main process
        """
        try:
            if cls.__listener is not None:
                cls.__listener.stop()
        except Exception:
            pass
