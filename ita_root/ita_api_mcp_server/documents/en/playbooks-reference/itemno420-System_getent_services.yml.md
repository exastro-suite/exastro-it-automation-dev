# Ansible Legacy Default Playbook - System_getent_services.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 420
- **playbook_name**: ~[Exastro standard] Get entry(services)
- **playbook_file**: System_getent_services.yml
## Overview
Queries the system services database using the Ansible getent module and stores the retrieved service name-to-port/protocol mappings in a registered variable for later use.
## Description
This playbook takes no input variables. It runs the Ansible `getent` module against the `services` database, which maps network service names to port numbers and protocols as normally found in `/etc/services`, and saves the output into the registered variable `ITA_DFLT_getent_services` so that later tasks can reference the service port information.
## Keyword
- service name to port mapping
- /etc/services lookup
- well-known port inventory
- TCP/UDP service registry
## Playbook
```yaml
- name: A wrapper to the unix getent utility (services)
  getent:
    database: services
  register: ITA_DFLT_getent_services
```
