# Ansible Legacy Default Playbook - Windows_win_owner_recursive.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 920
- **playbook_name**: ~[Exastro standard][Win] Modify owner (with recursion)
- **playbook_file**: Windows_win_owner_recursive.yml
## Overview
Changes the owner of specified Windows folders to a given user, recursively applying the change to all subfolders and files.
## Description
"ITA_DFLT_Change_owner_paths": Path of the folder whose owner is to be changed.
"ITA_DFLT_Change_owner_users": User (or group) to set as the new owner of the corresponding path.
Each of the variables can have multiple values specified at the same time (list type), and the values are paired positionally between the two lists.
## Keyword
- Windows file ownership
- Recursive owner change
- Set folder owner
## Playbook
```yaml
- name: Change the owner of folders recursively.
  win_owner:
    path: "{{ item.0 }}"
    user: "{{ item.1 }}"
    recurse: true
  with_together:
    - "{{ ITA_DFLT_Change_owner_paths }}"
    - "{{ ITA_DFLT_Change_owner_users }}"

```
