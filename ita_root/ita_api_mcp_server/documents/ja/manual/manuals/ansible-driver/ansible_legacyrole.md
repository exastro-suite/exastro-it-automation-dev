# Ansible-LegacyRole
# はじめに
本書では、Ansible driverのLegacyRole機能および操作方法について説明します。
# Ansible-LegacyRole概要
Legacyモードと同じく、Ansible標準の機能を用いて各種ホストへ設定を投入します。
構築コードをパッケージとして登録し、作業パターンをRoleの組み合わせで構成します。
# Ansible-LegacyRole メニュー構成
本章では、Ansible-LegacyRoleのメニュー構成について説明します。

## メニュー/画面一覧
1. **基本コンソールのメニュー**
Ansible-LegacyRoleで利用する 基本コンソールのメニュー一覧を以下に記述します。
1. **Ansible共通のメニュー**
※1 非表示メニューは、内部処理で使用するメニューです。
ITAをインストールした状態では表示されないメニューに設定されています。
非表示メニューを表示するには、管理コンソール --> ロール・メニュー紐付管理 で各メニューの復活処理を行います。詳細は「  」を参照してください。
内部処理で使用するメニューには、登録を行わないようにしてください。
1. **Ansible-LegacyRoleのメニュー**
Ansible-LegacyRoleのメニュー一覧を以下に記述します。
- No
     - 説明
- 1
     - Movement一覧
     - Movementの一覧を管理します。
- 2
     - ロールパッケージ管理
     - ロールパッケージを管理します。
- 3
     - Movement-ロール紐付
     - Movementでインクルードするロールパッケージを管理します。
- 4
     - 変数ネスト管理
     - 多段変数が繰返配列で構成されている場合の最大繰返配列数を管理します。
- 5
     - 代入値自動登録設定
     - パラメータシートに登録されているオぺレーションとホスト毎の項目値を紐付けるMovementと変数を管理します。
- 6
     - 作業実行
     - 作業実行するMovementとオペレーションを選択し実行を指示します。
- 7
     - 作業管理
     - 作業実行履歴を管理します。
- 8
     - 作業状態確認
     - 作業実行状態を表示します。
- 9
     - 作業対象ホスト
     - 作業実行毎の作業対象ホストを表示します。
- 10
     - 代入値管理
     - 作業実行毎の変数の具体値を表示します。
- 11
     - ロール名管理 （※1）
     - ロールパッケージ管理にアップロードしたロールパッケージファイル「zip」内に登録されているロール名とロールパッケージの紐付を閲覧できます。
- 12
     - Movement-変数紐付 （※1）
     - Movementで使用している変数を管理します。
- 13
     - 多段変数メンバー管理 （※1）
     - ロールパッケージ管理にアップロードしたロールパッケージファイル「zip」内のデフォルト変数定義ファイルやITA readmeファイルで定義している多段変数の構造を管理します。
- 14
     - 多段変数配列組合せ管理 （※1）
     - ロールパッケージ管理にアップロードしたロールパッケージファイル「zip」内のデフォルト変数定義ファイルやITA readmeファイルで定義している多段変数配列組合せを管理します。
※1 非表示メニューは、内部処理で使用するメニューです。
ITAをインストールした状態では表示されないメニューに設定されています。
非表示メニューを表示するには、管理コンソール --> ロール・メニュー紐付管理 で各メニューの復活処理を行います。詳細は「  」を参照してください。
内部処理で使用するメニューには、登録を行わないようにしてください。
# Ansible-LegacyRole利用手順
Ansible-LegacyRoleの利用手順について説明します。

