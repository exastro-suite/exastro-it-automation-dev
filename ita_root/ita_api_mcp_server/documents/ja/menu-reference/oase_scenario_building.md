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
- そのため既存フィルターをそのまま2つのルールで共有すると、どのホストのイベントでも**優先順位が上のルール1本だけ**が動く（1つのイベントは1つのルールにしか使われない。`rule.md`の「1つのイベントで動くルールは1つだけ」節参照）。結果として、**イベントと関係ないホストに対処が走り、もう一方のルールは永久に動かない**。
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

## イベントの任意の項目をラベルとして抽出する

「〇〇（イベント種別）の□□（項目名）をラベルとして使えるようにして」のような、**条件に使う値を1つ増やすだけ**の依頼の手順。6メニュー全部を触る必要はない。

### 必要なのは2メニューだけ

| メニュー | 作業 |
|---|---|
| `event_collection` | **再利用**。既存の収集設定を使う（新規作成は不要） |
| `label_creation` | **新規作成**。ラベルキーを1件追加 |
| `labeling` | **新規作成**。イベント項目の値をラベル値に写す設定を1件追加 |
| `filter` / `action` / `rule` | **触らない**。抽出したラベルを実際に条件として使う段階で初めて必要になる |

- `label_creation`だけ作っても値は入らない。**必ず`labeling`とセットで提案すること。**
- 逆に`labeling`だけ作ってもラベルキーが存在しないとエラーになる。作成順は`label_creation`→`labeling`。

### 手順

1. `menu-filter`で既存の`label_creation`と`labeling`を取得する。
    - 同じラベルキーが既にあれば新規作成は不要（その旨をユーザーに伝える）。
    - 既存`labeling`の`search_key_name`（例: `event.type`）を見て、イベントJSONの構造の手がかりにする。
2. **提案を作る前に`get-document`で`documents-menu/labeling.md`を取得する。** 付与パターンが3つあり、この依頼は「パターンC（イベント項目の値をそのまま抽出）」に該当する。値の種類ごとに設定を作るパターンAで代用してはいけない。
3. `label_creation`でラベルキーを登録する。
4. `labeling`でパターンCの設定を登録する（`search_key_name`のみ指定し、`type_name`/`comparison_method`/`search_value_name`/`label_value_name`はすべて`null`）。
5. 「このラベルは今後`filter`の条件に使える」旨をユーザーに伝えて完了とする。

### 注意点

- **イベント側のフィールド名は推測になることが多い。** 推測である旨を明示してユーザーに確認を取ること。`event_history`メニューで実データを確認しようとしても`System Error (999-99999)`になるため、確認手段として試さないこと。
- 「どんな値が来るか」をユーザーに聞く必要はない。パターンCは1件でそのフィールドの全ての値に対応できる。

## ラベルの値がしきい値を超えたときだけ対象にする

「□□（例: CPU使用率）が△△（例: 80%）を超えたときだけ対象にしたい」のような、**数値のしきい値で絞り込む**依頼の手順。

### filterには大小比較が無い（最重要）

`filter`の`condition_type`は`==`と`≠`の2値しかなく、`>`や`>=`は存在しない。そのため**しきい値の判定は`labeling`側で行い、`filter`はその結果のラベルを`==`で見る**という2段構えにする。これがExastroでの唯一の実現方法である。

```
labeling（ここで大小比較）                      filter（ここは == だけ）
  event.cpu_usage > 80 (float)  ──▶  cpu_over_80 = "true"  ──▶  ["cpu_over_80","==","true"]
                                     （80以下のイベントには
                                       ラベルが付かない）
```

| メニュー | 作業 |
|---|---|
| `label_creation` | **新規作成**。しきい値判定用のラベルキーを1件追加（例: `cpu_over_80`） |
| `labeling` | **新規作成**。パターンA（条件付き固定値）で`comparison_method`に`>`等を指定 |
| `filter` | **更新**。既存フィルターの`filter_condition_json`にそのラベルの`==`条件を追加 |
| `event_collection` / `action` / `rule` | **触らない** |

