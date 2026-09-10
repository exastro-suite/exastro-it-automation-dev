# Host Group Function
# Introduction
This document describes the functions and operation methods of the Host Group function in Exastro IT Automation.
# Host Group Overview and Benefits

## Host Group Overview
A Host Group refers to a group that gathers a set of hosts into a logical unit (function/role).
Hierarchy levels are counted such that a single Host Group represents 1 level, and one parent-child pair represents 2 levels; up to 15 levels can be defined from the topmost Host Group down to the bottommost Host Group.

## Benefits of Host Groups

### Inheritance of Parameters Between Host Groups
Parameters set on a parent Host Group are inherited by its child Host Groups.
By localizing where settings are configured in this way, the work of assigning/changing settings can be simplified.
When a child Host Group is added, parameter settings are also inherited automatically.
As a result, zabbix12 inherits the settings of zabbix1, in the same way as zabbix11.
A child Host Group can be linked to multiple parent Host Groups; this section explains parameter inheritance when there are multiple parent Host Groups.
If a parameter is duplicated between Host Groups, the value from the lowest-level Host Group is applied.
If a parameter is duplicated at the same level, it is inherited from the parent Host Group with the higher priority.
The method for setting priority is described in "".
# Main Functions of the Host Group Function
This is a function for managing Host Group settings and for splitting records in a Parameter Sheet that are organized by Host Group into records organized by host.
■ The following operations trigger the split process for all Parameter Sheets.
- Registering/updating/discontinuing/reactivating records in each of the Host Group-related menus.
- Host Group List
- Host Group Parent-Child Association
- Host Association Management
■ The following operations trigger the split process only for the relevant Parameter Sheet.
- Registering/updating/discontinuing/reactivating a Parameter Sheet (using Host Group).
- Creating, editing, or initializing a Parameter Sheet with Host Group Usage selected, in Parameter Sheet Definition/Creation.
# Menu Groups of the Host Group Function
The menu groups of the Host Group function and the menus that belong to them are as follows.
.. list-table:: Host Group Function
- | No.
     - | Menu Group
     - | Description
- | 1
     - | Host Group Management
     - | Host Group List
     - | Registers Host Groups.
- | 2
     - | Host Group Management
     - | Host Group Parent-Child Association
     - | Associates Host Group parent-child relationships.
- | 3
     - | Host Group Management
     - | Host Association Management
     - | Associates Host Groups, operations, and target hosts.
- | 4
     - | Host Group Management
     - | Host Group Split Target
     - | Manages the Parameter Sheet information targeted for splitting from Host Group units into host units, and the status of the split process.

## About the "Host Group Management" Menu Group
Host Group List, Host Group Parent-Child Association, and Host Association Management are the menus required to register Host Groups and to define which hosts are the target hosts for which operations.
# Record Splitting from Host Group to Host Unit, and Each Task
The flow of registering a Host Group using each menu and setting host-unit information for work execution is shown in the table below.
.. list-table:: Task Content and Target Menus for Each Task
   :name: Task Content and Target Menus for Each Task
- No.
     - Task Content
     - User Operation
     - Menu Group Used
     - Menu Used
     - Remarks
- 1
     - 
     - Yes
     - Parameter Sheet Creation
     - | Parameter Sheet Definition/Creation
     - -
- 2
     - 
     - Yes
     - Host Group Management
     - Host Group List
     - -
- 3
     - 
     - Yes
     - Host Group Management
     - Host Group Parent-Child Association
     - -
- 4
     - 
     - Yes
     - Host Group Management
     - Host Association Management
     - -
- 5
     - 
     - Yes
     - *2
     - Menu created in ""
     - -
- 6
     - 
     - | No
     - *2
     - Menu created in ""
     - Manual registration/update is not possible.
- 7
     - 
     - Yes
     - *2
     - Auto-Substitution Value Registration Settings
     - | For Auto-Substitution Value Registration Settings, refer to the following.
- 8
     - 
     - | No
     - *3
     - Target Hosts
     - | For Target Hosts, refer to the following.
- 9
     - 
     - | No
     - *3
     - Substitution Value Management
     - | For Substitution Value Management, refer to the following.
*2 This is the menu group specified as the creation destination in Parameter Sheet Definition/Creation.
*3 This is the menu group where Auto-Substitution Value Registration Settings can be configured. For an image of the records for each task, refer to the following.

## Image of Task Content and Records
This is an image of the records for each menu, for the task content of each No. above.
1. 
- | Target Host
        - Operation
        - Item 1
        - Item 2
