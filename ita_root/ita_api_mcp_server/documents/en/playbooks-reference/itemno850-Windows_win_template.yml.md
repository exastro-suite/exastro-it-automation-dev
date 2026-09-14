# Ansible Legacy Default Playbook - Windows_win_template.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 850
- **playbook_name**: ~[Exastro standard][Win] Deploy template file
- **playbook_file**: Windows_win_template.yml
## Overview
Renders Jinja2 template files and deploys them from the control node to specified destination directories on a remote Windows host, keeping the original source filename (win_template module).
## Description
This Playbook file deploys template files specified by "ITA_DFLT_Win_Template_Src_File_Name" to the destination directories specified by "ITA_DFLT_Win_Template_Dest_Directory".
"ITA_DFLT_Win_Template_Src_File_Name" can specify multiple templates (list type).
"ITA_DFLT_Win_Template_Dest_Directory" can specify multiple directories (list type).
## Keyword
- Windows template deployment
- win_template module
- Jinja2 rendering
- configuration file generation
## Playbook
```yaml
- name: Fetch files from remote nodes
  ansible.windows.win_template:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}\\{{ item.0 | basename }}"
  with_together:
    - "{{ ITA_DFLT_Win_Template_Src_File_Name }}"
    - "{{ ITA_DFLT_Win_Template_Dest_Directory }}"
```
