# Ansible-Pioneer
# はじめに
本書では、Ansible driverのPioneer機能および操作方法について説明します。
# Ansible-Pioneer概要
Ansibleに独自モジュールを追加し、対話形式による設定投入を可能とします。
# Ansible-Pioneer メニュー構成
本章では、Ansible-Pioneerのメニュー構成について説明します。

## メニュー/画面一覧
1. **基本コンソールのメニュー**
Ansible-Pioneerで利用する 基本コンソールのメニュー一覧を以下に記述します。
1. **Ansible共通のメニュー**
※1 非表示メニューは、内部処理で使用するメニューです。
ITAをインストールした状態では表示されないメニューに設定されています。
非表示メニューを表示するには、管理コンソール --> ロール・メニュー紐付管理 で各メニューの復活処理を行います。詳細は「  」を参照してください。
内部処理で使用するメニューには、登録を行わないようにしてください。
1. **Ansible-Pioneerのメニュー**
Ansible-Pioneerのメニュー一覧を以下に記述します。
- No
     - 説明
- 1
     - Movement一覧
     - Movementの一覧を管理します。
- 2
     - 対話種別
     - 同一目的の対話ファイルをまとめる対話種別を管理します。
- 3
     - OS種別
     - Pioneerより作業対象となる機器のOS種別を管理します。
- 4
     - 対話ファイル素材集
     - 対話種別に紐づけるOS種別とITAシステム独自フォーマットの作業手順ファイル（以降、対話ファイルと称す。）を管理します。
- 5
     - Movement-対話種別紐付
     - Movementでインクルードする対話ファイルに対応した対話種別を管理します。
- 6
     - 代入値自動登録設定
     - パラメータシートに登録されているオぺレーションとホスト毎の項目値を紐付けるMovementと変数を管理します。
- 7
     - 作業実行
     - 作業実行するMovementとオペレーションを選択し実行を指示します。
- 8
     - 作業管理
     - 作業実行履歴を管理します。
- 9
     - 作業状態確認
     - 作業実行状態を表示します。
- 10
     - 作業対象ホスト
     - 作業実行毎の作業対象ホストを表示します。
- 11
     - 代入値管理
     - 作業実行毎の変数の具体値を表示します。
- 12
     - Movement-変数紐付 （※1）
     - Movementで使用している変数を管理します。
※1 非表示メニューは、内部処理で使用するメニューです。
ITAをインストールした状態では表示されないメニューに設定されています。
非表示メニューを表示するには、管理コンソール --> ロール・メニュー紐付管理 で各メニューの復活処理を行います。詳細は「  」を参照してください。
内部処理で使用するメニューには、登録を行わないようにしてください。
# Ansible-Pioneer利用手順
Ansible-Pioneerの利用手順について説明します。

