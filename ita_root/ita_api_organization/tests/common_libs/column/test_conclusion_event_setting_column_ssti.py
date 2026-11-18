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
Jinja2 SSTI対策: 結論ラベル設定(ConclusionEventSettingColumn)の保存時バリデーションのテスト
"""
import pytest
from flask import Flask, g

from common_libs.column.conclusion_event_dialog_column import ConclusionEventSettingColumn

app = Flask(__name__)


class DummyAppMsg:
    def get_api_message(self, code, args=None):
        return f"{code} {args}"


COLUMN_NAME_JA = "結論ラベル設定"
COLUMN_NAME_EN = "Conclusion Label Settings"


class DummyLogger:
    def __getattr__(self, name):
        return lambda *a, **k: None


@pytest.fixture(autouse=True)
def setup_g():
    with app.app_context():
        g.appmsg = DummyAppMsg()
        g.applogger = DummyLogger()
        g.LANGUAGE = "ja"
        yield


@pytest.fixture
def column():
    # DB接続を伴う__init__は呼ばず、ラベルマスタのみ差し替える
    col = ConclusionEventSettingColumn.__new__(ConclusionEventSettingColumn)
    col.search_id_data_list = lambda: {"uuid-1": "result_label"}
    # 項目名(多言語)はカラム定義から取得するため、最小限の定義を持たせる
    col.objtable = {"COLINFO": {"conclusion_label_settings": {
        "COLUMN_NAME_JA": COLUMN_NAME_JA, "COLUMN_NAME_EN": COLUMN_NAME_EN, "COLUMN_NAME_REST": "conclusion_label_settings"}}}
    col.rest_key_name = "conclusion_label_settings"
    return col


@pytest.mark.parametrize("label_value", [
    "True",
    "{{ A.host }}",
    "host={{ A.host }} rule={{ A._exastro_rule_name }}",
    "{% if A.x %}y{% else %}n{% endif %}",
])
def test_valid_label_value_is_accepted(column, label_value):
    ret, msg, result = column.get_input_values_by_value(["result_label", label_value])

    assert ret is True
    assert msg is None
    assert result == {"label_key": "uuid-1", "label_value": label_value}


@pytest.mark.parametrize("label_value", [
    "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}",
    "{{ ''.__class__.mro() }}",
    "{{ '{0.__class__.__mro__[1].__subclasses__}'.format(42) }}",
    "{{ A.__class__.__base__.__subclasses__() }}",
])
def test_ssti_label_value_is_rejected(column, label_value):
    """SSTIペイロードは保存時に499-01711で拒否され、label_valueは結果に含まれない"""
    ret, msg, result = column.get_input_values_by_value(["result_label", label_value])

    assert ret is False
    assert msg == f"499-01711 ['{COLUMN_NAME_JA}']"
    assert "label_value" not in result


def test_syntax_error_label_value_is_rejected(column):
    ret, msg, result = column.get_input_values_by_value(["result_label", "{{ A. }}"])

    assert ret is False
    assert msg.startswith("499-01711")


def test_existing_checks_still_work(column):
    """既存のチェック(必須・文字列型)は従来通り動作する"""
    # 値が空
    ret, msg, _ = column.get_input_values_by_value(["result_label", ""])
    assert ret is False and msg.startswith("499-01707")
    # 文字列以外
    ret, msg, _ = column.get_input_values_by_value(["result_label", 123])
    assert ret is False and msg.startswith("MSG-00032")
    # 存在しないラベル
    ret, msg, _ = column.get_input_values_by_value(["unknown_label", "x"])
    assert ret is False and msg.startswith("MSG-00032")


@pytest.mark.parametrize("language, expected_name", [("ja", COLUMN_NAME_JA), ("en", COLUMN_NAME_EN)])
def test_item_name_in_message_follows_language(column, language, expected_name):
    """エラーメッセージの項目名は、現在の言語のカラム名になる(日本語固定ではない)"""
    g.LANGUAGE = language

    ret, msg, _ = column.get_input_values_by_value(["result_label", "{{ A. }}"])

    assert ret is False
    assert msg == f"499-01711 ['{expected_name}']"
