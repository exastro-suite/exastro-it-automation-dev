# Ansible Legacy Default Playbook - System_user_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 60
- **playbook_name**: ~[Exastro standard] Add user
- **playbook_file**: System_user_add.yml
## Overview
Creates OS user accounts on target hosts and assigns each user to a corresponding group, pairing user names with group names by list position.
## Description
This Playbook file registers users specified by "ITA_DFLT_User_Names" to groups specified by "ITA_DFLT_User_Group_Names".
"ITA_DFLT_User_Names" can specify multiple users (list type).
"ITA_DFLT_Group_Names" can specify multiple groups (list type).
## Keyword
- create user account
- OS account provisioning
- group assignment
## Playbook
```yaml
- name: Add user
  user:
    name: "{{ item.0 }}"
    group: "{{ item.1 }}"
    state: present 
  with_together:
    - "{{ ITA_DFLT_User_Names }}"
    - "{{ ITA_DFLT_User_Group_Names }}"

```
