# Ansible Legacy Default Playbook - System_seboolean.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 470
- **playbook_name**: ~[Exastro standard] Modify SELinux
- **playbook_file**: System_seboolean.yml
## Overview
Toggles SELinux boolean settings on the target host, setting each named boolean to a given state and persistence using Ansible's seboolean module.
## Description
This Playbook file changes the bool values for the names specified by "ITA_DFLT_Booleans_Name" using the values (true/false) specified by "ITA_DFLT_State" and uses the values (true/false) specified by "ITA_DFLT_Persistent" to configure the persistency of the files (If the files will keep the settings after reboot or not).
Each of the variables can have multiple specified at the same time (list type).
## Keyword
- SELinux configuration
- security policy
- getsebool/setsebool
- security hardening
## Playbook
```yaml
# This Playbook file changes the bool values for the names specified by "ITA_DFLT_Booleans_Name" 
# using the values (true/false) specified by "ITA_DFLT_State" and uses the values (true/false) 
# specified by "ITA_DFLT_Persistent" to configure the persistency of the files 
# (If the files will keep the settings after reboot or not).
# Each of the variables can have multiple specified at the same time (list type).
- name: Toggles SELinux booleans
  ansible.posix.seboolean:
    name: "{{ item.0 }}"
    state: "{{ item.1 }}"
    persistent: "{{ item.2 }}"
  with_together:
    - "{{ ITA_DFLT_Booleans_Name }}"
    - "{{ ITA_DFLT_State }}"
    - "{{ ITA_DFLT_Persistent }}"
```
