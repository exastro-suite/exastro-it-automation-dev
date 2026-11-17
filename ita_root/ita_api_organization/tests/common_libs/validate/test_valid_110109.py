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
ルール(メニューID 110109)の通知テンプレートファイル(事前通知・事後通知)の検証のテスト

事後通知(after_notification)は、検証対象のファイルパスを誤ったキーで参照していたため、
ファイルの検証が一切行われていなかった。事前・事後の両方が同じように検証されることを確認する。
"""
import pytest
from flask import Flask, g

from common_libs.validate.valid_110109 import external_valid_menu_before

app = Flask(__name__)

SSTI = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"


class DummyAppMsg:
    def get_api_message(self, code, args=None):
        return f"{code} {args or ''}".strip()


class DummyLogger:
    def __getattr__(self, name):
        return lambda *a, **k: None


class DummyDb:
    def sql_execute(self, sql, params=None):
        return [{"COL_GROUP_NAME_JA": "通知", "COL_GROUP_NAME_EN": "Notification"}]


@pytest.fixture(autouse=True)
def setup_g():
    with app.app_context():
        g.appmsg = DummyAppMsg()
        g.applogger = DummyLogger()
        g.LANGUAGE = "ja"
        yield


@pytest.fixture
def objtable():
    return {"COLINFO": {
        key: {"COLUMN_NAME_JA": "通知", "COLUMN_NAME_EN": "Notification", "COL_GROUP_ID": "1"}
        for key in ("before_notification", "after_notification")
    }}


def run(objtable, tmp_path, column, content):
    """指定したカラム(事前/事後)に、テンプレートファイルをアップロードして登録する場合の検証結果を返す"""
    path = tmp_path / "template.j2"
    if isinstance(content, str):
        content = content.encode("utf-8")
    path.write_bytes(content)

    parameter = {
        "filter_a": "f1", "filter_b": None, "filter_operator": None,
        "rule_label_name": "rule", "action_id": "a1",
        column: "template.j2",
    }
    option = {
        "cmd_type": "Register",
        "entry_parameter": {"parameter": parameter, "file_path": {column: str(path)}},
        "current_parameter": {"parameter": {"rule_label_name": "rule"}, "file_path": {}},
    }
    return external_valid_menu_before(DummyDb(), objtable, option)


@pytest.fixture(params=["before_notification", "after_notification"])
def column(request):
    return request.param


def test_valid_template_is_accepted(objtable, tmp_path, column):
    ok, msg, _ = run(objtable, tmp_path, column, "[TITLE]\n{{ _id }}\n[BODY]\nhost={{ labels.host }}\n")

    assert ok is True


@pytest.mark.parametrize("name, content", [
    ("SSTI(本文のみ)", "[TITLE]\n__external_url__\n[BODY]\n" + SSTI + "\n"),
    ("標準テンプレートの形+末尾にSSTI", "[TITLE]\n{{ labels._exastro_type }}\n[BODY]\n{{ labels.host }}\n" + SSTI + "\n"),
    ("構文エラー", "[TITLE]\nt\n[BODY]\n{% if x %}\n"),
])
def test_invalid_jinja2_is_rejected(objtable, tmp_path, column, name, content):
    """事前・事後のどちらでも、jinja2として不正なファイルは499-01815で拒否される"""
    ok, msg, _ = run(objtable, tmp_path, column, content)

    assert ok is False
    assert any("499-01815" in m for m in msg)


def test_missing_title_or_body_is_rejected(objtable, tmp_path, column):
    """事前・事後のどちらでも、[TITLE]/[BODY]の過不足は拒否される(従来の検証も事後で動くこと)"""
    ok, msg, _ = run(objtable, tmp_path, column, "[TITLE]\nt\n")

    assert ok is False
    assert any("499-01817" in m for m in msg)