### 手順

1. **提案を作る前に`get-document`で`documents-menu/filter.md`と`documents-menu/labeling.md`を取得する。** filter側に大小比較が無いことと、`labeling`のパターンA（`type_name`×`comparison_method`の組合せ）を確認する。
2. `menu-filter`で既存の`label_creation`/`labeling`/`filter`を取得する。**「既にOASEの設定をしていますか」のように、自分で`menu-filter`すれば分かることをユーザーに質問してはいけない。** 既存構成を自分で把握した上で提案を組み立てること。
3. `label_creation`でしきい値判定用のラベルキーを登録する。
4. `labeling`でパターンAの設定を登録する。
    - `search_key_name`: しきい値を判定する数値が入っているイベント項目（例: `event.cpu_usage`）
    - `type_name`: `float`（整数しか来ないと分かっているなら`integer`）
    - `comparison_method`: `>`（「以上」なら`>=`。「超えた」と「以上」でどちらになるかはユーザーに確認する）
    - `search_value_name`: しきい値（例: `80`）
    - `label_value_name`: `true`のような固定値
5. `filter`を`Update`して`filter_condition_json`に`["<ラベルキー>", "==", "true"]`を追加する。
6. しきい値を下回るイベントにはラベルが付かないため条件にマッチしない、という仕組みをユーザーに説明して完了とする。

### 注意点

- **パターンC（値の抽出。全項目`null`）では要件を満たせない。** 値を`cpu_usage`ラベルに抽出しても、filterで`cpu_usage > 80`と書けないため絞り込めない。しきい値判定は必ずパターンA。
- **「監視ツール側で80%以上のアラートだけ送るよう設定する」はExastro側の設定ではない。** ユーザーがExastroでの条件設定を求めているときに、これを第一候補や推奨案として提示してはいけない。
- 「超えたとき（`>`）」か「以上（`>=`）」か、しきい値を`label_key_name`に埋め込むか（`cpu_over_80`）値に依存しない名前にするか（`cpu_threshold_exceeded`）は、ユーザーに確認すること。
- しきい値を判定する数値のフィールド名は推測になることが多い。推測である旨を明示して確認を取ること。
- **既存フィルターのどれにしきい値条件を追加するかは必ずユーザーに確認すること。** 既存ルールの発火条件が狭まるため、黙って全フィルターを更新してはいけない。
- `filter`の`Update`では、直前の`menu-filter`で取得した`last_update_date_time`を必ず渡すこと。省略すると`last_update_date_time is invalid (None)`（499-00201）になる。変更しない列（`filter_name`/`search_condition_id`/`available_flag`等）も全て再送すること。

## 既存ルールにマッチしたら別のConductorを実行する

「〇〇（ルール名）にマッチしたら△△（Conductor名）を実行して」という依頼への対応手順。詳細は`rule.md`の「既存ルールにマッチしたら別のConductorを実行する（差し替え／追加）」節と`action.md`を参照。

### 最初に押さえる仕様（最重要）

- **1つのイベントで動くルールは1つだけ**（マッチしたイベントは予約済みになり、他のルールには渡らない）。優先順位は`rule_priority`の**数値が小さいほど高い**。
- **1つのルールに指定できるアクションは1つだけ。**
- よって「今のアクションに加えて△△も」は、ルールやフィルターを増やすだけでは実現できない。結論イベントでの連鎖が必要になる。

### 手順

1. **提案を作る前に`get-document`で`documents-menu/rule.md`と`documents-menu/action.md`を取得する。**
2. `menu-filter`で対象ルール・既存アクション・フィルターを取得し、ルールに今どのアクションが紐付いているかを把握する（ユーザーに聞かない）。
3. 既存ルールに既にアクションがある場合は、**差し替え（今のアクションの代わりに△△）か、追加（今のアクションの後に△△も）かを`ask_user_choice`で確認する**。選択肢には次を明記すること。
    - 差し替え: 今のアクション（例: Sleep）は実行されなくなる
    - 追加: 結論イベントで連鎖させるため、**△△は今のConductorが正常終了したときだけ、その後に直列で**実行される
