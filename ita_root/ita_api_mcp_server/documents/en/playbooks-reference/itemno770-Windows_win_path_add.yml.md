# Ansible Legacy Default Playbook - Windows_win_path_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 770
- **playbook_name**: ~[Exastro standard][Win] Add path
- **playbook_file**: Windows_win_path_add.yml
## Overview
Uses the `ansible.windows.win_path` module to add a path element to one or more specified Windows environment variables at a given scope, pairing variable name, element, and scope by list position.
## Description
This Playbook file adds the environment variable names specified by "ITA_DFLT_Environment_Name" with the path element specified by "ITA_DFLT_Elements".
"ITA_DFLT_Scope" specifies the level at which the specified environment variable must be managed.
Each of the variables can have multiple specified at the same time (list type).
## Keyword
- windows path variable
- environment variable management
- win_path module
- path element addition
## Playbook
```yaml
# This Playbook file adds the environment variable names specified by "ITA_DFLT_Environment_Name" with the path element specified by "ITA_DFLT_Elements". 
# "ITA_DFLT_Scope" specifies the level at which the specified environment variable must be managed.
# Each of the variables can have multiple specified at the same time (list type).
- name: add Windows path environment variables
  ansible.windows.win_path:
    name: "{{ item.0 }}"
    elements: "{{ item.1 }}"
    scope: "{{ item.2 }}"
    state: present
  with_together:
    - "{{ ITA_DFLT_Environment_Name }}"
    - "{{ ITA_DFLT_Elements }}"
    - "{{ ITA_DFLT_Scope }}"
```
