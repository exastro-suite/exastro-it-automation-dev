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
- **重要（よくある誤解）** `host_id`は「Conductorを**どのホストに対して実行するか**」の指定であり、**どのイベントにマッチするかには一切影響しない**。
  - したがって「ホストAのイベントならホストAに、ホストBのイベントならホストBに対処する」という出し分けは、`host_id`を変えたアクションを2つ作るだけでは実現できない。ホスト条件の無いフィルターは全ホストのイベントにマッチするため、どのホストのイベントでも**優先順位が上のルール1本だけ**が動き（1つのイベントは1つのルールにしか使われない。`rule.md`参照）、**イベントと関係ないホストに対処が走ったり、本来動くべきルールが動かなかったりする**。
  - イベント側のホスト絞り込みは`filter`メニューの`filter_condition_json`に固定ラベル`_exastro_host`の条件を書くことで行う（`filter.md`参照）。
- `event_collaboration`を`True`にすると、イベントの発生元ホスト（`_exastro_host`）がそのまま実行対象になる。ホストごとにアクションを複製する必要がなくなるため、**「イベントが起きたホストで対処する」要件ではこちらを優先して検討すること**（この場合`host_id`は指定しない）。

## アクションの一意制約（重要・複製時にハマる）

- このメニューには列の組合せに対する一意制約があり、同じ組合せのアクションは2つ作れない。違反すると次のエラーになる。
  ```
  The combination is incorrect. (Combination: {'operation_id': None, 'conductor_class_id': 'Sleep_Execution', 'event_collaboration': 'False'}, Target ID: [...])  (499-00201 / MSG-00006)
  ```
- **一意制約に含まれる列はバージョンによって異なる。** 新しいバージョンでは`host_name`（ホスト）と`parameter_sheet_name`（パラメータシート）も含まれるが、**古いバージョンでは`operation_id`+`conductor_class_id`+`event_collaboration`の3列しか見ていない**。
  - つまり古いバージョンでは、**同じConductorを使った「Conductor直接実行モード」のアクションを、ホストだけ変えて2つ作ることができない**。既存アクションとぶつかってエラーになる。
- **重要（事前チェック）** アクションを**新規登録する前に**必ず`menu-filter`（`menu: "action"`）で既存アクションを確認し、これから登録する`conductor_class_id`・`event_collaboration`・`operation_id`の組合せが既存と一致しないかを検査すること。一致する場合は**登録を試みずに**下表の回避策を選び、その理由とともにユーザーへ提示すること（エラーを出してから直すのではなく、先に回避する）。
- それでもこのエラーが出た場合は、同じペイロードで再試行せず、次のいずれかに切り替えること（エラーメッセージの`Target ID`が既存アクションのIDなので、`menu-filter`でそれを確認してから判断する）。

| 回避策 | 内容 | 備考 |
|---|---|---|
| 1. イベント連携で1本化 | 既存アクションを`event_collaboration: True`に更新し、アクションを増やさない | **第一候補**。イベント発生元ホストで実行されるためホストごとの複製が不要になる |
| 2. オペレーション実行モードにする | ホスト用のオペレーションを`operation_list`に新規作成し、`operation_id`を指定（`host_id`/`parameter_sheet_id`は指定しない） | `operation_id`が異なるので制約を満たす |
| 3. 別のConductorを使う | `conductor_class_id`を変える | 対処内容自体を分けたい場合のみ |

- 回避策を選ぶ際はユーザーに確認を取ること。特に1はイベントが発生したどのホストでも対処が走るようになるため、挙動の変化を明示すること。

## 既存アクションを`Update`するときの注意（重要）

- `maintenance-all`の`Update`では、**相互排他バリデーションは「今回渡した値」だけで判定される**。既存レコードに入っている値は補完されない。
- そのため`event_collaboration`を`True`に変更する／`host_id`を変更する場合は、**同じペイロードで`parameter_sheet_id`も必ず一緒に渡すこと**。省略すると次のエラーになる。
  ```
  If an Host/Event cooperation or Host/Host name is selected, necessary to set the usage Parameter Sheet Name.  (499-00201)
  ```
- 更新前に`menu-filter`で既存レコードを取得し、**変更しない項目（`conductor_class_id`/`parameter_sheet_id`等）も含めて渡す**のが安全。
- イベント連携モードへ切り替える`Update`の例（`host_id`は明示的に`null`にする）
  ```json
  {
    "menu": "action",
    "records": [{
      "type": "Update",
      "parameter": {
        "action_id": "<既存のaction_id>",
        "last_update_date_time": "<menu-filterで取得した値をそのまま>",
        "event_collaboration": "True",
        "host_id": null,
        "parameter_sheet_id": "<既存と同じパラメータシート名>"
      }
    }]
  }
  ```

## parameter_sheet_id column

- 対象ホストに対して実行するパラメータシート（メニュー）を名称で指定する。
- **選べるのは次の条件を全て満たすパラメータシートだけ**（`list-menu-info-pulldown`の`parameter_sheet_id`に出るものが全て）。
  - ホスト/オペレーションを持つパラメータシート（データシートは不可）
  - バンドル（縦型、vertical）ではない
  - **ホストグループ対応ではない**
- 例えば`file_copy`（ファイルコピー（ホストグループ対応））は**ホストグループ対応なので候補に出ない**。このようなパラメータシートを使うConductorは、モードB（Conductor直接実行）では登録できないため、**モードA（オペレーション実行）を使うこと**。
  - モードAでは、`operation_id`に指定したオペレーションに登録済みのパラメータ（対象ホスト・値）でConductorが実行される。既存のオペレーションを流用する場合は、そのオペレーションのパラメータ（対象ホスト等）が要件に合っているかを`menu-filter`で確認して提示すること。新規オペレーションを作る場合は、そのオペレーション用のパラメータシートのレコードも登録する必要がある。

## Conductorが使うパラメータシートの調べ方

- Conductorの中身（どのMovementを含むか）を`menu-filter`で読むことはできない。`conductor_class_edit`はメニューではなく、指定すると`[menu] is invalid.`（499-00001）になる。
- Conductorがどのパラメータシートを使うかは、Movementの代入値自動登録設定（例: `subst_value_auto_reg_setting_ansible_legacy`）を`menu-filter`し、関連するパラメータシート（メニュー）を確認すること。

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