4. △△の`conductor_class_id`を使う既存アクションがあれば流用する。無ければアクションを新規作成する。
    - `list-menu-info-pulldown`の`parameter_sheet_id`に△△のパラメータシートが無い場合（ホストグループ対応のシート等）は、**モードA（オペレーション実行）しか使えない**。
    - モードAで既存オペレーションを流用するか新規作成するかはユーザーに確認する。流用するなら、そのオペレーションの登録済みパラメータ（対象ホスト等）を`menu-filter`で調べて提示する。
5. 差し替えの場合: 既存ルールを`Update`して`action_id`だけを変える（変更しない列と`last_update_date_time`も全て渡す）。
6. 追加の場合: `rule.md`の連鎖手順どおり、`label_creation`（連鎖用ラベル）→ 既存ルールの`conclusion_label_settings`更新 → 結論イベント用`filter`新規 → `action` → `rule`新規の順に登録する。

### 注意点

- 「同じフィルターで2本目のルールを作る」「同じ条件のフィルターをもう1つ作る」は一意制約で登録できない。また作れたとしても、1つのイベントでは1本しか動かない。
- 連鎖用のフィルター条件に`_exastro_rule_name`は使えない（プルダウンに無い）。必ず独自のラベルキーを`conclusion_label_settings`で付与する。
- `maintenance-all`の`records`は配列で渡すこと。JSON文字列にすると`Records array is required`になる。

## OASE設定を廃止する／廃止から復元する

「◇◇（ルール名）を廃止にして」「◇◇を廃止から復元させて」への対応手順。書き方そのものは`documents-tools/maintenance-all.md`の「破棄（Discard）・復元（Restore）」節、廃止済みの探し方は`documents-tools/menu-filter.md`の「廃止済みレコードの扱い」節を参照。

### 最初に押さえる仕様（最重要）

- **OASEの6メニューは、廃止時に参照チェックをしない。** 有効なルールが使っているフィルターやアクションでも廃止できてしまう。その場合ルールは**エラーを出さずに動かなくなる**（判定時に参照先のフィルターが無いとしてスキップされる）。
- **復元時も参照先が有効かはチェックされない。** フィルターやアクションが廃止されたままのルールを復元しても、そのルールは動かない。
- 参照先が廃止されていると、参照している側の項目は`Failed to exchange ID. (<ID>)`と表示される。

### 依存関係と順序

```
label_creation ◀── labeling ◀── filter ◀── rule ──▶ action
（ラベルキー）    （ラベル付与）  （フィルター） （ルール） （アクション）
```

- **廃止**: 使う側から先に止める。`rule` → （`filter`／`action`）→ `labeling` → `label_creation`
- **復元**: 使われる側から先に戻す。`label_creation` → `labeling` → （`filter`／`action`）→ `rule`

### 手順

1. **`get-document`で`documents-tools/maintenance-all.md`と`documents-tools/menu-filter.md`を取得する。**
2. 対象を`menu-filter`で取得する。復元の場合は`{"discard": {"NORMAL": "1"}}`を付ける。同名の廃止済みが複数あれば、`last_update_date_time`と参照先の有効性で候補を絞り、それでも1件に決まらなければユーザーに確認する。
3. **影響範囲を調べて提示する。**
    - フィルター／アクションを廃止する場合: それを使っている有効な`rule`を`menu-filter`で探す。あれば「そのルールが動かなくなる」ことを伝え、ルールも廃止するか、フィルター／アクションだけ廃止するかを`ask_user_choice`で確認する。
    - ルールを復元する場合: `filter_a`/`filter_b`/`action_id`が有効か確認する。廃止されていれば、先にそれらを復元する必要があることを伝える。
    - ラベルキーを廃止する場合: それを使う`labeling`/`filter`の条件/`rule`の`conclusion_label_settings`を確認する。
