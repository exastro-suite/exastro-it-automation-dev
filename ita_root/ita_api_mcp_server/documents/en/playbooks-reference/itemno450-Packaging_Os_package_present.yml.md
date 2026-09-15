# Ansible Legacy Default Playbook - Packaging_Os_package_present.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 450
- **playbook_name**: ~[Exastro standard] Install package
- **playbook_file**: Packaging_Os_package_present.yml
## Overview
Installs one or more OS packages on the target host using Ansible's generic package module, targeting packages listed in a variable.
## Description
This Playbook file installs packages specified by "ITA_DFLT_Install_Target_packages" using the OS's generic package manager module.
"ITA_DFLT_Install_Target_packages" can specify multiple packages (list type).
## Keyword
- package installation
- software provisioning
- yum/apt/dnf
- package deployment
## Playbook
```yaml
- name: Install packages with the generic OS package manager
  package:
    name: "{{ item }}"
    state: present
  with_items:
    - "{{ ITA_DFLT_Install_Target_packages }}"
```
