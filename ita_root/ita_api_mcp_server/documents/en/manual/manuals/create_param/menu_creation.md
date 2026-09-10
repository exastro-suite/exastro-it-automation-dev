# Parameter Sheet Creation Function
# Introduction
This document describes the functions and operation methods of parameter sheet creation.
# Overview of the Parameter Sheet Creation Function
The parameter sheet creation function is a function for creating menus that can be operated on ITA.
There are two types of menus that can be created: "parameter sheets" and "data sheets".
Created menus (parameter sheets/data sheets) can be operated from Web, Excel, and REST API, just like other menus.
The number, format, size, and input restrictions of the items in a menu (parameter sheet/data sheet) can be freely designed using the parameter sheet creation function.
By using it as the reference source for items selected via pulldown from other menus, it is also possible to prevent inconsistencies in wording.

## Parameter sheet
- | **Managing IaC variable values**
You can create parameter sheets that can be configured in the "Auto-Registration Settings for Assigned Values" menu of each driver.
Menus created by selecting "Parameter sheet (with host/operation)" or "Parameter sheet (with operation)" in the "Creation Target" item of the "Basic Information" frame of the "Parameter Sheet Creation Information" tab of the "Parameter Sheet Definition/Creation" menu (under the "Parameter Sheet Creation" menu group) are called parameter sheets.
By configuring the target parameter sheet and IaC variable in the "Auto-Registration Settings for Assigned Values" menu of each driver, the value entered in the "Parameter" item of the parameter sheet can be automatically assigned to the IaC variable.
     Example of parameter sheet usage
- | List of options available for a parameter sheet
  - | **With host/operation**
The parameter sheet is created on a per "host" and "operation" basis.
  - | **With operation**
The parameter sheet is created on a per "operation" basis.
  - | **Using host groups**
By linking with "", you can manage IaC variable values for host groups.
  - | **Using bundles**
When configuring parameters that repeat the same item, you can use bundles to improve visibility.

## Data sheet
- | **Managing data within ITA**
You can create data sheets with freely defined items. Data sheets cannot be used with the "Auto-Registration Settings for Assigned Values" menu of each driver.
This can be used to manage information on ITA as a CMDB (Configuration Management Database).
# Main Functions of the Parameter Sheet Creation Function
The main functions of the parameter sheet creation function are classified into the following categories.
-  | Web
-  | Backyard
# Menu Groups of the Parameter Sheet Creation Function
The "Parameter Sheet Creation" menu group and the menus that belong to it are as follows.
-  | When creating a parameter sheet or data sheet using the "Parameter Sheet Definition/Creation" menu, data is automatically registered in each of the "Parameter Sheet Definition List", "Column Group Management", and "Menu Item Creation Information" menus, so there is no need to create data within each of those menus.
-  | If you want to use a hidden menu, restore the target menu using "Role/Menu Association Management".
（For the restoration/discontinuation procedure, refer to  .）
    Menus belonging to the "Parameter Sheet Creation" menu group
-*Menu\ | **Menu it\      | **Sub-\                              | **Description**                    |
        | belongs to**    | menu**                               |                                     |
Parameter\| Parameter Sheet\ | \ \ \           | Creates a parameter\                |
Sheet\ | Definition/Creation |                                       | sheet or data sheet and its associ\|
| Parameter sheet or\                 |
Parameter\ | \ \           | Maintains the parameter\            |
Sheet Def\ |                                       | sheet or data sheet to be created.  |
inition List |                                       |                                      |
Parameter\ | \ \             | Checks the status of parameter\     |
Sheet\ |                                       | sheet creation.                     |
Column Group\ | \ \        | Maintains the columns of the para\  |
Management\ |                                       | meter sheet or data sheet to be cre\|
| Hidden menu at install time.        |
Parameter\ | \ \      | Maintains the items managed by\     |
Sheet Item\ |                                       | the parameter sheet or data sheet\  |
Creation Information |                                       | to be created.                      |
| Hidden menu at install time.        |
Parameter\ | \ \       | Maintains the unique constraint\    |
| Hidden menu at install time.        |
(multiple items)\     |                                       | of the parameter sheet or data she\ |
| Hidden menu at install time.        |
Parameter\ |\ \           | Displays the association between\   |
Sheet Def-Table\|                                       | the created parameter sheet and\    |
Association Management |                                       | the DB table.                       |
| Hidden menu at install time.        |
Other Menu Integration | \ \       | Displays the association of the\    |
| menu group, menu, item, and DB tab\ |
| Hidden menu at install time.        |
| Menu for managing items. (for single choice) |
| Hidden menu at install time.        |
| Menu for managing items. (for two-choice)    |
| Hidden menu at install time.        |
| Hidden menu at install time.        |
Although the "Parameter Sheet Definition/Creation" menu allows you to maintain parameter sheets and data sheets one at a time, if you want to maintain multiple parameter sheets and data sheets at once, you can use Excel to perform bulk maintenance from each menu in the "Parameter Sheet Creation" menu group.
# About Parameter Sheets and Data Sheets
- | Classification of the sheet to create
Select "Parameter Sheet Creation" menu group --> "Parameter Sheet Definition/Creation" menu, and in the "Creation Target" field within the "Parameter Sheet Creation Information" tab,
  - | Selecting "Parameter Sheet" and executing parameter sheet creation
A menu (\ **parameter sheet)**\ whose items can be configured in the "Auto-Registration Settings for Assigned Values" menu of each driver is created.
     Menu (parameter sheet) created by selecting "Parameter Sheet" in the "Creation Target" field
  - | Selecting "Data Sheet" and executing parameter sheet creation
