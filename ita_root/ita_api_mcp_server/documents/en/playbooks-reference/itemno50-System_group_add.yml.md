# Ansible Legacy Default Playbook - System_group_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 50
- **playbook_name**: ~[Exastro standard] Add group
- **playbook_file**: System_group_add.yml
## Overview
Creates one or more OS groups on the target host using Ansible's group module, based on a list of group names.
## Description
This Playbook file registers groups specified by "ITA_DFLT_Groups".
"ITA_DFLT_Groups" can specify multiple groups (list type).
## Keyword
- group creation
- user group management
- account provisioning
## Playbook
```yaml
- name: Add group
  group:
    name: "{{ item }}"
    state: present
  with_items:
    - "{{ ITA_DFLT_Groups }}"
```
