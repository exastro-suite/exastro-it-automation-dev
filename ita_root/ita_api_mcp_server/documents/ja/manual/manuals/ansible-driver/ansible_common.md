# Ansible共通機能

## Ansible driver概要

### Ansible Core
PF構築自動化ツール。Playbookに処理を記述し、モジュールを使って各種機器を制御します。

### Ansible Automation Controller
Ansibleに管理機能を拡張したプラットフォーム。プロジェクト、インベントリ、認証情報を組み合わせてジョブテンプレートを作成し実行します。

### Ansible Execution Agent
ITAとは独立したAnsible実行専用サーバー。Ansible-builderで実行環境を構築し、Ansible-runnerで実行します。ワークスペース単位に用意し、冗長化構成が可能です。

### Ansible driverの3つのモード

1. **Legacyモード**: Ansible標準機能で設定を投入。構築コードを単体YAMLファイルとして登録
2. **Legacy Roleモード**: 構築コードをパッケージとして登録。Roleの組み合わせで構成
3. **Pioneerモード**: 独自モジュールで対話形式の設定投入が可能。Telnet/SSHでログイン可能な機器に対応

## 変数の種類

### 通常変数
変数名に対して具体値を1つ定義できる変数

### 複数具体値変数
変数名に対して具体値を複数定義できる変数

### 多段変数
階層化された変数。Ansible-LegacyRoleでのみ使用可能

### グローバル変数
`Ansible共通 --> グローバル変数管理`から登録。複数のPlaybookやタスクで共通利用する情報を一元管理

### グローバル変数（センシティブ）
暗号化して保存するグローバル変数。ansible-vaultを通して使用。認証情報やAPIキーなど機微情報の管理に使用

### テンプレート埋込変数
`Ansible共通 --> テンプレート管理`から登録する変数

### ファイル埋込変数
`Ansible共通 --> ファイル管理`から登録する変数

### ITA独自変数

#### 機器一覧の変数
- `__inventory_hostname__`: ホスト名
- `__dnshostname__`: DNSホスト名
- `__ipaddress__`: IPアドレス
- `__loginprotocol__`: プロトコル
- `__loginuser__`: ログインユーザID
- `__loginpassword__`: ログインパスワード

#### Movement ID
- `__movement_id__`: Movement一覧のMovement ID

#### オペレーション
- `__operation__`: オペレーション情報
- `__operation_datetime__`: 実施予定日時
- `__operation_id__`: オペレーションID
- `__operation_name__`: オペレーション名称

#### 作業インスタンスID
- `__execution_no__`: 作業状態確認の作業No.

#### ConductorインスタンスID
- `__conductor_id__`: Conductor作業確認のConductorインスタンスID

#### データ連携
- `__workflowdir__`: 作業ディレクトリパス
- `__conductor_workflowdir__`: Conductor作業ディレクトリパス（Movement間でファイル共有）
- `__movement_status_filepath__`: ステータスファイルパス
- `__parameters_dir_for_epc__`: 作業ディレクトリ（in）の「_parameters」のパス
- `__parameters_file_dir_for_epc__`: 作業ディレクトリ（in）の「_parameters_file」のパス
- `__parameter_dir__`: 作業結果ディレクトリ（out）の「_parameters」のパス
- `__parameters_file_dir__`: 作業結果ディレクトリ（out）の「_parameters_file」のパス

#### オーガナイゼーション管理
- `__organization_id__`: オーガナイゼーションID
- `__workspace_id__`: ワークスペースID
- `__external_url__`: サービス用公開エンドポイント

## 変数抜出対象資材

- **Playbook素材集**: Playbook素材（Legacy）
- **対話ファイル素材集**: 対話ファイル素材（Pioneer）
- **ロールパッケージ管理**: ロールパッケージファイル（LegacyRole）
- **テンプレート管理**: 変数定義（全モード）
- **機器一覧**: インベントリファイル追加オプション（Legacy、LegacyRole）
- **Movement一覧**: ヘッダセクション（Legacy、LegacyRole）
- **パラメータシート**: テンプレート管理選択項目（全モード）

## 主要メニュー

- **機器一覧**: 作業対象機器の管理
- **インターフェース情報**: Ansible実行方式の設定
- **Ansible Automation Platform ノード一覧**: AAPのノード情報管理
- **グローバル変数管理**: 共通変数の一元管理
- **グローバル変数（センシティブ）管理**: 機密情報の暗号化管理
- **ファイル管理**: Playbookで使用するファイル管理
- **テンプレート管理**: テンプレートファイルと変数管理
- **実行環境定義テンプレート管理**: 実行環境のテンプレート管理
- **実行環境管理**: Ansible実行環境の管理
- **エージェント管理**: Ansible Execution Agentの管理
- **管理対象外変数リスト**: 変数抜出対象外とする変数の指定
