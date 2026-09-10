# Ansible Legacy Default Playbook - Windows_win_disk_image_mount.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 950
- **playbook_name**: ~[Exastro standard][Win] Mount
- **playbook_file**: Windows_win_disk_image_mount.yml
## Overview
Mounts an ISO disk image on a Windows host as a virtual drive and displays the resulting mount path.
## Description
"ITA_DFLT_mount_image_path": Path to the ISO disk image file to be mounted on the target Windows host.
## Keyword
- Mount ISO image
- Virtual drive
- Disk image attach
## Playbook
```yaml
- name: Ensure an ISO is mounted
  community.windows.win_disk_image:
    image_path: "{{ ITA_DFLT_mount_image_path }}"
    state: present
  register: disk_image_out

- name: disk path
  debug:
    msg: "{{ disk_image_out.mount_paths[0] }}"

```
