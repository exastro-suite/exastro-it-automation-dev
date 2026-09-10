# Ansible Legacy Default Playbook - System_selinux_enforcing.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 210
- **playbook_name**: ~[Exastro standard] Enable SELinux (enforcing)
- **playbook_file**: System_selinux_enforcing.yml
## Overview
Uses the `ansible.posix.selinux` module to set the SELinux state to "enforcing" for a given policy on the target host.
## Description
This Playbook file changes the SELinux settings to "Enforcing".
Make sure to specify a policy name in "ITA_DFLT_Policy_Name".
(E.g. targeted)
## Keyword
- security policy
- mandatory access control
- turn on SELinux
## Playbook
```yaml
# This Playbook file changes the SELinux settings to "Enforcing".
# Make sure to specify a policy name in "ITA_DFLT_Policy_Name".
# (E.g. targeted)
- name: Change the SELinux policy state to enforcing
  ansible.posix.selinux:
    policy: "{{ ITA_DFLT_Policy_Name }}"
    state: enforcing
```
