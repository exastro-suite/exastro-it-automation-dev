# Ansible Legacy Default Playbook - System_getent_netgroup.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 370
- **playbook_name**: ~[Exastro standard] Get entry(netgroup
- **playbook_file**: System_getent_netgroup.yml
## Overview
Queries the system netgroup database using the Ansible getent module and stores the retrieved network group definitions in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `netgroup` database, which defines network-wide groups of hosts, users, and domains used for access control (typically distributed via NIS), and saves the output into the registered variable `ITA_DFLT_getent_netgroup` so that later tasks can reference the netgroup information.
## Keyword
- NIS netgroup lookup
- network access control groups
- host/user/domain triplets
- centralized access grouping
## Playbook
```yaml
- name: A wrapper to the unix getent utility (netgroup)
  getent:
    database: netgroup
  register: ITA_DFLT_getent_netgroup
```
