# Ansible Legacy Default Playbook - Utilities_Logic_pause_in-seconds.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 600
- **playbook_name**: ~[Exastro standard] Sleep (seconds)
- **playbook_file**: Utilities_Logic_pause_in-seconds.yml
## Overview
Pauses playbook execution on target hosts for a configurable number of seconds using Ansible's pause module.
## Description
This Playbook file uses the time specified in "ITA_DFLT_Sleep_Seconds" to pause (sleep) Jobs and Jobflows.
## Keyword
- wait
- delay
- timer
## Playbook
```yaml
# This Playbook file uses the time specified in "ITA_DFLT_Sleep_Seconds" to pause (sleep) Jobs and Jobflows.
- name: pause
  pause:
    seconds: "{{ ITA_DFLT_Sleep_Seconds }}"


```
