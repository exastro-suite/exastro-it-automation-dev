#!/bin/bash
#   Copyright 2022 NEC Corporation
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

BASENAME=$(basename "$0")
BASEPATH=$(dirname "$0")

export PLATFORM_API_ORIGIN=http://platform-api:8000
export DB_ADMIN_USER=root
export DB_ADMIN_PASSWORD=password
export UNITTEST_DB_HOST=unittest-ita-db

export TESTDATA_PYTHON=$(realpath "${BASEPATH}/../db/exports/${ITA_DBMS}/testdata.py")
export TESTDATA_DATABASE_DUMP=$(realpath "${BASEPATH}/../db/exports/${ITA_DBMS}/pytest1_init_databases.sql")
export TEST_RESTORE_DATABASE_DUMP=$(realpath "${BASEPATH}/../db/exports/${ITA_DBMS}/pytest2_restore_databases.sql")
export TESTDATA_CREATEUSER_SQL=$(realpath "${BASEPATH}/../db/exports/${ITA_DBMS}/pytest9_database_users.sql")

echo "※注意※"
echo "本scriptはDBを初期化(migration直後)した状態で実行してください"
echo "また、テスト用のデータはmariadb,mysql双方で2回実施する必要があります"
echo ".envをmariadb設定でmigration後に本scriptを実行し、.envをmysql設定に切り替えてmigration後に本scriptを実行してください"

read -p "実行しますか? (Y/other):" CONFIRM
if [ "${CONFIRM}" != "Y" ]; then
    exit 1
fi

echo

python3 ${BASEPATH}/make_tests_db_exports.py
