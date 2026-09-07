"""DBConnectWs の代わりにテストで使うダミー DB クラス（DummyDB）

本物の DB を立てずに、Python の dict に行を持たせて table_select / table_insert / table_update を
再現する。テスト対象のコードからは本物の DBConnectWs と区別がつかない。

common_libs/common/dbconnect/dbconnect_common.py:_table_update_with_ids のセマンティクスを
忠実に再現している点。Issue #2618 は「更新不要なカラムまで渡すと直前の UPDATE が巻き戻る」バグなので、
このセマンティクスが無いと回帰テストとして機能しない。
"""
import copy


class DummyDB:
    """データベース接続(DBConnectWs)のダミークラス（テーブルの中身をメモリに保持する）

    Attributes:
        rows_by_table: {table_name: [row(dict), ...]} テーブルの実体
        select_calls: table_select の呼び出し履歴 [(table_name, where_str), ...]
        update_calls: table_update の呼び出し履歴 [{'table', 'pkey', 'data_list'}, ...]
        insert_calls: table_insert の呼び出し履歴 [{'table', 'pkey', 'data_list'}, ...]
        fail_update_on_call: 指定回数目(1 origin)の table_update を False で返す
        fail_insert_on_call: 指定回数目(1 origin)の table_insert を False で返す
    """

    COLUMN_NAME_TIMESTAMP = 'LAST_UPDATE_TIMESTAMP'

    def __init__(self, rows_by_table=None, timestamp='2026-08-19 12:00:00'):
        """
        constructor

        Arguments:
            rows_by_table: {table_name: [row(dict), ...]}
            timestamp: table_insert / table_update が自動設定するタイムスタンプ
        """
        self.rows_by_table = copy.deepcopy(rows_by_table) if rows_by_table else {}
        self.select_calls = []
        self.update_calls = []
        self.insert_calls = []
        self.fail_update_on_call = None
        self.fail_insert_on_call = None
        self.transaction_started = 0
        self._timestamp = timestamp
        self._uuid_seq = 0

    # - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
    # DBConnectWs 互換 API
    # - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +

    def table_select(self, table_name, where_str="", bind_value_list=[]):
        """
        select table

        `WHERE DISUSE_FLAG = '0'`（TableBase.store_dbdata_in_memory が組み立てる唯一の WHERE）だけを解釈する。
        本物の DB と同様、呼ぶたびに独立した dict を返す（メモリ上の書き換えが実体に伝播しない）。
        """
        self.select_calls.append((table_name, where_str))

        rows = self.rows_by_table.get(table_name, [])
        if "DISUSE_FLAG = '0'" in where_str:
            rows = [row for row in rows if row.get('DISUSE_FLAG') == '0']
        elif where_str:
            raise AssertionError(f"DummyDB does not support this where clause: {where_str}")

        return copy.deepcopy(rows)

    def table_insert(self, table_name, data_list, primary_key_name, is_register_history=False):
        """
        insert table

        本物と同様に、主キーが未設定なら払い出して data_list を書き換えてから返す。
        """
        if isinstance(data_list, dict):
            data_list = [data_list]

        self.insert_calls.append({
            'table': table_name,
            'pkey': primary_key_name,
            'data_list': copy.deepcopy(data_list),
        })

        if self.fail_insert_on_call is not None and len(self.insert_calls) == self.fail_insert_on_call:
            return False

        rows = self.rows_by_table.setdefault(table_name, [])
        for data in data_list:
            if primary_key_name not in data or not data[primary_key_name]:
                data[primary_key_name] = self._create_uuid()
            data[self.COLUMN_NAME_TIMESTAMP] = self._timestamp
            rows.append(copy.deepcopy(data))

        return data_list

    def table_update(self, table_name, data_list, primary_key_name, is_register_history=False, last_timestamp=True):
        """
        update table

        本物（dbconnect_common.py:_table_update_with_ids）と同じく
        **data の全キーを SET し、その中の主キーで WHERE を作る**。
        「更新しないカラムも渡しておけば安全」ではないという、Issue #2618 の温床をそのまま再現する。
        """
        if isinstance(data_list, dict):
            data_list = [data_list]

        self.update_calls.append({
            'table': table_name,
            'pkey': primary_key_name,
            'data_list': copy.deepcopy(data_list),
        })

        if self.fail_update_on_call is not None and len(self.update_calls) == self.fail_update_on_call:
            return False

        rows = self.rows_by_table.setdefault(table_name, [])
        for data in data_list:
            data = dict(data)
            if last_timestamp is True:
                data[self.COLUMN_NAME_TIMESTAMP] = self._timestamp

            # 本物は data に主キーが無いと KeyError になる
            pkey_value = data[primary_key_name]

            targets = [row for row in rows if row.get(primary_key_name) == pkey_value]
            if not targets:
                raise AssertionError(
                    f"DummyDB: no row matched {table_name}.{primary_key_name} = {pkey_value}"
                )
            for row in targets:
                # SET 句に載るのは data のキー全部（本物と同じ）
                row.update(data)

        return data_list

    def db_transaction_start(self):
        """トランザクション開始"""
        self.transaction_started += 1

    # - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +
    # テスト用ヘルパ
    # - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - + - +

    def rows(self, table_name):
        """テーブルの実体（DB に入っている状態）を返す"""
        return self.rows_by_table.get(table_name, [])

    def find_row(self, table_name, **conditions):
        """条件に一致する行を 1 件返す（0 件 / 複数件は AssertionError）"""
        matched = [
            row for row in self.rows(table_name)
            if all(row.get(key) == value for key, value in conditions.items())
        ]
        assert len(matched) == 1, f"expected exactly 1 row for {conditions}, got {len(matched)}"
        return matched[0]

    def update_data_list(self, index):
        """index 回目(0 origin)の table_update に渡された data_list を返す"""
        return self.update_calls[index]['data_list']

    def insert_data_list(self, index):
        """index 回目(0 origin)の table_insert に渡された data_list を返す"""
        return self.insert_calls[index]['data_list']

    def _create_uuid(self):
        """主キーの払い出し（テストで追跡できるよう連番にする）"""
        self._uuid_seq += 1
        return f"generated-uuid-{self._uuid_seq}"
