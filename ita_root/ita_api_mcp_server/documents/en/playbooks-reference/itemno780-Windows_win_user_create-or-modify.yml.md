# Ansible Legacy Default Playbook - Windows_win_user_create-or-modify.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 780
- **playbook_name**: ~[Exastro standard][Win] Add user
- **playbook_file**: Windows_win_user_create-or-modify.yml
## Overview
Creates (or updates) local Windows user accounts with specified passwords and adds each user to a corresponding group, using paired lists of usernames, passwords, and groups.
## Description
This Playbook file creates the users specified with "ITA_DFLT_Win_User_Name" with the passwords specified with "ITA_DFLT_Win_Password". The users are put in the groups specified by "ITA_DFLT_Win_Groups".
"ITA_DFLT_Win_User_Name" can specify multiple templates (list type).
"ITA_DFLT_Win_Password" can specify multiple files (list type).
"ITA_DFLT_Win_Groups" can specify multiple files (list type).
## Keyword
- Windows local user creation
- win_user module
- batch account provisioning
- user group assignment
- password setup
## Playbook
```yaml
# This Playbook file creates the users specified with "ITA_DFLT_Win_User_Name" with the passwords specified with "ITA_DFLT_Win_Password". The users are put in the groups specified by "ITA_DFLT_Win_Groups".
# "ITA_DFLT_Win_User_Name" can specify multiple templates (list type).
# "ITA_DFLT_Win_Password" can specify multiple files (list type).
# "ITA_DFLT_Win_Groups" can specify multiple files (list type).
- name: Add user
  ansible.windows.win_user:
    name: "{{ item.0 }}"
    password: "{{ item.1 }}"
    state: present
    groups: "{{ item.2 }}"
  with_together:
    - "{{ ITA_DFLT_Win_User_Name }}"
    - "{{ ITA_DFLT_Win_Password }}"
    - "{{ ITA_DFLT_Win_Groups }}"
```
