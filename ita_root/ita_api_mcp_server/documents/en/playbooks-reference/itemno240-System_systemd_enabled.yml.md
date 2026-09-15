# Ansible Legacy Default Playbook - System_systemd_enabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 240
- **playbook_name**: ~[Exastro standard] Enable systemd startup
- **playbook_file**: System_systemd_enabled.yml
## Overview
Uses the Ansible `systemd` module to enable each unit in a given list so that it starts automatically on system boot, iterating over the list with `with_items`.
## Description
This Playbook file configures services specified by "ITA_DFLT_Services" to run on server startup.
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- systemd unit management
- boot-time startup
- autostart configuration
- service enablement
## Playbook
```yaml
- name: Enabled service
  systemd:
    name: "{{ item }}"
    enabled: yes
  with_items:
    - "{{ ITA_DFLT_Services }}"
```
