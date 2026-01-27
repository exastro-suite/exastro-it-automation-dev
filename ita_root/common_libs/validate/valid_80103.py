# Copyright 2025 NEC Corporation#
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
from flask import g
import json

from common_libs.terraform_driver.cloud_ep.terraform_restapi import *  # noqa: F403


def external_valid_menu_before(objdbca, objtable, option):
    retBool = True
    msg = ''

    # 削除時はチェックしない
    # Do not check when deleting
    if option.get("cmd_type") == "Delete":
        return retBool, msg, option

    # 入力値取得
    entry_parameter = option.get('entry_parameter').get('parameter')
    # current_parameter = option.get('current_parameter').get('parameter')
    cmd_type = option.get("cmd_type")
    tf_org_name_uuid = entry_parameter.get('tf_organization_name')
    pj_name = entry_parameter.get('tf_project_name')

    # 該当のProjectが存在することを確認する(廃止時はチェックしない)
    if not cmd_type == "Discard":
        # デフォルトプロジェクトを使用するなら存在確認はスキップ
        if pj_name is None:
            return retBool, msg, option,

        # org_name_uuidにはOrganization管理のUUIDが渡ってくるので、APIリクエスト用にオーガナイゼーション名に変換する
        where_str = 'WHERE ORGANIZATION_ID = %s AND DISUSE_FLAG = %s'
        ret = objdbca.table_select("T_TERE_ORGANIZATION", where_str, [tf_org_name_uuid, 0])
        if not ret or len(ret) != 1:
            log_msg = g.appmsg.get_log_message("MSG-82041", [tf_org_name_uuid])
            g.applogger.info(log_msg)
            msg = g.appmsg.get_api_message("MSG-82041", [tf_org_name_uuid])
            retBool = False
            return retBool, msg, option,
        org_name = ret[0].get('ORGANIZATION_NAME')

        # RESTAPIコールクラスのためにインターフェース情報を取得
        ret, interface_info_data = get_intarface_info_data(objdbca)  # noqa: F405
        if not ret:
            log_msg = g.appmsg.get_log_message("MSG-82001", [])
            g.applogger.info(log_msg)
            msg = g.appmsg.get_api_message("MSG-82001", [])
            retBool = False
            return retBool, msg, option,

        # RESTAPIコールクラス
        ret, restApiCaller = call_restapi_class(interface_info_data)  # noqa: F405
        if not ret:
            log_msg = g.appmsg.get_log_message("MSG-82002", [])
            g.applogger.info(log_msg)
            msg = g.appmsg.get_api_message("MSG-82002", [])
            retBool = False
            return retBool, msg, option,

        # ページネーション対応
        respons_contents_data = []
        next_query = "?page[number]=1&page[size]=20"
        while next_query is not None:
            # Project一覧取得
            response_array = get_tf_project_list(restApiCaller, org_name, next_query)  # noqa: F405
            response_status_code = response_array.get('statusCode')
            # ステータスコードが200以外の場合はエラー判定
            if not response_status_code == 200:
                log_msg = g.appmsg.get_log_message("MSG-82042", [])
                g.applogger.info(log_msg)
                msg = "[API Error]" + g.appmsg.get_api_message("MSG-82042", []) + " StatusCode:" + str(response_status_code)
                retBool = False
                return retBool, msg, option,

            # 取得したProject一覧から、該当のProjectが存在するか確認
            respons_contents_json = response_array.get('responseContents')
            respons_contents = json.loads(respons_contents_json)
            respons_contents_data.extend(respons_contents.get('data'))
            next_page = respons_contents.get("meta", {}).get("pagination", {}).get("next-page")
            if next_page is not None:
                next_query = "?page[number]=" + str(next_page) + "&page[size]=20"
            else:
                next_query = None

        pj_exist_flag = False
        for data in respons_contents_data:
            attributes = data.get('attributes')
            if pj_name == attributes.get('name'):
                pj_exist_flag = True
                break

        # 該当ProjectがTerraformに登録されていない場合はバリデエラー
        if not pj_exist_flag:
            log_msg = g.appmsg.get_log_message("MSG-82043", [])
            g.applogger.info(log_msg)
            msg = g.appmsg.get_api_message("MSG-82043", [])
            retBool = False
            return retBool, msg, option,

    return retBool, msg, option,
