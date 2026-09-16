# セキュリティ修正: json_storage_item NULL時の権限チェックバイパス

## 発見された脆弱性

### 問題の概要

エクスポートファイルダウンロードAPI (`/ita/menu/{menu}/{uuid}/{column}/file/`) において、`json_storage_item` カラムが NULL の場合に権限チェックが完全にスキップされる脆弱性が発見されました。

### 影響範囲

- **対象API**
  - `/api/{org}/workspaces/{ws}/ita/menu/menu_export_import_list/{uuid}/file_name/file/`
  - `/api/{org}/workspaces/{ws}/ita/menu/bulk_excel_export_import_list/{uuid}/result_file/file/`
  - 履歴ダウンロード（同上の履歴版）

- **影響**
  - 書き込み権限のないメニューのエクスポートファイルをダウンロード可能
  - エクスポート対象メニューが不明なため、権限チェック自体が実行されない

### 脆弱性の原因

#### 修正前のコード

```python
# menu_filter.py get_file_path() 関数
status_code, result, msg = objmenu.rest_filter(filter_parameter, mode, base64_file_flg=False)

if menu in ['menu_export_import_list', 'bulk_excel_export_import_list']:
    record = result[0].get('parameter')
    json_storage_item = record.get('json_storage_item')  # ← rest_filter の結果に json_storage_item が含まれていない
    if json_storage_item:  # ← 常に None なので、if ブロック全体がスキップされる
        try:
            storage_data = json.loads(json_storage_item)
            menu_list = storage_data.get('menu', [])
            check_export_menu_permission(objdbca, menu_list)
        except Exception as e:
            raise e
    # ← ここに到達して権限チェックなしでダウンロード可能
```

#### 根本原因

**`rest_filter()` の結果に `json_storage_item` カラムが含まれていない**

- `rest_filter()` は API 用のレスポンスを生成するメソッド
- デフォルトでは表示用のカラムのみを返す
- 内部処理用の `json_storage_item` は含まれない
- そのため、`record.get('json_storage_item')` は常に `None` を返す

#### 問題のシナリオ

1. **`rest_filter()` の仕様により常に発生**
   - `rest_filter()` は API レスポンス用のメソッド
   - 表示用カラムのみを返すため、内部処理用の `json_storage_item` は含まれない
   - そのため、**すべてのダウンロードリクエストで権限チェックがスキップされていた**

2. **実際のログ**
   ```
   [2026-09-15 17:07:25,480][WARNING] [Download Permission Check] json_storage_item is None: uuid=d8e2f8e5-95c5-493b-8e43-8b2f68c22dc1, menu=menu_export_import_list
   [2026-09-15 17:07:25,482][INFO] [api-end][SUCCESS][status_code=200]
   ```
   権限チェックがスキップされ、ダウンロードが成功している

3. **影響の深刻度**
   - **HIGH**: すべてのエクスポートファイルが権限チェックなしでダウンロード可能だった
   - 書き込み権限のないメニューのデータも取得可能
   - EXPORT_PERMISSION_CHECK_FLG による制御も機能していなかった

---

## 実施した修正

### 修正内容

`json_storage_item` が NULL の場合は**アクセスを拒否**するように変更しました。

#### 修正後のコード

```python
# menu_filter.py get_file_path() 関数
if menu in ['menu_export_import_list', 'bulk_excel_export_import_list']:
    # rest_filter の結果には json_storage_item が含まれないため、直接DBから取得
    table_name = objmenu.get_table_name()
    ret = objdbca.table_select(table_name, 'WHERE UUID = %s AND DISUSE_FLAG = %s', [uuid, 0])
    if len(ret) == 0:
        # レコードが存在しない場合はエラー
        g.applogger.error(f"[Download Permission Check] Record not found: uuid={uuid}, menu={menu}")
        msg = g.appmsg.get_api_message("MSG-30026", [])
        raise AppException("401-00001", [msg], [msg])

    json_storage_item = ret[0].get('JSON_STORAGE_ITEM')
    if json_storage_item:
        try:
            storage_data = json.loads(json_storage_item)
            menu_list = storage_data.get('menu', [])
            if menu_list:
                # エクスポート対象メニューへの書き込み権限をチェック
                check_export_menu_permission(objdbca, menu_list)
            else:
                # menu_list が空の場合もエラー
                g.applogger.error(f"[Download Permission Check] json_storage_item exists but menu list is empty: uuid={uuid}")
                msg = g.appmsg.get_api_message("MSG-30026", [])
                raise AppException("401-00001", [msg], [msg])
        except json.JSONDecodeError as e:
            # JSON パースエラー
            g.applogger.error(f"[Download Permission Check] Failed to parse json_storage_item: uuid={uuid}, error={str(e)}")
            msg = g.appmsg.get_api_message("MSG-30026", [])
            raise AppException("499-00001", [msg], [msg])
        except AppException:
            # AppException はそのまま再送出
            raise
        except Exception as e:
            # 予期しない例外
            g.applogger.error(f"[Download Permission Check] Unexpected error: uuid={uuid}, error={str(e)}")
            raise
    else:
        # json_storage_item が NULL の場合はアクセス拒否
        g.applogger.error(f"[Download Permission Check] json_storage_item is None, access denied: uuid={uuid}, menu={menu}")
        msg = g.appmsg.get_api_message("401-00001", [])
        raise AppException("401-00001", [msg], [msg])
```

#### 修正のポイント

