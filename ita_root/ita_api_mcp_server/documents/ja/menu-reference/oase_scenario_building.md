# OASE: 新しい監視イベントへの一括対応設定を構築する

ユーザーから「〇〇（監視ツール名）で△△（イベント種別）が出たら、自動で対処できるようにして」のような要望を受けたときに、OASEの各メニューをどの順序で・どう呼び出せば一気通貫で構築できるかを示す。各メニューの項目の詳細（必須項目・相互排他ルール・JSON書式等）は、本ドキュメントではなく各メニューの個別リファレンス（`event_collection.md`, `label_creation.md`, `labeling.md`, `filter.md`, `action.md`, `rule.md`）を`get-document`ツールで参照すること。

## 作成順序（依存関係があるため、この順番を守ること）

```
1. event_collection（収集設定）  … 監視ツールからのイベント取得元を定義
2. label_creation（ラベル作成） … イベントに付与するラベルのキーを定義（1と並行可）
3. labeling（ラベル付与）       … 1と2を参照し、イベントの特定フィールド値をラベルに変換
4. filter（フィルター）         … 2で作ったラベル条件でイベントを絞り込む
5. action（アクション）         … 対応処理（Conductor実行等）を定義（1〜4と並行可）
6. rule（ルール）               … 4のフィルターと5のアクションを結びつけ、マッチ時の動作を確定
```

- `labeling`は`event_collection`（イベント収集設定ID）と`label_creation`（ラベルキーID）の両方を参照するため、2つとも先に作成しておく。
- `rule`は`filter`（filter_a/filter_b）と`action`（action_id）の両方を参照するため、必ず最後に作成する。
- 既存のラベル・フィルター・アクションが要望に合致する場合は、新規作成せず再利用してよい（`menu-filter`ツールで既存レコードを確認すること）。

## 各ステップで使うツール

- 既存レコードの確認: `menu-filter`（`menu`に各REST名を指定）
- プルダウン項目（Conductor名、ホスト名、パラメータシート名等）の候補確認: `list-menu-info-pulldown`
- 新規作成・更新: `maintenance-all`

## End-to-Endの具体例

要望: 「Zabbixで高負荷アラートが出たら、サービスを自動で再起動して」

### Step 1: 収集設定（event_collection）
```json
{
  "menu": "event_collection",
  "records": [{
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
  }]
}
```

### Step 2: ラベル作成（label_creation）
```json
{
  "menu": "label_creation",
  "records": [{
    "type": "Register",
    "parameter": { "label_key_name": "event_type", "color_code": "#FF0000" }
  }]
}
```

### Step 3: ラベル付与（labeling）— Step1・Step2で作成した名称を参照
```json
{
  "menu": "labeling",
  "records": [{
    "type": "Register",
    "parameter": {
      "labeling_settings_name": "イベント種別ラベル付与",
      "event_collection_settings_name": "Zabbix監視イベント収集",
      "search_key_name": "alert.type",
      "type_name": "string",
      "comparison_method": "==",
      "search_value_name": "高負荷アラート",
      "label_key_name": "event_type",
      "label_value_name": "高負荷アラート"
    }
  }]
}
```

### Step 4: フィルター（filter）— Step2で作成したラベルキーを条件に使用
```json
{
  "menu": "filter",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "filter_name": "高負荷アラートフィルター",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"高負荷アラート\"]]",
      "search_condition_id": "Unique"
    }
  }]
}
```

### Step 5: アクション（action）
```json
{
  "menu": "action",
  "records": [{
    "type": "Register",
    "parameter": {
      "action_name": "サービス再起動",
      "conductor_class_id": "Ansible実行",
      "event_collaboration": "False",
      "host_id": "[H]web-server-01",
      "parameter_sheet_id": "httpd再起動"
    }
  }]
}
```