A menu (\ **data sheet)**\ that cannot be used in the "Auto-Registration Settings for Assigned Values" menu is created.
     Menu (data sheet) created by selecting "Data Sheet" in the "Creation Target" field
   Comparison of parameter sheets and data sheets
-*Value selected\   | **Auto-Registr\  | **Menu item**       | **Relationship wi\  |
for Creation Ta\   | ation Settings\ |                     | th host/operation** |
rget**             | for Assigned\   |                     |                      |
                    | Values**         |                     |                      |
Parameter\       | Configurable | "Host"\             | Specific "\          |
Parameter\       | Configurable | "Operation"\        | Specific "\          |
Data\             | Not configurable | All items\      | "Host"\              |
Data sheets are intended for use as the reference source for items selected via pulldown from other menus, or for uses such as centrally managing data on ITA as a CMDB (Configuration Management Database).
- | Parameter sheet creation patterns
There are a total of 5 creation patterns for parameter sheets that can be created.
1. Parameter sheet selected & "Host group" used & "Bundle" used
1. Parameter sheet selected & "Host group" used
1. Parameter sheet selected & "Bundle" used
1. Parameter sheet selected
1. Data sheet selected
When a parameter sheet is selected, a menu (parameter sheet) is created for each of 3 menu groups.
  - | A. For input
  - | B. For auto-registration of assigned values
  - | C. For reference
When a data sheet is selected, a menu (data sheet) is created for 1 menu group.
  - | A) For input
Maintenance (register/update/discontinue/restore) operations on a menu (parameter sheet/data sheet) can only be performed from the "A) For Input" menu group; maintenance (register/update/discontinue/restore) operations cannot be performed from any other menu group.
     Parameter sheet creation patterns
-*Menu\ | **Menu\  | **Maintenance**    |
for registration       |                     |
    - | Using host groups
When grouping target work hosts using the host group function, we recommend using host groups. For details about the host group function, refer to "".
When parameter sheet "Parameter Sheet 1" and data sheet "Data Sheet 1" are created,
the appearance in each of the For Input, For Auto-Registration of Assigned Values, and For Reference groups is as follows.
# Operation Description of the "Parameter Sheet Definition/Creation" Menu
In the "Parameter Sheet Definition/Creation" menu of the "Parameter Sheet Creation" menu group, you can create a parameter sheet and configure its items at the same time.
   "Parameter Sheet Definition/Creation" menu

## (A) Configuring items/groups
Create the items to be configured in the parameter sheet.
The recommended number of items that can be added to one parameter sheet is 100, and the upper limit is 1000.
If there are many items, it may affect the display and behavior of the parameter sheet.
When you enter an item, it can be added to the parameter sheet as an item.
Configure the column group.
Dragging and dropping an item onto the area of a displayed column group allows you to configure it.
Multiple items can be configured for a single group.
      Column group in menu
Reverts the entered/configured item to its previous state.
-  | Item name definition
      Item name definition
-  | Item name definition (for REST API)
      Item name definition (for REST API)
-  | Input method selection
Select the input method from the pulldown menu.
 Configuration items for each input method
-*Configuration point**                |     | **Description/Item to be created**                                 |
Initial\ | When registering data from the created parameter sheet\     |
| A value that exceeds the "Maximum byte count" set for the item, or\       |
| when data is exported to Excel from the created parameter\       |
| sheet, the initial value is set in the blank cell of the item.\  |
Initial\ | When registering data from the created parameter\               |
value\ | sheet, enter the value that appears by default in the input field.\   |
| A value that is less than the "Minimum value" set for the item, or\             |
| when data is exported to Excel from the created parameter\       |
| sheet, the initial value is set in the blank cell of the item.\  |
Initial\ | When registering data from the created parameter sheet\     |
| A value that is less than the "Minimum value" or exceeds the "Maximum value" set for the item,\ |
| or when data is exported to Excel from the created parameter\       |
| sheet, the blank cell will contain the value set as the initial value.  |
Input\ | Initial\ | When registering data from the created parameter\               |
| value\ | sheet, enter the value that appears by default in the input field.\   |
Input\ | Initial\ | When registering data from the created parameter\               |
| value\ | sheet, enter the value that appears by default in the input field.\   |
Input\ | Sele\ | Created parameter sheet\                         |
| ction\ | "Menu group: Menu: Item" structure.    |
reference\ | for the item, another item that exists in the same parameter sheet\ |
| For detailed usage,\                                   |
Initial\ | When registering data from the created parameter sheet,\ |
| the value registered in the "Selection items" set for the item\       |
| is used. Also, when data is exported to Excel from the created\  |
| parameter sheet, the blank cell of the item is set with the\           |
| initial value.\           |
Item\ | Type\ | The maximum is set with\                    |
Initial\ | When registering data from the created parameter sheet,\ |
| the "Maximum byte count"\                   |
| set for the item, and also from the created parameter\               |
| sheet, the set value is applied.                    |
Parameter sheet reference        | For the item of a menu created with the creation target "Parameter sheet (with operation)",\ |
when data is registered, the value of the matching operation\   |
Input\ | Sele\ | Selects the item of a menu created with the creation target "Parameter sheet\ |
ction\ | (with operation)" from a pulldown\   |
 For details about linked items for auto-registration of assigned values, refer to  .
 Configuration items common to all input methods
-*Configuration point**                | **Description**                                                      |
Required                        | Sets whether an item is required, using a checkbox.    |
Unique constraint item                | Sets whether an item is a unique constraint item, using a checkbox.|

## (B) "Parameter Sheet Creation Information" tab
- | Enter the information required to create the parameter sheet.
  - | "Basic Information" frame
     "Basic Information" frame settings
