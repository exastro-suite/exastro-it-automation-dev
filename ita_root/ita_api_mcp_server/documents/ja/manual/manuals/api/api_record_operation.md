# APIのアクセス（認証）について
利用する対象のAPIのエンドポイント、パラメータ、詳細については、各利用者向けの、「」、「」を参照してください。
   - 最終ログイン時の言語情報が参照されます。
   - 初回ログイン後の設定が行われていない為、認証エラーとなります。
# 登録、編集のAPI、関連APIの実行例
以下、登録、編集のAPI、及び関連APIの実行の例について記載します。
- -  
APIのエンドポイントで使用するメニュー名の確認方法ついて
   - 「管理コンソール --> メニュー管理」から該当するメニューのレコードを確認し、「メニュー名(rest) 」の値を使用してください。
パラメータで使用する、JSONデータ、FOEMデータに関する補足
パラメータ指定時の形式、指定方法について
コンテンツタイプ、パラメータ指定の方法や、curlの実行環境等により、適切なもので対応してください。
    - JSONデータをJSONファイルで保存し、パラメータにJSONファイルを指定して使用する
    - JSONデータのシングルクォーテーション「'」が使用できない場合、ダブルクォーテーション「 "」 を用いて、かつ内部で使用されたダブルクォーテーションをエスケープした書き方に変更する
    - 末尾の「\\」、「^」については、ご利用環境で適切なものに変更する
