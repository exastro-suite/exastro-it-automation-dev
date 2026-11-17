# Copyright 2023 NEC Corporation#
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

from flask import g
import os
import traceback
import sys
from jinja2 import FileSystemLoader
from jinja2.exceptions import SecurityError
from jinja2.sandbox import SandboxedEnvironment
from common_libs.common.util import get_iso_datetime, arrange_stacktrace_format
from common_libs.notification.validator import find_unsafe_jinja2_access


def validate_jinja2_template_file(path, file):
    """アップロードされたjinja2テンプレートを、サンドボックス内で検証する。

    アップロードされたファイルは利用者が自由に書けるため、サンドボックスなしの
    jinja2.Environmentで評価すると、保存の検証の時点で任意コードが実行されてしまう（SSTI）。
    そのため、SandboxedEnvironmentで評価し、さらに静的に危険な属性アクセスも検査する。
    ({% include %}等で同じディレクトリのファイルを読む挙動は従来どおり)

    Args:
        path: jinja2ファイルのあるディレクトリ
        file: jinja2ファイル名
    Raises:
        Exception: 構文エラー・評価エラー・危険な属性アクセスを含む場合
    """
    env = SandboxedEnvironment(loader=FileSystemLoader(path, encoding='utf8'))

    # 静的検査: 評価されない分岐や、先にエラーになる式の後ろに書かれた危険な記述も検出する
    source, _, _ = env.loader.get_source(env, file)
    unsafe_name = find_unsafe_jinja2_access(env.parse(source))
    if unsafe_name is not None:
        raise SecurityError("access to attribute '{}' is not allowed in jinja2 template".format(unsafe_name))

    # 動的検査: 従来どおり空の変数で評価し、構文エラー・評価エラーを検出する
    env.get_template(file).render({})


def external_valid_menu_before(objdbca, objtable, option):

    target_column_name = {
        "ja": objtable["COLINFO"]["template_file"]["COLUMN_NAME_JA"],
        "en": objtable["COLINFO"]["template_file"]["COLUMN_NAME_EN"],
    }

    target_lang = g.LANGUAGE if g.LANGUAGE is not None else "ja"

    retBool = True
    msg = ''

    # 入力値取得
    cmd_type = option.get("cmd_type")

    jinja2_file_path = None
    if cmd_type in ["Register", "Update"]:
        jinja2_file_path = option.get('entry_parameter').get('file_path', {}).get('template_file', '')
        if not jinja2_file_path:
            jinja2_file_path = option.get('current_parameter').get('file_path', {}).get('template_file', '')

    if jinja2_file_path:
        try:
            # jinja2の形式として問題無いか確認する
            validate_jinja2_template_file(os.path.dirname(jinja2_file_path), os.path.basename(jinja2_file_path))
        except Exception as e:
            # バックトレース出力
            t = traceback.format_exc()
            g.applogger.info("[timestamp={}] {}".format(get_iso_datetime(), arrange_stacktrace_format(t)))
            retBool = False
            msg = g.appmsg.get_api_message("MSG-10980", [target_column_name[target_lang], str(e)])

    return retBool, msg, option,