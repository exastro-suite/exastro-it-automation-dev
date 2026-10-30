# menu-filter tool reference

## file parameter
- 最初に「いいえ」と指定してください。
- ファイルが必須であるためオプションを「はい」に設定する場合は、オプションを「いいえ」に設定したときに取得したリストに基づいてレコード数を十分に絞り込む`filter_conditions`を指定する必要があります。

## Filter Conditions Format
このセクションでは、`.filter_conditions` のパラメータを指定する方法について説明します

### Supported Search Options
- **NORMAL**: 部分一致 - `{"column_name_rest": {"NORMAL": "exact_value"}}`
- **LIST**: 複数の値 (完全一致) - `{"column_name_rest": {"LIST": ["value1", "value2"]}}`
- **RANGE**: 範囲検索 - `{"column_name_rest": {"RANGE": {"START": "min", "END": "max"}}}`

### Examples
```json
// Exact match
{"operation_name": {"NORMAL": "operation name"}}

// Multiple values
{"status": {"LIST": ["Completed", "Executing"]}}

// Empty = 廃止されていない全レコードを取得（廃止済みは含まれない。下記参照）
{}
```

## 廃止済みレコードの扱い（重要）
- **`filter_conditions`に`discard`を指定しない場合、自動で`{"discard": {"NORMAL": "0"}}`が付き、廃止されていないレコードだけが返る。** 空の`{}`でも廃止済みは含まれない。
- 廃止済みのレコードを探すとき（「廃止から復元して」等）は、`discard`を明示すること。
  ```json
  // 廃止済みだけ
  {"rule_name": {"NORMAL": "CPU Alert File Copy Rule"}, "discard": {"NORMAL": "1"}}
  // 廃止済みと有効の両方
  {"rule_name": {"NORMAL": "CPU Alert File Copy Rule"}, "discard": {"LIST": ["0", "1"]}}
  ```
- 同じ名前の廃止済みレコードが複数あることは珍しくない（作り直しのたびに残る）。復元対象を選ぶときは、`last_update_date_time`が新しいものを候補にし、参照先（ルールの`filter_a`/`action_id`など）が有効かも確認すること。参照先が廃止されていると、その項目は`Failed to exchange ID. (<ID>)`と表示される。複数候補がある場合はユーザーに確認すること。
