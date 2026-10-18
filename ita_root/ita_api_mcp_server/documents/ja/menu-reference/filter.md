# filter reference

OASEのフィルター。ラベル条件でイベントを絞り込み、ルール評価の対象を決める。1つのフィルターは複数のルールで再利用できる。

## filter_condition_json column

- REST入力値は `[[label_name, condition_type, condition_value], ...]` という**3要素配列のリストをJSON文字列化**したもの。
  - `label_name`: ラベルの名称（`label_creation`で作成したラベル、または固定ラベル`_exastro_type`等）。
  - `condition_type`: `"=="`（等しい）または`"≠"`（等しくない）の**2値のみ**。それ以外の比較演算子（`<`等）はfilterでは使えない。
  - `condition_value`: 比較する値（文字列）。
- デフォルト値（未指定時の初期値）: `[["_exastro_type", "≠", "conclusion"]]`（結論イベントを除外する標準条件）。新しいフィルターを作る際も、通常イベントのみを対象にするならこの条件を残しておくこと。
- 例: Zabbixからの監視イベントで、イベント種別が`高負荷アラート`のものだけに絞る場合
  ```json
  [["_exastro_type", "≠", "conclusion"], ["event_type", "==", "高負荷アラート"]]
  ```

## search_condition_id column（検索方法）

`group_label_key_ids`/`group_condition_id`/`group_period`の必須・禁止が、選んだ検索方法によって変わる。

**選択肢の数はバージョンによって異なる**（`Grouping`が1つにまとまっている環境と、`Grouping (Period Extension)`/`Grouping (No Period Extension)`の2つに分かれている環境がある）。**登録前に必ず`list-menu-info-pulldown`で実際の選択肢を取得し、そこに存在する値をそのまま指定すること。**

| search_condition_id | 動作 | group_label_key_ids / group_condition_id | group_period |
|---|---|---|---|
| `Unique`（ユニーク） | 条件に一致する一意のイベントのみ評価。複数一致したら全て未知イベント扱い | 指定禁止 | 指定禁止 |
| `Queuing`（キューイング） | 複数一致したイベントを古い順に評価（ルールに複数回マッチする可能性あり） | 指定禁止 | 指定禁止 |
| `Grouping`系（グルーピング） | 同一属性の連続イベントを同一グループとみなし、先頭イベントのみ使用 | 両方必須 | 期間延長ありの場合は**指定禁止**／期間延長なしの場合は指定可（省略時は先頭イベントのTTL） |

- `Unique`/`Queuing`を選んだ場合、同一の`filter_condition_json`を持つフィルター（グルーピング系を除く）が既に存在すると登録エラーになる。
- グルーピング系を選んだ場合、同一の`group_label_key_ids`+`group_condition_id`+`filter_condition_json`の組合せを持つフィルターが既に存在すると登録エラーになる。

## group_label_key_ids column

- REST入力値はラベル名の配列をJSON文字列化したもの。例: `["process", "host"]`

## ワイルドカード（`*`）の扱い

- `filter_condition_json`の`condition_value`に`"*"`（ワイルドカード、任意の値にマッチ）を使う場合のルール:
  - `search_condition_id`が`Unique`/`Queuing`のときは**ワイルドカード使用禁止**（グルーピング専用の機能）。
  - グルーピング系のときは使用可。但し`condition_type`が`"≠"`（等しくない）の条件に`"*"`を使うことはできない（`"=="`の条件でのみ使用可）。

## 新規作成時の最小サンプル（ユニーク検索、イベント種別で絞る）

```json
{
  "menu": "filter",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "available_flag": "True",
        "filter_name": "高負荷アラートフィルター",
        "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"高負荷アラート\"]]",
        "search_condition_id": "Unique"
      }
    }
  ]
}
```