## Ansible-LegacyRoleの作業フロー
-  **作業フロー詳細と参照先**
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
Ansible-LegacyRole --> Movement一覧 から、作業用のMovementを登録します。
1. **ロールパッケージの登録**
Ansible-LegacyRole --> ロールパッケージ管理 から、作業で使用するロールパッケージを登録します。
1. **グローバル変数の登録（必要に応じて実施）**
Ansible共通 --> グローバル変数管理 、Ansible共通 --> グローバル変数（センシティブ）管理 から、ロールパッケージ内で使用するグローバル変数を登録します。
1. **テンプレートファイルの登録（必要に応じて実施）**
Ansible共通 --> テンプレート管理 から、ロールパッケージ内で使用するテンプレートファイルとテンプレート埋込変数を登録します。
1. **ファイル素材の登録（必要に応じて実施）**
Ansible共通 --> ファイル管理 から、ロールパッケージ内で使用するファイル素材とファイル埋込変数を登録します。
1. **管理対象外変数の登録（必要に応じて実施）**
Ansible共通 --> 管理対象外変数リスト から、変数抜出対象の資材から抜出した変数で、 Ansible-LegacyRole --> 代入値自動登録 の Movement名:変数名 に表示したくない変数を登録します。
1. **Movementにロールパッケージを登録**
Ansible-LegacyRole --> Movement-ロール紐付 から、登録したMovementでインクルードするロールパッケージを登録します。
1. **多段変数の最大繰返数を登録（必要に応じて実施）**
Ansible-LegacyRole --> 変数ネスト管理 から、多段変数で配列定義されているメンバー変数の配列の最大繰返数を登録します。
1. **パラメータシートの作成**
パラメータシート作成・定義 から、作業対象の設定に使用するデータを登録するためのパラメータシートを作成します。
1. **パラメータシートにデータを登録**
前項で作成したパラメータシートから、作業対象の設定に使用するデータを登録します。
1. **代入値自動登録設定**
Ansible-LegacyRole --> 代入値自動登録設定 から、パラメータシートに登録されているオペレーションとホスト毎の項目の設定値と、Movementの変数を紐付けます。
1. **作業実行**
Ansible-LegacyRole --> 作業実行 から、Movementとオペレーションを選択し作業の実行を行います。
1. **作業状態確認**
1. **作業履歴確認**
Ansible-LegacyRole --> 作業管理 から、実行した作業の一覧が表示され履歴が確認できます。
# Ansible-LegacyRole メニュー操作方法説明
本章では、Ansible-LegacyRoleで利用するメニューについて説明します。

## 基本コンソール

## Ansible共通

## Ansible-LegacyRole

