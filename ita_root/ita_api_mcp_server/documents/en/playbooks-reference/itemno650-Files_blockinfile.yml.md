# Ansible Legacy Default Playbook - Files_blockinfile.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 650
- **playbook_name**: ~[Exastro standard] Text block operation
- **playbook_file**: Files_blockinfile.yml
## Overview
Inserts, replaces, or removes a marked multi-line block of text within a file on target hosts using Ansible's blockinfile module.
## Description
This Playbook file uses the following variables to insert, update, or remove a block of text in a file:
- "ITA_DFLT_file_path": the path of the file to be edited.
- "ITA_DFLT_block_marker": the marker text used to identify the boundaries of the managed block; if omitted, the module default marker is used.
- "ITA_DFLT_block_state": whether the block should be present or absent in the file; defaults to "present" if not specified.
- "ITA_DFLT_insertafter": a pattern indicating where the block should be inserted after; if omitted, the module default behavior is used.
- "ITA_DFLT_block_string": the text content of the block to insert; if omitted, no block content is set.
## Keyword
- edit configuration file
- text block insertion
- managed block
## Playbook
```yaml
- name: Insert or replace text blocks.
  blockinfile:
    path: "{{ ITA_DFLT_file_path }}"
    marker: "{{ ITA_DFLT_block_marker | default(omit) }}"
    state: "{{ ITA_DFLT_block_state | default('present') }}"
    insertafter: "{{ ITA_DFLT_insertafter | default(omit) }}"
    block: |
      {{ ITA_DFLT_block_string | default(omit) }}
```
