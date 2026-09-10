# Ansible Legacy Default Playbook - System_getent_passwd.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 390
- **playbook_name**: ~[Exastro standard] Get entry(passwd)
- **playbook_file**: System_getent_passwd.yml
## Overview
Queries the system passwd database using the Ansible getent module and stores the retrieved user account entries in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `passwd` database, which contains user account information such as UID, GID, home directory, and shell, normally found in `/etc/passwd`, and saves the output into the registered variable `ITA_DFLT_getent_passwd` so that later tasks can reference the account information.
## Keyword
- user account lookup
- /etc/passwd entries
- UID and GID inventory
- account attribute retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (passwd)
  getent:
    database: passwd
  register: ITA_DFLT_getent_passwd
```
