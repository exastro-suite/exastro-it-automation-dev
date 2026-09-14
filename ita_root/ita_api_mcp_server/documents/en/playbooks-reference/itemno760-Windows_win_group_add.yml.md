# Ansible Legacy Default Playbook - Windows_win_group_add.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 760
- **playbook_name**: ~[Exastro standard][Win] Add group
- **playbook_file**: Windows_win_group_add.yml
## Overview
Uses the `ansible.windows.win_group` module to create one or more local Windows groups with specified names and descriptions on the target host, pairing names and descriptions by list position.
## Description
"ITA_DFLT_Create_group_names" specifies one or more local Windows group names (list type) to create on the target host.
"ITA_DFLT_Create_group_discriptions" specifies the corresponding descriptions (list type) for each group, matched by position with "ITA_DFLT_Create_group_names".
## Keyword
- windows group creation
- local group management
- win_group module
- user group setup
## Playbook
```yaml
- name: Create new groups
  ansible.windows.win_group:
    name: "{{ item.0 }}"
    description: "{{ item.1 }}"
    state: present
  with_together:
    - "{{ ITA_DFLT_Create_group_names }}"
    - "{{ ITA_DFLT_Create_group_discriptions }}"
```
