# Ansible Legacy Default Playbook - System_getent_rpc.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 410
- **playbook_name**: ~[Exastro standard] Get entry(rpc)
- **playbook_file**: System_getent_rpc.yml
## Overview
Queries the system rpc database using the Ansible getent module and stores the retrieved RPC program name-to-number mappings in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `rpc` database, which maps Remote Procedure Call (RPC) program names to their program numbers as normally found in `/etc/rpc`, and saves the output into the registered variable `ITA_DFLT_getent_rpc` so that later tasks can reference the RPC program information.
## Keyword
- RPC program number mapping
- /etc/rpc lookup
- remote procedure call registry
- NFS/RPC service inventory
## Playbook
```yaml
- name: A wrapper to the unix getent utility (rpc)
  getent:
    database: rpc
  register: ITA_DFLT_getent_rpc
```
