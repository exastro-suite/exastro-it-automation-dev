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
ARG USERNAME=app_user
ARG GROUPNAME=app_user
ARG APP_PATH=/exastro

FROM    registry.access.redhat.com/ubi8/ubi-init as common_build
ARG USERNAME
ARG GROUPNAME
ARG APP_PATH
ENV PYTHONPATH=/exastro/
ENV USER_ID=50101
ENV EXECUTE_INTERVAL=1
ENV LANGUAGE=en
ENV STORAGEPATH=/storage/
ENV SERVICE_NAME=ita-job-etl

ENV FILE_PATH_LIVENESS=/tmp/liveness

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    dnf install -y \
    gcc \
    python39 \
    python39-devel \
    python39-mod_wsgi \
    langpacks-en \
    wget \
    unzip \
&&  pip3.9 install poetry==1.6.0 \
&&  poetry config virtualenvs.create false \
&&  groupadd $GROUPNAME \
&&  useradd -m -s /bin/bash -g $GROUPNAME $USERNAME

WORKDIR $APP_PATH

COPY ./ita_root/ita_job_etl/pyproject.toml ./ita_root/ita_job_etl/poetry.lock $APP_PATH/

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    poetry install --only first_install

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    poetry install --without develop_build

#
# JOB default Settings
#

# sub processの起動数（sub process交代のタイミングでこの数を超えることがあります）
# Number of sub processes started (this number may be exceeded when sub processes are replaced)
ENV SUB_PROCESS_ACCEPTABLE=2

# sub processの再起動（別の新プロセス起動）の間隔のデフォルト値
# JOBの最大のtimeout時間の1.5倍もしくはデフォルト値が設定される
# Default value for restarting sub process (starting another new process) interval
# 1.5 times the maximum timeout time of JOB or default value is set
ENV SUB_PROCESS_ACCEPTABLE_SECONDS_DEFAULT=7200

# メイン処理の実行間隔
# この間隔でprocessやthreadの状態の監視、および各種間隔実行の時間経過を確認する
# （他の間隔指定は本間隔単位以下にしても機能しません）
#
# Execution interval of main processing
# Monitor the status of processes and threads at this interval, and check the time elapsed for various interval executions
# (Other interval specifications will not work even if they are less than this interval unit)
ENV SUB_PROCESS_WATCH_INTERVAL_SECONDS=1

# QUEUE監視のDBへの再接続間隔
# Reconnection interval to DB for QUEUE monitoring
ENV SUB_PROCESS_DB_RECONNECT_INTERVAL_SECONDS=30

# 例外発生後の処理再開までの間隔（エラーログのラッシュ防止用）
# Interval until processing resumes after an exception occurs (to prevent error log rush)
ENV EXCEPTION_RESTART_INTERVAL_SECONDS=5

# sub process当たりの最大同時実行JOB数
# Maximum number of concurrently executing jobs per sub process
ENV MAX_JOB_PER_PROCESS=3

# QUEUE read interval
ENV QUEUE_WATCH_INTERVAL_SECONDS=3

# メンテナンスモードのチェック間隔
# Maintenance mode check interval
ENV MAINTENANCE_MODE_CHECK_INTERVAL_SECONDS=10

# CLEAN UP call interval
ENV CLEANUP_INTERVAL_SECONDS=3600

# JOB CANCEL Timeout time
ENV JOB_CANCEL_TIMEOUT_SECONDS=3

# Log Level resetting interval
ENV RESET_LOG_LEVEL_INTERVAL_SECONDS=10

# menu_create job timeout seconds
ENV JOB_MENU_CREATE_TIMEOUT_SECONDS=20

# ansible_legacy_vars_listup job timeout seconds
ENV JOB_ANSIBLE_LEGACY_VARS_LISTUP_TIMEOUT_SECONDS=300

# ansible_pioneer_vars_listup job timeout seconds
ENV JOB_ANSIBLE_PIONEER_VARS_LISTUP_TIMEOUT_SECONDS=300

# ansible_legacy_role_vars_listup job timeout seconds
ENV JOB_LEGACY_ROLE_VARS_LISTUP_TIMEOUT_SECONDS=300

#
# Build for development
#   Specify options when creating this image: --target develop_build
#
FROM    common_build as develop_build
ARG USERNAME
ARG GROUPNAME
ARG APP_PATH

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    dnf install -y \
    sudo \
    git \
    vim \
    diffutils \
    bind-utils \
    iputils \
&&  usermod -G wheel $USERNAME \
&&  echo '%wheel ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers \
&&  echo "%${GROUPNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    poetry install --with develop_build

USER $USERNAME

RUN mkdir ~/.config \
&& mkdir ~/.vscode-server \
&& mkdir ~/.vscode-server-insiders

WORKDIR $APP_PATH

COPY ./ita_root/ita_job_etl/ $APP_PATH/
COPY ./ita_root/common_libs/ $APP_PATH/common_libs/
COPY ./ita_root/messages/ $APP_PATH/messages/
# COPY ./ita_root/backyard/ $APP_PATH/backyard/

ENTRYPOINT ["python3","./job_manager.py"]

#
# Build for production
#
FROM    common_build
ARG USERNAME
ARG GROUPNAME
ARG APP_PATH

USER $USERNAME
WORKDIR $APP_PATH

COPY ./ita_root/ita_job_etl/ $APP_PATH/
COPY ./ita_root/common_libs/ $APP_PATH/common_libs/
COPY ./ita_root/messages/ $APP_PATH/messages/
# COPY ./ita_root/backyard/ $APP_PATH/backyard/

ENTRYPOINT ["python3","./job_manager.py"]
