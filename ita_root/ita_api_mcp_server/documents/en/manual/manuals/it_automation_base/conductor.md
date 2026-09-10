# Conductor
# Introduction
This document describes the functions and operation methods of Conductor in Exastro IT Automation.
# Overview of Conductor
This chapter describes the functions and operation methods of Conductor.
Conductor provides the following functions, which are commonly required when performing work using Exastro IT Automation.
# Conductor Menus and Screen Layout

## List of Conductor Menus
The menus in the Conductor menu group are shown below.
 List of Exastro IT Automation Conductor Menus
-*No** | **Menu group** | **Menu**                    | **Description**                                                                                 |
1      | Conductor            | Conductor interface information   | You can maintain (view/update) the Conductor interface information.                       |
| This menu must always contain exactly 1 record.                                          |
2      |                      | Conductor notification destination definition             | You can maintain (view/register/update) the definitions related to notifications executed when working with Conductor.   |
3      |                      | Conductor list                   | You can maintain (view/discontinue) Conductors.                                             |
4      |                      | Conductor edit/work execution           | You can edit/execute work on Conductors.                                                       |
5      |                      | Conductor work history               | You can view the Conductor list (execution history).                                                  |
6      |                      | Conductor work check               | You can check the execution results of Conductor work.                                                  |
7      |                      | Conductor scheduled work execution | You can maintain (view/register/update) Conductor work that is executed periodically according to a schedule.|
# ITA Conductor Usage Procedure

## Work Flow
The standard work flow for ITA Conductor is as follows.
1. Register/check device information (Ansible common)
1. Register/check operations (Basic Console)
1. Register Movements from each ITA Driver
1. Check Movements (Basic Console)
1. Register the Conductor interface information
1. Register a Conductor
1. Check the Conductor
1. Execute the Conductor
1. Check the Conductor execution results
1. Check the Conductor execution history
- | For how to register "device information", refer to "Ansible common  ".
- | For how to register "operations", refer to "Basic Console -  ".
- | For how to register Movements, refer to the usage manual for each Driver.
- | A directory path shared between each Movement during Conductor execution is available.
When information needs to be passed between Movements, the shared directory path can be used to pass information.
  .. | For details on "Ansible driver", refer to the separate "Ansible-driver Usage Manual".
  .. | For details on "Terraform driver", refer to the separate "Terraform-driver Usage Manual".
- | Work flows executed via "Conductor call" each have their own individual shared directory path.
# Function and Operation Description

## Conductor Interface Information
1. In the "Conductor interface information" menu, you set the path of the directory shared by each Movement executed from Conductor, and the refresh interval for the "Conductor work check" menu.
      Conductor interface information
2. Details of the "Conductor interface information" menu --> "List" submenu are as follows.
    "List" submenu
Conductor interface ID | Automatically numbered by the system, so it cannot be edited.                                                                             |          | Automatic input  |                   |
State monitoring interval (in milliseconds)  |  Enter the interval at which the "Conductor work execution" display is refreshed. Normally, approximately 1000 milliseconds\                                        |  ○       | Manual input  | Minimum value 1000 milliseconds  |

## Conductor Notification Destination Definition
1. In the "Conductor notification destination definition" menu, you can configure definitions related to notifications executed when working with Conductor.
      Conductor notification destination definition
2. Details of the "Conductor notification destination definition" menu --> "List" submenu are as follows.
   .. list-table:: "List" submenu
- Item
        - Description
        - Required
        - Input format
- Conductor notification ID
        - Automatically numbered by the system, so it cannot be edited.
        -
        - Automatic input
- Notification name
        - Enter the notification name.
        - ○
        - Manual input
- Notification destination URL
        - Enter the URL of the notification destination.
        - ○
        - Manual input
- Header
        - Enter the HTTP header fields in JSON format.
        - ○
        - Manual input
- Message
        - Enter the message content according to the specifications of the notification destination service.
        - ○
        - Manual input
