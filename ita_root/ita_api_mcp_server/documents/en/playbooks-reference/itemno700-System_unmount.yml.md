# Ansible Legacy Default Playbook - System_unmount.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 700
- **playbook_name**: ~[Exastro standard] Unmount
- **playbook_file**: System_unmount.yml
## Overview
Uses the `ansible.posix.mount` module to unmount the filesystem at a specified path and remove its entry from `/etc/fstab` on the target host.
## Description
"ITA_DFLT_mount_path" specifies the path of the mount point to unmount and to remove from the fstab configuration on the target host.
## Keyword
- unmount filesystem
- fstab entry removal
- disk unmount
- storage management
## Playbook
```yaml
- name: Unmount device.
  ansible.posix.mount:
    path: "{{ ITA_DFLT_mount_path }}"
    state: absent
```
