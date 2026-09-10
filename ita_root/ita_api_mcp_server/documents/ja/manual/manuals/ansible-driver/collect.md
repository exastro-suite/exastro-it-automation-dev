# 収集機能
# はじめに
本書では、ITAの収集機能および操作方法について説明します。
# 収集機能概要
本章では収集機能について説明します。

## 収集機能について
収集機能とは、ITAで実施した、作業実行結果（規定のフォーマットで出力されたソースファイル）を元に、パラメータシートへ値を自動で登録する機能です。
本機能は、Ansible-Driverを対象としています。
パラメータシートの詳細については、「」を参照してください。

#### 収集機能概要図

#### 収集機能データ登録処理概要図
ファイル格納先、収集項目値管理の設定値に従い、パラメータシートへの登録、更新を行います。
※収集機能のデータ型の取り扱い例については、「  」をご参照ください。

## パラメータシートへの登録方法について
収集機能は、登録された設定値から対象のファイルの値をパラメータシートに登録、更新します。

#### 収集機能の動作要件
ITAで以下の設定がされている必要があります。
- | パラメータシート定義・作成 にて、パラメータシート（ホスト/オペレーションあり）が作成されている
- | 収集項目値管理 にて、作業実行結果（ソースファイル）とパラメータシートの項目と紐づけ設定がされている
- | 収集対象機器（ホスト名）が、機器一覧に登録済み
作業実行後に、以下の状態である場合、パラメータシートへの登録を実施します。
- | 作業実行の結果、正常に完了している
- | 作業実行の出力結果として、規定の構造でディレクトリ、ファイルが配置されている
パラメータシートへの登録元となるソースファイルを生成するIaC（Playbook、Role）については、各ユーザー様で準備する必要があります。
参考： Ansible Playbook Collection（OS設定収集）
# 収集機能でのディレクトリ、ファイル構造、変数取り扱い
本章では収集機能で扱うディレクトリ、ファイル構造、変数について説明します。

## 収集対象ディレクトリ、ファイル構造
         - key: PermitRootLogin
         - key: PasswordAuthentication
収集対象ディレクトリについて、収集対象ディレクトリパス（ソースファイルの出力先として）をIaC(Playbook,Role)内にて、で以下の変数として扱えます。
.. list-table:: 収集機能対象ディレクトリITA独自変数
- ITA独自変数
     - 変数指定内容
     - 備考
- __parameter_dir__
     -  作業結果ディレクトリ配下の「_parameters」のパスへ変換されます。
     -
- __parameters_file_dir__
     -  作業結果ディレクトリ配下の「_parameters_file」のパスへ変換されます。
     -
- __parameters_dir_for_epc__
     -  作業ディレクトリ配下の「_parameters」のパスへ変換されます。
     -
- __parameters_file_dir_for_epc__
     -  作業ディレクトリ配下の「_parameters_file」のパスへ変換されます。
     -
-  _parameters           ※1
-  _parameters_file      ※4
-  test.txt      ※5
- | 備考
※2 ホスト名（機器一覧に登録されているものが収集対象）
ソースファイルを生成するPlaybookを作成する際の出力先について、「」を使用しない場合、以下の構造を認識してPlaybookを記述する必要があります。
- モード
     - モード別識別子
     - 階層構造
     - 備考
