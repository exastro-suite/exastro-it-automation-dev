# Ansible実行環境のカスタマイズ
# はじめに
本書では、ITAで使用するAnsible実行環境のカスタマイズ方法を説明します。
# Ansible 実行環境カスタマイズの概要
- | Ansible-Coreでのカスタマイズ例
  - | Ansible作業時のビルドにカスタマイズ工程を追加する例（docker-compose版のみ）
    - | コレクションを使用する例
    - | 自作モジュールを使用する例
  - | Ansible作業時にカスタマイズを施したイメージを使用する例
- | Ansible Execution AgentやAnsible Automation Platformでのカスタマイズ例
  - | コレクションを使用する例（無償版ベースイメージ）
  - | コレクションを使用する例（有償版ベースイメージ）
  - | 自作モジュールを使用する例
# Ansible-Coreでのカスタマイズ例

## Ansible作業時のビルドにカスタマイズ工程を追加する例
Ansible作業時のビルドにカスタマイズ工程を追加するという手順の関係上、本手順は「docker-compose版のみ」となります。

### 既存の環境変数を確認
既存の環境変数を確認します。

### 既存のイメージを削除

### ビルドファイルの編集

#### コレクションを使用する例
そのため下記以外のコレクションを追加する場合、及びコレクションに必要なライブラリをインストール場合の手順となります。
   ---------------------------------------- -------

#### 自作モジュールを使用する例
   -rw-r--r--. 1 user01 user01 1024 Jan 1 00:00 ~/exastro-docker-compose/ita_by_ansible_execute/templates/work/my_module.py

## Ansible作業時にカスタマイズを施したイメージを使用する例

### カスタマイズを施したイメージの出力

### カスタマイズを施したイメージの投入

#### docker-compose版
イメージの確認後、Ansible-CoreでのAnsible作業時に対象のイメージを使用するように環境変数を設定します。
   - # ANSIBLE_AGENT_IMAGE=my-exastro-ansible-agent
   - # ANSIBLE_AGENT_IMAGE_TAG=
環境変数の編集後、「`~/exastro-docker-compose/setup.sh` 」を実行して編集を反映します。

#### Kubenetes版
イメージの投入後、Ansible-CoreでのAnsible作業時に対象のイメージを使用するように環境変数を設定します。
   -     ANSIBLE_AGENT_IMAGE: "docker.io/exastro/exastro-it-automation-by-ansible-agent"
   -     ANSIBLE_AGENT_IMAGE_TAG: ""
# Ansible Execution Agentでのカスタマイズ例

## コレクションを使用する例（無償版ベースイメージ）
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.access.redhat.com/ubi9/ubi-init:latest」を使用する
  - | コレクションは「Azure.AzCollection」を使用する

### ITAでの実行環境定義登録
Ansible共通 --> 実行環境定義テンプレート管理 に実行環境定義のテンプレートファイルを登録します。
  Ansible共通 --> 実行環境定義テンプレート管理 に設定するパラメータ一覧
項目名                                      | 設定値                                                                                 | 備考                                                                                     |
テンプレートファイル                        | 下記内容を登録します。                                                                 | 将来的に、必要となる `ansible_core` のバージョンは変更となる可能性があります。           |
Ansible共通 --> 実行環境管理 に実行環境定義のテンプレートファイルとテンプレートファイルに代入する設定値の紐付けを登録します。
  Ansible共通 --> 実行環境管理 に設定するパラメータ一覧
