# Terraform driver 共通
# はじめに
本書では、「」「」（以下、Terraform driver）における共通の機能について説明します。
# 概要

## Terraformについて
また、Terraform CloudおよびTerraform EnterpriseではPolicy as Codeによるアクセスポリシーをコード化して管理することが可能です。

## Terrform driverについて
Terraform driverはITAの機能として、Teraformへの実行および実行ログの取得を行うことができます。
作業の実行（Plan /Apply）に利用するModuleファイルや、PolicyCheckを行うためのPolicyファイルをITA上で部品化し、再利用できるよう管理することができます。
-  | **Terraform Cloud/EP driver**
ITAで登録した Terraform Cloud もしくは Terraform Enterprise に対し、Organizationの作成、Workspaceの作成、作業の実行（Plan/ PolicyCheck / Apply）および作業ログの取得を行うことができます。
操作方法等については「」を参照してください。
-  | **Terraform CLI driver**
操作方法等については「」を参照してください。
# 変数の取り扱い

## 変数の種類
※設定方法の詳細は、「 -> 」「 -> 」を参照してください。
Moduleファイルの中のVariableブロックに定義した対象を変数として扱えます。
通常変数 | 変数名に対して具体値を定義できる変数です。               |
Module内の変数は HCL（HashiCorp Configuration Language）\|
この場合「xxx」がModuleから変数として抜出されます。      |
また、typeとdefault値を設定することができます。          |
typeとdefaultの設定は必須ではありません。                |

## 変数の抜出および具体値登録
ITAにアップロードされたModule素材から変数を抜出して具体値を登録できます。
抜出した変数の具体値は「 -> 」「 -> 」にて、パラメータシートと連携させることで具体値を登録します。
Terraform Cloud/EP driverでは、登録された変数と具体値は作業実行時に連携先TerraformのWorkspaceで管理するVariablesに対し、「変数名」が「Key」、「具体値」が「Value」として登録されます。
Terraform CLI driverでは、登録された変数と具体値は、作業実行時に生成されるterraform.tfvarsファイルに「変数名」が「Key」、「具体値」が「Value」として記載され、作業実行で使用されます。

## 変数のタイプについて
変数内でtypeを設定することができます。
Module内の変数は HCL（HashiCorp ConfigurationLanguage）の変数ルールに従い記述してください。
ITA内で扱う変数は以下の通りです。
.. list-table:: 変数タイプ
- type
     - 詳細
     - | メンバー変数対象
     - | 代入順序対象
     - typeの記述例
     - defaultの記述例
- string
     - 文字列型。
     - ×
     - ×
     - string
     - あいう
- number
     - 数字型。
     - ×
     - ×
     - number
     - 123
- bool
     - Boolean型（trueまたはfalse）。
     - ×
     - ×
     - bool
     - true
- list
     - 配列型。
     - ×
     - 〇
     - list(string)
     - ["あ", "い", "う"]
- set
     - | 配列型。ユニークな値の設定が求められる。
     - ×
     - 〇
     - set(number)
     - [1, 2, 3]
- tuple
     - | 配列型。予めn番目にどのtypeを設定するか決めておく必要があります。
値の入力数が決められているため、ITシステムA上ではメンバー変数としてプルダウンで選択します。
     - 〇
     - ×
     - tuple([string, number])
     - ["あいう", 2023]
- map
     - | key-value（連想配列）型。ITA上ではmap型が一つ以上含まれているtypeを設定した場合、type情報からkey値を特定できないため、代入値自動登録設定をする場合はHCL設定をONする必要があります。
HCL設定については「」を参照してください。
     - ×
     - ×
     - map(string)
     - {"test_key" = "test_value"}
- object
     - | key-value（連想配列）型。ITA上ではkey名をメンバー変数として扱います。key名に日本語は含まないでください。
     - 〇
     - ×
     - object({test_key = string})
     - {"test_key" = "test_value"}
- any
     - すべてに適合する型ですが、ITA上ではstring型と同じ扱いになります。
     - ×
     - ×
     - any
     - あいう
- 記載なし
     - typeを記載しなかった場合、ITA上では string型と同じ扱いになります。
     - ×
     - ×
     -
     - あいう
