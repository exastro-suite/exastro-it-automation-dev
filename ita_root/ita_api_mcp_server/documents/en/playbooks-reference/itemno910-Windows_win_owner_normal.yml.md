# Ansible Legacy Default Playbook - Windows_win_owner_normal.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 910
- **playbook_name**: ~[Exastro standard][Win] Modify owner (no recursion)
- **playbook_file**: Windows_win_owner_normal.yml
## Overview
Changes the owner of specified Windows files or folders to a given user, without applying the change recursively to subfolders/files.
## Description
"ITA_DFLT_Change_owner_paths": Path of the file or folder whose owner is to be changed.
"ITA_DFLT_Change_owner_users": User (or group) to set as the new owner of the corresponding path.
Each of the variables can have multiple values specified at the same time (list type), and the values are paired positionally between the two lists.
## Keyword
- Windows file ownership
- Set folder owner
- Non-recursive ownership change
## Playbook
```yaml
- name: Change the owner of folders or files.
  win_owner:
    path: "{{ item.0 }}"
    user: "{{ item.1 }}"
    recurse: false
  with_together:
    - "{{ ITA_DFLT_Change_owner_paths }}"
    - "{{ ITA_DFLT_Change_owner_users }}"

```
