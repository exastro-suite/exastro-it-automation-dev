# Ansible Legacy Default Playbook - System_getent_shadow.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 430
- **playbook_name**: ~[Exastro standard] Get entry(shadow)
- **playbook_file**: System_getent_shadow.yml
## Overview
Queries the system shadow database using the Ansible getent module and stores the retrieved encrypted user password entries in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `shadow` database, which holds encrypted user password entries and password aging information normally found in `/etc/shadow`, and saves the output into the registered variable `ITA_DFLT_getent_shadow` so that later tasks can reference the password entry information.
## Keyword
- encrypted user passwords
- /etc/shadow entries
- password aging information
- account credential inventory
## Playbook
```yaml
- name: A wrapper to the unix getent utility (shadow)
  getent:
    database: shadow
  register: ITA_DFLT_getent_shadow
```
