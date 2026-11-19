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
#

from jinja2 import nodes
from jinja2.sandbox import SandboxedEnvironment
from jinja2.exceptions import SecurityError
import re
from common_libs.common.util import print_exception_msg

# SSTI対策: 保存時点でも危険な属性アクセスを検知できるようサンドボックス化された環境を使う
_sandbox_env = SandboxedEnvironment()


# サンドボックスの is_internal_attribute() が個別に禁止している、_で始まらない危険な属性名
_UNSAFE_ATTR_NAMES = frozenset([
    "mro",
    "gi_frame", "gi_code", "cr_frame", "cr_code", "ag_frame", "ag_code",
    "tb_frame", "f_globals", "f_locals", "f_builtins", "f_back", "f_code",
])


def _is_unsafe_attr_name(name):
    """属性名・キー名が、SSTIに使われる危険なものかを判定する。

    `__class__` `__globals__` のような`__`を含む`_`始まりの名前（および`_TemplateReference__context`のような
    名前修飾されたもの）と、`mro`等を危険とみなす。
    `_exastro_xxx` のように`__`を含まない`_`始まりの名前は、辞書キーとして正規に使われるため危険とみなさない。
    """
    return (name.startswith("_") and "__" in name) or name in _UNSAFE_ATTR_NAMES


def find_unsafe_jinja2_access(template_ast):
    """構文木(AST)を静的に走査し、SSTIにつながる危険な属性アクセスを探す。

    レンダリングによる検証は、テンプレートの先頭付近で別の式がエラーになると評価が止まり、
    後ろに書かれた式が検査されない（`{{ labels.host }}`や`{{ 1/0 }}`の後ろにSSTIを置くとすり抜ける）。
    また、`{% if false %}`のように実行されない分岐も評価されない。
    そのため、評価の成否に依存しない静的な検査を併用する。

    ※文字列を組み立てて属性名を作る方法（`|attr('_'~'_class__')`等）は静的には判定できない。
      その場合も、実行時にサンドボックスが遮断する。

    Args:
        template_ast (jinja2.nodes.Template): Environment.parse()の戻り値
    RETRUN:
        最初に見つかった危険な名前(str)。なければNone
    """
    for node in template_ast.find_all((nodes.Getattr, nodes.Getitem, nodes.Filter)):
        if isinstance(node, nodes.Getattr):
            if _is_unsafe_attr_name(node.attr):
                return node.attr
        elif isinstance(node, nodes.Getitem):
            if isinstance(node.arg, nodes.Const) and isinstance(node.arg.value, str) and _is_unsafe_attr_name(node.arg.value):
                return node.arg.value
        elif node.name == "attr":
            # {{ x|attr('__class__') }} の形
            for arg in node.args:
                if isinstance(arg, nodes.Const) and isinstance(arg.value, str) and _is_unsafe_attr_name(arg.value):
                    return arg.value
    return None


def has_unsafe_jinja2_access(template_ast):
    """find_unsafe_jinja2_access()の結果を真偽値で返す。

    Args:
        template_ast (jinja2.nodes.Template): Environment.parse()の戻り値
    RETRUN:
        result :True（危険な記述あり）/ False（なし）
    """
    return find_unsafe_jinja2_access(template_ast) is not None


def is_binary_file(template_data_binary):
    """ファイルの形式をチェックする。バイナリファイルの場合はエラーを返す。
    空のファイルの場合も本判定でエラーとする

    Args:
        template_data_binary (bytes): base64.b64decodeで取得したbytes
    RETRUN:
        result :True（正常）/ False（エラー）
    """

    # chardetを依存に持たないコンテナからもこのモジュールをimportできるよう、使用箇所で遅延importする
    import chardet

    encode = chardet.detect(template_data_binary)
    return encode['encoding'] is None


def is_jinja2_template(template_data_decoded):
    """jinja2のテンプレートとして問題無いか（構文エラー・SSTIにつながる危険な属性アクセス）をチェックする。

    Args:
        template_data_decoded (str): 評価する文字列
    RETRUN:
        result :True（正常）/ False（エラー）
    """

    try:
        template_ast = _sandbox_env.parse(template_data_decoded)
        template = _sandbox_env.from_string(template_data_decoded)
    except Exception as e:
        # 構文エラー(TemplateSyntaxError)のほか、None等の不正な入力で発生する例外も不正として扱う
        print_exception_msg(e)
        return False

    # 静的検査: 評価の成否に依存せず、危険な属性アクセスを含む式を検出する
    if has_unsafe_jinja2_access(template_ast):
        return False

    try:
        # 動的検査: 保存時点では予約変数の値が無いためコンテキスト無しでrenderし、SecurityErrorのみを不正とみなす
        # ※先に別の式がエラーになると以降は評価されないため、上の静的検査と併用する
        template.render()
    except SecurityError as e:
        print_exception_msg(e)
        return False
    except Exception:
        # 未定義変数によるUndefinedError等は保存時点では想定内のため許容する
        pass

    return True


def contains_title(template_data_decoded):
    """テンプレートに[TITLE]を含むかチェックする。
    含まない、もしくは複数含む場合はエラーとする。

    Args:
        template_data_decoded (str): 評価する文字列
    RETRUN:
        result :True（正常）/ False（エラー）
    """

    title_count = len(re.findall(r'\[TITLE\]', template_data_decoded))
    return title_count == 1


def contains_body(template_data_decoded):
    """テンプレートに[BODY]を含むかチェックする。
    含まない、もしくは複数含む場合はエラーとする。

    Args:
        template_data_decoded (str): 評価する文字列
    RETRUN:
        result :True（正常）/ False（エラー）
    """

    body_count = len(re.findall(r'\[BODY\]', template_data_decoded))
    return body_count == 1
