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
実行環境定義テンプレート管理(メニューID 20110)の、テンプレートファイル検証のテスト

アップロードされたjinja2は、保存時の検証でも評価される。
サンドボックスなしで評価すると、アップロードした時点で任意コードが実行されてしまう(SSTI)ため、
サンドボックス内で評価され、危険な記述は拒否されることを確認する。
"""
import pytest
from flask import Flask, g

from common_libs.validate.valid_20110 import external_valid_menu_before

app = Flask(__name__)


class DummyAppMsg:
    def get_api_message(self, code, args=None):
        return f"{code} {args}"


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


OBJTABLE = {"COLINFO": {"template_file": {"COLUMN_NAME_JA": "テンプレートファイル", "COLUMN_NAME_EN": "Template file"}}}


def validate(tmp_path, content, cmd_type="Register", use_current=False):
    """テンプレートを保存する場合の検証結果を返す。use_current=Trueなら、ファイルを変えない更新(既存ファイルの再検証)"""
    path = tmp_path / "template.j2"
    path.write_text(content, encoding="utf-8")
    entry = {} if use_current else {"template_file": str(path)}
    current = {"template_file": str(path)} if use_current else {}
    option = {
        "cmd_type": cmd_type,
        "entry_parameter": {"file_path": entry},
        "current_parameter": {"file_path": current},
    }
    return external_valid_menu_before(None, OBJTABLE, option)


def ssti(marker):
    return "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker


@pytest.mark.parametrize("content", [
    "FROM {{ base_image | default('x') }}\nRUN echo {{ name | default('a') }}\n",
    "{% for i in [1, 2] %}{% if i > 1 %}x{{ i }}{% endif %}{% endfor %}\n",
    "固定の文字列のみ\n",
])
def test_valid_template_is_accepted(tmp_path, content):
    ok, msg, _ = validate(tmp_path, content)

    assert ok is True


def test_ssti_is_rejected_and_not_executed(tmp_path):
    """SSTIは保存時の検証で拒否され、検証中にコマンドが実行されない"""
    marker = tmp_path / "marker.txt"

    ok, msg, _ = validate(tmp_path, "FROM x\n" + ssti(marker) + "\n")

    assert ok is False
    assert msg.startswith("MSG-10980")
    assert not marker.exists()


def test_ssti_after_failing_expression_is_rejected(tmp_path):
    """先にエラーになる式があっても、後ろのSSTIが実行・見逃されない"""
    marker = tmp_path / "marker.txt"

    ok, msg, _ = validate(tmp_path, "{{ 1/0 }}\n" + ssti(marker) + "\n")

    assert ok is False
    assert not marker.exists()


def test_ssti_in_unreachable_branch_is_rejected(tmp_path):
    """実行されない分岐に書かれたSSTIも、静的検査で拒否される(実行時に評価されるのを防ぐ)"""
    ok, msg, _ = validate(tmp_path, "{% if false %}{{ ''.__class__.__mro__ }}{% endif %}\n")

    assert ok is False
    assert msg.startswith("MSG-10980")


def test_syntax_error_is_still_rejected(tmp_path):
    """従来の検証(構文エラーの拒否)は維持される"""
    ok, msg, _ = validate(tmp_path, "{% if x %}\n")

    assert ok is False
    assert msg.startswith("MSG-10980")


def test_existing_file_is_revalidated_on_update_without_new_file(tmp_path):
    """更新でファイルを渡さない場合、既存のファイル(current_parameter側)が検証される(従来の仕様)"""
    marker = tmp_path / "marker.txt"

    ok, msg, _ = validate(tmp_path, ssti(marker), cmd_type="Update", use_current=True)

    assert ok is False
    assert not marker.exists()


def test_include_in_same_directory_still_works(tmp_path):
    """{% include %}で同じディレクトリのファイルを読む従来の挙動は維持される"""
    (tmp_path / "part.j2").write_text("PART {{ v | default('d') }}\n", encoding="utf-8")

    ok, msg, _ = validate(tmp_path, "{% include 'part.j2' %}\n")

    assert ok is True


def test_delete_is_not_validated(tmp_path):
    """削除の場合はテンプレートの検証をしない(従来の仕様)"""
    ok, msg, _ = validate(tmp_path, "{% if x %}\n", cmd_type="Delete")

    assert ok is True
