# event_collection reference

OASEのイベント収集設定。監視ツール等のエージェントがどこに・どう接続してイベントを取得するかを定義する。`maintenance-all`等でこのメニューを操作する前に本リファレンスを読むこと。

## connection_method_name column

- 接続方式によって必須になる項目が変わる。登録・更新前に必ず以下の早見表で確認すること。

| connection_method_name | request_method_nameの許容値 | 必須になる項目 | 禁止事項 |
|---|---|---|---|
| `No Agent Used`（エージェント不使用） | - | - | `url`は不要 |
| `Bearer Authentication` | `GET` / `POST` | `url`, `auth_token`（新規登録時） | `request_header`に`authorization:`を含めてはいけない（大文字小文字区別なし） |
| `password authentication`（パスワード認証/Basic） | `GET` / `POST` | `url`, `username`, `password`（新規登録時） | `request_header`に`authorization:`を含めてはいけない |
| `Optional Authentication`（任意の認証） | `GET` / `POST` | `url` | 認証情報は`parameter`に自分で記述する |
| `IMAP password authentication` | `IMAP: Plaintext` のみ | `url`, `username`, `password`（新規登録時） | - |

- **重要** 選択肢はバージョンによって異なる（古い環境には存在しない接続方式がある。例: 共有鍵認証`Authentication SharedKeyLite`は廃止済みで、現行環境のプルダウンには出てこない）。**登録前に必ず`list-menu-info-pulldown`で実際の選択肢を取得し、そこに存在する値をそのまま指定すること。** 表に載っていない値や、ユーザーの言葉を直訳した値（例: 「任意認証」→`Arbitrary authentication`）を推測で指定してはいけない（正しくは`Optional Authentication`）。
- `No Agent Used`以外を選んだ場合、`url`（接続先）が空だと登録できない。
- `connection_method_name`が`IMAP password authentication`の場合、`response_list_flag`は自動的に`True`へ強制設定される（指定しても上書きされる）。
- 更新時に接続方式を変更し、かつ`password`を指定しなかった場合、既存の`password`はクリアされる（再入力が必要）。

## request_header column

- JSON形式のオブジェクト、または Jinja2 テンプレート（`{{ ... }}`や`{% ... %}`を含む文字列）のいずれかで指定する。どちらでもない形式はエラーになる。
- `connection_method_name`が`Bearer Authentication`/`password authentication`/`Optional Authentication`のとき、`authorization:`という文字列（大文字小文字区別なし）を含めてはいけない（認証情報は別項目で管理されるため）。

## parameter column

- `request_header`と同様に、JSON形式のオブジェクト、またはJinja2テンプレートのいずれかで指定する。

## ttl column

- 単位は秒。最小値10、最大値2147483647。
- **API経由の登録では必須。** 省略すると`{"ttl": ["Required fields."]}`（499-00201）で失敗する。画面では`3600`が初期表示されるが`maintenance-all`ではその既定値が適用されないため、必ず明示的に渡すこと（`3600`が妥当な値）。

## request_header と parameter は必ず明示的に渡す（重要）

- `connection_method_name`が`Bearer Authentication`/`password authentication`/`Optional Authentication`のとき、`maintenance-all`で`request_header`/`parameter`のキーを省略すると、バリデーションメッセージではなく**原因の分からない`System Error (999-99999)`で登録が失敗する**。
- そのため両方のキーを常に含めること。設定する内容が無い場合は空のJSONオブジェクトを文字列として渡す。
  ```json
  "request_header": "{}",
  "parameter": "{}"
  ```
- `username`（`password authentication`の場合）も同様で、値が空でもキー自体は含めること。
- このメニューで`System Error (999-99999)`が出た場合は同じペイロードで再試行せず、不足している`request_header`/`parameter`のキーを追加して1回だけ再試行すること。

## 新規作成時の最小サンプル（Bearer認証、GETの例）

```json
{
  "menu": "event_collection",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "event_collection_settings_name": "Zabbix監視イベント収集",
        "connection_method_name": "Bearer Authentication",
        "request_method_name": "GET",
        "url": "https://zabbix.example.com/api/events",
        "auth_token": "xxxxxxxx",
        "request_header": "{}",
        "parameter": "{}",
        "ttl": "3600"
      }
    }
  ]
}
```

## 既存の収集設定をもとに新しい収集設定を作るとき（複製）

- `event_collection_settings_name`は**一意**。複製先には別の名前を付けること。
- **`auth_token`/`password`/`secret_access_key`はパスワード項目のため、`menu-filter`では値が返らない（`null`になる）。** 既存の設定からはコピーできないので、複製先の認証情報は必ずユーザーに確認すること。推測やダミー値で登録してはいけない。
- 監視ツールが別の機器であれば`url`も異なるはずなので、`url`もユーザーに確認すること。`connection_method_name`/`request_method_name`/`request_header`/`parameter`/`ttl`/`response_key`/`event_id_key`などは既存の値を流用してよい（流用する旨を提案に明記する）。
- 収集設定を追加しただけではラベルは付かない。ラベル付与設定は収集設定ごとに必要なので、`labeling.md`の「既存のラベル付与設定を別の収集設定にコピーする」節も参照すること。
