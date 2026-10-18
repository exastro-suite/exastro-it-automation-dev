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

## しきい値（大小比較）の条件を作りたいとき（重要）

「CPU使用率が80%を**超えたとき**だけ対象にしたい」「レスポンスタイムが1000ms**以上**のときだけ」のように、**数値のしきい値でイベントを絞り込みたい場合、filterには大小比較が無いため、比較は`labeling`側で行い、filterはその結果のラベルを`==`で見る**という2段構えにする。これがExastroでの唯一の実現方法である。

```
labeling（ここで大小比較する）           filter（ここは == だけ）
  search_key_name:    event.cpu_usage
  type_name:          float          ─┐
  comparison_method:  >               ├─ 80を超えたイベントにだけ
  search_value_name:  80              │   cpu_over_80 = "true" が付く
  label_key_name:     cpu_over_80    ─┘        │
  label_value_name:   true                     ▼
                                      [["cpu_over_80", "==", "true"], ...]
```

手順:

1. `label_creation`でしきい値判定用のラベルキーを作る（例: `cpu_over_80`）。
2. `labeling`で**パターンA（条件に合致したときだけ固定値を付与）** の設定を作る。`comparison_method`に`>`/`>=`/`<`/`<=`を指定し、`type_name`は数値なら`integer`か`float`、`label_value_name`には`true`のような固定値を入れる。`labeling`では`<`/`<=`/`>`/`>=`が使える（filterとは違う）。詳細は`labeling.md`を参照。
3. `filter`の`filter_condition_json`に`[["cpu_over_80", "==", "true"]]`を加える。しきい値を下回るイベントにはラベルが付かないため、この条件にマッチせず対象外になる。

注意点:

- **`labeling`のパターンC（値の抽出。全項目`null`）でしきい値判定はできない。** 値を`cpu_usage`ラベルに抽出しても、filterでは`cpu_usage > 80`と書けないため要件を満たせない。しきい値判定は必ずパターンAで行うこと。
- **「監視ツール側で80%以上のアラートだけ送るように設定する」はExastro側の設定ではない。** ユーザーがExastroでの条件設定を求めているときに、この回避策を第一候補として提示してはいけない（提示するとしても、Exastro側で完結する上記の方法を推奨案として併記すること）。
- しきい値は変わりうるので、`label_key_name`に`cpu_over_80`のようにしきい値を埋め込むか、`cpu_threshold_exceeded`のような値に依存しない名前にするかはユーザーに確認すること。
- **既存のフィルターにしきい値条件を追加する場合は、どのフィルターに追加するかを必ずユーザーに確認すること。** 既存ルールの発火条件が狭まるため、黙って全フィルターを更新してはいけない。
- 既存フィルターを`Update`する場合は、直前に`menu-filter`で取得した`last_update_date_time`を必ず渡すこと。省略すると`{"0": {"Individual check": ["last_update_date_time is invalid (None)"]}}`（499-00201）になる。また`Update`は渡した値だけで検証されるため、`filter_name`/`search_condition_id`/`available_flag`など**変更しない列も全て再送**すること。

## 固定ラベル（組み込みラベル）— `_exastro_host` によるホスト絞り込み（重要）

`label_creation`で作成したラベル以外に、Exastroに最初から組み込まれている固定ラベルを`label_name`に指定できる。実際に使える一覧は`list-menu-info-pulldown`の`filter_condition_json.label_name`で取得できる。

| 固定ラベル | 内容 | 値の入り方 |
|---|---|---|
| `_exastro_host` | **イベントの対象ホスト名**。ホストごとにイベントを出し分けるにはこれを使う | **自動では入らない。`labeling`で付与する必要がある**（下記） |
| `_exastro_type` | イベント種別。`conclusion`は結論イベント（通常は`≠ conclusion`で除外する） | 自動 |
| `_exastro_event_collection_settings_id` | イベントを取得した収集設定のID | 自動 |
| `_exastro_fetched_time` / `_exastro_end_time` | イベントの取得時刻 / 終了時刻 | 自動 |
| `_exastro_agent_name` / `_exastro_agent_version` | 取得元エージェントの名称 / バージョン | 自動 |

### `_exastro_host`の値は`labeling`で埋める（必須）

