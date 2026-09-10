# Ansible Legacy Default Playbook - Net_Tools_Basics_get_url.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 200
- **playbook_name**: ~[Exastro standard] Download URL
- **playbook_file**: Net_Tools_Basics_get_url.yml
## Overview
Uses the `get_url` module to download one or more files from HTTP, HTTPS, or FTP URLs to a destination directory on the target host.
## Description
This playbook downloads files from remote URLs to the target host.
- `ITA_DFLT_Download_URL`: One or more source URLs (HTTP, HTTPS, or FTP) to download (list type).
- `ITA_DFLT_Destination_Directory`: The local directory on the target host where downloaded files are saved (defaults to `/tmp/` if not specified).
## Keyword
- file download
- FTP transfer
- web resource retrieval
## Playbook
```yaml
- name: Downloads files from HTTP, HTTPS, or FTP to node
  get_url:
    url: "{{ item }}"
    dest: "{{ ITA_DFLT_Destination_Directory | default ('/tmp/') }}"
  with_items:
    - "{{ ITA_DFLT_Download_URL }}"
```
