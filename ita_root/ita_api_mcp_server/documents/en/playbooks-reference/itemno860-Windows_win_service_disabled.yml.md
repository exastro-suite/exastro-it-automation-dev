# Ansible Legacy Default Playbook - Windows_win_service_disabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 860
- **playbook_name**: ~[Exastro standard][Win] Disable service startup
- **playbook_file**: Windows_win_service_disabled.yml
## Overview
Disables automatic startup (sets start_mode to disabled) for one or more Windows services on a remote host using the win_service module.
## Description
This Playbook file deactivates "automatic boot mode" for the services specified by "ITA_DFLT_Service_Name".
"ITA_DFLT_Service_Name" can specify multiple service names (list type).
## Keyword
- Windows service management
- win_service module
- disable service startup
- service boot mode configuration
## Playbook
```yaml
# This Playbook file deactivates "automatic boot mode" for the services specified by "ITA_DFL_Service_Name".
# "ITA_DFLT_Service_Name" can specify multiple service names (list type).
- name: Disable automatic startup of Windows services
  ansible.windows.win_service:
    name: "{{ item }}"
    start_mode: disabled
  with_items:
    - "{{ ITA_DFLT_Service_Name }}"
```
