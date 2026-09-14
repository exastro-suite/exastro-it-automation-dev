# Ansible Legacy Default Playbook - Packaging_Os_dnf_latest.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 710
- **playbook_name**: ~[Exastro standard] Update dnf
- **playbook_file**: Packaging_Os_dnf_latest.yml
## Overview
Uses the Ansible `dnf` module to update one or more specified packages to their latest version on the target host, iterating over a list of names, then logs the result at debug verbosity 3.
## Description
This Playbook file updates packages specified by "ITA_DFLT_Update_Target_packages" to the latest version available.
"ITA_DFLT_Update_Target_packages" can specify multiple files (list type).
The task results are displayed at debug level 3 (-vvv).
## Keyword
- dnf update
- rpm package upgrade
- yum update
- software update
## Playbook
```yaml
# This Playbook file updates packages specified by "ITA_DFLT_Update_Target_packages" to the latest version available.
# "ITA_DFLT_Update_Target_packages" can specify multiple files (list type).
# The task results are displayed at debug level 3 (-vvv). 
- name: Update packages with the dnf package manager
  dnf:
    name: "{{ item }}"
    state: latest
  with_items:
    - "{{ ITA_DFLT_Update_Target_packages }}"
  register: ITA_RGST_DnfUpdate_Result

- name: Debug the result
  debug:
    var: ITA_RGST_DnfUpdate_Result
    verbosity: 3
```