- Ansible-Legacy
     - legacy
     - /<上位ディレクトリ(Ansible）>/legacy/
     -
- Ansible-Pioneer
     - pioneer
     - /<上位ディレクトリ(Ansible）>/pioneer/
     -
- Ansible-LegacyRole
     - legacy_role
     - /<上位ディレクトリ(Ansible）>/legacy_role/
     -
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters/localhost/SAMPLE.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters/localhost/OS/RH_snmpd.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters_file/localhost/TEST.txt
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters/localhost/SAMPLE.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters/localhost/OS/RH_snmpd.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters_file/localhost/TEST.txt
ファイルアップロード項目のパラメータシートを収集対象とする場合、ソースファイルの変数の値（ファイル名/ファイルパス）と該当するファイルが、_parameters_file配下に配置されている必要があります。
収集項目値管理の設定は、「収集項目値管理」参照してください。
\_parameters_file配下に配置されているアップロード対象ファイルの指定方法として、以下の記載方法があります。
.. list-table:: アップロード対象ファイルの指定方法
- 指定方式
     - YAMLファイルへの記載方法
     - 備考
- ファイル名指定
     - VAR_FILE_NAME : <‘ファイル名> ’
     -
- ファイルパス指定 (後方一致)
     - VAR_FILE_NAME : ‘/<階層X>/<ファイル名>’
     -
     - VAR_FILE_NAME : ‘/<上位ディレクトリ>/_parameters_file/localhost/<階層X>/<ファイル名>’
     -
■　e.g.) 通常変数の構造の変数の場合のディレクトリ構造とソースファイルの内容
-  _parameters
-  _parameters_file
-  config               ※アップロード対象ファイル

## 取り扱う変数と種類
収集機能で扱うソースファイル内で扱える変数は以下の3種類があります。
- | 通常変数
変数名に対して具体値を1つ定義できる変数です。
- | 複数具体値変数
変数名に対して具体値を複数定義できる変数です。
      - root
      - mysql
- | 多段変数
階層化された変数です。
       - user-name: alice      #メンバ変数
変数名は、下記の7文字を除くascii文字\(0x20～0x7e)が使用出来ます。
尚、クォーテーションで囲まないと変数名の先頭に使用出来ない文字がいくつかあります。
# 収集機能 メニュー構成
本章では、収集機能のメニュー構成について説明します。

## メニュー/画面一覧
1. Ansible共通 のメニュー
Ansible共通 のメニュー一覧を以下に記述します。
- No
     - メニューグループ
     - 説明
- 1
     - Ansible共通
     - 収集項目値管理
     - | 作業実行の出力結果（ソースファイル）と、パラメータシートの項目の紐づけ設定を行い、
収集機能で登録する対象パラメータを管理します。
1. Ansible driver メニュー
Ansible driverの各メニューグループに対応するメニュー一覧を以下に記述します。
- No
     - メニューグループ
     - 説明
- 1
     - Ansible-Legacy
     - 作業管理
     - 作業実行履歴を管理します。収集機能によるパラメータシートの登録状況、実行ログを参照します。
- 2
     - Ansible-LegacyRole
     - 作業管理
     - 作業実行履歴を管理します。収集機能によるパラメータシートの登録状況、実行ログを参照します。
- 3
     - Ansible-Pioneer
     - 作業管理
     - 作業実行履歴を管理します。収集機能によるパラメータシートの登録状況、実行ログを参照します。
# 収集機能の利用手順
収集機能の利用手順について説明します

## 作業フロー
収集機能の実施における標準的なフローは以下のとおりです。
ITA Ansible-Driverの利用方法は、「」を参照してください。
ITA 基本コンソールの利用方法は、「」を参照してください。

#### 収集機能作業フロー
以下は、Ansibleで作業を実行し、パラメータシートへ収集するまでの流れです。
-  作業フロー詳細と参照先
1. パラメータシート（ホスト/オペレーションあり）の作成
1. 収集項目値管理 の登録
1. 作業準備
1. 作業実行
実行日時、投入オペレーション、Movement、ワークフローを選択し処理の実行を指示します。
1. 収集機能実行
作業実行が完了した作業Noを収集機能の対象として、パラメータシートへの登録処理を実施します。
1. 収集状況確認
# 収集機能・操作方法説明
本章では、収集機能で利用するメニューの機能について説明します。
登録方法の詳細は、関連マニュアルの「」をご参照下さい。

## Ansible 共通

#### 収集項目値管理
1. 収集項目値管理 では、収集項目とパラメータシートの項目の紐付設定を行います。
1. 一覧 --> 登録 or 編集 より、収集項目の登録を行います。
- 項目：収集項目(From)
     - 説明
     - 入力必須
     - 制約事項
- パース形式
     - YAML:YAML形式のファイルを解析し、パラメータを生成します。
     - 〇
     - ※1
- PREFIX（ファイル名）
     - ファイル名の拡張子を除いて入力して下さい。
     - 〇
     - ※1
- 変数名
     - | 収集対象の変数名を入力して下さい。
配列、ハッシュ構造の場合、メンバ変数の入力が必須となります。
     - 〇
     - ※1
- メンバ変数
     - 変数が複数具体値、多段変数の場合入力して下さい。
     -
     - ※1
- 項目：パラメータシート(To)
     - 説明
     - 入力必須
     - 制約事項
- メニューグループ:メニュー:項目
     - | 項目を選択して下さい。
メニューグループ名、メニュー名、項目名を「:」区切りで接続した形で表示されます。
     -
     - ※2
※1 ファイル名、変数、メンバ変数入力値の例
※2 同一の「パラメータシート(To) - メニューグループ：メニュー：項目 」に対して、複数の「PREFIX(ファイル名) - 変数名 」を設定している場合、ファイル順に処理が実行されます。詳しくは「」参照。
■e.g.) 通常変数の構造の変数の場合
   ■収集値項目管理の収集項目(FROM)の入力可能な値
   変数名： VAR_sample_config_1
■ e.g.) 複数具体値の構造の変数の場合1
     - SAMPLE1
     - SAMPLE2
     - SAMPLE3
   ■収集値項目管理の収集項目(FROM)の入力可能な値
   変数名： VAR_sample2_conf
   メンバ変数：  [0]