### Step 6: ルール（rule）— Step4のフィルターとStep5のアクションを紐付け
```json
{
  "menu": "rule",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "rule_name": "高負荷アラート対応ルール",
      "rule_label_name": "high_load_rule",
      "rule_priority": "1",
      "filter_a": "高負荷アラートフィルター",
      "action_id": "サービス再起動",
      "conclusion_label_settings": "[]",
      "action_label_inheritance_flag": "True",
      "event_label_inheritance_flag": "False",
      "ttl": "3600"
    }
  }]
}
```

これで「Zabbixで高負荷アラートが出たら、サービスを自動で再起動する」一連の設定が完成する。実行結果（判定・アクション実行履歴）は`evaluation_results`メニューで確認できる。

## 既存ルールを別のホスト向けに複製・拡張する

「〇〇（既存のルール名）と同じ構成を△△（ホスト名）向けにも作って」のような依頼を受けた場合の手順。

### Step 0: まず既存構成を読み取る

`menu-filter`で対象ルールと、そこから辿れる`filter`/`action`、さらに`labeling`/`label_creation`/`event_collection`を取得し、**どのメニューが再利用でき、どれを新規作成するのかを確定させてから**提案すること。

### Step 1: そもそも複製が必要かを先に判断する（重要）

**「イベントが発生したホストに対して対処したい」だけなら、ホストごとに複製する必要はない。** `action`の`event_collaboration`を`True`にすると、イベントの発生元ホスト（固定ラベル`_exastro_host`）がそのまま実行対象になるため、**1組の設定で全ホストをカバーできる**。

したがって提案時は次の2案を提示し、`ask_user_choice`でユーザーに選ばせること。

| 案 | 内容 | 向いているケース |
|---|---|---|
| 案A: イベント連携で1本化 | 既存アクションを`event_collaboration: True`（`host_id`は未指定）に更新する。フィルター・ルールの追加は不要 | 対処内容がホスト共通で、今後ホストが増えても設定を増やしたくない |
| 案B: ホストごとに複製 | 新しいホスト用に`filter`/`action`/`rule`を1組追加する | ホストごとに実行する対処内容やパラメータシートを変えたい |

### Step 2（案Bの場合）: 再利用するものと新規作成するものを分ける

| メニュー | 複製時の扱い |
|---|---|
| `event_collection`（収集設定） | **再利用**。同じ監視ツールから取得するなら追加不要 |
| `label_creation`（ラベル作成） | **再利用**。ラベルキーは共通で使える |
| `labeling`（ラベル付与） | **原則再利用**。ただし`_exastro_host`を付与する設定が無い場合は**新規作成が必要**（下記Step 3-2） |
| `filter`（フィルター） | **新規作成が必須**（下記の理由を参照） |
| `action`（アクション） | **新規作成**。`host_id`を新しいホストにする |
| `rule`（ルール） | **新規作成**。新しいフィルターと新しいアクションを紐付ける |

### Step 3（案Bの場合）: フィルターを再利用してはいけない理由（重要）

- `action`の`host_id`は「Conductorを**どのホストに対して実行するか**」の指定にすぎず、**どのイベントにマッチするかには影響しない**。
- そのため既存フィルターをそのまま2つのルールで共有すると、**どちらのルールも全ホストのイベントで発火**し、関係ないホストにまで対処が走る（しかも`rule_priority`が同じだと挙動が不定になる）。
- 正しくは、**`filter_condition_json`に固定ラベル`_exastro_host`の条件を足した新しいフィルターを作る**。
- **さらに、元のフィルターにも`_exastro_host`条件を追加（`Update`）すること。** これを忘れると、元のルールが新ホストのイベントまで拾い続け、出し分けが成立しない。この更新は既存設定の挙動を変えるため、必ず提案に含めてユーザーの承認を取ること。
- なお条件がまったく同じフィルターは2つ作れない（`Identical filter conditions cannot be specified.` / 499-00201）。名前を変えるだけでは登録できないので、必ず条件自体を異なるものにすること。
- ルールの一意制約も`filter_a`+`filter_operator`+`filter_b`なので、**同じフィルターを使うルールを2つ作ることもできない**（`The combination is incorrect.` / MSG-00006）。フィルターの新規作成は避けられない。

