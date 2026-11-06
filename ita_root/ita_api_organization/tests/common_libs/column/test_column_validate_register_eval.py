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
Column.before_iud_col_action / after_iud_col_action のユニットテスト(カラム単位)

カラム定義(T_COMN_MENU_COLUMN_LINK)の BEFORE_VALIDATE_REGISTER /
AFTER_VALIDATE_REGISTER の値は、現状
    eval('exec_func.{}(self.objdbca, self.objtable, option)'.format(値))
に検証なしで埋め込まれる。メニュー単位(test_before_validate_register_eval.py)と同じ問題。

期待する挙動:
  - 関数名(先頭は英字、英数字とアンダースコア)だけを受け付ける
  - それ以外(式、属性アクセス、呼び出し、ダンダー名)は評価せずに拒否する
    拒否の形は ValueError の送出、または (False, msg, option) の戻りのどちらでもよい
  - 拒否時は検証用関数が呼ばれず、式の副作用も起きない

対策を入れる前は TestRejectsNonIdentifier が失敗する(意図したRed)。

実行: cd ita_root/ita_api_organization && python3 -m pytest tests/common_libs/column/test_column_validate_register_eval.py
"""
import sys
import types

import pytest

from common_libs.column.column_class import Column

VALID_PATH_CMDB = "common_libs.validate.valid_cmdb_menu"
VALID_PATH_MENU = "common_libs.validate.valid_99999"

OPTION = {"entry_parameter": {"parameter": {}}}

MARKER = "_bvr_col_eval_marker"


class _FakeColumn(Column):
    """DBに接続せず、設定値とシートタイプだけを差し込めるColumn"""

    def __init__(self, config, sheet_type="2", menu="99999"):  # noqa: super().__init__ は意図的に呼ばない
        self._config = config
        self._sheet_type = sheet_type
        self._menu = menu
        self.objdbca = object()
        self.objtable = {}

    def get_call_before_valid_info(self):
        return self._config

    def get_call_after_valid_info(self):
        return self._config

    def get_sheet_type(self):
        return self._sheet_type

    def get_menu(self):
        return self._menu


def _before(col, option):
    return col.before_iud_col_action(option)


def _after(col, option):
    return col.after_iud_col_action("", option)


RUNNERS = [
    pytest.param(_before, id="before_iud_col_action"),
    pytest.param(_after, id="after_iud_col_action"),
]


@pytest.fixture
def fake_validate_module(monkeypatch):
    """valid_<menu> / valid_cmdb_menu を差し替え、呼び出しを記録する"""
    calls = []

    def make(path):
        mod = types.ModuleType(path)

        def ok(objdbca, objtable, option):
            calls.append((path, "ok"))
            return True, "", dict(option, touched=True)

        def ng(objdbca, objtable, option):
            calls.append((path, "ng"))
            return False, "rejected", option

        mod.ok = ok
        mod.ng = ng
        mod.ONE = 1
        monkeypatch.setitem(sys.modules, path, mod)

    make(VALID_PATH_CMDB)
    make(VALID_PATH_MENU)
    return calls


@pytest.mark.parametrize("run", RUNNERS)
class TestColumnExecValidate:
    def test_null_is_skipped(self, run, fake_validate_module):
        ret, msg, option = run(_FakeColumn(None), OPTION)
        assert ret is True and msg == "" and option is OPTION
        assert fake_validate_module == []

    def test_function_name_is_called(self, run, fake_validate_module):
        ret, msg, option = run(_FakeColumn("ok", sheet_type="0"), OPTION)
        assert ret is True
        assert option["touched"] is True
        assert fake_validate_module == [(VALID_PATH_MENU, "ok")]

    @pytest.mark.parametrize("sheet_type", ["1", "2", "3", "4"])
    def test_module_selection_by_sheet_type(self, run, sheet_type, fake_validate_module):
        run(_FakeColumn("ok", sheet_type=sheet_type), OPTION)
        assert fake_validate_module == [(VALID_PATH_CMDB, "ok")]

    def test_validation_failure_is_propagated(self, run, fake_validate_module):
        ret, msg, option = run(_FakeColumn("ng", sheet_type="0"), OPTION)
        assert ret is False and msg == "rejected"

    def test_unknown_function_raises_attribute_error(self, run, fake_validate_module):
        with pytest.raises(AttributeError, match="nonexistent_func"):
            run(_FakeColumn("nonexistent_func", sheet_type="0"), OPTION)


# 関数名ではない設定値。いずれも評価・呼び出しされずに拒否されるべき
NON_IDENTIFIER_CONFIGS = [
    pytest.param("ONE.__class__", id="attribute-access"),
    pytest.param("ok.__call__", id="attribute-of-function"),
    pytest.param("__name__", id="dunder-name"),
    pytest.param("__class__", id="dunder-class"),
    pytest.param("ok; ok", id="statement-separator"),
    pytest.param("ok(None, None, None)", id="call-expression"),
    pytest.param("ok or ng", id="boolean-expression"),
    pytest.param("ok if 1 else ng", id="conditional-expression"),
    pytest.param("1ok", id="leading-digit"),
    pytest.param(
        "ok(None, None, option) if __import__('sys').modules.setdefault('%s', 1) else ok" % MARKER,
        id="side-effect-expression",
    ),
]


@pytest.mark.parametrize("run", RUNNERS)
@pytest.mark.parametrize("config", NON_IDENTIFIER_CONFIGS)
class TestRejectsNonIdentifier:
    """関数名以外の設定値は、評価も呼び出しもされずに拒否される"""

    def test_rejected_without_evaluation(self, run, config, fake_validate_module):
        sys.modules.pop(MARKER, None)
        try:
            try:
                ret, msg, option = run(_FakeColumn(config, sheet_type="0"), OPTION)
            except ValueError:
                pass  # 例外による拒否
            else:
                assert ret is False, "式が受理された: %r" % config  # 戻り値による拒否
            assert fake_validate_module == [], "検証用関数が呼ばれた"
            assert MARKER not in sys.modules, "式の副作用が実行された"
        finally:
            sys.modules.pop(MARKER, None)
