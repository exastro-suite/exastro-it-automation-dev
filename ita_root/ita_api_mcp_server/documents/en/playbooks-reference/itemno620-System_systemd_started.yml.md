# Ansible Legacy Default Playbook - System_systemd_started.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 620
- **playbook_name**: ~[Exastro standard] Start systemd
- **playbook_file**: System_systemd_started.yml
## Overview
Starts one or more systemd-managed services on target hosts using Ansible's systemd module, iterating over a list of service names.
## Description
This Playbook file starts services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- systemd start
- unit file
- launch daemon
## Playbook
```yaml
- name: Start service
  systemd:
    name: "{{ item }}"
    state: started
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
