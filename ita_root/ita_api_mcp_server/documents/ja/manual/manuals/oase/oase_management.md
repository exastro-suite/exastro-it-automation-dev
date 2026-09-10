# OASE管理
# はじめに
本書では、OASE管理の機能および操作方法について説明します。
# エージェント概要

## エージェントについて
エージェントは、Exastro IT Automation（以下、ITA）とは独立しており、ITA OASEと外部サービスの仲介役として機能します。
エージェントは、対象とする外部サービスのイベント収集設定をITAから取得し、その設定を用いて外部サービスからイベントを取得します。このプロセスを経て、取得したイベントをITAに送信します。
# エージェント利用手順
本章では、エージェント（Exastro OASE Agent）の利用手順について説明します。

## 作業フロー
-  **作業フロー詳細と参照先**
1. **イベント収集設定**
1. **ラベル設定**
1. **エージェントのインストール・起動**
# 通知テンプレート（共通）概要
OASEの通知機能のイベント種別と、その動作仕様の概要を以下に示します。
# 通知テンプレート（共通）利用手順
OASEの通知機能を利用するために必要な作業フローは以下のとおりです。
-  **作業フロー詳細と参照先**
1. **通知テンプレート（共通）のメンテナンス（閲覧/更新）**
1. **通知先設定の登録**
Exastro システムにオーガナイゼーション管理者でログインし、メニューより 通知管理 から登録します。
1. **（通知先がメールの方のみ）メール送信サーバの設定**
Exastro システムにオーガナイゼーション管理者でログインし、メニューより メール送信サーバ設定 から登録します。
# メニュー構成
本章では、OASE管理で利用するメニュー構成について説明します。

## メニュー/画面一覧
OASE管理のメニュー一覧を以下に記述します。
1      | OASE管理             | イベント収集             | イベント収集対象の情報を管理します。   |
2      |                      | 通知テンプレート（共通） | OASEの通知で使用する情報を管理します。 |
# 機能メニュー操作説明
本章では、OASE管理機能のメニュー操作説明について説明します。

## メニューについて
本節では、OASE管理をインストールした状態で表示されるメニューの操作について記載します。

