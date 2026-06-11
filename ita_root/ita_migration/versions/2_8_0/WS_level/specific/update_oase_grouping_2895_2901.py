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

import inspect
from flask import g
import json
import os
from common_libs.common.dbconnect import *  # noqa: F403


def check_oase_installed():
    """OASEがインストールされているかチェック
    """
    common_db = DBConnectCommon()  # noqa: F405
    organization_id = g.ORGANIZATION_ID

    # オーガナイゼーションのドライバー情報を取得
    # Get driver information for each organization
    org_no_install_driver = common_db.table_select(
        "T_COMN_ORGANIZATION_DB_INFO",
        "WHERE ORGANIZATION_ID = '{}' AND DISUSE_FLAG = {}".format(organization_id, 0)
    )[0]["NO_INSTALL_DRIVER"]
    common_db.db_disconnect()

    # OASEがインストール済みの場合のみ適用
    # Only applicable if oase is already installed
    org_no_install_driver = json.loads(org_no_install_driver) if org_no_install_driver is not None else {}
    return 'oase' not in org_no_install_driver


def add_group_period_column(ws_db):
    """#2901
    T_OASE_FILTERテーブルにGROUP_PERIODカラムを追加
    Add GROUP_PERIOD column to T_OASE_FILTER table.
    """
    filter_table_name = "T_OASE_FILTER"
    filter_table_name_jnl = filter_table_name + "_JNL"

    # 各テーブルごとにGROUP_PERIODカラムの存在を確認してから追加
    # Check each table individually before adding GROUP_PERIOD column
    for table_name in [filter_table_name, filter_table_name_jnl]:
        check_column_sql = f"SHOW COLUMNS FROM {table_name}"
        check_column = ws_db.sql_execute(check_column_sql)

        for row in check_column:
            if row['Field'] == 'GROUP_PERIOD':
                g.applogger.info(f"GROUP_PERIOD column already exists in {table_name}. Skipping.")
                break
        else:
            g.applogger.info(f"Adding GROUP_PERIOD column to {table_name}")
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN GROUP_PERIOD INT AFTER GROUP_CONDITION_ID"
            ws_db.sql_execute(alter_sql)

    return True


