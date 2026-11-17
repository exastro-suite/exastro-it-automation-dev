# Copyright 2025 NEC Corporation#
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
Jinja2 SSTI対策: 結論ラベル設定(Action.generateConclusionLables)のテスト
"""
import pytest
from flask import Flask, g

from libs.action import Action


class DummyEventObj:
    def __init__(self, labels):
        self.labels = labels

    def get_events(self, event_id):
        return True, {"labels": self.labels}


class DummyLogger:
    def __getattr__(self, name):
        return lambda *a, **k: None


class DummyAppMsg:
    def get_log_message(self, code, args=None):
        return f"{code} {args}"


@pytest.fixture(autouse=True)
def flask_g():
    app = Flask(__name__)
    with app.app_context():
        g.applogger = DummyLogger()
        g.appmsg = DummyAppMsg()
        yield


def generate(label_value, labels=None):
    action = Action(wsDb=None, EventObj=DummyEventObj(labels or {"host": "serverA", "_exastro_rule_name": "rule1"}))
    rule_row = {"CONCLUSION_LABEL_SETTINGS": [{"label_key": "1", "label_value": label_value}]}
    action_parameters, _ = action.generateConclusionLables(["ev-a"], rule_row, {"1": "result_label"}, "0", "0")
    return action_parameters["result_label"]


def test_ssti_is_blocked(tmp_path):
    """結論ラベル設定のSSTIは実行されず、エラー文字列がラベル値になる"""
    marker = tmp_path / "marker.txt"
    payload = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker

    value = generate(payload)

    assert value.startswith("CONCLUSION LABELS jinja2TEMPLATE ERROR")
    assert "unsafe" in value
    assert not marker.exists()


def test_ssti_is_blocked_even_when_cached(tmp_path):
    """同じテンプレートの2回目(template_cache経由)でも遮断される"""
    marker = tmp_path / "marker.txt"
    payload = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker
    action = Action(wsDb=None, EventObj=DummyEventObj({"host": "h"}))
    rule_row = {"CONCLUSION_LABEL_SETTINGS": [{"label_key": "1", "label_value": payload}]}

    for _ in range(2):
        params, _ = action.generateConclusionLables(["ev-a"], rule_row, {"1": "result_label"}, "0", "0")
        assert params["result_label"].startswith("CONCLUSION LABELS jinja2TEMPLATE ERROR")

    assert not marker.exists()


@pytest.mark.parametrize("template, expected", [
    ("True", "True"),
    ("{{ A.host }}", "serverA"),
    ("host={{ A.host }} rule={{ A._exastro_rule_name }}", "host=serverA rule=rule1"),
    ("{% if A.host == 'serverA' %}yes{% else %}no{% endif %}", "yes"),
    ("{{ A.host | upper }}", "SERVERA"),
])
def test_legitimate_templates_still_work(template, expected):
    """A/Bラベル参照(_始まりの辞書キー含む)・フィルタ・制御構文は従来通り動作する"""
    assert generate(template) == expected