## イベント収集
1. OASE管理 --> イベント収集 では、（エージェントに設定する）イベント収集対象の、接続方式・認証方式・TTL等をメンテナンス（閲覧/登録/更新/廃止）できます。
-*項目**                           | **説明**                                               | **入力必須** | **入力方法** | **制約事項**    |
イベント収集設定名                 | 任意のイベント収集設定名を入力します。                 | 〇           | 自動入力     | 最大長255バイト |
接続方式                           | イベント収集対象への接続方法を選択します。             | 〇           | リスト選択   | ※2              |
・Jinja2形式で予約変数を使用できます。                 |              |              |                 |
使用可能な予約変数の詳細は\                          |              |              |                 |
・Jinja2形式で予約変数を使用できます。                 |              |              |                 |
使用可能な予約変数の詳細は\                          |              |              |                 |
パラメータ                         | ・JSON形式で入力します。                               | ー           | 手動入力     | 最大長255バイト |
・Jinja2形式で予約変数を使用できます。                 |              |              |                 |
クエリパラメータ(接続先に追加される、"?"以降の値）\    |              |              |                 |
・使用可能な予約変数の詳細は\                          |              |              |                 |
※1 イベント収集対象への設定です。
- 接続方式
     - リクエストメソッド
     - 認証情報
- IMAP パスワード認証
     - ・IMAP: Plaintext
     - | ・ユーザー名
- Bearer認証
     - | ・GET
     - ・認証トークン
- パスワード認証
     - | ・GET
     - | ・ユーザー名
- 任意の認証
     - | ・GET
     - ・パラメータに記述

## 通知テンプレート（共通）
1. OASE管理 --> 通知テンプレート（共通） では、OASEの通知機能で使用するテンプレートをメンテナンス（閲覧/登録/更新/廃止）できます。
デフォルトの通知テンプレートは、利用する通知方法(  )に応じて内容を変更、または項目を追加してください。
メール以外の通知方法を利用する場合、通知のテンプレートのフォーマット調整が必須です。
- 項目
     - 説明
     - 入力必須
     - 入力方法
     - 制約事項
- イベント種別
     - | テンプレートを使用するイベント種別を選択します。
     - 〇
     - リスト選択
     - ー
- テンプレート
     - | 通知で使用するテンプレートを編集できます。
     - 〇
     - 手動入力
     - 最大サイズ2MB
- 通知先
     - | テンプレートを使用する通知先を選択します。
デフォルトのテンプレートには通知先を設定することはできません。
     - ー
     - リスト選択
     - ー
- デフォルト
     - イベント種別に対して、レコードにない通知先に送信する場合にはデフォルトのテンプレートが使用されます。
     - ー
     - ー
     - ー
- 備考
     - 自由記述欄です。
     - ー
     - 手動入力
     - 最大長4000バイト
テンプレートの初期設定値は下記のとおりです。
    Jinja2テンプレートを用いて通知設定を行う際は、以下の点にご注意ください。
    - 必須要素の定義: テンプレートには、通知のタイトルと本文を定義する **[TITLE]** および **[BODY]** 要素が **必須** です。
    - 構文不足による通知失敗: 必須要素（[TITLE]または[BODY]）が不足している場合や、要素の記述に誤りがある場合、通知の実行は **失敗します**。
    - 編集箇所: 出力内容を変更する場合は、 **[TITLE] および [BODY] の要素内部のみ** を編集してください。これらの要素自体を削除したり変更したりしないでください。
    - Jinja2構文の参照: テンプレート内で使用する変数や制御構文の詳細については、Jinja2の公式ドキュメントを参照してください。
# 付録

## OASE Agentの処理フローと.envの設定値
- OASE Agentの処理フロー
- OASE Agentのインストール時、.envに設定した、一部の設定値について
- パラメータ
   - 説明
- AGENT_NAME
   - 起動する OASEエージェントの名前および、内部データベースのファイル名として使用されます。
- EXASTRO_URL
   - ITAに対してAPIリクエストをする際に、リクエスト先として使用されます。
- EXASTRO_ORGANIZATION_ID
   - ITAに対してAPIリクエストをする際に、Organizationを識別するために使用されます。
- EXASTRO_WORKSPACE_ID
   - | ITAに対してAPIリクエストをする際に、ワークスペースを識別するために使用されます。
EXASTRO_ORGANIZATION_IDで設定したオーガナイゼーションと紐づいたワークスペースである必要があります。
- EXASTRO_REFRESH_TOKEN
   - | ITAに対してAPIリクエストをする際に、Bearer認証の認証トークンとして使用されます。
※ユーザーのロールが、OASE - イベント - イベント履歴メニューをメンテナンス可能である必要があります。
- EXASTRO_USERNAME
   - | ITAに対してAPIリクエストをする際に、Basic認証のユーザー名として使用されます。
※ユーザーのロールが、OASE - イベント - イベント履歴メニューをメンテナンス可能である必要があります。
- EXASTRO_PASSWORD
   - | ITAに対してAPIリクエストをする際に、Basic認証のパスワードとして使用されます。
- EVENT_COLLECTION_SETTINGS_NAMES
   - このパラメータで設定されている値から、イベント収集設定をITAから取得し、設定ファイルを生成します。
- ITERATION
- EXECUTE_INTERVAL

## イベント収集設定の即時反映について
本項では、イベント収集設定を変更した際に、OASE Agentに即時反映させる方法について説明します。
1. 設定ファイル「event_collection_settings.json」を削除します。
OASE Agentでは、設定ファイル「event_collection_settings.json」が存在しない場合、ITAからイベント収集設定を取得し、設定ファイルを作成します。
設定ファイルを削除することで最新の設定を反映させることができます。
※この操作を行わない場合、 で示した「ITERATION」の数だけループする処理が終了するまで、変更後の設定が反映されません。

## エージェントのデコード処理について

### 動作確認済み文字コード
-*送信方法**             | **メールのHeader**                                                        |
-*形式**  | **言語**     | **Content-Transfer-Encoding** | **Content-Type**                          |

## レスポンスキーとイベントIDキー

### レスポンスキー
・監視ソフトは、監視対象マシンで発出されたアラートやメトリックス（状態）をHTTP APIで取得できる機能があり、

### JMESPath
JMESPathの指定方法について、

### レスポンスリストフラグ

### イベントIDキー
- 項目名
   - 設定値
- レスポンスキー
   - :program:`value`
- レスポンスリストフラグ
   - :program:`True`
OASE管理 --> イベント収集 での設定値は、下記の設定が適切です。
- 項目名
   - 設定値
- レスポンスキー
   - :program:`value`
- レスポンスリストフラグ
   - :program:`True`
- イベントIDキー
   - :program:`id`
   .. list-table:: 正しくない、イベントIDキーの設定
- 項目名
        - 設定値
- レスポンスキー
        - :program:`value`
- レスポンスリストフラグ
        - :program:`True`
- イベントIDキー
        - :program:`value[].id`

## 監視ソフト毎のイベント収集設定例
本項では、代表的な監視ソフト :dfn:`Zabbix` と :dfn:`Grafana` をイベント収集で利用する場合の、 OASE管理 --> イベント収集 での設定例について説明します。
次に、cURLのパラメータを、 OASE管理 --> イベント収集 に設定する順番で説明します。
利用するバージョンのHTTP APIの仕様を確認し、 OASE管理 --> イベント収集 の設定を行ってください。

### Zabbix
:dfn:`Zabbix` から、イベントを取得する、 OASE管理 --> イベント収集 での設定例について説明します。
   --url http://<ZabbixのIP Address か Domain>/zabbix/api_jsonrpc.php \
   --header 'content-type: application/json-rpc' \
   --data "{\"jsonrpc\": \"2.0\",\"method\": \"problem.get\",\"id\": 1,\"params\": {},\"auth\": \"<Zabbix APIトークン>"}"