#### Movement一覧
1. Movement情報のメンテナンス（閲覧/登録/更新/廃止）を行います。
項目                                | 説明                                                                              | 入力必須  | 入力方法     | 制約事項                                              |
MovementID                          | 登録時に自動採番した36桁の文字列が表示されます。                                  | ー        | 自動入力     | ー                                                    |
Movement名                          | Movementの名称を入力します。                                                      | ○         | 手動入力     | 最大長255バイト                                       |
遅延                                | Movementの実行が指定期間遅延した場合に Ansible-\                  | ー        | 手動入力     | 0～2,147,483,647                                      |
ヘッダー\               | ITAが自動生成する親Playbookの先頭からtasks\                                       | ー        | 手動入力     | 最大長4000バイト                                      |
※1 ヘッダーセクションで「become: yes」を設定した場合
作業対象に以下の設定が必要です。
ログインユーザの sudo権限を NOPASSWD付で :file:/etc/sudoers` に設定します。
-*Demo_user ALL=(ALL) NOPASSWD:ALL**

#### ロールパッケージ管理
1. ユーザが作成したロールパッケージファイル（zip）のメンテナンス（閲覧/登録/更新/廃止）を行います。
ロールパッケージファイルは、「roles」のある階層のディレクトリをzipにて圧縮したものを登録してください。ロールパッケージディレクトリ構成などは「  」を参照してください。
項目                              | 説明                                                                                | 入力必須  | 入力方法     | 制約事項               |
項番                              | 登録時に自動採番した36桁の文字列が表示されます。                                    | －        | 自動入力     | －                     |
ロールパッケージ名                | ITAで管理するロールパッケージ名を入力します。                                       | ○         | 手動入力     | 最大長255バイト        |
アップロードするロールパッケージファイルに含まれるPlaybookファイルは、文字コードが\ |           |              |                        |
ターゲット | Linux                | Linuxで使用可能なPlaybookの場合、「＊」を選択します。                               | －        | リスト選択   | 説明欄記載のとおり。   |
Windows              | Windowsで使用可能なPlaybookの場合、「＊」を選択します。                             | －        | リスト選択   | 説明欄記載のとおり。   |
その他               | Linux、Windows以外の用途で使用可能なPlaybookの場合、Playbookの用途を入力します。    | －        | 手動入力     | 最大長4000バイト       |
説明                              | Playbookについての説明を入力します。                                                | ー        | 手動入力     | 最大長4000バイト       |
説明(en)                          | Playbookについての説明を英語で入力します。                                          | ー        | 手動入力     | 最大長4000バイト       |
**ロールパッケージ内に定義した変数を取り出すタイミング**
内部の処理でロールパッケージ内に定義している変数を抽出します。抽出した変数は、「  」で具体値の登録が可能になります。
抽出のタイミングはリアルタイムではないので、「  」で変数が扱えるまでに **時間がかかる** 場合があります。
Movement単位での変数名の一意管理
Ansible-LegacyRoleでは、変数抜出対象資材から抜出した変数名をMovement単位で一意管理します。
同一ロールパッケージ内でロールを跨って同じ変数名を使用していて、変数構造が異なる場合、 Ansible-LegacyRole --> ロールパッケージ管理 の登録でエラーとなります。
具体的には、通常変数と多段変数や多段変数同士で多段構造が異なる場合、同じ変数名を使用していると登録でエラーとなります。
なお、ロールパッケージが異なる場合は上記の場合でも登録することが可能です。
1            | package_A              | role1        | | VAR_SAMPLE:                                                            | 〇        | | ・変数名が同じ                                                 |
|                                                                          |           | | ・多段変数のメンバー変数の定義が同じ                           |
| |  - { VAR_001: "aaaa" , \VAR_002:\ "bbbb" }                             |           | | ・メンバー変数の記載順序が異なる                               |
2            | package_A              | role1        | | VAR_SAMPLE:                                                            | ×         | | ・変数名が同じ                                                 |
|                                                                          |           | | ・多段変数のメンバー変数の定義が異なる                         |
3             | package_A              | role1        | | VAR_SAMPLE:                                                            | ×         | | ・変数名が同じ                                                 |
|                                                                          |           | | ・通常変数と多段変数が混在している                             |

#### Movement-ロール紐付
1. Movementでインクルードするロールパッケージのメンテナンス（閲覧/登録/更新/廃止）を行います。
- 項目
        - 説明
        - 入力必須
        - 入力方法
        - 制約事項
- 項番
        - | 登録時に自動採番した36桁の文字列が表示されます。
        - ー
        - 自動入力
        - ー
- Movement
        - | Ansible-LegacyRole --> Movement一覧 で登録した  Movement名 が表示されます。
Movementを選択します。
        - 〇
        - リスト選択
        - ー
- ロールパッケージ名:ロール名
        - | Ansible-LegacyRole --> ロールパッケージ管理 で登録した ロールパッケージファイル（ZIP形式） に含まれているロール名が表示されます。
Movementでインクルードするロールパッケージのロールを選択します。
同一Movementに複数のロールパッケージは登録出来ません。
        - 〇
        - リスト選択
        - ー
- インクルード順序
        - | ロールの実行順序（1～）を入力します。
        - 〇
        - 手動入力
        - 1～2,147,483,647
- 備考
        - 自由記述欄です。
        - ー
        - 手動入力
        - 最大長4000バイト

#### 変数ネスト管理
1. Ansible-LegacyRole --> ロールパッケージ管理 で登録した ロールパッケージファイル（ZIP形式） で定義されている多段変数で、繰返配列が定義されているメンバー変数の配列の最大繰返数のメンテナンス（閲覧/更新）を行います。
利用方法については、「  」を参照てください。
- 項目
        - 説明
        - 入力必須
        - 入力方法
        - 制約事項
- 項番
        - | 登録時に自動採番した36桁の文字列が表示されます。
        - ー
        - 自動入力
        - ー
- 最大繰返数
        - | 配列の最大繰返数を1～1,024の範囲で入力します。
最大繰返数の上限値は「管理コンソール - 」より識別ID「MAXIMUM_ITERATION_ANSIBLE-LEGACYROLE」の設定値にて、1～1024の範囲内で変更することが可能です。
        - 〇
        - 手動入力
        - 入力値1～1,024(「」の設定値により変動)
- 備考
        - 自由記述欄です。
        - ー
        - 手動入力
        - 最大長4000バイト
**初期登録および繰返数の更新タイミング**
内部の処理でロールパッケージ内に定義している多段変数繰返配列で定義されているメンバー変数の繰返数を初期登録します。初期登録後、変数ネスト管理で繰返数を更新することが出来ます。
なお、初期登録および繰返数の更新はリアルタイムではないので、「  」で変数が扱えるまでに **時間がかかる** 場合があります。

#### 代入値自動登録設定
1. パラメータシートの項目の設定値とMovementの変数との紐付管理（閲覧/登録/更新/廃止）を行います。
登録した情報は作業実行により Ansible-LegacyRole --> 代入値管理 と Ansible-LegacyRole--> 作業対象ホスト に反映されます。
項目                              | 説明                                                               | 入力必須                                     | 入力方法     | 制約事項                    |
項番                              | 登録時に自動採番した36桁の文字列が表示されます。                   | ー                                           | 自動入力     | ー                          |
パラメータシー\ | メニューグルー\ | パラメータシートの項目が表示されます。                             | ○                                            | リスト選択   | 説明欄記載のとおり。        |
ト（From）      | プ:メニュー:項目|                                                                    |                                              |              |                             |
選択対象となるパラメータシートは\                                  |                                              |              |                             |
パラメータシート作成 --> \                         |                                              |              |                             |
パラメータシート定義・作成 --> 作成対象\                          |                                              |              |                             |
で、パラメータシート（ホスト/オペレーションあり）\                 |                                              |              |                             |
を選択して作成したパラメータシートの項目になります。               |                                              |              |                             |
代入順序        | パラメータシートがバンドルの\                                      |                                |              |                             |
登録方式                          | IaC変数（To） で選択した変数の具体値\             | ○                                            | リスト選択   | 説明欄記載のとおり。        |
に設定する内容を選択します。                                       |                                              |              |                             |
項目の設定値が IaC変数（To） で選択した変数\  |                                              |              |                             |
項目の名称が IaC変数（To） で選択した変数\    |                                              |              |                             |
Movement名                        | Ansible-LegacyRole --> Movement一覧 で登録した\   | ○                                            | リスト選択   | 説明欄記載のとおり。        |
Movement名 が表示されます。                       |                                              |              |                             |
Movementを選択します。                                             |                                              |              |                             |
IaC変数（To）   | Movement名\     | Ansible-LegacyRole --> Movement-ロール紐付 で\    | ○                                            | リスト選択   | 説明欄記載のとおり。        |
:変数名         | 登録した資材で使用している変数が表示されます。                     |                                              |              |                             |
パラメータシート（From） で選択した項目の具体値\  |                                              |              |                             |
を紐付けたい変数を選択します。                                     |                                              |              |                             |
Movement名:変\  | Movement名:変数名 で多段変数を選択した場合に\     |         | リスト選択   | 説明欄記載のとおり。        |
数名:メンバー\  | 多段変数のメンバー変数が表示されます。                             |                                              |              |                             |
変数            |                                                                    |                                              |              |                             |
メンバー変数を選択します。                                         |                                              |              |                             |
代入順序        | 複数具体値が設定できる変数の場合に必須入力になります。             |   | 手動入力     | 1～2,147,483,647            |
NULL連携                          | パラメータシートの具体値が\                                        | ー                                           | リスト選択   | 説明欄記載のとおり。        |
Ansible-LegacyRole --> 代入値管理 に\             |                                              |              |                             |
NULL（空白）の値を登録するかを選択します。                         |                                              |              |                             |
パラメータシートの値がどのような\                              |                                              |              |                             |
値でも Ansible-LegacyRole --> 代入値管理 に\  |                                              |              |                             |
登録が行われます。                                             |                                              |              |                             |
パラメータシートに値が入力\                                    |                                              |              |                             |
理` に登録が行われます。                                       |                                              |              |                             |
※1:パラメータシート（バンドル）を使用する場合のみ必須
パラメータシート（バンドル）のリピート設定されている項目とMovementの変数を紐付ける場合、 Ansible-LegacyRole --> 代入値自動登録設定 でパラメータシート（From） の代入順序を入力する必要があります。
※2:選択した変数が多段変数の場合のみ必須
多段変数の場合にのみメンバー変数の選択が必要になります。メンバー変数に表示される変数は具体値を必要とする変数のみです。
メンバー変数名の表示は各階層の変数を「.」でつないで表示します。
繰返配列の場合は「[ ]」で繰返位置（0～）をつないで表示します。繰返し配列の数は Ansible-LegacyRole --> 変数ネスト管理 で設定を行います。
e.g.） 代入値自動登録設定で選択できるメンバー変数と変数ネスト管理で最大繰返数を更新後に選択できるメンバー変数の確認
1. 下記のようにロールパッケージの変数定義ファイル（defaults/main.yml）に変数を定義して、 Ansible-LegacyRole --> ロールパッケージ管理 でロールパッケージを登録します。
-*変数定義ファイルの記述内容**
           - name: alice
               - craete_dir: /dir
               - craete_pass:
                   - sample_pass: pass1
               - craete_pass:
                   - sample_pass: pass2
                 - craete_users:
                     - prod_user: user1
                     - dev_user: user2
