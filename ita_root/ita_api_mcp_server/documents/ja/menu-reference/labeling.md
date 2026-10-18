# labeling reference

OASEのラベル付与設定。受信したイベントの特定フィールドの値を条件に、`label_creation`で作成したラベルキー（または固定ラベル）に値を設定する。**`event_collection`（収集設定）と`label_creation`（ラベルキー）を先に作成しておく必要がある**。

## event_collection_settings_name column

- 事前に`event_collection`メニューで作成済みの収集設定名を指定する（存在しない名称を指定するとエラーになる）。

## search_key_name column

- 受信イベントのJSON内のキーをJMESPath形式で指定する。
- 使用可能文字: 正規表現 `^[a-zA-Z0-9!#%&()*+,-.;<=>?@[\]^_{|}~]+$`
- 空欄にする場合は、`type_name`/`comparison_method`/`search_value_name`も全て空欄にすること（検索条件を使わず、常に固定のラベル値を付与するパターン）。この場合`label_value_name`は必須。

## type_name column と comparison_method column（組合せ早見表）

値のデータ型と比較方法は組み合わせが決まっている。表にない組合せはバリデーションエラーになる。

| type_name（値のデータ型） | 使用できる comparison_method |
|---|---|
| `string`（文字列）, `integer`（整数）, `float`（小数） | `==`（等しい）, `≠`（等しくない）, `<`, `<=`, `>`, `>=` のいずれか（正規表現系は不可） |
| `bool`（真偽値）, `object`（オブジェクト）, `array`（配列）, `falsy`（空判定） | `==`, `≠` のみ |
| `any`（その他） | `RegExp`（正規表現、optionなし）, `RegExp(DOTALL)`, `RegExp(MULTILINE)` のいずれかのみ |

- `type_name`が`integer`の場合、`search_value_name`は整数に変換できる値でなければならない。`float`の場合は小数に変換できる値、`bool`の場合は`"true"`/`"false"`（大文字小文字区別なし）のいずれかでなければならない。
- `type_name`が`object`の場合は`search_value_name`が`{`で始まり`}`で終わる有効なJSON、`array`の場合は`[`で始まり`]`で終わる有効なJSONでなければならない。
- `type_name`が`falsy`の場合、`search_value_name`は空にすること（値を入れるとエラー）。かつ`comparison_method`が`≠`のときは`label_value_name`が必須。
- `type_name`が`any`で正規表現を使う場合、`search_value_name`に正規表現として妥当な文字列を指定すること（コンパイルできないとエラー）。
- **部分一致用の比較方法は存在しない。** `Contains`/`contains`/`LIKE`/`in`といった値は存在せず、`{"comparison_method": ["The input value is an invalid value.(input value:Contains)"]}`（499-00201）で失敗する。部分一致させたい場合（例:「トリガー名に`CPU`が含まれる」）は、`type_name: "any"` + `comparison_method: "RegExp"` + `search_value_name: ".*CPU.*"` を使うこと。
- 受け付けられる値の正確な一覧は、このメニューに対して`list-menu-info-pulldown`を実行すると確認できる。

## label_key_name column

- 必須。付与先のラベルキー名を指定する（`label_creation`で作成済みのもの、または固定ラベル）。

## label_value_name column

- 付与するラベルの値。
- 正規表現（`RegExp`系）を使った場合、キャプチャグループを`\1`, `\2`...のように参照できる。空欄にするとマッチ結果全体がそのまま使われる。

## 新規作成時の最小サンプル（CPU使用率が80を超えたらlabel_valueに実測値を入れる例）

```json
{
  "menu": "labeling",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "CPU使用率ラベル付与",
        "event_collection_settings_name": "Zabbix監視イベント収集",
        "search_key_name": "cpu.usage",
        "type_name": "float",
        "comparison_method": ">",
        "search_value_name": "80",
        "label_key_name": "cpu_usage",
        "label_value_name": ""
      }
    }
  ]
}
```
