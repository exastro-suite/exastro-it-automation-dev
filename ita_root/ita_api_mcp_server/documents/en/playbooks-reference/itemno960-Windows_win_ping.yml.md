# Ansible Legacy Default Playbook - Windows_win_ping.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 960
- **playbook_name**: ~[Exastro standard][Win] Ping
- **playbook_file**: Windows_win_ping.yml
## Overview
Verifies connectivity and that Ansible can execute modules on a Windows target host using the win_ping module.
## Description
This Playbook file checks the connection to the target host.
Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
## Keyword
- Windows connectivity test
- Ansible module test
- Host reachability check
## Playbook
```yaml
# This Playbook file checks the connection to the target host.
# Note that as this Playbook file does not contain variables that can be externally controlled,
# we do not recommend using it linked to a Movement alone, but together with other Playbook files.
- name: A windows version of the classic ping module
  win_ping:
```
