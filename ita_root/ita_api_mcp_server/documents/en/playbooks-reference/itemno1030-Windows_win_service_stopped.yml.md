# Ansible Legacy Default Playbook - Windows_win_service_stopped.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1030
- **playbook_name**: ~[Exastro standard][Win] Stop service
- **playbook_file**: Windows_win_service_stopped.yml
## Overview
Uses the `ansible.windows.win_service` module with `state: stopped` to stop one or more Windows services, iterating over a list of service names.
## Description
This Playbook file stops services specified by "ITA_DFLT_Service_Name".
"ITA_DFLT_Service_Name" can specify multiple service names (list type).
## Keyword
- Windows service stop
- halt service
- service shutdown
## Playbook
```yaml
# This Playbook file stops services specified by "ITA_DFLT_Service_Name".
# "ITA_DFLT_Service_Name" can specify multiple service names (list type).
- name: stop Windows services
  ansible.windows.win_service:
    name: "{{ item }}"
    state: stopped
  with_items:
    - "{{ ITA_DFLT_Service_Name }}"
```