- PROXY URL
        - If a PROXY setting is required, enter the URL.
        - ○
        - Manual input
- PROXY PORT
        - If a PROXY setting is required, enter the PORT.
        - ○
        - Manual input
- Work check URL
        - Enter the FQDN to be used for the reserved variable of the work check URL.
        - ○
        - Manual input
- Suppression start date/time
        - Enter this if you want to suppress notifications.
        - ○
        - Manual input
- Suppression end date/time
        - Enter this if you want to suppress notifications.
        - ○
        - Manual input
- Remarks
        - A free-text field.
        - -
        - Manual input
   ※For the ITA-specific variables that can be used in the message, refer to the table below.
   .. list-table:: Conductor Notification Destination Definition ITA-specific Variables
- ITA-specific variable
        - Variable content
- __CONDUCTOR_INSTANCE_ID__
        - Conductor instance ID
- __CONDUCTOR_NAME__
        - Conductor instance name
- __STATUS_ID__
        - Status ID
- __OPERATION_ID__
        - Operation ID
- __OPERATION_NAME__
        - Operation name at execution time
- __EXECUTION_USER__
        - Work execution user
- __PARENT_CONDUCTOR_INSTANCE_ID__
        - Parent Conductor instance ID
- __PARENT_CONDUCTOR_NAME__
        - Parent Conductor name
- __TOP_CONDUCTOR_INSTANCE_ID__
        - Top-level Conductor instance ID
- __TOP_CONDUCTOR_NAME__
        - Top-level Conductor name
- __ABORT_EXECUTE_FLAG__
        - Emergency stop flag
- __REGISTER_TIME__
        - Registration date/time
- __TIME_BOOK__
        - Scheduled date/time
- __TIME_START__
        - Start date/time
- __TIME_END__
        - End date/time
- __NOTICE_NAME__
        - Notification log
- __NOTE__
        - Remarks
- __JUMP_URL__
- Status ID
        - Status name
- 3
        - In progress
- 4
        - In progress (delayed)
- 5
        - Paused
- 6
        - Completed successfully
- 7
        - Completed with error
- 8
        - Completed with warning
- 9
        - Emergency stopped
- 10
        - Schedule cancelled
- 11
        - Unexpected error

## Conductor List
1. In the "Conductor list" menu, you can view/discontinue registered Conductors.
   "Conductor list" menu

## Conductor Edit/Work Execution
-*Mode** | **Description**                                                                                                |
Edit\      | - | A mode in which you can create a new Conductor                                                                     |
- | The default mode of the "Conductor edit/work execution" menu                                              |
View\      | - | A mode in which you can only view a Conductor                                                                     |
Update\      | - | A mode in which you can edit an existing Conductor                                                                   |

#### About "Edit" Mode
- | Register the Conductor name and the parts that make up the work flow (hereafter, "Node").

### Node List
- | Consists of the following tabs.
- | Movement tab
- | A list of registered Movement names
- | Function tab
- | Conductor end
- | Conductor pause
- | Conductor call
- | Conditional branch
- | Parallel branch
- | Parallel merge
- | Status File branch
- | The behavior of each Node is as follows.
-*Image**       | **Name**                     | **Behavior Description**                      |
image1|       | Conductor start              | Starts the Conductor             |
image2|       | Conductor end                | Ends the Conductor.             |
※When there are multiple Conductor \                |
end nodes, all Conductor \  |
image3|       | Conductor pause              | Pauses the work flow.      |
image4|       | Conductor call               | Calls another registered Cond\               |
If the called Conductor ends with a warning\|
the "Movement", "Conducto\                 |
arranged in sequence, the "Movement", "Conducto\ |
the work result directory of the "Movement"\ |
image10|      | Various Movements                 | Executes the Movement.            |
- | The constraints on Nodes are as follows.
- | To register/update, the IN/OUT of all Nodes must be connected.
- | To use Parallel merge, Parallel branch must also be in use.
- | A flow branched by Conditional branch cannot be merged with Parallel merge.
- | For Parallel branch, Conditional branch, Parallel merge, and Conductor pause, you cannot connect the same type of Node consecutively.
- | You cannot specify a Conductor that is currently being updated as the target of a Conductor call and update it.
- | Each Node can be added by dragging and dropping it from the Node list.
- | The description in the "Remarks" field has no effect on process execution. It is a memo field that can only be viewed on the web.

