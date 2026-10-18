# action reference

OASEのアクション。ルールがマッチしたときに実行する対応処理を定義する。Conductorを通じてAnsible Playbook等を実行する。1つのアクションは複数のルールで再利用できる。

## 実行モードの早見表（相互排他、重要）

アクションには2つの実行モードがあり、**どちらか一方のみ**を指定する。両方の項目を混在させると登録エラーになる。

| モード | operation_id | event_collaboration | host_id | parameter_sheet_id |
|---|---|---|---|---|
| A: オペレーション実行モード | **指定する** | `False`（キーは必ず渡す） | 指定禁止 | 指定禁止 |
| B: Conductor直接実行モード | 指定しない | **キーは必ず渡す**: イベント連携なら`True`、`host_id`を使うなら`False` | `event_collaboration`が`False`のとき必須 | **必須** |

- `event_collaboration`は**どちらのモードでも登録時に必須**。キーを省略すると`{"event_collaboration": ["Required fields."]}`（499-00201）で失敗するため、イベント連携を使わない場合でも`"False"`を明示的に渡すこと。
- モードAは`operation_id`（Movement系オペレーション）と`event_collaboration: "False"`を指定する。`host_id`/`parameter_sheet_id`は指定しないこと。
- モードBは`operation_id`を指定しない代わりに、
  - `event_collaboration`を`True`にする（元イベントの`_exastro_host`ラベルの値を対象ホストとして使う）、**または**
  - `event_collaboration`を`False`にして`host_id`で対象ホストを明示する
  のどちらか一方を選び、かつ`parameter_sheet_id`（利用パラメータシート）を必ず指定する。
  `event_collaboration=True`と`host_id`指定を同時に行うことはできない。
- `conductor_class_id`（Conductorクラス）はどちらのモードでも必須。

## host_id column

- 値の書式は `[H]<ホスト名>` （`[H]`接頭辞+ホスト名）。例: `[H]web-server-01`
- プルダウン候補は`list-menu-info-pulldown`ツールで取得できる。

## parameter_sheet_id column

- 対象ホストに対して実行するパラメータシート（メニュー）を名称で指定する。

## 新規作成時の最小サンプル（Conductor直接実行モード、ホスト指定）

```json
{
  "menu": "action",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "action_name": "サービス再起動",
        "conductor_class_id": "Ansible実行",
        "event_collaboration": "False",
        "host_id": "[H]web-server-01",
        "parameter_sheet_id": "httpd再起動"
      }
    }
  ]
}
```
