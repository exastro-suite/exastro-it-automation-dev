# Ansible Legacy Default Playbook - Files_copy_remote-to-remote.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 90
- **playbook_name**: ~[Exastro standard] Copy file (within host)
- **playbook_file**: Files_copy_remote-to-remote.yml
## Overview
Copies files that already reside on the remote target host from a source path to a destination path, pairing multiple source/destination lists item by item.
## Description
This Playbook file copies local files specified by "ITA_DFLT_Src_Files" to remote files specified by "ITA_DFLT_Dest_Files".
"ITA_DFLT_Src_Files" can specify multiple files (list type).
"ITA_DFLT_Dest_Files" can specify multiple files (list type).
## Keyword
- File duplication on remote host
- Remote source copy
- Server-side file copy
## Playbook
```yaml
- name: Copy data from remote to remote
  copy:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}"
    remote_src: yes
  with_together:
    - "{{ ITA_DFLT_Src_Files }}"
    - "{{ ITA_DFLT_Dest_Files }}"

```