def add_menu_column_link(ws_db):
    """#2901
    メニューカラム紐付けにグルーピング期間（GROUP_PERIOD）を追加
    Add grouping period (GROUP_PERIOD) to menu column link.
    """
    menu_column_link_table_name = "T_COMN_MENU_COLUMN_LINK"
    menu_column_link_table_name_jnl = menu_column_link_table_name + "_JNL"
    column_definition_id = '11010712'

    insert_sql = """
INSERT INTO T_COMN_MENU_COLUMN_LINK (COLUMN_DEFINITION_ID,MENU_ID,COLUMN_NAME_JA,COLUMN_NAME_EN,COLUMN_NAME_REST,COL_GROUP_ID,COLUMN_CLASS,COLUMN_DISP_SEQ,REF_TABLE_NAME,REF_PKEY_NAME,REF_COL_NAME,REF_SORT_CONDITIONS,REF_MULTI_LANG,REFERENCE_ITEM,SENSITIVE_COL_NAME,FILE_UPLOAD_PLACE,BUTTON_ACTION,COL_NAME,SAVE_TYPE,AUTO_INPUT,INPUT_ITEM,VIEW_ITEM,UNIQUE_ITEM,REQUIRED_ITEM,AUTOREG_HIDE_ITEM,AUTOREG_ONLY_ITEM,INITIAL_VALUE,VALIDATE_OPTION,VALIDATE_REG_EXP,BEFORE_VALIDATE_REGISTER,AFTER_VALIDATE_REGISTER,DESCRIPTION_JA,DESCRIPTION_EN,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES('11010712','110107','期間','Period','group_period','11010711','3',57,NULL,NULL,NULL,NULL,'0',NULL,NULL,NULL,NULL,'GROUP_PERIOD',NULL,'0','1','1','0','0','0','0',NULL,'{
"int_min": 10,
"int_max": 2147483647
}',NULL,NULL,NULL,'[最小値]10（秒）
[最大値]2147483647（秒）
検索方法で「グルーピング（期間延長なし）」を選択したときに、先頭イベントのTTLとは別に、グルーピングを行う対象の期間を指定したい場合に入力してください。','[Minimum value] 10 (seconds)
[Maximum value] 2147483647 (seconds)
Use this field to define the grouping duration independently of the first event TTL when the "Grouping (No Period Extension)" search method is active.',NULL,'0',"2026/02/09 10:00",1);"""

    insert_sql_jnl = """
INSERT INTO T_COMN_MENU_COLUMN_LINK_JNL (JOURNAL_SEQ_NO,JOURNAL_REG_DATETIME,JOURNAL_ACTION_CLASS,COLUMN_DEFINITION_ID,MENU_ID,COLUMN_NAME_JA,COLUMN_NAME_EN,COLUMN_NAME_REST,COL_GROUP_ID,COLUMN_CLASS,COLUMN_DISP_SEQ,REF_TABLE_NAME,REF_PKEY_NAME,REF_COL_NAME,REF_SORT_CONDITIONS,REF_MULTI_LANG,REFERENCE_ITEM,SENSITIVE_COL_NAME,FILE_UPLOAD_PLACE,BUTTON_ACTION,COL_NAME,SAVE_TYPE,AUTO_INPUT,INPUT_ITEM,VIEW_ITEM,UNIQUE_ITEM,REQUIRED_ITEM,AUTOREG_HIDE_ITEM,AUTOREG_ONLY_ITEM,INITIAL_VALUE,VALIDATE_OPTION,VALIDATE_REG_EXP,BEFORE_VALIDATE_REGISTER,AFTER_VALIDATE_REGISTER,DESCRIPTION_JA,DESCRIPTION_EN,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES(11010712,"2026/02/09 10:00",'INSERT','11010712','110107','期間','Period','group_period','11010711','3',57,NULL,NULL,NULL,NULL,'0',NULL,NULL,NULL,NULL,'GROUP_PERIOD',NULL,'0','1','1','0','0','0','0',NULL,'{
"int_min": 10,
"int_max": 2147483647
}',NULL,NULL,NULL,'[最小値]10（秒）
[最大値]2147483647（秒）
検索方法で「グルーピング（期間延長なし）」を選択したときに、先頭イベントのTTLとは別に、グルーピングを行う対象の期間を指定したい場合に入力してください。','[Minimum value] 10 (seconds)
[Maximum value] 2147483647 (seconds)
Use this field to define the grouping duration independently of the first event TTL when the "Grouping (No Period Extension)" search method is active.',NULL,'0',"2026/02/09 10:00",1);"""

    for table_name in [menu_column_link_table_name, menu_column_link_table_name_jnl]:
        check_menu_column = ws_db.table_select(table_name, "WHERE COLUMN_DEFINITION_ID=%s", [column_definition_id])
        # カラムが存在しない場合はINSERTを実行
        if not check_menu_column:
            if table_name == menu_column_link_table_name:
                ws_db.sql_execute(insert_sql)
            else:
                ws_db.sql_execute(insert_sql_jnl)
        else:
            g.applogger.info(f"Menu column link for GROUP_PERIOD already exists in {table_name}. Skipping.")

    return True


