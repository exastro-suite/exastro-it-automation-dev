# Ansible Legacy Default Playbook - System_reboot.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 510
- **playbook_name**: ~[Exastro standard] Reboot
- **playbook_file**: System_reboot.yml
## Overview
Reboots the target host and waits for it to come back online, with an optional configurable timeout.
## Description
This Playbook file reboots the Target host.
The user can specify timeout time with "ITA_DFLT_Reboot_Timeout".
## Keyword
- system restart
- restart server
- reboot timeout
## Playbook
```yaml
# This Playbook file reboots the Target host.
# The user can specify timeout time with "ITA_DFLT_Reboot_Timeout".
- name: Reboot
  reboot:
    reboot_timeout: "{{ ITA_DFLT_Reboot_Timeout | default(600) }}"

```