（コマンド・パラメータ中の <Zabbix APIトークン> の詳細は、後述します。）
1. :dfn:`Zabbix` からイベントを取得する、イベント収集の設定例
上記のcURLコマンドを参考に、同等な取得を行う、 OASE管理 --> イベント収集 の設定値は、下記の様に設定します。
.. list-table:: Zabbixの設定例
- 項目名
     - 設定値
- イベント収集名
     - <Zabbix障害取得と分かる名称>
- 接続方式
     - 任意の認証
- リクエストメソッド
     - POST
- 接続先
     - | http://<ZabbixのIP Address か Domain>/zabbix/api_jsonrpc.php
- リクエストヘッダー
- パラメータ
- レスポンスキー
     - result
- レスポンスリストフラグ
     - True
- イベントIDキー
     - eventid
パラメータ で設定している、<Zabbix APIトークン>は、Zabbixユーザーの認証情報で、
  1. | ブラウザで、:dfn:`Zabbix` に管理者でサイイン
初期状態の管理者のログイン情報は、
  2. | サイドメニュー  > ユーザー > ユーザー を選択
     --url http://<ZabbixのIP Address か Domain>/zabbix/api_jsonrpc.php \
     --header "Content-Type: application/json-rpc" \
     --data "{\"auth\":null,\"method\":\"user.login\",\"id\":1,\"params\":{\"user\":\"<ユーザー名>\",\"password\":\"<パスワード>\"},\"jsonrpc\":\"2.0\"}" \
<Zabbix APIトークン>を、  OASE管理 --> イベント収集 の パラメータ の <Zabbix APIトークン> の箇所に貼り付けます。
ブラウザでログイン後、サイドメニュー > ユーザー設定 > APIトークン の :guilabel:`APIトークンの作成` で作成できます。

