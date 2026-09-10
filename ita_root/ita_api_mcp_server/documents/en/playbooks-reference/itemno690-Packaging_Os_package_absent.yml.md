# Ansible Legacy Default Playbook - Packaging_Os_package_absent.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 690
- **playbook_name**: ~[Exastro standard] Uninstall package
- **playbook_file**: Packaging_Os_package_absent.yml
## Overview
Uses the Ansible generic `package` module to uninstall one or more specified packages from the target host via the OS's native package manager, iterating over a list of package names.
## Description
"ITA_DFLT_Uninstall_Target_packages" specifies one or more package names (list type) to be uninstalled using the target host's OS-native package manager (dnf, yum, apt, etc., auto-detected by the `package` module).
## Keyword
- generic package removal
- os-native package manager
- apt uninstall
- yum uninstall
## Playbook
```yaml
- name: Uninstall packages with the generic OS package manager
  package:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Uninstall_Target_packages }}"
```