項目名                      | 設定値                                  | 備考                                                                              |
実行環境構築方法            | ITA                                     | ー                                                                                |
実行環境定義名              | 実行環境パラメータ定義/~[Exastro standa\| 初期データとして用意されているものを使用します。                                  |
テンプレート名              | azure_ee_template                       | Ansible共通 --> 実行環境定義テンプレート管理 のテンプレート名    |
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | azure_ee_ubi9                                                               | Ansible共通 --> 実行環境管理 の実行環境名  |
ansible-\ | ansible-builderで実行環境をbuildする際に\                                   | 通常は設定不要です。                                        |
builder\  | ansible-builderのパラメータが必要であれば入力します。                       |                                                             |

## コレクションを使用する例（有償版ベースイメージ）
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest」を使用する
  - | コレクションは「Azure.AzCollection」を使用する

### Ansible Execution Agentでの事前準備

### ITAでの実行環境定義登録
入力用 --> 実行環境パラメータ定義 に実行環境定義のテンプレートファイルに代入する設定値を登録します。
  入力用 --> 実行環境パラメータ定義 に設定するパラメータ一覧
項目名                                      | 設定値                                                                     | 備考                                                                                     |
bindep_file                                 | 下記内容を登録します。                                                     | ー                                                                                       |
Ansible共通 --> 実行環境定義テンプレート管理 に実行環境定義のテンプレートファイルを登録します。
  Ansible共通 --> 実行環境定義テンプレート管理 に設定するパラメータ一覧
項目名                                      | 設定値                                                                                 | 備考                                                                                     |
テンプレートファイル                        | 下記内容を登録します。                                                                 | 将来的に、必要となる `ansible_core` のバージョンは変更となる可能性があります。           |
Ansible共通 --> 実行環境管理 に実行環境定義のテンプレートファイルとテンプレートファイルに代入する設定値の紐付けを登録します。
  Ansible共通 --> 実行環境管理 に設定するパラメータ一覧
項目名                      | 設定値                                  | 備考                                                                              |
実行環境構築方法            | ITA                                     | ー                                                                                |
実行環境定義名              | 実行環境パラメータ定義/azure_ee         |  入力用 --> 実行環境パラメータ定義 のexecution_environment_name  |
テンプレート名              | azure_ee_template                       |  Ansible共通 --> 実行環境定義テンプレート管理 のテンプレート名   |
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | azure_ee                                                                    | Ansible共通 --> 実行環境管理 の実行環境名  |
ansible-\ | ansible-builderで実行環境をbuildする際に\                                   | 通常は設定不要です。                                        |
builder\  | ansible-builderのパラメータが必要であれば入力します。                       |                                                             |

## 自作モジュールを使用する例
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.access.redhat.com/ubi9/ubi-init:latest」を使用する
  - | 自作モジュールは「 `/tmp/ansible_module/my_module.py` 」を使用する

### 自作モジュールの配置
   -rw-r--r--. 1 userA userA 1024 Jan 1 00:00 /tmp/ansible_module/my_module.py

### ITAでの実行環境定義登録
Ansible共通 --> 実行環境定義テンプレート管理 に実行環境定義のテンプレートファイルを登録します。
  Ansible共通 --> 実行環境定義テンプレート管理 に設定するパラメータ一覧
項目名                                      | 設定値                                                                                      | 備考                                                                                     |
テンプレートファイル                        | 下記内容を登録します。                                                                      | 自作モジュールのファイルパスが異なる場合は、\                                            |
Ansible共通 --> 実行環境管理 に実行環境定義のテンプレートファイルとテンプレートファイルに代入する設定値の紐付けを登録します。
  Ansible共通 --> 実行環境管理 に設定するパラメータ一覧
項目名                      | 設定値                                                                           | 備考                                                                              |
実行環境構築方法            | ITA                                                                              | ー                                                                                |
実行環境定義名              | 実行環境パラメータ定義/~[Exastro standard] default (no galaxy collection)        |  初期データとして用意されているものを使用します。                                 |
テンプレート名              | my_module_ubi9_template                                                          |  Ansible共通 --> 実行環境定義テンプレート管理 のテンプレート名   |
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | my_module_ubi9                                                              | Ansible共通 --> 実行環境管理 の実行環境名  |
ansible-\ | ansible-builderで実行環境をbuildする際に\                                   | 通常は設定不要です。                                        |
builder\  | ansible-builderのパラメータが必要であれば入力します。                       |                                                             |
# Ansible Automation Platformでのカスタマイズ例

## コレクションを使用する例（無償版ベースイメージ）
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.access.redhat.com/ubi9/ubi-init:latest」を使用する
  - | コレクションは「Azure.AzCollection」を使用する

### ansible-builderのインストール

### 必要ファイルの準備
- | execution-environment.yml
  - ansible-builderの定義ファイル
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | galaxy-requirements.yml
  - インストールしたいansible-galaxy コレクションリストを記載するファイル
     - azure.azcollection
- | python-requirements.txt
  - Python の依存関係を解決するためにPython 要件を記載するファイル
- | bindep.txt
  - システムレベルの依存関係を解決するためにパッケージ要件を記載するファイル

### ansible-builderの実行

### ControlNodeのawxユーザ用にカスタムイメージをコピー

### ExecutionNodeのawxユーザ用にカスタムイメージをコピー

### AAPに実行環境を登録
コピーしたカスタムイメージを使用する実行環境設定をAnsible Automation Platformに登録します。

### ITAに実行環境を登録
ITAに実行環境設定を登録します。
登録する環境名は、AAPで登録した名前（上記ではazure_ee_ubi9）となります。
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | e.g.) azure_ee_ubi9                                                         | AAPに実行環境を登録 で登録した実行環境名   |

