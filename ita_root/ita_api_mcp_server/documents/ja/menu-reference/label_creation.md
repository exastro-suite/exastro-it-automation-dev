# label_creation reference

OASEのユーザーラベル（キー）を定義するメニュー。イベントに付与する属性のキー名そのものを登録する（値はここでは決めない。値の付与は`labeling`メニューで行う）。

## label_key_name column

- 半角英数字と`_`（アンダースコア）、`-`（ハイフン）のみ使用可能。先頭は英数字でなければならない。
- 正規表現: `^[a-zA-Z0-9][a-zA-Z0-9_-]*$`
- 例: `process`, `cpu_usage`, `host-group` は可、`_process`や`プロセス`、スペースを含むものは不可。
- `_exastro_`で始まるラベルキーはExastro組み込みのシステムラベル（`_exastro_type`, `_exastro_host`等）用に予約されており、別のビュー（固定ラベル）から参照される。**固定ラベルはここで作る必要が無く、作ることもできない**（先頭がアンダースコアなので上記の正規表現に違反し、`The input value is an invalid value.`で失敗する）。
- **注意: `_exastro_host`だけは値が自動で入らない。** ホスト名でイベントを絞り込みたい場合は、`label_creation`ではなく**`labeling`でイベントのホスト名フィールドを`_exastro_host`に写す設定を作る**こと（書き方は`filter.md`参照）。

## color_code column

- `#RRGGBB`形式（`#`+16進6桁）の文字列のみ許容。
- 正規表現: `^#([0-9a-fA-F]{6})$`
- 例: `#FF0000`

## 新規作成時の最小サンプル

```json
{
  "menu": "label_creation",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "label_key_name": "cpu_usage",
        "color_code": "#FF0000"
      }
    }
  ]
}
```