### Grafana
:dfn:`Grafana` で、イベントを取得するための、 OASE管理 --> イベント収集 での設定例について説明します。
   --url 'http://<GrafanaのIP addres か Domain>:3000/api/prometheus/grafana/api/v1/alerts' \
   --header 'authorization: Bearer <認証トークン>' \
   --header 'Content-Type: application/json'
（コマンド・パラメータ中の <認証トークン> の詳細は、後述します。）
1. :dfn:`Grafana` からイベントを取得する、イベント収集の設定例
上記cURLコマンドを参考に、同等な取得を行う、 OASE管理 --> イベント収集 の設定値は、下記の様に設定します。
.. list-table:: Grafanaの設定例
- 項目名
     - 設定値
- イベント収集名
     - <Grafanaアラート取得と分かる名称>
- 接続方式
     - Bearer認証
- リクエストメソッド
     - GET
- 接続先
     - | http://<GrafanaのIP addres か Domain>:3000/api/prometheus/grafana/api/v1/rules
- リクエストヘッダー
- 認証トークン
     - <認証トークン>
- レスポンスキー
     - data.alerts
- レスポンスリストフラグ
     - True
- イベントIDキー
     - activeAt
下記の手順で取得できます。
初期設定では、
  9. | クリップボードの認証トークンを、 OASE管理 --> イベント収集 の 認証トークン に貼り付けます。

## 利用可能な予約変数一覧
OASE管理 --> イベント収集 では、以下の項目で予約変数が使用可能です。
- :dfn:`接続先`
- :dfn:`リクエストヘッダー`
- :dfn:`パラメータ`

### 予約変数
- 変数名
     - 説明
     - 出力例
- EXASTRO_LAST_FETCHED_TIMESTAMP
     - 前回取得時日時（UNIXタイムスタンプ）
     - 1704817434
- EXASTRO_LAST_FETCHED_DD_MM_YY
     - 前回取得時日時（DD/MM/YY HH:MM:SS形式）
     - 10/01/24 01:23:45
- EXASTRO_LAST_FETCHED_YY_MM_DD
     - 前回取得時日時（YYYY/MM/DD HH:MM:SS形式）
     - 2024/01/10 01:23:45
- EXASTRO_LAST_FETCHED_EVENT_IS_EXIST
     - 前回取得イベントの存在フラグ
     - True、False
- EXASTRO_LAST_FETCHED_EVENT
     - 前回取得イベントのrawデータのオブジェクト
     - | (例: Zabbixの場合)
使用方法については  を参照
- EXASTRO_EVENT_COLLECTION_SETTING
     - イベント収集設定の項目のオブジェクト
     -  を参照
- EXASTRO_LAST_FETCHED_TIME
     - | 前回取得時日時（YYYY-MM-DD HH:MM:SS形式）
     - 2025-09-19 10:45:34
- EXASTRO_CURRENT_TIME
     - | 現在時刻（YYYY-MM-DD HH:MM:SS形式）
     - 2025-09-19 10:45:34
-*〇使用例**
このデータから clock 項目を取得し、Zabbix APIの event.get メソッドのパラメータとして設定する例を以下に示します。
 に登録された情報を予約変数として参照することができます。
以下は、使用可能な項目と対応する変数名の一覧です。
- 項目名
     - 変数名.属性
- イベント収集設定名
     - EXASTRO_EVENT_COLLECTION_SETTING.EVENT_COLLECTION_SETTINGS_NAME
- 接続先
     - EXASTRO_EVENT_COLLECTION_SETTING.URL
- ポート
     - EXASTRO_EVENT_COLLECTION_SETTING.PORT
- リクエストヘッダー
     - EXASTRO_EVENT_COLLECTION_SETTING.REQUEST_HEADER
- プロキシ
     - EXASTRO_EVENT_COLLECTION_SETTING.PROXY
- 認証トークン
     - EXASTRO_EVENT_COLLECTION_SETTING.AUTH_TOKEN
- ユーザー名
     - EXASTRO_EVENT_COLLECTION_SETTING.USERNAME
- パスワード
     - EXASTRO_EVENT_COLLECTION_SETTING.PASSWORD
