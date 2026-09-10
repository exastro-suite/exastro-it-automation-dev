# Ansible Legacy Default Playbook - Windows_win_file_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 830
- **playbook_name**: ~[Exastro standard][Win] Delete File/Folder
- **playbook_file**: Windows_win_file_remove.yml
## Overview
Deletes files or recursively removes directories on a remote Windows host using the win_file module with state set to absent.
## Description
- `ITA_DFLT_Remove_File_or_Directory`: the file or directory path(s) to delete on the remote Windows host (list type, multiple values can be specified).
## Keyword
- Windows file deletion
- win_file module
- recursive directory removal
- cleanup task
## Playbook
```yaml
- name: Recursively remove directory or remove file
  win_file:
    path: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Remove_File_or_Directory }}"
```
