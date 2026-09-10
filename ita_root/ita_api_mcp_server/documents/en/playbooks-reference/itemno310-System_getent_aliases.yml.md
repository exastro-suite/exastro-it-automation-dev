# Ansible Legacy Default Playbook - System_getent_aliases.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 310
- **playbook_name**: ~[Exastro standard] Get entry(aliases)
- **playbook_file**: System_getent_aliases.yml
## Overview
Uses the Ansible `getent` module to query the "aliases" database on the target node via the getent utility and registers the returned entries.
## Description
This Playbook file is a wrapper around the Unix `getent` utility that queries the "aliases" database, which returns mail alias entries configured on the target node.
This playbook takes no input parameters; the query target database ("aliases") is fixed.
The retrieved entries are stored in the "ITA_DFLT_getent_aliases" registered variable for use in subsequent tasks.
## Keyword
- mail alias lookup
- getent database query
- sendmail/postfix aliases retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (aliases)
  getent:
    database: aliases
  register: ITA_DFLT_getent_aliases
```