### Detailed Information for Each Node
- | The name of the tab changes depending on the selected Node.
1. When no Node is selected (Conductor tab)
- | Displayed when no Node is selected.
- | The items in the tab are as follows.
        Conductor notification settings popup
     .. list-table:: "Conductor" tab
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- ID
          - A unique ID corresponding to the Conductor is entered automatically.
          - \-
          - Automatic input
          - \-
- Name
          - Enter an arbitrary Conductor name.
          - ○
          - Manual input
          - \-
- Update date/time
          - The date/time the selected Conductor was updated is entered automatically.
          - \-
          - Automatic input
          - \-
- Notification
          - | Select the notification to execute.
The notifications you can select are those registered in "  ".
          - \-
          - Checkbox
          - \-
- Movement common display settings
          - Select settings related to the display of Movement nodes (node width and Movement name display format).
          - \-
          - List selection
          - \-
- Remarks
          - Enter a description or comment for the Conductor.
          - \-
          - Manual input
          - \-
1. When a Movement is selected
- |  Displayed when a Node in the "Movement" tab of " " is selected.
- | The tab name displays the orchestrator name of the selected Movement (example: Ansible Legacy Role).
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- Movement ID
          - The ID of the selected Movement is displayed.
          - \-
          - Automatic input
          - \-
- Name
          - The name of the selected Movement is displayed.
          - \-
          - Automatic input
          - \-
- Skip
          - Check this to skip the target work. This is a parameter that can be changed in the "Conductor work execution" menu.
          - \-
          - Manual input
          - \-
- Individual operation
The selected operation name is displayed.
          - \-
          - Selection
          - \-
- Remarks
          - You can enter a description or comment for the Node.
          - \-
          - Manual input
          - \-
  #. "Remarks" field when each Node is selected
- | Displayed when each Node in the "Movement" tab and "Function" tab of " " is selected.
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- Remarks
          - You can enter a description or comment for the Node.
          - \-
          - Manual input
          - \-
  #. When Conductor call is selected
- | Displayed when "Conductor call" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
     .. list-table:: "Conductor call" tab
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- Skip
          - | Check this to skip the target work.
          - \-
          - \-
- Called Conductor
The name of the specified Conductor is displayed.
          - \-
          - Selection
          - \-
- Individual operation
The name of the specified operation is displayed.
          - \-
          - Selection
          - \-
  #. When Conditional branch is selected
- | Displayed when "Conditional branch" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
-*Item**| **Description**                                     | **Required**  | **Input format**  | **Constraints**  |
Condition\| Sets the number of branches.　                       |  \-           |  Selection         |  \-           |
case | Movement, Conductor                          |  \-           |  Selection         |  \-           |
Sets conditional branching based on the result.             |               |               |               |
You can change the settings by drag and drop.             |               |               |               |
  #. When Parallel branch is selected
- | Displayed when "Parallel branch" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- Parallel branch settings
The default number of branches is 2. A value of 2 or less cannot be set.
          - \-
          - Selection
          - \-
  #. When Parallel Merge is selected
- | Displayed when "Parallel merge" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- case
The default number of branches is 2. A value of 2 or less cannot be set.
          - \-
          - Selection
          - \-
  #. When Conductor end is selected
- | Displayed when "Conductor end" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- End status
          - | When processing reaches End, the selected status is reflected in the Conductor's status.
- Normal (default value)
- Warning
- Error
          - \-
          - Selection
          - \-
  #. When Status file branch is selected (Status file branch tab)
