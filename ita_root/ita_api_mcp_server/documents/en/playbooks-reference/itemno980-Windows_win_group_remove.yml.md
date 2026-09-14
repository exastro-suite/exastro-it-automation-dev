# Ansible Legacy Default Playbook - Windows_win_group_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 980
- **playbook_name**: ~[Exastro standard][Win] Remove group
- **playbook_file**: Windows_win_group_remove.yml
## Overview
Removes one or more local Windows groups by name using the win_group module, setting each group's state to absent.
## Description
"ITA_DFLT_Remove_groups": Name of the local Windows group to remove. Multiple group names can be specified at the same time (list type).
## Keyword
- Windows local group deletion
- Delete user group
- Group management
## Playbook
```yaml
- name: Remove groups
  ansible.windows.win_group:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Remove_groups }}"
```