4. ユーザーの承認を取ってから`Discard`/`Restore`を実行する。`parameter`は**主キーと`last_update_date_time`だけ**にし、`discard`を含めない。
5. **`menu-filter`で読み直し、`discard`の値が変わったことを確認してから完了を報告する。**

### 注意点

- 「廃止」と「物理削除（`Delete`）」は別物。ユーザーが「廃止」と言ったら`Discard`を使う。
- 廃止したルールに紐付いていたフィルター・アクションは残る。不要なら続けて廃止できることを伝える（勝手に廃止しない）。
- シナリオ1-5の連鎖構成のように、別のルールの`conclusion_label_settings`がこのルール用のラベルを付けている場合、そのラベルは使われずに残る（害はない）。気づいたら伝えること。

## 新しい収集設定を追加し、既存のラベル付与設定をコピーして流用する

「〇〇（既存の収集設定名）と同じラベル付与設定を、新しく追加する△△（収集設定名）にもコピーして設定して」への対応手順。同じ種類の監視ツールを複数台に増やすときの典型パターン。

### 手順

1. **`get-document`で`documents-menu/event_collection.md`と`documents-menu/labeling.md`を取得する**（それぞれの「複製」「コピー」節）。
2. `menu-filter`でコピー元の収集設定と、そのラベル付与設定を全件取得する。
3. 複製先の収集設定について、**`url`と認証情報（`auth_token`等）をユーザーに確認する**。認証情報は`menu-filter`で取れないため、既存からはコピーできない。それ以外の項目は既存の値を流用し、流用する旨を提案に書く。
4. **既存のフィルターとルールが、新しい収集設定のイベントにどう効くかを`menu-filter`で実際に調べてから説明する**（下記「影響の考え方」）。調べずに「フィルターにホスト条件はありません」などと推測で断定してはいけない。
5. 承認後、`event_collection`（新規）→ `labeling`（コピー、1件ずつ`Register`）の順に登録する。
6. `menu-filter`で読み直し、コピー先のラベル付与設定がコピー元と同じ件数・同じ内容であることを確認してから報告する。

### 影響の考え方（重要）

- **フィルターとルールは収集設定を区別しない。** フィルターはラベルの値だけを見るので、新しい収集設定のイベントでもラベルが条件に合えば、既存のルールが発火する。
- したがって、既存フィルターの条件を見て次のように説明すること。
    - `_exastro_host`の条件がある場合: 新しい監視ツールのイベントでも、ホスト名がその値と一致したときだけ発火する。一致しないホストのイベントには、ラベルが付くだけでどのルールも動かない。新しいホスト用の対処が必要なら、フィルターとルールの追加（シナリオ「既存ルールを別のホスト向けに複製・拡張する」）が別途必要になる。
    - `_exastro_host`の条件が無い場合: 新しい監視ツールのどのホストのイベントでも、既存のルールが動く。
- 収集設定ごとに対処を分けたい場合は、固定ラベル`_exastro_event_collection_settings_id`（値は収集設定のID）をフィルター条件に使える。

### 注意点

- 収集設定だけ追加してラベル付与設定をコピーしないと、新しい収集設定のイベントには`_exastro_host`を含めてラベルが1つも付かず、どのルールにもマッチしない。
- コピー先の`labeling_settings_name`は、コピー元と区別できる名前にする（例: 末尾に` (zabbix-02)`）。

## 不要になったラベル付与設定を整理する（物理削除の依頼）

「〇〇（収集設定名）に紐づく不要なラベル付与設定を物理削除して」への対応手順。

### 最初に押さえる仕様（最重要）

