# Ansible Legacy Default Playbook - System_getent_networks.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 380
- **playbook_name**: ~[Exastro standard] Get entry(networks)
- **playbook_file**: System_getent_networks.yml
## Overview
Queries the system networks database using the Ansible getent module and stores the retrieved network name-to-address mappings in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `networks` database, which maps symbolic network names to network addresses as normally found in `/etc/networks`, and saves the output into the registered variable `ITA_DFLT_getent_networks` so that later tasks can reference the network naming information.
## Keyword
- network name to address mapping
- /etc/networks lookup
- symbolic network identifiers
- subnet naming inventory
## Playbook
```yaml
- name: A wrapper to the unix getent utility (networks)
  getent:
    database: networks
  register: ITA_DFLT_getent_networks
```
