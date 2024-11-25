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
import importlib

import job_config as config
from jobs.base_job_executor import BaseJobExecutor

class JobClasses():
    """JOB実行のclassへのアクセスclass / Access class for job execution class
    """

    # JOBのexecutor classをimportする / Import JOB executor class
    __job_executor_classes = {}
    for __job_name, __job_config in config.JOB_CONFIG.items():
        __job_executor_classes[__job_name] = getattr(importlib.import_module(__job_config["module"]), __job_config["class"])

    @classmethod
    def get_job_executor_class(cls, job_name: str) -> type[BaseJobExecutor]:
        """get job executor class

        Args:
            job_name (str): job name

        Returns:
            type[BaseJobExecutor]: job executor class
        """
        return cls.__job_executor_classes[job_name]