- **OASEのメニュー（`labeling`を含む）は物理削除できない。** `list-menu-info`の`row_delete_flag`が`"0"`で、`Delete`は`401-00001`になる。これはロール権限の問題ではないので、権限の付与を案内してはいけない（`documents-tools/maintenance-all.md`の「物理削除（Delete）」節）。
- できるのは廃止（`Discard`）だけで、**廃止してもレコードはDBに残り、レコード数は減らない**。依頼の目的が「レコード数の削減」なら、ITAの機能では達成できないことを正直に伝えること。

### 手順

1. **`get-document`で`documents-tools/maintenance-all.md`と`documents-tools/menu-filter.md`を取得し、`list-menu-info`で`labeling`の`row_delete_flag`/`row_disuse_flag`を確認する。** `Delete`を試してからエラーで気づくのではなく、先に確認すること。
2. 対象の収集設定に紐づくラベル付与設定を`menu-filter`で取得する。
3. **「不要」の中身をユーザーに確認する。** 判断の材料として、各ラベル付与設定が付けるラベルが使われているかを調べて提示する。
    - `filter`の`filter_condition_json`の条件、`group_label_key_ids`
    - `rule`の`conclusion_label_settings`
    - `_exastro_host`はフィルター条件に無くても、`action`の`event_collaboration: True`（実行先ホストの決定）に使われる
4. 物理削除はできないので、代わりに廃止でよいかを`ask_user_choice`で確認する。
5. 廃止は`documents-menu/oase_scenario_building.md`の「OASE設定を廃止する／廃止から復元する」節と同じ手順で行い、読み直して確認してから報告する。

### 注意点

- **収集設定が有効なままラベル付与設定をすべて廃止すると、その収集設定のイベントにはラベルが1つも付かなくなる**（`_exastro_host`も入らない）。監視ツール自体を撤去するのであれば、収集設定（`event_collection`）も廃止するかを確認すること。廃止の順序は`labeling` → `event_collection`。

## 2つのイベントが同時に起きたときだけ対応する（AND相関）

「〇〇と△△が同時に起きたときだけ対応したい」への対応手順。詳細は`rule.md`の「AND相関（A and B）」節を参照。

### 手順

1. **`get-document`で`documents-menu/rule.md`を取得し、「AND相関（A and B）」節を読む。**
2. `menu-filter`で`labeling`/`filter`/`rule`を取得し、〇〇と△△のそれぞれについて、ラベル付与とフィルターがあるか、**どちらかのフィルターを単独で使っている既存ルールがあるか**を確認する。
3. 足りないラベル付与・フィルターを作る（イベント項目のフィールド名・値が推測なら申告して確認する）。
4. 既存の単独ルールがある場合は、その扱いを`ask_user_choice`で確認する。第一候補は「既存ルールをAND相関に変える」。既存ルールを残す案を出すときは、優先順位による副作用（`rule.md`の表）を具体的な秒数とともに書くこと。「既存ルールより先に動く可能性がある」のような曖昧な説明で済ませてはいけない。
5. 「同時に」は「収集設定の`ttl`秒以内に両方そろえば」という意味であることを、実際の`ttl`の値を添えて説明する。
6. 承認後に登録・更新し、読み直して確認してから報告する。

### 注意点

- 既存ルールを`Update`してAND相関に変える場合、`conclusion_label_settings`（シナリオ1-5の連鎖ラベル等）は既存の値のまま再送すること。変えると後続の連鎖が止まる。
- ラベル付与は収集設定ごとに必要。収集設定が複数ある場合（シナリオ1-7）は、どの収集設定のイベントを対象にするか確認すること。

## どちらか一方だけ起きたときに対応する（XOR相関）

「〇〇または△△のどちらか一方だけ起きたら対応したい」への対応手順。詳細は`rule.md`の「XOR相関（A xor B）」節を参照。

### 手順