## コレクションを使用する例（有償版ベースイメージ）
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest」を使用する
  - | コレクションは「Azure.AzCollection」を使用する

### ansible-builderのインストール

### 必要ファイルの準備
- | execution-environment.yml
  - ansible-builderの定義ファイル
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | galaxy-requirements.yml
  - インストールしたいansible-galaxy コレクションリストを記載するファイル
     - azure.azcollection
- | python-requirements.txt
  - Python の依存関係を解決するためにPython 要件を記載するファイル
- | bindep.txt
  - システムレベルの依存関係を解決するためにパッケージ要件を記載するファイル

### ansible-builderの実行

### ControlNodeのawxユーザ用にカスタムイメージをコピー

### ExecutionNodeのawxユーザ用にカスタムイメージをコピー

### AAPに実行環境を登録
コピーしたカスタムイメージを使用する実行環境設定をAnsible Automation Platformに登録します。

### ITAに実行環境を登録
ITAに実行環境設定を登録します。
登録する環境名は、AAPで登録した名前（上記ではazure_ee）となります。
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | e.g.) azure_ee                                                              | AAPに実行環境を登録 で登録した実行環境名   |

## 自作モジュールを使用する例
- | このケースでは下記条件でカスタマイズを施します。
  - | ベースイメージは「registry.access.redhat.com/ubi9/ubi-init:latest」を使用する
  - | 自作モジュールは「 `/tmp/ansible_module/my_module.py` 」を使用する

### 自作モジュールの配置
   -rw-r--r--. 1 root root 1024 Jan 1 00:00 /tmp/ansible_module/my_module.py

### ansible-builderのインストール

### 必要ファイルの準備
- | execution-environment.yml
  - ansible-builderの定義ファイル
     - src: /tmp/ansible_module/my_module.py
       - COPY _build/configs/my_module.py /usr/share/ansible/plugins/modules/
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | python-requirements.txt
  - Python の依存関係を解決するためにPython 要件を記載するファイル
- | bindep.txt
  - システムレベルの依存関係を解決するためにパッケージ要件を記載するファイル

### ansible-builderの実行

### ControlNodeのawxユーザ用にカスタムイメージをコピー

### ExecutionNodeのawxユーザ用にカスタムイメージをコピー

### AAPに実行環境を登録
コピーしたカスタムイメージを使用する実行環境設定をAnsible Automation Platformに登録します。

### ITAに実行環境を登録
ITAに実行環境設定を登録します。
登録する環境名は、AAPで登録した名前（上記ではmy_module_ubi9_image）となります。
Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 （実行しようとするAnsible作業のMovement）に実行環境設定を登録します。
実行環境設定に関連しないパラメータについては記載省略としています。
  Ansible[Legacy/Pioneer/Legacy-Role] --> Movement一覧 に設定するパラメータ一覧
項目名                              | 設定値                                                                      | 備考                                                        |
MovementID                          | （記載省略）                                                                | ー                                                          |
Movement名                          | （記載省略）                                                                | ー                                                          |
オプションパラメータ    | （記載省略）                                                                | ー                                                          |
Ansible \   | 実行環境  | e.g.) my_module_ubi9_image                                                  | AAPに実行環境を登録 で登録した実行環境名   |
