# Ansible Legacy Default Playbook - Files_stat.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 260
- **playbook_name**: ~[Exastro standard] Find Filemaster
- **playbook_file**: Files_stat.yml
## Overview
Uses the Ansible `stat` module to retrieve file or filesystem status information for each path in a given list, registering the results for later use.
## Description
This Playbook file retrieves the status (such as existence, size, permissions, and timestamps) of the files or paths specified by "ITA_DFLT_Target_Path".
"ITA_DFLT_Target_Path" can specify multiple paths (list type), and each one is checked in turn.
The retrieved status information is stored in the "ITA_DFLT_Files_stat" registered variable for use in subsequent tasks.
## Keyword
- file status check
- filesystem metadata
- file existence check
- stat command wrapper
## Playbook
```yaml
- name: Retrieve file or file system status
  stat:
    path: "{{ item }}"
  with_items:
    - "{{ ITA_DFLT_Target_Path }}"
  register: ITA_DFLT_Files_stat
```
