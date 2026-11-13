#   Copyright 2026 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License")
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
"""
AnsibleVaultClass.AnsibleVault.Vault のテスト

Vault() は「シェルテンプレートから実行シェルを生成 → subprocess で実行 → 結果を整形」する。
ここでは実際のテンプレート(common_libs/ansible_driver/shells/ky_ansible_vault_command_shell_template.sh)
と subprocess をそのまま使い、ansible-vault コマンドだけをスタブに差し替えて検証する。

  - TestVault                : Vault() 本体（正常系 / 異常系 / 一時ファイル削除 / subprocess 呼び出し方）
  - TestVaultCallers         : CreateAnsibleExecFiles の呼び出し元4メソッドが Vault() に渡す引数
                               （CreateAnsibleExecFiles の import に dictknife が必要。未導入の場合は skip）
  - TestVaultRealAnsibleVault: 本物の ansible-vault で暗号化→復号できること
                               （ansible-vault が無い環境では skip）
"""
import inspect
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import common_libs.ansible_driver.classes.AnsibleVaultClass as vault_module
from common_libs.ansible_driver.classes.AnsibleVaultClass import AnsibleVault

# テスト対象モジュール(common_libs/ansible_driver/classes/AnsibleVaultClass.py)から見たシェル格納ディレクトリ
# テストファイルの位置や環境変数 PYTHONPATH はコンテナ内外で異なるため、import したモジュールの位置を基準にする
SHELLS_DIR = Path(os.path.abspath(vault_module.__file__)).parent.parent / "shells"

# スタブの ansible-vault が標準出力に返す暗号化文字列
STUB_VAULT_OUTPUT = "$ANSIBLE_VAULT;1.1;AES256\n6162636465\n3031323334\n"

# 引数・標準入力を記録し、STUB_VAULT_RC が 0 以外なら標準エラーに出力して異常終了する
STUB_ANSIBLE_VAULT = """#!/bin/bash
printf '%s\\n' "$@" > "$STUB_RECORD_DIR/argv"
cat > "$STUB_RECORD_DIR/stdin"
if [ "${STUB_VAULT_RC:-0}" != "0" ]; then
    echo "ERROR! stub failure" >&2
    exit "$STUB_VAULT_RC"
fi
printf '$ANSIBLE_VAULT;1.1;AES256\\n6162636465\\n3031323334\\n'
"""