■ e.g.) 複数具体値の構造の変数の場合2
     - key: PermitRootLogin
     - key: PasswordAuthentication
    ■収集値項目管理の収集項目(FROM)の入力可能な値
    変数名： VAR_RH_sshd_config:
    メンバ変数：  [0].key
■e.g.)複数具体値の構造の変数の場合3
       - sec_name: "testsec"
       - sec_name: "local"
   ■収集値項目管理の収集項目(FROM)の入力可能な値
   変数名： VAR_RH_snmp_config:
   メンバ変数：  com2sec[0].sec_name

## Ansible-Legacy、Ansible-Pioneer、Ansible-LegacyRole

#### 収集状況の確認
- 項目
     - 説明
     - 備考
- ステータス
     - | 収集機能の実行状況の表示
対象外：収集機能対象外　（対象ファイルなし）
収集済み：収集機能実施済み
収集済み（通知あり）：登録/更新中に不備があった場合
収集エラー：Movementのオペレーション、ホストに不備がある場合
     - ※
- 収集ログ
     - 収集機能実行のログをダウンロード
     -
- | 作業状態
     - 収集機能対象
     - 対象ファイル
     - | 収集状況
     - 収集ログ
     - 備考
- 完了以外
     - なし
     - 対象外
     - 空
     - 空
     -
- 完了以外
     - あり
     - 対象外
     - 空
     - 空
     -
- 完了
     - なし
     - 対象
     - 対象外
     - ログファイルあり
     -
- 完了
     - あり
     - 対象
     - 収集済み
     - ログファイルあり
     -
