# Ansible Legacy Default Playbook - Packaging_Os_rpm_key_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 40
- **playbook_name**: ~[Exastro standard] Add RPM key
- **playbook_file**: Packaging_Os_rpm_key_add.yml
## Overview
Iterates over a list of GPG keys and registers each one with the system RPM database using the rpm_key module, ensuring each key is present.
## Description
This Playbook file registers GPG keys specified by "ITA_DFLT_Gpg_Keys" to the RPM database.
"ITA_DFLT_Gpg_Keys" can specify multiple GPG keys (list type).
## Keyword
- RPM package signing
- GPG public key import
- package repository trust setup
- rpm_key module
## Playbook
```yaml
- name: Add gpg key
  rpm_key:
    key: "{{ item }}"
    state: present
  with_items:
    - "{{ ITA_DFLT_Gpg_Keys }}"
```
