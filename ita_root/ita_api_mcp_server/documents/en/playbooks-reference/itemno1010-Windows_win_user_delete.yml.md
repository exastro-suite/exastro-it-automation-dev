# Ansible Legacy Default Playbook - Windows_win_user_delete.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1010
- **playbook_name**: ~[Exastro standard][Win] Remove user
- **playbook_file**: Windows_win_user_delete.yml
## Overview
Uses the `ansible.windows.win_user` module with `state: absent` to delete one or more local user accounts on a Windows host, iterating over a list of usernames.
## Description
This Playbook file deletes users specified by "ITA_DFLT_Win_User_Name".
"ITA_DFLT_Win_User_Name" can specify multiple user names (list type).
## Keyword
- user account removal
- Windows local user deletion
- account deprovisioning
## Playbook
```yaml
# This Playbook file deletes users specified by "ITA_DFLT_Win_User_Name".
# "ITA_DFLT_Win_User_Name" can specify multiple user names (list type).
- name: Delete user
  ansible.windows.win_user:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Win_User_Name }}"
```
