# Ansible Legacy Default Playbook - Files_fetch.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 250
- **playbook_name**: ~[Exastro standard] Fetch files
- **playbook_file**: Files_fetch.yml
## Overview
Uses the Ansible `fetch` module to copy each file in a given list from the remote target node to the local workflow directory, registers the result, and prints it at debug verbosity level 3.
## Description
This Playbook file stores files specified by "ITA_DFLT_Target_File_Name" to "__workflowdir__".
"ITA_DFLT_Target_File_name" can specify multiple files (list type).
Files stored in "__workflowdir__" can be retrieved as result data after the Movement ends.
The task results are displayed at debug level 3 (-vvv).
## Keyword
- remote file retrieval
- file download
- collecting files from managed nodes
## Playbook
```yaml
# This Playbook file stores files specified by "ITA_DFLT_Target_File_Name" to "__workflowdir__".
# "ITA_DFLT_Target_File_name" can specify multiple files (list type).
# Files stored in "__workflowdir__" can be retrieved as result data after the Movement ends.
# The task results are displayed at debug level 3 (-vvv).
- name: Fetch files from remote nodes
  fetch:
    src: "{{ item }}"
    dest: "{{ __workflowdir__ }}"
  with_items:
    - "{{ ITA_DFLT_Target_File_Name }}"
  register: ITA_RGST_Fetch_Result

- name: Debug the result
  debug:
    var: ITA_RGST_Fetch_Result
    verbosity: 3

```