### Step 3-2（案A・案B共通）: `_exastro_host`を付与する`labeling`があるか確認する（重要）

- `_exastro_host`は固定ラベルだが、**値は自動では入らない**。`labeling`でイベントのホスト名フィールドを`_exastro_host`に写す設定が必要。
- Step 0で取得した`labeling`に`label_key_name`が`_exastro_host`のレコードが**無ければ、新規作成を提案に含めること**。これが無いと、
  - 案B: `_exastro_host`条件のフィルターが永久にマッチしない
  - 案A: `event_collaboration: True`でも実行対象ホストが決まらない
- 1件で全ホストをカバーできる書き方（`search_key_name`のみ指定し、他は`null`）は`filter.md`を`get-document`で参照すること。`_exastro_host`を`label_creation`で作ろうとしてはいけない（`_exastro_`始まりは`label_key_name`の正規表現違反で失敗する）。
- `search_key_name`に指定するイベント側のフィールド名は実際のイベント構造に依存するため、推測した場合はその旨を明示してユーザーに確認すること。

### Step 4（案Bの場合）: 具体的な呼び出し例

既存: ルール`CPUアラート対応ルール` → フィルター`高負荷アラートフィルター`（条件にホスト指定なし）→ アクション（`host_id: [H]web-server-01`）
依頼: これを`web-server-02`向けにも作る

**4-0. 【書き込み前に必須】案Bが成立するかを先に判定する**

アクションには一意制約があり、**古いバージョンでは`operation_id`+`conductor_class_id`+`event_collaboration`の3列しか見ていない**（`host_name`は含まれない）。そのため「既存アクションと同じConductorで、ホストだけ変えたアクション」は登録できず、`The combination is incorrect.`（499-00201）で失敗する。

**1件も書き込む前に**`menu-filter`（`menu: "action"`）で既存アクションを取得し、次を判定すること。

- 既存アクションが「Conductor直接実行モード」（`operation_id`が`null`）で、これから作るアクションと`conductor_class_id`が同じ場合 → **そのままでは案Bを実行できない**。
  - この時点でユーザーに状況を伝え、次のどれにするか`ask_user_choice`で選ばせる。**失敗してから直すのではなく、書き込む前に確定させる。**
    1. **案Aに切り替える**（既存アクションを`event_collaboration: True`に更新し、フィルター・ルールの追加はしない）… 最もシンプル。ホスト別のフィルター／ルールも不要になる
    2. **オペレーション実行モードで作る**（`operation_list`にホスト用オペレーションを新規作成し、アクションは`operation_id`を指定。`host_id`/`parameter_sheet_id`は指定しない）
        - オペレーションを新規作成する場合は、その前に`get-document`で`documents-menu/operation_list.md`を取得すること（`scheduled_date_for_execution`が必須のため、省略すると`{"scheduled_date_for_execution": ["Required fields."]}`で失敗する）
    3. **別のConductorを使う**（対処内容自体を分けたい場合のみ）
  - **重要** 1を選んだ場合はフィルターの新規作成も既存フィルターの更新も**不要**。先にフィルターを作ってしまうと後で廃止する手戻りが発生するので、**書き込みはこの判定の後に始めること**。
- 衝突しない場合（既存がオペレーション実行モード、または別Conductorを使う場合）→ 4-1以降をそのまま実行する。

**また、`Update`/`Discard`には直前の`menu-filter`で取得した`last_update_date_time`を必ず含めること。** この値は更新ごとに変わるため、**同じレコードに連続して書き込む場合は毎回`menu-filter`で取り直す**こと。古い値を使うと`Processing was canceled because the record was updated from another session.`、省略すると`last_update_date_time is invalid (None)`で失敗する。

