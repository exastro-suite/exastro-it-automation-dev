# Ansible Legacy Default Playbook - Utilities_Logic_debug_verbosity-3.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 110
- **playbook_name**: ~[Exastro standard] Debug message (-vvv display)
- **playbook_file**: Utilities_Logic_debug_verbosity-3.yml
## Overview
Uses the Ansible `debug` module to print the value of a specified variable to the console, but only when the playbook is run with verbosity level 3 (-vvv).
## Description
"ITA_DFLT_Debug_Target": the variable or value to display in the debug output; its content is printed only when verbosity level 3 (-vvv) is used.
## Keyword
- verbose logging
- troubleshooting output
- variable inspection
## Playbook
```yaml
- name: Print statements during execution
  debug:
    var: "{{ ITA_DFLT_Debug_Target }}"
    verbosity: 3
```