## Ansible-Pioneer作業フロー
-  **作業フロー詳細と参照先**
1. **OS種別の登録**
Ansible-Pioneer --> OS種別 から、作業対象のOS種別を登録します。
1. **作業対象への接続情報を登録**
Ansible共通 --> 機器一覧 から、作業対象への接続情報を登録します。
1. **オペレーション名の登録**
基本コンソール --> オペレーション一覧 から、作業用のオペレーション名を登録します。
1. **Ansible Automation Controllerホスト情報を登録（必要に応じて実施）**
Ansible共通 --> Ansible Automation Controllerホスト一覧 から、Ansible Automation Controllerのホスト情報を登録します。
1. **インターフェース情報の登録**
Ansible共通 --> インターフェース情報 から、Ansible Core、Ansible Automation Controller、Ansible Execution Agentのいずれの実行エンジンを使用するかを選択し、実行エンジンのサーバへの接続情報を登録します。
1. **実行環境定義テンプレート管理の登録（必要に応じて実施）**
Ansible共通 --> 実行環境定義テンプレート管理 から、Ansible Execution Agent内にansible-builderで実行環境（コンテナ）をbuildする際の実行環境定義ファイル(execution-environment.yml)のテンプレートファイルを登録します。
尚、ITAをインストールすると、pythonモジュールやansible galaxyコレクションが追加できるテンプレートファイルが登録されます。
1. **パラメータシート「実行環境パラメータ定義」の登録（必要に応じて実施）**
Ansible共通 --> 実行環境定義テンプレート管理 より登録した実行環境定義ファイル(execution-environment.yml)のテンプレートファイルに埋め込むパラメータを登録します。
尚、ITAをインストールすると、実行環境定義テンプレートファイル(execution-environment.yml)に埋め込むパラメータが登録された パラメータシート「実行環境パラメータ定義」 が登録されます。
1. **実行環境管理の登録（必要に応じて実施）**
Ansible共通 --> 実行環境定義テンプレート管理 で登録した実行環境定義ファイル(execution-environment.yml)のテンプレートファイルと パラメータシート「実行環境パラメータ定義」 の紐付を登録します。
尚。ITAをインストールすると、 パラメータシート「実行環境パラメータ定義」 と Ansible共通 --> 実行環境定義テンプレート管理 の紐付が登録されます。
1. **Movementの登録**
Ansible-Pioneer --> Movement一覧 から、作業用のMovementを登録します。
1. **対話種別の登録**
Ansible-Pioneer --> 対話種別 から、対話種別を登録します。
1. **対話ファイルの登録**
Ansible-Pioneer --> 対話ファイル素材集 から、対話種別とOS種別の組み合わせに対して対話ファイルを登録します。
1. **グローバル変数の登録（必要に応じて実施）**
Ansible共通 --> グローバル変数管理 、Ansible共通 --> グローバル変数（センシティブ）管理 から、対話ファイルで使用するグローバル変数を登録します。
1. **テンプレートファイルの登録（必要に応じて実施）**
Ansible共通 --> テンプレート管理 から、対話ファイルで使用するテンプレートファイルとテンプレート埋込変数を登録します。
1. **ファイル素材の登録（必要に応じて実施）**
Ansible共通 --> ファイル管理 から、対話ファイルで使用するファイル素材とファイル埋込変数を登録します。
1. **管理対象外変数の登録（必要に応じて実施）**
Ansible共通 --> 管理対象外変数リスト から、変数抜出対象の資材から抜出した変数で、 Ansible-Pioneer --> 代入値自動登録 の Movement名:変数名 に表示したくない変数を登録します。
1. **Movementに対話ファイルを登録**
Ansible-Pioneer --> Movement-対話種別紐付 から、登録したMovementでインクルードする対話ファイルに対応した対話種別を登録します。
1. **パラメータシートの作成**
パラメータシート作成・定義 から、作業対象の設定に使用するデータを登録するためのパラメータシートを作成します。
1. **パラメータシートにデータを登録**
前項で作成したパラメータシートから、作業対象の設定に使用するデータを登録します。
1. **代入値自動登録設定**
Ansible-Pioneer --> 代入値自動登録設定 から、パラメータシートに登録されているオペレーションとホスト毎の項目の設定値と、Movementの変数を紐付けます。
1. **作業実行**
Ansible-Pioneer --> 作業実行 から、Movementとオペレーションを選択し作業の実行を行います。
1. **作業状態確認**
1. **作業履歴確認**
Ansible-Pioneer --> 作業管理 から、実行した作業の一覧が表示され履歴が確認できます。
# Ansible-Pioneer メニュー操作方法説明
本章では、Ansible-Pioneerで利用するメニューについて説明します。

## 基本コンソール

## Ansible共通

## Ansible-Pioneer

#### OS種別
1. 作業対象となる機器のOS種別のメンテナンス（閲覧/登録/更新/廃止）を行います。
項番                       | 登録時に自動採番した36桁の文字列が表示されます。                       | ー                 | 自動入力              | ー                                              |

