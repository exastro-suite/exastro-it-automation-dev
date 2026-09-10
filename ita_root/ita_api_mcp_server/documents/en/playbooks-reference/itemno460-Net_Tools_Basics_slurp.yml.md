# Ansible Legacy Default Playbook - Net_Tools_Basics_slurp.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 460
- **playbook_name**: ~[Exastro standard] Load file
- **playbook_file**: Net_Tools_Basics_slurp.yml
## Overview
Reads a file from the target host using Ansible's slurp module and stores its base64-encoded content in a registered variable.
## Description
This Playbook file reads the file specified by "ITA_DFLT_Target_File" from the Target host using the slurp module, and stores the base64-encoded content in the registered variable "ITA_DFLT_Files_text".
## Keyword
- remote file read
- file content retrieval
- base64 encode
- file transfer
## Playbook
```yaml
- name: Slurps a file from remote nodes
  slurp:
    src: "{{ ITA_DFLT_Target_File }}"
  register: ITA_DFLT_Files_text
```