-*Setting\    | **Description**                                  | **Cre\        |
No.     | Parameter sheet creation\                     | Displayed  | Displayed |
When editing the menu (parameter sheet/data sheet), the item number of the menu is displayed. |       |      |
Parameter\| Enter the name of the parameter sheet\                 | Displayed  | Displayed |
sheet\| to be created. The name\   |       |      |
name       | "Main Menu" cannot be used as a menu name.  |       |      |
Creation Target | From the pulldown, select "Parameter\               | Displayed  | Displayed |
sheet (with host/operation)", "\  |       |      |
"Parameter sheet (with operation)", or\ |       |      |
"Data sheet", the "Target Menu Group\   |       |      |
"Parameter sheet (with host/operation)\  |       |      |
"Parameter sheet (with operation)"\ |       |      |
checkbox and the "Target Menu\         |       |      |
For Input" field and "For Reference" field are displayed.  |       |      |
Display\ | The display in the menu group\               | Displayed  | Displayed |
Order Group | when "Parameter sheet (with host/opera\ |       | Displayed |
Creates the parameter sheet.            |       |      |
Creates the parameter sheet.            |       |      |
When "Parameter sheet" is selected in the "Creation Target" field\ |       | Displayed |
creates the corresponding parameter sheet.  |       |      |
The last updated by "Parameter Sheet Creation\       |       |      |
Function" (the user used by Backyard when updating a record)\|       |      |
The last updated by "Parameter Sheet Creation\         |       |      |
Function" (the user used by Backyard when updating\|       |      |
The options for Creation Target and the patterns available for auto-registration of assigned values for each driver are described below.
    .. list-table:: Creation target and applicability to auto-registration of assigned values for each driver
- |
         - | Parameter sheet
(with host/operation)
         - | Parameter sheet
(with operation)
         - | Data sheet
- | 
         - | ○
         - | △
         - | ▲
- | 
         - | ×
         - | ○
         - | ▲
              - | ○	: Selectable for auto-registration of assigned values.
              - | ×	: Not selectable for auto-registration of assigned values.
              - | △	: Not selectable for auto-registration of assigned values, but the value can be used from a parameter sheet that uses parameter sheet reference.
A parameter sheet created with "Creation Target" set to "Parameter sheet (with host/operation)" and the item set to "Parameter sheet reference"
              - | ▲	: Not selectable for auto-registration of assigned values, but the value can be used from a parameter sheet that uses pulldown reference.
A parameter sheet created with "Creation Target" set to "Parameter sheet (with host/operation)/Parameter sheet (with operation)" and the item set to "Pulldown"
※For "Parameter sheet reference" and "Pulldown", refer to  .
  - | "Target Menu Group" frame
Displays the menu group used when creating the parameter sheet.
     "Target Menu Group" frame settings
-*Setting\| **Description**                                     | **Cre\         |
Input\  | The default value is the "For Input" menu group.     | Displayed  | Displayed  |
The menu group name selected is displayed. |       |       |
assign\| is the "For Auto-Registration of Assigned Values" menu group. |       | Displayed  |
If the field is "Parameter sheet", the "Target Menu\|       |       |
The menu group name selected is displayed. |       |       |
※"Target Menu Group\                     |       |       |
For\  | is the "For Reference" menu group.           |       | Displayed  |
If the field is "Parameter sheet", the "Target Menu\|       |       |
The menu group name selected is displayed. |       |       |
The image is for the case where "Parameter Sheet" is selected in the "Creation Target" field.
      - | Select the menu group that will be the target for creating the parameter sheet.
      - | By default, the "For Input", "For Auto-Registration of Assigned Values", and "For Reference" menu groups are selected.
      - | If you do not want to use the default menu groups, create them in advance in the "Admin Console" menu group. (For details on how to create them, refer to  .)
  - | "Unique Constraint (Multiple Items)" frame
This is a function that, when registering data in the created menu, controls so that the same combination of records cannot be registered for the specified multiple items.
       Menu with "Unique Constraint (Multiple Items)" configured
      - | The following patterns will result in a validation error.
  - | "Access Permission Role" frame
    - | When a role is selected
The parameter sheet definition (each menu under the "Parameter Sheet Creation" menu group) can only be accessed by the selected role.
The created menu (parameter sheet/data sheet) can only be accessed by the role selected in the "Role/Menu Association Management" menu settings.
    - | When no role is selected
The parameter sheet definition (each menu under the "Parameter Sheet Creation" menu group) can be accessed by all roles.
The created menu (parameter sheet/data sheet) can only be accessed by the system administrator role and the role to which the creating user belongs, according to the "Role/Menu Association Management" menu settings.

## (C) "Preview"
- | "Preview" tab
- | "Log" tab

## (D) "Create"
Clicking this after entering the required items creates the parameter sheet.
     Parameter sheet creation history
When a parameter sheet is created with the "Parameter Sheet Definition/Creation" menu,
data is automatically entered into each of the "Parameter Sheet Definition List", "Column Group Management", "Parameter Sheet Item Creation Information", "Unique Constraint (Multiple Items) Creation Information", and "Parameter Sheet Role Creation Information" menus.

