# Ansible Legacy Default Playbook - Windows_win_service_enabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 880
- **playbook_name**: ~[Exastro standard][Win] Enable service startup
- **playbook_file**: Windows_win_service_enabled.yml
## Overview
Enables automatic startup (sets start_mode to auto) for one or more Windows services on a remote host using the win_service module.
## Description
This Playbook file changes the boot mode for services specified by "ITA_DFLT_Service_Name" to automatic.
"ITA_DFLT_Service_Name" can specify multiple service names (list type).
## Keyword
- Windows service management
- win_service module
- enable service startup
- automatic boot mode
## Playbook
```yaml
# This Playbook file changes the boot mode for services specified by "ITA_DFLT_Service_Name" to automatic.
# "Ita_DFLT_Service_Name" can specify multiple service names (list type).
- name: Automatic startup settings for Windows services
  ansible.windows.win_service:
    name: "{{ item }}"
    start_mode: auto
  with_items:
    - "{{ ITA_DFLT_Service_Name }}"
```