-  | **※1 …メンバー変数対象**
変数がkey-value型である場合のkey名です。
変数のタイプがobjectの場合、<KEY> = <TYPE> の <KEY> をメンバー変数とします。
変数のタイプがtupleの場合、tuple内に定義した変数を先頭から[0],[1],[2]…と採番してメンバー変数となります。
変数のタイプが変数ネスト管理メニューの登録対象の場合、最大繰返数をもとに[0],[1],[2]…と採番してメンバー変数となります。
変数ネストに関しては「 -> 」「 -> 」を参照してください。
      - | **例: 変数タイプがobjectの場合**
1. tfファイルと登録値
1. 代入値例(代入値自動登録設定)
- 項番
              - 変数名
              - メンバー変数
              - 代入順序
              - パラメータシートの入力値
- 1
              -  VAR_hoge
              -  NAME
              -  入力不可
              -  my_machine
- 2
              - VAR_hoge
              - IP
              - 入力不可
              - 192.168.100.1
1. Terraformに送信される値
      -  | **例: 変数のタイプがtupleの場合**
1. tfファイルと登録値
1. 代入値例(代入値自動登録設定)
- 項番
              - 変数名
              - メンバー変数
              - 代入順序
              - パラメータシートの入力値
- 1
              -  VAR_hoge
              -  [0]
              -  入力不可
              -  def
- 2
              -  VAR_hoge
              -  [1]
              -  入力不可
              -  2024
1. Terraformに送信される値
      -  | **例: 変数のタイプがネスト管理対象の場合**
1. tfファイルと登録値
1. 代入値例(代入値自動登録設定)
- 項番
              - 変数名
              - メンバー変数
              - 代入順序
              - パラメータシートの入力値
- 1
              -  VAR_hoge
              -  [0]
              -  1
              -  あああ
- 2
              -  VAR_hoge
              -  [0]
              -  2
              -  いいい
- 3
              - VAR_hoge
              - [1]
              - 1
              - ううう
- 4
              - VAR_hoge
              - [1]
              - 2
              - えええ
1. Terraformに送信される値
-  | **※2 …代入順序対象**
変数に複数具体値を設定する際の先頭から代入する順序です。
変数または階層構造の変数の最下層の変数のタイプがlist,setの場合、「 -> 」「 -> 」にて設定可能です。
      -  | **例: 変数タイプがlistの場合**
1. tfファイルと登録値
1. 代入値例(代入値自動登録設定)
- 項番
              - 変数名
              - メンバー変数
              - 代入順序
              - パラメータシートの入力値
- 1
              -  VAR_hoge
              -  入力不要
              -  1
              -  あいう
- 2
              - VAR_hoge
              - 入力不要
              - 2
              - かきく
1. Terraformに送信される値
      -  | **例: 階層構造の変数の最下層の変数タイプがsetの場合**
1. tfファイルと登録値
1. 代入値例(代入値自動登録設定)
- 項番
              - 変数名
              - メンバー変数
              - 代入順序
              - パラメータシートの入力値
- 1
              -  VAR_hoge
              -  key
              -  1
              -  1
- 2
              - VAR_hoge
              - key
              - 2
              - 2
1. Terraformに送信される値
# 構築コード記述方法
Policyについては Terraform Cloud/EP driver のみ有効な機能です。

## Moduleの記述

## Policyの記述
# 付録

## Module素材「Variableブロック」記入例・登録例
Module素材の「Variableブロック」の記入例と、代入値自動登録設定への登録例を、変数のタイプ毎に記載します。
1. **シンプルなパターン**
1. string型
1. number型
1. bool型
1. list型
1. set型
1. tuple型
1. map型
1. object型
1. any型
1. typeの記載がない
1. **複雑なパターン**
1. list型の中にlist型
1. list型の中にobject型
1. object型の中のlist型の中にobject型
1. **特殊なパターン**
1. list型の中にmap型

## 変数ネスト管理フロー例
変数ネスト管理の操作例を記載します。
1. **最大繰返数を増加させる**
1. **最大繰返数を減少させる**
