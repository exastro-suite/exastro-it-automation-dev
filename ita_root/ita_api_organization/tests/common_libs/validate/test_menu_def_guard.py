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
common_libs.validate.menu_def_guard のユニットテスト

メニュー定義(10203/10204)・ロール-メニュー紐付(10104)の更新ガードの部品を、
DBに接続せずに検証する。loadTable を経由した全体の挙動は
tests/common_libs/loadtable/test_menu_definition_guard.py で検証する。

期待する挙動:
  - 識別子は英数字・アンダースコア・ハイフンのみ。それ以外(バッククォート、空白、引用符など)は拒否する
  - 拒否リスト(初期状態でメニューが読まないテーブル、接続情報など)は、どのメニューからも指定できない
    履歴テーブル(*_JNL)も指定できない。ビュー(V_)はテーブル(T_)と同じ扱い
  - 機微テーブル(権限・メニュー定義・システム設定・認証情報)は、所有メニュー以外からは指定できない
    所有メニューは、マスタ(T_COMN_MENU_TABLE_LINK)の定義と一致する
  - 参照先テーブル・列は、データベースに実在しなければ拒否する
  - モードは環境変数 MENU_DEF_GUARD_MODE。未設定・不正な値は enforce
  - 拒否は enforce のときのみ。monitor / warn はガードログを出して通す