**さらに`Update`では、バリデーションが「今回渡した値」だけで判定される**（既存レコードの値は補完されない）。そのため**変更しない項目も含めて全項目を渡すこと**。1項目だけ渡すと、例えば`rule`では`filter_a`が未指定とみなされて`Duplicate filters are selected.`、`action`では`If an Host/Event cooperation or Host/Host name is selected, necessary to set the usage Parameter Sheet Name.`で失敗する（いずれも499-00201）。

**4-1. 既存フィルターにホスト条件を追加（Update）**
```json
{
  "menu": "filter",
  "records": [{
    "type": "Update",
    "parameter": {
      "filter_id": "<既存のfilter_id>",
      "last_update_date_time": "<menu-filterで取得した値をそのまま>",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"高負荷アラート\"], [\"_exastro_host\", \"==\", \"web-server-01\"]]"
    }
  }]
}
```

**4-2. 新ホスト用フィルターを作成**
```json
{
  "menu": "filter",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "filter_name": "高負荷アラートフィルター（web-server-02）",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"高負荷アラート\"], [\"_exastro_host\", \"==\", \"web-server-02\"]]",
      "search_condition_id": "Unique"
    }
  }]
}
```
`_exastro_host`の値は**ホスト名のみ**（`[H]`接頭辞を付けない）。

**4-3. 新ホスト用アクションを作成**

**注意** 古いバージョンでは、アクションの一意制約が`operation_id`+`conductor_class_id`+`event_collaboration`の3列しか見ていないため、**既存アクションと同じConductorを使ってホストだけ変えたアクションは登録できない**（`The combination is incorrect.` / 499-00201）。下記で失敗した場合は`action.md`の「アクションの一意制約」節の回避策（イベント連携で1本化／オペレーション実行モードにする／別Conductorを使う）に切り替えること。
```json
{
  "menu": "action",
  "records": [{
    "type": "Register",
    "parameter": {
      "action_name": "サービス再起動（web-server-02）",
      "conductor_class_id": "<既存アクションと同じConductor>",
      "event_collaboration": "False",
      "host_id": "[H]web-server-02",
      "parameter_sheet_id": "<既存アクションと同じパラメータシート>"
    }
  }]
}
```

**4-4. 新ホスト用ルールを作成**
```json
{
  "menu": "rule",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "rule_name": "CPUアラート対応ルール（web-server-02）",
      "rule_label_name": "high_load_rule_web_server_02",
      "rule_priority": "1",
      "filter_a": "高負荷アラートフィルター（web-server-02）",
      "action_id": "サービス再起動（web-server-02）",
      "conclusion_label_settings": "[]",
      "action_label_inheritance_flag": "True",
      "event_label_inheritance_flag": "False",
      "ttl": "3600"
    }
  }]
}
```
- `rule_label_name`は既存ルールと重複しない値にする（登録後は変更できない）。
- フィルターが`_exastro_host`で排他になっているため、両ルールが同じイベントで同時にマッチすることはない。よって`rule_priority`は既存と同じ値でよい。

### 複製時のチェックリスト

提案を提示する前に、次の全てを満たしているか自己点検すること。

1. **書き込みを1件も行う前に**、Step 4-0のアクション一意制約の事前チェックを`menu-filter`で済ませたか（案Bが成立するかの判定）
2. 新しいフィルターの`filter_condition_json`に`_exastro_host == <新ホスト名>`が入っているか
3. **既存フィルターにも`_exastro_host == <元ホスト名>`を追加する`Update`を提案に含めているか**
4. 新しいルールの`rule_label_name`が既存と重複していないか
5. 再利用するもの（収集設定・ラベル作成・ラベル付与）と新規作成するもの（フィルター・アクション・ルール）を提案の中で明示しているか
6. 案A（`event_collaboration: True`による1本化）も選択肢として提示したか
7. `Update`/`Discard`のペイロードに、直前の`menu-filter`で取得した`last_update_date_time`が入っているか
8. `Update`のペイロードに、変更しない項目も含めて全項目が入っているか（渡した値だけでバリデーションされるため）