1. **`get-document`で`documents-menu/rule.md`を取得し、「XOR相関（A xor B）」節を読む。** AND相関の節の「`ttl`まで待つ」はXORには当てはまらない。
2. `menu-filter`で`labeling`/`filter`/`rule`を取得し、〇〇と△△のラベル付与・フィルターの有無と、どちらかのフィルターを単独で使う既存ルールの有無を確認する。
3. **「一方だけ」の意味を`ask_user_choice`で確認する。** 選択肢には次の挙動をそのまま書くこと。
    - XOR: それぞれ来たらすぐ対応。同じ判定周期にそろったときだけ何もしない（少しでも時間差があれば両方に対応する）
    - 吸収ルール構成: `ttl`秒以内に両方そろったら何もしない。片方だけなら対応するが、対応は`ttl`秒遅れる
    - 単独ルール2本: どちらが起きても対応する
4. 既存の単独ルールがある場合は、`rule.md`のXORの表に沿って副作用を説明し、扱いを確認する。
5. 承認前に登録内容（ルールの優先順位を含む）を一覧で示し、承認後に登録して、読み直して確認してから報告する。

## 〇〇が起きてから一定時間内に復旧しなければエスカレーションする（時系列相関）

「〇〇が発生してから△△分たっても□□（復旧通知）が来なければエスカレーションしたい」への対応手順。詳細は`rule.md`の「時系列相関（A -> B）」節を参照。

### 手順

1. **`get-document`で`documents-menu/rule.md`を取得し、「時系列相関（A -> B）」節を読む。**
2. `menu-filter`で`event_collection`（`ttl`）・`labeling`・`filter`・`rule`・`action`を取得し、障害と復旧のラベル付与・フィルターの有無、障害のフィルターを単独で使う既存ルールの有無を確認する。
3. 構成は「上位：`A -> B`（障害 → 復旧、アクションなし）の吸収ルール、下位：障害だけのエスカレーションルール」にする。吸収ルールに`A and B`を使わない。
4. **依頼の「△△分」と収集設定の`ttl`を比べる。** 違えば、待ち時間は収集設定の`ttl`で決まることを伝え、`ttl`を変えるか（影響するルールも提示）、今の`ttl`のままにするかを確認する。
5. エスカレーションの内容（Conductor／通知）を確認する。通知なら通知先・テンプレートの設定が必要。
6. 承認前に登録内容（ルールの優先順位、収集設定の`ttl`変更の有無を含む）を一覧で示し、承認後に登録して、読み直して確認してから報告する。

## 冗長構成の監視ツールから届く同じイベントを1件にまとめる（重複排除）

「〇〇と△△の両方から同じアラートが重複して届くので1件にまとめて」への対応手順。詳細は`documents-menu/deduplication.md`を参照。

### 手順

1. **`get-document`で`documents-menu/deduplication.md`を取得する。**
2. `menu-filter`で`event_collection`・`labeling`・`deduplication`を取得し、〇〇と△△の収集設定、それぞれのラベル付与設定、既に重複排除設定に入っている収集設定が無いかを確認する。
3. 各ラベルが監視ツールどうしで同じ値になるかを確認し、判定条件（条件なし／`is matched`／`is ignored`）を根拠とともに提案する。
4. 承認前に登録内容を一覧で示す。複数選択の項目は表示名のJSON配列を**文字列**にして渡す（配列のまま渡すと`System Error (999-99999)`）。
5. 登録後に読み直して確認し、「重複したイベントは先着のイベントにまとめられ、ルールの対処は1回だけ動く」「登録後に受信したイベントから効く」ことを伝えて報告する。

## アラートの種類ごとに通知の文面・宛先を変える（通知設定）

「〇〇（イベント種別）の通知メールの文面を△△用に変えて、宛先も□□にして」への対応手順。詳細は`rule.md`の「ルールの通知（事前通知・事後通知）を設定する」節を参照。

### 手順

