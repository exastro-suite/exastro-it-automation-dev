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

from common_libs.common import *  # noqa: F403
from common_libs.common.dbconnect import DBConnectWs
from common_libs.common import menu_info
from common_libs.common.mongoconnect.mongoconnect import MONGOConnectWs
from common_libs.api import api_filter
from libs.organization_common import check_menu_info, check_auth_menu, check_sheet_type


@api_filter
def get_column_list(organization_id, workspace_id, menu):  # noqa: E501
    """get_column_list

    メニューの項目一覧(REST用項目名)を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2001
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405

    try:
        # メニューの存在確認
        menu_record = check_menu_info(menu, objdbca)

        # 『メニュー-テーブル紐付管理』の取得とシートタイプのチェック
        sheet_type_list = ['0', '1', '2', '3', '4', '5', '6']
        # 28 : 作業管理のシートタイプ追加
        sheet_type_list.append('28')
        check_sheet_type(menu, sheet_type_list, objdbca)

        # メニューに対するロール権限をチェック
        check_auth_menu(menu, objdbca)

        # メニューのカラム情報を取得
        data = menu_info.collect_menu_column_list(objdbca, menu, menu_record)
    except Exception as e:
        raise e
    finally:
        objdbca.db_disconnect()
    return data,


@api_filter
def get_menu_info(organization_id, workspace_id, menu):  # noqa: E501
    """get_menu_info

    メニューの基本情報および項目情報を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse200
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405

    try:
        # メニューの存在確認
        menu_record = check_menu_info(menu, objdbca)

        # 『メニュー-テーブル紐付管理』の取得とシートタイプのチェック
        sheet_type_list = False     # シートタイプはすべて許容
        menu_table_link_record, custom_file_list = menu_info.custom_check_sheet_type(menu, sheet_type_list, objdbca)

        # メニューに対するロール権限をチェック
        privilege = check_auth_menu(menu, objdbca)

        # メニューの基本情報および項目情報の取得
        if len(custom_file_list) == 0:
            data = menu_info.collect_menu_info(objdbca, menu, menu_record, menu_table_link_record, privilege)
        else:
            # 独自メニュー用の基本情報および項目情報の取得
            data = menu_info.collect_custom_menu_info(objdbca, menu, menu_record, privilege, custom_file_list)
    except Exception as e:
        raise e
    finally:
        objdbca.db_disconnect()
    return data,


@api_filter
def get_pulldown_list(organization_id, workspace_id, menu):  # noqa: E501
    """get_pulldown_list

    IDColumn項目のプルダウン選択用の一覧を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str

    :rtype: InlineResponse2002
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405

    try:
        # メニューの存在確認
        menu_record = check_menu_info(menu, objdbca)

        # 『メニュー-テーブル紐付管理』の取得とシートタイプのチェック
        sheet_type_list = ['0', '1', '2', '3', '4', '5', '6']
        # 28 : 作業管理のシートタイプ追加
        sheet_type_list.append('28')
        check_sheet_type(menu, sheet_type_list, objdbca)

        # メニューに対するロール権限をチェック
        check_auth_menu(menu, objdbca)

        # IDColumn項目のプルダウン一覧の取得
        data = menu_info.collect_pulldown_list(objdbca, menu, menu_record)
    except Exception as e:
        raise e
    finally:
        objdbca.db_disconnect()
    return data,


@api_filter
def get_search_candidates(organization_id, workspace_id, menu, column):  # noqa: E501
    """get_search_candidates

    表示フィルタで利用するプルダウン検索の候補一覧を取得する # noqa: E501

    :param organization_id: OrganizationID
    :type organization_id: str
    :param workspace_id: WorkspaceID
    :type workspace_id: str
    :param menu: メニュー名
    :type menu: str
    :param column: REST用項目名
    :type column: str

    :rtype: InlineResponse2003
    """
    # DB接続
    objdbca = DBConnectWs(workspace_id)  # noqa: F405

    try:
        # メニューの存在確認
        menu_record = check_menu_info(menu, objdbca)

        # 『メニュー-テーブル紐付管理』の取得とシートタイプのチェック
        sheet_type_list = ['0', '1', '2', '3', '4', '5', '6']
        # MongoDBからデータを取得するシートタイプを追加。後から追加したことを示すためあえてappendしている。
        # 26 : MongoDBを利用するシートタイプ
        sheet_type_list.append('26')
        # 28 : 作業管理のシートタイプ追加
        sheet_type_list.append('28')
        menu_table_link_record = check_sheet_type(menu, sheet_type_list, objdbca)

        # メニューに対するロール権限をチェック
        check_auth_menu(menu, objdbca)

        # MongoDB向けの処理かどうかで分岐
        if menu_table_link_record[0]["SHEET_TYPE"] == '26':
            wsMongo = MONGOConnectWs()

            # 既存処理もインデックス指定で取得しているため1レコードしか取れない前提で処理して問題ないと判断。
            # 都度インデックス指定でアクセスするのは手間なので先頭のデータでそれぞれ変数を上書きする。
            menu_record = menu_record[0]
            menu_table_link_record = menu_table_link_record[0]

            data = menu_info.collect_search_candidates_from_mongodb(wsMongo, column, menu_record, menu_table_link_record, objdbca)

        else:
            # 対象項目のプルダウン検索候補一覧を取得
            data = menu_info.collect_search_candidates(objdbca, menu, column, menu_record, menu_table_link_record)
    except Exception as e:
        raise e
    finally:
        objdbca.db_disconnect()

        if 'wsMongo' in locals():
            wsMongo.disconnect()
    return data,
