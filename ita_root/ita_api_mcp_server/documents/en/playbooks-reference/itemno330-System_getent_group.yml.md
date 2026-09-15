# Ansible Legacy Default Playbook - System_getent_group.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 330
- **playbook_name**: ~[Exastro standard] Get entry(group)
- **playbook_file**: System_getent_group.yml
## Overview
Uses the Ansible `getent` module to query the "group" database on the target node via the getent utility and registers the returned entries.
## Description
This Playbook file is a wrapper around the Unix `getent` utility that queries the "group" database, which returns group account entries (such as group name, GID, and members) configured on the target node.
This playbook takes no input parameters; the query target database ("group") is fixed.
The retrieved entries are stored in the "ITA_DFLT_getent_group" registered variable for use in subsequent tasks.
## Keyword
- group account lookup
- getent database query
- GID and members retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (group)
  getent:
    database: group
  register: ITA_DFLT_getent_group
```
