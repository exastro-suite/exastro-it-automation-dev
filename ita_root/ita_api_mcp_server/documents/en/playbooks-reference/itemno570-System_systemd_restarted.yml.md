# Ansible Legacy Default Playbook - System_systemd_restarted.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 570
- **playbook_name**: ~[Exastro standard] Restart systemd
- **playbook_file**: System_systemd_restarted.yml
## Overview
Restarts one or more systemd-managed services on target hosts using Ansible's systemd module, reloading the systemd daemon and iterating over a list of service names.
## Description
This Playbook file reboots services specified by "ITA_DFLT_Services".
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- systemd restart
- daemon-reload
- unit file
## Playbook
```yaml
- name: Restart service
  systemd:
    name: "{{ item }}"
    state: restarted
    daemon_reload: yes
  with_items:
    - "{{ ITA_DFLT_Services }}"

```
