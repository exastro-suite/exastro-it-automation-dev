# Ansible Legacy Default Playbook - System_service_started.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 610
- **playbook_name**: ~[Exastro standard] Start service
- **playbook_file**: System_service_started.yml
## Overview
Starts one or more OS services on target hosts using Ansible's service module, iterating over a list of service names.
## Description
This Playbook file starts services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- service start
- launch daemon
- init system
## Playbook
```yaml
- name: Start service
  service:
    name: "{{ item }}"
    state: started
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
