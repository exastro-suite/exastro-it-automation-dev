# Ansible Legacy Default Playbook - Files_file_remove.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 130
- **playbook_name**: ~[Exastro standard] Delete files/Directories
- **playbook_file**: Files_file_remove.yml
## Overview
Uses the Ansible `file` module to recursively remove one or more files or directories, registering and printing the result via `debug` at verbosity level 3 (-vvv).
## Description
This Playbook file deletes files or directories specified by "ITA_DFLT_Remove_File_or_Directory".
"ITA_DFLT_Remove_File_or_Directory" can specify multiple files (list type).
The task results are displayed at debug level 3 (-vvv).
## Keyword
- directory removal
- recursive delete
- cleanup task
## Playbook
```yaml
# This Playbook file deletes packages specified by "ITA_DFLT_Remove_File_or_Directory".
# "ITA_DFLT_Remove_File_or_Directory" can specify multiple files (list type).
# The task results are displayed at debug level 3 (-vvv).
- name: Recursively remove directory or remove file
  file:
    path: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Remove_File_or_Directory }}"
  register: ITA_RGST_Absent_Result

- name: Debug the result
  debug:
    var: ITA_RGST_Absent_Result
    verbosity: 3

```
