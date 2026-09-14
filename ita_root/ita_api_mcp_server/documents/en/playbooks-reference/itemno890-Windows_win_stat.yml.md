# Ansible Legacy Default Playbook - Windows_win_stat.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 890
- **playbook_name**: ~[Exastro standard][Win] Get file status
- **playbook_file**: Windows_win_stat.yml
## Overview
Retrieves status information (existence, size, timestamps, attributes) for one or more files/paths on a Windows host using win_stat, following symbolic links.
## Description
This Playbook file acquires the file path information specified by "ITA_DFLT_File_Path".
"ITA_DFLT_File_Path" can specify multiple file paths (list type).
## Keyword
- File attributes check
- Windows file existence check
- File metadata lookup
## Playbook
```yaml
# This Playbook file acquires the file path information specified by "ITA_DFLT_File_Path".
# "ITA_DFLT_File_Path" can specify multiple file paths (list type).
- name: Get information about Windows files
  ansible.windows.win_stat:
    path: "{{ item }}"
    follow: true
  with_items:
    - "{{ ITA_DFLT_File_Path }}"
  
```
