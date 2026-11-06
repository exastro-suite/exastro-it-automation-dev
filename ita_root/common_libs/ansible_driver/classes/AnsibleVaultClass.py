# Copyright 2022 NEC Corporation#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import subprocess
from common_libs.ansible_driver.functions.util import *   # noqa: F403
from common_libs.common import *  # noqa: F403

"""
  ansible vault関連モジュール
"""


class AnsibleVault:
    """
      ansible vault関連クラス
    """
    def CreateVaultPasswordFilePath(self, ansiblePlaybookVaultPath=False):
        """
          ansible-vaultパスワードファイルパス生成
          Arguments:
            ansiblePlaybookVaultPath: ansible-playbookコマンドのansible-vaultパスワードファイルパス生成判定
          Returns:
            ansible-vaultパスワードファイルパス
        """
        if ansiblePlaybookVaultPath is False:
            VaultPasswordFilePath = "{}/.vault_{}".format(get_OSTmpPath(), os.getpid())  # noqa: F405
            # /tmpに作成したファイルはゴミ掃除リストに追加
            addAnsibleCreateFilesPath(VaultPasswordFilePath)  # noqa: F405
        else:
            VaultPasswordFilePath = "{}/.tmp/.tmpkey".format(ansiblePlaybookVaultPath)
        return VaultPasswordFilePath

    def CreateVaultPasswordFile(self, VaultPasswordFilePath, vaultPassword):
        """
          ansible-vaultパスワードファイル生成
          Arguments:
            VaultPasswordFilePath: ansible-vaultパスワードファイルパス
            vaultPassword: ansible-vaultパスワード(エンコード文字列)
          Returns:
            True
        """
        self.VaultPasswordFilePath = VaultPasswordFilePath
        #  #2079 /storage配下は使用していないので対象外
        fd = open(VaultPasswordFilePath, 'w')
        fd.write(ky_decrypt(vaultPassword))  # noqa: F405
        fd.close()
        return True

    def RemoveVaultPasswordFile(self):
        """
          ansible-vaultパスワードファイル削除
          Arguments:
            なし
          Returns:
            なし
        """
        retry_remove(self.VaultPasswordFilePath)  # noqa: F405

    def Vault(self, ansible_path, password_file, value, indento, engine_virtualenv_path, passwdFileDel=True):
        """
          ansible-vaultで指定文字列を暗号化
          Arguments:
            ansible_path:           ansible-coreインストール先パス
            password_file:          ansible-vaultパスワードファイルパス
            value:                  暗号化したい文字列
            indento:                暗号化された文字列に付与するインデント
            engine_virtualenv_path: 仮想環境パス(非コンテナ環境用)
            passwdFileDel:          ansible-vaultパスワードファイルの削除有無
          Returns:
            True/False, mt_encode_value: 暗号化された文字列
        """
        result = True
        mt_encode_value = ""

        strExecshellTemplateName = "{}/{}".format(get_AnsibleDriverShellPath(), "ky_ansible_vault_command_shell_template.sh")  # noqa: F405

        strExecshellName = "{}/ansible_vault_execute_shell_{}.sh".format(get_OSTmpPath(), os.getpid())  # noqa: F405
        # /tmpに作成したファイルはゴミ掃除リストに追加
        addAnsibleCreateFilesPath(strExecshellName)  # noqa: F405

        if engine_virtualenv_path:
            virtualenv_flg = "__define__"
            engine_virtualenv_path += "/bin/activate"
            ansible_path = ""
        else:
            virtualenv_flg = "__undefine__"
            engine_virtualenv_path = "__undefine__"
        # CR+LFをLFに置換
        value = value.replace("\r\n", "\n")

        # ansibel-vault パスワードファイル生成
        vault_value_file = "{}/ansible_vault_value_{}".format(get_OSTmpPath(), os.getpid())  # noqa: F405
        # /tmpに作成したファイルはゴミ掃除リストに追加
        addAnsibleCreateFilesPath(vault_value_file)  # noqa: F405
        # #2079 /storage配下ではないので対象外
        fd = open(vault_value_file, 'w')
        fd.write(value)
        fd.close()

        # ansibleインストールバスが設定されている場合に/を追加
        if ansible_path:
            ansible_path += "/"

        # ansible-vault commad 生成
        VaultCmd = "cat {} | {}ansible-vault encrypt --vault-password-file {}".format(vault_value_file, ansible_path, password_file)

        # sshAgentの設定とPlaybookを実行するshellのテンプレートを読み込み
        #  #2079 /storage配下ではないので対象外
        fd = open(strExecshellTemplateName, 'r')
        strShell = fd.read()
        fd.close()

        # テンプレート内の変数を実値に置き換え
        strShell = strShell.replace('<<ansible_valut_command>>', VaultCmd)
        strShell = strShell.replace('<<virtualenv_path>>', engine_virtualenv_path)

        # ansible-vaultshell作成
        #  #2079 /storage配下ではないので対象外
        fd = open(strExecshellName, 'w')
        fd.write(strShell)
        fd.close()

        # パーミッション設定
        retry_chmod(strExecshellName, 0o777)  # noqa: F405
        # Ansible_vault実行Commnad発行
        cmd = [strExecshellName, virtualenv_flg]

        # text=Trueはpython3.6にないので未使用
        try:
            ret = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError as e:
            # shell=True時と同様にコマンド起動失敗をエラー結果として扱う
            ret = subprocess.CompletedProcess(cmd, 126, b"", str(e).encode())

        # 一時ファイル削除

        retry_remove(vault_value_file)  # noqa: F405
        retry_remove(strExecshellName)  # noqa: F405

        if passwdFileDel is True:
            self.RemoveVaultPasswordFile()

        # 結果判定
        if ret.returncode != 0:
            # エラー情報退避
            indento = ""
            mt_encode_value = to_str(ret.stderr)  # noqa: F405
        else:
            # 暗号化文字列取得
            output = to_str(ret.stdout)   # noqa: F405
            arry_list = output.split("\n")

            # 暗号化文字列加工
            for line in arry_list:
                if line.strip() == 0:
                    continue
                if mt_encode_value.strip() != 0:
                    mt_encode_value += "\n"
                # インデント設定
                mt_encode_value += indento + line

        if ret.returncode != 0:
            result = False
        return result, mt_encode_value

    def setValutPasswdIndento(self, val, indento):
        """
          ansible-vaulで暗号化された文字列に所定のインデントを付加
          Arguments:
            val: 暗号化された文字列
            indento: 所定のインデント文字列
          Returns:
            暗号化された文字列に所定のインデントを付加した文字列
        """
        edit_val = ""
        array_list = val.split("\n")
        for line in array_list:
            if edit_val == "":
                edit_val = line
            else:
                edit_val += "\n" + indento + line
        return edit_val