以下、コンテンツタイプによるパラメータの指定方法の詳細は、「」を参照してください。
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -H "Content-Type: application/json" \
       --data-raw [ { \"file\": { \"playbook_file\": \"LSBuYW1lOiBydW4gImVjaG8iCiAgY29tbWFuZDogZWNobyB7eyBWQVJfU1RSXzEgfX0=\" }, \"parameter\": { \"discard\": \"0\", \"item_no\": null, \"playbook_name\": \"echo\", \"playbook_file\": \"echo.yml\", \"remarks\": null, \"last_update_date_time\": null, \"last_updated_user\": null }, \"type\": \"Register\" } ]
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -H "Content-Type: application/json" \
       -d @playbook_files_sample.json
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -F "json_parameters=[{\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}] " \
       -F "0.playbook_file=@echo.yml"

## 一覧取得（Menu Filter：レコードの取得）
    BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
      -H "Authorization: Basic ${BASE64_BASIC}" \
      -H "Authorization: Basic ${BASE64_BASIC}" \
      -H "Content-Type: application/json" \
      --data-raw "{\"discard\":{\"LIST\":[\"0\"]}}"
条件指定で利用可能な検索方法を以下に記載します。
- **オプション**
       - **説明**
       - **設定例**
       - **制約事項**
- NORMAL
       - | あいまい検索を実施します。
       - {"対象のキー":{"NORMAL":"検索条件"}}
       -
- LIST
       - | 完全一致検索を実施します。
       - {"対象のキー":{"LIST":["検索条件"]}}
       -
- RANGE
       - | 範囲指定による検索を実施します。
       - {"対象のキー":{"RANGE":{"START":"検索条件","END":"検索条件"}}}
       -
機器一覧の条件指定した検索のパラメータ:
  - 廃止含まず
  - ホスト名に「host」を含む
  - 最終更新日時が「2023/01/01 00:00:00」～「2023/12/31 00:00:00」の間
   - | 論理削除状態のレコードのことを指します。
   - | 各レコードのdiscardの値で、レコードの論理削除状態を示します。
- "0"：有効なレコード
- "1"：廃止されたレコード
   - 廃止状態のレコードは、バリデーションの対象には含まれません。
   - ファイルのデータは、base64エンコードした文字列で出力されます。必要に応じて、base64デコードして使用してください。
   - パスワード等の一部の項目について、暗号化された形で保存されます。
   - 一覧取得のAPIで出力される値は、nullとなり登録された値は、出力されません。
※暗号化された形で、保存される項目については、各メニューのマニュアルを参照してください。

## 登録、編集（Menu MaintenanceAll レコードの一括操作）
登録、編集のAPIのパラメータの指定方式として、以下のContent-Typeで選択可能です。
- application/json 形式
  - パラメータをJSONデータで送信します。
  - ファイルデータは、パラメータ内に、base64文字列として記載し送信します。
- multipart/form-data 形式
  - パラメータ、ファイルをformデータとして送信します。
  - ファイルのformデータのキーは、パラメータのJSONデータのindexと、対象のキーを「.」で接続して使用します。
以下のサンプルはBasic認証を使用して、「Ansible共通 --> 機器一覧」、「Ansible-Legacy --> Playbook素材集」のレコード操作のAPIを呼出しています。
- 登録、編集時のバリデーションについて
   - 各項目のバリデーションについては、各メニューのマニュアルを参照してください。

### Content-Typeによるパラメータの構造の違いについて
以下は、各Content-Type毎の、パラメータの構成について説明します。
パラメータで使用する対象キーの取得、確認方法については、「」を参照してください。
- Content-Type: application/json
- Content-Type: multipart/form-data
以下、登録、更新時のパラメータ例について記載します。
- 「Ansible-Legacy --> Playbook素材集」の登録のサンプル
- 「Ansible-Legacy --> Playbook素材集」の更新のサンプル
   - last_update_date_timeには、FILTERで取得した最新の該当レコードの値を使用してください。
   - 最新の値と一致しない場合、レコードの更新は行われません。
   - | ファイルの登録、更新方法
parameter、file配下の指定のキーに、登録、更新する値を指定してください。
   - | ファイル名の変更方法
   - | ファイルの削除方法
   - | ファイルの登録、更新方法
parameter配下の指定のキーに、登録、更新する値を指定してください。
   - | ファイル名の変更方法
   - | ファイルの削除方法
   - parameter配下の変更する対象の項目の値のみ変更して、file配下、もしくは、-F でファイル指定せずに、対象項目のキーを含めずに更新してください。
   - プルダウン項目の対象、使用可能な値については、「 」で取得できる情報を参照してください。

### Ansible共通 - 機器一覧
   BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -H "Content-Type: application/json" \
     --data-raw "[{ \"file\": {\"ssh_private_key_file\": \"\", \"server_certificate\": \"\"}, \"parameter\": { \"authentication_method\": \"パスワード認証\", \"connection_options\": null, \"connection_type\": \"machine\", \"discard\": \"0\", \"host_dns_name\": null, \"host_name\": \"exastro-test\", \"hw_device_type\": null, \"instance_group_name\": null, \"inventory_file_additional_option\": null, \"ip_address\": \"127.0.0.1\", \"lang\": \"utf-8\", \"login_password\": \"password\", \"login_user\": \"root\", \"os_type\": null, \"passphrase\": null, \"port_no\": null, \"protocol\": \"ssh\", \"remarks\": null, \"server_certificate\": null, \"ssh_private_key_file\": null }} ]"
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -F 'json_parameters="[ { "parameter": { "discard": "0", "managed_system_item_number": null, "hw_device_type": null, "host_name": "exastro-test", "host_dns_name": null, "ip_address": "127.0.0.1", "login_user": "root", "login_password": "asdfghjkl", "ssh_private_key_file": "ssh_key_file.pem", "authentication_method": "パスワード認証","port_no": null, "server_certificate": "certificate_file.crt", "protocol": "ssh", "os_type": null, "lang": "utf-8", "connection_options": null, "inventory_file_additional_option": null, "instance_group_name": null,"connection_type": "machine", "remarks": null,"last_update_date_time": null, "last_updated_user": null}, "type": "Register" }]"' \
     -F '0.ssh_private_key_file=@/ssh_key_file.pem' \
     -F '0.server_certificate=@/certificate_file.crt' \

### Ansible-Legacy - Playbook素材集
   BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -H "Content-Type: application/json" \
     --data-raw "[{\"file\":{\"playbook_file\":\"LSBuYW1lOiBydW4gImVjaG8iCiAgY29tbWFuZDogZWNobyB7eyBWQVJfU1RSXzEgfX0=\"},\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}]"
    -H "Authorization: Basic ${BASE64_BASIC}" \
    -F "json_parameters=[{\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}] " \
    -F "0.playbook_file=@echo.yml"

## APIのパラメータ関連情報（Menu Info メニュー情報の取得）
レコードの一括操作パラメータの作成について
レコードの一括操作のパラメータ、項目の構成については、以下を参照してください。
- -  

### メニュー情報
 で使用する、メニューの構成情報、カラムグループ、カラムに関する設定値を取得できます。
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/
     MENU="対象メニュー"
     BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
                     "column_name_rest": "", # APIのパラメータで指定する項目名
レコードの一括操作のパラメータに関するメニューの項目情報と設定値について
メニューの情報取得APIの、項目情報(column_info)のキーと設定値について
    .. list-table:: メニューの項目情報のキーと設定値
- **キー**
         - **説明**
         - **設定値**
- column_name
         - 文字列
- column_name_rest
         - APIのパラメータで指定する項目名
         - 文字列
- auto_input
         - | 自動入力フラグ
         - | "0":非対象
- input_item
         - | 入力対象フラグ
登録、編集のAPI実行時の入力対象項目
         - | "0": 非対象
- view_item
         - | 出力対象フラグ
         - | "0": 非対象
- required_item
         - | 必須入力フラグ
登録、編集のAPI実行時の必須対象項目
         - | "0": 非対象
- unique_item
         - | 一意制約フラグ
登録、編集のAPI実行時の一意制約対象項目
         - | "0": 非対象
※バリデーションについては、各メニューのマニュアルを参照してください。

### パラメータの項目情報
 で使用するパラメータの情報、を取得できます。
より詳細な設定を確認したい場合は、 も併せて参照してください。
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/column/
     MENU="対象メニュー"
     BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
  - | 例: 「Playbook素材集」のレスポンス
             "playbook_file": "Playbook素材",
             "playbook_name": "Playbook素材名",

### プルダウン項目で使用可能なリスト
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/pulldown/
     MENU="対象メニュー"
     BASE64_BASIC=$(echo -n "ユーザー名を設定してください:パスワードを設定してください" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
  - | 例: 「機器一覧」のレスポンス
# パラメータ適用（API）
本APIは、オペレーションの生成からパラメータの適用までを行いConductor作業実行を行うAPIです。
尚、Conductor作業実行の完了確認は行いません。完了確認は、 Conductor  -->  Conductor作業履歴 より行って下さい。

## request形式
- 項目
     - 説明
- APIカテゴリ
     - Apply
- API名
     - パラメータ適用
- URL
     - /api/{organizaiton_id}/workspaces/{workspace_id}/ita/apply/
- method
     - POST
- headers
     - | content-type: application/json
- Request body
     - | Request bodyを参照して下さい。

## Request body
conductor_class_name                   | Conductor名            | ○    | 文字列           | | 作業実行を要求するConductor名を指定します。                                                                                 |
|                  | | Conductor名は、Conductor  -->  Conductor一覧 に登録されている Conductor名称 を指定します。|
|                  | | Conductor  -->  Conductor一覧 に登録されていないConductor名を指定した場合はエラーになります。              |
operation_name                         | オペレーション名       |      | 文字列           | | 作業実行を行うオペレーション名を指定します。                                                                                |
|                  | + | 既存オペレーション                                                                                                        |
|                  |   | 基本コンソール  -->  オペレーション一覧 に登録されている オペレーション名 を指定します。|
|                  | + | 新規オペレーション                                                                                                        |
|                  |   | 基本コンソール  -->  オペレーション一覧 に登録されていない オペレーション名 \           |
|                  |   | 指定されたoperation_nameが 基本コンソール  -->  オペレーション一覧 に登録されます。                      |
|                  | + | オペレーション自動採番                                                                                                    |
|                  |   | operation_nameの指定がない場合や省略した場合は、以下の採番ルールで オペレーション名 を採番し\            |
|                  |     基本コンソール  -->  オペレーション一覧 に登録されます。                                                 |
schedule_date                          | 予約日時               |      | 文字列           | | Conductor作業実行の予約日時を yyyy/mm/dd hh:mi:ss で指定します。                                                            |
parameter_info                         | パラメータ情報         |      | 配列             | | 登録/更新/廃止/復活の操作を行うパラメータ情報を指定します。                                                                 |
|                  | | 複数メニューが対象で順序性を考慮する必要がある場合は、配列の順番で調整して下さい。                                          |
|                  | | Conductor作業実行のみを行う場合は省略して下さい。                                                                           |
※1             | (menu_name_rest)      | メニュー名(REST)       |      | 配列             | | 管理コンソール  -->  メニュー管理 の メニュー名(Rest) を指定します。                      |
|                        |      |                  | | 登録の場合： Register                                                                                                       |
parameter    | パラメータ             |      | 辞書             | | 対象メニューのカラムキーと値の組み合わせを指定します。                                                                      |
|                        |      |                  | | operation_nameで「新規オペレーション」や「オペレーション自動採番」を指定した場合、オペレーション名に相当する\               |
|                        |      |                  | | また、conductor_class_nameで、Conductor call function（以降、サブConductorと称す。）が含まれるConductor名を指定した場合\    |
|                        |      |                  |   で、サブConductorの個別オペレーションを明示的に指定する必要がある場合、該当のオペレーション名を指定します。                 |

## Request bodyの具体例

### 既存オペレーションで登録済みパラメータを使用したConductorの作業実行

### 既存オペレーションで登録済みパラメータを使用したConductorの予約実行

### 既存オペレーションでパラメータ適用をしたConductorの作業実行
オペレーション「operation_name_select」の指定について
既存オベーションの場合、オペレーション「operation_name_select」に設定する値は、該当オペレーションの「実施予定日」(YYYY/MM/DD hh:mm)_「オペレーション名」で指定します。

### 新規オペレーションでパラメータ適用をしたConductorの作業実行
オペレーション「operation_name_select」の指定について
新規オペレーションの場合、オペレーション「operation_name_select」の指定は不要です。

### オペレーション自動採番でパラメータ適用をしたConductorの予約実行
オペレーション「operation_name_select」の指定について
オペレーション自動採番の場合、オペレーション「operation_name_select」の指定は不要です。

### 複数メニューに対して複数レコードのパラメータ適用をしたConductor作業実行

### サブConductorの個別オペレーションを明示的に指定してパラメータ適用でConductor作業実行

## response body
     Request bodyで指定しているメニュー名(REST):sample_menu_001 の 1レコード目(0オリジン) の キー:column_1 に指定した値の文字数の不備でエラーが発生した場合の例
             "1": {                                                                                    メニュー名(REST)のレコード番号が0オリジンで表示されます。
                "column_1": [ "文字長エラー (閾値 : 値<=8byte, 値 : 30byte), menu : sample_menu_001"]  キー：エラーとなった項目のREST名、値：エラー内容、menu : エラーとなったメニュー名（REST)

## 留意事項
本APIは、ITAで更新可能なメニューに対してパラメータ適用を行う事が出来ます。

### ホストグループへのパラメータ適用
「ホストグループ管理」にパラメータ適用をした場合、指定されたホストグループに属するホスト解析が処理されない状態でconductor作業実行が行われます。
「ホストグループ管理」へのパラメータ適用は、以下のレコード操作を行うAPIで事前に登録を行ってください。

### 変数抜出対象のメニューへのパラメータ適用
変数抜出対象のメニューにパラメータ適用は、指定されたパラメータ内で使用している変数の刈取りが処理されない状態でconductor作業実行が行われます。
変数抜出対象のメニューへのパラメータ適用は、以下のレコード操作を行うAPIで事前に登録を行ってください。
変数抜出対象のメニューについては、「 -> 」\

### エラー時のロールバック
