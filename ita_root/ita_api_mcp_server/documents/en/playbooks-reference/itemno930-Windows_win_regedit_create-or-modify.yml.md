# Ansible Legacy Default Playbook - Windows_win_regedit_create-or-modify.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 930
- **playbook_name**: ~[Exastro standard][Win] Modify/add registry
- **playbook_file**: Windows_win_regedit_create-or-modify.yml
## Overview
Creates or updates Windows registry keys and entries, setting the path, entry name, value data, and value type for each entry using win_regedit.
## Description
This Playbook file adds or edits registry keys and values.
The variables are as follows:
"ITA_DFLT_Regedit_Path": Registry Path name
"ITA_DFLT_Regedit_Name": Registry Entry name
"ITA_DFLT_Regedit_Data": Registry Entry value
"ITA_DFLT_Regedit_Type": Registry value Data type
Each of the variables can have multiple specified at the same time (list type).
## Keyword
- Windows registry editing
- Registry key creation
- Registry value type
## Playbook
```yaml
# This Playbook file adds or edits registry keys and values.
# The variables are as follows:
# "ITA_DFLT_Regedit_Path": Registry Path name
# "ITA_DFLT_Regedit_Name": Registry Entry name
# "ITA_DFLT_Regedit_Data": Registry Entry value
# "ITA_DFLT_Regedit_Type": Registry value Data type
# Each of the variables can have multiple specified at the same time (list type).
- name: Add, change registry keys and values
  ansible.windows.win_regedit:
    path: "{{ item.0 }}"
    name: "{{ item.1 }}"
    data: "{{ item.2 }}"
    type: "{{ item.3 }}"
  with_together:
    - "{{ ITA_DFLT_Regedit_Path }}"
    - "{{ ITA_DFLT_Regedit_Name }}"
    - "{{ ITA_DFLT_Regedit_Data }}"
    - "{{ ITA_DFLT_Regedit_Type }}"
```
