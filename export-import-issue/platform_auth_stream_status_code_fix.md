# platform-auth ストリームモードのステータスコード伝播バグ修正

## 発見された問題

### 症状

**エクスポートファイルダウンロードで401エラーが返されても、ブラウザ側では200 OKとして処理され、ダウンロードが進行してしまう。**

### 実際のログ

```
# バックエンド（ita-api-organization）は401を返している
http://ita-api-organization:8000 "GET .../file/ HTTP/1.1" 401 3219

# しかし、platform-authは200を返している
### end func:ita_workspace_api_call response.status_code=200
"GET .../file/ HTTP/1.1" 200 -
```

### 根本原因

**platform-authのストリームモード処理で、バックエンドのステータスコードが設定されていない**

#### 問題のコード

[platform-auth/api.py:839-845](platform_root/platform_auth/api.py#L839-L845)

```python
if stream:
    # stream形式の場合は、独自の返却を実施する
    response = Response(chunk_response(return_api, response_chunk_byte))
    # ↑ ステータスコードが設定されていない！デフォルトで200になる
    for key, value in return_api.headers.items():
        if key.lower().startswith('content-'):
            response.headers[key] = value
```

#### 比較：non-streamモード（正常）

```python
else:
    response = make_response()
    response.status_code = return_api.status_code  # ← ちゃんと設定されている
    response.data = return_api.content
    ...
```

---

## 実施した修正

### 修正内容

**ストリームモードでもバックエンドのステータスコードを設定**

```python
if stream:
    # stream形式の場合は、独自の返却を実施する
    response = Response(chunk_response(return_api, response_chunk_byte))
    response.status_code = return_api.status_code  # ← 追加
    for key, value in return_api.headers.items():
        if key.lower().startswith('content-'):
            response.headers[key] = value
```

### 修正ファイル

- `/workspace/exastro-platform-dev/platform_root/platform_auth/api.py`
  - 4箇所の同じパターンをすべて修正

### 影響範囲

#### 修正対象となったストリームAPIエンドポイント

すべてのストリームモード対応エンドポイントに影響します（[stream_pattern.py](platform_root/platform_auth/config/stream/stream_pattern.py)参照）：

1. **監査ログダウンロード**
   - `/api/{org_id}/platform/auditlog/download/{download_id}`

2. **ユーザー一括処理**
   - `/api/{org_id}/platform/jobs/users/bulk/format`
   - `/api/{org_id}/platform/jobs/users/bulk/status/{job_id}/download`
   - `/api/{org_id}/platform/jobs/users/export/status/{job_id}/download`

3. **ITAファイル関連**
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/{uuid}/{column}/file` ← **今回の問題**
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/excel/format`
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/excel`
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/excel/journal`
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/compare/execute/output`
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/conductor/{id}/input_data`
   - `/api/{org_id}/workspaces/{ws_id}/ita/menu/{menu}/conductor/{id}/result_data`

4. **Terraform Policy**
   - `/api/{org_id}/workspaces/{ws_id}/ita/terraform/policy/{org_name}/download/{policy_name}`

5. **Ansible Execution Agent**
   - `/api/{org_id}/workspaces/{ws_id}/ansible_execution_agent/populated_data`

---

## 影響と効果

### 修正前の動作

- バックエンドが401/403/500などのエラーを返しても、フロントエンドには200 OKとして届く
- ブラウザ側のJavaScriptでは `response.ok === true` となり、エラー処理が実行されない
- ファイルダウンロードが進行し、エラーレスポンスのHTMLやJSONが「ファイル」として保存される可能性がある

### 修正後の動作

- バックエンドのステータスコードがそのまま伝播される
- 401エラーの場合、ブラウザ側で `response.ok === false` となり、適切なエラー処理が実行される
- ユーザーにエラーメッセージが表示される
- ファイルダウンロードが中断される

### セキュリティ向上

- **権限チェックが正しく機能する**
  - 今回追加したエクスポート/インポート権限チェック機能が正しく動作する
  - 権限のないユーザーはファイルをダウンロードできない

---

## テスト

### 確認項目

1. **エラーレスポンスが正しく返されること**
   ```bash
   # 権限なしユーザーでアクセス
   curl -u test_user:password \
     "http://localhost:8000/api/org1/workspaces/ws1/ita/menu/menu_export_import_list/{uuid}/file_name/file/"
   
   # 期待値: HTTP 401 Unauthorized が返る
   ```

2. **正常なファイルダウンロードは影響を受けないこと**
   ```bash
   # 権限ありユーザーでアクセス
   curl -u admin:password \
     "http://localhost:8000/api/org1/workspaces/ws1/ita/menu/menu_export_import_list/{uuid}/file_name/file/" -O
   
   # 期待値: HTTP 200 OK、ファイルがダウンロードされる
   ```

3. **ブラウザでのエラー表示**
   - 権限なしユーザーでダウンロードボタンをクリック
   - エラーメッセージが表示される
   - ダウンロードが中断される

---

## 関連修正

この修正は以下の機能と連携して動作します：

1. **[エクスポート/インポート権限チェック](security_fix_json_storage_item.md)**
   - バックエンドでの権限チェック実装

2. **[JavaScript エラーハンドリング改善](../ita_root/ita_web_server/contents/common/js/common.js)**
   - Content-Type チェック追加
   - エラーレスポンスの適切な処理

3つの修正が組み合わさって、完全な権限制御が実現されます。

---

## 後方互換性

### 破壊的変更

**YES** - エラーレスポンスのステータスコードが正しく伝播されるようになります

### 影響を受ける可能性のあるケース

1. **エラーレスポンスを200として処理していたクライアント**
   - 修正後は正しいステータスコード（401/403/500など）が返される
   - クライアント側でエラーハンドリングが実行される

2. **ストリームモードのすべてのエンドポイント**
   - 上記「修正対象となったストリームAPIエンドポイント」参照
   - 正常なリクエストには影響なし（200は200のまま）

### 推奨される対応

既存のクライアント実装で、ストリームAPIのエラーハンドリングが適切に実装されていることを確認してください。

---

## まとめ

- **問題**: platform-authのストリームモードでステータスコードが設定されず、常に200が返されていた
- **修正**: `response.status_code = return_api.status_code` を1行追加（4箇所）
- **効果**: バックエンドのエラーが正しくフロントエンドに伝播されるようになり、権限チェックが機能する
- **影響**: すべてのストリームモードAPIエンドポイントで、エラーレスポンスが正しく処理されるようになる

この修正により、エクスポート/インポート権限チェック機能が正しく動作し、セキュリティが向上します。
