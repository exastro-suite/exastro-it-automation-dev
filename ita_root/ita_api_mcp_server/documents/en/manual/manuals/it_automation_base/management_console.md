# Management Console
# Introduction
This document describes the overview and operation methods of the management console of the ITA system.
# Overview
In the management console, in addition to the initial menus, if a using department wants to manage its own information in the ITA database, it is possible to create individual menus suited to the management level.
When registering/changing/deleting individual menus, please contact product support.
1        | Management Console         | Main menu              |
2        |                        | System settings                |
3        |                        | Menu group management        |
4        |                        | Menu management            |
5        |                        | Role/menu binding management    |
6        |                        | Operation deletion management      |
7        |                        | File deletion management            |
# Screen Description

## How to Access the Management Console
Upon successful login, ITA transitions to the main menu.
You can navigate to the management console by selecting the management console from the Dashboard on the main menu.
You can also navigate to a specific menu within the management console by selecting the management console from the menu group tab on the left side.
# Information on Each Individual Menu
This section describes the information for each individual menu.

## System Settings
Updates various information that should be configured during ITA system deployment and operation.
 System settings
-*No.** | **Item name**         | **Description**                                |
1       | Identification ID             | The ID used to identify the system setting.            |
2       | Item name             | The item name of the system setting.              |
3       | Setting value             | The setting value of the system setting.              |

## Menu Group Management
 Menu group management
-*No.** | **Item name**         | **Description**                                                |
1       | Menu group\  | The ID of the menu group.                              |
2       | Parent menu group\  | You can set the parent menu group.                    |
3       | Menu group\  | You can set the Japanese menu group name.              |
4       | Menu group\  | You can set the English menu group name.                |
5       | Panel image         | You can set the panel image for the menu group.\           |
6       | Parameter sheet\  | You can set the flag for whether it can be used\     |
creation usage flag     | as a "target menu group" in the parameter sheet creation function.          |
7       | Display order           | You can set the display order of the menu group on the Dashboard\  |
   - | Since this is a data update operation, please log in as a system administrator.
   - | The menu group name must be\ **unique**\ .
   - | Menu group names cannot be registered as duplicates.
   - | Menu groups are displayed on the main menu in ascending order of "display order". If the "display order" is the same, they are displayed in ascending order of "menu group ID".
   - | Only\ **PNG files**\ can be used for the "panel image".

## Menu Management
 Menu management
-*No.** | **Item name**         | **Description**                                                |
1       | Menu ID         | The ID of the menu.                                      |
2       | Menu group   | You can set the parent menu group.                |
3       | Menu name (ja)     | You can set the Japanese menu name.                      |
4       | Menu name (en)     | You can set the English menu name.                        |
5       | Menu name (rest)   | You can set the menu name used in REST.                        |
6       | Menu\          | You can set the display order in the submenu of the menu group\ |
7       | Auto filter\    | You can set whether the "Auto filter" \                   |
checkbox           | checkbox is checked by default when the menu is displayed.|
8       | Initial filter       | You can set the "Filter" \                         |
9       | Custom menu material | You can register a ZIP\                           |
for displaying a custom menu.                                     |
10      | Max web display rows    | You can set the maximum number of rows to display in the "list".              |
The maximum number of rows to display in the confirmation dialog can be set.        |
12      | Max Excel output rows  | You can set the maximum number of rows for Excel output.                   |
13      | Sort key         | You can set the sort order displayed in the "list".                |
   - | The menu name must be\ **unique**\ .
   - | The sort key must be set using JSON format notation.
   - | The maximum number of rows for Excel output can be set from 0 to 1048576.
   - | For the sort key, enter ASC/DESC for the item name and the key column name for the value. Example: {"ASC":"display_order"}
   - | "Remarks" is optional.
If "list of items for each menu" or "total number of history records for the list of items for each menu" exceeds the "maximum number of rows for Excel output",
downloading an Excel format file from the "Download all / Bulk file registration" tab will be aborted.

### Overview of the "Custom Menu Material" Function
This is the material used when a menu is registered directly in the Menu Management menu.
It is not used for menus created with existing menus or the parameter sheet creation function.
Compress the HTML, JavaScript, CSS, etc. that you want to display on the menu into a ZIP file and register it.
If "custom menu material" is not registered for a newly created menu, nothing will be displayed even if that menu is displayed.
To display a custom menu, after registering the "custom menu material", you need to grant "maintainable" or "view only" permission for the menu you want to display in the Role/Menu Binding Management menu.
For how to use custom menu materials and for samples, see .

## Role/Menu Binding Management
Registers/updates/discontinues the association between each menu and roles.
 Role/menu binding management
-*No.** | **Item name**         | **Description**                                   |
1       | UUID               | The ID of the role/menu binding management.         |
2       | Role             | You can set the role to bind.             |
3       | Menu           | You can set the menu to bind.           |
4       | Binding               | You can set whether the menu is made\    |
maintainable or view-only for the role. |

## Operation Deletion Management

## File Deletion Management
# Custom Menus

## How to Use Custom Menus

### Usage Procedure
(1) In the Menu Management menu, register the "custom menu material" and create a new menu.
Create the "custom menu material" to register by referring to .
   New menu registration
(2) In the Role/Menu Binding Management menu, grant "maintainable" or "view only" permission for the registered menu.
   Role/menu binding management registration
(3) Display the registered menu.

### Custom Menu Material Sample
Displays a menu similar to other ITA menus.
When displaying a menu created without registering "custom menu material"

## JavaScript Library Information

### jQuery

### select2

### Ace
A full-featured text editor for the web.

### ExcelJS

### diff2html

## IT Automation JavaScript/CSS Information

### common.js
This is a collection of various basic functions in the variable fn. It is required when using other ITA JavaScript.
-*Usage example**
Retrieves the operation list.
Registers data.
※Data registration is also possible with fn.fetch, but this one is dedicated to data registration and displays progress during registration.
FORMDATA | Please convert the registration data into form data and pass it.               |
-*Usage example**
Registers one operation.
     // Registration data
                 operation_name: 'Operation name',
     // Add the parameters to the form data (convert registerData to a string)
     // Register

### common.css

### ui.js
-*Usage example**
     // Menu information
             menu_name: 'Tab menu sample',
             menu_info: 'This is a tab menu sample.'
     // Tab definition
     // The function set above is called by name. It also becomes the tab's ID.
     // Menu title / description field

### table.js
Allows you to display and edit the Table for the specified parameter sheet.
INFO   | Menu information. Please pass the information obtained from "/menu/{menuNanmeRest}/info/". |
PARAMS | Specifies the required parameters. See the usage example below for details.                      |
-*Usage example**
Displays the operation list.
     // Operation list menu name (REST)
     // Get menu information
     // Get required parameters

### dialog.js
-*Usage example**
         // Dialog display definition