def _write_executable(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(0o755)
    return path


@pytest.fixture
def vault_env(tmp_path, mock_g, monkeypatch):
    """
    Vault() を実行するための環境を tmp_path 配下に用意する。

      tmp/     : get_OSTmpPath() の差し替え先（実行シェル・値ファイルの作成先）
      stub/    : スタブの ansible-vault（PATH には追加しない。必要なテストで add_path() する）
      record/  : スタブが受け取った引数・標準入力の記録先
      .vault_pw: ansible-vault パスワードファイル
    """
    tmp_dir = tmp_path / "tmp"
    tmp_dir.mkdir()
    record_dir = tmp_path / "record"
    record_dir.mkdir()
    stub_dir = tmp_path / "stub"
    _write_executable(stub_dir / "ansible-vault", STUB_ANSIBLE_VAULT)
    password_file = tmp_path / ".vault_pw"
    password_file.write_text("test_vault_password")

    # get_AnsibleDriverShellPath() は環境変数 PYTHONPATH を基準にするため、テスト対象モジュールの位置に差し替える
    assert (SHELLS_DIR / "ky_ansible_vault_command_shell_template.sh").is_file(), SHELLS_DIR
    monkeypatch.setattr(vault_module, "get_AnsibleDriverShellPath", lambda: str(SHELLS_DIR))
    monkeypatch.setenv("STUB_RECORD_DIR", str(record_dir))
    monkeypatch.delenv("STUB_VAULT_RC", raising=False)
    monkeypatch.setattr(vault_module, "get_OSTmpPath", lambda: str(tmp_dir))
    # addAnsibleCreateFilesPath() のゴミ掃除リスト
    mock_g.AnsibleCreateFilesPath = str(tmp_path / "cleanup_list")

    class Env:
        pass

    env = Env()
    env.tmp_dir = tmp_dir
    env.record_dir = record_dir
    env.stub_dir = stub_dir
    env.password_file = password_file
    env.add_path = lambda: monkeypatch.setenv("PATH", "{}:{}".format(stub_dir, os.environ["PATH"]))
    env.shell_file = tmp_dir / "ansible_vault_execute_shell_{}.sh".format(os.getpid())
    env.value_file = tmp_dir / "ansible_vault_value_{}".format(os.getpid())
    return env


def _vault(env, value="secret", indento="", ansible_path="", engine_virtualenv_path="", passwdFileDel=False):
    obj = AnsibleVault()
    # CreateVaultPasswordFile() を通さない場合も RemoveVaultPasswordFile() が動くように設定
    obj.VaultPasswordFilePath = str(env.password_file)
    return obj.Vault(ansible_path, str(env.password_file), value, indento, engine_virtualenv_path, passwdFileDel)


class TestVault:
    """AnsibleVault.Vault のテスト"""

    def test_signature_has_no_exec_user(self):
        """
        正常系: exec_user 引数が削除されていること
        期待値: 引数は ansible_path, password_file, value, indento, engine_virtualenv_path, passwdFileDel
        """
        params = list(inspect.signature(AnsibleVault.Vault).parameters)
        assert params == ["self", "ansible_path", "password_file", "value", "indento",
                          "engine_virtualenv_path", "passwdFileDel"]

    def test_vault_success_output_format(self, vault_env):
        """
        正常系: ansible-vault の出力を整形して返す
        期待値: 各行(先頭行含む)の前に改行が付く。
                呼び出し元で " !vault |" に連結して YAML のブロックスカラーにするため、先頭の改行は必須
        """
        vault_env.add_path()

        result, value = _vault(vault_env)

        assert result is True
        assert value == "\n" + STUB_VAULT_OUTPUT
        assert value.startswith("\n$ANSIBLE_VAULT;1.1;AES256\n")

    def test_vault_success_with_indento(self, vault_env):
        """
        正常系: indento を指定した場合
        期待値: 各行の先頭に indento が付く
        """
        vault_env.add_path()

        result, value = _vault(vault_env, indento="    ")

        assert result is True
        assert value == "\n    $ANSIBLE_VAULT;1.1;AES256\n    6162636465\n    3031323334\n    "

    def test_vault_passes_value_and_password_file(self, vault_env):
        """
        正常系: ansible-vault に渡す引数と標準入力
        期待値: encrypt --vault-password-file <password_file> が渡り、
                暗号化対象の値は標準入力から CR+LF を LF に変換して渡る
        """
        vault_env.add_path()

        result, _ = _vault(vault_env, value="line1\r\nline2")

        assert result is True
        argv = (vault_env.record_dir / "argv").read_text().splitlines()
        assert argv == ["encrypt", "--vault-password-file", str(vault_env.password_file)]
        assert (vault_env.record_dir / "stdin").read_text() == "line1\nline2"

    def test_vault_with_ansible_path(self, vault_env):
        """
        正常系: ansible_path を指定した場合
        期待値: PATH 上に無くても <ansible_path>/ansible-vault が実行される
        """
        result, value = _vault(vault_env, ansible_path=str(vault_env.stub_dir))

        assert result is True
        assert value == "\n" + STUB_VAULT_OUTPUT

    def test_vault_with_engine_virtualenv_path(self, vault_env, tmp_path):
        """
        正常系: engine_virtualenv_path を指定した場合
        期待値: <engine_virtualenv_path>/bin/activate を source してから ansible-vault を実行する。
                ansible_path は無視される
        """
        venv_dir = tmp_path / "venv"
        (venv_dir / "bin").mkdir(parents=True)
        (venv_dir / "bin" / "activate").write_text('export PATH="{}:$PATH"\n'.format(vault_env.stub_dir))

        result, value = _vault(vault_env, ansible_path="/nonexistent", engine_virtualenv_path=str(venv_dir))

        assert result is True
        assert value == "\n" + STUB_VAULT_OUTPUT

    def test_vault_ansible_vault_failed(self, vault_env, monkeypatch):
        """
        異常系: ansible-vault が異常終了した場合
        期待値: False と標準エラー出力の内容を返す
        """
        vault_env.add_path()
        monkeypatch.setenv("STUB_VAULT_RC", "1")

        result, value = _vault(vault_env, indento="    ")

        assert result is False
        assert value == "ERROR! stub failure\n"

    def test_vault_ansible_vault_not_found(self, vault_env, monkeypatch):
        """
        異常系: ansible-vault コマンドが見つからない場合
        期待値: 例外にならず False を返す
        """
        monkeypatch.setenv("PATH", "/usr/bin:/bin")

        result, value = _vault(vault_env)

        assert result is False
        assert "ansible-vault" in value

    def test_vault_shell_not_executable(self, vault_env, monkeypatch):
        """
        異常系: 実行シェルに実行権限が付かず起動できない場合（OSError）
        期待値: 例外にならず False とエラー内容を返す。一時ファイルは削除される
        """
        vault_env.add_path()
        monkeypatch.setattr(vault_module, "retry_chmod", lambda *args, **kwargs: None)

        result, value = _vault(vault_env)

        assert result is False
        assert "Permission denied" in value
        assert not vault_env.shell_file.exists()
        assert not vault_env.value_file.exists()

    @pytest.mark.parametrize("error", [
        FileNotFoundError(2, "No such file or directory"),
        PermissionError(13, "Permission denied"),
    ])
    def test_vault_subprocess_oserror(self, vault_env, error):
        """
        異常系: subprocess.run が OSError を送出した場合
        期待値: 例外にならず False とエラー内容を返す
        """
        with patch.object(vault_module.subprocess, "run", side_effect=error):
            result, value = _vault(vault_env)

        assert result is False
        assert value == str(error)

    def test_vault_runs_without_shell(self, vault_env):
        """
        正常系: 実行シェルをシェル経由(shell=True)ではなく直接実行していること
        期待値: subprocess.run に [実行シェル, virtualenv_flg] のリストが渡り、shell=True は指定されない
        """
        vault_env.add_path()
        real_run = subprocess.run
        spy = MagicMock(side_effect=lambda *args, **kwargs: real_run(*args, **kwargs))

        with patch.object(vault_module.subprocess, "run", spy):
            result, _ = _vault(vault_env)

        assert result is True
        args, kwargs = spy.call_args
        assert args[0] == [str(vault_env.shell_file), "__undefine__"]
        assert kwargs.get("shell", False) is False

    def test_vault_removes_temporary_files(self, vault_env):
        """
        正常系: 一時ファイルの削除
        期待値: 実行シェルと値ファイルは削除される。passwdFileDel=False ならパスワードファイルは残る
        """
        vault_env.add_path()

        result, _ = _vault(vault_env, passwdFileDel=False)

        assert result is True
        assert not vault_env.shell_file.exists()
        assert not vault_env.value_file.exists()
        assert vault_env.password_file.exists()

    def test_vault_removes_password_file(self, vault_env):
        """
        正常系: passwdFileDel=True の場合
        期待値: パスワードファイルも削除される
        """
        vault_env.add_path()

        result, _ = _vault(vault_env, passwdFileDel=True)

        assert result is True
        assert not vault_env.password_file.exists()


class TestVaultCallers:
    """CreateAnsibleExecFiles から Vault() を呼び出す4メソッドのテスト"""

    @pytest.fixture(autouse=True)
    def _require_dictknife(self):
        # CreateAnsibleExecFiles の import に dictknife が必要
        pytest.importorskip("dictknife")

    @pytest.fixture
    def instance(self, create_ansible_exec_files_instance):
        instance = create_ansible_exec_files_instance({
            "SERVICE_ACCOUNT_INFO": None,
            "SERVICE_ACCOUNT_TOKEN": None,
            "ANSIBLE_EXEC_MODE": "1",
            "ANSIBLE_VAULT_PASSWORD": "dummy_encrypted_password",
        })
        instance.LocalLogPrint = MagicMock()
        return instance

    @pytest.mark.parametrize("method_name", [
        "makeAnsibleVaultPassword",
        "makeAnsibleVaultValue",
        "makeAnsibleVaultGBL",
        "makeAnsibleVault",
    ])
    def test_caller_passes_arguments_in_order(self, instance, method_name):
        """
        正常系: 呼び出し元が Vault() に渡す引数の並び
        期待値: ("", パスワードファイル, 暗号化対象, "", virtualenv, True) の順で渡し、
                戻り値は " !vault |" に連結されインデントが付く
        """
        with patch.object(AnsibleVault, "CreateVaultPasswordFilePath", return_value="/tmp/.vault_test"), \
                patch.object(AnsibleVault, "CreateVaultPasswordFile", return_value=True), \
                patch.object(AnsibleVault, "Vault", return_value=(True, "\nENCRYPTED")) as mock_vault:
            out = getattr(instance, method_name)("secret", "", "  ", "key")

        mock_vault.assert_called_once_with("", "/tmp/.vault_test", "secret", "", instance.lv_engine_virtualenv_name, True)
        assert out == " !vault |\n  ENCRYPTED"

    @pytest.mark.parametrize("method_name", [
        "makeAnsibleVaultPassword",
        "makeAnsibleVaultValue",
        "makeAnsibleVaultGBL",
        "makeAnsibleVault",
    ])
    def test_caller_vault_failed(self, instance, method_name):
        """
        異常系: Vault() が失敗した場合
        期待値: False を返し、Vault() のエラー内容をログに出力する
        """
        with patch.object(AnsibleVault, "CreateVaultPasswordFilePath", return_value="/tmp/.vault_test"), \
                patch.object(AnsibleVault, "CreateVaultPasswordFile", return_value=True), \
                patch.object(AnsibleVault, "Vault", return_value=(False, "ERROR! failure")):
            out = getattr(instance, method_name)("secret", "", "  ", "key")

        assert out is False
        logged = [c.args[2] for c in instance.LocalLogPrint.call_args_list]
        assert "ERROR! failure" in logged


@pytest.mark.skipif(shutil.which("ansible-vault") is None, reason="ansible-vault コマンドが無い環境では実行しない")
class TestVaultRealAnsibleVault:
    """本物の ansible-vault を使ったテスト"""

    def test_vault_encrypt_and_decrypt(self, vault_env, tmp_path):
        """
        正常系: 本物の ansible-vault で暗号化した結果を復号できること
        期待値: 復号結果が暗号化前の値と一致する
        """
        result, value = _vault(vault_env, value="secret_value")

        assert result is True
        assert value.startswith("\n$ANSIBLE_VAULT;")

        encrypted_file = tmp_path / "encrypted.txt"
        encrypted_file.write_text(value.lstrip("\n"))
        ret = subprocess.run(
            ["ansible-vault", "decrypt", "--vault-password-file", str(vault_env.password_file),
             "--output", "-", str(encrypted_file)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert ret.returncode == 0, ret.stderr
        assert ret.stdout.decode() == "secret_value"
