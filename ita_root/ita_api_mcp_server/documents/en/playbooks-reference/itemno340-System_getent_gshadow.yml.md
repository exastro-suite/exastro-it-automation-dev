# Ansible Legacy Default Playbook - System_getent_gshadow.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 340
- **playbook_name**: ~[Exastro standard] Get entry(gshadow)
- **playbook_file**: System_getent_gshadow.yml
## Overview
Queries the system gshadow database using the Ansible getent module and stores the retrieved group shadow entries in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `gshadow` database, which holds the encrypted group password entries normally found in `/etc/gshadow`, and saves the output into the registered variable `ITA_DFLT_getent_gshadow` so that later tasks can reference the group password information.
## Keyword
- NSS group database
- encrypted group passwords
- Linux group administrator list
- account/group inventory lookup
## Playbook
```yaml
- name: A wrapper to the unix getent utility (gshadow)
  getent:
    database: gshadow
  register: ITA_DFLT_getent_gshadow
```
