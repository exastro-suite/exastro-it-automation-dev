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
loadTable.exec_menu_before_validate による メニュー定義更新ガードのユニットテスト

メニュー-テーブル紐付管理(10203)、メニュー-カラム紐付管理(10204)、ロール-メニュー紐付管理(10104)の
更新には、参照先テーブル・列対応・権限付与を制限する検証がない。
このため、メニュー定義の更新権限だけで、接続先ワークスペースDB内の任意のテーブルを
メニューの参照先にできる。DBに接続せずに、期待する挙動を検証する。

期待する挙動(編集は許可し、変更後の定義を固定の検証で確認する):
  - 検証は T_COMN_MENU_TABLE_LINK.BEFORE_VALIDATE_REGISTER(10203で編集可能な設定値)に依らず、
    10203/10204/10104 では必ず実行される
  - 10203: table_name / view_name は識別子の形式で、実在し、機微テーブルは所有メニュー以外から指定できない
  - 10204: id_link_table は同様。参照先の列と column_name は対象テーブルに実在する
  - 10104: 自分が属するロールへ、10203/10204/10104 のメンテナンス権限を付与できない
  - 変更していない項目(既存値)は検査しない。業務テーブル間の通常の変更は拒否しない
  - モードは環境変数 MENU_DEF_GUARD_MODE。enforce(既定・未設定時)で拒否し、
    monitor / warn ではガードログのみで通す

対策を入れる前は TestRejectsUnsafeDefinition が失敗する(意図したRed)。
TestAllowsSafeDefinition は対策の前後とも成功する(誤拒否していないことの確認)。

