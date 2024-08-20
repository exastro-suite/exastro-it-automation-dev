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

import tarfile
import subprocess

from flask import g
from common_libs.common import *  # noqa: F403
from common_libs.ag.util import ky_decrypt, app_exception, exception
from common_libs.common import storage_access
from common_libs.ansible_driver.classes.AnscConstClass import AnscConst

def unexecuted_instance(objdbca, organization_id, workspace_id):
    """
        未実行インスタンス取得
        ARGS:
            organization_id:OrganizationID
            workspace_id: WorkspaceID
        RETRUN:
            statusCode, {}, msg
    """

    # 各テーブル
    t_ansl_exec_sts_inst = "T_ANSL_EXEC_STS_INST"
    t_ansp_exec_sts_inst = "T_ANSP_EXEC_STS_INST"
    t_ansr_exec_sts_inst = "T_ANSR_EXEC_STS_INST"
    t_ansc_execdev = "T_ANSC_EXECDEV"
    t_ansc_info = "T_ANSC_IF_INFO"

    # Legacy_role
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansl_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s', ['0', '11'])

    result = {}
    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        ans_vent_path = record.get("I_ANS_VENT_PATH") # 仮想環境パス

        result[execution_no] = {
            "driver_id": "legacy",
            "ans_vent_path": ans_vent_path
        }

    # pioneer
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansp_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s', ['0', '11'])

    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        ans_vent_path = record.get("I_ANS_VENT_PATH") # 仮想環境パス

        result[execution_no] = {
            "driver_id": "pioneer",
            "ans_vent_path": ans_vent_path
        }

    # role
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansr_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s', ['0', '11'])

    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        ans_vent_path = record.get("I_ANS_VENT_PATH") # 仮想環境パス

        result[execution_no] = {
            "driver_id": "legacy_role",
            "ans_vent_path": ans_vent_path
        }

    # 実行環境構築方法取得
    ret = objdbca.table_select(t_ansc_execdev, 'WHERE  DISUSE_FLAG=%s' ['0'])

    for record in ret:
        build_type = record['BUILD_TYPE']
        user_name = record['USER_NAME']
        password = record['PASSWORD']
        base_image = record['BASE_IMAGE_OS_TYPE']
        password = ky_decrypt(password)

    # 実行時データ削除フラグ取得
    ret = objdbca.table_select(t_ansc_info, 'WHERE  DISUSE_FLAG=%s' ['0'])
    for record in ret:
        anstwr_del_runtime_data = record['ANSTWR_DEL_RUNTIME_DATA']

    result[execution_no]["build_type"] = build_type
    result[execution_no]["user_name"] = user_name
    result[execution_no]["password"] = password
    result[execution_no]["base_image"] = base_image
    result[execution_no]["anstwr_del_runtime_data"] = anstwr_del_runtime_data

    objdbca.db_commit()

    return result

def get_execution_status(status):
    """
        緊急停止状態を返す
        ARGS:
            organization_id:OrganizationID
            workspace_id: WorkspaceID
        RETRUN:
            statusCode, {}, msg
    """

    if status == AnscConst.SCRAM:
        return True

    return False