#### Movement一覧
1. Movement情報のメンテナンス（閲覧/登録/更新/廃止）を行います。
項目                                      | 説明                                                                                                           | 入力必須  | 入力方法     | 制約事項                                                   |
MovementID                                | 登録時に自動採番した36桁の文字列が表示されます。                                                               | ー        | 自動入力     | ー                                                         |
Movement名                                | Movementの名称を入力します。                                                                                   | ○         | 手動入力     | 最大長255バイト                                            |
遅延タイマー                              | Movementの実行が指定期間遅延した場合に Ansible-\                                               | ー        | 手動入力     | 0～2,147,483,647                                           |
並列実行数              | ansible-playbookコマンドのオプションパラメータ\                                                                | ー        | 手動入力     | 1～4,294,967,296                                           |
Ansible \   | 実行環境  | :menuselection:Ansible共通 --> 実行環境定義` に登録されている 実\                             | ー        | リスト選択   | 説明欄記載のとおり。                                       |
Agent \     |           | （コンテナ）をbuildする際に使用するテンプレートファイルとパラメータシート「実行\                               |           |              |                                                            |
利用情報    |           | 環境パラメータ定義」が紐付いている実行環境名を選択します。                                                     |           |              |                                                            |
builder\  | ansibe-builderのパラメータを入力します。                                                                       |           |              |                                                            |
利用情報    |           | に設定されているデフォルトの実行環境が使用されます。                                                           |           |              |                                                            |

#### 対話種別
1. 対話種別のメンテナンス（閲覧/登録/更新/廃止）を行います。
Ansible-Pioneerでは、「OS種別」ごとの差異を対話ファイルごとに定義し、同一目的の対話ファイルを「対話種別」として纏めて機器差分を吸収（抽象化）します。
- 項目
        - 説明
        - 入力必須
        - 入力方法
        - 制約事項
- 項番
        - 登録時に自動採番した36桁の文字列が表示されます。
        - ー
        - 自動入力
        - ー
- 対話種別名
        - 対話種別名を入力します。
        - 〇
        - リスト選択
        - 最大長255バイト
- 備考
        - 自由記述欄です。
        - ー
        - 手動入力
        - 最大長4000バイト

#### 対話ファイル素材集
1. ユーザが作成した対話ファイルのメンテナンス（閲覧/登録/更新/廃止）を行います。
対話種別とOS種別の組み合わせごとに対話ファイルを登録します。
１つの対話種別で複数のOSに対応させたい場合は、同じ対話種別で、OS種別それぞれについて対話ファイルを登録してください。
項目                              | 説明                                                                                | 入力必須  | 入力方法     | 制約事項               |
項番                              | 登録時に自動採番した36桁の文字列が表示されます。                                    | －        | 自動入力     | －                     |
で登録した :menuselection:対話種別` が表示されます。                               |           |              |                        |
登録する対話ファイルの対話種別を選択します。                                        |           |              |                        |
OS種別                            | Ansible-Pioneer --> OS種別 で登録した OS種別 \    | ○         | リスト選択   | 説明欄記載のとおり。   |
登録する対話ファイルのOS種別を選択します。                                          |           |              |                        |
ターゲット | Linux                | Linuxで使用可能なPlaybookの場合、「＊」を選択します。                               | －        | リスト選択   | 説明欄記載のとおり。   |
Windows              | Windowsで使用可能なPlaybookの場合、「＊」を選択します。                             | －        | リスト選択   | 説明欄記載のとおり。   |
その他               | Linux、Windows以外の用途で使用可能なPlaybookの場合、Playbookの用途を入力します。    | －        | 手動入力     | 最大長4000バイト       |
説明                              | Playbookについての説明を入力します。                                                | ー        | 手動入力     | 最大長4000バイト       |
説明(en)                          | Playbookについての説明を英語で入力します。                                          | ー        | 手動入力     | 最大長4000バイト       |
**対話ファイル内に定義した変数を取り出すタイミング**
内部の処理で対話ファイル内に定義している変数を抽出します。抽出した変数は、「  」で具体値の登録が可能になります。
抽出のタイミングはリアルタイムではないので、「  」で変数が扱えるまでに **時間がかかる** 場合があります。

#### Movement-対話種別紐付
1. Movementでインクルードする対話ファイルに対応した対話種別のメンテナンス（閲覧/登録/更新/廃止）を行います。
- 対話種別
        - 説明
        - 入力必須
        - 入力方法
        - 制約事項
- 項番
        - 登録時に自動採番した36桁の文字列が表示されます。
        - ー
        - 自動入力
        - ー
- Movement
        - | Ansible-Pioneer --> Movement一覧 で登録した Movement名 が表示されます。
Movement を選択します。
        - 〇
        - リスト選択
        - 説明欄記載のとおり。
- 対話種別
        - | Ansible-Pioneer --> 対話種別 で登録した 対話種別 が表示されます。
Movementでインクルードする対話ファイルに対応した対話種別を選択します。
        - 〇
        - リスト選択
        - 説明欄記載のとおり。
- インクルード順序
        - | 対話種別の実行順序（1～）を入力します。
        - 〇
        - 手動入力
        - 1～2,147,483,647
- 備考
        - 自由記述欄です。
        - 〇
        - 手動入力
        - 最大長4000バイト