1. **`rest_filter()` ではなく `table_select()` を使用**
   - `rest_filter()` は API レスポンス用で、内部カラムを含まない
   - `table_select()` で直接 DB から `JSON_STORAGE_ITEM` を取得

2. **履歴ファイルも同様に修正**
   - 履歴テーブル (`_JNL`) から `JOURNAL_SEQ_NO` で取得

### 修正ファイル

- `ita_root/ita_api_organization/libs/menu_filter.py`
  - `get_file_path()` 関数
  - `get_history_file_path()` 関数

### エラーパターン

| 状況 | エラーコード | 動作 |
|------|------------|------|
| `json_storage_item` が NULL | 401-00001 | アクセス拒否 |
| `menu_list` が空 | 401-00001 | アクセス拒否 |
| JSON パースエラー | 499-00001 | システムエラー |
| 権限なし（check_export_menu_permission） | 401-00001 | アクセス拒否 |

---

## 影響と対応

### 既存データへの影響

**修正により、正しく権限チェックが動作するようになります。**

#### セキュリティレベルの向上

- **修正前**: `rest_filter()` の仕様により、**すべてのダウンロードで権限チェックがスキップされていた**（CRITICAL リスク）
- **修正後**: `table_select()` で直接 DB から取得し、正しく権限チェックを実行（リスク排除）

#### 互換性

- **破壊的変更**: YES
  - 修正前は権限チェックが機能していなかったため、修正後は正しく権限制限が適用される
  - 書き込み権限のないメニューのエクスポートファイルはダウンロード不可になる

#### データの整合性チェック（推奨）

念のため、`json_storage_item` が NULL のレコードが存在しないか確認：

```sql
-- json_storage_item が NULL のレコードを確認
SELECT UUID, EXECUTION_NO, EXECUTION_USER, TIME_REGISTER
FROM T_MENU_EXPORT_IMPORT
WHERE JSON_STORAGE_ITEM IS NULL
AND DISUSE_FLAG = '0';
```

もし NULL のレコードが存在する場合：
- 正常なフローで作成されたレコードは `json_storage_item` が必ず設定される
- NULL のレコードは異常データなので廃止を推奨

```sql
-- 異常データを廃止
UPDATE T_MENU_EXPORT_IMPORT
SET DISUSE_FLAG = '1'
WHERE JSON_STORAGE_ITEM IS NULL;
```

---

## テスト

### 手動テスト手順

1. **正常系: json_storage_item が存在する場合**
   ```bash
   # 通常のエクスポート → ダウンロード
   curl -u admin:password -X POST ".../ita/menu/bulk/export/execute/" \
     -d '{"menu":["operation_list"],"mode":"1","abolished_type":"1","journal_type":"1"}'
   # → execution_no を取得
   
   curl -u admin:password ".../ita/menu/menu_export_import_list/{execution_no}/file_name/file/" -O
   # → 200 OK、ダウンロード成功
   ```

2. **異常系: json_storage_item が NULL の場合**
   ```sql
   -- テストデータを作成（json_storage_item = NULL）
   UPDATE T_MENU_EXPORT_IMPORT
   SET JSON_STORAGE_ITEM = NULL
   WHERE UUID = '{test_uuid}';
   ```
   ```bash
   curl -u admin:password ".../ita/menu/menu_export_import_list/{test_uuid}/file_name/file/"
   # → 401 Unauthorized、エラーメッセージ表示
   ```

3. **異常系: menu_list が空の場合**
   ```sql
   -- テストデータを作成（menu が空配列）
   UPDATE T_MENU_EXPORT_IMPORT
   SET JSON_STORAGE_ITEM = '{"menu":[],"mode":"1","abolished_type":"1","journal_type":"1"}'
   WHERE UUID = '{test_uuid}';
   ```
   ```bash
   curl -u admin:password ".../ita/menu/menu_export_import_list/{test_uuid}/file_name/file/"
   # → 401 Unauthorized
   ```

---

## 関連する権限チェック実装

本修正は、エクスポート/インポート権限チェック機能の一部として実装されました。

### 関連機能

1. **エクスポート実行時の権限チェック**
   - `libs/export_import.py`: `check_export_menu_permission()`
   - エクスポート対象メニューに対する書き込み権限チェック

2. **ファイルダウンロード時の権限チェック（今回修正）**
   - `libs/menu_filter.py`: `get_file_path()`, `get_history_file_path()`
   - エクスポートファイルダウンロード時に実行時と同じ権限をチェック

3. **EXPORT_PERMISSION_CHECK_FLG による制御**
   - FLAG=0: 権限チェックスキップ（環境移行に必要な内部メニュー）
   - FLAG=1: 書き込み権限チェック（デフォルト）

### 一貫性の確保

- エクスポート実行時にチェックした権限が、ダウンロード時にもバイパスされないように修正
- `json_storage_item` を使ってエクスポート実行時のパラメータを保存し、ダウンロード時に再度権限チェックを実行

---

## まとめ

- **脆弱性**: `rest_filter()` の仕様により、`json_storage_item` が取得できず、**すべてのダウンロードで権限チェックがスキップされていた**
- **根本原因**: `rest_filter()` は API レスポンス用で内部カラムを返さない
- **修正**: `table_select()` で直接 DB から `JSON_STORAGE_ITEM` を取得
- **影響**: 修正後は正しく権限チェックが動作し、権限のないユーザーはダウンロード不可になる
- **セキュリティ向上**: CRITICAL リスクを排除

この修正により、エクスポートファイルのダウンロードにおいて、エクスポート実行時と同等の権限制御が保証されます。
