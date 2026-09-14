# Ansible Legacy Default Playbook - System_systemd_stopped.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 640
- **playbook_name**: ~[Exastro standard] Stop systemd
- **playbook_file**: System_systemd_stopped.yml
## Overview
Stops one or more systemd-managed services on target hosts using Ansible's systemd module, iterating over a list of service names.
## Description
This Playbook file stops services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- systemd stop
- unit file
- halt daemon
## Playbook
```yaml
- name: Stop service
  systemd:
    name: "{{ item }}"
    state: stopped
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
