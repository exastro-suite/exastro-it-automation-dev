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
ARG WORK_PATH=/tmp

FROM    registry.access.redhat.com/ubi9/ubi-init:9.4 AS common_build
ARG USERNAME
ARG GROUPNAME
ARG WORK_PATH

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    dnf install -y \
    openssh-clients \
    python3.12 \
    python3.12-devel \
    python3.12-pip \
    sshpass \
&&  pip3.12 install poetry==1.8.4 \
&&  poetry config virtualenvs.create false \
&&  groupadd $GROUPNAME \
&&  useradd -m -s /bin/bash -g $GROUPNAME $USERNAME

RUN alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1000000 \
&&  alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 31200 \
&&  alternatives --set python3 /usr/bin/python3.12

WORKDIR $WORK_PATH

COPY ./ita_root/ita_by_ansible_execute/ita_ansible_agent/pyproject.toml ./ita_root/ita_by_ansible_execute/ita_ansible_agent/poetry.lock $WORK_PATH/

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    poetry install --only first_install

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    poetry install

COPY ./ita_root/ita_by_ansible_execute/ita_ansible_agent/config/centos8.repo /etc/yum.repos.d/centos8.repo

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    dnf install -y --enablerepo=baseos expect

RUN --mount=type=secret,id=host_certificate_file,dst=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem \
    dnf install -y --enablerepo=appstream telnet

COPY ./ita_root/ita_by_ansible_execute/ita_ansible_agent/config/ansible.cfg /etc/ansible/ansible.cfg

USER $USERNAME

ENTRYPOINT ["sh"]
