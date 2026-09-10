# movement_list_ansible_legacy reference
## host_specific_format column
- It is determined by the setting values in the `device_list` menu of the target device.
    - If `ip_address` is set and `host_dns_name` is not set, set `IP`.
    - If `host_dns_name` is set and `ip_address` is not set, set `Host name`.

## header_section column
- Decide whether to add `become: true` based on whether root privileges are required.
- If it is unclear whether the task to be executed requires root privileges, confirm with the user whether root privileges are required and decide whether to add `become: true` accordingly.

