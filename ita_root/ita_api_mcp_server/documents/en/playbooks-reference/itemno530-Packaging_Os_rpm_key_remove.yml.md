# Ansible Legacy Default Playbook - Packaging_Os_rpm_key_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 530
- **playbook_name**: ~[Exastro standard] Remove RPM key
- **playbook_file**: Packaging_Os_rpm_key_remove.yml
## Overview
Removes one or more GPG keys from the RPM database on the target host using Ansible's rpm_key module.
## Description
This Playbook file deletes GPG keys specified by "ITA_DFLT_Gpg_Key_Ids" from the RPM database.
"ITA_DFLT_Gpg_Key_Ids" can specify multiple GPG keys (list type).
## Keyword
- GPG key removal
- RPM database
- package signing key management
## Playbook
```yaml
- name: Remove gpg key
  rpm_key:
    key: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Gpg_Key_Ids }}"
```
