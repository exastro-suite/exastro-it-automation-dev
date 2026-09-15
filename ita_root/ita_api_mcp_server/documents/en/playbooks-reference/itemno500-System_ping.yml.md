# Ansible Legacy Default Playbook - System_ping.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 500
- **playbook_name**: ~[Exastro standard] Ping
- **playbook_file**: System_ping.yml
## Overview
Verifies connectivity to the target host and confirms that a usable Python interpreter is available, using Ansible's ping module.
## Description
This Playbook file connects to the Target host and checks for usable Python.
Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
## Keyword
- connectivity check
- host reachability test
- health check
## Playbook
```yaml
# This Playbook file connects to the Target host and checks for usable Python.
# Note that as this Playbook file does not contain variables that can be externally controlled, we do not recommend using it linked to a Movement alone, but together with other Playbook files.
- name: ping
  ping:

```
