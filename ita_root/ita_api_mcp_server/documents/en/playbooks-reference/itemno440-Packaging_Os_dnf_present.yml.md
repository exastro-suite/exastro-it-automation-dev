# Ansible Legacy Default Playbook - Packaging_Os_dnf_present.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 440
- **playbook_name**: ~[Exastro standard] Install dnf
- **playbook_file**: Packaging_Os_dnf_present.yml
## Overview
Iterates over a list of package names and installs each with the dnf module, registering the install results and printing them at high debug verbosity.
## Description
This Playbook file installs packages specified by "ITA_DFLT_Install_Target_packages".
"ITA_DFLT_Install_Target_packages" can specify multiple files (list type).
The task results are displayed at debug level 3 (-vvv).
## Keyword
- dnf package manager
- RPM package installation
- yum/dnf install task
- package deployment automation
## Playbook
```yaml
# This Playbook file installs packages specified by "ITA_DFLT_Install_Target_packages".
# "ITA_DFLT_Install_Target_packages" can specify multiple files (list type).
# The task results are displayed at debug level 3 (-vvv).
- name: Install packages with the dnf package manager
  dnf:
    name: "{{ item }}"
    state: present
  with_items:
    - "{{ ITA_DFLT_Install_Target_packages }}"
  register: ITA_RGST_DnfInstall_Result

- name: Debug the result
  debug:
    var: ITA_RGST_DnfInstall_Result
    verbosity: 3
```
