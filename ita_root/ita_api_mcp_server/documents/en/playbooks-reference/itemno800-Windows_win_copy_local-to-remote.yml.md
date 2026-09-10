# Ansible Legacy Default Playbook - Windows_win_copy_local-to-remote.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 800
- **playbook_name**: ~[Exastro standard][Win] Copy file
- **playbook_file**: Windows_win_copy_local-to-remote.yml
## Overview
Copies files from the local Ansible control node to remote Windows hosts, using paired lists of source and destination paths (win_copy module, remote_src disabled).
## Description
- `ITA_DFLT_Src_Files`: the local source file path(s) to copy from the control node (list type, multiple values can be specified).
- `ITA_DFLT_Dest_Files`: the destination file path(s) on the remote Windows host to copy to (list type, multiple values can be specified).
## Keyword
- Windows local to remote copy
- win_copy module
- file deployment
- source destination mapping
## Playbook
```yaml
- name: Copy data from local to remote
  win_copy:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}"
    remote_src: no
  with_together:
    - "{{ ITA_DFLT_Src_Files }}"
    - "{{ ITA_DFLT_Dest_Files }}"
```