- 固定ラベルは**`label_creation`に登録する必要はない（登録もできない）**。`_exastro_`で始まる名前は`label_key_name`の正規表現（先頭は英数字）に違反するため、`label_creation`で作ろうとすると`The input value is an invalid value.`で失敗する。
- ただし`_exastro_host`だけは**値が自動で入らない**。収集したイベントに自動付与されるのは`_exastro_type`等だけで、`_exastro_host`は空のままである。
- そのため、**`_exastro_host`をフィルター条件に使う場合は、イベント内のホスト名フィールドを`_exastro_host`に写す`labeling`設定を必ず作る**こと。`label_key_name`に`_exastro_host`を指定すればよい（固定ラベルもラベルキーのプルダウンに含まれる）。
- **ホストごとに1件ずつ作る必要はない。** `search_key_name`だけ指定し、`type_name`/`comparison_method`/`search_value_name`/`label_value_name`を**すべて`null`で渡す**と、そのフィールドの値がそのままラベル値になる（値の転記のみを行うパターン）。1件でどのホストにも対応できるため、通常はこちらを使う。
  ```json
  {
    "menu": "labeling",
    "records": [{
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "対象ホストのラベル付与",
        "event_collection_settings_name": "Zabbix監視イベント収集",
        "search_key_name": "host.name",
        "type_name": null,
        "comparison_method": null,
        "search_value_name": null,
        "label_key_name": "_exastro_host",
        "label_value_name": null
      }
    }]
  }
  ```
  - **キー自体は省略できない。** 省略すると`Required keys ['type_name', 'comparison_method', 'search_value_name', 'label_value_name'] are missing.`（499-00201）になり、空文字`""`を渡すと`The input value is an invalid value.(input value:)`になる。必ず`null`を渡すこと。
  - `search_key_name`に指定するフィールド名（`host.name`等）は**実際のイベントJSONの構造に依存する**ため、推測した場合はその旨をユーザーに伝えて確認を取ること。
- `action`の`event_collaboration: True`（イベント発生元ホストで実行）も`_exastro_host`ラベルの値を使うため、**この`labeling`設定が無いと実行対象ホストが決まらない**。

- **重要** 「このホストで起きたイベントだけを対象にしたい」という要件は、**必ず`filter_condition_json`の`_exastro_host`条件で実現する**こと。`action`メニューの`host_id`は「Conductorをどのホストに対して実行するか」の指定であり、**どのイベントにマッチするかには一切影響しない**。
  ```json
  [["_exastro_type", "≠", "conclusion"], ["event_type", "==", "高負荷アラート"], ["_exastro_host", "==", "web-server-01"]]
  ```
- `_exastro_host`の`condition_value`には**ホスト名のみ**を書く。`action.host_id`で使う`[H]`接頭辞は付けない。
- ホスト条件の無いフィルターは**全ホストのイベントにマッチする**。ホストごとにルールを分ける構成では、新しく作る側だけでなく**既存フィルターにも`_exastro_host`条件を追加**しないと、既存ルールが全ホストのイベントを拾い続ける。

## search_condition_id column（検索方法）

`group_label_key_ids`/`group_condition_id`/`group_period`の必須・禁止が、選んだ検索方法によって変わる。

**選択肢の数はバージョンによって異なる**（`Grouping`が1つにまとまっている環境と、`Grouping (Period Extension)`/`Grouping (No Period Extension)`の2つに分かれている環境がある）。**登録前に必ず`list-menu-info-pulldown`で実際の選択肢を取得し、そこに存在する値をそのまま指定すること。**

| search_condition_id | 動作 | group_label_key_ids / group_condition_id | group_period |
|---|---|---|---|
| `Unique`（ユニーク） | 条件に一致する一意のイベントのみ評価。複数一致したら全て未知イベント扱い | 指定禁止 | 指定禁止 |
| `Queuing`（キューイング） | 複数一致したイベントを古い順に評価（ルールに複数回マッチする可能性あり） | 指定禁止 | 指定禁止 |
| `Grouping`系（グルーピング） | 同一属性の連続イベントを同一グループとみなし、先頭イベントのみ使用 | 両方必須 | 期間延長ありの場合は**指定禁止**／期間延長なしの場合は指定可（省略時は先頭イベントのTTL） |

- `Unique`/`Queuing`を選んだ場合、同一の`filter_condition_json`を持つフィルター（グルーピング系を除く）が既に存在すると登録エラーになる。
  - つまり**条件がまったく同じフィルターは2つ作れない**。既存フィルターを別ホスト向けに複製する際は、`_exastro_host`条件を足して条件を異なるものにすること（名前を変えるだけでは登録できない）。
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