## How to Use the "Parameter Sheet Definition/Creation" Menu After Parameter Sheet Creation Has Been Accepted
After newly creating a parameter sheet with the "Parameter Sheet Definition/Creation" menu, you can edit or initialize the created parameter sheet, or create a new parameter sheet by reusing the created parameter sheet as a template.
（The setting values of existing items and some parts of the basic information cannot be modified.）
Make sure the parameter sheet name is different from any existing menu name.
For existing items, you can freely change the setting values of "Item Name", "Regular Expression", "Description", and "Remarks".
For the setting values of "Maximum Byte Count", "Minimum Value", "Maximum Value", "Number of Digits", and "Maximum File Byte Count", you can only change them to a value larger than the original value.
If you change the "Regular Expression", even if the already registered data becomes inconsistent with the changed "Regular Expression", the data is retained.
Even if you check "Required" or "Unique Constraint", since the record may be empty, inconsistencies may occur in the registered data.
If you change the target menu group, the menu created in the previously selected menu group is discontinued, and it is newly registered in the changed menu group. (In this case as well, the registered data is retained.)
You cannot change the settings for "Parameter Sheet Name", "Creation Target", "Use Host Group", or "Use Bundle" in "Basic Information".
If you update item data from the "Parameter Sheet Item Creation Information" menu and then execute "Create (Edit)", inconsistencies may occur in the created parameter sheet.
When editing an existing parameter sheet, since item names cannot be swapped between items, changing an item name may cause an error when creating.
The edited content is discarded, and it reverts to the state of the registered content.
If you change the target menu group, the menu created in the previously selected menu group is discontinued, and it is newly registered in the changed menu group.
You cannot change the "Parameter Sheet Name" in "Basic Information".
There are no restrictions on editing other than "Parameter Sheet Name", but all data registered in the "For Input" menu group will be deleted.
When editing an existing parameter sheet, since item names cannot be swapped between items, changing an item name may cause an error when creating.
The edited content is discarded, and it reverts to the state of the registered content.

## Checking Parameter Sheets in the "Parameter Sheet Definition List" Menu
The "Parameter Sheet Definition List" menu allows you to check and perform the following operations.
- | Display a list of created parameter sheets
- | Maintain (view/update/discontinue/restore) created parameter sheets
You can maintain (view/update/discontinue/restore) parameter sheets.
   "Parameter Sheet Definition List" menu
By setting arbitrary values in each item in "Parameter Sheet Definition List", you can filter the definition list using those values as filter elements.
 "Parameter Sheet Definition List" menu settings
-*Setting\ | **Description**                                    | **Cre\|      |
Parameter\ | Enter the name of the parameter sheet\                   | Displayed | Displayed |
sheet\ | to be created. The name\       |      |      |
When "Parameter Sheet Creation Status" is "Created"\ |      |      |
Parameter\ | Enter the name of the parameter sheet\                   | Displayed | Displayed |
When "Parameter Sheet Creation Status" is "Created"\ |      |      |
Parameter\ | Enter the name of the parameter sheet\                   | Displayed | Displayed |
(rest)  | When "Parameter Sheet Creation Status" is "Created"\ |      |      |
Sheet\  | Select the "Creation Target" of the parameter sheet to be created\   | Displayed | Displayed |
"Parameter sheet (with host/operation\  |      |      |
)" or "Parameter sheet (with operation)" |      |      |
Table\     | The display in the menu group\                   | Displayed | Displayed |
le      | When "Parameter Sheet" is selected in the "Creation Target" field\ |      | Displayed |
you can set "Bundle" to True.    |      |      |
Creates the parameter sheet.              |      |      |
Group| When "Parameter sheet\             |      | Displayed |
(with host/operation)" is selected in the "Creation Target"\  |      |      |
you can set it to True.                        |      |      |
Creates the corresponding parameter sheet.      |      |      |
Input\   | Select from the pulldown the menu group that will\ | Displayed | Displayed |
For Input Menu\ | create the input parameter sheet and data sheet\ |      |      |
Auto-\ | If the field is "Parameter Sheet", you can select the "Auto-\ |      | Displayed |
Registration\ | Registration of Assigned Values Menu Group" field.  |      |      |
Group\ | that creates the parameter sheet for auto-registration of assigned values.  |      |      |
For\ | If the "Creation Target" field is "Parameter Sheet", you can select the "\ |      | Displayed |
Reference\ | For Reference Menu Group" field.  |      |      |
※       | The menu group that creates the reference parameter sheet\       |      |      |
Parameter\ | If parameter sheet creation is\                     | Displayed | Displayed |
in progress, the "Parameter Sheet Name" cannot be changed\     |      |      |
If you do not want to use the default menu groups, create them in advance in the "Admin Console" menu group. (For details on how to create them, refer to  .)
About discontinuation of records in the Parameter Sheet Definition List
The Parameter Sheet Definition List is the configuration information for creating parameter sheets.
Even if you discontinue a parameter sheet record in the Parameter Sheet Definition List, no change occurs to the menu (already-created parameter sheet) in Admin Console --> Menu List.
If you want to discontinue an already-created parameter sheet, refer to  .

## Checking Creation Status in the "Parameter Sheet Creation History" Menu
Check the status of parameter sheet creation.
   "Parameter Sheet Creation History" menu
When the status becomes "Completed" (typically within several tens of seconds), the menu (parameter sheet/data sheet) is added to the menu group.
 Items in the "Parameter Sheet Creation History" menu
-*Item name** | **Description**                                                |
Parameter\| The name of the parameter sheet to be created.                      |
Status | The status of the parameter sheet creation progress.              |
State before parameter sheet creation                            |
Backyard is executing the parameter sheet creation process              |
Parameter sheet creation completed successfully                        |
State in which the parameter sheet creation ended with an error              |
Creation Ty\  | The type of parameter sheet creation.                    |
New creation: When a new parameter sheet was created          |
Initialization: When an existing parameter sheet was initialized            |
Edit: When an existing parameter sheet was edited                |

