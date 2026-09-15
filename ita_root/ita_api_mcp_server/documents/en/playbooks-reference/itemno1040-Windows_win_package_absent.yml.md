# Ansible Legacy Default Playbook - Windows_win_package_absent.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 1040
- **playbook_name**: ~[Exastro standard][Win] Uninstall package
- **playbook_file**: Windows_win_package_absent.yml
## Overview
Uses `ansible.windows.win_package` with `state: absent` to uninstall Windows packages, matching path/product ID/arguments per item via paired lists, then debugs the result at verbosity 3.
## Description
"ITA_DFLT_Install_Target_packages": path(s) to the installer package(s) to uninstall, used as the `path` parameter for each entry (optional per item).
"ITA_DFLT_Install_Target_packages_product_id": product ID(s) of the package(s) to uninstall, used as the `product_id` parameter for each entry (optional per item).
"ITA_DFLT_Install_Target_packages_with_args": additional command-line arguments passed to the uninstaller for each package (optional per item).
These three lists are paired together so that entry N in each list corresponds to the same package. The uninstall result is registered as `ITA_RGST_WinPackageInstall_Result` and printed via debug output when verbosity level 3 (-vvv) is used.
## Keyword
- software uninstall
- MSI removal
- package deprovisioning
- silent uninstall
## Playbook
```yaml
- name: Uninstall package
  ansible.windows.win_package:
    path: "{{ item.0 | default(omit) }}"
    product_id: "{{ item.1 | default(omit) }}"
    arguments: "{{ item.2 | default(omit) }}"
    state: absent
  with_together:
    - "{{ ITA_DFLT_Install_Target_packages }}"
    - "{{ ITA_DFLT_Install_Target_packages_product_id }}"
    - "{{ ITA_DFLT_Install_Target_packages_with_args }}"
  register: ITA_RGST_WinPackageInstall_Result

- name: Debug the result
  debug:
    var: ITA_RGST_WinPackageInstall_Result
    verbosity: 3
```
