# Ansible Legacy Default Playbook - Files_find.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 270
- **playbook_name**: ~[Exastro standard] Find file list
- **playbook_file**: Files_find.yml
## Overview
Uses the Ansible `find` module with regex pattern matching to search each given path for files/directories that match age, type, and name-pattern criteria, then prints the resulting file list.
## Description
This Playbook file searches for files matching specified criteria under the paths specified by "ITA_DFLT_Target_Path" (list type, checked one by one).
"ITA_DFLT_Age" controls the minimum age filter of the files to select (defaults to "0s" if not set).
"ITA_DFLT_File_Type" controls the type of file system object to match, such as file, directory, or any (defaults to "any" if not set).
"ITA_DFLT_Name_Pattern" specifies the regular expression pattern that file names must match (defaults to ".*" if not set).
"ITA_DFLT_Recurse" controls whether the search recurses into subdirectories (defaults to "yes" if not set).
The matched file list is registered as "ITA_RGST_File_Lists" and printed via a debug task.
## Keyword
- file search
- directory search
- pattern matching search
- recursive file lookup
## Playbook
```yaml
- name: Return a list of files based on specific criteria
  find:
    age: "{{ ITA_DFLT_Age | default('0s') }}"
    file_type: "{{ ITA_DFLT_File_Type | default('any') }}"
    paths: "{{ item }}"
    patterns:
      - "{{ ITA_DFLT_Name_Pattern | default('.*') }}"
    recurse: "{{ ITA_DFLT_Recurse | default('yes') }}"
    use_regex: yes
  with_items:
    - "{{ ITA_DFLT_Target_Path }}"
  register: ITA_RGST_File_Lists

- name: Print a list of files
  debug:
    var: ITA_RGST_File_Lists
    verbosity: 0
```