## Checking the Created Parameter Sheet
This describes the parameter sheets in the following patterns (1)–(3), which are created depending on the values selected in the "Basic Information" frame of the "Parameter Sheet Creation Information" tab of the "Parameter Sheet Definition/Creation" menu (under the "Parameter Sheet Creation" menu group).
1. **Data sheet**
A. For Input menu group
1. **Parameter sheet**
A. For Input menu group
B. For Auto-Registration of Assigned Values menu group
C. For Reference menu group
1. **Parameter sheet & bundle usage**
A. For Input menu group
B. For Auto-Registration of Assigned Values menu group
C. For Reference menu group
1. **Parameter sheet & host group usage**
A. For Input menu group
B. For Auto-Registration of Assigned Values menu group
C. For Reference menu group

#### 1. When "Data Sheet" is selected in the "Creation Target" field
If "Data Sheet" is selected in the "Creation Target" field of the "Parameter Sheet Definition/Creation" menu (or the "Parameter Sheet Definition List" menu) when creating a parameter sheet, a data sheet is created.
Confirm that the data sheet has been added to the menu group specified in the "For Input (Menu Group)" field.
   "For Input" menu group
A) For Input menu group (data sheet)
-**************************************
A data sheet is created that can be maintained (registered/updated/discontinued/restored).
   Data sheet created under the For Input menu group
 Item list (data sheet "For Input" menu)
-*Item**                          | **Description**                     | **Requi\   | **Input method** | **Constraints**    |
Parameter      | [Created item\  | The item created in "Parameter Sheet Def\    | Depends on\ | Depends on\    | Depends on\       |
name]             | inition/Creation" is displayed\| the item setting\ | the item setting\  | the item setting\     |
Since a data sheet is not associated with a specific host/operation, the host/operation items are not displayed.
Data sheets are not created in the "For Auto-Registration of Assigned Values" and "For Reference" menu groups.

#### 2. When "Parameter Sheet (with Host/Operation)" is selected in the "Creation Target" field
If "Parameter sheet (with host/operation)" is selected in the "Creation Target" field of the "Parameter Sheet Definition/Creation" menu (or the "Parameter Sheet Definition List" menu) when creating a parameter sheet, a parameter sheet is created.
   Parameter sheet creation
Confirm that the parameter sheet has been added to the menu groups specified in the "For Input (Menu Group)" field, the "For Auto-Registration of Assigned Values (Menu Group)" field, and the "For Reference (Menu Group)" field.
   "For Input", "For Auto-Registration of Assigned Values", "For Reference" menu groups
A) For Input menu group (with host/operation)
-***************************************************
A parameter sheet is created that can be maintained (registered/updated/discontinued/restored) on a per host/operation basis.
   Parameter sheet created under the For Input menu group
 Item list ("Parameter sheet (with host/operation)" For Input menu)
-*Item**                          | **Description**                     | **Requi\   | **Input method** | **Constraints**    |
     | Registered from --> Device List     |           |              |                 |
Operation  | Operation name| Basic console\              | ○         | List selection   | -              |
     | Operation name registered from --> Operation List\    |           |              |                 |
     |    |           |              |                 |
Reference date/time        | Of the selected operation\    | -        | -           | Operation\ |
Scheduled execution date      | Of the selected operation\    | -        | -           | Operation\ |
Last execution date/time    | Of the selected operation\    | -        | -           | Operation\ |
Parameter      | [Created item\  | The item created in "Parameter Sheet Def\    | Depends on\ | Depends on\    | Depends on\       |
name]             | inition/Creation" is displayed\| the item setting\ | the item setting\  | the item setting\     |
B) For Auto-Registration of Assigned Values menu group (with host/operation)
-*************************************************************
This is a view-only menu. The content registered in the For Input menu group is displayed in the "List" submenu.
   Parameter sheet created under the For Auto-Registration of Assigned Values menu group
C) For Reference menu group (with host/operation)
-***************************************************
This is a view-only menu. The settings that are valid as of the date/time specified in the "Operation: Reference Date/Time" field of the "Display Filter" submenu are displayed in the "List" submenu.
   Parameter sheet created under the For Reference menu group
※The "Reference date/time" is the "Last Execution Date/Time" of the operation if it has a value, or the "Scheduled Execution Date/Time" if "Last Execution Date/Time" has no value.

#### 3. When "Parameter Sheet (with Operation)" is selected in the "Creation Target" field
If "Parameter sheet (with operation)" is selected in the "Creation Target" field of the "Parameter Sheet Definition/Creation" menu (or the "Parameter Sheet Definition List" menu) when creating a parameter sheet, a parameter sheet is created.
   Parameter sheet creation
Confirm that the parameter sheet has been added to the menu groups specified in the "For Input (Menu Group)" field, the "For Auto-Registration of Assigned Values (Menu Group)" field, and the "For Reference (Menu Group)" field.
   "For Input", "For Auto-Registration of Assigned Values", "For Reference" menu groups
A) For Input menu group (with operation)
-********************************************
A parameter sheet is created that can be maintained (registered/updated/discontinued/restored) on a per operation basis.
   Parameter sheet created under the For Input menu group
 Item list ("Parameter sheet (with operation)" For Input menu)
-*Item**                          | **Description**                     | **Requi\   | **Input method** | **Constraints**    |
Operation  | Operation name| Basic console\              | ○         | List selection   | -              |
     | Operation name registered from --> Operation List\    |           |              |                 |
     |    |           |              |                 |