1. **`get-document`で`documents-menu/rule.md`を取得し、通知の節を読む。**
2. 「イベント種別」がアラートの種類（CPU高負荷など）か、OASEの通知の種類（新規・既知・未知など）かを判断する。アラートの種類なら、そのアラートを扱うルールを`menu-filter`で特定する。
3. `list-menu-info-pulldown`（`menu: "rule"`）で通知先の候補を確認する。候補に□□が無ければ、Exastro Platformの「通知管理」で通知先を登録してもらう必要があること（メールなら「メール送信サーバー設定」も）を伝える。ツールからは登録できない。
4. 文面は`rule.md`の表の変数（`events`・`rule`・`action`・`conductor`）で作る。`{{ labels.xxx }}`のような共通テンプレートの書き方は使わない。
5. 通知先が未登録の場合は、テンプレートだけ先に登録するか、登録を待つかを確認する。
6. ルールを`Update`する（テンプレートは`create-text-file`の`file_id`で渡し、変更しない列も全て再送）。読み直して確認してから報告する。

## 同じホストで多発するイベントを1つのインシデントにまとめる（グルーピング）

「〇〇（ホスト名）で△△（イベント種別）が多発した場合に1つのインシデントとして集約したい」への対応手順。詳細は`filter.md`の「多発するイベントを1つのインシデントにまとめる（グルーピング）」節を参照。

### 手順

1. **`get-document`で`documents-menu/filter.md`を取得し、グルーピングの節を読む。**
2. `menu-filter`で〇〇の△△を扱うフィルターとルール、収集設定の`ttl`を確認する。`list-menu-info-pulldown`で`search_condition_id`の選択肢（期間延長あり／なしの有無）を確認する。
3. 既存フィルターの検索方法を`Grouping`に変え、`group_label_key_ids`（例: `["_exastro_host", "alert_type"]`）と`group_condition_id`（`is the target`）を指定する。期間延長ありなら`group_period`はキーごと送らない。
4. 変更前後の動き（今は来るたびに対処が動く／同時に来ると全部未知になる → 変更後は1インシデントにつき1回）と、インシデントの区切り（最後のイベントから`ttl`秒静かになるまで同じインシデント）を、実際の`ttl`の値で説明して承認を取る。
5. 更新後に読み直して確認してから報告する。

## 一次ルールの判定結果を使って二次判定する（多段判定）

「◇◇（ルール名）の判定結果を使って、さらに☆☆という条件で二次判定したい」への対応手順。詳細は`rule.md`の「多段判定」節を参照。

### 手順

1. **`get-document`で`documents-menu/rule.md`を取得し、「多段判定」節と「追加: 結論イベントでルールを連鎖させる」節を読む。**
2. `menu-filter`で◇◇の`conclusion_label_settings`・`event_label_inheritance_flag`・アクション、`_exastro_type == conclusion`を含むフィルターとそれを使うルールを確認する。
3. ☆☆の判定に使うラベルが結論イベントに載っていなければ、`conclusion_label_settings`にJinja2で必要なラベルだけを足す（例: `["severity", "{{ A.severity }}"]`）案を第一候補にする。
4. 既に◇◇の結論イベントを使っているルールがあれば、二次判定との関係をユーザーに確認する。
5. **無限ループの確認**: 各段の結論イベントのラベルと、結論イベント用フィルターを照合し、自分自身や前の段のフィルターにマッチしないことを確認して、その結果を提案に書く。
6. 承認後に登録し、読み直して確認してから報告する。

## 障害を自動復旧し、直らなければ通知する（自動復旧＋エスカレーション）

「〇〇（サーバー名）で△△（障害種別）が起きたら□□（Conductor名）で自動復旧して、直らなければ☆☆に通知して」への対応手順。新しい障害種別なら、ラベル付与・フィルター・アクション・ルールの一括構築（本書の前半）に、通知（`rule.md`の通知の節）とエスカレーションを組み合わせる。

### 「直らなければ」の意味を最初に確認する

