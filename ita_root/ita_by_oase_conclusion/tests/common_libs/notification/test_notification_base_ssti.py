# Copyright 2026 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Jinja2 SSTI対策: 通知テンプレート(Notification._create_notise_message)のテスト
"""
import pytest
from flask import Flask, g

from common_libs.notification.notification_base import Notification


class DummyNotification(Notification):
    """抽象メソッドを実装しただけのテスト用クラス(_create_notise_messageはclassmethodのため実体は不要)"""

    @classmethod
    def _fetch_table(cls, objdbca, decision_information):
        return {}

    @classmethod
    def _get_template(cls, fetch_data, decision_information):
        return []

    @staticmethod
    def _fetch_notification_destination(fetch_data, decision_information):
        return []


class DummyAppMsg:
    def get_log_message(self, code, args=None):
        return f"{code} {args}"


class DummyLogger:
    def __getattr__(self, name):
        return lambda *a, **k: None


@pytest.fixture(autouse=True)
def flask_g():
    app = Flask(__name__)
    with app.app_context():
        g.applogger = DummyLogger()
        g.appmsg = DummyAppMsg()
        yield


def test_ssti_in_body_is_blocked(tmp_path):
    """通知テンプレート内のSSTIは実行されず、Noneが返る"""
    marker = tmp_path / "marker.txt"
    template = (
        "[TITLE]\ntest\n[BODY]\n"
        "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker
    )

    result = DummyNotification._create_notise_message({"_id": "evt-1"}, template)

    assert result is None
    assert not marker.exists()


def test_ssti_in_title_is_blocked(tmp_path):
    marker = tmp_path / "marker.txt"
    template = (
        "[TITLE]\n{{ ''.__class__.__mro__[1].__subclasses__() }}\n[BODY]\nbody"
    )

    result = DummyNotification._create_notise_message({"_id": "evt-1"}, template)

    assert result is None
    assert not marker.exists()


def test_legitimate_template_still_works():
    """_id(_始まりのキー)や通常のキーを参照する正規テンプレートは従来通りレンダリングされる"""
    template = "[TITLE]\nEvent {{ _id }}\n[BODY]\nhost={{ labels.host }}"
    item = {"_id": "evt-999", "labels": {"host": "server01"}}

    result = DummyNotification._create_notise_message(item, template)

    assert result == {"title": "Event evt-999", "message": "host=server01"}