- \_
        -
        -
        -
- \_
        -
        -
        -
1. 
- Host Group
- HG_1
- HG_2
- hg_1a
- hg_1b
- hg_2a
- hg_2b
1. 
- Parent Host Group
        - Child Host Group
- HG_1
        - hg_1a
- HG_1
        - hg_1b
- HG_2
        - hg_2a
- HG_2
        - hg_2b
1. 
- Host Group
        - Operation
        - Target Host
- hg_1a
        - OP1
        - host_1a
- hg_1b
        - OP1
        - host_1b
- hg_2a
        - OP1
        - host_2a
- hg_2b
        - OP1
        - host_2b
1. 
- | Target Host
        - Operation
        - Item 1
        - Item 2
- HG_1
        - 2023/01/01 00:00_OP1
        - 111
        - AAA
- HG_2
        - 2023/01/01 00:00_OP1
        - -
        - BBB
1. 
- Target Host
        - Operation
        - Scheduled Execution
        - Item 1
        - Item 2
- host_1a
        - OP1
        - 2023/01/01 00:00:00
        - 111
        - AAA
- host_1b
        - OP1
        - 2023/01/01 00:00:00
        - 111
        - AAA
- host_2a
        - OP1
        - 2023/01/01 00:00:00
        - -
        - BBB
- host_2b
        - OP1
        - 2023/01/01 00:00:00
        - -
        - BBB
1. 
- Menu Group:Menu Name:Item Name
        - Movement
        - Variable Name
- Auto-Substitution Value Registration:HG Parameter Management:Item 1
        - Movement1
        - VAR_Variable_1
- Auto-Substitution Value Registration:HG Parameter Management:Item 2
        - Movement2
        - VAR_Variable_2
1. 
- Operation
        - Movement
        - Target Host
- OP1
        - Movement1
        - host_1a
- OP1
        - Movement1
        - host_1b
- OP1
        - Movement2
        - host_1a
- OP1
        - Movement2
        - host_1b
- OP1
        - Movement2
        - host_2a
- OP1
        - Movement2
        - host_2b
1. 
- Operation
        - Movement
        - Target Host
        - Variable Name
        - Concrete Value
- 2023/01/01 00:00_OP1
        - Movement1
        - host_1a
        - VAR_Variable 1
        - 111
- 2023/01/01 00:00_OP1
        - Movement1
        - host_1b
        - VAR_Variable 1
        - 111
- 2023/01/01 00:00_OP1
        - Movement2
        - host_1a
        - VAR_Variable 2
        - AAA
- 2023/01/01 00:00_OP1
        - Movement2
        - host_1b
        - VAR_Variable 2
        - AAA
- 2023/01/01 00:00_OP1
        - Movement2
        - host_2a
        - VAR_Variable 2
        - BBB
- 2023/01/01 00:00_OP1
        - Movement2
        - host_2b
        - VAR_Variable 2
        - BBB

## Details of the Task Content

### Parameter Sheet Creation
Use the Parameter Sheet Creation function to create a Parameter Sheet menu.
For details on the Parameter Sheet Creation function, refer to "".

### Registering Host Groups
Register Host Groups using the Host Group List menu.
.. list-table:: Host Group List Registration
- | Item
     - | Description
     - | Required
     - | Input Format
     - | Constraints
- | Host Group Name
     - | Enter the name of the Host Group.
     - | ○
     - | Manual input
     - | Max length is 255 bytes.
- | Priority
     - | Enter the priority.
     - |
     - | Manual input
     - | Input range is 0 to 2,147,483,647.

### Defining Host Group Parent-Child Relationships
Define Host Group parent-child relationships using the Host Group Parent-Child Association menu.
.. list-table:: Host Group Parent-Child Association Registration
- | Item
     - | Description
     - | Required
     - | Input Format
     - | Constraints
- | Parent Host Group
     - | Select the name of the parent Host Group.
     - | ○
     - | List selection
     - |
- | Child Host Group
     - | Select the name of the child Host Group associated with the Host Group.
     - | ○
     - | List selection
     - |
If there is a Host Group whose parent-child relationship forms a loop, an error is displayed at the time of registration or update.
In the example below, the parent-child relationships "HG1 (parent) and HG2 (child)" and "HG2 (parent) and HG3 (child)" have already been defined, but the reverse parent-child relationship "HG3 (parent) and HG1 (child)" is additionally defined, causing the parent-child relationship to form a loop.

