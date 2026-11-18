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
Jinja2 SSTI対策: 保存時バリデーション(is_jinja2_template)のテスト

対象:
    - common_libs.validate.valid_110101.is_jinja2_template (イベント収集設定)
    - common_libs.notification.validator.is_jinja2_template (通知テンプレート/アクション)
"""
import pytest
from flask import Flask, g

from common_libs.validate.valid_110101 import is_jinja2_template as is_jinja2_template_110101
from common_libs.notification.validator import is_jinja2_template as is_jinja2_template_notification

app = Flask(__name__)


class DummyLogger:
    def __getattr__(self, name):
        return lambda *a, **k: None


@pytest.fixture(autouse=True)
def setup_g():
    with app.app_context():
        # print_exception_msgがg.apploggerを参照するため
        g.applogger = DummyLogger()
        yield


@pytest.fixture(params=[is_jinja2_template_110101, is_jinja2_template_notification],
                ids=["valid_110101", "notification.validator"])
def is_jinja2_template(request):
    return request.param


# 正規利用パターン(誤検知しないこと)
VALID_TEMPLATES = [
    ("固定文字列", "True"),
    ("空文字", ""),
    ("予約変数のネストdict参照", "{{ EXASTRO_LAST_FETCHED_EVENT.labels.host }}"),
    ("予約変数のdatetimeメソッド", "{{ EXASTRO_CURRENT_TIME.strftime('%Y-%m-%d') }}"),
    ("予約変数+urlencodeフィルタ", "{{ EXASTRO_EVENT_COLLECTION_SETTING.AUTH_TOKEN | urlencode }}"),
    ("A/Bラベル参照(_始まりの辞書キー含む)", "host={{ A.host }} rule={{ A._exastro_rule_name }}"),
    ("_idの参照", "{{ _id }}"),
    ("labelsの_exastro_*キー(標準テンプレートの形)", "{{ labels._exastro_event_collection_settings_id }}{{ labels._exastro_fetched_time }}"),
    ("辞書の添字アクセス", "{{ labels['host'] }}"),
    ("if制御構文", "{% if A.x %}y{% endif %}"),
    ("forループ", "{% for k in ['a','b'] %}{{ k }}{% endfor %}"),
    ("文字列操作", "{{ 'abc-def'.split('-') | join('_') | upper }}"),
    ("tojsonフィルタ", "{{ {'a': 1} | tojson }}"),
    ("format()", "{{ '{}-{}'.format('a', 'b') }}"),
]

# 構文エラー
SYNTAX_ERROR_TEMPLATES = [
    ("属性名なし", "{{ A. }}"),
    ("閉じ忘れ", "{{ my_var "),
    ("制御構文の閉じタグなし", "{% if value %}True"),
]

# SSTI(サンドボックスで遮断されるべきもの)
MALICIOUS_TEMPLATES = [
    ("self経由のRCE", "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"),
    ("__class__.mro", "{{ ''.__class__.mro() }}"),
    ("__class__.__mro__.__subclasses__", "{{ ''.__class__.__mro__[1].__subclasses__() }}"),
    ("str.format()経由のバイパス", "{{ '{0.__class__.__mro__[1].__subclasses__}'.format(42) }}"),
    ("未定義の予約変数を踏み台にする", "{{ EXASTRO_LAST_FETCHED_EVENT.__class__.__base__.__subclasses__() }}"),
    ("制御構文内のSSTI", "{% if self.__init__.__globals__ %}x{% endif %}"),
    ("単一アンダースコアの属性アクセス", "{{ ''.__class__ }}{{ ''.__class__.__name__ }}"),
    # 先に評価がエラーになる式があっても、後ろのSSTIを見逃さない（レンダリングは最初のエラーで止まるため静的検査が必要）
    ("前に未定義変数の属性参照(標準テンプレートの形)+SSTI", "{{ labels._exastro_type }}\n{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"),
    ("前にlabels.host+SSTI", "{{ labels.host }}\n{{ ''.__class__.__mro__[1].__subclasses__() }}"),
    ("前にゼロ除算+SSTI", "{{ 1/0 }}\n{{ ''.__class__ }}"),
    ("前にtojson失敗+SSTI", "{{ x | tojson }}\n{{ ''.__class__ }}"),
    ("attrフィルタ", "{{ 1/0 }}{{ ''|attr('__class__') }}"),
    ("添字によるアクセス", "{{ 1/0 }}{{ ''['__class__'] }}"),
    ("名前修飾された内部属性", "{{ 1/0 }}{{ self._TemplateReference__context }}"),
    ("前にエラー+制御構文内のSSTI", "{{ 1/0 }}{% for c in ''.__class__.__mro__ %}{{ c }}{% endfor %}"),
]


@pytest.mark.parametrize("name, template", VALID_TEMPLATES, ids=[n for n, _ in VALID_TEMPLATES])
def test_valid_templates_are_accepted(is_jinja2_template, name, template):
    """正規のテンプレートは誤検知されずTrueになる"""
    assert is_jinja2_template(template) is True


@pytest.mark.parametrize("name, template", SYNTAX_ERROR_TEMPLATES, ids=[n for n, _ in SYNTAX_ERROR_TEMPLATES])
def test_syntax_errors_are_rejected(is_jinja2_template, name, template):
    """構文エラーはFalseになる"""
    assert is_jinja2_template(template) is False


@pytest.mark.parametrize("name, template", MALICIOUS_TEMPLATES, ids=[n for n, _ in MALICIOUS_TEMPLATES])
def test_ssti_payloads_are_rejected(is_jinja2_template, name, template):
    """SSTIペイロードは保存時にFalseとなり拒否される"""
    assert is_jinja2_template(template) is False


def test_none_is_rejected(is_jinja2_template):
    """Noneは不正(従来の挙動を維持)"""
    assert is_jinja2_template(None) is False


def test_ssti_payload_is_not_executed_during_validation(is_jinja2_template, tmp_path):
    """検証(render)中にペイロードが実行されないこと(マーカーファイルが作られない)"""
    marker = tmp_path / "marker.txt"
    payload = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id > %s').read() }}" % marker

    assert is_jinja2_template(payload) is False
    assert not marker.exists()


def test_standard_notification_templates_are_accepted(is_jinja2_template):
    """リポジトリ同梱の標準通知テンプレートが、新しい静的検査で誤検知されないこと"""
    import glob
    import os
    root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    files = glob.glob(os.path.join(root, "ita_api_admin", "files", "110102", "*.j2"))
    assert files, "標準テンプレートが見つからない"
    for path in files:
        with open(path, encoding="utf-8") as f:
            assert is_jinja2_template(f.read()) is True, path


def test_appended_ssti_to_standard_template_is_rejected(is_jinja2_template):
    """標準テンプレートの末尾にSSTIを追記したものは拒否される（編集で追記するケース）"""
    import glob
    import os
    root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
    path = glob.glob(os.path.join(root, "ita_api_admin", "files", "110102", "*.j2"))[0]
    with open(path, encoding="utf-8") as f:
        body = f.read()

    payload = "{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}"

    assert is_jinja2_template(body + "\n" + payload) is False
