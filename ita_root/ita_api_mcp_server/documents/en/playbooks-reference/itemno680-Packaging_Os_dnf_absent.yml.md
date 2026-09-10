# Ansible Legacy Default Playbook - Packaging_Os_dnf_absent.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 680
- **playbook_name**: ~[Exastro standard] Uninstall dnf
- **playbook_file**: Packaging_Os_dnf_absent.yml
## Overview
Uses the Ansible `dnf` module to uninstall one or more specified packages from the target host, iterating over a list of package names, then logs the result at debug verbosity 3.
## Description
This Playbook file uninstalls packages specified by "ITA_DFLT_Uninstall_Target_packages".
"ITA_DFLT_uninstall_Target_packages" can specify multiple files (list type).
The task results are displayed at debug level 3 (-vvv).
## Keyword
- dnf uninstall
- rpm package removal
- yum uninstall
- software removal
## Playbook
```yaml
# This Playbook file uninstalls packages specified by "ITA_DFLT_Uninstall_Target_packages".
# "ITA_DFLT_uninstall_Target_packages" can specify multiple files (list type).
# The task results are displayed at debug level 3 (-vvv).
- name: Uninstall packages with the dnf package manager
  dnf:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Uninstall_Target_packages }}"
  register: ITA_RGST_DnfUninstall_Result

- name: Debug the result
  debug:
    var: ITA_RGST_DnfUninstall_Result
    verbosity: 3
```
