# Ansible Legacy Default Playbook - System_systemd_disabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 190
- **playbook_name**: ~[Exastro standard] Disable systemd startup
- **playbook_file**: System_systemd_disabled.yml
## Overview
Uses the `systemd` module to disable one or more systemd-managed units so that they no longer start automatically at boot.
## Description
This Playbook file removes the configuration that makes services specified by "ITA_DFLT_Services" run on server startup.
"ITA_DFLT_Services" can specify multiple services (list type).
## Keyword
- boot startup
- autostart
- systemd unit
## Playbook
```yaml
- name: Disabled service
  systemd:
    name: "{{ item }}"
    enabled: no
  with_items:
    - "{{ ITA_DFLT_Services }}"
```