1. 1. のように変数を定義してロールパッケージを登録した場合、 Ansible-LegacyRole --> 変数ネスト管理 には下記のように登録され、 Ansible-LegacyRole --> 代入値自動登録設定 ではデフォルトで下記のメンバー変数が選択できます。
      .. list-table:: 変数ネスト管理の登録内容
- 変数名
           - メンバー変数名
           - 最大繰返数
- VAR_aaaa
           - 0
           - 1
- VAR_aaaa
           - 0.directory
           - 1
- VAR_aaaa
           - 0.password
           - 1
- VAR_aaaa
           - 0.password.sample
           - 1
- VAR_aaaa
           - 0.user.root
           - 1
- VAR_aaaa
           - 0.user.root.dev
           - 1
- VAR_aaaa
           - 0.user.root.prod
           - 1
      .. list-table:: 代入値自動登録設定で選択可能なメンバー変数
- 変数名
           - メンバー変数名
- VAR_aaaa
           - [0].directory[0].create_dir
- VAR_aaaa
           - [0].name
- VAR_aaaa
           - [0].object
- VAR_aaaa
           - [0].password[0].create_pass
- VAR_aaaa
           - [0].password[0].sample[0].sample_pass
- VAR_aaaa
           - [0].user.root[0].create_users
- VAR_aaaa
           - [0].user.root[0].dev[0].dev_user
