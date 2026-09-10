# Ansible Legacy Default Playbook - Windows_win_updates_all.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1060
- **playbook_name**: ~[Exastro standard][Win] Update (all)
- **playbook_file**: Windows_win_updates_all.yml
## Overview
Uses `ansible.windows.win_updates` with `category_names: '*'` and `reboot: true` to download and install all applicable Windows updates and reboot the host afterward.
## Description
This Playbook file updates Windows.
Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
## Keyword
- Windows Update
- patch all categories
- automatic reboot after update
- OS patching
## Playbook
```yaml
# This Playbook file updates Windows.
# Note that as this Playbook file does not contain variables that can be externally controlled,
# we do not recommend using it linked to a Movement alone, but together with other Playbook files.
- name: Download and install Windows updates and restart（all）
  ansible.windows.win_updates:
    category_names: '*'
    reboot: true
```
