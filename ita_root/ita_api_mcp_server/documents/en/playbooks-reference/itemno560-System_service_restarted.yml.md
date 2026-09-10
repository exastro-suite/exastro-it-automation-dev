# Ansible Legacy Default Playbook - System_service_restarted.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 560
- **playbook_name**: ~[Exastro standard] Restart service
- **playbook_file**: System_service_restarted.yml
## Overview
Restarts one or more OS services on target hosts using Ansible's service module, iterating over a list of service names.
## Description
This Playbook file reboots services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- service restart
- reboot daemon
- init system
## Playbook
```yaml
- name: Start service
  service:
    name: "{{ item }}"
    state: restarted
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
