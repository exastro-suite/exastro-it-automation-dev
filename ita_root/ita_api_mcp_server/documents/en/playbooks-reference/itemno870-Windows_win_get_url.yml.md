# Ansible Legacy Default Playbook - Windows_win_get_url.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 870
- **playbook_name**: ~[Exastro standard][Win] Download URL
- **playbook_file**: Windows_win_get_url.yml
## Overview
Downloads one or more files from HTTP, HTTPS, or FTP URLs to a remote Windows host using the win_get_url module, saving them to a specified or default directory.
## Description
- `ITA_DFLT_Download_URL`: the URL(s) of the file(s) to download via HTTP, HTTPS, or FTP (list type, multiple values can be specified).
- `ITA_DFLT_Destination_Directory`: the destination directory on the remote Windows host where downloaded files are saved; defaults to `%windir%\Temp` when not specified.
## Keyword
- Windows file download
- win_get_url module
- HTTP/FTP file retrieval
- temp directory download
## Playbook
```yaml
- name: Downloads files from HTTP, HTTPS, or FTP to node
  win_get_url:
    url: "{{ item }}"
    dest: "{{ ITA_DFLT_Destination_Directory | default ('%windir%\\Temp') }}"
  with_items:
    - "{{ ITA_DFLT_Download_URL }}"
```
