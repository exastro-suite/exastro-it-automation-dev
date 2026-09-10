# Ansible Legacy Default Playbook - Windows_win_copy_remote-to-remote.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 810
- **playbook_name**: ~[Exastro standard][Win] Copy file (within host)
- **playbook_file**: Windows_win_copy_remote-to-remote.yml
## Overview
Copies files between locations on the same remote Windows host (remote-to-remote), using paired lists of source and destination paths (win_copy module with remote_src enabled).
## Description
- `ITA_DFLT_Src_Files`: the source file path(s) already present on the remote Windows host to copy from (list type, multiple values can be specified).
- `ITA_DFLT_Dest_Files`: the destination file path(s) on the same remote Windows host to copy to (list type, multiple values can be specified).
## Keyword
- Windows remote to remote copy
- win_copy module
- within-host file duplication
- file copy on same server
## Playbook
```yaml
- name: Copy data from remote to remote
  win_copy:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}"
    remote_src: yes
  with_together:
    - "{{ ITA_DFLT_Src_Files }}"
    - "{{ ITA_DFLT_Dest_Files }}"
```
