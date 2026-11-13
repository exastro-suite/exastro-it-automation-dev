# Copyright 2026 NEC Corporation#
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
"""
メニュー定義(10203/10204)・ロール-メニュー紐付(10104)の更新に対する共通ガード
Common guard for menu definition (10203/10204) and role-menu link (10104) updates.

モードは環境変数 MENU_DEF_GUARD_MODE で切り替える(運用者がインフラ側で設定する。画面からは変更できない)。
  enforce(既定): 違反を拒否
  monitor / warn: 違反をガードログに出力するのみ(処理は続行)
未設定・不正な値は enforce とする。
"""
import os
import re

from flask import g

MODE_ENV = "MENU_DEF_GUARD_MODE"
MODES = ("monitor", "warn", "enforce")
DEFAULT_MODE = "enforce"

# 識別子として許可する形式
IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

# どのメニューからも参照先に指定できないテーブル(所有メニューの例外なし)。
# 初期状態でメニューが読まないテーブルを機械的に洗い出し、リスクの高いものを明示している。
# テーブルの追加・削除に合わせてメンテナンスする(マスタのメニューが読むテーブルを含めないこと。
# tests/common_libs/loadtable/test_menu_definition_guard.py の整合テストで検出する)。
DENY_TABLES = frozenset([
    # --- 接続情報・内部管理(リスクが高い) ---
    "T_COMN_WORKSPACE_DB_INFO",         # 組織DBのテーブル(DB・MongoDBの接続情報とパスワード)。ワークスペースDBには通常存在しないが、構成変更に備えて明示
    "T_COMN_BACKYARD_USER",             # バックヤードユーザーのマスタ
    "T_COMN_PROC_LOADED_LIST",          # バックヤード処理の実行フラグ(書き換えると処理の起動を操作できる)
    "T_COMN_RECODE_LOCK_TABLE",         # レコードロック対象のテーブル一覧
    "T_COMN_WEB_TABLE_SETTINGS",        # ユーザごとの画面設定(テーブル表示・ウィジェット)
    "T_COMN_AAC_VIRTUALENV",            # AAC 仮想環境マスタ

    # --- 画面・機能の内部データ(メニューが直接読まない) ---
    "T_AI_ATTACHMENT_FILE",             # AI機能の添付ファイル
    "T_DP_HIDE_MENU_LIST",              # 非表示メニューの一覧
    "T_MENU_COLLECTION_FILTER_DATA",    # パラメータ集の検索条件情報
    "T_MENU_PARAM_PURPOSE",             # パラメータシート作成の用途マスタ
    "T_OASE_EVENT_COLLECTION_PROGRESS",  # OASE イベント収集の経過

    # --- 内部で使う固定マスタ(メニューのプルダウンからは参照されない) ---
    "T_ANSC_TWR_JOBTP_PROPERTY",        # Tower ジョブテンプレートのプロパティ
    "T_CICD_GIT_PROTOCOL_TYPE",         # CI/CD: Git プロトコル種別
    "T_CICD_GIT_REPOSITORY_TYPE",       # CI/CD: Git リポジトリ種別
    "T_CICD_MATL_FILE_TYPE",            # CI/CD: 資材ファイルタイプ
    "T_CICD_MATL_TYPE",                 # CI/CD: ITA 素材タイプ
    "T_CICD_REPO_SYNC_STATUS",          # CI/CD: Git リポジトリ同期状態
    "T_OASE_EVENT",                     # OASE: イベントマスタ
    "T_OASE_EVENT_STATUS",              # OASE: イベント状態マスタ
    "T_OASE_LABEL_KEY_FIXED",           # OASE: ラベルキー固定マスタ
])

# 履歴テーブルは参照先として直接指定しない(履歴は各メニューのテーブルから自動で決まる)
DENY_SUFFIXES = ("_JNL",)

