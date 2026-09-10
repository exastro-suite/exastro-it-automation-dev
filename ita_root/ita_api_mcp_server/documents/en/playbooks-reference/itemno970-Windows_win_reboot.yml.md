# Ansible Legacy Default Playbook - Windows_win_reboot.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 970
- **playbook_name**: ~[Exastro standard][Win] Reboot
- **playbook_file**: Windows_win_reboot.yml
## Overview
Reboots a Windows target host and waits for it to come back online, using a configurable reboot timeout that defaults to 600 seconds.
## Description
This Playbook file reboots the Target host.
The user can specify timeout time with "ITA_DFLT_Reboot_Timeout".
## Keyword
- Windows restart
- Reboot timeout
- Wait for host online
## Playbook
```yaml
# This Playbook file reboots the Target host.
# The user can specify timeout time with "ITA_DFLT_Reboot_Timeout".
- name: Reboot a windows machine
  win_reboot:
    reboot_timeout: "{{ ITA_DFLT_Reboot_Timeout | default(600) }}"

```
