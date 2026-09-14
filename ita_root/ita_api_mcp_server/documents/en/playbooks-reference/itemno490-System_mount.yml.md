# Ansible Legacy Default Playbook - System_mount.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 490
- **playbook_name**: ~[Exastro standard] Mount
- **playbook_file**: System_mount.yml
## Overview
Mounts a filesystem or device on the target host at a specified path, using a given source, filesystem type, and optional mount options.
## Description
This Playbook file mounts a device or filesystem on the Target host using Ansible's mount module.
"ITA_DFLT_mount_path" specifies the mount point path where the device will be mounted.
"ITA_DFLT_mount_src" specifies the source device or path to be mounted.
"ITA_DFLT_mount_fstype" specifies the filesystem type of the device.
"ITA_DFLT_mount_opts" specifies optional mount options; if not set, no options are applied.
## Keyword
- filesystem mount
- disk mount
- storage configuration
- mount point setup
## Playbook
```yaml
- name: Mount up device.
  ansible.posix.mount:
    path: "{{ ITA_DFLT_mount_path }}"
    src: "{{ ITA_DFLT_mount_src }}"
    fstype: "{{ ITA_DFLT_mount_fstype }}"
    opts: "{{ ITA_DFLT_mount_opts | default(omit) }}"
    state: mounted
```
