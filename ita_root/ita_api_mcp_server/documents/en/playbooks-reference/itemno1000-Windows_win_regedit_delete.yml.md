# Ansible Legacy Default Playbook - Windows_win_regedit_delete.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1000
- **playbook_name**: ~[Exastro standard][Win] Remove registry
- **playbook_file**: Windows_win_regedit_delete.yml
## Overview
Uses the `ansible.windows.win_regedit` module with `state: absent` to delete Windows registry entries, pairing registry paths and entry names from two lists with `with_together`.
## Description
This Playbook file deletes the Registry key.
The variables are as follows:
"ITA_DFLT_Regedit_Path": Registry Path name
"ITA_DFLT_Regedit_Name": Registry Entry name
Each of the variables can have multiple specified at the same time (list type).
## Keyword
- regedit
- registry maintenance
- Windows registry cleanup
- registry value removal
## Playbook
```yaml
# This Playbook file deletes the Registry key. 
# The variables are as follows: 
# "ITA_DFLT_Regedit_Path": Registry Path name
# "ITA_DFLT_Regedit_Name": Registry Entry name
# Each of the variables can have multiple specified at the same time (list type).
- name: remove registry keys and values
  ansible.windows.win_regedit:
    path: "{{ item.0 }}"
    name: "{{ item.1 }}"
    state: absent
  with_together:
    - "{{ ITA_DFLT_Regedit_Path }}"
    - "{{ ITA_DFLT_Regedit_Name }}"
```