| 意味 | 作り方 | 注意 |
|---|---|---|
| 自動復旧（Conductor）が**失敗**したら知らせたい | 自動復旧ルールに**事後通知**を付け、本文に`{{ conductor.status }}`を出す | **事後通知は正常終了でも異常終了でも毎回送られる**（失敗のときだけには絞れない） |
| 自動復旧のあと、**一定時間内に復旧通知が来なければ**知らせたい | 下の「結論イベントを起点にしたエスカレーション」 | 自動復旧が失敗すると結論イベントが出ず、エスカレーションも動かない（上の事後通知と組み合わせる） |

### 結論イベントを起点にしたエスカレーション（判定エンジンで確認）

障害イベントは自動復旧ルールが使うので、2-3の「障害 → 復旧」の吸収構成は同じ障害イベントにはかけられない。**自動復旧ルールの結論イベント**を起点にする。

```
障害イベント ─▶ ルール1: 自動復旧（□□を実行。結論ラベルで目印 recovery_tried=true を付ける）
                  │ □□が正常終了すると結論イベントができる
                  ▼
   ┌─ ルール2（上位）: 結論イベント(recovery_tried) and 復旧イベント（A and B、アクションなし）… 何もしない
   └─ ルール3（下位）: 結論イベント(recovery_tried) だけ … ☆☆に通知
```

| 来方 | ルール2が`A and B`（推奨） | ルール2が`A -> B` |
|---|---|---|
| 自動復旧のあと、待ち時間内に復旧イベント | 吸収し、通知しない | 吸収し、通知しない |
| **自動復旧（□□）の実行中に復旧イベント**（結論イベントより先） | 結論イベントができた時点で吸収し、通知しない | **吸収も通知もされない。** その復旧イベントは使われずに収集設定の`ttl`まで残り、その間に起きた次の障害のエスカレーションも黙って止める |
| 復旧イベントが来ない／待ち時間より後に来る | 結論イベントが期限切れになった時点でルール3が動き、通知する | 同左 |
| 前の障害の復旧イベントが使われずに残っている | 吸収され、通知しない（下の注意） | 吸収も通知もされない |

- **ルール2は`A and B`にする。** 自動復旧の実行中に復旧すること（プロセス再起動の直後に監視ツールが復旧を検知するなど）はよくあり、`A -> B`ではその場合に結論イベントより先に復旧イベントが来てしまう。結論イベントのほうが復旧イベントより有効期限が短いため、`rule.md`の「時系列相関」節の`A and B`禁止（障害と復旧が同じ収集設定から来る場合の話）はここには当てはまらない（判定エンジンで確認）。
- 注意: どちらの構成でも、**使われずに残っている復旧イベント**（自動復旧が失敗して結論イベントが出なかったとき、障害なしに届いた復旧など）が収集設定の`ttl`の間に次の結論イベントと出会うと、エスカレーションされない。自動復旧の失敗はルール1の事後通知で知らせる（上の表）ことを合わせて提案し、この制約も伝える。

- **待ち時間はルール1の`ttl`列**（結論イベントの有効期限）で決まる。収集設定の`ttl`ではないので、収集設定を変えずに「〇分以内に直らなければ」を設定できる。依頼の「〇分」を秒にしてルール1の`ttl`に入れる。
- 復旧イベントのフィルターには`["_exastro_type", "≠", "conclusion"]`を入れ、ルール2のフィルターAは結論イベント（`_exastro_type == conclusion`かつ目印ラベル）にする。
- **通知先を指定するルールには`action_id`が必須。** ルール3を「通知だけ」にすることはできないので、何をアクションにするか（もう一度□□を実行する、など）をユーザーに確認する。
- 多段の連鎖なので、`rule.md`の「多段判定」節の無限ループの確認（ルール2・3の結論イベントがルール2・3のフィルターに再びマッチしないこと）を行い、結果を提案に書く。
- 通知先が未登録なら、Platformでの登録が必要なこと（`rule.md`の通知の節）を伝える。
