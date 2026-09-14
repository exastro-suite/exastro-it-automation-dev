# Ansible Legacy Default Playbook - Windows_win_disk_image_unmount.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1050
- **playbook_name**: ~[Exastro standard][Win] Unmount
- **playbook_file**: Windows_win_disk_image_unmount.yml
## Overview
Uses the `community.windows.win_disk_image` module with `state: absent` to unmount a previously mounted disk image, such as an ISO file, on a Windows host.
## Description
"ITA_DFLT_mount_image_path": the path to the disk image (e.g., an ISO file) that is currently mounted and should be unmounted.
## Keyword
- ISO unmount
- disk image detach
- eject virtual drive
- mounted image cleanup
## Playbook
```yaml
- name: Unmount ISO
  community.windows.win_disk_image:
    image_path: "{{ ITA_DFLT_mount_image_path }}"
    state: absent
```
