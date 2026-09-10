# Ansible Legacy Default Playbook - System_getent_ahosts.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 280
- **playbook_name**: ~[Exastro standard] Get entry(ahosts)
- **playbook_file**: System_getent_ahosts.yml
## Overview
Uses the Ansible `getent` module to query the "ahosts" database on the target node via the getent utility and registers the returned entries.
## Description
This Playbook file is a wrapper around the Unix `getent` utility that queries the "ahosts" database, which returns all address entries (IPv4 and IPv6) for hosts on the target node.
This playbook takes no input parameters; the query target database ("ahosts") is fixed.
The retrieved entries are stored in the "ITA_DFLT_getent_ahosts" registered variable for use in subsequent tasks.
## Keyword
- name resolution
- host address lookup
- getent database query
- DNS/hosts entry retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (ahosts)
  getent:
    database: ahosts
  register: ITA_DFLT_getent_ahosts
```
