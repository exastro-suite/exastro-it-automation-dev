# Ansible Legacy Default Playbook - System_service_stopped.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 630
- **playbook_name**: ~[Exastro standard] Stop service
- **playbook_file**: System_service_stopped.yml
## Overview
Stops one or more OS services on target hosts using Ansible's service module, iterating over a list of service names.
## Description
This Playbook file stops services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- service stop
- halt daemon
- init system
## Playbook
```yaml
- name: Stop service
  service:
    name: "{{ item }}"
    state: stopped
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