- | Displayed when "Status file branch" in the "Function" tab of " " is selected.
- | The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- Status file branch settings
          - | Sets conditional branching based on the Movement's status file.
          - \-
          - Selection
          - \-
- Remarks
          - You can enter a description or comment for the Node.
          - \-
          - Manual input
          - \-
- | The status file referenced is the "MOVEMENT_STATUS_FILE" under the work result directory of each Movement.
- | If the status file does not exist, the "else" side processing is performed.
- | If the content of the status file spans multiple lines (including line break codes), the value after the line break code is excluded from evaluation.
      .. list-table:: Status File ITA-specific Variables
- **ITA-specific variable**
           - **Variable content**
           - **Constraints**
- __movement_status_filepath__
           - The path of "MOVEMENT_STATUS_FILE" under the work result directory
           - ※
  #. "Node" tab
-  Displayed when multiple Nodes in the "Movement" tab and "Function" tab of " " are selected.
- Allows you to align items within the grid.
- The items in the tab are as follows.
- **Item**
          - **Description**
          - **Required**
          - **Input format**
          - **Constraints**
- |image11|
          - Aligns the multiple selected Nodes to the left.
          - \-
          - Selection
          - \-
- |image12|
          - Aligns the multiple selected Nodes to the horizontal center.
          - \-
          - Selection
          - \-
- |image13|
          - Aligns the multiple selected Nodes to the right.
          - \-
          - Selection
          - \-
- |image14|
          - Aligns the multiple selected Nodes to the top.
          - \-
          - Selection
          - \-
- |image15|
          - Aligns the multiple selected Nodes to the vertical center.
          - \-
          - Selection
          - \-
- |image16|
          - Aligns the multiple selected Nodes to the bottom.
          - \-
          - Selection
          - \-
- |image17|
          - Distributes the multiple selected Nodes evenly in the horizontal direction.
          - \-
          - Selection
          - \-
- |image18|
          - Distributes the multiple selected Nodes evenly in the vertical direction.
          - \-
          - Selection
          - \-
- | The operations available in the "Conductor edit/work execution" menu are as follows.
 List of "Conductor edit/work execution" menu execution operations
-*Item**    | **Description**                          | **New** | **Update**          | **Rema |
JSON save    | Saves the configuration information of the currently displayed Conductor\  | 〇       |         |         |      |
JSON read\     | Reads the configuration information (JSON format) of a Conductor\  |   〇     |         |         |      |
Register        | Executes registration.                | 〇       |         | 〇      |      |
Change and edit the Conductor. |          |         |         |      |
Reuse\         | An existing registered Conducto\                 |          | 〇      |  〇     |      |

#### About "View" Mode
   "Conductor edit/work execution" menu ("View" mode)
- **Item**
     - **Description**
- :guilabel:`Select`
     - You can select and view a registered Conductor.
- :guilabel:`Edit`
     - You can edit a registered Conductor.
- :guilabel:`Execute work`
     - Executes work for the selected Conductor.
- :guilabel:`Reuse as new`
     - You can copy a registered Conductor to create a new one.
- :guilabel:`New`
     - You can create a new Conductor.

#### About "Update" Mode
   "Conductor edit/work execution" menu ("Update" mode)
- **Item**
     - **Description**
- :guilabel:`Update`
     - The edited content is saved.
- :guilabel:`Reload`
     - Discards the edited content and reverts to the registered state.
- :guilabel:`Cancel`
- :guilabel:`Full screen`
     - | The browser display becomes full screen.
- :guilabel:`Fit to screen`
     - Displays at a scale where all Nodes are visible.

#### About Conductor Work Execution
- | For Movement and Conductor Call operations, only the skip setting and setting values can be changed.
※Changes are not reflected in the data registered by Conductor editing. They are reflected only in work execution.
- Regarding the access permissions set for an executed Conductor, at the time of execution it inherits the roles common to the access permissions set for the selected Conductor and operation. If there is no common role, work execution is not possible.
- The common items of "Work execution settings" are as follows.
.. list-table:: List of common items for "Work execution settings"
- **Item**
     - **Description**
     - **Required**
     - **Input format**
     - **Constraints**
