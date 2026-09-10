# Excel Bulk Export/Import
# Introduction
This document describes the functions and operation methods of the Excel Bulk Export/Import function in ITA.
# Overview of Excel Bulk Export/Import

## Details of Excel Bulk Export/Import

### About the Function
Excel Bulk Export/Import bundles the downloadable Excel files found in each menu into a zip file and performs export/import of them all at once. For information on the downloadable files, refer to "  ".
The menus that can be exported are limited to menus for which the "Association" item is set to "View Only" or "Maintainable" in the Role-Menu Association Management menu, and which have an editable Excel file.
The menus that can be imported are limited to menus for which the "Association" item is set to "Maintainable" in the Role-Menu Association Management menu, and which have an editable Excel file.
# Menus and Screen Configuration of Excel Bulk Export/Import

## Menu List
The menus of Excel Bulk Export/Import are shown below.
.. list-table:: ITA Menu List
- No.
     - Description
- 1
     - Excel Bulk Export
     - Bundles the downloadable files in each menu into a zip file and exports them.
- 2
     - Excel Bulk Import
     - Imports a zip file containing the bundled downloadable files.
- 3
     - Excel Bulk Export/Import Management
     -  Manages the status of exports executed from the Excel Bulk Export menu and imports executed from the Excel Bulk Export menu.
# Function and Operation Method Description

## Excel Bulk Export
Bundles the downloadable files in each menu into a zip file and exports them.
- Name
     - Description
- All Records
     - Exports all data.
- Excluding Discontinued
     - Exports data excluding data in the discontinued state.
- Discontinued Only
     - Exports only data in the discontinued state.
(2) Select the menus to export
The menus displayed are limited to menus for which the "Association" item is set to "Maintainable" or "View Only" in the Role-Menu Association Management menu, and which have an editable Excel file.
The execution No. of the export process is displayed, so check the status of the process in the Excel Bulk Export/Import Management menu.
   └─ 101_Management Console …③
       └─ System Settings_20210708235959.xlsx …④
- No.
     - Name
     - Extension
     - Description
- 1
     - File name
     - File
     - The file name is "ITA_FILES_YYYYMMDDhhmmss.zip".
- 2
     - MENU_LIST.txt
     - txt
     - A list of the exported menu REST names and file names is output.
- 3
     - Menu group folder
     - Folder
     - | Created for each menu group.
The folder name is "menu group ID_menu group name".
- 4
     - Downloaded file
     - xlsx
     - | Output as an Excel file.
Placed under the menu group folder to which it belongs.

## Excel Bulk Import
Edit the data exported from the Excel Bulk Export menu, and import it.
1. Create the list of files to import.
By editing MENU_LIST.txt in the zip exported from the Excel Bulk Export menu, you can edit the list of files to import.
MENU_LIST.txt records the menu REST names and file names as of the time of export.
Menu REST name:File name
         #Management Console
         system_settings:System Settings_20230425162004.xlsx
         operation_list:Operation List_20230425162005.xlsx
※The menus to import can also be selected in the Excel Bulk Import menu.
   #. Edit the files to import.
1.  Bundle the edited files into a zip file.
1. The contents of the file to import are as follows.
         └─ 101_Management Console …③
             └─ System Settings_20210708235959.xlsx …④
- No.
           - Name
           - Extension
           - Description
- 1
           - File name
           - File
           - The file name can be anything.
- 2
           - MENU_LIST.txt
           - txt
           - Records the REST names and file names of the menus to import.
- 3
           - Menu group folder
           - Folder
           - | Create one for each menu group.
The folder name is "menu group ID_menu group name".
- 4
           - Editable Excel file
           - xlsx
           - Place the editable Excel file under the menu group folder.
The menus whose checkbox is checked are imported.
For menus that do not need to be imported, uncheck the checkbox.
The execution No. of the import process is displayed, so check the status of the process in the Excel Bulk Export/Import Management menu.
1. Specifying two or more of the same menu REST name in MENU_LIST.txt
2. Specifying the same file name for two or more different menus in MENU_LIST.txt
4. Specifying a menu REST name in MENU_LIST.txt that does not exist
8. The menu group folder name does not follow the combination "menu group ID_menu group name".
9. The logged-in user does not have "Maintainable" permission for the target menu

## Excel Bulk Export/Import Management
Manages the status of exports executed from the Excel Bulk Export menu and imports executed from the Excel Bulk Import menu.
- Item
     - Description
- Execution No.
     - A unique ID is automatically assigned.
- Status
     - | Transitions in the order [Not Executed], [Running], [Completed].
- Process Type
     - | Export ... Excel Bulk Export
- Discontinuation Info
     - [All Records], [Excluding Discontinued], or [Discontinued Only] is displayed.
- Executing User
     - The user who executed the export or import process is displayed.
- File Name
     - | For an export, once the status becomes [Completed], the exported data is displayed; download and use it.
- Language
     - | The language used by the logged-in user is displayed.
- Result
     - | A text file describing the import result is displayed.
   101_Management Console:10101_System Settings
   Input file: System Settings_20230425155441.xlsx
   Registered: 0 records
   202_Ansible-Legacy:20201_Movement List
   Input file: Movement List_20230425155442.xlsx
   Registered: 0 records
   202_Ansible-Legacy:20202_Playbook Material Collection
   Input file: Playbook Material Collection_20230425155443.xlsx
   This is not the editable Excel file for this menu.
