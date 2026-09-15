# Ansible Legacy Default Playbook - Packaging_Os_package_latest.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 720
- **playbook_name**: ~[Exastro standard] Update package
- **playbook_file**: Packaging_Os_package_latest.yml
## Overview
Uses the Ansible generic `package` module to update one or more specified packages to their latest version via the OS's native package manager, iterating over a list of package names.
## Description
"ITA_DFLT_Update_Target_packages" specifies one or more package names (list type) to be updated to their latest available version using the target host's OS-native package manager (dnf, yum, apt, etc., auto-detected by the `package` module).
## Keyword
- generic package update
- os-native package manager
- apt upgrade
- yum update
## Playbook
```yaml
- name: Update packages with the generic OS package manager
  package:
    name: "{{ item }}"
    state: latest
  with_items:
    - "{{ ITA_DFLT_Update_Target_packages }}"
```
