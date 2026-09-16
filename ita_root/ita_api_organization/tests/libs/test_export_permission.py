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

"""
エクスポート権限チェック機能のテスト

今回追加した以下の機能をテストします:
- _get_write_permission_menu_id_list(): EXPORT_PERMISSION_CHECK_FLG を考慮した権限フィルタ
- check_export_menu_permission(): エクスポート実行時の権限チェック
"""

import pytest
from unittest.mock import MagicMock
from flask import g

from libs.export_import import _get_write_permission_menu_id_list, check_export_menu_permission, check_import_menu_permission
from common_libs.common.exception import AppException


@pytest.fixture
def mock_objdbca():
    """モックDBコネクションを返すフィクスチャ"""
    objdbca = MagicMock()
    return objdbca


@pytest.fixture
def mock_g_with_roles(app_context_with_mock_g):
    """g.ROLES と g.LANGUAGE を設定するフィクスチャ"""
    g.ROLES = ['role1']
    g.LANGUAGE = 'ja'
    g.appmsg.get_api_message.return_value = "権限エラーメッセージ"
    g.applogger = MagicMock()
    yield


class TestGetWritePermissionMenuIdList:
    """_get_write_permission_menu_id_list() のテスト"""

    def test_empty_list(self, mock_objdbca, mock_g_with_roles):
        """空リストを渡した場合、空リストが返る"""
        result = _get_write_permission_menu_id_list(mock_objdbca, [])
        assert result == []

    def test_all_flag_0_menus(self, mock_objdbca, mock_g_with_roles):
        """すべて EXPORT_PERMISSION_CHECK_FLG='0' のメニューは権限チェックをスキップ"""
        menu_id_list = ['10203', '10204', '50102']

        # T_COMN_MENU から EXPORT_PERMISSION_CHECK_FLG を取得
        mock_objdbca.table_select.return_value = [
            {'MENU_ID': '10203', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
            {'MENU_ID': '10204', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
            {'MENU_ID': '50102', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
        ]

        result = _get_write_permission_menu_id_list(mock_objdbca, menu_id_list)

        # FLAG=0 なので全部返る（権限チェックなし）
        assert result == ['10203', '10204', '50102']
        # table_select は T_COMN_MENU のみ（T_COMN_ROLE_MENU_LINK は呼ばれない）
        assert mock_objdbca.table_select.call_count == 1

    def test_all_flag_1_with_write_permission(self, mock_objdbca, mock_g_with_roles):
        """すべて EXPORT_PERMISSION_CHECK_FLG='1' かつ書き込み権限あり"""
        menu_id_list = ['10101', '10102', '10201']

        # T_COMN_MENU から EXPORT_PERMISSION_CHECK_FLG を取得
        # 2回目の呼び出しは T_COMN_ROLE_MENU_LINK
        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10201', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 2回目: T_COMN_ROLE_MENU_LINK (書き込み権限あり)
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
                {'MENU_ID': '10102', 'PRIVILEGE': '0'},
                {'MENU_ID': '10201', 'PRIVILEGE': '1'},
            ],
        ]

        result = _get_write_permission_menu_id_list(mock_objdbca, menu_id_list)

        # 全部書き込み権限があるので全部返る
        assert result == ['10101', '10102', '10201']
        assert mock_objdbca.table_select.call_count == 2

    def test_flag_1_without_write_permission(self, mock_objdbca, mock_g_with_roles):
        """EXPORT_PERMISSION_CHECK_FLG='1' で書き込み権限なし"""
        menu_id_list = ['10101', '10102']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 2回目: T_COMN_ROLE_MENU_LINK (10101のみ権限あり)
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        result = _get_write_permission_menu_id_list(mock_objdbca, menu_id_list)

        # 10101 のみ権限があるので返る
        assert result == ['10101']

    def test_mixed_flag_0_and_flag_1(self, mock_objdbca, mock_g_with_roles):
        """FLAG=0 と FLAG=1 が混在"""
        menu_id_list = ['10203', '10101', '50102', '10102']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10203', 'EXPORT_PERMISSION_CHECK_FLG': '0'},  # チェックスキップ
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},  # チェック必要
                {'MENU_ID': '50102', 'EXPORT_PERMISSION_CHECK_FLG': '0'},  # チェックスキップ
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},  # チェック必要
            ],
            # 2回目: T_COMN_ROLE_MENU_LINK (10101のみ権限あり)
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        result = _get_write_permission_menu_id_list(mock_objdbca, menu_id_list)

        # FLAG=0 の 10203, 50102 と、権限ありの 10101 が返る
        # 10102 は FLAG=1 で権限なしなので除外
        assert result == ['10203', '10101', '50102']

    def test_preserve_order(self, mock_objdbca, mock_g_with_roles):
        """入力の順序が維持される"""
        menu_id_list = ['50102', '10203', '10101']

        mock_objdbca.table_select.side_effect = [
            [
                {'MENU_ID': '50102', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
                {'MENU_ID': '10203', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        result = _get_write_permission_menu_id_list(mock_objdbca, menu_id_list)

        # 入力順序が維持される
        assert result == ['50102', '10203', '10101']


class TestCheckExportMenuPermission:
    """check_export_menu_permission() のテスト"""

    def test_empty_menu_list(self, mock_objdbca, mock_g_with_roles):
        """空リストの場合は何もしない"""
        # 例外が投げられないことを確認
        check_export_menu_permission(mock_objdbca, [])

    def test_all_menus_have_write_permission(self, mock_objdbca, mock_g_with_roles):
        """すべてのメニューに書き込み権限がある場合"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10101', 'MENU_NAME_REST': 'menu1', 'MENU_NAME_JA': 'メニュー1', 'MENU_NAME_EN': 'Menu 1'},
                {'MENU_ID': '10102', 'MENU_NAME_REST': 'menu2', 'MENU_NAME_JA': 'メニュー2', 'MENU_NAME_EN': 'Menu 2'},
            ],
            # 2回目: T_COMN_MENU (EXPORT_PERMISSION_CHECK_FLG)
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
                {'MENU_ID': '10102', 'PRIVILEGE': '0'},
            ],
        ]

        # 例外が投げられないことを確認
        check_export_menu_permission(mock_objdbca, menu_rest_list)

    def test_no_write_permission_raises_exception(self, mock_objdbca, mock_g_with_roles):
        """書き込み権限がないメニューがある場合、例外が投げられる"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10101', 'MENU_NAME_REST': 'menu1', 'MENU_NAME_JA': 'メニュー1', 'MENU_NAME_EN': 'Menu 1'},
                {'MENU_ID': '10102', 'MENU_NAME_REST': 'menu2', 'MENU_NAME_JA': 'メニュー2', 'MENU_NAME_EN': 'Menu 2'},
            ],
            # 2回目: T_COMN_MENU (EXPORT_PERMISSION_CHECK_FLG)
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK (10101のみ権限あり)
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        with pytest.raises(AppException) as exc_info:
            check_export_menu_permission(mock_objdbca, menu_rest_list)

        # エラーコードが 401-00001 であることを確認
        assert exc_info.value.args[0] == "401-00001"
        # メニュー名が含まれていることを確認
        assert 'メニュー2' in exc_info.value.args[2][0]

    def test_flag_0_menu_skip_permission_check(self, mock_objdbca, mock_g_with_roles):
        """EXPORT_PERMISSION_CHECK_FLG='0' のメニューは権限チェックをスキップ"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10203', 'MENU_NAME_REST': 'menu1', 'MENU_NAME_JA': 'メニュー-テーブル紐付管理', 'MENU_NAME_EN': 'Menu-Table link'},
                {'MENU_ID': '10102', 'MENU_NAME_REST': 'menu2', 'MENU_NAME_JA': 'メニュー2', 'MENU_NAME_EN': 'Menu 2'},
            ],
            # 2回目: T_COMN_MENU (EXPORT_PERMISSION_CHECK_FLG)
            [
                {'MENU_ID': '10203', 'EXPORT_PERMISSION_CHECK_FLG': '0'},  # チェックスキップ
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK (10102の権限あり)
            [
                {'MENU_ID': '10102', 'PRIVILEGE': '1'},
            ],
        ]

        # 例外が投げられないことを確認（10203 は FLAG=0 なのでチェックスキップ）
        check_export_menu_permission(mock_objdbca, menu_rest_list)

    def test_all_flag_0_menus(self, mock_objdbca, mock_g_with_roles):
        """すべて EXPORT_PERMISSION_CHECK_FLG='0' の場合、権限チェック自体がスキップ"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {'MENU_ID': '10203', 'MENU_NAME_REST': 'menu1', 'MENU_NAME_JA': 'メニュー1', 'MENU_NAME_EN': 'Menu 1'},
                {'MENU_ID': '50102', 'MENU_NAME_REST': 'menu2', 'MENU_NAME_JA': 'メニュー2', 'MENU_NAME_EN': 'Menu 2'},
            ],
            # 2回目: T_COMN_MENU (EXPORT_PERMISSION_CHECK_FLG)
            [
                {'MENU_ID': '10203', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
                {'MENU_ID': '50102', 'EXPORT_PERMISSION_CHECK_FLG': '0'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK は呼ばれない（全部 FLAG=0）
        ]

        # 例外が投げられないことを確認
        check_export_menu_permission(mock_objdbca, menu_rest_list)
        # T_COMN_ROLE_MENU_LINK へのクエリは実行されない
        assert mock_objdbca.table_select.call_count == 2


class TestCheckImportMenuPermission:
    """check_import_menu_permission() のテスト"""

    def test_empty_menu_list(self, mock_objdbca, mock_g_with_roles):
        """空リストの場合は何もしない"""
        check_import_menu_permission(mock_objdbca, [])

    def test_all_new_menus(self, mock_objdbca, mock_g_with_roles):
        """すべて新規メニュー（存在しない）の場合は権限チェックしない"""
        menu_rest_list = ['new_menu1', 'new_menu2']

        # T_COMN_MENU に該当メニューが存在しない
        mock_objdbca.table_select.return_value = []

        # 例外が投げられないことを確認
        check_import_menu_permission(mock_objdbca, menu_rest_list)

    def test_existing_menu_with_flag_0(self, mock_objdbca, mock_g_with_roles):
        """既存メニューで FLAG=0 の場合は権限チェックしない"""
        menu_rest_list = ['menu1', 'menu2']

        # T_COMN_MENU から既存メニューを取得（すべて FLAG=0）
        mock_objdbca.table_select.return_value = [
            {
                'MENU_ID': '10203',
                'MENU_NAME_REST': 'menu1',
                'MENU_NAME_JA': 'メニュー-テーブル紐付管理',
                'MENU_NAME_EN': 'Menu-Table link',
                'EXPORT_PERMISSION_CHECK_FLG': '0'
            },
            {
                'MENU_ID': '50102',
                'MENU_NAME_REST': 'menu2',
                'MENU_NAME_JA': 'パラメータシート定義一覧',
                'MENU_NAME_EN': 'Parameter sheet definition list',
                'EXPORT_PERMISSION_CHECK_FLG': '0'
            },
        ]

        # 例外が投げられないことを確認（FLAG=0 なので権限チェックスキップ）
        check_import_menu_permission(mock_objdbca, menu_rest_list)
        # T_COMN_MENU のみ呼ばれる（_get_write_permission_menu_id_list は呼ばれない）
        assert mock_objdbca.table_select.call_count == 1

    def test_existing_menu_with_flag_1_and_write_permission(self, mock_objdbca, mock_g_with_roles):
        """既存メニューで FLAG=1 かつ書き込み権限あり"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {
                    'MENU_ID': '10101',
                    'MENU_NAME_REST': 'menu1',
                    'MENU_NAME_JA': 'メニュー1',
                    'MENU_NAME_EN': 'Menu 1',
                    'EXPORT_PERMISSION_CHECK_FLG': '1'
                },
                {
                    'MENU_ID': '10102',
                    'MENU_NAME_REST': 'menu2',
                    'MENU_NAME_JA': 'メニュー2',
                    'MENU_NAME_EN': 'Menu 2',
                    'EXPORT_PERMISSION_CHECK_FLG': '1'
                },
            ],
            # 2回目: T_COMN_MENU (_get_write_permission_menu_id_list 内)
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
                {'MENU_ID': '10102', 'PRIVILEGE': '0'},
            ],
        ]

        # 例外が投げられないことを確認
        check_import_menu_permission(mock_objdbca, menu_rest_list)

    def test_existing_menu_with_flag_1_without_write_permission(self, mock_objdbca, mock_g_with_roles):
        """既存メニューで FLAG=1 だが書き込み権限なし → 例外"""
        menu_rest_list = ['menu1', 'menu2']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU
            [
                {
                    'MENU_ID': '10101',
                    'MENU_NAME_REST': 'menu1',
                    'MENU_NAME_JA': 'メニュー1',
                    'MENU_NAME_EN': 'Menu 1',
                    'EXPORT_PERMISSION_CHECK_FLG': '1'
                },
                {
                    'MENU_ID': '10102',
                    'MENU_NAME_REST': 'menu2',
                    'MENU_NAME_JA': 'メニュー2',
                    'MENU_NAME_EN': 'Menu 2',
                    'EXPORT_PERMISSION_CHECK_FLG': '1'
                },
            ],
            # 2回目: T_COMN_MENU (_get_write_permission_menu_id_list 内)
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
                {'MENU_ID': '10102', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK (10101のみ権限あり)
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        with pytest.raises(AppException) as exc_info:
            check_import_menu_permission(mock_objdbca, menu_rest_list)

        # エラーコードが 401-00001 であることを確認
        assert exc_info.value.args[0] == "401-00001"
        # メニュー名が含まれていることを確認
        assert 'メニュー2' in exc_info.value.args[2][0]

    def test_mixed_new_and_existing_menus(self, mock_objdbca, mock_g_with_roles):
        """新規メニューと既存メニューが混在"""
        menu_rest_list = ['new_menu', 'existing_menu_flag0', 'existing_menu_flag1']

        mock_objdbca.table_select.side_effect = [
            # 1回目: T_COMN_MENU (new_menu は存在しない、他2つは既存)
            [
                {
                    'MENU_ID': '10203',
                    'MENU_NAME_REST': 'existing_menu_flag0',
                    'MENU_NAME_JA': 'メニュー-テーブル紐付管理',
                    'MENU_NAME_EN': 'Menu-Table link',
                    'EXPORT_PERMISSION_CHECK_FLG': '0'
                },
                {
                    'MENU_ID': '10101',
                    'MENU_NAME_REST': 'existing_menu_flag1',
                    'MENU_NAME_JA': 'メニュー1',
                    'MENU_NAME_EN': 'Menu 1',
                    'EXPORT_PERMISSION_CHECK_FLG': '1'
                },
            ],
            # 2回目: T_COMN_MENU (_get_write_permission_menu_id_list 内、10101のみ)
            [
                {'MENU_ID': '10101', 'EXPORT_PERMISSION_CHECK_FLG': '1'},
            ],
            # 3回目: T_COMN_ROLE_MENU_LINK
            [
                {'MENU_ID': '10101', 'PRIVILEGE': '1'},
            ],
        ]

        # 例外が投げられないことを確認
        # new_menu: 新規なのでチェックスキップ
        # existing_menu_flag0: FLAG=0 なのでチェックスキップ
        # existing_menu_flag1: FLAG=1 で書き込み権限あり
        check_import_menu_permission(mock_objdbca, menu_rest_list)
