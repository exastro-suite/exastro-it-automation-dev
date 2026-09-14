# Ansible Legacy Default Playbook - System_authorized_key_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 30
- **playbook_name**: ~[Exastro standard] Add Authorized key
- **playbook_file**: System_authorized_key_add.yml
## Overview
Uses the Ansible `authorized_key` module to register an SSH public key into each user's authorized_keys file, pairing users and keys one-to-one via `with_together`, setting state to present.
## Description
This Playbook file registers SSH authentication keys specified by "ITA_DFLT_Authorized_Keys" to users specified by "ITA_DFLT_Users".
"ITA_DFLT_Users" can specify multiple users (list type).
"ITA_DFLT_Authorized_Keys" can specify multiple SSH authentication keys (list type).
## Keyword
- SSH public key registration
- authorized_keys file setup
- passwordless SSH login setup
## Playbook
```yaml
- name: Add authorized key
  authorized_key:
    user: "{{ item.0 }}"
    key: "{{ item.1 }}"
    state: present
  with_together:
    - "{{ ITA_DFLT_Users }}"
    - "{{ ITA_DFLT_Authorized_Keys }}"
```