Reference date/time        | Of the selected operation\    | -        | -           | Operation\ |
Scheduled execution date      | Of the selected operation\    | -        | -           | Operation\ |
Last execution date/time    | Of the selected operation\    | -        | -           | Operation\ |
Parameter      | [Created item\  | The item created in "Parameter Sheet Def\    | Depends on\ | Depends on\    | Depends on\       |
name]             | inition/Creation" is displayed\| the item setting\ | the item setting\  | the item setting\     |
B) For Auto-Registration of Assigned Values menu group (with operation)
-******************************************************
This is a view-only menu. The content registered in the For Input menu group is displayed in the "List" submenu.
   Parameter sheet created under the For Auto-Registration of Assigned Values menu group
C) For Reference menu group (with operation)
-********************************************
This is a view-only menu. The settings that are valid as of the date/time specified in the "Operation: Reference Date/Time" field of the "Display Filter" submenu are displayed in the "List" submenu.
   Parameter sheet created under the For Reference menu group
※The "Reference date/time" is the "Last Execution Date/Time" of the operation if it has a value, or the "Scheduled Execution Date/Time" if "Last Execution Date/Time" has no value.

#### 4. When "Parameter Sheet" is selected in the "Creation Target" field and the "Use Bundle" checkbox is checked
If "Parameter sheet (with host/operation)" or "Parameter sheet (with operation)" is selected in the "Creation Target" field of the "Parameter Sheet Definition/Creation" menu (or the "Parameter Sheet Definition List" menu) when creating a parameter sheet, and the "Use" checkbox in the "Use Bundle" field is checked, a bundle-display parameter sheet is created.
   Parameter sheet (bundle usage) creation
Confirm that the parameter sheet has been added to the menu groups specified in the "For Input (Menu Group)" field, the "For Auto-Registration of Assigned Values (Menu Group)" field, and the "For Reference (Menu Group)" field.
   "For Input", "For Auto-Registration of Assigned Values", "For Reference" menu groups
A) For Input menu group (bundle usage)
-**************************************
A parameter sheet is created that can be maintained (registered/updated/discontinued/restored).
For "Parameter sheet (with host/operation)", by entering the "Assignment Order" field for an already-registered combination of "Host Name" and "Operation", you can configure multiple parameters.
For "Parameter sheet (with operation)", by entering the "Assignment Order" field for an already-registered combination of "Operation", you can configure multiple parameters.
   Parameter sheet created under the For Input menu group
 Item list ("Parameter sheet (bundle usage)" For Input menu)
-*Item**                          | **Description**                     | **Requi\   | **Input method** | **Constraints**    |
Host name                          | Common to Ansible\                | ○         | List selection   | "Parameter\   |
     | Registered from --> Device List     |           |              | Sheet (Ope\   |
Operation  | Operation name| Basic console\              | ○         | List selection   | -              |
     | Operation name registered from --> Operation List\    |           |              |                 |
     |    |           |              |                 |
Reference date/time        | Of the selected operation\    | -        | -           | Operation\ |
Scheduled execution date      | Of the selected operation\    | -        | -           | Operation\ |
Last execution date/time    | Of the selected operation\    | -        | -           | Operation\ |
Parameter      | [Created item\  | The item created in "Parameter Sheet Def\    | Depends on\ | Depends on\    | Depends on\       |
name]             | inition/Creation" is displayed\| the item setting\ | the item setting\  | the item setting\     |
Example: What happens when attempting the above registration without using a bundle ①
You cannot configure multiple parameters for an already-registered combination of "Host Name" and "Operation".
   Parameter sheet created under the For Input menu group
If "11.11.11.11" and "test1.com" are already set for the combination of "host1" and "ope_sample1", attempting to set "22.22.22.22" and "test2.com" for the same combination results in a duplicate error.
Example: What happens when attempting the above registration without using a bundle ②
To configure multiple parameters for an already-registered combination of "Host Name" and "Operation" without using a bundle, you can do so by increasing the number of items, but this makes the parameter sheet wider and reduces visibility.
   "Parameter Sheet Definition/Creation" menu
You can configure as many parameters as the number of items created in the "Parameter Sheet Definition/Creation" menu (under the "Parameter Sheet Creation" menu group).
   Parameter sheet created under the For Input menu group
Also, since the item does not exist, you cannot register content corresponding to "IP Address_4" and "Domain_4" ("44.44.44.44" and "test4.com") for the same combination of "Host Name" and "Operation".
When creating a parameter sheet that repeats the same item, we recommend using a bundle. (Bundles cannot be used with data sheets.)
B) For Auto-Registration of Assigned Values menu group (bundle usage)
-************************************************
This is a view-only menu. The content registered in the For Input menu group is displayed in the "List" submenu.
   Parameter sheet created under the For Auto-Registration of Assigned Values menu group
C) For Reference menu group (bundle usage)
-**************************************
This is a view-only menu.
The settings that are valid as of the date/time specified in the "Operation: Reference Date/Time" field of the "Display Filter" submenu are displayed in the "List" submenu.
   Parameter sheet created under the For Reference menu group
※The "Reference date/time" is the "Last Execution Date/Time" of the operation if it has a value, or the "Scheduled Execution Date/Time" if "Last Execution Date/Time" has no value.

#### 5. When "Parameter Sheet" is selected in the "Creation Target" field and the "Use Host Group" checkbox is checked
If "Parameter sheet (with host/operation)" is selected in the "Creation Target" field of the "Parameter Sheet Definition/Creation" menu (or the "Parameter Sheet Definition List" menu) when creating a parameter sheet, and
the "Use" checkbox in the "Use Host Group" field is checked, a parameter sheet corresponding to host groups is created.
   Parameter sheet creation (host group usage)
