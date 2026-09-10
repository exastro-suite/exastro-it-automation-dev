# Ansible Legacy Default Playbook - Windows_win_service_started.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1080
- **playbook_name**: ~[Exastro standard][Win]Start service
- **playbook_file**: Windows_win_service_started.yml
## Overview
Uses the `ansible.windows.win_service` module with `state: started` to start one or more Windows services, iterating over a list of service names.
## Description
This Playbook file starts services specified by "ITA_DFLT_Service_Name".
"ITA_DFLT_Service_Name" can specify multiple service names (list type).
## Keyword
- Windows service start
- launch service
- service activation
## Playbook
```yaml
# This Playbook file starts services specified by "ITA_DFLT_Service_Name".
# "ITA_DFLT_Service_Name" can specify multiple service names (list type).
- name: start Windows services
  ansible.windows.win_service:
    name: "{{ item }}"
    state: started
  with_items:
    - "{{ ITA_DFLT_Service_Name }}"
```
