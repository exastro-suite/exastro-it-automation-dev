# Ansible Legacy Default Playbook - Windows_win_domain.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 790
- **playbook_name**: ~[Exastro standard][Win] Check Domain
- **playbook_file**: Windows_win_domain.yml
## Overview
Creates a new Active Directory domain in a new forest on the target Windows host, using paired lists of DNS domain names and Safe Mode Administrator passwords.
## Description
- `ITA_DFLT_dns_domain_name`: the DNS domain name(s) for the new Active Directory domain to be created (list type, multiple values can be specified).
- `ITA_DFLT_domain_safe_mode_password`: the Directory Services Restore Mode (Safe Mode) Administrator password(s) used when creating each corresponding domain (list type, multiple values can be specified).
## Keyword
- Active Directory domain creation
- new forest setup
- win_domain module
- domain controller promotion
- DSRM password
## Playbook
```yaml
- name: Create new domain in a new forest on the target host
  ansible.windows.win_domain:
    dns_domain_name: "{{ item.0 }}"
    safe_mode_password: "{{ item.1 }}"
  with_together:
    - "{{ ITA_DFLT_dns_domain_name }}"
    - "{{ ITA_DFLT_domain_safe_mode_password }}"
```
