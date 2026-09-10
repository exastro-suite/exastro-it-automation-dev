# Ansible Legacy Default Playbook - System_service_disabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 180
- **playbook_name**: ~[Exastro standard] Disable service startup
- **playbook_file**: System_service_disabled.yml
## Overview
Uses the legacy `service` module to disable one or more services so that they no longer start automatically at boot.
## Description
This Playbook file removes the configuration that makes services specified by "ITA_DFLT_Services" run on server startup.
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- boot startup
- autostart
- service management
## Playbook
```yaml
- name: Disable service
  service:
    name: "{{ item }}"
    enabled: false
  with_items:
    - "{{ ITA_DFLT_Services }}"
```
