#### Register Preset

`register-parameter-collection-filter` を新規登録として呼び出す場合の入力例です。
`uuid` と `last_update_date_time` は新規登録のため空文字列を指定しています。
`mode` が `host`　の場合でも、対象オペレーションのUUIDは必ず設定してください。
対象オペレーションが判断できない場合は、ユーザーに確認するようにしてください。

```json
{
    "uuid": "",
    "filter_name": "test",
    "filter_json": "{\"tableDirection\":\"horizontal\",\"mode\":\"operation\",\"mainHost\":\"\",\"operation\":[\"23971849-4fc5-41e5-9ca2-fe3772d995a9\"],\"mainOperation\":\"23971849-4fc5-41e5-9ca2-fe3772d995a9\",\"host\":[\"1\",\"3979ff2d-7393-49e8-b464-807e5d3145fc\",\"8dfb9e60-c9f2-499d-9267-6cad945c1391\"],\"parameter\":[\"c4c72fe6-479a-41a3-bc1f-0b04336bb61f\"]}",
    "last_update_date_time": ""
}
```

- `filter_name`: 検索条件の表示名(ユニーク制約あり)
- `filter_json`: パラメータ集の検索条件を表すJSON文字列
    - `mode`: `"operation"` または `"host"` などの表示モード
    - `operation` / `mainOperation`: 対象オペレーションのUUID
    - `host`: 対象ホストのID一覧(ホストの `managed_system_item_number`)
    - `parameter`: 対象パラメータシートのID一覧(パラメータシートの `menu_id`)
        - パラメータ集はパラメータシート単位で選択します。シート内の項目(カラム)のIDではありません。
    - `operation` / `host` / `parameter` には、パラメータ集の画面で選択できる値だけを指定してください。画面に存在しないIDを指定しても、エラーにはならず、画面上では無視されます。
- 更新時は `uuid` と `last_update_date_time` に `get-parameter-collection-filter` で取得した値を指定する

#### 返却値

- `uuid`: 登録・更新したプリセットのUUID。新規登録では登録後に一覧から `filter_name` で特定します。特定できなかった場合は含まれません。
