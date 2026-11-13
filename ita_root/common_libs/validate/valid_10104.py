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
10104 ロール-メニュー紐付管理 の個別バリデーション
自分が属するロールへ、システム管理メニューのメンテナンス権限を付与する更新を検出する。
"""
from flask import g

from common_libs.validate import menu_def_guard

MENU_ID = "10104"


def _resolve_menu_id(objdbca, value):
    """メニュー項目(表示名またはID)から MENU_ID を解決する。解決できない場合は None"""
    if value is None or value == "":
        return None
    rows = objdbca.table_select(
        "V_COMN_MENU_GROUP_MENU_PULLDOWN",
        "WHERE MENU_ID = %s OR MENU_GROUP_NAME_PULLDOWN_JA = %s OR MENU_GROUP_NAME_PULLDOWN_EN = %s",
        [value, value, value])
    return str(rows[0].get("MENU_ID")) if rows else None


def _is_maintenance(objdbca, value):
    """紐付(権限)項目がメンテナンス可かを判定する"""
    if value is None or value == "":
        return False
    rows = objdbca.table_select(
        "T_COMN_OPERATION_PRIVILEGES",
        "WHERE PRIVILEGES_ID = %s OR PRIVILEGES_NAME_JA = %s OR PRIVILEGES_NAME_EN = %s",
        [value, value, value])
    return bool(rows) and str(rows[0].get("PRIVILEGES_ID")) == menu_def_guard.PRIVILEGE_MAINTENANCE


def external_valid_menu_before(objdbca, objtable, option):
    retBool = True
    msg = ''

    # 廃止・削除時はチェックしない(復活は付与と同じ効果のため検査する)
    cmd_type = option.get("cmd_type")
    if cmd_type in ("Delete", "Discard"):
        return retBool, msg, option

    new = option.get("entry_parameter", {}).get("parameter", {}) or {}
    old = (option.get("current_parameter") or {}).get("parameter", {}) or {}
    # Restore 時は更新前の値を引き継ぐ
    role = new.get("role_name", old.get("role_name"))
    menu = new.get("menu_name", old.get("menu_name"))
    associate = new.get("associate", old.get("associate"))

    menu_id = _resolve_menu_id(objdbca, menu)
    if menu_id not in menu_def_guard.PROTECTED_MENU_IDS:
        return retBool, msg, option
    if not _is_maintenance(objdbca, associate):
        return retBool, msg, option

    # 保護対象メニューへのメンテナンス権限の付与は全件ガードログに残す
    menu_def_guard.guard_log(MENU_ID, cmd_type, "grant", menu_id, f"role={role} associate={associate}", "protected menu grant")

    # 自分が属するロールへの自己付与を拒否する
    if role in (getattr(g, "ROLES", None) or []):
        errormsg = g.appmsg.get_api_message("499-01909", [menu_id])
        return menu_def_guard.judge(MENU_ID, cmd_type, "grant_self", menu_id, role, errormsg, option)

    return retBool, msg, option
