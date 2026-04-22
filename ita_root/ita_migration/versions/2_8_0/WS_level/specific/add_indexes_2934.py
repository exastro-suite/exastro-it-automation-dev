#!/usr/bin/env python3
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

# インデックス定義
# Index definitions
INDEX_DEFINITIONS = [
    {
        "table_name": "T_COMN_CONDUCTOR_INSTANCE",
        "index_name": "IND_T_COMN_CONDUCTOR_INSTANCE_03",
        "columns": "CONDUCTOR_INSTANCE_ID, STATUS_ID",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_NODE_INSTANCE_JNL",
        "index_name": "IND_T_COMN_CONDUCTOR_NODE_INSTANCE_JNL_01",
        "columns": "NODE_INSTANCE_ID, LAST_UPDATE_TIMESTAMP DESC",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_NODE_INSTANCE_JNL",
        "index_name": "IND_T_COMN_CONDUCTOR_NODE_INSTANCE_JNL_02",
        "columns": "NODE_INSTANCE_ID, JOURNAL_REG_DATETIME DESC",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_INSTANCE_JNL",
        "index_name": "IND_T_COMN_CONDUCTOR_INSTANCE_JNL_01",
        "columns": "CONDUCTOR_INSTANCE_ID, LAST_UPDATE_TIMESTAMP DESC",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_STATUS",
        "index_name": "IND_T_COMN_CONDUCTOR_STATUS_02",
        "columns": "DISUSE_FLAG, DISP_SEQ",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_NODE_STATUS",
        "index_name": "IND_T_COMN_CONDUCTOR_NODE_STATUS_02",
        "columns": "DISUSE_FLAG, DISP_SEQ",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_NODE",
        "index_name": "IND_T_COMN_CONDUCTOR_NODE_02",
        "columns": "DISUSE_FLAG, DISP_SEQ",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_ORCHESTRA",
        "index_name": "IND_T_COMN_ORCHESTRA_02",
        "columns": "DISUSE_FLAG, DISP_SEQ",
        "requires_oase": False,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_NODE_INSTANCE",
        "index_name": "IND_T_COMN_CONDUCTOR_NODE_INSTANCE_05",
        "columns": "CONDUCTOR_INSTANCE_ID, NODE_INSTANCE_ID",
        "requires_oase": False,
    },
    {
        "table_name": "T_OASE_LABELING_SETTINGS",
        "index_name": "IND_T_OASE_LABELING_SETTINGS_02",
        "columns": "DISUSE_FLAG, LABELING_SETTINGS_NAME",
        "requires_oase": True,
    },
    {
        "table_name": "T_COMN_CONDUCTOR_INSTANCE",
        "index_name": "IND_T_COMN_CONDUCTOR_INSTANCE_04",
        "columns": "STATUS_ID, TIME_BOOK, TIME_REGISTER",
        "requires_oase": False,
    },
    {
        "table_name": "T_OASE_EVENT_COLLECTION_PROGRESS",
        "index_name": "IND_T_OASE_EVENT_COLLECTION_PROGRESS_02",
        "columns": "EVENT_COLLECTION_SETTINGS_ID, AGENT_NAME(512), FETCHED_TIME",
        "requires_oase": True,
    },
    {
        "table_name": "T_ANSL_EXEC_STS_INST_JNL",
        "index_name": "IND_T_ANSL_EXEC_STS_INST_JNL_01",
        "columns": "EXECUTION_NO",
        "requires_oase": False,
    },
]


def check_oase_installed():
    """OASEがインストールされているかチェック
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


def index_exists(ws_db, table_name, index_name):
    """対象テーブルにインデックスが存在するか判定
    Check whether the index already exists on target table
    """
    sql = """
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
        AND table_name = %s
        AND index_name = %s
    """
    rows = ws_db.sql_execute(sql, [table_name, index_name])
    if not rows:
        return False

    count_value = list(rows[0].values())[0]

    return int(count_value) > 0


def main(work_dir_path, ws_db):
    """インデックスを追加する
    Add indexes
    """
    del work_dir_path

    g.applogger.info(f"[Trace][start] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")

    # OASEのインストール確認
    # Check if OASE is installed
    oase_installed = check_oase_installed()

    try:
        # トランザクション開始
        # Start transaction
        ws_db.db_transaction_start()

        for index_def in INDEX_DEFINITIONS:
            table_name = index_def["table_name"]
            index_name = index_def["index_name"]
            columns = index_def["columns"]

            # OASEのインストールが必要なインデックスで、かつOASEがインストールされていない場合はスキップ
            # Skip if the index requires OASE but OASE is not installed
            if index_def["requires_oase"] and not oase_installed:
                g.applogger.info(f"Skipping {index_name}: OASE is not installed.")
                continue

            # インデックスの存在確認
            # Check if the index already exists
            if index_exists(ws_db, table_name, index_name):
                g.applogger.info(f"Index already exists. Skipping: {index_name} on {table_name}")
                continue

            # インデックス作成
            # Create index
            create_index_sql = f"CREATE INDEX {index_name} ON {table_name} ({columns})"
            ws_db.sql_execute(create_index_sql)
            g.applogger.info(f"Created index: {index_name} on {table_name}")

        ws_db.db_transaction_end(True)

    except Exception as e:
        g.applogger.error(f"Failed to add indexes: {str(e)}")
        ws_db.db_transaction_end(False)
        raise

    g.applogger.info(f"[Trace][end] {os.path.splitext(os.path.basename(inspect.currentframe().f_code.co_filename))[0]}")
    return 0
