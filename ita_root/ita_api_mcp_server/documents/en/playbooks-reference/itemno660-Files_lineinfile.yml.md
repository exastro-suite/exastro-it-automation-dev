# Ansible Legacy Default Playbook - Files_lineinfile.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 660
- **playbook_name**: ~[Exastro standard] Text line operation
- **playbook_file**: Files_lineinfile.yml
## Overview
Inserts, replaces, or removes a single line of text in a file on target hosts using Ansible's lineinfile module, matching against a regular expression.
## Description
This Playbook file uses the following variables to insert, update, or remove a line of text in a file:
- "ITA_DFLT_file_path": the path of the file to be edited.
- "ITA_DFLT_regexp": the regular expression used to find the line to replace or remove.
- "ITA_DFLT_line_string": the line content to insert or use as the replacement.
- "ITA_DFLT_line_state": whether the line should be present or absent in the file; defaults to "present" if not specified.
## Keyword
- edit configuration file
- text line insertion
- regular expression match
## Playbook
```yaml
- name: Insert or replace text lines.
  lineinfile:
    path: "{{ ITA_DFLT_file_path }}"
    regexp: "{{ ITA_DFLT_regexp }}"
    line: "{{ ITA_DFLT_line_string }}"
    state: "{{ ITA_DFLT_line_state | default('present') }}"
```
