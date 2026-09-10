# Ansible Legacy Default Playbook - Windows_win_share_delete.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 840
- **playbook_name**: ~[Exastro standard][Win] Delete shared settings
- **playbook_file**: Windows_win_share_delete.yml
## Overview
Deletes existing Windows file share definitions on a remote host using the win_share module with state set to absent.
## Description
This Playbook file deletes shared names specified by "ITA_DFLT_Share_Name".
"ITA_DFLT_Share_Name" can specify multiple share names (list type).
## Keyword
- Windows file share removal
- win_share module
- delete network share
- shared folder cleanup
## Playbook
```yaml
# This Playbook file deletes shared names specified by "ITA_DFLY_Share_Name".
# "ITA_DFLT_Share_Name" can specify multiple share names (list type).
- name: delete Windows shares
  ansible.windows.win_share:
    name: "{{ item }}"
    state: absent
  with_items:
    - "{{ ITA_DFLT_Share_Name }}"
```