#### 代入値自動登録設定
1. パラメータシートの項目の設定値とMovementの変数との紐付管理（閲覧/登録/更新/廃止）を行います。
登録した情報は作業実行により Ansible-Pioneer --> 代入値管理 と Ansible-Pioneer--> 作業対象ホスト に反映されます。
項目                              | 説明                                                               | 入力必須                                     | 入力方法     | 制約事項                    |
項番                              | 登録時に自動採番した36桁の文字列が表示されます。                   | ー                                           | 自動入力     | ー                          |
パラメータシー\ | メニューグルー\ | パラメータシートの項目が表示されます。                             | ○                                            | リスト選択   | 説明欄記載のとおり。        |
ト（From）      | プ:メニュー:項目|                                                                    |                                              |              |                             |
選択対象となるパラメータシートは\                                  |                                              |              |                             |
パラメータシート作成 --> \                         |                                              |              |                             |
パラメータシート定義・作成 --> 作成対象\                          |                                              |              |                             |
で、パラメータシート（ホスト/オペレーションあり）\                 |                                              |              |                             |
を選択して作成したパラメータシートの項目になります。               |                                              |              |                             |
代入順序        | パラメータシートがバンドルの場合、\                                |                                |              |                             |
登録方式                          | IaC変数（To） で選択した変数の具体値\             | ○                                            | リスト選択   | 説明欄記載のとおり。        |
に設定する内容を選択します。                                       |                                              |              |                             |
項目の設定値が IaC変数（To） で選択した変数\  |                                              |              |                             |
項目の名称が IaC変数（To） で選択した変数\    |                                              |              |                             |
Movement名                        | Ansible-Pioneer --> Movement一覧 で登録した\      | ○                                            | リスト選択   | 説明欄記載のとおり。        |
Movement名 が表示されます。                       |                                              |              |                             |
Movementを選択します。                                             |                                              |              |                             |
IaC変数（To）   | Movement名\     | Ansible-Pioneer --> Movement-対話種別紐付 で\     | ○                                            | リスト選択   | 説明欄記載のとおり。        |
:変数名         | 登録した資材で使用している変数が表示されます。                     |                                              |              |                             |
パラメータシート（From） で選択した項目の具体値\  |                                              |              |                             |
を紐付けたい変数を選択します。                                     |                                              |              |                             |
代入順序        | 複数具体値変数にする場合に入力してください。                       |      | 手動入力     | 1～2,147,483,647            |
NULL連携                          | パラメータシートの具体値が\                                        |                                              | リスト選択   | 説明欄記載のとおり。        |
Ansible-Pioneer --> 代入値管理 に\                |                                              |              |                             |
NULL（空白）の値を登録するかを選択します。                         |                                              |              |                             |
パラメータシートの値がどのような\                              |                                              |              |                             |
値でも Ansible-Pioneer --> 代入値管理 に\     |                                              |              |                             |
登録が行われます。                                             |                                              |              |                             |
パラメータシートに値が入力\                                    |                                              |              |                             |
管理` に登録が行われます。                                     |                                              |              |                             |
※1: パラメータシート（バンドル）を使用する場合のみ必須
パラメータシート（バンドル）のリピート設定されている項目とMovementの変数を紐付ける場合、 Ansible-Pioneer --> 代入値自動登録設定 でパラメータシート（From） の代入順序を入力する必要があります。
Ansible-Pioneer では、代入順序が未入力の場合は、通常変数として扱います。
代入順序が入力されている場合は、複数具体値変数として扱います。複数具体値変数の場合は複数の
特定の複数具体値変数に対して代入順序が連続していなくても問題ありません。
e.g.）複数具体値変数に代入順序を入力して作業実行する場合
1. Ansible-Pioneer --> 代入値自動登録設定 でパラメータシートに登録されている項目の設定値と対話ファイル内の変数を紐付けします。
       パラメータシートの登録内容
-*ホスト名**   | **オペレーション名**   | **パラメータ**                            |
      .. list-table:: 代入値自動登録設定の登録内容
- メニュー名
           - 項目
           - 変数名
           - 代入順序
- sample-menu
           - 項目1
           - VAR_substitutionA
           - 30
- sample-menu
           - 項目2
           - VAR_substitutionA
           - 10
- sample-menu
           - 項目3
           - VAR_substitutionA
           - 20
- sample-menu
           - 項目1
           - VAR_substitutionB
           - 2
- sample-menu
           - 項目2
           - VAR_substitutionB
           - 4
- sample-menu
           - 項目3
           - VAR_substitutionB
           - 1
- sample-menu
           - 項目4
           - VAR_substitutionB
           - 3
1. 作業実行時、ホスト変数ファイル（host_vars/test-host）には、代入値自動登録設定で登録した変数が下記のように出力されます。
-*ホスト変数ファイルへの出力内容**
           - value2
           - value3
           - value1
           - value3
           - value1
           - value4
           - value2
**ホスト変数ファイルへの出力**
代入値自動登録設定で登録した変数のみが作業実行時にホスト変数ファイルへ出力されます。
作業実行時に 対話ファイルで使用している変数が代入値自動登録設定に登録されていない場合、作業実行がエラーとなります。
**ファイル埋込変数とテンプレート埋込変数を対話ファイルの変数に紐付して使用する例**
e.g.） ファイル埋込変数 CPF_test とテンプレート埋込変数 TPF_sample を代入値自動登録設定で対話ファイルの変数に紐付して使用する場合
1. Ansible共通 --> ファイル管理 ／ Ansible共通 --> テンプレート管理 で下記のように登録します。
      .. list-table:: ファイル管理の登録内容
- ファイル埋込変数名
           - ファイル素材
- CPF_test
           - test_file.txt
      .. list-table:: テンプレート管理の登録内容
- テンプレート埋込変数名
           - テンプレート素材
- TPF_sample
           - sample.tpl
1. パラメータシート定義・作成 で「Ansible共通:ファイル管理:ファイル埋込変数名」「Ansible共通:テンプレート管理:テンプレート埋込変数名」をパラメータシートの項目としてパラメータシート作成後、パラメータシートで項目の設定値としてファイル埋込変数とテンプレート埋込変数を登録します。
       サンプルパラメータシートの登録内容
-*ホスト名**   | **オペレーション名**   | **パラメータ**                        |
- **ファイル管理**| **テンプレート管理**|
1. Ansible-Pioneer --> 代入値自動登録設定 で2. のパラメータシートに登録した項目の設定値と対話ファイルの変数を紐付して Ansible-Pioneer --> 作業実行 で作業実行します。
      .. list-table:: 代入値自動登録設定の登録内容
- メニュー名
           - 項目
           - 変数名
- サンプルパラメータシート
           - ファイル管理
           - VAR_filetest
- サンプルパラメータシート
           - テンプレート管理
           - VAR_temptest
         作業状態確認の代入値管理
 代入値自動登録設定の連携対象項目については、 を参照してください。

#### 作業実行
作業対象のMovementをMovement一覧から選択します。
作業対象のオペレーションをオペレーション一覧から選択します。
1. **作業実行**
1. **ドライラン**
ドライランを行った場合の動作は、Ansible-Playbookコマンドの--checkパラメータを指定した実行となります。
1. **パラメータ確認**

#### 作業状態確認
1. **実行状態表示**
「実行種別」には、作業実行の場合は「通常」、ドライランの場合は「ドライラン」、パラメータ確認の場合は「パラメータ確認」が表示されます。
「呼出元Conductor」には、Conductorから実行した場合に、どのConductorから実行されたかを表示します。Ansible-Pioneerから直接実行した場合は空欄になります。
1. **作業対象ホスト確認**
1. **代入値確認**
1. **緊急停止/予約取り消し**
1. **実行ログ表示**
さらに、 Ansible共通 --> インターフェース情報 の オプションパラメータ でジョブスライス数を指定することによりグループ化された作業対象をさらにジョブスライス数で分割しplaybookが実行され、ansibleの実行ログも分割されます。
- 要素
        - 内容
- グループ番号
        - 作業対象の Ansible共通 --> 機器一覧 の ユーザ ・ パスワード ・ ssh秘密鍵ファイル ・ パスフレーズ ・ 接続タイプ ・ インスタンスグルーブ の項目値でグルーブ化した 1 からの通番です。
- 通番
        - | ジョブスライス数の設定によりグループ内を分割した 1 からの通番です。
1. **ログ検索**
実行ログ、エラーログのリフレッシュ表示間隔と最大表示行数を、  Ansible共通 --> インターフェース情報  の  状態監視周期（単位ミリ秒） と 進行状態表示行数 で設定できます。
1. **投入データ**
実行したPlaybookなどをダウンロードすることができます。
1. **結果データ**

#### 作業管理
呼出元Conductor                                                               | Conductorから実行した場合にConductor名が表示されます。                       |
Movement            | ID                                                      | 作業実行で選択したMovementのIDが表示されます。                               |
名称                                                    | 作業実行で選択したMovementの名称が表示されます。                             |
遅延タイマー                                            | 作業実行で選択したMovementの遅延タイマーが表示されます。                     |
Ansible利用情報               | ホスト指定形式          | 作業実行で選択したMovementのホスト指定形式が表示されます。                   |
WinRM接続               | 作業実行で選択したMovementのWinRM接続が表示されます。                        |
ヘッダーセクション      | 作業実行で選択したMovementのヘッダーセクションが表示されます。               |
ansible.cfg             | 作業実行で選択したMovementのansible.cfgがアップロード出来ます。              |
Ansible Execution Agent \     | 実行環境                | 作業実行で選択したMovementのAnsible Execution Agentの実行環境が表示されます。|
ansible-builder\        | 作業実行で選択したMovementのansible-builderパラメータが表示されます。        |
パラメータ              |                                                                              |
Ansible Automation \          | 実行環境                | 作業実行で選択したMovementの実行環境が表示されます。                         |
オペレーション      | No.                                                     | 作業実行で選択したオペレーションのIDが表示されます。                         |
名称                                                    | 作業実行で選択したオペレーションの名称が表示されます。                       |
作業状況            | 予約日時                                                | 作業実行で予約日時を設定した場合に予約日時が表示されます。                   |
収集状況            | ステータス                                              | 収集機能のステータスを表示します。                                           |
収集ログ                                                | 収集機能のログがダウンロード出来ます。                                       |
Conductorインスタンス番号                                                     | Conductorから実行された場合にConductorインスタンス番号を表示します。         |

#### 作業対象ホスト
1. 作業実行毎の作業対象ホストを閲覧できます。
- 項目
        - 説明
- 項番
        - 作業実行時に自動採番した36桁の文字列が表示されます。
- 作業No
        - 作業実行時の作業Noが表示されます。
- オペレーション
        - 作業実行時のオペレーションが表示されます。
- Movement名
        - 作業実行時のMovementが表示されます。
- ホスト名
        - 作業実行時の対象ホストが表示されます。
- 備考
        - 自由記述欄です。

#### 代入値管理
1. 作業実行毎の変数の具体値を閲覧できます。
オペレーション                            | 作業実行時のオペレーションが表示されます。                                                                  |
Movement名                                | 作業実行時のMovementが表示されます。                                                                        |
Movement名:変数名                         | 作業実行時の変数が表示されます。                                                                            |
具体値     | 文字列    | Sensitive設定    | 「True」または「False」が表示されます。                                                                     |
値               | 作業実行時の変数の具体値が表示されます。                                                                    |
| + | Sensitive設定 が「True」の場合                                                         |
|   | パラメータシートで入力した具体値は暗号化されITA上では表示されません。\                                  |
|     変数の具体値は、ansible-vaultで暗号化した内容が設定されます。                                           |
| + | Sensitive設定 が「False」の場合                                                        |
|   | パラメータシートで入力した具体値が表示されます。                                                        |
ファイル                     | 作業実行の変数に紐づくファイル名が表示されます。                                                            |
代入順序                                  | 複数具体値変数の場合に、代入順序が表示されます。                                                            |
# 対話ファイル（Ansible-Pioneer）の記述方法
- 用語
        - 説明
- コマンドプロンプト
        - ターミナルから作業対象サーバーにsshで接続した場合に、コマンド入力待ちの状態を示す文字列です。
- 標準出力
        - 作業対象サーバーにコマンド投入後、コマンドプロンプトより前に出力されるコマンドの処理結果です。

## 対話ファイルの構成
conf             | timeoutパラメータによりタイムアウト値を指定します。  |
対話ファイルの先頭にconfセッションのtimeoutパラメータを記述します。
- | e.g.）confセッションのtimeoutパラメータの記述例
- | e.g.）パスワード認証の記述例
       - expect: '*assword'

## 対話モジュール

#### expectモジュール
-***
-***
パラメータ　         | 書式                               | 必須/任意  | 説明　                                                                             |
-*****
- | e.g.）expectモジュールの記述例
     - expect: '*assword'

#### stateモジュール
-***
-***
パラメータ　         | 書式                                     | 必須/任意  | 説明　                                                                             |
-*****
- | e.g.）stateモジュールの記述例
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.）success_exitの使用例
     # 127.0.0.1、localhostを含む行があれば正常と判定しますが「success_exit: yes」の設定により対話ファイルを正常終了します。
       - state: 'cat /etc/hosts'
           - '127.0.0.1'
           - 'localhost'
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.）ignore_errorsの使用例
     # 対象行がなければ異常と判定しますが「ignore_errors: yes」の設定により次の処理に進みます。
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.）shellの使用例
     # parameter値をユーザ作成のshellのパラメータで渡します。
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) ユーザshell（/tmp/grep.sh）の例
- | e.g.）stateモジュールで作業対象ホストのファイルを、「結果データ」に保存する例
     # デフォルトのshellはparameterの設定がないと異常と判定します。次の処理に進める為に「ignore_errors: yes」を設定します。
      - state: 'cat /etc/hosts'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

#### commandモジュール
-***
④registerで指定されているregister変数名に標準出力の内容を保存する。
⑦registerで指定されているregister変数名に標準出力の内容を保存する。
-***
パラメータ　         | 書式                                     | 必須/任意  | 説明　                                                                             |
-*****
- | e.g.) commandモジュールの記述例
対話ファイルの記述とwith_itemsで使用する変数の具体値は以下の様になります。
  - | 対話ファイルの記述内容
     - command: "systemctl  {{ item.0 }}  {{ item.1 }}"
         - '{{ VAR_status_list }}'    # item.0
         - '{{ VAR_service_list }}'   # item.1
         - '{{ VAR_prompt_list }}'    # item.2
         - '{{ VAR_timeout_list }}'   # item.3
  - | with_itemsで使用する変数の具体値
       - start
       - start
       - httpd
       - mysql
     # commandで使用している変数の具体値が2個あるので
     # promptとtimeoutで使用している変数の具体値は3個必要になります。
       - コマンドプロンプト
       - コマンドプロンプト
       - コマンドプロンプト
       - 10
       - 10
       - 10
- | e.g.） whenを使用した例
       - expect: 'password:'
       # VAR_hosts_makeというITA変数がホスト変数ファイルに記載（代入値自動登録でパラメータシートの項目と変数の紐付を行ってる）されている場合、
       - command: cat /etc/hosts
           - VAR_hosts_make is define
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.） exec_whenとregisterを使用した例
       - expect: 'password:'
       # VAR_hosts_makeという変数がホスト変数ファイルに記載されている場合、hostsファイルをcatします。
       - command: cat /etc/hosts
           - VAR_hosts_make is define
       # VAR_hosts_makeという変数がホスト変数ファイルに記載されている場合、
       # with_itemsの複数具体値変数に設定されている具体値数分、コマンドを投入します。
       - command: 'echo {{ item.0 }}  {{ item.1 }} >> /etc/hosts'
           - VAR_hosts_make is define
           - '{{ VAR_hosts_ip }}'     # item.0
           - '{{ VAR_hosts_name }}'   # item.1
           - result_stdout no match({{ item.0 }} *{{ item.1 }})
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.）failed_whenを使用した例
       - expect: 'password:'
       # with_itemsの複数具体値変数に設定されている具体値数分コマンドを投入します。
       # サービスの自動起動を設定します。
       - command: 'systemctl enable {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
       # with_itemsの複数具体値変数に設定されている具体値数分コマンドを投入します。
       - command: 'systemctl start {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
       # with_itemsの複数具体値変数に設定されている具体値数分コマンドを投入します。
       # 例えば、VAR_service_status_listの具体値をrunningと設定し、サービスが起動している場合、
       - command: 'systemctl status {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
           - '{{ VAR_service_status_list }}'  # item.1
           - stdout match({{ item.1 }})
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.） whenでor/and条件を使用した例
       - expect: 'password:'
       - command: systemctl stop my_service
           - '{{ VAR_status }} == 10 OR {{ VAR_status }} == 11'
           - '{{ VAR_sub_status }} == 20 OR {{ VAR_sub_status }} == 21'
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

#### localactionモジュール
-***
-***
パラメータ　         | 書式                                     | 必須/任意  | 説明　                                                                           |
-*****
- | e.g.）localactionの記述例
       - expect: 'password:'
       # Movementで共有するディレクトリ（{{ __workflowdir__ }}）にホスト毎のディレクトリを作成する。
       - localaction: mkdir -p 0755 {{ __workflowdir__ }}/{{ __inventory_hostname__ }}
       - state: cat /etc/hosts
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

## 正規表現
下記のモジュール及びパラメータに記述した文字列は正規表現で評価されます。
- expectモジュールのexpectパラメータ
- stateモジュールのpromptパラメータ
- commandモジュールのpromptパラメータ
- commandモジュールのwhen/exec_when/failed_whenパラメータのmatch()
- 対象文字
     - エスケープ後
- \\
     - | \\\\
- \*
     - \\*
- \.
     - \\.
- \+
     - \\+
- ?
     - \\?
- \|
     - \\|
- { }
     - \\{ \\}
- ( )
     - \\( \\)
- [ ]
     - \\[ \\]
- ^
     - \\^
- $
     - \\$
- | e.g.) 正しい例
- | e.g.) 誤った例

## 注意事項

#### stateモジュールとcommandモジュールの使用時の注意事項
1. promptパラメータに正規表で後方一致「\.\*」を記述した場合
stateモジュールとcommandモジュールは、コマンドを投入後、promptパラメータで指定されたコマンドプロンプトより前のデータを標準出力として扱います。
   - | e.g.）正規表現で後方一致の使用例
       - state: echo 'saple data'
1. 対話コマンドを処理する場合
   - | e.g.）対話コマンド「ssh-keygen」を処理する例
        - expect: 'assword:'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
        # 秘密鍵ファイルのパスを設定
        - expect: 'id_rsa\):'
        # パスフレーズを設定
        - expect: ' passphrase\):'
        - expect: ' passphrase again:'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'

#### 複数具体値変数使用時の注意事項
対話ファイルで複数具体値変数が使用出来るパラメータは、commandモジュールのwith_itemsパラメータのみです。これ以外で使用した場合、作業実行時にエラーとなります。

#### 対話ファイル終了時の注意事項
- | e.g.）対話ファイルの最終行に、セッションを終了するコマンド「exit」を投入する例
       - expect: 'assword:'
       - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
       - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'

#### 対話ファイルをyaml形式で記載する際の注意事項
対話ファイルはyaml形式のファイルとして扱います。以下のようなYAML形式に準じていない記載があると対話モジュールの登録時にエラーとなります。
- | 各モジュールのパラメータに変数を記載している場合でパラメータ全体をクォーテーションで囲んでいない場合。
- | 各パラメータを定数のみで記載している場合で、定数の終端が「\ **:**\ 」の場合など、パラメータ全体をクォーテーションで囲んでいない場合。
各モジュールのパラメータは、パラメータ全体をクォーテーションで囲んでください。

#### 作業対象のログインユーザのLANGについての注意事項
ログインユーザの「LANG」の設定は Ansible共通 --> 機器一覧 の LANG より行ってください。
「euc/shift_jis」を設定した場合、作業対象との通信制御で使用しているpexpectモジュールのUTF-8へのデコード処理の特性で対話ファイルを正しく処理出来ない場合があります。

#### 作業対象へ投入するコマンドの終端コードについての注意事項
     - expect: 'password:'
     - command: '{{ VAR_command }}\r'
     - state: '{{ VAR_state }}\r'
        - '{{ VAR_parameter1 }}'
        - '{{ VAR_parameter2 }}'

#### Operating System Commandシーケンス
作業対象に依存しますが、作業対象から送られてくるコマンドプロンプトの直前にOperating System Commandシーケンスが付加されている場合があります。promptパラメータで指定された文字列の直前にあるエスケープシーケンスをITAが排除しています。
# 付録

## Ansible実行時に使用される投入データとITAメニューの紐づけ
ITAの各メニューより情報を抜出してAnsible実行に必要な投入データを作ります。この際、 Ansible共通 --> 機器一覧 の パスワード や Ansible-Pioneer --> 代入値管理 で Sensitive設定 が「True」に設定されている変数の具体値は、ansible-vaultで暗号化されています。
各種データとITAメニューの関係性は以下の通りです。

#### Ansible-Pioneer投入データ
- メニューグループ
     - メニュー
     - 項目
     - ディレクトリ解凍時のパス
     - 備考
- Ansible-Pioneer
     - 対話ファイル素材集
     - 対話ファイル
     - /child_playbooks
     -
- Ansible 共通
     - テンプレート管理
     - テンプレート素材
     - /template_files
     -
- Ansible 共通
     - ファイル管理
     - ファイル素材
     - /copy_files
     -
- Ansible-Pioneer
     - 代入値管理
     - 具体値（ファイル）
     - /upload_files
     -
- Ansible 共通
     - グローバル変数管理
     - 変数名/具体値
     - /host_vars
     -
- Ansible 共通
     - グローバル変数（センシティブ）管理
     - 変数名/具体値
     - /host_vars
     - ※ansible-vault で暗号化
- Ansible-Pioneer
     - 代入値管理
     - 変数名/具体値
     - /host_vars
     -
- Ansible-Pioneer
     - template 管理
     - テンプレート埋込変数
     - /host_vars
     -
- Ansible-Pioneer
     - ファイル管理
     - ファイル埋込変数
     - /host_vars
     -
- Ansible共通
     - 機器一覧
     - | ログインユーザ ID
     - /host_vars
     -
- Ansible共通
     - 機器一覧
     - ssh 認証鍵ファイル
     - /ssh_key_files
     -
- Ansible共通
     - インターフェース情報
     - オプションパラメータ
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible-Pioneer
     - Movement一覧
     - 並列実行数
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible共通
     - 機器一覧
     - | ホスト名
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible共通
     - 機器一覧
     - 接続オプション
     - /host_vars
     -
- Ansible-Pioneer
     - Movement-対話種別紐付
     - | 対話ファイル
     - /playbook.yml
     -
- Ansible共通
     - 実行環境定義テンプレート管理
     - テンプレートファイル
     - builder_executable_files/execution-environment.yml
     - Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Execution Agent」の場合のみ
- Ansible共通
     - パラメータシート「実行環境パラメータ定義」
     - 各種アップロードファイル
     - builder_executable_files/{{Rest API用項目名}}_アップロードファイル名
     - Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Execution Agent」の場合のみ
- Ansible共通
     - 実行環境管理
     - タグ名
     - | builder_executable_files/builder.sh
     - Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Execution Agent」の場合のみ

## Ansible実行時に作成される結果データ

#### Ansible-Pioneer結果データに保存されるファイル一覧
- ファイル名
     - 記録内容
     - Ansible Coreの場合
     - Ansible Automation Controllerの場合
     - AAnsible Execution Agentの場合
- result.txt
     - Ansibleの実行結果を記録
     - 〇
     -
     -
- xxx.pid
     - | Ansible-playbbokコマンドのプロセスIDを記録するファイル
     - 〇
     -
     - 〇
- pioneer.xxx
     - | PioneerモジュールのプロセスIDを記録するファイル。
     - 〇
     - 〇
     - 〇
- xxx_private.log
     - | Pioneerモジュールのログを記録するファイル。
     - 〇
     - 〇
     - 〇
- error.log
     - | 作業実行時のエラーメッセージ出力先ファイル
     - 〇
     - 〇
     - 〇
- exec.log.org
     - Ansible-playbbokコマンドの標準出力の出力先ファイル
     - 〇
     - 〇
     - 〇
- exec.log
     - | Aexec.log.orgを加工したファイル
     - 〇
     - 〇
     - 〇
- exec_<作業番号>_<グループ番号>
     - | 分割された実行ログファイル
     -
     - 〇
     -
- forced.txt
     - 緊急停止をした場合の記録ファイル
     - 〇
     -
     - 〇
- user_files
     - 実行したplaybookでITA独自変数「\__\workflowdir\__\」にファイル出力をした場合の出力先ディレクトリ。
     - 〇
     - 〇
     - 〇
- | child_exec.log
     - ansible-builderの実行ログ
     -
     -
     - 〇
