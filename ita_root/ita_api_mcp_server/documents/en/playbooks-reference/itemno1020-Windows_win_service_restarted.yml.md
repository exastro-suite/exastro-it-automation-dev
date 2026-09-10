# Ansible Legacy Default Playbook - Windows_win_service_restarted.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1020
- **playbook_name**: ~[Exastro standard][Win] Restart service
- **playbook_file**: Windows_win_service_restarted.yml
## Overview
Uses the `ansible.windows.win_service` module with `state: restarted` to restart one or more Windows services, iterating over a list of service names.
## Description
This Playbook file reboots services specified by "ITA_DFLT_Service_Name".
"ITA_DFLT_Service_Name" can specify multiple service names (list type).
## Keyword
- Windows service restart
- service bounce
- reboot service
## Playbook
```yaml
# This Playbook file reboots services specified by "ITA_DFLT_Service_Name".
# "ITA_DFLT_Service_Name" can specify multiple service names (list type).
- name: restart Windows services
  ansible.windows.win_service:
    name: "{{ item }}"
    state: restarted
  with_items:
    - "{{ ITA_DFLT_Service_Name }}"
```
