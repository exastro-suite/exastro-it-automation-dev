#   Copyright 2026 NEC Corporation
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
"""
設定値(名前)からモジュール内の関数・クラスを解決する
用途: 個別バリデーション(BEFORE_VALIDATE_REGISTER / AFTER_VALIDATE_REGISTER)の関数、およびカラムクラスの解決
"""
import re
from typing import Any

# 関数名・クラス名として許可する形式(先頭は英字。アンダースコア始まり・ダンダー名は不可)
_CALLABLE_NAME_PATTERN = re.compile(r'[A-Za-z][A-Za-z0-9_]*')


def get_validate_callable(module, name) -> Any:
    """
        設定値(関数名またはクラス名)から、モジュール内の呼び出し可能オブジェクト(関数・クラス)を取得する
        設定値は式として評価せず、識別子として検証した上で getattr で取得する
        取得結果の種別(関数かクラスか)は区別せず、callable であれば返す

        ARGS:
            module: 解決対象のモジュール(valid_xxx モジュール、common_libs.column など)
            name: 設定値(関数名またはクラス名)

        RETURN:
            callable(関数またはクラス)

        RAISES:
            ValueError: 名前の形式が不正、または呼び出し可能でない場合
            AttributeError: モジュールに該当の関数・クラスが存在しない場合
    """
    if not isinstance(name, str) or _CALLABLE_NAME_PATTERN.fullmatch(name) is None:
        raise ValueError(f"invalid validate callable name: {name!r}")

    target = getattr(module, name)
    if not callable(target):
        raise ValueError(f"validate callable is not callable: {name!r}")

    return target
