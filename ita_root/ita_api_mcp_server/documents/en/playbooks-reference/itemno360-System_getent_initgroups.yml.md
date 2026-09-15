# Ansible Legacy Default Playbook - System_getent_initgroups.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 360
- **playbook_name**: ~[Exastro standard] Get entry(initgroups)
- **playbook_file**: System_getent_initgroups.yml
## Overview
Queries the system initgroups database using the Ansible getent module and stores the retrieved initial group membership entries in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `initgroups` database, which lists the supplementary groups a user belongs to at login, and saves the output into the registered variable `ITA_DFLT_getent_initgroups` so that later tasks can reference the group membership information.
## Keyword
- user group membership lookup
- supplementary groups
- login group resolution
- account privilege inventory
## Playbook
```yaml
- name: A wrapper to the unix getent utility (initgroups)
  getent:
    database: initgroups
  register: ITA_DFLT_getent_initgroups
```
