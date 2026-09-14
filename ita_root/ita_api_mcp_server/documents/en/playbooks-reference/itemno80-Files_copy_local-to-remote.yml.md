# Ansible Legacy Default Playbook - Files_copy_local-to-remote.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 80
- **playbook_name**: ~[Exastro standard] Copy file
- **playbook_file**: Files_copy_local-to-remote.yml
## Overview
Copies files from the local Ansible control node to remote target hosts, using paired lists of source and destination file paths (copy module, remote_src disabled).
## Description
This Playbook file copies local files specified by "ITA_DFLT_Src_Files" to remote files specified by "ITA_DFLT_Dest_Files".
"ITA_DFLT_Src_Files" can specify multiple files (list type).
"ITA_DFLT_Dest_Files" can specify multiple files (list type).

## Additional description
- The `FileUploadColumn` item in the parameter sheet can be linked to `ITA_DFLT_Src_Files`.
## Keyword
- local to remote file transfer
- Ansible copy module
- source destination file mapping
- file deployment
## Playbook
```yaml
- name: Copy data from local to remote
  copy:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}"
    remote_src: no
  with_together:
    - "{{ ITA_DFLT_Src_Files }}"
    - "{{ ITA_DFLT_Dest_Files }}"
```