- VAR_aaaa
           - [0].user.root[0].prod[0].prod_user
1. Ansible-LegacyRole --> 変数ネスト管理 でメンバー変数「0.user.root.prod」の最大繰返数を初期値"1"から"3"に更新します。
      .. list-table:: 変数ネスト管理の更新内容
- 変数名
           - メンバー変数名
           - 最大繰返数
- VAR_aaaa
           - 0.user.root.prod
           - 3
1. 3. のようにメンバー変数を更新した場合、 Ansible-LegacyRole --> 代入値自動登録設定 で選択できるメンバー変数も下記のように更新されます。
（メンバー変数 [0].user.root[0].prod[1].prod_user と [0].user.root[0].prod[2].prod_user がプルダウンに追加されました。）
      .. list-table:: 代入値自動登録設定で選択可能なメンバー変数
- 変数名
           - メンバー変数名
- VAR_aaaa
           - [0].directory[0].create_dir
- VAR_aaaa
           - [0].name
- VAR_aaaa
           - [0].object
- VAR_aaaa
           - [0].password[0].create_pass
- VAR_aaaa
           - [0].password[0].sample[0].sample_pass
- VAR_aaaa
           - [0].user.root[0].create_users
- VAR_aaaa
           - [0].user.root[0].dev[0].dev_user
- VAR_aaaa
           - [0].user.root[0].prod[0].prod_user
- VAR_aaaa
           - [0].user.root[0].prod[1].prod_user
- VAR_aaaa
           - [0].user.root[0].prod[2].prod_user
※3:選択した変数が複数具体値設定可能な変数の場合のみ必須
特定の複数具体値変数に対して代入順序が連続していなくても問題ありません。
e.g.）複数具体値変数に代入順序を入力して作業実行する場合
1. 下記のようにロールパッケージの変数定義ファイル（defaults/main.yml）に変数を定義して、 Ansible-LegacyRole --> ロールパッケージ管理 でロールパッケージを登録します。
-*変数定義ファイルの記述内容**
           - user-name
           - group-name
           - meta-name
           - login
           - authorized
           - space
           - cluster