### Associating Host Groups, Operations, and Target Hosts
Register the target hosts associated with a Host Group and an operation using the Host Association Management menu.
.. list-table:: Host Association Management
- | Item
     - | Description
     - | Required
     - | Input Format
     - | Constraints
- | Host Group Name
     - | Select the Host Group.
     - | ○
     - | List selection
     - |
- | Operation
     - | Select the operation.
     - |
     - | List selection
     - | *1
- | Host Name
     - | Select the target host.
     - | ○
     - | List selection
     - |
*1 In Host Association Management, Operation can also be registered blank. If registered blank, the association is valid for all operations.
- | Example 1
- | Example 2
- | Example 3
- | Example of Operation Settings in Host Association Management
In the example above, for Host Groups zabbix1 and zabbix2, which were registered with a blank Operation, the association is valid for all operations.
On the other hand, for Host Group zabbix3, which was registered with an Operation, the association is valid only for the registered operation "OP10".
- | Host Group association for operation "OP10"
- | Host Group association for operations other than "OP10"

### Registering to the Parameter Sheet
In the Parameter Sheet menu for Host Groups created in "", register the concrete value for each operation for items that belong to the target host or Host Group.
After registration, reference/update/discontinue/reactivate are available.
.. list-table:: Parameter Sheet (Using Host Group)
- | Item
     - | Description
     - | Required
     - | Input Format
     - | Constraints
- | Host Name
     - | Select the target host or Host Group.
     - | ○
     - | List selection
     - |
- | Operation Name
     - | Select the operation.
     - | ○
     - | List selection
     - |
- | Reference Date/Time
     - | The reference date/time is displayed.
     - | -
     - | -
     - | The reference date/time of the selected operation is displayed.
- | Scheduled Execution Date
     - | The scheduled execution date is displayed.
     - | -
     - | -
     - | The scheduled execution date of the selected operation is displayed.
- | Last Execution Date/Time
     - | The last execution date/time is displayed.
     - | -
     - | -
     - | The last execution date/time of the selected operation is displayed.
- | Target Items of the Parameter Sheet
     - | Enter the concrete value of the item. In "", this is reflected as the concrete value of the variable associated with the operation, Movement, and
the target host.
     - | *
     - | *
     - | * This is the item name and item setting defined in Parameter Sheet Creation.
The combination of "Host Name" and "Operation" is registered uniquely.
Even for the same host, registration is possible if combined with a different operation.

### Conversion to Host Units
The information registered in "" is aggregated per operation by the internal process "Host Group Decomposition function", and is further inherited down to the target host unit according to the Host Group associations.
The information inherited down to the target host unit can be referenced in the host-specific Parameter Sheet menu created in "".
This is a menu that belongs to the menu group for Auto-Substitution Value Registration use. Only reference is possible; registration/update/discontinue/reactivate are not possible.
1. Assume the following items are registered in the Parameter Sheet menu.
(Information registered in "")
   .. list-table:: Information registered in ""
- Target Host or Host Group
        - Operation
        - Item 1
        - Item 2
- HG_1
        - 2023/01/01_00:00_OP1
        - 111
        - AAA
- HG_2
        - 2023/01/01_00:00_OP1
        - -
        - BBB
- host_1a
        - 2023/01/01_00:00_OP1
        - 222
        - -
1. Assume the Host Group parent-child relationships are as follows.
(Information registered in "")
- Parent Host Group
        - Child Host Group
- HG_1
        - hg_1a
- HG_1
        - hg_1b
- HG_2
        - hg_2a
- HG_2
        - hg_2b
1. Assume the association information for Host Group, Operation, and Target Host is as follows.
(Information registered in "")
- Host Group
        - Operation
        - Target Host
- hg_1a
        - 2023/01/01_00:00_OP1
        - host_1a
- hg_1b
        - 2023/01/01_00:00_OP1
        - host_1b
- hg_2a
        - 2023/01/01_00:00_OP1
        - host_2a
- hg_2b
        - 2023/01/01_00:00_OP1
        - host_2b
1. When conversion to host units is performed while the information in (1) through (3) is registered, the records become as shown below, and you can see that the information has been set per target host belonging to the Host Group.
When an item is registered for both a Host Group and a target host, the item registered for the target host takes priority. Accordingly, the value "222" registered for host_1a is applied.

### Associating Setting Values of Items per Operation and Target Host

### Reflection of Target Hosts Associated with an Operation
The target hosts associated with an operation are reflected automatically.

### Reflection of Substitution Values
For each operation, the concrete values to be substituted into variables within the Playbook or template file used by the target Movement are reflected automatically.
