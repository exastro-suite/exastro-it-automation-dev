# Ansible Legacy Default Playbook - System_sysctl_absent.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 140
- **playbook_name**: ~[Exastro standard] Delete sysctl
- **playbook_file**: System_sysctl_absent.yml
## Overview
Uses the Ansible `sysctl` module to remove one or more kernel parameters from the system's sysctl configuration and reloads the settings.
## Description
This Playbook file removes parameter names specified by "ITA_DFLT_Parameter_Names" from sysctl.
"ITA_DFLT_Parameter_Names" can specify multiple parameter names (list type).
## Keyword
- kernel tuning
- sysctl configuration
- remove parameter
## Playbook
```yaml
- name: Remove parameter
  sysctl:
    name: "{{ item }}"
    state: absent
    reload: yes
  with_items:
    - "{{ ITA_DFLT_Parameter_Names }}"
```
