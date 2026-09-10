# Ansible Legacy Default Playbook - Files_file_modify.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 480
- **playbook_name**: ~[Exastro standard] Modify permissions
- **playbook_file**: Files_file_modify.yml
## Overview
Changes file or directory permissions (mode) for one or more paths on the target host using Ansible's file module.
## Description
This Playbook file changes permissions specified by "ITA_DFLT_Mode" for the files/directories specified by "ITA_DFLT_Target_Path".
"ITA_DFLT_Target_Path" can specify multiple files/directories (list type).
"ITA_DFLT_Mode" can specify multiple permissions (list type).
## Keyword
- file permission change
- chmod
- access control
## Playbook
```yaml
- name: Modify permission
  file:
    path: "{{ item.0 }}"
    mode: "{{ item.1 }}"
  with_together:
    - "{{ ITA_DFLT_Target_Path }}"
    - "{{ ITA_DFLT_Mode }}"
```