1. Ansible-LegacyRole --> 代入値自動登録設定 でパラメータシートに登録されている項目の設定値とRole内の変数を紐付けします。
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
多段変数も同様で具体値を登録しているメンバー変数のみとなります。
e.g.） 代入値自動登録設定で具体値を登録した変数と作業実行時にホスト変数ファイルに出力される変数の確認
1. 下記のようにロールパッケージの変数定義ファイル（defaults/main.yml）に変数を定義して、 Ansible-LegacyRole --> ロールパッケージ管理 でロールパッケージを登録します。
-*変数定義ファイルの記述内容**
           - name: alice
                 - craete_users:
                     - prod_user: user1
                     - dev_user: user2
1. Ansible-LegacyRole --> 代入値自動登録設定 でパラメータシートに登録されている項目の設定値とRole内の変数を紐付けします。
       パラメータシートの登録内容
ホスト名       | オペレーション名       | パラメータ          |
      .. list-table:: 代入値自動登録設定の登録内容
- メニュー名
           - 項目
           - 変数名
           - メンバー変数名
- sample-menu
           - 項目1
           - VAR_output
           - [0].name
- sample-menu
           - 項目2
           - VAR_output
           - [0].user.root[0].dev[0].dev_user
1. 作業実行時、ホスト変数ファイル（host_vars/test-host）には、代入値自動登録設定で登録した変数が下記のように出力されます。
-*ホスト変数ファイルへの出力内容**
           - name: value1
               - dev:
                 - dev_user: value2
**ファイル埋込変数とテンプレート埋込変数をPlaybookの変数に紐付して使用する例**
e.g.） ファイル埋込変数 CPF_test とテンプレート埋込変数 TPF_sample を代入値自動登録設定でPlaybookの変数に紐付して使用する場合
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
1. Ansible-LegacyRole --> 代入値自動登録設定 で2. のパラメータシートに登録した項目の設定値とPlaybookの変数を紐付して Ansible-LegacyRole --> 作業実行 で作業実行します。
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
「呼出元Conductor」には、Conductorから実行した場合に、どのConductorから実行されたかを表示します。Ansible-LegacyRoleから直接実行した場合は空欄になります。
1. **作業対象ホスト確認**
1. **代入値確認**
1. **緊急停止/予約取り消し**
1. **実行ログ表示**
Ansible Automation Controllerで実行した場合、作業対象の Ansible共通 --> 機器一覧 の ユーザ ・ パスワード ・ ssh秘密鍵ファイル ・ パスフレーズ ・ 接続タイプ ・ インスタンスグルーブ の項目値でグループ化された作業対象の単位でPlaybookが実行され、ansibleの実行ログが分割されます。
さらに、 Ansible共通 --> インターフェース情報 か Ansible-LegacyRole --> Movement一覧 の オプションパラメータ でジョブスライス数を指定することによりグループ化された作業対象をさらにジョブスライス数で分割しplaybookが実行され、ansibleの実行ログも分割されます。
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
Movement名:変数名:メンバー変数            | 多段変数のメンバー変数が表示されます。                                                                      |
具体値     | 文字列    | Sensitive設定    | 「True」または「False」が表示されます。                                                                     |
値               | 作業実行時の変数の具体値が表示されます。                                                                    |
| + | Sensitive設定 が「True」の場合                                                         |
|   | パラメータシートで入力した具体値は暗号化されITA上では表示されません。\                                  |
|     変数の具体値は、ansible-vaultで暗号化した内容が設定されます。                                           |
| + | Sensitive設定 が「False」の場合                                                        |
|   | パラメータシートで入力した具体値が表示されます。                                                        |
ファイル                     | 作業実行の変数に紐づくファイル名が表示されます。                                                            |
代入順序                                  | 複数具体値変数の場合に、代入順序が表示されます。                                                            |
# 構築コード記述方法

## ロールパッケージの記述
- - | 含めるべきファイル
     - ITAでの取り扱い
