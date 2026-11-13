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
10204 メニュー-カラム紐付管理 の個別バリデーション
"""
from common_libs.validate import menu_def_guard

MENU_ID = "10204"
WATCHED_ITEMS = (
    "column_name", "column_name_rest", "column_class", "db_storage_format",
    "id_link_table", "id_link_key_column_name", "id_link_column_name", "id_link_sort_condition",
    "reference_item", "sensitive_coloumn_name", "file_upload_place", "button_action",
    "validation_value", "validation_reg_exp",
    "before_individual_validation", "after_individual_validation",
)
# プルダウン参照として一般的に使われるため、参照先としては許容するテーブル
LOOKUP_OK = ("T_COMN_MENU", "V_COMN_MENU")


def _target_row(objdbca, option):
    """更新対象レコードの (MENU_ID, 対象メニューのTABLE_NAME) を取得する(新規登録時は None, None)"""
    uuid = option.get("uuid")
    if not uuid:
        return None, None
    rows = objdbca.table_select("T_COMN_MENU_COLUMN_LINK", "WHERE COLUMN_DEFINITION_ID = %s", [uuid])
    if not rows:
        return None, None
    menu_id = rows[0].get("MENU_ID")
    trows = objdbca.table_select("T_COMN_MENU_TABLE_LINK", "WHERE MENU_ID = %s AND DISUSE_FLAG = '0'", [menu_id])
    return menu_id, (trows[0].get("TABLE_NAME") if trows else None)


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

    menu_id, own_table = _target_row(objdbca, option)

    def changed(item):
        return item in new and new.get(item) != old.get(item)

    # 参照先テーブル(プルダウン等)
    if changed("id_link_table"):
        ok, errormsg = menu_def_guard.check_table_reference(
            objdbca, "id_link_table", new.get("id_link_table"), menu_id, LOOKUP_OK)
        if ok is not True:
            return menu_def_guard.judge(MENU_ID, cmd_type, "id_link_table", old.get("id_link_table"), new.get("id_link_table"), errormsg, option)

    # 参照先テーブルの主キー列・表示列
    ref_table = new.get("id_link_table") if "id_link_table" in new else old.get("id_link_table")
    for item in ("id_link_key_column_name", "id_link_column_name"):
        if changed(item) or changed("id_link_table"):
            ok, errormsg = menu_def_guard.check_column_exists(objdbca, item, ref_table, new.get(item))
            if ok is not True:
                return menu_def_guard.judge(MENU_ID, cmd_type, item, old.get(item), new.get(item), errormsg, option)

    # 自メニューのテーブルに対する列対応(COL_NAME)
    if changed("column_name") and own_table:
        ok, errormsg = menu_def_guard.check_column_exists(objdbca, "column_name", own_table, new.get("column_name"))
        if ok is not True:
            return menu_def_guard.judge(MENU_ID, cmd_type, "column_name", old.get("column_name"), new.get("column_name"), errormsg, option)

    return retBool, msg, option