- Work execution Conductor
     - The selected Conductor is displayed.
     - \-
     - Automatic input
     -
- Operation
     - ○
     - Selection
     -
- Schedule
     - Specify the scheduled date/time for executing the Conductor.
     - \-
     - Manual input
     - A date/time earlier than the current time cannot be entered
- Execute work
     - Executes the registered Conductor.
     - ○
     -
**About Specifying the Operation**
This allows you to substitute and execute the "specific values" registered under a different operation ID in the "  " menu of the orchestrator to which that Movement belongs.
Use this when you want to reuse the same Movement to operate a different server, etc.
-*About Skip**
In edit/update mode, the skip setting is saved by :guilabel:`Register` / :guilabel:`Update`.
Also, in view mode, you can specify skip individually before execution, changing a skip setting already saved in Conductor editing and then executing the Conductor.
However, in view mode this change applies only at execution time and the setting is not saved.

## Conductor Work History
※If the Conductor has a hierarchical structure, the leaf-level Movements are also included.

## Conductor Work Check
The "Conductor work check" menu displays the execution status of Conductors.
   Conductor work execution
When you want to edit and re-execute a Conductor that has already been executed, it is recommended to create a separate Conductor using :guilabel:`Reuse as new` in the "Conductor edit/work execution" menu.
- | If a scheduled date/time is set for the selected Conductor work and it has not yet been executed, :guilabel:`Cancel schedule` is displayed.
- | The common items of the "Conductor work check" menu are as follows.
.. list-table:: List of common items for "Conductor work check"
- **Item**
        - **Description**
        - **Required**
        - **Input format**
        - **Constraints**
- Release stop
        - \-
        -
- Emergency stop
        - Stops the execution of the Conductor.
        - \-
        -
- Cancel schedule
        - Cancels the scheduled execution of the Conductor.
        - \-
        - Displayed when a scheduled date/time is set and it has not yet been executed.
- When you select a Node, the detailed information of the selected Node is displayed.
  #. "Conductor" tab
- Displayed when no Node is selected.
- The items in the tab are as follows.
      "Conductor" tab
-*Item**                        | **Description**                                 |
Conductor\       | ID           | A unique ID corresponding to the Conductor instance\ |
Name         | Displays the name of the Conductor being executed.\               |
Status   | Displays the status of the Conductor being executed and\   |
Execution user   | Displays the user who executed the Conductor.  |
Scheduled date/time     | Displays the execution date/time of the scheduled Conductor.|
Emergency stop     | If the Conductor being executed was emergency stopped\ |
Operation                  | Displays the operation name.           |
Remarks                            | A description or\                 |
  #. "Node" tab
-  Displayed when a Node is selected.
-  The items in the tab are as follows.
-*Item**                        | **Description**                                 |
Node ID      | On the Conductor's configuration information (JSON format)\         |
Status   | Displays the status of the Conductor being executed and\   |
St file   | If the selected Node is a Movement,\      |
Individual operation              | When an operation is specified for each Movement\    |
if so, its operation name is displayed\      |

## Conductor Scheduled Work Execution
1. In the "Conductor scheduled work execution" menu, you manage Conductor work that is executed periodically according to a schedule.
   Conductor scheduled work execution registration
   Conductor scheduled work execution schedule settings
 List of Conductor scheduled work execution registration items
