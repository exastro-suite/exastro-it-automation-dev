# Ansible Legacy Default Playbook - System_authorized_key_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 520
- **playbook_name**: ~[Exastro standard] Remove Authorized key
- **playbook_file**: System_authorized_key_remove.yml
## Overview
Removes specified SSH public keys from the authorized_keys file of specified users on the target host using Ansible's authorized_key module.
## Description
This Playbook file removes SSH authentication keys specified by "ITA_DFLT_Authorized_Keys" from users specified by "ITA_DFLT_Users".
"ITA_DFLT_Users" can specify multiple users (list type).
"ITA_DFLT_Authorized_Keys" can specify multiple SSH authentication keys (list type).
## Keyword
- SSH key removal
- revoke SSH access
- authorized_keys management
## Playbook
```yaml
- name: Remove authorized key
  authorized_key:
    user: "{{ item.0 }}"
    key: "{{ item.1 }}"
    state: absent
  with_together:
    - "{{ ITA_DFLT_Users }}"
    - "{{ ITA_DFLT_Authorized_Keys }}"
```
