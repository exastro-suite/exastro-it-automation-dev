#   Copyright 2024 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# ジョブ機能ユーザーID
ANSIBLE_LEGACY_VARS_LISTUP_USER_ID = "20201"  # Ansible Legacy 変数抽出機能
ANSIBLE_PIONEER_VARS_LISTUP_USER_ID = "20301"  # Ansible Pioneer 変数抽出機能
ANSIBLE_LEGACY_ROLE_VARS_LISTUP_USER_ID = "20401"  # Ansible Legacy Role 変数抽出機能
MENU_CREATE_USER_ID = "50101"  # パラメータシート作成機能ユーザーID

# パラメータシート作成機能ステータス
MENU_CREATE_UNEXEC = "1"  # 未実行/Unexecuted
MENU_CREATE_EXEC = "2"  # 実行中/Executing
MENU_CREATE_COMP = "3"  # 完了/Completed
MENU_CREATE_ERR = "4"  # 完了(異常)/Completed(error)

# T_COMN_PROC_LOADED_LIST ROW_ID
PROC_LOADED_ID_ANSIBLE_LEGACY = "202"
PROC_LOADED_ID_ANSIBLE_PIONEER = "203"
PROC_LOADED_ID_ANSIBLE_LEGACY_ROLE = "204"
PROC_LOADED_ID_CMDB_MENU_ANALYSIS = "501"
PROC_LOADED_ID_TERRAFORM_CLOUD_EP = "801"
PROC_LOADED_ID_TERRAFORM_CLI = "901"
