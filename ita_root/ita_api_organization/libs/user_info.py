#   Copyright 2022 NEC Corporation
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

import json
from common_libs.common import *  # noqa: F403
from flask import g
from libs.organization_common import check_auth_menu, get_auth_menus
from common_libs.common.exception import AppException


def collect_menu_group_panels(objdbca):
    """
        メニューグループの画像を取得する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            panels_data
    """
    # テーブル名
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_group = 'T_COMN_MENU_GROUP'

    # 変数定義
    workspace_id = g.get('WORKSPACE_ID')
    menu_group_list_id = '10102'  # 「メニューグループ管理」メニューのID
    column_name_rest = 'menu_group_icon'  # カラム名

    # 『メニュー管理』テーブルからメニューの一覧を取得
    ret = objdbca.table_select(t_common_menu, 'WHERE DISUSE_FLAG = %s ORDER BY MENU_GROUP_ID ASC, DISP_SEQ ASC', [0])

    menu_rest_names = []
    for recode in ret:
        menu_rest_names.append(recode.get('MENU_NAME_REST'))

    auth_menu_list = get_auth_menus(menu_rest_names, objdbca)

    menu_groups = []
    for menu_item in auth_menu_list:
        # 権限のあるメニューのメニューグループを格納
        menu_group_id = menu_item.get('MENU_GROUP_ID')
        menu_groups.append(menu_group_id)

    # 重複を除外
    menu_groups = list(set(menu_groups))

    # 『メニューグループ管理』テーブルからメニューグループの一覧を取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [0])

    panels_data = {}
    for recode in ret:
        # メニューグループに権限のあるメニューが1つもない場合は除外
        menu_group_id = recode.get('MENU_GROUP_ID')
        if menu_group_id not in menu_groups:
            continue

        # 対象ファイルの格納先を取得
        file_name = recode.get('MENU_GROUP_ICON')
        file_paths = get_upload_file_path(workspace_id, menu_group_list_id, menu_group_id, column_name_rest, file_name, '')  # noqa: F405

        # 対象ファイルをbase64エンコード
        encoded = file_encode(file_paths.get('file_path'))  # noqa: F405
        if not encoded:
            encoded = None

        panels_data[menu_group_id] = encoded

    return panels_data


def collect_user_auth(objdbca):
    """
        ユーザの権限情報を取得する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            user_auth_data
    """

    # ユーザIDを取得
    user_id = g.get('USER_ID')

    # ユーザ名を取得
    user_name = util.get_user_name(user_id)

    # workspaceに所属するロールを取得
    workspace_roles = util.get_workspace_roles()

    # ユーザが所属するロールのうち、workspaceに所属するロールを抽出
    roles = []
    for user_role in g.ROLES:
        if user_role in workspace_roles:
            roles.append(user_role)

    # Workspaceを取得
    workspaces = util.get_exastro_platform_workspaces()[0]

    # Webテーブル設定を取得
    ret = objdbca.table_select('T_COMN_WEB_TABLE_SETTINGS', 'WHERE USER_ID = %s', g.USER_ID)

    # メニューグループごとのメニュー一覧を作成
    if len(ret) == 0:
        web_table_settings = None
    else:
        if (ret[0]['WEB_TABLE_SETTINGS'] is None) or (len(ret[0]['WEB_TABLE_SETTINGS']) == 0):
            web_table_settings = None
        else:
            web_table_settings = json.loads(ret[0]['WEB_TABLE_SETTINGS'])

    user_auth_data = {
        "user_id": user_id,
        "user_name": user_name,
        "roles": roles,
        "workspaces": workspaces,
        "web_table_settings": web_table_settings
    }

    return user_auth_data


def collect_menus(objdbca):
    """
        ユーザがアクセス可能なメニューグループ・メニューの一覧を取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            menus_data
    """
    # テーブル名
    t_common_menu = 'T_COMN_MENU'
    t_common_menu_group = 'T_COMN_MENU_GROUP'

    # 変数定義
    lang = g.get('LANGUAGE')

    # 『メニュー管理』テーブルからメニューの一覧を取得
    ret = objdbca.table_select(t_common_menu, 'WHERE DISUSE_FLAG = %s ORDER BY MENU_GROUP_ID ASC, DISP_SEQ ASC', [0])

    # メニューグループごとのメニュー一覧を作成
    menu_rest_names = []
    for recode in ret:
        menu_rest_names.append(recode.get('MENU_NAME_REST'))

    auth_menu_list = get_auth_menus(menu_rest_names, objdbca)

    menus = {}
    for recode in auth_menu_list:
        menu_group_id = recode.get('MENU_GROUP_ID')
        if menu_group_id not in menus:
            menus[menu_group_id] = []

        add_menu = {}
        add_menu['id'] = recode.get('MENU_ID')
        add_menu['menu_name'] = recode.get('MENU_NAME_' + lang.upper())
        add_menu['menu_name_rest'] = recode.get('MENU_NAME_REST')
        add_menu['disp_seq'] = recode.get('DISP_SEQ')
        menus[menu_group_id].append(add_menu)

    # 『メニューグループ管理』テーブルからメニューグループの一覧を取得
    ret = objdbca.table_select(t_common_menu_group, 'WHERE DISUSE_FLAG = %s ORDER BY DISP_SEQ ASC', [0])

    # メニューグループの一覧を作成し、メニュー一覧も格納する
    menu_group_list = []
    for recode in ret:
        exclusion_flag = False
        # メニューグループに権限のあるメニューが1つもない場合は除外
        menu_group_id = recode.get('MENU_GROUP_ID')
        target_menus = menus.get(menu_group_id)
        if not target_menus:
            # 自分自身を親メニューグループとしているメニューグループを確認し、そのメニューグループに権限のあるメニューがあるかを確認
            for recode2 in ret:
                exclusion_flag = True
                parent_id = recode2.get('PARENT_MENU_GROUP_ID')
                if parent_id == menu_group_id:
                    child_menu_group_id = recode2.get('MENU_GROUP_ID')
                    child_target_menus = menus.get(child_menu_group_id)
                    if child_target_menus:
                        exclusion_flag = False
                        target_menus = child_target_menus
                        break
                else:
                    continue
        # exclusion_flagがTrueの場合は除外対象とする
        if exclusion_flag:
            continue

        add_menu_group = {}
        add_menu_group['parent_id'] = recode.get('PARENT_MENU_GROUP_ID')
        add_menu_group['id'] = menu_group_id
        add_menu_group['menu_group_name'] = recode.get('MENU_GROUP_NAME_' + lang.upper())
        add_menu_group['disp_seq'] = recode.get('DISP_SEQ')
        add_menu_group['menus'] = target_menus

        menu_group_list.append(add_menu_group)

    menus_data = {
        "menu_groups": menu_group_list,
    }

    return menus_data


