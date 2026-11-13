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
loadTable.exec_menu_before_validate / exec_menu_after_validate のユニットテスト

メニュー定義(T_COMN_MENU_TABLE_LINK)の BEFORE_VALIDATE_REGISTER /
AFTER_VALIDATE_REGISTER の値は、検証なしで
    eval('exec_func.{}(self.objdbca, self.objtable, target_option)'.format(値))
に埋め込まれる(2026-10 時点)。DBに接続せずに、期待する挙動を検証する。

期待する挙動(対策: 値を識別子として検証し、getattr で関数を取得する):
  - 関数名(英数字とアンダースコアの識別子、先頭は英字)だけを受け付ける
  - それ以外(式、属性アクセス、呼び出し、ダンダー名)は評価せずに拒否する
    拒否の形は ValueError の送出、または (False, msg, option) の戻りのどちらでもよい
  - 拒否時は検証用関数が呼ばれず、式の副作用も起きない

対策を入れる前は TestRejectsNonIdentifier が失敗する(意図したRed)。

実環境(ws1)での確認結果:
  - null                : 登録成功
  - nonexistent_func    : AttributeError (module has no attribute) -> 999-99999
  - __name__.__len__    : TypeError (expected 0 arguments, got 3)  -> 999-99999
  - 10203(メニュー-テーブル紐付管理)の更新権限があれば API から任意の文字列を設定できる

実行: cd ita_root/ita_api_organization && python3 -m pytest tests/common_libs/loadtable/test_before_validate_register_eval.py
"""
import importlib
import sys
import types

import pytest

from common_libs.loadtable.load_table import loadTable

VALID_PATH_CMDB = "common_libs.validate.valid_cmdb_menu"
VALID_PATH_MENU = "common_libs.validate.valid_99999"

OPTION = {"entry_parameter": {"parameter": {}}}


class _FakeTable(loadTable):
    """DBに接続せず、設定値とシートタイプだけを差し込めるloadTable"""

    def __init__(self, config, sheet_type="2", menu_id="99999"):  # noqa: super().__init__ は意図的に呼ばない
        self._config = config
        self._sheet_type = sheet_type
        self._menu_id = menu_id
        self.objdbca = object()
        self.objtable = {}

    def get_menu_before_validate_register(self):
        return self._config

    def get_menu_after_validate_register(self):
        return self._config

    def get_sheet_type(self):
        return self._sheet_type

    def get_menu_id(self):
        return self._menu_id


@pytest.fixture
def fake_validate_module(monkeypatch):
    """valid_<menu_id> / valid_cmdb_menu を差し替え、呼び出し引数を記録する"""
    calls = []

    def make(path):
        mod = types.ModuleType(path)

        def ok(objdbca, objtable, option):
            calls.append((path, "ok"))
            option = dict(option, touched=True)
            return True, "", option

        def ng(objdbca, objtable, option):
            calls.append((path, "ng"))
            return False, "rejected", option

        mod.ok = ok
        mod.ng = ng
        mod.ONE = 1
        monkeypatch.setitem(sys.modules, path, mod)
        return mod

    make(VALID_PATH_CMDB)
    make(VALID_PATH_MENU)
    return calls


EXEC_METHODS = ["exec_menu_before_validate", "exec_menu_after_validate"]


@pytest.mark.parametrize("method", EXEC_METHODS)
class TestExecMenuValidate:
    def test_null_is_skipped(self, method, fake_validate_module):
        """未設定(null)なら何も呼ばれず、optionはそのまま返る"""
        t = _FakeTable(None)
        ret, msg, option = getattr(t, method)(OPTION)
        assert ret is True and msg == "" and option is OPTION
        assert fake_validate_module == []

    def test_function_name_is_called(self, method, fake_validate_module):
        """関数名なら対応モジュールの関数が呼ばれ、戻り値のoptionが使われる"""
        t = _FakeTable("ok", sheet_type="0", menu_id="99999")
        ret, msg, option = getattr(t, method)(OPTION)
        assert ret is True
        assert option["touched"] is True
        assert fake_validate_module == [(VALID_PATH_MENU, "ok")]

    @pytest.mark.parametrize("sheet_type", ["1", "2", "3", "4"])
    def test_module_selection_by_sheet_type(self, method, sheet_type, fake_validate_module):
        """シートタイプ1~4はvalid_cmdb_menu、それ以外はvalid_<menu_id>"""
        # 注: 現状の実装は '2'(データシート)も valid_cmdb_menu を使う
        t = _FakeTable("ok", sheet_type=sheet_type)
        getattr(t, method)(OPTION)
        assert fake_validate_module == [(VALID_PATH_CMDB, "ok")]

    def test_other_sheet_type_uses_menu_module(self, method, fake_validate_module):
        t = _FakeTable("ok", sheet_type="0", menu_id="99999")
        getattr(t, method)(OPTION)
        assert fake_validate_module == [(VALID_PATH_MENU, "ok")]

    def test_validation_failure_is_propagated(self, method, fake_validate_module):
        t = _FakeTable("ng", sheet_type="0")
        ret, msg, option = getattr(t, method)(OPTION)
        assert ret is False and msg == "rejected"

    def test_unknown_function_raises_attribute_error(self, method, fake_validate_module):
        """存在しない関数名は AttributeError(利用者には 999-99999 として見える)"""
        t = _FakeTable("nonexistent_func", sheet_type="0")
        with pytest.raises(AttributeError, match="nonexistent_func"):
            getattr(t, method)(OPTION)


# 関数名ではない設定値。いずれも評価・呼び出しされずに拒否されるべき
MARKER = "_bvr_eval_marker"
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
        "ok(None, None, target_option) if __import__('sys').modules.setdefault('%s', 1) else ok" % MARKER,
        id="side-effect-expression",
    ),
]


@pytest.mark.parametrize("method", EXEC_METHODS)
@pytest.mark.parametrize("config", NON_IDENTIFIER_CONFIGS)
class TestRejectsNonIdentifier:
    """関数名以外の設定値は、評価も呼び出しもされずに拒否される"""

    def test_rejected_without_evaluation(self, method, config, fake_validate_module):
        sys.modules.pop(MARKER, None)
        t = _FakeTable(config, sheet_type="0")
        try:
            try:
                ret, msg, option = getattr(t, method)(OPTION)
            except ValueError:
                pass  # 例外による拒否
            else:
                assert ret is False, "式が受理された: %r" % config  # 戻り値による拒否
            assert fake_validate_module == [], "検証用関数が呼ばれた"
            assert MARKER not in sys.modules, "式の副作用が実行された"
        finally:
            sys.modules.pop(MARKER, None)
