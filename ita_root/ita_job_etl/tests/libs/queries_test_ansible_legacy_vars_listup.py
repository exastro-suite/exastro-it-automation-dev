
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

SQL_INSERT_ANSL_MATL_COLL = """
INSERT INTO `T_ANSL_MATL_COLL`
(`PLAYBOOK_MATTER_ID`,
`PLAYBOOK_MATTER_NAME`,
`PLAYBOOK_MATTER_FILE`,
`DISUSE_FLAG`,
`LAST_UPDATE_TIMESTAMP`,
`LAST_UPDATE_USER`)
VALUES
(%(PLAYBOOK_MATTER_ID)s,
%(PLAYBOOK_MATTER_NAME)s,
%(PLAYBOOK_MATTER_FILE)s,
%(DISUSE_FLAG)s,
%(LAST_UPDATE_TIMESTAMP)s,
%(LAST_UPDATE_USER)s);
"""