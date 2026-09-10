# Ansible Legacy Default Playbook - Utilities_Logic_debug_verbosity-0.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 120
- **playbook_name**: ~[Exastro standard] Debug message (constant output)
- **playbook_file**: Utilities_Logic_debug_verbosity-0.yml
## Overview
Uses the `find` module to search for files under given path(s) matching an age and name pattern, then always prints the result via `debug` at verbosity level 0.
## Description
This playbook searches for files/directories matching specified criteria and always prints the search result as a debug message, regardless of the `-v` verbosity flags used when running the playbook.
- `ITA_DFLT_Target_Path`: One or more base paths to search under (list type).
- `ITA_DFLT_Name_Pattern`: A regular expression used to filter matched file/directory names (defaults to `.*`, matching everything).
- `ITA_DFLT_Age`: Filters files by age, e.g. how long since they were modified (defaults to `0s`, meaning no age filtering).
- `ITA_DFLT_Recurse`: Whether to search subdirectories recursively (defaults to `yes`).
## Keyword
- file search
- regex filter
- always-on logging
- diagnostic output
## Playbook
```yaml
- name: Return a list of files based on specific criteria
  find:
    age: "{{ ITA_DFLT_Age | default('0s') }}"
    file_type: any
    paths: "{{ item }}"
    patterns:
      - "{{ ITA_DFLT_Name_Pattern | default('.*') }}"
    recurse: "{{ ITA_DFLT_Recurse | default('yes') }}"
    use_regex: yes
  with_items:
    - "{{ ITA_DFLT_Target_Path }}"
  register: output

- name: Print statements during execution
  debug:
    var: output
    verbosity: 0
```
