# Ansible Legacy Default Playbook - System_sysctl_present.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 750
- **playbook_name**: ~[Exastro standard] sysctly settings
- **playbook_file**: System_sysctl_present.yml
## Overview
Uses the `sysctl` module to set one or more kernel parameters to specified values on the target host, pairing parameter names with values by list position, and reloads the sysctl configuration.
## Description
"ITA_DFLT_Parameter_Names" specifies one or more sysctl parameter names (list type) to configure on the target host.
"ITA_DFLT_Parameter_Values" specifies the corresponding values (list type) to set for each parameter name, matched by position with "ITA_DFLT_Parameter_Names".
## Keyword
- kernel parameter configuration
- sysctl settings
- system tuning
- kernel tuning
## Playbook
```yaml
- name: Entry parameter
  sysctl:
    name: "{{ item.0 }}"
    value: "{{ item.1 }}"
    state: present
    reload: yes
  with_together:
    - "{{ ITA_DFLT_Parameter_Names }}"
    - "{{ ITA_DFLT_Parameter_Values }}"
```