- メールボックス名
     - EXASTRO_EVENT_COLLECTION_SETTING.MAILBOXNAME
- パラメータ
     - EXASTRO_EVENT_COLLECTION_SETTING.PARAMETER
- レスポンスキー
     - EXASTRO_EVENT_COLLECTION_SETTING.RESPONSE_KEY
- レスポンスリストフラグ
     - EXASTRO_EVENT_COLLECTION_SETTING.RESPONSE_LIST_FLAG
- イベントIDキー
     - EXASTRO_EVENT_COLLECTION_SETTING.EVENT_ID_KEY
- TTL
     - EXASTRO_EVENT_COLLECTION_SETTING.TTL

### 設定例
各設定箇所での予約変数の使用例を示します。
接続先URLに認証トークンを埋め込み、URLパラメータとして渡す。
パラメータでの使用例
1. **イベント収集時に、現在日時や前回取得日時をフィルター条件として指定**
1. **Zabbix連携での使用**
   - 前回取得イベントが存在する場合　：前回取得イベントIDの次のイベントから取得
   - 前回取得イベントが存在しない場合：前回取得時刻以降のイベントを取得

## 通知テンプレート（共通）の設定例

### 設定項目（ServiceNow（レコード登録）の場合）
通知テンプレート（共通）で、ServiceNow (レコード登録) を通知方法として選択した場合の、TITLE、BODY について説明します。
ServiceNow (レコード登録) を通知方法として選択した場合、TITLE に記載した内容は使用されません。
ServiceNow (レコード登録) を通知方法として選択した場合、BODY にはServiceNow の REST API でレコード登録を行う際のリクエストボディの形式で記載する必要があります。
- テンプレート例はあくまで一例です。実際の運用に合わせて、適宜カスタマイズしてください。
- | 使用するパラメータについては、ServiceNow の 利用するアプリケーションに応じて、 マニュアルや、REST API リファレンスを参照してください。
  - `ServiceNowテーブルAPIマニュアル <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html>`_ 参照してください
  - REST APIエクスプローラー
    - `https://<instance-name>.service-now.com/$restapi.do`
    -  REST APIエクスプローラーの利用については、`ServiceNowのマニュアル <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/task/t_GetStartedAccessExplorer.html>`_ を参照してください

### ServiceNow(レコード登録)の設定例
ServiceNow(レコード登録)を行う通知テンプレート（共通）の設定例を以下に示します。
ServiceNowのインシデントテーブルにレコード登録を行う設定例
ここでは、デフォルトのテンプレートの内容から、TITLE の内容をServiceNowの short_description に、BODY に、イベントRAWデータ, エージェント の内容をServiceNowの description に設定する例を示します。
イベントRAWデータ(raw_event_data), エージェント(exastro_agents) の内容は、Jinjaテンプレートのループ処理を使用して、動的に設定しています。
- | 1.新規イベント（受信時）のテンプレート例: New(received).j2
- | 1.新規イベント（受信時）の通知例
- | 2.新規イベント（統合時）のテンプレート例: New(consolidated).j2
- | 2.新規イベント（統合時）の通知例
ServiceNow (レコード登録) を通知方法として選択した場合、TITLE に記載した内容は使用されません。
ServiceNow (レコード登録) を通知方法として選択した場合、BODY に記載した内容をリクエストボディとして使用します。
そのため、BODY には、ServiceNow の REST API でレコード登録を行う際のリクエストボディの形式で記載する必要があります。
   - テンプレート例はあくまで一例です。実際の運用に合わせて、適宜カスタマイズしてください。
   - 使用するパラメータについては、ServiceNow の 利用するアプリケーションに応じて、 マニュアルや、REST API リファレンスを参照してください。
     - `ServiceNowテーブルAPIマニュアル <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html>`_ 参照してください
     - REST APIエクスプローラー
       - `https://<instance-name>.service-now.com/$restapi.do`
       -  REST APIエクスプローラーの利用については、`ServiceNowのマニュアル <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/task/t_GetStartedAccessExplorer.html>`_ を参照してください