- \（1）\　site.yml　\（マスターPlaybook）\
     - △
     - ITAで作成されるため、存在する場合は上書きされます。
- \（2）\　hosts
     - △
     - ITAで作成されるため、存在する場合は上書きされます。
- \（3）\　group_vars
     - △
     - ITAでは扱わないため、存在する場合は削除されます。
- \（4）\　host_vars
     - △
     - ITAで作成されるため、存在する場合は上書きされます。
- \（5）\　ITA readme
     - △
     - | ITA readmeはロール毎に定義します。無くてもエラーにはなりません。
- \（6）\　roles
     - 〇
     - rolesディレクトリが存在しない場合はアップロードでエラーになります。
- \（7）\　roles/[role 名①]
     - 〇
     - | role名ディレクトリが存在しない場合はアップロードでエラーになります。
- \（8）\　roles/[role 名①]/readme.md
     - △
     - ITA は関知しません。
- \（9）\　roles/[role 名①]/tasks
     - 〇
     - | tasksディレクトリは必須です。
- \（10）\　roles/[role 名①]/handlers
     - △
     - | handlersディレクトリの有無は関知しません。
- \（11）\　roles/[role 名①]/templates
     - △
     - | templatesディレクトリの有無は関知しません。
- \（12）\　roles/[role 名①]/files
     - △
     - | filesディレクトリの有無は関知しません。
- \（13）\　roles/[role 名①]/vars
     - △
     - | varsディレクトリの有無は関知しません。
- \（14）\　roles/[role 名①]/defaults
     - △
     - | defaultsディレクトリの有無は関知しません。
- \（15）\　roles/[role 名①]/meta
     - △
     - | metaディレクトリの有無は関知しません。

#### マスターPlaybook
ITAで作成するマスターPlaybookはへッダーセクションとrolesセクションで構成されます。
1. へッダーセクション
ヘッダーセクションは、デフォルト値が決まっていますが、 Ansible-LegacyRole --> Movement一覧 の ヘッダーセクション で変更することが出来ます。
        - hosts: all
1. rolesセクション
アップロードさたロールパッケージ内のロールを、 Ansible-LegacyRole --> Movement-ロール紐付 の インクルード順序 に従いroleで実行します。

#### ロールパッケージ内のロール名をディレクトリ階層にした場合の留意点
1. ロールとして認識するディレクトリは、tasksディレクトリがあるディレクトリになります。
   - parent/sample_role1
   - parent/sample_role2
   - sample_role6
1. tasksディレクトリが複数あるディレクトリ階層の除外

## ITAreadme の記述
Playbook中に直接変数を定義したくない場合など、defaults変数定義ファイルに変数が定義されていない際に、ITA readmeファイルに変数の定義を設定することで、代入値管理機能で変数の値を指定することができます。

#### ITA readmeのファイル名の命名規則
- ロール名
     - 作成するファイル名
- mysql
     - ita_readme_mysql.yml
- mysql/install
     - ita_readme_mysql%install.yml

#### ITA readmeのフォーマット
ITA readmeに定義されている変数の具体値がホスト変数ファイルに出力されるまでの流れを、以降「  」と称します。
また、ITA readmeとdefaults変数定義ファイルで変数定義が重なった場合、ITA readmeの変数構造が適用されます。
ITA readmeとdefaults変数定義ファイルで変数定義が重なった場合など、以下のルールで処理されます。
  .. list-table:: 変数採用ルール
- defaults変数定義ファイル
       - ITA readme
       - 変数構造の適用先
- 定義あり
       - 定義なし
       - デフォルト変数定義ファイル
- 定義なし
       - 定義あり
       - ITA readme
- 定義あり
       - 定義あり
       - ITA readme
ITA readmeに記載した変数と具体値は、ansibleに渡ることはありません。

## 「ita_readme」の活用例
- No.
     - 観点
- 1
     - 外部から取得したAnsible-LegacyRoleを編集せず利用する
- 2
     - 「ita_readme」の役割
- 3
     - 「defaults/main.yml」に記載の変数定義およびデフォルト値について
- 4
     - 「host_varsファイル」と「ITAのパラメータシート」について
- 5
     - 「defaults/main.yml」に追記したい場合の救済処置
- 6
     - playbookにおけるlength評価への応用
