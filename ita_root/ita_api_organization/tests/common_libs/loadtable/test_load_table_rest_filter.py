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
loadTable.rest_filter() のテスト

参照用メニュー(シートタイプ5, 6)の「基準日時(base_datetime)」をバインド変数で渡す修正をテストします:
- 基準日時の値がSQL文字列に直接埋め込まれず、バインド値として渡されること
- プレースホルダ(%s)がクォートで囲まれていないこと
- 他の検索条件と組み合わせた場合に、プレースホルダとバインド値の順序が一致すること
  (参照用検索条件はwhere句の末尾に結合されるため、基準日時のバインド値も末尾になる)
"""

import pytest
from unittest.mock import MagicMock

from common_libs.loadtable.load_table import loadTable


TABLE_NAME = 'V_CMDB_TEST'
PRIMARY_KEY = 'ROW_ID'
BASE_DATETIME = '2024/01/01 00:00:00'


def _make_filter_query(col_name, value):
    """ColumnClass.get_filter_query(NORMAL) と同じ形式の戻り値を生成する"""
    bindkey = "__{}__".format(col_name)
    return {
        "bindkey": bindkey,
        "bindvalue": {bindkey: "%{}%".format(value)},
        "where": " `{}` LIKE {} ".format(col_name, bindkey),
    }


@pytest.fixture(scope='function')
def objdbca():
    """DBアクセスオブジェクトのモック"""
    mock = MagicMock()
    mock.table_select.return_value = []
    mock.table_count.return_value = 0
    return mock


@pytest.fixture(scope='function')
def load_table_factory(app_context_with_mock_g, objdbca):
    """
    DBにアクセスせずにloadTableインスタンスを生成するフィクスチャ
    メニュー情報の取得メソッドをモックに差し替える
    """
    def _factory(sheet_type, restkey_colname=None):
        restkey_colname = restkey_colname or {}

        objmenu = loadTable.__new__(loadTable)
        objmenu.objdbca = objdbca
        objmenu.get_column_list = MagicMock(return_value=[])
        objmenu.get_primary_key = MagicMock(return_value=PRIMARY_KEY)
        objmenu.get_view_name = MagicMock(return_value=TABLE_NAME)
        objmenu.get_table_name = MagicMock(return_value=TABLE_NAME)
        objmenu.get_sheet_type = MagicMock(return_value=sheet_type)
        objmenu.get_sort_key = MagicMock(return_value=None)
        objmenu.get_restkey_list = MagicMock(return_value=list(restkey_colname.keys()))
        objmenu.convert_colname_restkey = MagicMock(return_value=({}, {}, {}))

        def _get_columnclass(rest_key):
            objcolumn = MagicMock()
            col_name = restkey_colname[rest_key]
            objcolumn.get_filter_query.side_effect = lambda search_mode, search_conf: _make_filter_query(col_name, search_conf)
            return objcolumn
        objmenu.get_columnclass = MagicMock(side_effect=_get_columnclass)

        return objmenu
    return _factory


def _get_select_args(objdbca):
    """table_selectに渡された(table_name, where_str, bind_value_list)を取得する"""
    assert objdbca.table_select.call_count == 1
    return objdbca.table_select.call_args.args


@pytest.mark.parametrize(
    "sheet_type",
    ["5", "6"],
    ids=["sheet_type_5_host_operation", "sheet_type_6_operation"],
)
def test_rest_filter_base_datetime_is_bound(load_table_factory, objdbca, sheet_type):
    """
    基準日時の値がバインド値として渡され、SQL文字列に埋め込まれないこと
    """
    objmenu = load_table_factory(sheet_type)
    parameter = {"base_datetime": {"NORMAL": BASE_DATETIME}}

    status_code, result, msg = objmenu.rest_filter(parameter, 'nomal')

    assert status_code == '000-00000'
    table_name, where_str, bind_value_list = _get_select_args(objdbca)
    assert table_name == TABLE_NAME
    assert where_str.startswith('where ')
    assert "tbl.BASE_TIMESTAMP <= %s" in where_str
    assert "'%s'" not in where_str
    assert BASE_DATETIME not in where_str
    assert bind_value_list == [BASE_DATETIME]
    # parameterから基準日時が削除されていること
    assert "base_datetime" not in parameter


@pytest.mark.parametrize(
    "sheet_type",
    ["5", "6"],
    ids=["sheet_type_5_host_operation", "sheet_type_6_operation"],
)
def test_rest_filter_base_datetime_with_quote_is_not_embedded(load_table_factory, objdbca, sheet_type):
    """
    クォートを含む基準日時の値もSQL文字列に埋め込まれず、そのままバインド値として渡されること
    """
    objmenu = load_table_factory(sheet_type)
    base_datetime = "2024/01/01' and '1'='1"
    parameter = {"base_datetime": {"NORMAL": base_datetime}}

    objmenu.rest_filter(parameter, 'nomal')

    table_name, where_str, bind_value_list = _get_select_args(objdbca)
    assert base_datetime not in where_str
    assert "'1'='1" not in where_str
    assert where_str.count('%s') == 1
    assert bind_value_list == [base_datetime]


@pytest.mark.parametrize(
    "sheet_type",
    ["5", "6"],
    ids=["sheet_type_5_host_operation", "sheet_type_6_operation"],
)
def test_rest_filter_base_datetime_with_other_condition_bind_order(load_table_factory, objdbca, sheet_type):
    """
    他の検索条件と組み合わせた場合、プレースホルダとバインド値の順序が一致すること
    (基準日時のバインド値は末尾になる)
    """
    objmenu = load_table_factory(sheet_type, {"host_name": "HOST_NAME", "item_1": "ITEM_1"})
    parameter = {
        "base_datetime": {"NORMAL": BASE_DATETIME},
        "host_name": {"NORMAL": "host01"},
        "item_1": {"NORMAL": "value01"},
    }

    objmenu.rest_filter(parameter, 'nomal')

    table_name, where_str, bind_value_list = _get_select_args(objdbca)
    assert bind_value_list == ["%host01%", "%value01%", BASE_DATETIME]
    assert where_str.count('%s') == len(bind_value_list)

    # プレースホルダの出現順が「検索条件 → 基準日時」であること
    pos_host = where_str.index("`HOST_NAME` LIKE %s")
    pos_item = where_str.index("`ITEM_1` LIKE %s")
    pos_base = where_str.index("tbl.BASE_TIMESTAMP <= %s")
    assert pos_host < pos_item < pos_base


@pytest.mark.parametrize(
    "sheet_type",
    ["5", "6"],
    ids=["sheet_type_5_host_operation", "sheet_type_6_operation"],
)
def test_rest_filter_without_base_datetime(load_table_factory, objdbca, sheet_type):
    """
    基準日時の指定が無い場合、基準日時の条件・バインド値が追加されないこと
    """
    objmenu = load_table_factory(sheet_type, {"host_name": "HOST_NAME"})
    parameter = {"host_name": {"NORMAL": "host01"}}

    objmenu.rest_filter(parameter, 'nomal')

    table_name, where_str, bind_value_list = _get_select_args(objdbca)
    assert "tbl.BASE_TIMESTAMP <=" not in where_str
    assert "select max(BASE_TIMESTAMP)" in where_str
    assert bind_value_list == ["%host01%"]
    assert where_str.count('%s') == len(bind_value_list)


@pytest.mark.parametrize(
    "sheet_type",
    ["5", "6"],
    ids=["sheet_type_5_host_operation", "sheet_type_6_operation"],
)
def test_rest_filter_base_datetime_count_mode(load_table_factory, objdbca, sheet_type):
    """
    件数取得(count)でも、基準日時がバインド値として末尾に渡されること
    """
    objdbca.table_count.return_value = 3
    objmenu = load_table_factory(sheet_type, {"host_name": "HOST_NAME"})
    parameter = {
        "base_datetime": {"NORMAL": BASE_DATETIME},
        "host_name": {"NORMAL": "host01"},
    }

    status_code, result, msg = objmenu.rest_filter(parameter, 'count')

    assert result == 3
    objdbca.table_select.assert_not_called()
    assert objdbca.table_count.call_count == 1
    table_name, where_str, bind_value_list = objdbca.table_count.call_args.args
    assert BASE_DATETIME not in where_str
    assert bind_value_list == ["%host01%", BASE_DATETIME]
    assert where_str.count('%s') == len(bind_value_list)


def test_rest_filter_base_datetime_ignored_for_non_reference_sheet(load_table_factory, objdbca):
    """
    参照用以外のシートタイプでは、基準日時の条件が生成されないこと
    """
    objmenu = load_table_factory("1", {"host_name": "HOST_NAME"})
    parameter = {"host_name": {"NORMAL": "host01"}}

    objmenu.rest_filter(parameter, 'nomal')

    table_name, where_str, bind_value_list = _get_select_args(objdbca)
    assert "BASE_TIMESTAMP" not in where_str
    assert bind_value_list == ["%host01%"]
