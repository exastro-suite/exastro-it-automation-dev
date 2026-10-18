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