def get_populated_data(objdbca, organization_id, workspace_id):
    """
        投入データ取得
        ARGS:
            organization_id:OrganizationID
            workspace_id: WorkspaceID
        RETRUN:
            statusCode, {}, msg
    """

    # 各テーブル
    t_ansl_exec_sts_inst = "T_ANSL_EXEC_STS_INST"
    t_ansp_exec_sts_inst = "T_ANSP_EXEC_STS_INST"
    t_ansr_exec_sts_inst = "T_ANSR_EXEC_STS_INST"

    # 各Driverパス
    legacy_dir_path = "/driver/ansible/legacy"
    pioneer_dir_path = "/driver/ansible/pioneer"
    role_dir_path = "/driver/ansible/legacy_role"

    # トランザクション開始
    objdbca.db_transaction_start()

    # Legacy_role
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansl_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s FOR UPDATE', ['0', '11'])

    result = {}
    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        conductor_name = record.get("CONDUCTOR_NAME") # 呼出元conductor
        conductor_instance_no = record.get("CONDUCTOR_INSTANCE_NO") # conductorインスタンスNO

        # in,outディレクトリをtarファイルにまとめる
        dir_path = "/storage/" + organization_id + "/" + workspace_id + legacy_dir_path + "/" + execution_no
        if os.path.exists(dir_path):
            gztar_path = dir_path + ".tar.gz"
            with tarfile.open(gztar_path, "w:gz") as tar:
                tar.add(dir_path, arcname="")

            # tarファイルをbase64に変換する
            in_out_data = encode_tar_file(dir_path, execution_no + ".tar.gz")

            # conductorから実行されている場合、__conductor_workflowdir__をtarファイルにまとめる
            if conductor_name is None:
                dir_path = "/storage/" + organization_id + "/" + workspace_id + legacy_dir_path + "/" + conductor_instance_no
                gztar_path = dir_path + ".tar.gz"
                with tarfile.open(gztar_path, "w:gz") as tar:
                    tar.add(dir_path, arcname="")

                # tarファイルをbase64に変換する
                conductor_data = encode_tar_file(dir_path, conductor_instance_no + ".tar.gz")
            else:
                conductor_data = ""

            result[execution_no] = {
                "in_out_data": in_out_data,
                "conductor_data": conductor_data
            }

            objdbca.db_commit()

    # pioneer
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansp_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s FOR UPDATE', ['0', '11'])

    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        conductor_name = record.get("CONDUCTOR_NAME") # 呼出元conductor
        conductor_instance_no = record.get("CONDUCTOR_INSTANCE_NO") # conductorインスタンスNO

        # in,outディレクトリをtarファイルにまとめる
        dir_path = "/storage/" + organization_id + "/" + workspace_id + pioneer_dir_path + "/" + execution_no
        if os.path.exists(dir_path):
            gztar_path = dir_path + ".tar.gz"
            with tarfile.open(gztar_path, "w:gz") as tar:
                tar.add(dir_path, arcname="")

            # tarファイルをbase64に変換する
            in_out_data = encode_tar_file(dir_path, execution_no + ".tar.gz")

            # conductorから実行されている場合、__conductor_workflowdir__をtarファイルにまとめる
            if conductor_name is None:
                dir_path = "/storage/" + organization_id + "/" + workspace_id + pioneer_dir_path + "/" + conductor_instance_no
                gztar_path = dir_path + ".tar.gz"
                with tarfile.open(gztar_path, "w:gz") as tar:
                    tar.add(dir_path, arcname="")

                # tarファイルをbase64に変換する
                conductor_data = encode_tar_file(dir_path, conductor_instance_no + ".tar.gz")
            else:
                conductor_data = ""

            result[execution_no] = {
                "in_out_data": in_out_data,
                "conductor_data": conductor_data
            }

            objdbca.db_commit()

    # role
    # 準備完了の作業インスタンス取得
    ret = objdbca.table_select(t_ansr_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s FOR UPDATE', ['0', '11'])

    for record in ret:
        execution_no = record.get("EXECUTION_NO") # 作業番号
        conductor_name = record.get("CONDUCTOR_NAME") # 呼出元conductor
        conductor_instance_no = record.get("CONDUCTOR_INSTANCE_NO") # conductorインスタンスNO

        # in,outディレクトリをtarファイルにまとめる
        dir_path = "/storage/" + organization_id + "/" + workspace_id + role_dir_path + "/" + execution_no
        if os.path.exists(dir_path):
            gztar_path = dir_path + ".tar.gz"
            with tarfile.open(gztar_path, "w:gz") as tar:
                tar.add(dir_path, arcname="")

            # tarファイルをbase64に変換する
            in_out_data = encode_tar_file(dir_path, execution_no + ".tar.gz")

            # conductorから実行されている場合、__conductor_workflowdir__をtarファイルにまとめる
            if conductor_name is None:
                dir_path = "/storage/" + organization_id + "/" + workspace_id + role_dir_path + "/" + conductor_instance_no
                gztar_path = dir_path + ".tar.gz"
                with tarfile.open(gztar_path, "w:gz") as tar:
                    tar.add(dir_path, arcname="")

                # tarファイルをbase64に変換する
                conductor_data = encode_tar_file(dir_path, conductor_instance_no + ".tar.gz")
            else:
                conductor_data = ""

            result[execution_no] = {
                "in_out_data": in_out_data,
                "conductor_data": conductor_data
            }

    # ステータスを実行待ちに変更
    objdbca.table_update(t_ansr_exec_sts_inst, 'WHERE  DISUSE_FLAG=%s AND STATUS_ID = %s FOR UPDATE', ['0', '12'])

    objdbca.db_commit()

    return result


def result_data_update(organization_id, workspace_id, execution_no, status, driver_id, out_base64_data, parameters_base64_data, conductor_base64_data):
    """
        通知されたファイルの更新
        ARGS:
            organization_id:OrganizationID
            workspace_id: WorkspaceID
        RETRUN:
            statusCode, {}, msg
    """

    if driver_id == "legacy":
        from_path = "/storage/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "in/project"
        tmp_out_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/out"
        tmp_parameters_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/parameters"
        tmp_conductor_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/conductor"
    elif driver_id == "pioneer":
        from_path = "/storage/" + organization_id + "/" + workspace_id + "/driver/ansible/pioneer/" + execution_no + "in/project"
        tmp_out_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/out"
        tmp_parameters_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/parameters"
        tmp_conductor_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/conductor"
    else:
        from_path = "/storage/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy_role/" + execution_no + "in/project"
        tmp_out_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/out"
        tmp_parameters_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/parameters"
        tmp_conductor_path = "/tmp/" + organization_id + "/" + workspace_id + "/driver/ansible/legacy/" + execution_no + "/conductor"

    # 作業ディレクトリ作成
    if not os.path.exists(tmp_out_path):
        os.mkdir(tmp_out_path)
        os.chmod(tmp_out_path, 0o777)

    # outディレクトリのtarファイル展開
    decode_tar_file(out_base64_data, tmp_out_path)

    # 展開したファイルの一覧を取得
    lst = os.listdir(tmp_out_path)

    if status == AnscConst.PROCESSING or status == AnscConst.PROCESS_DELAYED:
        for file_name in lst:
            if file_name == "error.log" or file_name == "exec.log":
                # 通知されたファイルで上書き
                shutil.move(tmp_out_path + "/" + file_name, from_path)
    elif status == AnscConst.COMPLETE or status == AnscConst.FAILURE:
        for file_name in lst:
            # 通知されたファイルで上書き
            shutil.move(tmp_out_path + "/" + file_name, from_path)

    # 作業ディレクトリ作成
    if not os.path.exists(tmp_parameters_path):
        os.mkdir(tmp_parameters_path)
        os.chmod(tmp_parameters_path, 0o777)

    # parametersディレクトリのtarファイル展開
    decode_tar_file(parameters_base64_data, tmp_parameters_path)

    # 展開したファイルの一覧を取得
    lst = os.listdir(tmp_parameters_path)

    if status == AnscConst.COMPLETE or status == AnscConst.FAILURE:
        for dir_name in lst:
            # 展開したファイルの一覧を取得
            lst = os.listdir(tmp_parameters_path + "/" + dir_name)
            for file_name in lst:
                # 通知されたファイルで上書き
                shutil.move(tmp_parameters_path + "/" + dir_name + "/" + file_name, from_path)

    # 作業ディレクトリ作成
    if not os.path.exists(tmp_conductor_path):
        os.mkdir(tmp_conductor_path)
        os.chmod(tmp_conductor_path, 0o777)

    # conductorディレクトリのtarファイル展開
    decode_tar_file(conductor_base64_data, tmp_conductor_path)

    # 展開したファイルの一覧を取得
    lst = os.listdir(tmp_conductor_path)

    if status == AnscConst.COMPLETE or status == AnscConst.FAILURE:
        for file_name in lst:
            # 通知されたファイルで上書き
            shutil.move(tmp_conductor_path + "/" + file_name, from_path)

    # 作業ディレクトリ削除
    shutil.rmtree(tmp_out_path)
    shutil.rmtree(tmp_parameters_path)
    shutil.rmtree(tmp_conductor_path)

def encode_tar_file(dir_path, file_name):
    """
        tarファイルをbase64に変換する
        ARGS:
            dir_path:ディレクトリパス
            workspace_id: ファイル名
        RETRUN:
            statusCode, {}, msg
    """

    cmd = "base64" + dir_path + "/" + file_name + "> tmp.txt"
    ret = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if ret.returncode != 0:
        msg = g.appmsg.get_api_message('MSG-10947', [])
        raise app_exception(msg)

    obj = storage_access.storage_read()
    obj.open(dir_path + "/tmp.txt")
    base64_data = obj.read()
    obj.close()

    # 処理終了後、作業ファイル削除
    os.remove(dir_path + "/" + file_name)
    os.remove(dir_path + "/tmp.txt")

    return base64_data

def decode_tar_file(base64_data, dir_path):
    """
        base64をtarファイルに変換する
        ARGS:
            base64_data: base64データ
            dir_path:ディレクトリパス
        RETRUN:
            statusCode, {}, msg
    """
    cmd = "base64 -d " + base64_data + " > " + dir_path
    ret = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if ret.returncode != 0:
        msg = g.appmsg.get_api_message('MSG-10947', [])
        raise app_exception(msg)

    return base64_data