# Ansible Legacy Default Playbook - System_user_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 550
- **playbook_name**: ~[Exastro standard] Remove user
- **playbook_file**: System_user_remove.yml
## Overview
Deletes one or more OS user accounts on the target host and removes their home directories using Ansible's user module.
## Description
This Playbook deletes users specified by "ITA_DFLT_User_Names", and also removes their home directories and mail spool.
"ITA_DFLT_User_Names" can specify multiple users (list type).
## Keyword
- user deletion
- delete home directory
- account cleanup
## Playbook
```yaml
- name: Remove user
  user:
    name: "{{ item }}"
    state: absent
    remove : yes
  with_items:
    - "{{ ITA_DFLT_User_Names }}"
```
