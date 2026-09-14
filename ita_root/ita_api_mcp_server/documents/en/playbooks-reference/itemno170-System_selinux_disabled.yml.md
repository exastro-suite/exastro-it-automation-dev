# Ansible Legacy Default Playbook - System_selinux_disabled.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 170
- **playbook_name**: ~[Exastro standard] Disable SELinux
- **playbook_file**: System_selinux_disabled.yml
## Overview
Uses the `ansible.posix.selinux` module to set the SELinux state to "disabled" for a given policy on the target host.
## Description
This Playbook file changes the SELinux settings to "Disabled".
Make sure to specify a policy name in "ITA_DFLT_Policy_Name".
(E.g. targeted)
## Keyword
- security policy
- mandatory access control
- turn off SELinux
## Playbook
```yaml
# This Playbook file changes the SELinux settings to "Disabled".
# Make sure to specify a policy name in "ITA_DFLT_Policy_Name".
# (E.g. targeted)
- name: Change the SELinux policy state to disabled
  ansible.posix.selinux:
    policy: "{{ ITA_DFLT_Policy_Name }}"
    state: disabled
```
