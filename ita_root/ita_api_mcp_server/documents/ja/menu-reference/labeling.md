# labeling reference

OASEのラベル付与設定。受信したイベントの特定フィールドの値を条件に、`label_creation`で作成したラベルキー（または固定ラベル）に値を設定する。**`event_collection`（収集設定）と`label_creation`（ラベルキー）を先に作成しておく必要がある**。

## event_collection_settings_name column

- 事前に`event_collection`メニューで作成済みの収集設定名を指定する（存在しない名称を指定するとエラーになる）。

## 付与パターンは3つある（どれを使うか先に決めること）

`labeling`は指定する項目の組合せによって挙動が変わる。**やりたいことから逆算してパターンを選ぶこと。**

| | やりたいこと | `search_key_name` | `type_name`/`comparison_method`/`search_value_name` | `label_value_name` |
|---|---|---|---|---|
| パターンA | 条件に合致したときだけ固定値を付与する | 指定 | 指定 | 指定 |
| パターンB | 条件を使わず常に固定値を付与する | **空欄** | **すべて空欄** | 必須 |
| パターンC | **イベント項目の値をそのままラベル値にする（値の抽出）** | 指定 | **すべて`null`** | **`null`** |

- 「イベントの〇〇という項目を、条件に使う値としてラベルに取り出したい」という要望は**パターンC**である。パターンAで代用しようとすると、取り得る値ごとに1件ずつ設定を作ることになり破綻する。
- 「〇〇が△△を**超えたとき**だけ対象にしたい」というしきい値（大小比較）の要望は**パターンA**である。`filter`は`==`/`≠`しか持たないため、大小比較はこの`labeling`で行い、filterでは付与されたラベルを`==`で見る、という2段構えにする（`filter.md`の「しきい値（大小比較）の条件を作りたいとき」節を参照）。**パターンCで値を抽出してもしきい値判定にはならない**（filterで`> 80`と書けないため）。
- 詳細は下記「パターンC」節を参照。

## パターンC: イベント項目の値をそのままラベルに抽出する

- `search_key_name`だけを指定し、`type_name`/`comparison_method`/`search_value_name`/`label_value_name`を**すべて明示的に`null`で渡す**と、そのフィールドの値がそのままラベル値になる。
- **値の種類ごとに設定を作る必要はない。1件でそのフィールドの全ての値に対応できる。**

```json
{
  "menu": "labeling",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "重大度ラベル付与",
        "event_collection_settings_name": "Zabbix監視イベント収集",
        "search_key_name": "event.severity",
        "type_name": null,
        "comparison_method": null,
        "search_value_name": null,
        "label_key_name": "severity",
        "label_value_name": null
      }
    }
  ]
}
```

- **キー自体を省略してはいけない。** 省略すると`{"0": {"Individual check": ["Required keys ['type_name', 'comparison_method', 'search_value_name', 'label_value_name'] are missing."]}}`（499-00201）になる。
- **空文字`""`を渡してもいけない。** `{"0": {"type_name": ["The input value is an invalid value.(input value:)"], "comparison_method": ["The input value is an invalid value.(input value:)"]}}`（499-00201）になる。必ずJSONの`null`を渡すこと。
- 付与先の`label_key_name`は、固定ラベル以外は**事前に`label_creation`で作成しておく必要がある**。ラベルキーを作っただけでは値が入らないため、`label_creation`と`labeling`は必ずセットで提案すること。

## search_key_name column

- 受信イベントのJSON内のキーをJMESPath形式で指定する。
- 使用可能文字: 正規表現 `^[a-zA-Z0-9!#%&()*+,-.;<=>?@[\]^_{|}~]+$`
- **どのフィールド名になるかは実際のイベントJSONの構造に依存する。** 推測した場合は「推測である」旨をユーザーに伝えて確認を取ること。既存の`labeling`設定の`search_key_name`（例: `event.type`）が同じ収集設定にあれば、その接頭辞を踏襲するのが安全。
- なお受信済みイベントの実データを`event_history`メニューで確認しようとしても、`menu-filter`では`System Error (999-99999)`になり取得できない。**イベント構造の確認手段として`event_history`を試さないこと**（ターンを消費するだけになる）。
- 空欄にする場合は、`type_name`/`comparison_method`/`search_value_name`も全て空欄にすること（パターンB。検索条件を使わず、常に固定のラベル値を付与する）。この場合`label_value_name`は必須。

## type_name column と comparison_method column（組合せ早見表）

値のデータ型と比較方法は組み合わせが決まっている。表にない組合せはバリデーションエラーになる。

| type_name（値のデータ型） | 使用できる comparison_method |
|---|---|
| `string`（文字列）, `integer`（整数）, `float`（小数） | `==`（等しい）, `≠`（等しくない）, `<`, `<=`, `>`, `>=` のいずれか（正規表現系は不可） |
| `bool`（真偽値）, `object`（オブジェクト）, `array`（配列）, `falsy`（空判定） | `==`, `≠` のみ |
| `any`（その他） | `RegExp`（正規表現、optionなし）, `RegExp(DOTALL)`, `RegExp(MULTILINE)` のいずれかのみ |

- **`<`/`<=`/`>`/`>=`が使えるのはこの`labeling`メニューだけで、`filter`の条件（`condition_type`）には存在しない。** しきい値でイベントを絞り込む要件は、ここで大小比較してラベルを付け、`filter`ではそのラベルを`==`で判定する。
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
- `null`を渡すとパターンC（`search_key_name`のフィールド値をそのまま付与）になる。空文字`""`と`null`は意味が異なるので混同しないこと。

## 新規作成時の最小サンプル（パターンA: CPU使用率が80を超えたらlabel_valueに実測値を入れる例）

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
