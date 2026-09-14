# Ansible Legacy Default Playbook - System_getent_hosts.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 350
- **playbook_name**: ~[Exastro standard] Get entry(hosts)
- **playbook_file**: System_getent_hosts.yml
## Overview
Queries the system hosts database using the Ansible getent module and stores the retrieved hostname-to-IP mappings in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `hosts` database, which contains hostname-to-IP-address mappings normally found in `/etc/hosts`, and saves the output into the registered variable `ITA_DFLT_getent_hosts` so that later tasks can reference the host resolution information.
## Keyword
- hostname to IP mapping
- /etc/hosts lookup
- name resolution inventory
- DNS static entries
## Playbook
```yaml
- name: A wrapper to the unix getent utility (hosts)
  getent:
    database: hosts
  register: ITA_DFLT_getent_hosts
```
