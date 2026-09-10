# Ansible Legacy Default Playbook - Files_file_mkdir.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 100
- **playbook_name**: ~[Exastro standard] Create directory
- **playbook_file**: Files_file_mkdir.yml
## Overview
Uses the Ansible `file` module to create one or more directories on the target host, iterating over a list of directory paths with `with_items`.
## Description
This Playbook file creates directories specified by "ITA_DFLT_Create_Directories".
"ITA_DFLT_Create_Directories" can specify multiple directories (list type).
## Keyword
- mkdir
- folder creation
- file system provisioning
- directory setup
## Playbook
```yaml
- name: Create directorys
  file:
    path: "{{ item }}"
    state: directory
  with_items:
    - "{{ ITA_DFLT_Create_Directories }}"
```