実行: cd ita_root/ita_api_organization && python3 -m pytest tests/common_libs/loadtable/test_menu_definition_guard.py
"""
import glob
import os
import re
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from common_libs.loadtable.load_table import loadTable

SENSITIVE_TABLE = "T_COMN_ROLE_MENU_LINK"


class _FakeTable(loadTable):
    """DBに接続せず、メニューIDと設定値(BEFORE_VALIDATE_REGISTER)だけを差し込めるloadTable"""

    def __init__(self, menu_id, db, config=None):  # noqa: super().__init__ は意図的に呼ばない
        self._menu_id = menu_id
        self._config = config
        self.objdbca = db
        self.objtable = {}

    def get_menu_before_validate_register(self):
        return self._config

    def get_sheet_type(self):
        return "0"

    def get_menu_id(self):
        return self._menu_id


@pytest.fixture
def guard_env(monkeypatch):
    """flask の g(メッセージ・ログ・ユーザ・ロール)を用意し、モード未設定(= enforce)にする"""
    app = Flask(__name__)
    with app.app_context():
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda code, args=None: f"{code}:{args}"
        g.applogger = MagicMock()
        g.USER_ID = "user-1"
        g.ROLES = ["role-own"]
        monkeypatch.delenv("MENU_DEF_GUARD_MODE", raising=False)
        yield


def _option(cmd_type, new, old=None):
    return {
        "uuid": "uuid-1", "cmd_type": cmd_type, "rest_key_name": "", "col_name": "",
        "entry_parameter": {"parameter": new},
        "current_parameter": {"parameter": old or {}},
    }


def _db(table_select=None, sql_execute=None):
    """table_select は呼び出し順の戻り値のリスト、sql_execute は固定の戻り値"""
    db = MagicMock()
    if table_select is not None:
        db.table_select.side_effect = list(table_select)
    db.sql_execute.return_value = sql_execute if sql_execute is not None else []
    return db


# 設定値(BEFORE_VALIDATE_REGISTER)。NULL は検証を外された状態を表す
CONFIGS = [
    pytest.param(None, id="validator-null"),
    pytest.param("some_other_func", id="validator-other"),
]


# 拒否されるべき定義(メニューID, DB, 変更後, 変更前)。いずれも対策前は受理される
UNSAFE = [
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": SENSITIVE_TABLE}]),
        {"table_name": SENSITIVE_TABLE}, {"table_name": "T_CMDB_X"},
        id="10203-table-to-sensitive",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": "V_COMN_ROLE_MENU_LINK"}]),
        {"view_name": "V_COMN_ROLE_MENU_LINK"}, {"view_name": "V_CMDB_X"},
        id="10203-view-to-sensitive",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]]),
        {"view_name": "V_X` UNION SELECT 1 -- "}, {"view_name": "V_X"},
        id="10203-identifier-injection",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], []),
        {"table_name": "T_NOT_EXISTS"}, {"table_name": "T_CMDB_X"},
        id="10203-table-not-exists",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": "T_COMN_WORKSPACE_DB_INFO"}]),
        {"table_name": "T_COMN_WORKSPACE_DB_INFO"}, {"table_name": "T_CMDB_X"},
        id="10203-table-to-deny-list",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "10102"}]], [{"TABLE_NAME": "T_COMN_WORKSPACE_DB_INFO"}]),
        {"table_name": "T_COMN_WORKSPACE_DB_INFO"}, {"table_name": "T_COMN_MENU_GROUP"},
        id="10203-deny-list-has-no-owner-exception",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": "T_CMDB_X_JNL"}]),
        {"table_name": "T_CMDB_X_JNL"}, {"table_name": "T_CMDB_X"},
        id="10203-table-to-history-table",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": "T_COMN_MENU_GROUP"}]),
        {"table_name": "T_COMN_MENU_GROUP"}, {"table_name": "T_CMDB_X"},
        id="10203-table-to-menu-group",
    ),
    pytest.param(
        "10204", lambda: _db([[{"MENU_ID": "20101"}], [{"TABLE_NAME": "T_CMDB_X"}]], []),
        {"column_name": "NOT_EXISTS"}, {"column_name": "DATA_JSON"},
        id="10204-column-not-exists",
    ),
    pytest.param(
        "10204", lambda: _db([[{"MENU_ID": "20101"}], [{"TABLE_NAME": "T_CMDB_X"}]], [{"TABLE_NAME": "T_COMN_SYSTEM_CONFIG"}]),
        {"id_link_table": "T_COMN_SYSTEM_CONFIG"}, {"id_link_table": "T_COMN_BOOLEAN_FLAG"},
        id="10204-ref-table-to-sensitive",
    ),
    pytest.param(
        "10104", lambda: _db([[{"MENU_ID": "10203"}], [{"PRIVILEGES_ID": "1"}]]),
        {"role_name": "role-own", "menu_name": "m", "associate": "1"}, None,
        id="10104-self-grant-10203",
    ),
    pytest.param(
        "10104", lambda: _db([[{"MENU_ID": "10104"}], [{"PRIVILEGES_ID": "1"}]]),
        {"role_name": "role-own", "menu_name": "m", "associate": "1"}, None,
        id="10104-self-grant-10104",
    ),
]


@pytest.mark.usefixtures("guard_env")
@pytest.mark.parametrize("config", CONFIGS)
@pytest.mark.parametrize("menu_id, make_db, new, old", UNSAFE)
class TestRejectsUnsafeDefinition:
    """安全でない定義への更新は、検証の設定値に依らず拒否される"""

    def test_rejected(self, menu_id, make_db, new, old, config):
        t = _FakeTable(menu_id, make_db(), config)
        ret, msg, _ = t.exec_menu_before_validate(_option("Update", new, old))
        assert ret is False, "安全でない定義が受理された (menu=%s, new=%r)" % (menu_id, new)
        assert msg


# 受理されるべき定義。対策の前後とも成功する
SAFE = [
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": "T_CMDB_Y"}]),
        {"table_name": "T_CMDB_Y"}, {"table_name": "T_CMDB_X"},
        id="10203-table-to-business",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "10104"}]], [{"TABLE_NAME": SENSITIVE_TABLE}]),
        {"table_name": SENSITIVE_TABLE}, {"table_name": "T_X"},
        id="10203-owner-menu-keeps-own-table",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "10103"}]], [{"TABLE_NAME": "T_COMN_MENU"}]),
        {"table_name": "T_COMN_MENU"}, {"table_name": "T_X"},
        id="10203-menu-owner-keeps-own-table",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "10101"}]], [{"TABLE_NAME": "T_COMN_SYSTEM_CONFIG"}]),
        {"table_name": "T_COMN_SYSTEM_CONFIG"}, {"table_name": "T_X"},
        id="10203-system-config-owner-keeps-own-table",
    ),
    pytest.param(
        "10203", lambda: _db([[{"MENU_ID": "20101"}]]),
        {"table_name": SENSITIVE_TABLE}, {"table_name": SENSITIVE_TABLE},
        id="10203-unchanged-value-not-checked",
    ),
    pytest.param(
        "10204", lambda: _db([[{"MENU_ID": "20101"}], [{"TABLE_NAME": "T_CMDB_X"}]], [{"COLUMN_NAME": "DATA_JSON"}]),
        {"column_name": "DATA_JSON"}, {"column_name": "OLD"},
        id="10204-column-exists",
    ),
    pytest.param(
        "10104", lambda: _db([[{"MENU_ID": "10203"}], [{"PRIVILEGES_ID": "1"}]]),
        {"role_name": "role-other", "menu_name": "m", "associate": "1"}, None,
        id="10104-grant-to-other-role",
    ),
    pytest.param(
        "10104", lambda: _db([[{"MENU_ID": "20101"}]]),
        {"role_name": "role-own", "menu_name": "m", "associate": "1"}, None,
        id="10104-self-grant-unprotected-menu",
    ),
]


@pytest.mark.usefixtures("guard_env")
@pytest.mark.parametrize("menu_id, make_db, new, old", SAFE)
class TestAllowsSafeDefinition:
    """通常の変更は拒否されない(誤拒否の確認)"""

    def test_allowed(self, menu_id, make_db, new, old):
        t = _FakeTable(menu_id, make_db())
        ret, msg, _ = t.exec_menu_before_validate(_option("Update", new, old))
        assert ret is True, "正規の変更が拒否された: %s" % msg


@pytest.mark.usefixtures("guard_env")
class TestGuardMode:
    @pytest.mark.parametrize("mode", ["monitor", "warn"])
    def test_monitor_mode_does_not_reject(self, mode, monkeypatch):
        """monitor / warn では違反を拒否せず、ガードログに出力する"""
        t = _FakeTable("10203", _db([[{"MENU_ID": "20101"}]], [{"TABLE_NAME": SENSITIVE_TABLE}]))
        monkeypatch.setenv("MENU_DEF_GUARD_MODE", mode)
        ret, _, _ = t.exec_menu_before_validate(_option("Update", {"table_name": SENSITIVE_TABLE}, {"table_name": "T_X"}))
        assert ret is True
        assert g.applogger.info.called

    @pytest.mark.parametrize("cmd_type", ["Discard", "Delete"])
    def test_discard_and_delete_are_not_checked(self, cmd_type):
        t = _FakeTable("10203", _db())
        ret, _, _ = t.exec_menu_before_validate(_option(cmd_type, {"table_name": SENSITIVE_TABLE}, {"table_name": "T_X"}))
        assert ret is True

    def test_other_menus_are_unaffected(self):
        """対象外のメニューは検証されない"""
        t = _FakeTable("20101", _db())
        ret, _, option = t.exec_menu_before_validate(_option("Update", {"table_name": SENSITIVE_TABLE}, {"table_name": "T_X"}))
        assert ret is True


def _master_sql_files():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4, "ita_api_admin", "sql"))
    return sorted(glob.glob(os.path.join(root, "*_master.sql")))


def _master_menu_tables():
    """マスタ(T_COMN_MENU_TABLE_LINK)の MENU_ID -> (TABLE_NAME, VIEW_NAME)"""
    result = {}
    for path in _master_sql_files():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("INSERT IGNORE INTO T_COMN_MENU_TABLE_LINK (") and "VALUES(" in line:
                    m = re.match(r"'?\d+'?,'?(\d+)'?,'([^']*)',(?:NULL|'([^']*)')", line.split("VALUES(", 1)[1])
                    if m:
                        result[m.group(1)] = (m.group(2), m.group(3))
    return result


class TestConsistencyWithMasterSql:
    """ガードの対応表が、マスタSQLの定義と食い違っていないこと(取り違えると正規メニューを壊す)"""

    def test_master_sql_is_found(self):
        assert _master_menu_tables(), "マスタSQLが読めない: テスト配置を確認してください"

    def test_owner_menus_match_master(self):
        from common_libs.validate.menu_def_guard import SENSITIVE_TABLE_OWNERS
        menu_tables = _master_menu_tables()
        for table, owners in SENSITIVE_TABLE_OWNERS.items():
            for owner in owners:
                assert owner in menu_tables, "所有メニューがマスタに無い: %s -> %s" % (table, owner)
                assert menu_tables[owner][0] == table, "所有メニューのテーブルがマスタと異なる: %s -> %s (マスタ: %s)" % (
                    table, owner, menu_tables[owner][0])

    def test_deny_list_is_not_read_by_any_menu_in_master(self):
        """拒否リストのテーブルを、マスタのメニューが読んでいない(読んでいれば正規メニューを壊す)"""
        from common_libs.validate.menu_def_guard import DENY_TABLES
        read = set()
        for table, view in _master_menu_tables().values():
            read.add(table)
            if view:
                read.add(view)
        read_keys = set("T_" + n[2:] if n.startswith("V_") else n for n in read)
        assert not (DENY_TABLES & read_keys), "メニューが読むテーブルが拒否リストにある: %s" % sorted(DENY_TABLES & read_keys)
