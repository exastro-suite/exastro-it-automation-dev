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
Jinja2 SSTI対策: イベント収集設定(APIClientCommon.render)のテスト
"""
import pytest
from flask import Flask, g

from common_libs.oase.api_client_common import APIClientCommon

app = Flask(__name__)


class DummyLogger:
    def __init__(self):
        self.info_messages = []

    def info(self, msg, *a, **k):
        self.info_messages.append(msg)

    def debug(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class DummyAppMsg:
    def get_log_message(self, code, args=None):
        return f"{code} {args}"


@pytest.fixture(autouse=True)
def setup_g():
    with app.app_context():
        g.applogger = DummyLogger()
        g.appmsg = DummyAppMsg()
        yield


def make_setting(**overrides):
    setting = {
        "EVENT_COLLECTION_SETTINGS_ID": "dummy-id",
        "EVENT_COLLECTION_SETTINGS_NAME": "dummy-name",
        "REQUEST_METHOD_ID": "1",
        "PORT": "", "PROXY": "", "AUTH_TOKEN": "secret-token-123", "USERNAME": "", "PASSWORD": "",
        "ACCESS_KEY_ID": "", "SECRET_ACCESS_KEY": "", "MAILBOXNAME": "",
        "LAST_FETCHED_TIMESTAMP": 0, "SAVED_IDS": None,
        "RESPONSE_LIST_FLAG": False, "RESPONSE_KEY": "", "EVENT_ID_KEY": "",
        "URL": "https://example.com/", "REQUEST_HEADER": "{}", "PARAMETER": "",
    }
    setting.update(overrides)
    return setting


def ssti_payload(marker):
    return "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker


@pytest.mark.parametrize("field", ["URL", "REQUEST_HEADER", "PARAMETER"])
def test_ssti_is_blocked_in_each_field(field, tmp_path):
    """URL/REQUEST_HEADER/PARAMETERいずれのフィールドでもSSTIが実行されない"""
    marker = tmp_path / "marker.txt"
    payload = ssti_payload(marker)

    client = APIClientCommon(make_setting(**{field: payload}), last_fetched_event=None)

    assert not marker.exists()
    # レンダリング失敗時は元の文字列にフォールバックし、エラーがログに記録される
    assert any("TEMPLATE RENDERING ERROR" in m and "unsafe" in m for m in g.applogger.info_messages)
    if field == "URL":
        assert client.url == payload


def test_legitimate_templates_still_work():
    """予約変数・フィルタ・日時メソッドを使う正規のテンプレートは従来通りレンダリングされる"""
    setting = make_setting(
        URL="https://example.com/?token={{ EXASTRO_EVENT_COLLECTION_SETTING.AUTH_TOKEN | urlencode }}"
            "&host={{ EXASTRO_LAST_FETCHED_EVENT.labels.host }}"
            "&y={{ EXASTRO_CURRENT_TIME.strftime('%Y') }}",
    )
    last_event = {"labels": {"host": "server01"}, "_exastro_oase_event_id": "evt-1"}

    client = APIClientCommon(setting, last_fetched_event=last_event)

    assert client.url.startswith("https://example.com/?token=secret-token-123&host=server01&y=")
    assert not any("TEMPLATE RENDERING ERROR" in m for m in g.applogger.info_messages)


def test_underscore_dict_key_is_accessible():
    """_始まりの辞書キー(_exastro_oase_event_id)はサンドボックス化後も参照できる"""
    setting = make_setting(URL="https://example.com/{{ EXASTRO_LAST_FETCHED_EVENT._exastro_oase_event_id }}")

    client = APIClientCommon(setting, last_fetched_event={"_exastro_oase_event_id": "evt-123"})

    assert client.url == "https://example.com/evt-123"
