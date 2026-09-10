# Ansible Legacy Default Playbook - Utilities_Logic_pause_in-minutes.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 590
- **playbook_name**: ~[Exastro standard] Sleep (minutes)
- **playbook_file**: Utilities_Logic_pause_in-minutes.yml
## Overview
Pauses playbook execution on target hosts for a configurable number of minutes using Ansible's pause module.
## Description
This Playbook file uses the time specified in "ITA_DFLT_Sleep_Minutes" to pause (sleep) Jobs and Jobflows.
## Keyword
- wait
- delay
- timer
## Playbook
```yaml
# This Playbook file uses the time specified in "ITA_DFLT_Sleep_Minutes" to pause (sleep) Jobs and Jobflows.
- name: pause
  pause:
    minutes: "{{ ITA_DFLT_Sleep_Minutes }}"


```
