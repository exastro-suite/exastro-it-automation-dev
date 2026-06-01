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
import json
import os
from flask import g

from common_libs.common.dbconnect import *  # noqa: F403


TARGET_TABLES = [
    "T_OASE_ACTION_LOG",
    "T_OASE_ACTION_LOG_JNL",
]

TARGET_COLUMNS = [
    "CONCLUSION_EVENT_LABELS",
    "ACTION_PARAMETERS"
]


def check_oase_installed():
    """
    OASEがインストールされているかチェック
    Check whether OASE is installed
    """
    common_db = DBConnectCommon()  # noqa: F405
    organization_id = g.ORGANIZATION_ID

    org_no_install_driver = common_db.table_select(
        "T_COMN_ORGANIZATION_DB_INFO",
        "WHERE ORGANIZATION_ID = '{}' AND DISUSE_FLAG = {}".format(organization_id, 0)
    )[0]["NO_INSTALL_DRIVER"]
    common_db.db_disconnect()

    org_no_install_driver = json.loads(org_no_install_driver) if org_no_install_driver is not None else {}
    return 'oase' not in org_no_install_driver


def is_longtext_column(ws_db, table_name, column_name):
    """
    対象カラムがLONGTEXT型かどうかを判定
    Check whether the target column is of type LONGTEXT
    """
    rows = ws_db.sql_execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", [column_name])

    if len(rows) == 0:
        raise RuntimeError(f"Column not found: {table_name}.{column_name}")

    column_type = str(rows[0].get("Type", "")).lower()
    return column_type == "longtext"


def alter_columns_to_longtext(ws_db, table_name, columns):
    """
    LONGTEXTへの変更が必要なカラムのみALTERを実行
    Modify only the columns that need to be changed to LONGTEXT
    """
    modify_clauses = []

    # 対象カラムがLONGTEXT型かどうかを判定
    # Check whether the target column is of type LONGTEXT
    for column_name in columns:
        if is_longtext_column(ws_db, table_name, column_name):
            g.applogger.info(f"Skipping {table_name}.{column_name}: already LONGTEXT")
            continue

        modify_clauses.append(f"MODIFY COLUMN {column_name} LONGTEXT")

    # 既に全ての対象カラムがLONGTEXT型の場合はALTERをスキップ
    # Skip ALTER if all target columns are already of type LONGTEXT
    if len(modify_clauses) == 0:
        g.applogger.info(f"Skipping {table_name}: all target columns are already LONGTEXT")
        return

    alter_sql = f"ALTER TABLE {table_name} " + ", ".join(modify_clauses)
    ws_db.sql_execute(alter_sql)
    g.applogger.info(f"{alter_sql}")


def main(work_dir_path, ws_db):
    """
    T_OASE_ACTION_LOG / T_OASE_ACTION_LOG_JNL の対象カラムをLONGTEXTへ変更
    Modify target columns in T_OASE_ACTION_LOG / T_OASE_ACTION_LOG_JNL to LONGTEXT
    """
    del work_dir_path

    g.applogger.info(f"[Trace][start] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    # OASEがインストールされていない場合はスキップ
    if not check_oase_installed():
        g.applogger.info("[Trace][skipped] Migration skipped because OASE is not installed.")
        return 0

    try:
        ws_db.db_transaction_start()

        for table_name in TARGET_TABLES:
            alter_columns_to_longtext(ws_db, table_name, TARGET_COLUMNS)

        ws_db.db_transaction_end(True)

    except Exception as e:
        g.applogger.error(f"Alter table failed: {str(e)}")
        ws_db.db_transaction_end(False)
        raise

    g.applogger.info(f"[Trace][end] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")
    return 0
