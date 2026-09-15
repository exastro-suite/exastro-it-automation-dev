# Ansible Legacy Default Playbook - System_getent_protocols.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 400
- **playbook_name**: ~[Exastro standard] Get entry(protocols)
- **playbook_file**: System_getent_protocols.yml
## Overview
Queries the system protocols database using the Ansible getent module and stores the retrieved network protocol name-to-number mappings in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `protocols` database, which maps network protocol names to their protocol numbers as normally found in `/etc/protocols`, and saves the output into the registered variable `ITA_DFLT_getent_protocols` so that later tasks can reference the protocol information.
## Keyword
- protocol name to number mapping
- /etc/protocols lookup
- IP protocol identifiers
- network protocol inventory
## Playbook
```yaml
- name: A wrapper to the unix getent utility (protocols)
  getent:
    database: protocols
  register: ITA_DFLT_getent_protocols
```
