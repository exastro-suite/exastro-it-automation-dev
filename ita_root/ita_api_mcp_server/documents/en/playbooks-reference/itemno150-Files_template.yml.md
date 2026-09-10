# Ansible Legacy Default Playbook - Files_template.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 150
- **playbook_name**: ~[Exastro standard] Deploy template file
- **playbook_file**: Files_template.yml
## Overview
Uses the Ansible `template` module to render one or more Jinja2 template source files and deploy them to their corresponding destination paths, pairing sources and destinations positionally.
## Description
This Playbook file deploys templates specified by "ITA_DFLT_Template_Src_Files" to files specified by "ITA_DFLT_Template_Dest_Files".
"ITA_DFLT_Template_Src_Files" can specify multiple templates (list type).
"ITA_DFLT_Template_Dest_Files" can specify multiple files (list type).
## Keyword
- Jinja2 template
- configuration file generation
- template rendering
## Playbook
```yaml
- name: Create template files
  template:
    src: "{{ item.0 }}"
    dest: "{{ item.1 }}"
  with_together:
    - "{{ ITA_DFLT_Template_Src_Files }}"
    - "{{ ITA_DFLT_Template_Dest_Files }}"
```