- 完了
     - あり
     - 対象
     - 収集済み(通知あり）
     - ログファイルあり
     -
- 完了
     - あり
     - 対象
     - 収集エラー
     - ログファイルあり
     -
作業状態が完了でない場合、収集機能対象外の為、収集状況 は更新されないため、空のままとなります。
設定項目値管理 の不備により、登録処理が失敗した場合でも収集済み（通知あり）となります。詳細は、以下ログファイル出力内容例を参照してください。
-*ログファイル出力内容例**

## BackYardコンテンツ
#.  パラメータシートへの登録処理の概要
1. 正常に完了した作業の一覧を取得します。
1. 収集対象作業Noから以下の情報を取得します。
- オペレーション情報
- 対象ホスト
- 対象ソースファイル
1. 対象のホストが機器一覧に登録されているか確認します。
登録： 収集対象
未登録： 対象外
1. 対象ソースファイルと収集項目値管理から対象パラメータシートのメニューIDを取得
1. 1～4 の情報から登録、更新用のパラメータを生成します。
対象のメニューに対して、データ確認を実施し、登録、更新かを判定します。
登録：　オペレーション、ホスト組み合わせで、一意のデータが登録されていない
更新：　オペレーション、ホスト組み合わせで、一意のデータが登録されている
1. パラメータシートへのデータの登録/更新を実施します。
1. 作業Noに収集状況のステータスを更新します。
なお、パラメータシートへのデータ登録のタイミングはBackyardの実行プロセスの周期に依存します。
# 付録

## 参考資材
以下、IaC(Playbook、Role)の参考例となります。
1. Exastro Playbook Collection
1. Ansibleコンフィグ取得、パラメータ生成Playbook
       - name: make yaml file
      - name: get vconsole config
      - name: get yum config
「Ansible-Legacy」-「Movement一覧」編集時、「ヘッダーセクション」に以下を記載してください。
設定変更については、「」を参照してください。
   - hosts: all

## 収集実行例

#### 複数ファイルの同一メニューを対象とした場合
収集項目値管理にて、一つの「メニュー-項目」に対して、複数の「PREFIX(ファイル名)-変数名」の設定をしている場合、対象ホストの収集対象ディレクトリ内に、該当する複数のソースファイルがある場合の収集処理の例について記載します。
-  _parameters
-  ita-sample01
-  SAMPLE_01.yml
-  SAMPLE_02.yml
-*■ 収集項目値管理設定**
- SAMPLE_01.yml
     - SAMPLE_02.yml
- | VAR_sample_config_1: 1
     - | VAR_sample_config_1: “A”
-*■ 収集値項目管理の設定と対象メニュー項目の収集例**
1. 収集値項目管理の設定と対象メニュー-項目
   収集値項目管理の設定とパラメータシート
-*■対象ファイル、収集値項目管理の設定内容に沿って、ファイル単位に収集処理を実行**
1. SAMPLE_01.yml の登録処理（登録）
2. SAMPLE_02.yml の登録処理（更新）
3. 収集機能完了後のレコードの状態

#### 収集対象ファイルの値の取り扱い
Yaml形式で出力された収集対象ファイルについて、パラメータシートへの登録処理時の値の取り扱いについて以下として扱います。
- No
     - キー
     - 値
     - 備考
- 1
     - VAR_TEST
     - TEST
     -
- 2
     - VAR_STR_TEST1
     - 'TEST1'
     -
- 3
     - VAR_STR_TEST2
     - "TEST2"
     -
- 4
     - VAR_null
     - null
     -
- 5
     - VAR_NULL
     - NULL
     -
- 6
     - VAR_STR_null
     - "null"
     -
- 7
     - VAR_STR_NULL
     -  "NULL"
     -
- 8
     - VAR_true
     - true
     -
- 9
     - VAR_false
     - false
     -
- 10
     - VAR_STR_true
     -  "true"
     -
- 11
     - VAR_STR_false
     - "false"
     -
- 12
     - VAR_YES
     - YES
     -
- 13
     - VAR_NO
     - NO
     -
- 14
     - VAR_STR_YES
     - "YES"
     -
- 15
     - VAR_STR_NO
     - "NO"
     -
- 16
     - VAR_NON
     -
     -
- 17
     - VAR_Quotation
     - ``''``
     -
- 18
     - VAR_WQuotation
     - ``""``
     -
- 19
     - VAR_INT
     - 100
     -
- No
     - 収集対象 (キー:値)
     - | パラメータシート
     - | RESTAPIレスポンス
     - | RESTAPIレスポンス
- 1
     - VAR_TEST: TEST
     - パラメータ/VAR_TEST
     - "TEST"
     - string
     - TEST
- 2
     - VAR_STR_TEST1: 'TEST1'
     - パラメータ/VAR_STR_TEST1
     - "TEST1"
     - string
     - TEST1
- 3
     - VAR_STR_TEST2: "TEST2"
     - パラメータ/VAR_STR_TEST2
     - "TEST2"
     - string
     - TEST2
- 4
     - VAR_null: null
     - パラメータ/VAR_null
     - null
     - null
     -
- 5
     - VAR_NULL: NULL
     - パラメータ/VAR_NULL
     - null
     - null
     -
- 6
     - VAR_STR_null: "null"
     - パラメータ/VAR_STR_null
     - "null"
     - string
     -  null
- 7
     - VAR_STR_NULL: "NULL"
     - パラメータ/VAR_STR_NULL
     -  "NULL"
     -  string
     -  NULL
- 8
     - VAR_true: true
     - パラメータ/VAR_true
     - "true"
     - string
     - true
- 9
     - VAR_false: false
     - パラメータ/VAR_false
     - "false"
     - string
     - false
- 10
     - VAR_STR_true: "true"
     - パラメータ/VAR_STR_true
     - "true"
     - string
     - true
- 11
     - VAR_STR_false: "false"
     - パラメータ/VAR_STR_false
     - "false"
     - string
     - false
- 12
     - VAR_YES: YES
     - パラメータ/VAR_YES
     - "true"
     - string
     - true
- 13
     - VAR_NO: NO
     - パラメータ/VAR_NO
     - "false"
     - string
     - false
- 14
     - VAR_STR_YES: "YES"
     - パラメータ/VAR_STR_YES
     - "YES"
     - string
     - YES
- 15
     - VAR_STR_NO: "NO"
     - パラメータ/VAR_STR_NO
     - "NO"
     - string
     - NO
- 16
     - VAR_NON:
     - パラメータ/VAR_NON
     - null
     - null
     -
- 17
     - VAR_Quotation: ''
     - パラメータ/VAR_Quotation
     - ``""``
     - string
     -
- 18
     - VAR_WQuotation: ""
     - パラメータ/VAR_WQuotation
     - ``""``
     - string
     -
- 19
     - VAR_INT: 100
     - パラメータ/VAR_INT
     - "100"
     - string
     - 100
※パラメータシートの項目は、文字列(単一行)の場合です。
-  対象パラメータシートのRESTAPI(filter)での取得結果
                   "last_updated_user": "収集作業機能",

#### 複数の同一ファイル名がアップロード対象ファイルの指定例
-  _parameters
-  _parameters_file
-  APP001
-  config                   #①
-  APP002
-  config                   #②
-  APP003
-  config                   #③
-  APP002
-  config                   #④
- 収集項目(FROM)/変数名
     - 対象ファイル
     - 備考
- VAR_upload_file_1
     - ①、②、③、④のファイルからランダム
     -
- VAR_upload_file_2
     - ②、④のファイルからランダム
     -
- VAR_upload_file_3
     - ①のファイルが対象
     -
- VAR_upload_file_4
     - ④のファイルが対象
     -
     - ②のファイルが対象

#### ファイル削除時の収集対象ファイル内の記載例
削除するファイルについて対象の変数名の値を空文字として設定することで削除可能です。
-  _parameters
-  _parameters_file
