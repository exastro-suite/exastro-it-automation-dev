# Ansible Legacy Default Playbook - Packaging_Language_pip.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 740
- **playbook_name**: ~[Exastro standard] pip
- **playbook_file**: Packaging_Language_pip.yml
## Overview
Uses the `ansible.builtin.pip` module to install one or more specified Python packages on the target host, iterating over a list of package names.
## Description
This Playbook file installs package names specified by "ITA_DFLT_Target_Package_Name".
Nothing will happen if the specified package names are already installed.
"ITA_DFLT_Target_Package_Name" can specify multiple package names (list type).
## Keyword
- pip install
- python library installation
- dependency management
- python package manager
## Playbook
```yaml
# This Playbook file installs package names specified by "ITA_DFLT_Target_Package_Name".
# Nothing will happen if the specified package names are already installed.
# "ITA_DFLT_Target_Package_Name" can specify multiple package names (list type).
- name: Manages Python library dependencies
  ansible.builtin.pip:
    name: "{{ item }}"
  with_items:
    - "{{ ITA_DFLT_Target_Package_Name }}"
```
