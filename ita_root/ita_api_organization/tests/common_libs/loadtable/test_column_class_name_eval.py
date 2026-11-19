#   Copyright 2026 NEC Corporation
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
"""
loadTable.set_columnclass のユニットテスト(COLUMN_CLASS_NAME 経路)

T_COMN_COLUMN_CLASS.COLUMN_CLASS_NAME の値は、現状
    eval('{}(self.objdbca,self.objtable,rest_key,cmd_type)'.format(値))
に検証なしで埋め込まれる。マスタデータだが、公開IF(MCP/REST)だけで書き換えられる経路を確認した。
  1. ワークスペース管理者ロールに Menu-Column link list(10204)の保守権限を付与する(Role-Menu link list)
  2. Menu-Table link list(10203)で 10204 の row_update_flag を True にする
  3. 10204 で任意メニューの列の COL_NAME を COLUMN_CLASS_ID / COLUMN_CLASS_NAME に付け替え、
     SAVE_TYPE(db_storage_format)を空にする
  4. 10203 でそのメニューの table_name を T_COMN_COLUMN_CLASS に変更する
  5. そのメニューの更新で COLUMN_CLASS_NAME に任意の文字列(識別子でない式 'SingleTextColumn.__mro__' を含む)を
     保存できることを確認した(SingleTextColumn の長さ制限以外に検証はない)
上記は管理者権限が前提で、実際の式の評価(コード実行)までは確認していない。
BEFORE_VALIDATE_REGISTER と同じ種類の問題として、期待する挙動を固定する。

期待する挙動:
  - 既知のカラムクラス名だけがインスタンス化される
  - それ以外(式、属性アクセス、呼び出し、組み込み関数名、ダンダー名)は評価せず、
    ValueError で拒否するか、TextColumn に置き換える(未設定時と同じ扱い)
  - いずれの場合も、設定値の式の副作用は起きない

対策を入れる前は TestRejectsNonClassName が失敗する(意図したRed)。

実行: cd ita_root/ita_api_organization && python3 -m pytest tests/common_libs/loadtable/test_column_class_name_eval.py
"""
import sys

import pytest

from common_libs import column as column_module
from common_libs.column.column_class import Column
from common_libs.loadtable.load_table import COLINFO, loadTable

MARKER = "_bvr_class_eval_marker"
REST_KEY = "k"


class _Recorded(Column):
    """DBに接続しないカラムクラスの代役"""

    def __init__(self, objdbca, objtable, rest_key_name, cmd_type=""):  # noqa: super().__init__ は意図的に呼ばない
        self.rest_key_name = rest_key_name


class _FakeTextColumn(_Recorded):
    pass


class _FakeSingleTextColumn(_Recorded):
    pass


class _FakeTable(loadTable):
    """DBに接続せず、COLUMN_CLASS_NAME だけを差し込めるloadTable"""

    def __init__(self, class_name):  # noqa: super().__init__ は意図的に呼ばない
        self._class_name = class_name
        self.objdbca = object()
        self.objtable = {COLINFO: {REST_KEY: {}}}

    def get_col_class_name(self, rest_key):
        return self._class_name

    def objcolumn(self):
        return self.objtable[COLINFO][REST_KEY].get("objcolumn")


@pytest.fixture(autouse=True)
def fake_column_classes(monkeypatch):
    monkeypatch.setattr(column_module, "TextColumn", _FakeTextColumn)
    monkeypatch.setattr(column_module, "SingleTextColumn", _FakeSingleTextColumn)
    sys.modules.pop(MARKER, None)
    yield
    sys.modules.pop(MARKER, None)


class TestKnownClassName:
    def test_known_class_is_instantiated(self):
        t = _FakeTable("SingleTextColumn")
        t.set_columnclass(REST_KEY, "")
        assert type(t.objcolumn()) is _FakeSingleTextColumn

    def test_null_falls_back_to_text_column(self):
        t = _FakeTable(None)
        t.set_columnclass(REST_KEY, "")
        assert type(t.objcolumn()) is _FakeTextColumn

    def test_unknown_identifier_falls_back_to_text_column(self):
        """識別子だが存在しないクラス名は、従来どおり TextColumn になる"""
        t = _FakeTable("NoSuchColumn")
        t.set_columnclass(REST_KEY, "")
        assert type(t.objcolumn()) is _FakeTextColumn


# カラムクラス名ではない設定値。いずれも評価されずに拒否(または TextColumn 化)されるべき
NON_CLASS_NAME_CONFIGS = [
    pytest.param("SingleTextColumn.__mro__", id="attribute-access"),
    pytest.param("__import__", id="dunder-import"),
    pytest.param("__class__", id="dunder-class"),
    pytest.param("print", id="builtin-function"),
    pytest.param("len", id="builtin-len"),
    pytest.param("SingleTextColumn; TextColumn", id="statement-separator"),
    pytest.param("SingleTextColumn if 1 else TextColumn", id="conditional-expression"),
    pytest.param("1Column", id="leading-digit"),
    pytest.param(
        "__import__('sys').modules.setdefault('%s', 1) or TextColumn" % MARKER,
        id="side-effect-expression",
    ),
]


@pytest.mark.parametrize("config", NON_CLASS_NAME_CONFIGS)
class TestRejectsNonClassName:
    """カラムクラス名以外の設定値は、式として評価されない"""

    def test_rejected_without_evaluation(self, config):
        t = _FakeTable(config)
        try:
            t.set_columnclass(REST_KEY, "")
        except ValueError:
            pass  # 例外による拒否
        else:
            # TextColumn への置き換えは許容。式の評価結果(None や 1 など)は不可
            assert type(t.objcolumn()) is _FakeTextColumn, "式が評価された: %r" % config
        assert MARKER not in sys.modules, "式の副作用が実行された"
