#   Copyright 2025 NEC Corporation
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
GitLabAgent.check_user / GitLabAgent.update_gitlab_userinfo のユニットテスト

実行方法 (ita_root/ita_by_ansible_execute 直下、pytest.ini 作成済みであること):
    python3 -m pytest tests/ansible_driver_tests/ansibletowerlibs/test_gitlab.py
"""
import os
from unittest.mock import Mock, MagicMock, patch

import pytest
from flask import Flask, g

from common_libs.ansible_driver.classes import gitlab as gitlab_module  # noqa: E402
from common_libs.ansible_driver.classes.gitlab import GitLabAgent  # noqa: E402
from common_libs.common.exception import AppException  # noqa: E402

USER = "ITA_ORG_TEST"


@pytest.fixture
def agent():
    """Flask g をモックした GitLabAgent"""
    app = Flask(__name__)
    with app.app_context():
        g.applogger = Mock()
        g.ORGANIZATION_ID = "org1"
        g.gitlab_connect_info = {"GITLAB_USER": USER, "GITLAB_TOKEN": "old-token"}
        env = {
            "GITLAB_PROTOCOL": "http",
            "GITLAB_HOST": "gitlab",
            "GITLAB_PORT": "40080",
            "GITLAB_ROOT_TOKEN": "root-token",
        }
        with patch.dict(os.environ, env):
            yield GitLabAgent()


# ---------------------------------------------------------------------------
# check_user
# ---------------------------------------------------------------------------
class TestCheckUser:
    def test_user_exists_token_valid(self, agent):
        agent.get_user_by_username = Mock(return_value=[{"id": 1, "username": USER}])
        agent.check_user_token = Mock(return_value=True)

        assert agent.check_user() == (True, None)
        agent.get_user_by_username.assert_called_once_with(USER)

    def test_user_exists_token_invalid(self, agent):
        user_info = {"id": 1, "username": USER}
        agent.get_user_by_username = Mock(return_value=[user_info])
        agent.check_user_token = Mock(return_value=False)

        assert agent.check_user() == (False, user_info)

    def test_user_not_found_create(self, agent):
        created = {"id": 2, "username": USER}
        agent.get_user_by_username = Mock(return_value=[])
        agent.create_user = Mock(return_value=created)

        assert agent.check_user() == (False, created)
        agent.create_user.assert_called_once_with(USER)

    def test_user_not_found_create_conflict_409(self, agent):
        """作成時に409(他プロセスが作成済み)なら再取得して返す"""
        existing = {"id": 3, "username": USER}
        agent.get_user_by_username = Mock(side_effect=[[], [existing]])
        err = AppException("999-00004", ["post:http://gitlab:40080/api/v4/users -> 409:{'message': 'exists'}"], [])
        agent.create_user = Mock(side_effect=err)

        assert agent.check_user() == (False, existing)
        assert agent.get_user_by_username.call_count == 2

    def test_user_not_found_create_error_other_status(self, agent):
        """409以外のエラーは再送出"""
        agent.get_user_by_username = Mock(return_value=[])
        err = AppException("999-00004", ["post:http://gitlab:40080/api/v4/users -> 500:error"], [])
        agent.create_user = Mock(side_effect=err)

        with pytest.raises(AppException) as exc:
            agent.check_user()
        assert exc.value is err
        assert agent.get_user_by_username.call_count == 1

    def test_user_not_found_create_error_without_status(self, agent):
        """ステータスコードが解析できない場合も再送出"""
        agent.get_user_by_username = Mock(return_value=[])
        agent.create_user = Mock(side_effect=AppException("999-00004", ["unknown error"], []))

        with pytest.raises(AppException):
            agent.check_user()

    def test_check_user_token_error_propagates(self, agent):
        agent.get_user_by_username = Mock(return_value=[{"id": 1}])
        agent.check_user_token = Mock(side_effect=AppException("999-00004", ["x -> 500:err"], []))

        with pytest.raises(AppException):
            agent.check_user()


# ---------------------------------------------------------------------------
# update_gitlab_userinfo
# ---------------------------------------------------------------------------
class TestUpdateGitlabUserinfo:
    user_info = {"id": 10, "username": USER}
    connect_info = {"PRIMARY_KEY": "pk1", "GITLAB_TOKEN": "db-token"}

    @pytest.fixture
    def db(self):
        db = MagicMock()
        db.sql_execute.return_value = [dict(self.connect_info)]
        with patch.object(gitlab_module, "DBConnectCommon", return_value=db):
            yield db

    def test_token_already_updated_by_other_process(self, agent, db):
        """DBのトークンが有効なら更新せず True"""
        agent.check_user_token = Mock(return_value=True)
        agent.create_personal_access_tokens = Mock()

        assert agent.update_gitlab_userinfo(self.user_info) is True

        agent.create_personal_access_tokens.assert_not_called()
        assert db.sql_execute.call_count == 1  # SELECT のみ
        assert "FOR UPDATE" in db.sql_execute.call_args[0][0]
        assert db.sql_execute.call_args[0][1] == ["org1"]
        db.db_transaction_start.assert_called_once()
        db.db_commit.assert_not_called()
        db.db_rollback.assert_not_called()
        db.db_disconnect.assert_called_once()
        # DBの値でキャッシュ/インスタンスが同期される
        assert g.gitlab_connect_info["GITLAB_TOKEN"] == "db-token"
        assert agent._token == "db-token"

    def test_token_regenerated(self, agent, db):
        agent.check_user_token = Mock(return_value=False)
        agent.create_personal_access_tokens = Mock(return_value="new-token")

        assert agent.update_gitlab_userinfo(self.user_info) is True

        agent.create_personal_access_tokens.assert_called_once_with(10, USER)
        assert db.sql_execute.call_count == 2
        update_sql, update_params = db.sql_execute.call_args[0]
        assert update_sql.startswith("UPDATE `T_COMN_ORGANIZATION_DB_INFO`")
        assert update_params == ["new-token", "pk1", "db-token"]
        db.db_commit.assert_called_once()
        db.db_rollback.assert_not_called()
        db.db_disconnect.assert_called_once()
        assert g.gitlab_connect_info["GITLAB_TOKEN"] == "new-token"
        assert agent._token == "new-token"

    def test_create_token_error_rollback(self, agent, db):
        agent.check_user_token = Mock(return_value=False)
        agent.create_personal_access_tokens = Mock(side_effect=AppException("999-00004", ["err"], []))

        with pytest.raises(AppException):
            agent.update_gitlab_userinfo(self.user_info)

        db.db_commit.assert_not_called()
        db.db_rollback.assert_called_once()
        db.db_disconnect.assert_called_once()
        assert agent._token == "db-token"  # 新トークンは反映されない

    def test_check_token_error_rollback(self, agent, db):
        agent.check_user_token = Mock(side_effect=AppException("999-00004", ["x -> 500:err"], []))

        with pytest.raises(AppException):
            agent.update_gitlab_userinfo(self.user_info)

        db.db_rollback.assert_called_once()
        db.db_disconnect.assert_called_once()

    def test_db_update_error_rollback(self, agent, db):
        agent.check_user_token = Mock(return_value=False)
        agent.create_personal_access_tokens = Mock(return_value="new-token")
        db.sql_execute.side_effect = [[dict(self.connect_info)], RuntimeError("db error")]

        with pytest.raises(RuntimeError):
            agent.update_gitlab_userinfo(self.user_info)

        db.db_commit.assert_not_called()
        db.db_rollback.assert_called_once()
        db.db_disconnect.assert_called_once()
        assert g.gitlab_connect_info["GITLAB_TOKEN"] == "db-token"

    def test_db_connect_error_no_rollback(self, agent):
        """DB接続自体に失敗した場合は rollback/disconnect を呼ばず例外を送出"""
        with patch.object(gitlab_module, "DBConnectCommon", side_effect=RuntimeError("connect error")):
            with pytest.raises(RuntimeError):
                agent.update_gitlab_userinfo(self.user_info)

    def test_select_no_rows_rollback(self, agent, db):
        """対象組織のレコードが無い場合(IndexError)はrollbackして送出"""
        db.sql_execute.return_value = []

        with pytest.raises(IndexError):
            agent.update_gitlab_userinfo(self.user_info)

        db.db_rollback.assert_called_once()
        db.db_disconnect.assert_called_once()
