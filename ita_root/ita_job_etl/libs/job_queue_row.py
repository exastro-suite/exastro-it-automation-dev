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

class JobQueueRow():
    """queueのレコードclass / queue record class
    """
    def __init__(self, row: dict):
        """constructor

        Args:
            row (dict): job queue record
        """
        self.organization_id = row.get('ORGANIZATION_ID', None)
        self.workspace_id = row.get('WORKSPACE_ID', None)
        self.job_name = row.get('JOB_NAME', None)
        self.job_key = row.get('JOB_KEY', None)
        self.queue_time = row.get('LAST_UPDATE_TIMESTAMP', None)
        self.__row = row
