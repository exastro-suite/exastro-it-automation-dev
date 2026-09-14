"""テストデータ生成の共通ヘルパー（create_*）

解析結果（mov_vars_dict）と DB の行（T_ANSR_MVMT_VAR_LINK / T_ANSR_NESTVAR_MEMBER）を組み立てる。
テストの意図が read しやすくなるよう、キー構成の知識はここに閉じ込める。
"""

# テーブル名
TABLE_MVMT_VAR_LINK = "T_ANSR_MVMT_VAR_LINK"
TABLE_NESTVAR_MEMBER = "T_ANSR_NESTVAR_MEMBER"

# AnscConst.GC_VARS_ATTR_* と同値（テスト側で意図が読めるように再掲）
ATTR_STD = '1'       # 一般変数
ATTR_LIST = '2'      # 複数具体値
ATTR_M_ARRAY = '3'   # 多段変数

TEST_USER_ID = "test_user_id"
OLD_USER_ID = "old_user_id"


def create_variable(var_name, var_attr, var_struct=None):
    """Variable を生成する"""
    from backyard_libs.ansible_driver.classes.VariableClass import Variable

    return Variable(var_name, var_attr, var_struct)


def create_mov_vars_dict(specs):
    """解析結果（backyard_main.py の mov_vars_dict）を組み立てる

    Arguments:
        specs: {movement_id: [(var_name, var_attr[, var_struct]), ...]}

    Returns:
        {movement_id: VariableManager}
    """
    from backyard_libs.ansible_driver.classes.VariableManagerClass import VariableManager

    mov_vars_dict = {}
    for movement_id, var_specs in specs.items():
        varmng = VariableManager()
        for var_spec in var_specs:
            var_name, var_attr = var_spec[0], var_spec[1]
            var_struct = var_spec[2] if len(var_spec) > 2 else None
            varmng.add_variable(create_variable(var_name, var_attr, var_struct))
        mov_vars_dict[movement_id] = varmng

    return mov_vars_dict


def create_link_row(link_id, movement_id, vars_name, var_attr, disuse_flag='0', note='initial note'):
    """T_ANSR_MVMT_VAR_LINK の 1 行を組み立てる

    NOTE は「更新対象外のカラムが巻き戻らない/書き換わらないこと」を検証するための番人。
    """
    return {
        'MVMT_VAR_LINK_ID': link_id,
        'MOVEMENT_ID': movement_id,
        'VARS_NAME': vars_name,
        'VARS_ATTRIBUTE_01': var_attr,
        'NOTE': note,
        'DISUSE_FLAG': disuse_flag,
        'LAST_UPDATE_USER': OLD_USER_ID,
        'LAST_UPDATE_TIMESTAMP': '2026-01-01 00:00:00',
    }


def create_chain_array_item(vars_key_id, vars_name, parent_vars_key_id='0', array_nest_level='1',
                            assign_seq_need='0', col_seq_member='0', col_seq_need='0',
                            member_disp='1', max_col_seq='0', vars_name_path=None, vars_name_alias=None):
    """Variable.var_struct['CHAIN_ARRAY'] の 1 要素を組み立てる

    キー構成は CheckAnsibleRoleFiles.MakeMultiArrayToLastVarChainArray() の生成物に合わせている。
    MVMT_VAR_LINK_ID は NestVarsMemberTable が付与するのでここには含めない。
    """
    return {
        'PARENT_VARS_KEY_ID': parent_vars_key_id,
        'VARS_KEY_ID': vars_key_id,
        'VARS_NAME': vars_name,
        'ARRAY_NEST_LEVEL': array_nest_level,
        'ASSIGN_SEQ_NEED': assign_seq_need,
        'COL_SEQ_MEMBER': col_seq_member,
        'COL_SEQ_NEED': col_seq_need,
        'MEMBER_DISP': member_disp,
        'VRAS_NAME_PATH': vars_name_path if vars_name_path is not None else f"path/{vars_name}",
        'VRAS_NAME_ALIAS': vars_name_alias if vars_name_alias is not None else f"alias_{vars_name}",
        'MAX_COL_SEQ': max_col_seq,
    }


def create_nest_var_struct(member_names=('member1',)):
    """多段変数の var_struct を組み立てる"""
    return {
        'CHAIN_ARRAY': [
            create_chain_array_item(vars_key_id=str(idx + 1), vars_name=member_name)
            for idx, member_name in enumerate(member_names)
        ],
    }


def create_member_row(member_id, link_id, chain_array_item, disuse_flag='0'):
    """T_ANSR_NESTVAR_MEMBER の 1 行を、対応する CHAIN_ARRAY 要素から組み立てる"""
    row = dict(chain_array_item)
    row.pop('COL_SEQ_MEMBER')
    row['ARRAY_MEMBER_ID'] = member_id
    row['MVMT_VAR_LINK_ID'] = link_id
    row['DISUSE_FLAG'] = disuse_flag
    row['LAST_UPDATE_USER'] = OLD_USER_ID
    row['LAST_UPDATE_TIMESTAMP'] = '2026-01-01 00:00:00'
    return row


def create_mov_vars_link_table(dummy_db, link_rows):
    """MovementVarsLinkTable を DB 状態込みで用意する（backyard_main.py:68-69 と同じ読み方）"""
    from backyard_libs.ansible_driver.classes.MovementVarsLinkTableClass import MovementVarsLinkTable

    dummy_db.rows_by_table[TABLE_MVMT_VAR_LINK] = list(link_rows)
    table = MovementVarsLinkTable(dummy_db)
    table.store_dbdata_in_memory(contain_disused_data=True)
    return table


def create_nest_vars_member_table(dummy_db, member_rows):
    """NestVarsMemberTable を DB 状態込みで用意する（backyard_main.py:71-72 と同じ読み方）"""
    from backyard_libs.ansible_driver.classes.NestVarsMemberTableClass import NestVarsMemberTable

    dummy_db.rows_by_table[TABLE_NESTVAR_MEMBER] = list(member_rows)
    table = NestVarsMemberTable(dummy_db)
    table.store_dbdata_in_memory(contain_disused_data=True)
    return table