def update_search_condition_data(ws_db):
    """#2895
    検索条件の選択肢「グルーピング」を「グルーピング（期間延長あり）」に更新し、検索条件カラムの説明文を更新
    Update search condition from 'Grouping' to 'Grouping (Period Extension)' and update descriptions
    """
    column_description_en = """Select a search method.
Unique: Only allows extraction of unique events. If multiple events are hit, all hit events are treated as unknown events.
Queuing: Extract unique events, but if multiple events are hit, use the oldest event. Please note that the rule may be matched multiple times.
Grouping: Groups events that match the filter conditions based on the labels and conditions specified in the grouping conditions. You can choose between "Period Extension," where the period of the first event is extended each time events are grouped, and "No Period Extension," where events are grouped within the TTL of the first event."""

    column_description_ja = """検索方法を選択します。
ユニーク：一意のイベントの抽出しか許可しません。複数イベントがヒットした場合、ヒットしたイベントすべてを未知のイベントとして処理します。
キューイング：一意のイベントを抽出しますが、複数イベントがヒットした場合、一番古いイベントを使用します。ルールに複数回マッチする可能性があるため、ご注意ください。
グルーピング：フィルター条件に合致したイベントの中から、グルーピング条件で指定したラベルと条件に該当するイベントをそれぞれグルーピングします。イベントがグルーピングされるごとに先頭イベントの期間が延長される「期間延長あり」と、先頭イベントのTTL内でグルーピングされる「期間延長なし」を選択できます。"""

    update_items = [
        {
            "table_name": "T_OASE_SEARCH_CONDITION",
            "data_list": {
                "SEARCH_CONDITION_ID": "3",
                "SEARCH_CONDITION_NAME_EN": "Grouping (Period Extension)",
                "SEARCH_CONDITION_NAME_JA": "グルーピング（期間延長あり）"
            },
            "primary_key_name": "SEARCH_CONDITION_ID",
            "is_register_history": False
        },
        {
            "table_name": "T_COMN_MENU_COLUMN_LINK",
            "data_list": {
                "COLUMN_DEFINITION_ID": "11010709",
                "DESCRIPTION_EN": column_description_en,
                "DESCRIPTION_JA": column_description_ja
            },
            "primary_key_name": "COLUMN_DEFINITION_ID",
            "is_register_history": False
        },
        {
            "table_name": "T_COMN_MENU_COLUMN_LINK_JNL",
            "data_list": {
                "JOURNAL_SEQ_NO": "11010709",
                "DESCRIPTION_EN": column_description_en,
                "DESCRIPTION_JA": column_description_ja
            },
            "primary_key_name": "JOURNAL_SEQ_NO",
            "is_register_history": False
        }
    ]

    for item in update_items:
        ws_db.table_update(
            table_name=item["table_name"],
            data_list=item["data_list"],
            primary_key_name=item["primary_key_name"],
            is_register_history=item["is_register_history"]
        )

    return True


def add_new_search_condition(ws_db):
    """#2895
    検索条件の選択肢「グルーピング（期間延長なし）」を追加
    Add new search condition 'Grouping (No Period Extension)'
    """
    table_name = "T_OASE_SEARCH_CONDITION"

    current_record = ws_db.table_select(
        table_name,
        "WHERE SEARCH_CONDITION_ID = 4",
        []
    )

    # すでに存在する場合は追加しない
    # Do not add if it already exists
    if len(current_record) == 0:
        insert_data_list = {
            "SEARCH_CONDITION_ID": 4,
            "SEARCH_CONDITION_NAME_EN": "Grouping (No Period Extension)",
            "SEARCH_CONDITION_NAME_JA": "グルーピング（期間延長なし）",
            "DISUSE_FLAG": 0,
            "LAST_UPDATE_USER": 1
        }

        ws_db.table_insert(
            table_name=table_name,
            primary_key_name="SEARCH_CONDITION_ID",
            data_list=[insert_data_list],
            is_register_history=False
        )
        g.applogger.info("Added new search condition: Grouping (No Period Extension)")
    else:
        g.applogger.info("Search condition 'Grouping (No Period Extension)' already exists. Skipping.")

    return True


def main(work_dir_path, ws_db):
    """
    #2901: add_group_period_column
    #2901: add_menu_column_link
    #2895: add_new_search_condition
    #2895: add_group_period_column
    """
    g.applogger.info(f"[Trace][start] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    # OASEがインストールされているかチェック
    # Check if OASE is installed
    if not check_oase_installed():
        g.applogger.info("[Trace][skipped] Migration skipped because OASE is not installed.")
        return 0

    try:
        # トランザクション開始
        # Start transaction
        ws_db.db_transaction_start()

        # T_OASE_FILTERテーブルにGROUP_PERIODカラムを追加
        # Add GROUP_PERIOD column to T_OASE_FILTER table.
        add_group_period_column(ws_db)

        # メニューカラム紐付けにグルーピング期間（GROUP_PERIOD）を追加
        # Add grouping period (GROUP_PERIOD) to menu column link.
        add_menu_column_link(ws_db)

        # 検索条件の選択肢「グルーピング」を「グルーピング（期間延長あり）」に更新し、検索条件カラムの説明文を更新
        # Update search condition from 'Grouping' to 'Grouping (Period Extension)' and update descriptions
        update_search_condition_data(ws_db)

        # 検索条件の選択肢「グルーピング（期間延長なし）」を追加
        # Add new search condition 'Grouping (No Period Extension)'
        add_new_search_condition(ws_db)

        # トランザクションコミット
        # Commit transaction
        ws_db.db_transaction_end(True)

    except Exception as e:
        g.applogger.error(f"Migration failed: {str(e)}")
        ws_db.db_transaction_end(False)
        raise

    g.applogger.info(f"[Trace][end] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    return 0