-*Item**                        | **Description**                                                     | **Required** | **Input format**  | **Constraints**          |
Conductor name                   | Conductors registered in "" are\      | ○            | List selection    | -                    |
Operation name                | Registered in "Basic Console - "\       | ○            | List selection    | -                    |
Registered operations are shown in the list.               |              |               |                       |
Execution user                      | The user who executed "Register"/"Update" is\       | -           | Automatic input      |                       |
registered as the user who executes the Conductor.                                 |              |               |                       |
When the scheduled work execution registers work with "" \       |              |               |                       |
the "execution user" is carried over during registration.             |              |               |                       |
Schedule settings                | Opens a window for configuring detailed schedule settings\        | -           | -            | -                    |
Schedule     | Next execution date | After registration is complete, based on the schedule settings, the next\      | -           | Automatic input      | -                    |
Start date     | Enter the date on which to start the scheduled work execution.                     | ○            | Manual input      | From the scheduler settings\ |
End date     | Enter the date on which to end the scheduled work execution.                     | -           | Manual input      | From the scheduler settings\ |
Interval         | Enter the interval at which to execute periodically, based on the configured cycle.      | ○            | Manual input      | From the scheduler settings\ |
Week number       | Used when "Month (specified day of week)" is selected for the cycle, for periodic\      | ※1           | List selection    | From the scheduler settings\ |
Day of week         | Used when "Day of week" or "Month (specified day of week)" is selected for the cycle\      | ※2           | List selection    | From the scheduler settings\ |
Day           | Used when "Month (specified date)" is selected for the cycle, for periodic\      | ※3           | Manual input      | From the scheduler settings\ |
Time         | Enter the time to execute periodically.                           | ※4           | Manual input      | From the scheduler settings\ |
Work suspension period     | Start         | Enter the start date of the work suspension period.                         | ※5           | Manual input      | From the scheduler settings\ |
Between the start date and the end date, Conductor work registration\       |              |               | can only be entered          |
End         | Enter the end date of the work suspension period.                         | ※5           | Manual input      | From the scheduler settings\ |
Between the start date and the end date, Conductor work registration\       |              |               | can only be entered          |
※5 If you set a work suspension period, both "Start" and "End" must be entered.
-*Status name**        | **Description**                                                                        |
Preparing                  | This is the status immediately after registration.                                                  |
From "Next execution date", the specified time before it as set in "Conductor interval time setting"\  |
work is registered to "" and then, based on the schedule settings again,\  |
after that, no further Conductor work is registered.                                          |
Inconsistency error            | This status occurs when there is an invalid value in the schedule settings.                      |
Binding error            | This status occurs when work registration to "" fails.       |
As with the "Active" status, work registration to "" is executed, and again\  |
based on the schedule settings, the "next execution date" is updated in this way.        |
If work registration fails again at that time, the status remains "Binding error".    |
Conductor discontinued           | This status occurs when the registered Conductor is discontinued.                         |
If a discontinued Conductor is restored, the status is updated to "Preparing".     |
Operation discontinued           | This status occurs when the registered operation is discontinued.                         |
1. Immediately after registering a scheduled work execution, the status becomes "Preparing", and then backyard updates the "next execution date" based on the schedule settings, at which point the status becomes "Active".
Work with a status of "Active" or "Binding error" executes work registration to "" the specified time before the "next execution date" as set in "Conductor interval time setting", and the "next execution date" is updated again based on the schedule settings.
1. The "Conductor interval time setting" can be used to configure, from "Management Console - ", how many minutes before the "next execution date" work registration is executed.
When menu import is performed between different organizations via "", if ID conversion of the execution user of the scheduled work execution at the import destination fails, and scheduled work execution is performed in that state, the status of the scheduled work execution becomes "Binding error".
# Appendix

## About Conductor Notification Destination Definition

#### Conductor Notification Destination Definition Setting Example
 Teams Setting Example
Item                   | Setting value                                           |
URLOPT_POSTFIELDS)    | Conductor name: \__CONDUCTOR_NAME__, <br>         |
 Slack Setting Example
Item                   | Setting value                                           |
URLOPT_POSTFIELDS)    | Conductor name: \__CONDUCTOR_NAME__, <br>         |
 Setting Sample (with Proxy setting, notification suppression setting, and other settings)

#### Notification Log Output Example

### Structure of the Notification Log

### Example) Notification Execution Log (Normal)

### Example) Notification Execution Log (Error)