# 権限・メニュー定義・システム設定・認証情報を保持するテーブルと、その所有メニュー。
# 所有メニュー以外からの参照先指定を拒否する(所有メニューは自身のテーブルのまま保てる)。
# 所有メニューはマスタ(T_COMN_MENU_TABLE_LINK)の定義と一致させること(整合テストで検出する)。
#   テーブル: (所有メニューID,)  # メニューID メニュー名
SENSITIVE_TABLE_OWNERS = {
    # --- システム管理(基本) ---
    "T_COMN_SYSTEM_CONFIG": ("10101",),     # 10101 システム設定
    "T_COMN_MENU_GROUP": ("10102",),        # 10102 メニューグループ管理
    "T_COMN_MENU": ("10103",),              # 10103 メニュー管理
    "T_COMN_ROLE_MENU_LINK": ("10104",),    # 10104 ロール-メニュー紐付管理(権限そのもの)
    "T_COMN_MENU_TABLE_LINK": ("10203",),   # 10203 メニュー-テーブル紐付管理(メニューの参照先の定義)
    "T_COMN_MENU_COLUMN_LINK": ("10204",),  # 10204 メニュー-カラム紐付管理(項目と列の対応の定義)
    "T_COMN_COLUMN_GROUP": ("10205",),      # 10205 カラムグループ管理

    # --- パスワード・トークン系の列クラスを持つメニューのテーブル(列クラスから機械抽出。漏れに注意) ---
    "T_ANSC_DEVICE": ("20101",),                    # 20101 機器一覧(ログインパスワード・パスフレーズ)
    "T_ANSC_IF_INFO": ("20102",),                   # 20102 インターフェース情報(Vault パスワード・認証トークン)
    "T_ANSC_TOWER_HOST": ("20103",),                # 20103 Ansible Automation Platform ノード一覧(パスワード・パスフレーズ)
    "T_TERE_IF_INFO": ("80101",),                   # 80101 インターフェース情報(Terraform-Cloud/EP。ユーザトークン)
    "T_OASE_EVENT_COLLECTION_SETTINGS": ("110101",),  # 110101 イベント収集(OASE。認証トークン・パスワード・シークレット)
}

# メンテナンス権限の付与を禁止するシステムメニュー
PROTECTED_MENU_IDS = ("10203", "10204", "10104")

PRIVILEGE_MAINTENANCE = "1"


def get_mode():
    """環境変数からモードを取得する。未設定・不正な値なら既定(enforce)"""
    mode = os.environ.get(MODE_ENV, "").strip().lower()
    return mode if mode in MODES else DEFAULT_MODE


def is_enforce():
    return get_mode() == "enforce"


def guard_log(menu_id, cmd_type, item, old, new, reason, mode=None):
    """違反・変更のガードログ"""
    try:
        user = getattr(g, "USER_ID", None)
        g.applogger.info(
            f"[MENU_DEF_GUARD] mode={mode} menu={menu_id} cmd={cmd_type} user={user} item={item} old={old} new={new} reason={reason}")
    except Exception:
        pass


def _table_key(name):
    """ビュー(V_)は対応するテーブル(T_)と同じ扱いにする"""
    return "T_" + name[2:] if name.startswith("V_") else name


def _owners_of(name):
    return SENSITIVE_TABLE_OWNERS.get(_table_key(name))


def is_denied(name):
    """どのメニューからも参照先にできないテーブルか"""
    return _table_key(name) in DENY_TABLES or name.endswith(DENY_SUFFIXES)


def check_table_reference(objdbca, item, value, own_menu_id=None, lookup_ok=()):
    """
    参照先テーブル/ビュー名の検査 (識別子形式・機微テーブル・実在確認)
    lookup_ok: プルダウン参照として許容するテーブル名(機微テーブルでも拒否しない)
    Returns: (True, '') or (False, message)
    """
    if value is None or value == "":
        return True, ""

    if not isinstance(value, str) or not IDENTIFIER_PATTERN.match(value):
        return False, g.appmsg.get_api_message("499-01907", [item, value])

    if is_denied(value):
        return False, g.appmsg.get_api_message("499-01906", [item, value])

    owners = _owners_of(value)
    if owners is not None and str(own_menu_id) not in owners and value not in lookup_ok:
        return False, g.appmsg.get_api_message("499-01906", [item, value])

    rows = objdbca.sql_execute(
        "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        [value])
    if len(rows) == 0:
        return False, g.appmsg.get_api_message("499-01908", [item, value])

    return True, ""


def check_column_exists(objdbca, item, table_name, column_name):
    """列の存在確認"""
    if not column_name or not table_name:
        return True, ""
    if not IDENTIFIER_PATTERN.match(str(column_name)):
        return False, g.appmsg.get_api_message("499-01907", [item, column_name])
    rows = objdbca.sql_execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        [table_name, column_name])
    if len(rows) == 0:
        return False, g.appmsg.get_api_message("499-01908", [item, f"{table_name}.{column_name}"])
    return True, ""


def judge(menu_id, cmd_type, item, old, new, errormsg, option):
    """
    違反を判定する。enforce なら拒否、それ以外はガードログのみで通す。
    Returns: (retBool, msg, option)
    """
    mode = get_mode()
    guard_log(menu_id, cmd_type, item, old, new, errormsg, mode)
    if mode == "enforce":
        return False, errormsg, option
    return True, "", option


def log_changes(menu_id, option, keys):
    """保護項目の変更をガードログに残す"""
    cmd_type = option.get("cmd_type")
    new = option.get("entry_parameter", {}).get("parameter", {}) or {}
    old = (option.get("current_parameter") or {}).get("parameter", {}) or {}
    for key in keys:
        if key in new and new.get(key) != old.get(key):
            guard_log(menu_id, cmd_type, key, old.get(key), new.get(key), "changed")
