# Ansible Legacy Default Playbook - System_group_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 540
- **playbook_name**: ~[Exastro standard] Remove group
- **playbook_file**: System_group_remove.yml
## Overview
Deletes one or more OS groups on the target host using Ansible's group module.
## Description
This Playbook file deletes groups specified by "ITA_DFLT_Groups".
"ITA_DFLT_Groups" can specify multiple groups (list type).
## Keyword
- group deletion
- remove group account
- user group cleanup
## Playbook
```yaml
- name: Remove group
  group:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Groups }}"
```
