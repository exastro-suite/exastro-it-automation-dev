#   Copyright 2022 NEC Corporation
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
import pytest
from _pytest.logging import LogCaptureFixture
from unittest import mock
from unittest.mock import MagicMock

import os
import psutil
import threading

from flask import g
import job_manager
import job_config
from common import test_common



def test_job_manager_main_sigterm_signal():
    """job manager main の終了動作(sigterm signal)
    """
    sub_process_count = 2
    with mock.patch("job_config.SUB_PROCESS_ACCEPTABLE", sub_process_count):
        g.initialize()

        # main processの起動
        main_thread = threading.Thread(
            target=job_manager.job_manager_main_process,
            name="main_process",
            daemon=True
        )
        main_thread.start()

        try:
            # sub processの起動確認
            assert test_common.check_state(
                timeout=50.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=sub_process_count)

        finally:
            job_manager.job_manager_process_sigterm_handler(None, None)

            # sub processの終了確認
            assert test_common.check_state(
                timeout=50.0, conditions=lambda : len([p for p in psutil.Process(os.getpid()).children() if p.name().startswith('python') ]), conditions_value=0)

            # main processの終了確認
            assert not main_thread.is_alive()

            main_thread.join()