- 7
     - playbookにおけるdefined評価への応用
- | **観点１：外部から取得したAnsible-LegacyRoleを編集せず利用する**
そのため「ita_readme」を「roles」ディレクトリの外に置いて、Ansible-LegacyRole（「roles」ディレクトリ）内で使われている変数にパラメータを与えることが可能となっております。
- | **観点２：「ita_readme」の役割について**
「ita_readme」は変数名および変数の型をITAに伝えるための機能です。
言い換えれば、「ita_readme」は変数の具体値（パラメータ）を定義するための機能ではありません（具体値を記載してもITAで認識しません）。
具体値を与える方法を以降の観点で説明します。
- | **観点３：「defaults/main.yml」に記載の変数定義およびデフォルト値について**
変数定義およびデフォルト値はhost_varsで定義されない限り有効となります。（例：『VAR_A：aaa』）
- | **観点４：「host_varsファイル」と「ITAのパラメータシート」について**
host_varsファイルはITAのパラメータシートから実行ごとに自動作成されます。
- | **観点５：「defaults/main.yml」に追記したい場合の救済処置**
Ansible-LegacyRole（「roles」ディレクトリ）に変更を加えたい場合、救済処置として「ita_readme」に変数名および型を記述することが可能です。
既に「defaults/main.yml」に記載がある変数を、改めて「ita_readme」に定義する必要はありません。
もし二つのファイルで同じ変数が定義されている場合は、「ita_readme」側が優位になります。
- | **観点６：playbookにおけるlength評価への応用**
変数に対し具体値があるか否かによって、length評価における条件分岐に活用することが可能です。
例えば、「defaults/main.yml」に『VAR_C:[]』がある状態で、変数「VAR_C」に具体値を与えずに実行した場合length＝0となります。
- | **観点７：playbookにおけるdefined評価への応用**
変数に対し具体値を定義しているか否かによって、defined評価による条件分岐に活用することが可能です。
例えば、「defaults/main.yml」で定義のない変数「VAR_G」と「VAR_H」を、「ita_readme」で定義を記述します。「ita_readme」に記述することで、ITAのパラメータシートで取り扱うことが可能となります。
変数「VAR_G」に具体値を付与せず実行すると、「defaults/main.yml」および「host_vars」に定義されずに動作するためdefined→falseとなります。
反対に、変数「VAR_H」に具体値「kkk」を付与し実行すると、「host_vars」に定義されて動作するためdefined→trueとなります。
# 付録

## Ansible実行時に使用される投入データとITAメニューの紐づけ
ITAの各メニューより情報を抜出してAnsible実行に必要な投入データを作ります。この際、 Ansible共通 --> 機器一覧 の パスワード や Ansible-LegacyRole --> 代入値管理 で Sensitive設定 が「True」に設定されている変数の具体値は、ansible-vaultで暗号化されています。
各種データとITAメニューの関係性は以下の通りです。

#### Ansible-LegacyRole投入データ
- メニューグループ
     - メニュー
     - 項目
     - ディレクトリ解凍時のパス
     - 備考
- Ansible-LegacyRole
     - ロールパッケージ管理
     - ロールパッケージ
     - /roles
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
- Ansible-LegacyRole
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
- Ansible-LegacyRole
     - 代入値管理
     - 変数名/具体値
     - /host_vars
     -
- Ansible-LegacyRole
     - template 管理
     - テンプレート埋込変数
     - /host_vars
     -
- Ansible-LegacyRole
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
     - 機器一覧
     - | winrm公開鍵ファイル
     - /winrm_key_files
     -
- Ansible共通
     - 機器一覧
     - サーバ証明書
     - /winrm_ca_files
     -
- Ansible共通
     - インターフェース情報
     - オプションパラメータ
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible-LegacyRole
     - Movement一覧
     - オプションパラメータ
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible共通
     - 機器一覧
     - | ログインユーザ ID
     - | Ansible共通 --> インターフェース情報 の 実行エンジン が「Ansible Core」「Ansible Automation Controller」の場合
     -
- Ansible-LegacyRole
     - Movement-ロール紐付
     - ロール名・インクルード順序
     - /site.yml
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

#### Ansible-LegacyRole 結果データに保存されるファイル一覧
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
