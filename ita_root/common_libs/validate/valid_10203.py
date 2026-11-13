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
10203 メニュー-テーブル紐付管理 の個別バリデーション
"""
from common_libs.validate import menu_def_guard

MENU_ID = "10203"
# 参照先を決める項目と、記録対象の項目
TABLE_ITEMS = ("table_name", "view_name")
WATCHED_ITEMS = TABLE_ITEMS + (
    "pk_column_name_rest", "sheet_type", "history_table_flag", "inheritance_flag", "vertical_flag",
    "hostgroup_flag", "row_insert_flag", "row_update_flag", "row_disuse_flag", "row_reuse_flag", "row_delete_flag",
    "substitution_value_link_flag", "lock_target_table", "unique_constraint",
    "before_individual_validation", "after_individual_validation",
)


def _target_menu_id(objdbca, option):
    """更新対象レコードのメニューIDを取得する(新規登録時は None)"""
    uuid = option.get("uuid")
    if not uuid:
        return None
    rows = objdbca.table_select("T_COMN_MENU_TABLE_LINK", "WHERE TABLE_DEFINITION_ID = %s", [uuid])
    return rows[0].get("MENU_ID") if rows else None


def external_valid_menu_before(objdbca, objtable, option):
    retBool = True
    msg = ''

    # 廃止・復活・削除時はチェックしない
    cmd_type = option.get("cmd_type")
    if cmd_type in ("Delete", "Discard", "Restore"):
        return retBool, msg, option

    new = option.get("entry_parameter", {}).get("parameter", {}) or {}
    old = (option.get("current_parameter") or {}).get("parameter", {}) or {}

    # 変更のガードログ
    menu_def_guard.log_changes(MENU_ID, option, WATCHED_ITEMS)

    target_menu_id = _target_menu_id(objdbca, option)
    for item in TABLE_ITEMS:
        # 変更された項目のみ検査する(既存値は対象外)
        if item not in new or new.get(item) == old.get(item):
            continue
        ok, errormsg = menu_def_guard.check_table_reference(objdbca, item, new.get(item), target_menu_id)
        if ok is not True:
            return menu_def_guard.judge(MENU_ID, cmd_type, item, old.get(item), new.get(item), errormsg, option)

    return retBool, msg, option
