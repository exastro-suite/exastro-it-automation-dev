# Ansible Legacy Default Playbook - Windows_win_file_mkdir.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 820
- **playbook_name**: ~[Exastro standard][Win] Create folder
- **playbook_file**: Windows_win_file_mkdir.yml
## Overview
Creates one or more directories on a remote Windows host using the win_file module with state set to directory.
## Description
- `ITA_DFLT_Create_Directory`: the directory path(s) to create on the remote Windows host (list type, multiple values can be specified).
## Keyword
- Windows folder creation
- win_file module
- directory provisioning
- filesystem setup
## Playbook
```yaml
- name: Create folders
  win_file:
    path: "{{ item }}"
    state: directory
  with_items:
    - "{{ ITA_DFLT_Create_Directory }}"
```