def regist_table_settings(objdbca, parameter):
    """
        Webのテーブル設定を登録する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            parameter: bodyの中身
        RETRUN:
            data
    """
    # DBコネクション開始
    objdbca.db_transaction_start()

    # Webテーブル設定を取得
    ret = objdbca.table_select('T_COMN_WEB_TABLE_SETTINGS', 'WHERE USER_ID = %s', g.USER_ID)

    # メニューグループごとのメニュー一覧を作成

    data_list = {
        'USER_ID': g.USER_ID,
        'WEB_TABLE_SETTINGS': str(json.dumps(parameter)),
    }
    if len(ret) == 0:

        # Webテーブル設定にINSERT
        ret = objdbca.table_insert('T_COMN_WEB_TABLE_SETTINGS', data_list, 'ROW_ID', False)
    else:
        data_list['ROW_ID'] = ret[0]['ROW_ID']
        # Webテーブル設定にUPDATE
        ret = objdbca.table_update('T_COMN_WEB_TABLE_SETTINGS', data_list, 'ROW_ID', False)

    # DBコネクション終了
    objdbca.db_transaction_end(True)

    return g.appmsg.get_api_message("000-00001")


def collect_widget_settings(objdbca):
    """
        Dashboardのwidget設定を取得
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
        RETRUN:
            widget_data
    """

    # 応答情報の初期化
    widget_data = {}
    widget_data['data'] = []
    widget_data['menu'] = {}
    widget_data['widget'] = []
    widget_data['movement'] = {}
    widget_data['work_info'] = {}
    widget_data['work_result'] = {}

    # メニュー情報の取得
    menu_info = {}
    menu_info['101'] = {}
    menu_info['101']['name'] = ''
    menu_info['101']['order'] = 0
    menu_info['101']['icon'] = ''
    menu_info['101']['remarks'] = ''
    menu_info['101']['position'] = ''

    # widget情報の取得
    widget_list = []

    widget_info = {}
    widget_info['widget_id'] = '1'
    widget_info['name'] = ''
    widget_info['display_name'] = ''
    widget_info['colspan'] = ''
    widget_info['rowspan'] = ''
    widget_info['display'] = ''
    widget_info['title'] = ''
    widget_info['background'] = ''
    widget_info['data'] = {}
    widget_info['data']['menu_col_number'] = ''
    widget_info['set_id'] = ''
    widget_info['area'] = ''
    widget_info['row'] = ''
    widget_info['col'] = ''

    widget_list.append(widget_info)

    # Movement情報の取得
    movement_info = {}
    movement_info['3'] = {}
    movement_info['3']['name'] = ''
    movement_info['3']['menu_id'] = ''
    movement_info['3']['number'] = 0

    # 作業状況の取得
    work_info = {}
    work_info['conductor'] = []

    conductor_info = {}
    conductor_info['2'] = {}
    conductor_info['2']['status'] = ''
    conductor_info['2']['end'] = 'YYYY-MM-DD HH:MI:SS.nnnnnn'

    work_info['conductor'].append(conductor_info)

    # 作業結果の取得
    work_result_info = {}
    work_result_info['conductor'] = []

    conductor_info = {}
    conductor_info['1'] = {}
    conductor_info['1']['status'] = ''
    conductor_info['1']['end'] = 'YYYY-MM-DD HH:MI:SS.nnnnnn'

    work_result_info['conductor'].append(conductor_info)

    # 応答情報の作成
    widget_data['menu'] = menu_info
    widget_data['widget'] = widget_list
    widget_data['movement'] = movement_info
    widget_data['work_info'] = work_info
    widget_data['work_result'] = work_result_info

    return widget_data


def regist_widget_settings(objdbca, parameter):
    """
        Dashboardのwidget設定を登録する
        ARGS:
            objdbca:DB接クラス  DBConnectWs()
            parameter: bodyの中身
        RETRUN:
            data
    """
    # DBコネクション開始
    objdbca.db_transaction_start()


    # DBコネクション終了
    objdbca.db_transaction_end(True)

    return g.appmsg.get_api_message("000-00001")

