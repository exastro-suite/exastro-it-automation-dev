# Ansible Legacy Default Playbook - System_getent_ethers.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 320
- **playbook_name**: ~[Exastro standard] Get entry(ethers)
- **playbook_file**: System_getent_ethers.yml
## Overview
Uses the Ansible `getent` module to query the "ethers" database on the target node via the getent utility and registers the returned entries.
## Description
This Playbook file is a wrapper around the Unix `getent` utility that queries the "ethers" database, which returns Ethernet (MAC) address to hostname mapping entries configured on the target node.
This playbook takes no input parameters; the query target database ("ethers") is fixed.
The retrieved entries are stored in the "ITA_DFLT_getent_ethers" registered variable for use in subsequent tasks.
## Keyword
- MAC address lookup
- getent database query
- Ethernet address mapping retrieval
## Playbook
```yaml
- name: A wrapper to the unix getent utility (ethers)
  getent:
    database: ethers
  register: ITA_DFLT_getent_ethers
```
