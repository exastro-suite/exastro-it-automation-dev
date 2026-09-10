# Ansible Legacy Default Playbook - Windows_win_package_present.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 900
- **playbook_name**: ~[Exastro standard][Win] Install package
- **playbook_file**: Windows_win_package_present.yml
## Overview
Installs one or more Windows packages using win_package, matching package path, product ID, and installer arguments for each entry, and records the install results.
## Description
"ITA_DFLT_Install_Target_packages": Path to the installer package for each package to install.
"ITA_DFLT_Install_Target_packages_product_id": Product ID used to detect whether the corresponding package is already installed.
"ITA_DFLT_Install_Target_packages_with_args": Command-line arguments passed to the installer for the corresponding package.
Each of the variables can have multiple values specified at the same time (list type), and the values are paired positionally across the three lists.
## Keyword
- Windows software installation
- MSI/EXE installer
- Silent install arguments
## Playbook
```yaml
- name: Install package with list of arguments instead of a string
  ansible.windows.win_package:
    path: "{{ item.0 | default(omit) }}"
    product_id: "{{ item.1 | default(omit) }}"
    arguments: "{{ item.2 | default(omit) }}"
    state: present
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
