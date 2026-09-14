# Ansible Legacy Default Playbook - System_service_enabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 230
- **playbook_name**: ~[Exastro standard] Enable service startup
- **playbook_file**: System_service_enabled.yml
## Overview
Uses the Ansible `service` module to enable each service in a given list so that it starts automatically on system boot, iterating over the list with `with_items`.
## Description
This Playbook file configures services specified by "ITA_DFLT_Services" to run on server startup.
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- service management
- boot-time startup
- autostart configuration
- init system
## Playbook
```yaml
- name: Enable service
  service:
    name: "{{ item }}"
    enabled: true
  with_items:
    - "{{ ITA_DFLT_Services }}"
```
