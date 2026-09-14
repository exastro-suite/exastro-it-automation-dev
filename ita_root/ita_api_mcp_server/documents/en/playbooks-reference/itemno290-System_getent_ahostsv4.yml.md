# Ansible Legacy Default Playbook - System_getent_ahostsv4.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 290
- **playbook_name**: ~[Exastro standard] Get entry(ahostsv4)
- **playbook_file**: System_getent_ahostsv4.yml
## Overview
Uses the Ansible `getent` module to query the "ahostsv4" database on the target node via the getent utility and registers the returned entries.
## Description
This Playbook file is a wrapper around the Unix `getent` utility that queries the "ahostsv4" database, which returns IPv4 address entries for hosts on the target node.
This playbook takes no input parameters; the query target database ("ahostsv4") is fixed.
The retrieved entries are stored in the "ITA_DFLT_getent_ahostsv4" registered variable for use in subsequent tasks.
## Keyword
- IPv4 name resolution
- host address lookup
- getent database query
- DNS/hosts entry retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (ahostsv4)
  getent:
    database: ahostsv4
  register: ITA_DFLT_getent_ahostsv4
```
