# Ansible Legacy Default Playbook - Windows_win_path_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 990
- **playbook_name**: ~[Exastro standard][Win] Remove path
- **playbook_file**: Windows_win_path_remove.yml
## Overview
Removes specified path elements from a named Windows environment variable (e.g. PATH) at a given scope, using the win_path module with state absent.
## Description
This Playbook file removes the environment variable names specified by "ITA_DFLT_Environment_Name" with the path element specified by "ITA_DFLT_Elements".
"ITA_DFLT_Scope" specifies the level at which the specified environment variable must be managed.
Each of the variables can have multiple specified at the same time (list type).
## Keyword
- Windows environment variable
- PATH element removal
- User or machine scope
## Playbook
```yaml
# This Playbook file removes the environment variable names specified by "ITA_DFLT_Environment_Name" with the path element specified by "ITA_DFLT_Elements".
# "ITA_DFLT_Scope" specifies the level at which the specified environment variable must be managed.
# Each of the variables can have multiple specified at the same time (list type).
- name: remove Windows path environment variables
  ansible.windows.win_path:
    name: "{{ item.0 }}"
    elements: "{{ item.1 }}"
    scope: "{{ item.2 }}"
    state: absent
  with_together:
    - "{{ ITA_DFLT_Environment_Name }}"
    - "{{ ITA_DFLT_Elements }}"
    - "{{ ITA_DFLT_Scope }}"
```
