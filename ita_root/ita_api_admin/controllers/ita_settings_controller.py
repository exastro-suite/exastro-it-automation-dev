#   Copyright 2023 NEC Corporation
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
controller
ita_settings
"""
# import connexion
from flask import g
import json
import os

from common_libs.api import api_filter_admin
from common_libs.common.dbconnect import *  # noqa: F403


@api_filter_admin
def get_ita_settings():  # noqa: E501
    """get_ita_settings

    Organizationで選択可能なドライバの一覧を取得する # noqa: E501


    :rtype: InlineResponse2002
    """

    try:
        # ITA_DB connect
        common_db = DBConnectCommon()  # noqa: F405

        # 『バージョン情報』テーブルからバージョン情報を取得
        ret = common_db.table_select('T_COMN_VERSION', 'WHERE DISUSE_FLAG = %s', [0])

        additional_driver_json = ret[0].get('ADDITIONAL_DRIVER')
        additional_driver = []
        if additional_driver_json is not None:
            additional_driver = json.loads(additional_driver_json)

        # OASEはMongoDBの設定有無でデフォルトのチェック有無を変更する
        mongo_host = os.environ.get('MONGO_HOST', '')

        for driver_data in additional_driver:
            # デフォルトのチェック有無を設定
            if driver_data["id"] == "oase":
                if not mongo_host:
                    driver_data["enable"] = False
                else:
                    driver_data["enable"] = True
            else:
                driver_data["enable"] = True

            # descriptionの言語を選定
            if g.LANGUAGE == "ja":
                if driver_data.get("description_ja"):
                    driver_data["description"] = driver_data.pop("description_ja")
                else:
                    # descriptionの中身がない場合はkeyごと削除
                    del driver_data["description_ja"]
                del driver_data["description_en"]
            else:
                if driver_data.get("description_en"):
                    driver_data["description"] = driver_data.pop("description_en")
                else:
                    # descriptionの中身がない場合はkeyごと削除
                    del driver_data["description_en"]
                del driver_data["description_ja"]

        result_data = {
            'drivers': {
                'options': additional_driver
            }
        }

    finally:
        if "common_db" in locals():
            common_db.db_disconnect()

    return result_data,
