# Common Operations
# Introduction
This document describes the operation methods for the common parts of the ITA menus.
# Overview
# Screen Description

## Screen Layout
- No.
     - Description
- 1
     - Menu name
     - | The name of the menu currently being displayed is shown.
- 2
     - Menu
     - | The menu groups available for operation/display are shown as a list.
Also, the menus available for operation/display within the current menu group are shown as a list.
- 3
     - Submenu
     - | This is the part used for registration, configuration, etc. corresponding to each menu.
- 4
     - Workspace information
     - | The current workspace and the list of workspaces you have access to are displayed.
- 5
     - Login information
     - | The name of the currently logged-in account is displayed.
# Common Operations for Each Menu
This section describes the operation methods for the parts common to each menu.
For information specific to each menu, refer to the manual for the relevant function.

## List tab
You can check registered items and perform registration/update/discontinuation/restoration.
- | **Register**
Registers a new item for each menu.
The registration content differs depending on the menu, so refer to the usage manual for each menu.
For bulk registration using Excel format or JSON format files, see "  ".
              - | \ :guilabel:`Add`\
A record for new registration is added.
Use this when you want to register multiple items at the same time.
              - | \ :guilabel:`Duplicate`\
For the procedure, see "  ".
              - | \ :guilabel:`Delete`\
For input items that allow selection via a pull-down menu during registration/update, the specifications are as follows.
1. A search box is displayed.
1. The selectable items are displayed.
For input items that allow file upload during registration/update, the specifications are as follows.
1. :guilabel:`+`: You can select a file and upload it.
1. :guilabel:``: You can create and edit a text file.
1. :guilabel:``: You can delete the file.
1. From "Management Console - ", you can set file upload prohibited extensions in the setting value of identification ID "FORBIDDEN_UPLOAD".
- | **Display filter**
Specifies the search criteria for displaying items registered in each menu.
The search criteria and search items differ for each menu. This section describes the common functions.
1. Discontinued column
Other options, "All records" and "Discontinued only," can also be selected as needed to specify the desired display method.
-*Selecting one of these is required**\ .
1. Search criteria
1. Auto filter
1. Column description (Description)
1. Filter
1. Excel download
1. JSON download / JSON download (without file)
1. File name: Select the file name link to download the file.
1. :guilabel:``: You can preview the text file.
- | **Edit**
Updates registered items.
The editing content differs depending on the menu, so refer to the usage manual for each menu.
              - | \ :guilabel:`Add`\
A record for new registration is added.
Use this when you want to register multiple items at the same time.
              - | \ :guilabel:`Duplicate`\
For the procedure, see "  ".
              - | \ :guilabel:`Delete`\
              - | \ :guilabel:`Discontinue`\
- | **Duplicate**
You can register a new item by reusing the information of a registered item.
1. A new registration record is displayed, reflecting the values of the target item.
- | **Table settings**
You can change the table settings.
Changed settings are stored on the server, so the table settings remain applied even when accessing from a different terminal, browser, or environment.
  - | Common settings: Applied to the common parts of the submenus of all menus.
  - | Individual settings: Applied only to the menu in which they are set. If common settings are selected for each item, the settings selected in the common settings are applied.
   Table settings_Individual settings
   Table settings_Common settings
.. list-table:: Table settings: Individual settings
- | Item
     - | Description
     - | Setting value
     - | Remarks
- | Item display direction
     - | Sets the display direction of items.
     - | Select from the following.
- Common settings
     - |
- | Filter display position
     - | Sets the display position of the filter.
     - | Select from the following.
- Common settings
     - |
- | Item menu display
     - | Sets how the item menu is displayed.
     - | Select from the following.
- Common settings
     - |
- | Item display/hide, left-fixed/right-fixed
     - | Sets display/hide for each item.
Sets items to be fixed to the left or right when scrolling horizontally.
     - | Select the target item.
     - |
.. list-table:: Table settings: Common settings
- | Item
     - | Description
     - | Setting value
     - | Remarks
- | Item display direction
     - | Sets the display direction of items.
     - | Select from the following.
     - |
- | Filter display position
     - | Sets the display position of the filter.
     - | Select from the following.
     - |
- | Item menu display
     - | Sets how the item menu is displayed.
     - | Select from the following.
     - |
**Display behavior based on each item's settings**
              Menu group (Item display direction: Vertical)
              Menu group (Item display direction: Horizontal)
              Menu group (Filter display position: Inside)
              Menu group (Filter display position: Outside)
Item menu display: When left unselected (default), the item menu is displayed by selecting :guilabel:`` for each record.
              Menu group (Item menu display: Hidden)
              Menu group (Item menu display: Shown)

## Change history tab
For each menu, you can display the change history of registered items.
- | **Checking change history**
1. By specifying the primary key of each menu, you can display the change history of the corresponding item.
1. The list is displayed in order of most recent change date and time, with the changed parts from the previous version shown in orange bold text.
- | **About change history when a pull-down selection is included**
The "Change history" displays the value at the time the value was edited (registered/updated/discontinued/restored).
Example: When item "paramB" of parameter sheet "param001" references item "master" of "master001"
1. As advance preparation, create the following data sheet and parameter sheet in the Parameter Sheet Creation menu group > Parameter Sheet Definition/Creation menu.
     - | Data sheet "master001"
          A data sheet created in the "Parameter Sheet Definition/Creation" menu
     - | Parameter sheet "param001"
          A parameter sheet created in the "Parameter Sheet Definition/Creation" menu
1. From the Input menu group > master001 menu, register the value "mas1-1" for parameter "master".
1. From the Input menu group > param001 menu, register one item.
1. From the Input menu group > master001 menu, edit the value of parameter "master" and update it to "mas1-2".
1. From the Input menu group > master001 menu, edit the value of parameter "master" and update it to "mas1-3".
1. From the Input menu group > param001 menu, edit and update the previously registered "paramA" item.
1. From the Input menu group > master001 menu, edit the value of parameter "master" and update it to "mas1-4".
1. From the Input menu group > master001 menu, edit the value of parameter "master" and update it to "mas1-5".
1. From the Input menu group > param001 menu, edit and update the previously registered "paramA" item.
1. The result will be as follows.
     Change history of parameter sheet "param001"

## Download all / Bulk file registration
You can also use a file in the same format to register information in bulk.
1. Download the file that suits your purpose.
1. Edit and save the downloaded file.
The editing content differs depending on the menu, so refer to the usage manual for each menu.
Files downloaded from \ :guilabel:`Download all change history (Excel)`\ cannot be used for bulk registration.
If "Execution process type" is not selected or an incorrect process type is selected, registration will not be executed.
1. Download the file that suits your purpose.
1. Edit and save the downloaded file.
The editing content differs depending on the menu, so refer to the usage manual for each menu.
