# Customizing the Ansible Execution Environment
# Introduction
This document explains how to customize the Ansible execution environment used by ITA.
# Overview of Ansible Execution Environment Customization
- | Examples of customization with Ansible Core
  - | Example of adding a customization step to the build during Ansible work (docker-compose version only)
    - | Example using a collection
    - | Example using a custom-written module
  - | Example of using an image with customizations applied during Ansible work
- | Examples of customization with Ansible Execution Agent or Ansible Automation Platform
  - | Example using a collection (free-version base image)
  - | Example using a collection (paid-version base image)
  - | Example using a custom-written module
# Examples of Customization with Ansible Core

## Example of Adding a Customization Step to the Build During Ansible Work
Because this procedure adds a customization step to the build during Ansible work, this procedure applies only to the "docker-compose version."

### Checking existing environment variables
Check the existing environment variables.

### Removing the existing image

### Editing the build file

#### Example using a collection
This is the procedure for adding collections other than the ones below, and for installing libraries required by a collection.
   ---------------------------------------- -------

#### Example using a custom-written module
   -rw-r--r--. 1 user01 user01 1024 Jan 1 00:00 ~/exastro-docker-compose/ita_by_ansible_execute/templates/work/my_module.py

## Example of Using an Image with Customizations Applied During Ansible Work

### Exporting the customized image

### Deploying the customized image

#### docker-compose version
After confirming the image, configure the environment variable so that Ansible-Core uses the target image during Ansible work.
   - # ANSIBLE_AGENT_IMAGE=my-exastro-ansible-agent
   - # ANSIBLE_AGENT_IMAGE_TAG=
After editing the environment variable, run `~/exastro-docker-compose/setup.sh` to apply the changes.

#### Kubernetes version
After deploying the image, configure the environment variable so that Ansible-Core uses the target image during Ansible work.
   -     ANSIBLE_AGENT_IMAGE: "docker.io/exastro/exastro-it-automation-by-ansible-agent"
   -     ANSIBLE_AGENT_IMAGE_TAG: ""
# Examples of Customization with Ansible Execution Agent

## Example Using a Collection (Free-Version Base Image)
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.access.redhat.com/ubi9/ubi-init:latest"
  - | The collection used is "Azure.AzCollection"

### Registering the execution environment definition in ITA
Register the execution environment definition template file in Ansible Common --> Execution Environment Definition Template Management.
  List of parameters to configure in Ansible Common --> Execution Environment Definition Template Management
Item name                                    | Setting value                                                                          | Notes                                                                                    |
Template file                               | Register the following content.                                                       | The `ansible_core` version required in the future may change.           |
Register the association between the execution environment definition template file and the setting values to substitute into the template file in Ansible Common --> Execution Environment Management.
  List of parameters to configure in Ansible Common --> Execution Environment Management
Item name                   | Setting value                            | Notes                                                                             |
Execution environment build method | ITA                              | -                                                                                 |
Execution environment definition name | Execution Environment Parameter Definition/~[Exastro standa\| Uses the data provided as initial data.                                  |
Template name               | azure_ee_template                       | Template name in Ansible Common --> Execution Environment Definition Template Management    |
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | azure_ee_ubi9                                                               | Execution environment name in Ansible Common --> Execution Environment Management  |
ansible-\ | Enter ansible-builder parameters if\                                        | Normally no setting is required.                             |
builder\  | needed when building the execution environment with ansible-builder.       |                                                             |

## Example Using a Collection (Paid-Version Base Image)
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest"
  - | The collection used is "Azure.AzCollection"

### Preparation on the Ansible Execution Agent

### Registering the execution environment definition in ITA
Register the setting values to substitute into the execution environment definition template file in Input --> Execution Environment Parameter Definition.
  List of parameters to configure in Input --> Execution Environment Parameter Definition
Item name                                    | Setting value                                                              | Notes                                                                                    |
bindep_file                                 | Register the following content.                                            | -                                                                                       |
Register the execution environment definition template file in Ansible Common --> Execution Environment Definition Template Management.
  List of parameters to configure in Ansible Common --> Execution Environment Definition Template Management
Item name                                    | Setting value                                                                          | Notes                                                                                    |
Template file                               | Register the following content.                                                       | The `ansible_core` version required in the future may change.           |
Register the association between the execution environment definition template file and the setting values to substitute into the template file in Ansible Common --> Execution Environment Management.
  List of parameters to configure in Ansible Common --> Execution Environment Management
Item name                   | Setting value                            | Notes                                                                             |
Execution environment build method | ITA                              | -                                                                                 |
Execution environment definition name | Execution Environment Parameter Definition/azure_ee         |  execution_environment_name in Input --> Execution Environment Parameter Definition  |
Template name               | azure_ee_template                       |  Template name in Ansible Common --> Execution Environment Definition Template Management   |
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | azure_ee                                                                    | Execution environment name in Ansible Common --> Execution Environment Management  |
ansible-\ | Enter ansible-builder parameters if\                                        | Normally no setting is required.                             |
builder\  | needed when building the execution environment with ansible-builder.       |                                                             |

## Example Using a Custom-Written Module
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.access.redhat.com/ubi9/ubi-init:latest"
  - | The custom-written module used is `/tmp/ansible_module/my_module.py`

### Placing the custom-written module
   -rw-r--r--. 1 userA userA 1024 Jan 1 00:00 /tmp/ansible_module/my_module.py

### Registering the execution environment definition in ITA
Register the execution environment definition template file in Ansible Common --> Execution Environment Definition Template Management.
  List of parameters to configure in Ansible Common --> Execution Environment Definition Template Management
Item name                                    | Setting value                                                                               | Notes                                                                                    |
Template file                               | Register the following content.                                                            | If the custom-written module's file path differs,\                                       |
Register the association between the execution environment definition template file and the setting values to substitute into the template file in Ansible Common --> Execution Environment Management.
  List of parameters to configure in Ansible Common --> Execution Environment Management
Item name                   | Setting value                                                                    | Notes                                                                             |
Execution environment build method | ITA                                                                       | -                                                                                 |
Execution environment definition name | Execution Environment Parameter Definition/~[Exastro standard] default (no galaxy collection)        |  Uses the data provided as initial data.                                 |
Template name               | my_module_ubi9_template                                                          |  Template name in Ansible Common --> Execution Environment Definition Template Management   |
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | my_module_ubi9                                                              | Execution environment name in Ansible Common --> Execution Environment Management  |
ansible-\ | Enter ansible-builder parameters if\                                        | Normally no setting is required.                             |
builder\  | needed when building the execution environment with ansible-builder.       |                                                             |
# Examples of Customization with Ansible Automation Platform

## Example Using a Collection (Free-Version Base Image)
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.access.redhat.com/ubi9/ubi-init:latest"
  - | The collection used is "Azure.AzCollection"

### Installing ansible-builder

### Preparing the required files
- | execution-environment.yml
  - The ansible-builder definition file
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | galaxy-requirements.yml
  - File that lists the ansible-galaxy collections to install
     - azure.azcollection
- | python-requirements.txt
  - File that lists the Python requirements needed to resolve Python dependencies
- | bindep.txt
  - File that lists package requirements needed to resolve system-level dependencies

### Running ansible-builder

### Copying the custom image for the ControlNode's awx user

### Copying the custom image for the ExecutionNode's awx user

### Registering the execution environment in AAP
Register the execution environment configuration that uses the copied custom image in Ansible Automation Platform.

### Registering the execution environment in ITA
Register the execution environment configuration in ITA.
The environment name to register is the name registered in AAP (azure_ee_ubi9 in the example above).
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | e.g.) azure_ee_ubi9                                                         | The execution environment name registered in "Registering the execution environment in AAP"   |

