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
- 接続方式を変えない更新（例: `ttl`だけの変更）では、認証情報の項目を送らなければ**既存の値がそのまま残る**（DBで確認）。`menu-filter`では`null`と返るが、消えたわけではないので、ユーザーに再入力や確認を求めなくてよい。

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

## 収集間隔（エージェントがイベントを取りに行く間隔）

- **このメニューには収集間隔の項目は無い。** 秒数の項目は`ttl`だけだが、`ttl`はイベントを判定対象として扱う期間であり、収集間隔ではない。`ttl`を短くしても検知は速くならず、AND相関や「〜が来なければ」の待ち時間が短くなるなど既存ルールの動きが変わるので、収集間隔の依頼で`ttl`を変えてはいけない。
- 収集間隔は、ITAとは別に動くOASEエージェントの環境変数（`.env`）`EXECUTE_INTERVAL`（秒）で決まる。製品コード（`agent/agent_init.py`）で確認した仕様は次のとおり。
    - 未指定時の既定値は**5秒**。3秒以下を指定すると3秒になる（下限3秒）。
    - 1つのエージェントは、`EVENT_COLLECTION_SETTINGS_NAMES`に並べた収集設定をすべて同じ間隔で回る。**収集設定ごとに間隔を変えることはできない。** 特定の収集設定だけ変えたい場合は、その収集設定専用のエージェントを別に立て、元のエージェントの`EVENT_COLLECTION_SETTINGS_NAMES`から外す。
    - エージェントは`ITERATION`回（既定10、10〜120に丸められる）ループするたびに、収集設定をITAから取り直す。`EXECUTE_INTERVAL × ITERATION`が86400秒以上になると`ITERATION`が自動で減らされる。
    - 変更は、エージェントを動かしているサーバーで`.env`（またはコンテナの環境変数）を書き換え、エージェントを再起動する。**MCPツールからは変更も現在値の確認もできない。**
- `connection_method_name`が`No Agent Used`（エージェント不使用）の収集設定は、エージェントが取りに行かない（外部からITAのAPIへイベントを送る方式）。収集間隔は関係なく、送る側のタイミングで決まる。

### 「検知が遅いので収集間隔を△△秒にして」と依頼されたとき

1. `menu-filter`で対象の収集設定を取得し、`connection_method_name`を確認する（`No Agent Used`なら上記のとおり間隔の設定は無い）。
2. ITAの設定では収集間隔を変えられないこと、`ttl`は別物なので変えないことを伝える。
3. **依頼の値が本当に「短く」なるかを確かめる。** 既定値は5秒なので、エージェントの設定を変えていなければ「30秒に短く」は実際には**長くなり、検知はさらに遅くなる**。現在値はMCPから見えないので、エージェントを管理している人に`EXECUTE_INTERVAL`の現在値を確認してもらうよう伝え、現在値が分からないまま「短くなる」と断定しない。
4. 同じエージェントが受け持つほかの収集設定にも効くことを伝える（その収集設定だけ変えたい場合の方法も示す）。
5. 間隔以外の遅れの原因のうち、**ITA側で確認できるもの**を`menu-filter`で調べて示す。特に、その収集設定のイベントを使うルールがAND相関（`A and B`）や吸収構成（`rule.md`の「AND相関」「XOR相関」節）で、片方のイベントが`ttl`秒まで待たされていないか。ほかに、監視ツール側の評価間隔、ITAの判定処理の実行間隔もありうることを添える。

## 認証情報（パスワード・トークン）を変更するとき

「〇〇のパスワードが変わったので収集設定を更新して」のような依頼では、次の順で進める。

1. **対象の収集設定を特定する。** `menu-filter`で`event_collection`を取得し、依頼の監視ツールに当たる収集設定が複数あれば（例: 冗長構成の2台）、どれを更新するかを`ask_user_choice`で確認する（「すべて」の選択肢も入れる）。
2. **接続方式から、変える項目を決める。**

| connection_method_name | 変える項目 |
|---|---|
| `Bearer Authentication` | `auth_token` |
| `password authentication` / `IMAP password authentication` | `password`（ユーザー名も変わったなら`username`も） |
| `Optional Authentication` | `parameter`または`request_header`に書いた認証情報 |
| `No Agent Used` | 認証情報なし（送る側の設定を変える） |

- 「パスワードが変わった」と言われても、接続方式が`Bearer Authentication`ならパスワードは使っていない。パスワードの変更でトークンが無効になるかは監視ツール次第（例: ZabbixのAPIトークンはユーザーのパスワードを変えても無効にならない）。**更新するかどうかを聞く前に**このことを伝え、トークンを作り直したかを確認する。

3. **新しい値の受け取り方を確認する（重要）。** チャットに入力された値はLLMに送られ、会話履歴（`conversations`メニュー）にも平文で残る。次の2つを`ask_user_choice`で示し、ユーザーに選んでもらう。
    - ITAの画面（OASE管理 > イベント収集）でユーザー自身が入力する（推奨。値がチャットに残らない）。この場合、エージェントは対象の収集設定名と変える項目を案内し、入力後に読み直して最終更新日時が変わったことを確認する。
    - チャットで値を受け取り、エージェントが更新する（会話履歴に残ることを了承してもらったうえで）。
4. 更新は`Update`で、主キー・`last_update_date_time`・`menu-filter`で取得したほかの列をそのまま送り、変える認証情報の項目だけ新しい値にする。**変えない認証情報の項目は送らない**（送らなければ既存の値が残る）。`menu-filter`が返す`null`を送り直してはいけない。
5. **受け取った値を回答に書き戻さない**（伏せ字にもしない。「入力いただいた値」と書く）。
6. 読み直して最終更新日時が変わったことを確認する。認証情報の項目は`menu-filter`では`null`と返るので、値そのものはMCPでは確認できないことを伝える。
7. **反映のタイミングを伝える。** OASEエージェントは`ITERATION`回のループごとに収集設定をITAから取り直すので、新しい値が使われるのは最大で`EXECUTE_INTERVAL × ITERATION`秒後（既定値なら5秒×10回＝約50秒後）。すぐに反映したい場合は、エージェントのコンテナ内の`event_collection_settings.json`を削除すると次のループで取り直す（エージェントのサーバーでの作業）。新しい値で接続できたかは、その後イベントが届くかで確認してもらう。
