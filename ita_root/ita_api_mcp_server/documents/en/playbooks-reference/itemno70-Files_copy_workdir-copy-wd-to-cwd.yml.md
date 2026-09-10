# Ansible Legacy Default Playbook - Files_copy_workdir-copy-wd-to-cwd.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 70
- **playbook_name**: ~[Exastro standard] Copy directory (WD to CWD)
- **playbook_file**: Files_copy_workdir-copy-wd-to-cwd.yml
## Overview
Copies all files from the local `__workflowdir__` directory to the `__conductor_workflowdir__` directory using a local `copy` action, run on the Ansible control node.
## Description
This Playbook file copies files stored in "__workflowdir__" to "__conductor_workflowdir__".
The "__conductor_workflowdir__" files are accesible from subsequent Movements are the Movement ends.
Use this for transfering information over Movements.
Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
## Keyword
- workflow directory copy
- conductor workflow directory
- cross-movement data transfer
- local file copy
## Playbook
```yaml
# This Playbook file copies files stored in "__workflowdir__" to "__conductor_workflowdir__".
# The "__conductor_workflowdir__" files are accesible from subsequent Movements are the Movement ends.
# Use this for transfering information over Movements.
# Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
- name: Copy data from workdir to conductor_workdir
  local_action:
    module: copy
    src: "{{ __workflowdir__ }}/"
    dest: "{{ __conductor_workflowdir__ }}/"
```