## Example Using a Collection (Paid-Version Base Image)
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.redhat.io/ansible-automation-platform-24/ee-minimal-rhel9:latest"
  - | The collection used is "Azure.AzCollection"

### Installing ansible-builder

### Preparing the required files
- | execution-environment.yml
  - The ansible-builder definition file
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | galaxy-requirements.yml
  - File that lists the ansible-galaxy collections to install
     - azure.azcollection
- | python-requirements.txt
  - File that lists the Python requirements needed to resolve Python dependencies
- | bindep.txt
  - File that lists package requirements needed to resolve system-level dependencies

### Running ansible-builder

### Copying the custom image for the ControlNode's awx user

### Copying the custom image for the ExecutionNode's awx user

### Registering the execution environment in AAP
Register the execution environment configuration that uses the copied custom image in Ansible Automation Platform.

### Registering the execution environment in ITA
Register the execution environment configuration in ITA.
The environment name to register is the name registered in AAP (azure_ee in the example above).
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | e.g.) azure_ee                                                              | The execution environment name registered in "Registering the execution environment in AAP"   |

## Example Using a Custom-Written Module
- | In this case, customization is applied under the following conditions.
  - | The base image used is "registry.access.redhat.com/ubi9/ubi-init:latest"
  - | The custom-written module used is `/tmp/ansible_module/my_module.py`

### Placing the custom-written module
   -rw-r--r--. 1 root root 1024 Jan 1 00:00 /tmp/ansible_module/my_module.py

### Installing ansible-builder

### Preparing the required files
- | execution-environment.yml
  - The ansible-builder definition file
     - src: /tmp/ansible_module/my_module.py
       - COPY _build/configs/my_module.py /usr/share/ansible/plugins/modules/
       - RUN /usr/bin/python3.11 -m pip install --upgrade pip
- | python-requirements.txt
  - File that lists the Python requirements needed to resolve Python dependencies
- | bindep.txt
  - File that lists package requirements needed to resolve system-level dependencies

### Running ansible-builder

### Copying the custom image for the ControlNode's awx user

### Copying the custom image for the ExecutionNode's awx user

### Registering the execution environment in AAP
Register the execution environment configuration that uses the copied custom image in Ansible Automation Platform.

### Registering the execution environment in ITA
Register the execution environment configuration in ITA.
The environment name to register is the name registered in AAP (my_module_ubi9_image in the example above).
Register the execution environment configuration for the Movement (the Ansible work Movement to be executed) in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List.
Parameters not related to execution environment configuration are omitted.
  List of parameters to configure in Ansible[Legacy/Pioneer/Legacy-Role] --> Movement List
Item name                           | Setting value                                                               | Notes                                                       |
MovementID                          | (omitted)                                                                   | -                                                          |
Movement name                       | (omitted)                                                                   | -                                                          |
Option parameters       | (omitted)                                                                   | -                                                          |
Ansible \  | Execution environment | e.g.) my_module_ubi9_image                                                  | The execution environment name registered in "Registering the execution environment in AAP"   |