Confirm that the parameter sheet has been added to the menu groups specified in the "For Input (Menu Group)" field, the "For Auto-Registration of Assigned Values (Menu Group)" field, and the "For Reference (Menu Group)" field.
   "For Input", "For Auto-Registration of Assigned Values", "For Reference" menu groups
A) For Input menu group (host group usage)
-********************************************
A parameter sheet is created that can be maintained (registered/updated/discontinued/restored) on a per host group and per host name basis.
   Parameter sheet (host group usage) created under the For Input menu group
 Item list ("Parameter sheet (bundle usage)" For Input menu)
-*Item**                          | **Description**                     | **Requi\   | **Input method** | **Constraints**    |
     | Registered from --> Device List     |           |              |                 |
     | Registered from --> Host Group Management\|           |              |                 |
Operation  | Operation name| Basic console\              | ○         | List selection   | -              |
     | Operation name registered from --> Operation List\    |           |              |                 |
     |    |           |              |                 |
Reference date/time        | Of the selected operation\    | -        | -           | Operation\ |
Scheduled execution date      | Of the selected operation\    | -        | -           | Operation\ |
Last execution date/time    | Of the selected operation\    | -        | -           | Operation\ |
Parameter      | [Created item\  | The item created in "Parameter Sheet Def\    | Depends on\ | Depends on\    | Depends on\       |
name]             | inition/Creation" is displayed\| the item setting\ | the item setting\  | the item setting\     |
For "Parameter sheet (with host/operation)", if "Use Host Group" is selected, you can select a host group for the host name.
B) For Auto-Registration of Assigned Values menu group (host group usage)
-******************************************************
This is a view-only menu. The content registered in the For Input menu group is displayed in the "List" submenu.
   Parameter sheet created under the For Auto-Registration of Assigned Values menu group
For "Parameter sheet (with host/operation)", if "Use Host Group" is selected, "" lets you check data split from host groups into individual hosts.
C) For Reference menu group (host group usage)
-********************************************
This is a view-only menu. The settings that are valid as of the date/time specified in the "Operation: Reference Date/Time" field of the "Display Filter" submenu are displayed in the "List" submenu.
   Parameter sheet created under the For Reference menu group
For "Parameter sheet (with host/operation)", if "Use Host Group" is selected, "" lets you check data split into individual hosts.
※The "Reference date/time" is the "Last Execution Date/Time" of the operation if it has a value, or the "Scheduled Execution Date/Time" if "Last Execution Date/Time" has no value.
# Menus of the "Parameter Sheet Creation" Menu Group That Are Hidden at Install Time

## Registering Column Groups in the "Column Group Management" Menu
The "Column Group Management" menu is hidden at install time. You can maintain (view/update/discontinue/restore) the column groups of the parameter sheet to be created.
   "Column Group Management" menu
A column group is a group that visually consolidates the heading portion of parameter sheet items.
With the parameter sheet creation function, you can create column groups for the items to be created.
   Parameter sheet created under the For Input menu group
 "Column Group Management" menu settings
-*Setting\    | **Description**                                                |
※Displayed in the "List/Update" submenu                    |
※Displayed in the "List/Update" submenu                    |
1. The data itself cannot be selected as its own parent column group.
1. If it is specified as the parent group of other data, it cannot be discontinued.
1. Parent-child relationships that would form a loop cannot be configured.

## Registering the Items to Configure in the "Parameter Sheet Item Creation Information" Menu
The "Parameter Sheet Item Creation Information" menu is hidden at install time.
You can maintain (view/update/discontinue/restore) the items managed by the parameter sheet or data sheet menu.
   "Parameter Sheet Item Creation Information" menu
 "Parameter Sheet Item Creation Information" menu settings
-*Setting\           | **Description**                                                  |
Parameter\     | The parameter sheet to which the item is associated\                         |
Item name (ja)      | Parameter sheet\                                         |
Item name (en)      | Parameter sheet\                                         |
Select an item of a menu created with the creation target "Parameter sheet (with operation)"\       |
so that when data is registered,\   |
the value of the data with a matching operation is referenced.        |
Displayed\             | Displayed in the menu\                                       |
**About items linked to auto-registration of assigned values**

## Registering Unique Constraints (Multiple Items) in the "Unique Constraint (Multiple Items) Creation Information" Menu
The "Unique Constraint (Multiple Items) Creation Information" menu is hidden at install time.
You can maintain (view/update/discontinue/restore) the unique constraint (multiple items) creation information of the parameter sheet to be created.
   "Unique Constraint (Multiple Items) Creation Information" menu
 "Unique Constraint (Multiple Items) Creation Information" menu settings
-*Setting item**   | **Description**                                            |
Parameter\    | The parameter sheet for which the unique constraint (multiple items) is configured\         |
Unique constraint\      | For the selected parameter sheet\                         |
When you want to configure a unique constraint (multiple items) for the parameter sheet selected in "Parameter Sheet Name".   |
(multiple items).                        |

## Registering the Roles to Configure in the "Parameter Sheet Role Creation Information" Menu
The "Parameter Sheet Role Creation Information" menu is hidden at install time.
You can maintain (view/update/discontinue/restore) the parameter sheet role creation information of the parameter sheet to be created.
   "Parameter Sheet Role Creation Information" menu
 "Parameter Sheet Role Creation Information" menu settings
-*Setting item**   | **Description**                                            |
Parameter\    | The parameter sheet for which the parameter sheet role creation information is configured\ |
Role         | For the selected parameter sheet\                         |
# Appendix

