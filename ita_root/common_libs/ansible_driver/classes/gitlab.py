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
"""
GitLab connection agnet module for Ansible Automation Controller
"""
from flask import g
import requests  # noqa F401
import os
import re
import json
import urllib.parse
from common_libs.common.exception import AppException
from common_libs.common.dbconnect import *  # noqa: F403

class GitLabAgent:
    """
    GitLab connection agnet class for Ansible Automation Controller
    """
    _protocol = ""
    _host = ""
    _port = ""
    _api_base_url = ""
    _user = ""
    _token = ""
    _root_token = ""

    def __init__(self, root_mode=False):
        """
        constructor
        """
        self._protocol = os.environ.get('GITLAB_PROTOCOL')
        self._host = os.environ.get('GITLAB_HOST')
        self._port = os.environ.get('GITLAB_PORT')
        self._api_base_url = "{}://{}:{}/api/v4".format(self._protocol, self._host, self._port)

        self._root_token = os.environ.get('GITLAB_ROOT_TOKEN')

        if root_mode is False:
            self._user = g.gitlab_connect_info.get('GITLAB_USER')
            self._token = g.gitlab_connect_info.get('GITLAB_TOKEN')
        else:
            self._user = "root"
            self._token = os.environ.get('GITLAB_ROOT_TOKEN')
    @property
    def user(self):
        return self._user

    @property
    def token(self):
        return self._token

    def send_api(self, method, resource, name, data=None, get_params=None, as_row=False, is_root=False, retry_limit=3):
        """
        request gitlab RESTAPI

        Arguments:
            method: get or post or put or delete
            resource: url resource
            data: request body
            get_params: get query paramater
            as_row: whether return response-object or not
            is_root: wheter root user or not
            retry_limit: retry limit for re-generate token
        Returns:
            http response body OR boolean OR response-object
        """

        retry_count = 0
        while True:
            g.applogger.info('[Trace] gitlab api request start. (endpoint: {}:{}, name: {})'.format(method, resource, name)) # 外部アプリへの処理開始・終了ログ

            success, status_code, response = self.send_api_once(method, resource, data, get_params, as_row, is_root)

            if success is True:
            # 成功
                g.applogger.info('[Trace] gitlab api request succeeded.') # 外部アプリへの処理開始・終了ログ
                return response
            # 失敗
            g.applogger.info('[Trace] gitlab api request failed. ({})'.format(response)) # 外部アプリへの処理開始・終了ログ
            if status_code < 500 or retry_count == retry_limit:
                raise AppException("999-00004", [response])
            # ステータスコード500以上は上限までリトライする
            retry_count = retry_count + 1

    def send_api_once(self, method, resource, data=None, get_params=None, as_row=False, is_root=False):
        """
        request gitlab RESTAPI

        Arguments:
            method: get or post or put or delete
            resource: url resource
            data: request body
            get_params: get query paramater
            as_row: whether return response-object or not
            is_root: wheter root user or not
        Returns:
            http response body OR boolean OR response-object
        """
        url = self._api_base_url + resource
        headers = {
            "PRIVATE-TOKEN": self._token if is_root is False else self._root_token,
            "Content-Type": "application/json"
        }
        data_json = json.dumps(data)

        # トークンがログに出力されないようにマスクする
        log_headers = dict(headers, **{"PRIVATE-TOKEN": "********"})
        g.applogger.debug('[Trace] gitlab request parameters. (method:{} url:{} headers={} params={} data={})'.format(method, url, log_headers, get_params, data_json))

        # APIへの送信実行
        response = getattr(requests, method.lower())(url, headers=headers, params=get_params, data=data_json, timeout=(12, 600))

        if response.headers.get('Content-Type') == 'application/json':
            if 200 <= response.status_code < 400:
                res = response.json()

                if "error" in res:
                    err_msg = "{}:{} -> {}:{}".format(method, url, response.status_code, res)
                    return False, response.status_code, err_msg
                else:
                    if as_row is True:
                        return True, response.status_code, response
                    return True, response.status_code, res

            else:
                err_msg = "{}:{} -> {}:{}".format(method, url, response.status_code, response.text)
                return False, response.status_code, err_msg
        else:
            if 200 <= response.status_code < 400:
                if as_row is True:
                    return True, response.status_code, response
                return True, response.status_code, True
            else:
                err_msg = "{}:{} -> {}:{}".format(method, url, response.status_code, response.text)
                return False, response.status_code, err_msg

    @staticmethod
    def _get_status_code(e):
        # e.args = ("999-00004", ["delete:http://...:40080/api/v4/projects/8 -> 400:{...}"], [])
        try:
            match = re.search(r' -> (\d{3}):', e.args[1][0])
        except (IndexError, TypeError):
            return None
        return str(match.group(1)) if match else None

    def get_http_repo_url(self, project_name):
        """
        get gitlab http repository url

        Arguments:
            project_name: project_name
        Returns:
            (str) url
        """
        return "{protocol}://{user}:{token}@{host}:{port}/{user}/{project_name}.git".format(protocol=self._protocol, host=self._host, port=self._port, user=self._user, token=urllib.parse.quote(self._token), project_name=project_name)  # noqa E501

    def get_http_repo_url_scm(self, project_name):
        """
        get gitlab http repository url for SCM

        Arguments:
            project_name: project_name
        Returns:
            (str) url
        """
        return "{protocol}://{host}:{port}/{user}/{project_name}.git".format(protocol=self._protocol, host=self._host, port=self._port, user=self._user, project_name=project_name)  # noqa E501

    def check_user(self):
        # userがいるかをrootユーザで確認
        user_list = self.get_user_by_username(self._user)
        if user_list:
            res = self.check_user_token()
            if res is True:
                return True, None
            else:
            # userはあったが、トークンが無効
                g.applogger.info("[Trace] gitlab USER( {} ) is Unauthorized".format(self._user))
                return False, user_list[0]
        else:
            # ユーザを作成
            g.applogger.info("[Trace] gitlab USER( {} ) is NOT FOUND on GITLAB".format(self._user))
            try:
                res = self.create_user(g.gitlab_connect_info['GITLAB_USER'])
                return False, res
            except AppException as e:
                # 作成したら、既に他のプロセス等で作成済みだった場合を考慮
                if self._get_status_code(e) == "409":
                    g.applogger.info("[Trace] gitlab USER( {} ) is already created on GITLAB".format(self._user))

                    user_list = self.get_user_by_username(self._user)
                    return False, user_list[0]
                else:
                    raise

    def update_gitlab_userinfo(self, user):
        common_db = None
        try:
            # トークンが、他のプロセスによって更新されていることを考慮し、再度DBから取り出して疎通確認を行う
            organization_id = g.get('ORGANIZATION_ID')
            common_db = DBConnectCommon()  # noqa: F405

            common_db.db_transaction_start()
            # 排他制御で最新の情報を取り出す
            connect_info = common_db.sql_execute("SELECT * FROM `T_COMN_ORGANIZATION_DB_INFO` WHERE `ORGANIZATION_ID`=%s and `DISUSE_FLAG`=0 LIMIT 1 FOR UPDATE", [organization_id])[0]

            g.gitlab_connect_info['GITLAB_TOKEN'] = connect_info["GITLAB_TOKEN"]
            self._token = connect_info["GITLAB_TOKEN"]

            res = self.check_user_token()
            if res is True:
                # 書き換えられている様子なら、何もせずに終了
                g.applogger.info("[Trace] gitlab USER( {} ) is already updated by antoher".format(self._user))
                return True
            # 認証に失敗したら、トークンが更新されていないと判断する

            # 新しいGitLabからトークンを払い出してDBを更新
            token = self.create_personal_access_tokens(user['id'], user['username'])
            common_db.sql_execute("UPDATE `T_COMN_ORGANIZATION_DB_INFO` SET `GITLAB_TOKEN`=%s, `LAST_UPDATE_TIMESTAMP`=NOW(6) WHERE `PRIMARY_KEY`=%s and `GITLAB_TOKEN`=%s and `DISUSE_FLAG`=0", [token, connect_info["PRIMARY_KEY"], connect_info["GITLAB_TOKEN"]])
            common_db.db_commit()

            # キャッシュを更新
            g.gitlab_connect_info['GITLAB_TOKEN'] = token
            self._token = token
            g.applogger.info("[Trace] Newly updated the gitlab USER( {} )".format(self._user))
        except Exception:
            if common_db is not None:
                common_db.db_rollback()
            raise
        finally:
            if common_db is not None:
                common_db.db_disconnect()

        return True

    def get_user_self(self):
        # https://docs.gitlab.com/ja-jp/api/users/#retrieve-the-current-user
        res = self.send_api(method="get", resource="/user", name="get_user_self")

        return res

    def check_user_token(self):
        # https://docs.gitlab.com/ja-jp/api/users/#retrieve-the-current-user

        g.applogger.info('[Trace] gitlab api request start. (endpoint: get:/user, name: get_user_self)') # 外部アプリへの処理開始・終了ログ
        success, status_code, response = self.send_api_once(method="get", resource="/user")
        if success is True:
            g.applogger.info('[Trace] gitlab api request succeeded.') # 外部アプリへの処理開始・終了ログ
            return True
        else:
            g.applogger.info('[Trace] gitlab api request failed. ({})'.format(response)) # 外部アプリへの処理開始・終了ログ
            if status_code != 401:
                raise AppException("999-00004", [response])
            else:
                # 401 Unauthorized
                return False

    def get_user_by_username(self, username=""):
        # https://docs.gitlab.com/ja-jp/api/users/#as-a-regular-user
        # rootユーザ用関数
        if not username:
            params = {}
        else:
            params = {
                "username": username
            }

        return self.send_api(method="get", resource="/users", name="get_user_by_username", get_params=params, is_root=True)

    def create_user(self, username):
        # https://docs.gitlab.com/ja-jp/api/users/#create-a-user
        # rootユーザ用関数
        payload = {
            "name": username,
            "username": username,
            "email": username + "@example.com",
            "can_create_group": False,
            "admin": False,
            "external": False,  # can_create_project
            "force_random_password": True,
            "projects_limit": 10000,
            "skip_confirmation": True
        }

        res = self.send_api(method="post", resource="/users", name="create_user", data=payload, is_root=True)
        return res

    def delete_user(self, user_id):
        # https://docs.gitlab.com/ja-jp/api/users/#delete-a-user
        # rootユーザ用関数
        payload = {
            "id": user_id,
            'hard_delete': True
        }

        return self.send_api(method="delete", resource="/users/{}".format(user_id), name="delete_user", data=payload, is_root=True)

    def create_personal_access_tokens(self, user_id, username):
        # https://docs.gitlab.com/ja-jp/api/user_tokens/#create-a-personal-access-token-for-a-user
        # rootユーザ用関数
        # 有効期限を指定していないので、 1年で失効
        payload = {
            "user_id": user_id,
            "name": username,
            # "expires_at": "YYYY-MM-DD",
            "scopes": ["api"]
        }

        res = self.send_api(method="post", resource="/users/{}/personal_access_tokens".format(user_id), name="create_personal_access_tokens", data=payload, is_root=True)
        return res.get('token')

    def get_project_by_user_id(self, user_id, page=1):
        # https://docs.gitlab.com/ja-jp/api/projects/#list-all-personal-projects-for-a-user
        get_params = {
            "page": page,
            "per_page": 100
        }

        return self.send_api(method="get", resource="/users/{}/projects".format(user_id), name="get_project_by_user_id", get_params=get_params, as_row=True, is_root=True)

    def get_all_project_by_user_id(self, user_id):
        res = []

        is_get_all = False
        next_page = 1
        while is_get_all is False:
            response = self.get_project_by_user_id(user_id, next_page)
            project_list = response.json()
            res.extend(project_list)

            current_page = response.headers.get('X-Page')
            total_pages = response.headers.get('X-Total-Pages')
            if current_page == total_pages:
                is_get_all = True
            else:
                next_page = response.headers.get('X-Next-Page')

        return res

    def get_project_by_name(self, project_name):
        """
        get project by project_name

        Arguments:
            project_name: project_name
        Returns:
            (json)http response body
        """
        user = self.get_user_self()
        if user:
            is_get_all = False
            next_page = 1
            while is_get_all is False:
                response = self.get_project_by_user_id(user['id'], next_page)
                project_list = response.json()
                for project in project_list:
                    if project['path'] == project_name:
                        is_get_all = True
                        return project

                current_page = response.headers.get('X-Page')
                total_pages = response.headers.get('X-Total-Pages')
                if current_page == total_pages:
                    is_get_all = True
                else:
                    next_page = response.headers.get('X-Next-Page')

        return False

    def create_project(self, project_name):
        # https://docs.gitlab.com/ja-jp/api/projects/#create-project
        organization_id = g.get('ORGANIZATION_ID')
        workspace_id = g.get('WORKSPACE_ID')
        payload = {
            "name": project_name,
            "path": project_name,  # Repository name for new project.
            "visibility": "private",
            "emails_enabled": False,
            "initialize_with_readme": False,
            "topics": [self._user, "organization_id_" + organization_id, "workspace_id_" + workspace_id]
        }

        return self.send_api(method="post", resource="/projects", name="create_project", data=payload)

    def get_project(self, project_id):
        # https://docs.gitlab.com/ja-jp/api/projects/#retrieve-a-project
        res = self.send_api(method="get", resource="/projects/{}".format(project_id), name="get_project")

        return res

    def delete_project(self, project_id):
        # https://docs.gitlab.com/ja-jp/api/projects/#delete-a-project
        # GitLab 18 以降は、permanently_removeがFalseだと削除予定の状態になり、プロジェクトの保持期間を過ぎると削除される
        # 即時削除(permanently_remove)は、削除予定の状態のプロジェクトにのみ指定でき、full_path(path_with_namespace)も必要
        # そのため、 1.削除予定にする → 2.permanently_remove で完全削除 の2段階で行う
        resource = "/projects/{}".format(project_id)

        try:
            # 1. 削除予定にする
            self.send_api(method="delete", resource=resource, name="delete_schedule_project")
        except AppException as e:
            status_code = self._get_status_code(e)
            if status_code == "400":
                # Project has already been marked for deletion
                pass
            else:
                raise

        # 削除予定にすると、パスが「{user}/{project_name}-deletion_scheduled-{id}」に変更されるため、
        # full_path には、削除予定にした後のプロジェクトのpath_with_namespaceを取得して指定する
        project = self.get_project(project_id)

        try:
            # 2. 完全削除
            payload = {
                "permanently_remove": True,
                "full_path": project.get("path_with_namespace")
            }
            return self.send_api(method="delete", resource=resource, name="delete_permanently_project", data=payload)
        except AppException as e:
            status_code = self._get_status_code(e)
            if status_code == "404":
                # 1.の時点で即時削除される設定(遅延削除なし)の場合や、他プロセスで削除済みの場合
                g.applogger.info("[Trace] gitlab project( {} ) is already deleted.".format(project_id))
                return True
            raise
