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
    - `host`: 対象ホストのUUID一覧
    - `parameter`: 対象パラメータ項目のUUID一覧
- 更新時は `uuid` と `last_update_date_time` に `get-parameter-collection-filter` で取得した値を指定する