## Parameter Sheet Definition-Table Association Management
This is a menu that displays the association between the created parameter sheet and the DB table.
This is a hidden menu at install time.
This is a menu used by Backyard, and users do not operate it.
Even if the association is changed directly after the parameter sheet is created, this menu is not updated to follow the change.
   Parameter Sheet Definition-Table Association Management
 List of settings
-*Item name**         | **Description**                                        |
Parameter sheet name | The name of the parameter sheet associated with the DB.        |
Parameter sheet name\| The rest name of the parameter sheet associated with the DB.  |

## Other Menu Integration
Displays the default-configured menus, as well as the association between the created parameter sheet's menu group, menu, items, and DB table.
This is a hidden menu at install time.
This is a menu used by Backyard, and users do not operate it.
Even if the association is changed directly after the parameter sheet is created, this menu is not updated to follow the change.
   Other Menu Integration
 List of settings
-*Item name**         | **Description**                                        |
Menu group name | The name of the menu group associated with the DB.        |
Menu name         | The menu name of the created parameter\                                 |
sheet or data sheet.  |
Menu name (rest)   | The rest name of the created menu name.                |
Item name (ja)         | The item name (Japanese) of the created menu name.        |
Item name (en)         | The item name (English) of the created menu name.          |
Menu group\  | The created menu group name\                     |
name: menu name\     | : menu name: item name (Japanese).                |
Menu group\  | The created menu group name\                     |
name: menu name\     | : menu name: item name (English).                  |
Parameter sheet\  | If the target of parameter sheet creation,\               |

## Selection 1
This is a menu for managing items used for pulldown selection. (for single choice)
This is a hidden menu at install time.
-*Item name**         | **Description**                                        |

## Selection 2
This is a menu for managing items used for pulldown selection. (for two-choice)
This is a hidden menu at install time.
-*Item name**         | **Description**                                        |

## Targets Available for "Selection Items" of "Pulldown Selection"
-*Menu  | **Menu** | **Item**        | **Remarks**             |
Manage\       | Menu Management | Me\           |                      |
name + menu name |                      |
Movement list | Movement name      |                      |
File Management | Fi\           |                      |
le embedded variable name  |                      |
Template Management | te embedded variable name  |                      |
Conductor   | Conduct\     | Conductor name   |                      |
Parameter\ | Selection 1        | \*-(blank)   |                      |
Parameter\ | Selection 2        | True-False      |                      |
Parameter\ | Selection 2        | Yes-No          |                      |
In addition to the above, items whose column class is one of "String (single line)", "String (multiple lines)", "Integer", "Decimal", "Date and time", "Date", or "Link" in a menu (parameter sheet/data sheet) created by the function of the "Parameter Sheet Creation" menu group, and which is both "Required" and "Unique Constraint", are also targets.

## About "Reference Items" When Using "Pulldown Selection"
When using "Pulldown Selection" for an item, you can display other items in the same menu side by side, based on the value selected in "Pulldown Selection".
-*Selection item**              | **Me\    | **Item name** | **Item name (rest)** | **Remarks**       |
Admin Console: Me\       | Me\    | Menu\  | menu_name_rest   |                |
nu Management: Menu Name  | nu Management | name (rest)   |                  |                |
In addition to the above, when the "Selection Item" is a menu created by the function of the "Parameter Sheet Creation" menu group, other items of the parameter sheet selected in "Selection Item" whose column class is one of "String (single line)", "String (multiple lines)", "Integer", "Decimal", "Date and time", "Date", "Password", "File Upload", or "Link" are also targets.
When you create a parameter sheet with a "Reference Item" configured for "Pulldown Selection", for the parameter sheet created in the "For Input" menu group, only the "Pulldown Selection" item field is displayed from "Register", but in "List/Update", the record in the same row as the value set in "Pulldown Selection" is displayed side by side.
When "List" is displayed for the menus created in the "For Auto-Registration of Assigned Values" menu group and "For Reference" menu group, the value of the "Reference Item" is also displayed side by side.
The "Reference Item" displayed in the menu created in the "For Auto-Registration of Assigned Values" menu group can be used the same as a normal value in the "Auto-Registration Settings for Assigned Values" of each driver.

## Reference Item Information
Displays information about the reference items available for pulldown selection in "Parameter Sheet Definition/Creation".
This is a hidden menu at install time.
This is a menu used by Backyard, and users do not operate it.
   Reference item information available for pulldown selection in "Parameter Sheet Definition/Creation"
-*Item name**         | **Description**                                        |
Other Menu Integration ID | The ID of the target menu that is the reference source.            |
Menu group name | The name of the target menu group that is the reference source.      |
Menu name         | The name of the target menu that is the reference source.              |
Sensitive setting      | The reference source and\                                       |
Parameter sheet\  | If the target of parameter sheet creation,\               |

## Discontinuing (Logical Deletion) / Restoring a Created Parameter Sheet
This describes the procedure for discontinuing (logically deleting) / restoring a created parameter sheet.
   - Menu name (ja)
   - Menu name (en)
   - Menu name (rest)
For discontinuation/restoration, target the menu belonging to the menu group specified when the parameter sheet was created.
Parameter Sheet Creation --> Parameter Sheet Definition/Creation --> Target Menu Group
      From Admin Console --> Menu Management, select the target parameter sheet and execute discontinuation.
      From Admin Console --> Menu Management, select the target parameter sheet and execute discontinuation.
Note that a discontinued parameter sheet can no longer be used.
If it is used in a pulldown item or reference item of a parameter sheet, it will result in an ID conversion failure (X).
If it is used in the auto-registration of assigned values of each driver, it will result in an ID conversion failure (X).
Similarly, the same applies to items of other menus that reference the menu name or item name of the discontinued parameter sheet.
