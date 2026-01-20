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


def main(work_dir_path, ws_db):
    """t_comn_conductor_regularly_listのmigration対応(Issue#2872)

    Args:
        work_dir_path (str): 作業フォルダパス / Work directory path
        ws_db (obj): ワークスペースDB接続オブジェクト / Workspace DB connection object

    Returns:
        int: 0:正常終了 / Normal termination
             0以外:異常終了 / Abnormal termination
    """

    g.applogger.info(f"[Trace][start] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    common_db = DBConnectCommon()  # noqa: F405

    organization_id = g.ORGANIZATION_ID

    # organization単位のドライバ情報を取得する
    # Get driver information for each organization
    org_no_install_driver = common_db.table_select("T_COMN_ORGANIZATION_DB_INFO", "WHERE ORGANIZATION_ID = '{}' AND DISUSE_FLAG = {}".format(organization_id, 0))[0]["NO_INSTALL_DRIVER"]
    common_db.db_disconnect()

    # oaseインストール済みの場合しか対応しない
    # Only applicable if oase is already installed
    org_no_install_driver = json.loads(org_no_install_driver) if org_no_install_driver is not None else {}
    if 'oase' in org_no_install_driver:
        g.applogger.info("[Trace][skipped] update_oase_filter_search_condition skipped because OASE is not installed.")
        return 0

    # 検索条件の更新
    # Update Search Condition

    # トランザクション開始
    # Start transaction
    ws_db.db_transaction_start()

    # 「グルーピング」-> 「グルーピング（期間延長あり）」への更新 & カラムの説明文更新
    # Update from "Grouping" to "Grouping (Period Extension)" & Update column description

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

    # 「グルーピング（期間延長なし）」の追加
    # Add "Grouping (No Period Extension)"

    table_name = "T_OASE_SEARCH_CONDITION"

    current_record = ws_db.table_select(
        table_name,
        "WHERE SEARCH_CONDITION_ID = 4",
        []
    )

    insert_data_list = {
        "SEARCH_CONDITION_ID": 4,
        "SEARCH_CONDITION_NAME_EN": "Grouping (No Period Extension)",
        "SEARCH_CONDITION_NAME_JA": "グルーピング（期間延長なし）",
        "DISUSE_FLAG": 0,
        "LAST_UPDATE_USER": 1
    }

    # すでに存在している場合は追加しない
    # Do not add if it already exists
    if len(current_record) == 0:
        ws_db.table_insert(
            table_name=table_name,
            primary_key_name="SEARCH_CONDITION_ID",
            data_list=[insert_data_list],
            is_register_history=False
        )

    # トランザクションコミット
    # Commit transaction
    ws_db.db_commit()

    g.applogger.info(f"[Trace][end] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    return 0
