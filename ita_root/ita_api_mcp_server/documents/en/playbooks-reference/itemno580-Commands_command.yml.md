# Ansible Legacy Default Playbook - Commands_command.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 580
- **playbook_name**: ~[Exastro standard] Run command
- **playbook_file**: Commands_command.yml
## Overview
Executes an arbitrary shell command string on target hosts via the Ansible command module, registers the result, and prints it at debug verbosity level 3.
## Description
This Playbook file is simple.
It passes the variable given string, "ITA_DFLT_Command_String", to the Ansible command module and executes it.
The task results are displayed at debug level 3 (-vvv).
## Keyword
- arbitrary command execution
- shell command
- remote execution
## Playbook
```yaml
# This Playbook file is simple. 
# It passes the variable given string, "ITA_DFLT_Command_String", to the Ansible command module and executes it.
# The task results are displayed at debug level 3 (-vvv).
- name: Execute commands on targets
  command: "{{ ITA_DFLT_Command_String }}"
  register: ITA_RGST_Command_Result

- name: Debug the result
  debug:
    var: ITA_RGST_Command_Result
    verbosity: 3


```
