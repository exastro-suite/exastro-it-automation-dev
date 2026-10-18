# rule reference

OASEのルール。フィルター結果に基づき「どのアクションを実行するか」「どんな結論イベントを生成するか」を決める。**`filter`と`action`を先に作成しておく必要がある**。6メニューの中では最後に作成する。

## filter_a / filter_operator / filter_b columns（相互排他、重要）

- `filter_a`は必須。
- `filter_b`と`filter_operator`は**両方指定する、または両方未指定にする**。片方だけ指定するとエラーになる。
- `filter_a`と`filter_b`に同じフィルターを指定することはできない。
- `filter_operator`に指定できる値は次の3つのみ:
  - `A and B` : フィルターAとBの両方にマッチしたときだけ条件成立
  - `A xor B` : フィルターAとBのどちらか一方だけにマッチしたときに条件成立
  - `A -> B` : フィルターAにマッチした後にフィルターBにマッチしたときに条件成立（時系列相関）
- 単一フィルターだけで判定したい場合は、`filter_a`のみ指定し`filter_b`/`filter_operator`は空にする。

## action_id column

- 事前に`action`メニューで作成済みのアクション名を指定する。省略可（アクションを実行せず結論イベント生成のみ行うルールも作れる）。

## before_notification_destination / after_notification_destination columns

- 通知先（複数選択）を指定する場合、**対応する通知テンプレート（`before_notification`/`after_notification`、ファイルアップロード項目）と`action_id`を必ずセットで指定する**こと。通知先だけ指定してテンプレートやaction_idが無いとエラーになる。
- 通知テンプレートファイルには`[TITLE]`と`[BODY]`の両方のセクションが必要（Jinja2構文も使用可）。

## conclusion_label_settings column

- REST入力値は `[[label_key, label_value], ...]` という**2要素配列のリストをJSON文字列化**したもの。マッチ時に生成する結論イベントへ付与するラベルを定義する。
- **登録時に必須**なので、キーは必ず渡すこと。省略すると`{"conclusion_label_settings": ["Required fields."]}`（499-00201）で失敗する。
- **`label_value`を空にしてはいけない。** `[["_exastro_host", ""]]`は`{"conclusion_label_settings": ["Value is required."]}`（499-01707）で拒否される。画面ではその行が値空のデフォルトとして表示されるが、APIは受け付けない。
- 結論ラベルが不要な場合は、空リストを文字列として渡す。
  ```json
  "conclusion_label_settings": "[]"
  ```
- `label_key`は`label_creation`に登録済みのラベルキー（または`_exastro_host`等の予約キー）であること。有効なキーは`list-menu-info-pulldown`で確認できる。未知のキーは`MSG-00032`で失敗する。
- 例: 結論イベントに`severity=high`を付与したい場合
  ```json
  "conclusion_label_settings": "[[\"severity\", \"high\"]]"
  ```

## rule_label_name column

- 結論イベントの`_exastro_rule_name`ラベルに設定される名前。
- **登録後は変更できない**。更新時に別の値へ変えようとするとエラーになる。

## rule_priority column

- 整数、最小値1。複数のルールが同時にマッチした場合、値が大きい（高優先度）ルールが優先される。

## ttl column

- 単位は秒。最小値10、最大値2147483647。デフォルト3600。

## 新規作成時の最小サンプル

```json
{
  "menu": "rule",
  "records": [
    {
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
    }
  ]
}
```