実行: cd ita_root/ita_api_organization && python3 -m pytest tests/common_libs/validate/test_menu_def_guard.py
"""
from unittest.mock import MagicMock

import pytest
from flask import Flask, g

from common_libs.validate import menu_def_guard
from common_libs.validate.menu_def_guard import (
    DENY_TABLES, SENSITIVE_TABLE_OWNERS, check_column_exists, check_table_reference, get_mode, is_denied,
    is_enforce, judge, log_changes)


@pytest.fixture
def guard_env(monkeypatch):
    """flask の g(メッセージ・ログ・ユーザ)を用意し、モード未設定の状態にする"""
    app = Flask(__name__)
    with app.app_context():
        g.appmsg = MagicMock()
        g.appmsg.get_api_message.side_effect = lambda code, args=None: f"{code}:{args}"
        g.applogger = MagicMock()
        g.USER_ID = "user-1"
        monkeypatch.delenv(menu_def_guard.MODE_ENV, raising=False)
        yield


def _db(rows=None):
    """sql_execute は rows を返す"""
    db = MagicMock()
    db.sql_execute.return_value = rows if rows is not None else []
    return db


@pytest.mark.usefixtures("guard_env")
class TestMode:
    def test_default_is_enforce_when_not_configured(self):
        assert get_mode() == "enforce"
        assert is_enforce() is True

    @pytest.mark.parametrize("value, expected", [
        pytest.param("enforce", "enforce", id="enforce"),
        pytest.param(" ENFORCE ", "enforce", id="upper-case-with-space"),
        pytest.param("warn", "warn", id="warn"),
        pytest.param("monitor", "monitor", id="monitor"),
        pytest.param("unknown", "enforce", id="unknown-falls-back-to-enforce"),
        pytest.param("", "enforce", id="empty-falls-back-to-enforce"),
    ])
    def test_mode_values(self, monkeypatch, value, expected):
        monkeypatch.setenv(menu_def_guard.MODE_ENV, value)
        assert get_mode() == expected
        assert is_enforce() is (expected == "enforce")


@pytest.mark.usefixtures("guard_env")
class TestCheckTableReference:
    @pytest.mark.parametrize("value", [
        pytest.param("T_CMDB_X", id="plain"),
        pytest.param("V_CMDB_X-1", id="with-hyphen"),
    ])
    def test_valid_existing_table(self, value):
        ok, msg = check_table_reference(_db([{"TABLE_NAME": value}]), "table_name", value, "20101")
        assert ok is True and msg == ""

    @pytest.mark.parametrize("value", [None, ""], ids=["none", "empty"])
    def test_empty_is_not_checked(self, value):
        db = _db()
        ok, _ = check_table_reference(db, "table_name", value, "20101")
        assert ok is True
        db.sql_execute.assert_not_called()

    @pytest.mark.parametrize("value", [
        pytest.param("T_X`", id="backquote"),
        pytest.param("T X", id="space"),
        pytest.param("T_X;DROP", id="semicolon"),
        pytest.param("T_X' OR '1", id="quote"),
        pytest.param("db.T_X", id="dot"),
        pytest.param(123, id="not-string"),
    ])
    def test_invalid_identifier_is_rejected_without_query(self, value):
        db = _db([{"TABLE_NAME": "x"}])
        ok, msg = check_table_reference(db, "table_name", value, "20101")
        assert ok is False and "499-01907" in msg
        db.sql_execute.assert_not_called()

    @pytest.mark.parametrize("value", [
        pytest.param("T_COMN_WORKSPACE_DB_INFO", id="workspace-db-info"),
        pytest.param("T_COMN_BACKYARD_USER", id="backyard-user"),
        pytest.param("T_COMN_PROC_LOADED_LIST", id="proc-loaded-list"),
        pytest.param("T_COMN_WEB_TABLE_SETTINGS", id="web-table-settings"),
        pytest.param("T_OASE_EVENT", id="oase-event"),
        pytest.param("V_COMN_WORKSPACE_DB_INFO", id="view-of-denied-table"),
        pytest.param("T_CMDB_X_JNL", id="history-table"),
        pytest.param("V_COMN_MENU_JNL", id="history-view"),
    ])
    def test_deny_list_is_rejected_for_every_menu(self, value):
        for own in ("20101", "10101", None):
            ok, msg = check_table_reference(_db([{"TABLE_NAME": value}]), "table_name", value, own)
            assert ok is False and "499-01906" in msg

    @pytest.mark.parametrize("value", [
        pytest.param("T_COMN_ROLE_MENU_LINK", id="role-menu-link"),
        pytest.param("V_COMN_ROLE_MENU_LINK", id="role-menu-link-view"),
        pytest.param("T_COMN_MENU_TABLE_LINK", id="menu-table-link"),
        pytest.param("T_COMN_MENU_COLUMN_LINK", id="menu-column-link"),
        pytest.param("T_COMN_SYSTEM_CONFIG", id="system-config"),
        pytest.param("T_COMN_MENU", id="menu"),
        pytest.param("T_COMN_MENU_GROUP", id="menu-group"),
        pytest.param("T_COMN_COLUMN_GROUP", id="column-group"),
        pytest.param("T_ANSC_DEVICE", id="credential-device"),
        pytest.param("T_OASE_EVENT_COLLECTION_SETTINGS", id="credential-oase"),
    ])
    def test_sensitive_table_is_rejected_for_other_menus(self, value):
        ok, msg = check_table_reference(_db([{"TABLE_NAME": value}]), "table_name", value, "20999")
        assert ok is False and "499-01906" in msg

    @pytest.mark.parametrize("table, owner", sorted(
        (t, o) for t, owners in SENSITIVE_TABLE_OWNERS.items() for o in owners))
    def test_sensitive_table_is_allowed_for_its_owner_menu(self, table, owner):
        """所有メニューは自身のテーブルのまま保てる(マスタの定義と一致している)"""
        ok, _ = check_table_reference(_db([{"TABLE_NAME": table}]), "table_name", table, owner)
        assert ok is True

    def test_owner_mapping_matches_master_definition(self):
        """マスタ(T_COMN_MENU_TABLE_LINK)の所有関係。取り違えると、所有メニューが自身のテーブルを保てない"""
        assert SENSITIVE_TABLE_OWNERS["T_COMN_MENU"] == ("10103",)
        assert SENSITIVE_TABLE_OWNERS["T_COMN_SYSTEM_CONFIG"] == ("10101",)
        assert SENSITIVE_TABLE_OWNERS["T_COMN_MENU_GROUP"] == ("10102",)

    def test_deny_list_and_owner_map_do_not_overlap(self):
        """拒否リストは所有メニューの例外がない。所有メニューのテーブルを誤って含めない"""
        assert DENY_TABLES.isdisjoint(SENSITIVE_TABLE_OWNERS)

    def test_sensitive_table_is_rejected_for_new_record(self):
        """新規登録(対象メニュー不明)では所有メニューと見なさない"""
        ok, msg = check_table_reference(_db([{"TABLE_NAME": "T_COMN_ROLE_MENU_LINK"}]), "table_name", "T_COMN_ROLE_MENU_LINK", None)
        assert ok is False and "499-01906" in msg

    def test_lookup_ok_exempts_sensitive_check_but_not_deny_list(self):
        ok, _ = check_table_reference(_db([{"TABLE_NAME": "T_COMN_MENU"}]), "id_link_table", "T_COMN_MENU", "10104", ("T_COMN_MENU",))
        assert ok is True
        ok, _ = check_table_reference(_db([{"TABLE_NAME": "T_COMN_WORKSPACE_DB_INFO"}]), "id_link_table", "T_COMN_WORKSPACE_DB_INFO", "10104", ("T_COMN_WORKSPACE_DB_INFO",))
        assert ok is False

    def test_not_existing_table_is_rejected(self):
        ok, msg = check_table_reference(_db([]), "table_name", "T_NOT_EXISTS", "20101")
        assert ok is False and "499-01908" in msg

    def test_existence_query_is_parameterized(self):
        """テーブル名はSQL文字列に埋め込まず、バインド変数で渡す"""
        db = _db([{"TABLE_NAME": "T_CMDB_X"}])
        check_table_reference(db, "table_name", "T_CMDB_X", "20101")
        sql, binds = db.sql_execute.call_args[0]
        assert "T_CMDB_X" not in sql and binds == ["T_CMDB_X"]

    def test_denied_table_is_rejected_without_query(self):
        db = _db([{"TABLE_NAME": "T_COMN_WORKSPACE_DB_INFO"}])
        check_table_reference(db, "table_name", "T_COMN_WORKSPACE_DB_INFO", "20101")
        db.sql_execute.assert_not_called()


class TestIsDenied:
    @pytest.mark.parametrize("name, expected", [
        pytest.param("T_COMN_WORKSPACE_DB_INFO", True, id="listed"),
        pytest.param("V_COMN_WORKSPACE_DB_INFO", True, id="view-of-listed"),
        pytest.param("T_ANY_JNL", True, id="history-suffix"),
        pytest.param("T_CMDB_X", False, id="dynamic"),
        pytest.param("T_COMN_ROLE_MENU_LINK", False, id="owner-controlled-is-not-denied"),
        pytest.param("T_COMN_BOOLEAN_FLAG", False, id="lookup"),
    ])
    def test_is_denied(self, name, expected):
        assert is_denied(name) is expected


@pytest.mark.usefixtures("guard_env")
class TestCheckColumnExists:
    def test_existing_column(self):
        ok, _ = check_column_exists(_db([{"COLUMN_NAME": "DATA_JSON"}]), "column_name", "T_CMDB_X", "DATA_JSON")
        assert ok is True

    def test_not_existing_column(self):
        ok, msg = check_column_exists(_db([]), "column_name", "T_CMDB_X", "NOPE")
        assert ok is False and "499-01908" in msg

    @pytest.mark.parametrize("table, column", [
        pytest.param(None, "A", id="table-none"),
        pytest.param("T_X", None, id="column-none"),
        pytest.param("T_X", "", id="column-empty"),
    ])
    def test_missing_target_is_not_checked(self, table, column):
        db = _db()
        ok, _ = check_column_exists(db, "column_name", table, column)
        assert ok is True
        db.sql_execute.assert_not_called()

    def test_invalid_identifier_is_rejected_without_query(self):
        db = _db([{"COLUMN_NAME": "x"}])
        ok, msg = check_column_exists(db, "column_name", "T_X", "A`B")
        assert ok is False and "499-01907" in msg
        db.sql_execute.assert_not_called()


@pytest.mark.usefixtures("guard_env")
class TestJudgeAndGuardLog:
    def test_judge_rejects_only_in_enforce(self, monkeypatch):
        option = {}
        assert judge("10203", "Update", "table_name", "a", "b", "err", option) == (False, "err", option)
        monkeypatch.setenv(menu_def_guard.MODE_ENV, "enforce")
        assert judge("10203", "Update", "table_name", "a", "b", "err", option) == (False, "err", option)
        for mode in ("monitor", "warn"):
            monkeypatch.setenv(menu_def_guard.MODE_ENV, mode)
            assert judge("10203", "Update", "table_name", "a", "b", "err", option) == (True, "", option)

    def test_judge_writes_guard_log_with_mode_in_every_mode(self, monkeypatch):
        for mode in ("monitor", "warn", "enforce"):
            g.applogger.reset_mock()
            monkeypatch.setenv(menu_def_guard.MODE_ENV, mode)
            judge("10203", "Update", "table_name", "a", "b", "err", {})
            assert g.applogger.info.call_count == 1
            line = g.applogger.info.call_args[0][0]
            assert "[MENU_DEF_GUARD]" in line and "mode=" + mode in line
            assert "user=user-1" in line and "old=a" in line and "new=b" in line

    def test_log_changes_logs_only_changed_keys(self):
        option = {
            "cmd_type": "Update",
            "entry_parameter": {"parameter": {"table_name": "T_B", "view_name": "V_A"}},
            "current_parameter": {"parameter": {"table_name": "T_A", "view_name": "V_A"}},
        }
        log_changes("10203", option, ("table_name", "view_name", "absent"))
        assert g.applogger.info.call_count == 1
        assert "item=table_name" in g.applogger.info.call_args[0][0]

    def test_guard_log_failure_does_not_break_validation(self, monkeypatch):
        monkeypatch.setenv(menu_def_guard.MODE_ENV, "monitor")
        g.applogger.info.side_effect = RuntimeError("log down")
        assert judge("10203", "Update", "table_name", "a", "b", "err", {}) == (True, "", {})
