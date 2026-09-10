# Terraform Cloud/EP driver
# Introduction
This document describes the functions and operation methods of Terraform Cloud/EP driver.
For an overview of Terraform and Terraform driver, and for functions common to Terraform CLI driver, refer to "".
# Console Menu Structure
This chapter describes the menu structure used by Terraform Cloud/EP driver.

## Menu/Screen List
1. **Basic Console menus**
The list of Basic Console menus used by Terraform Cloud/EP driver is described below.
- No
        - Menu group
        - Description
- 1
        - Basic Console
        - Operation list
        - You can maintain (view/register/update/discontinue) the operation list.
1. **Terraform Cloud/EP driver menus**
The list of Terraform Cloud/EP driver menus is described below.
-*N\  | **Menu\  | **Menu\  | **Description**                               |
Cloud/EP     | Interface Information | Manages the information.                   |
Organization Management        | Manages the information.                   |
Management         | Manages the information.                   |
4     |              | Movement\    | Manages the Movement list.           |
5     |              | Module\      | Manages Module files.           |
6     |              | Policy Management   | Manages Policy files.           |
7     |              | Policy \     | Manages Policy Sets                 |
Set Management      | A Policy Set manages the relationship\            |
Set-Policy\  | between Policy and\                         |
Set-Work\    | Workspace.                         |
10    |              | Movement-\   | Manages the association\        |
Module Link   | between Movements and Module materials.                         |
11    |              | Variable\  | If the type of a variable defined in the tf file\      |
Nesting Management         | registered in the Module material collection is\        |
| list or set, and that variable contains a\          |
| list, set, tuple, or object defined\           |
| within it, manages the maximum\          |
| iteration count of the member variables.             |
12    |              | Automatic Assignment\  | Manages the Movement and variable\      |
Value Registration Setting     | linked to the item and value of each operation\      |
| registered in the parameter sheet menu.\          |
| \                          |
13    |              | Work Execution     | Executes the Movement and operation\  |
14    |              | Work Management     | Manages work execution history.             |
16    |              | Assignment Value Management   | Manages the assignment values of variables.             |
Terraform\   | Displays the list of registered Organizations, Workspaces,\ |
Management         | Policies, and Policy Sets, and\     |
18    |              | Module-Variable\ | Manages the link between\          |
Link\        | Module variables and Module materials.                         |
19    |              | Member\    | Manages member variables.             |
Variable Management\    |                                        |
20    |              | Movement-\   | Manages the link between Movements and variables.      |
Variable Link\    |                                        |
21    |              | Movement-\   | Manages the link between Movements and\           |
Member\    | member variables.                         |
Variable Link\    |                                        |
※1 Hidden menus are menus in which data is registered/updated by internal functions.
When the Terraform Cloud/EP driver function is installed, these menus are set so as not to be displayed.
To display a hidden menu, restore the menu from Management Console --> Role/Menu Binding Management. For details, refer to "".
# Usage Procedure
This section describes the usage procedure for each Terraform Cloud/EP menu.

## Terraform Cloud/EP Work Flow
The standard work flow for each Terraform Cloud/EP driver menu is as follows.
-  **Work flow details and references**
1. **Registering the submitted operation name**
1. **Configuring the interface information**
Registers the information of the Terraform linked with ITA.
1. **Registering and linking an Organization**
Registers the Organization information used by Terraform, and performs the linkage with Terraform.
1. **Registering and linking a Workspace**
Registers the Workspace information used by Terraform, and performs the linkage with Terraform.
1. **Registering a Movement**
Registers a Movement for the work.
1. **Registering a Module material**
Registers the Module file to be executed for the work.
1. **Registering a Policy (if necessary)**
Registers a Policy file to be executed by the PolicyCheck performed before work execution.
1. **Registering a Policy set (if necessary)**
Registers a Policy set for linking with the Workspace to which the Policy is applied.
1. **Linking a Policy to a Policy set (if necessary)**
Registers the link between a Policy set and a Policy.
1. **Linking a Workspace to a Policy set (if necessary)**
Registers the link between a Policy set and a Workspace.
1. **Specifying a Module material for a Movement**
Specifies a Module material for the registered Movement.
1. **Setting the maximum iteration count (if necessary)**
Sets the maximum iteration count of variables and member variables.
1. **Creating a parameter sheet (if necessary)**
Required when setting concrete values for variables defined in a Module material.
1. **Registering data in the parameter sheet (if necessary)**
Required when setting concrete values for variables defined in a Module material.
1. **Automatic Assignment Value Registration Setting (if necessary)**
Required when setting concrete values for variables defined in a Module material.
1. **Executing work**
1. **Checking work status**
1. **Checking work history**
# Applying Policies

## About Linking Policy/PolicySet/Workspace
-*To use the Policy function, the linked Terraform must be Terraform Enterprise or Terraform Cloud with a plan for which the "Policy & Security" function is enabled.**
To apply a Policy, you must first complete each Policy-related setting registration, and then configure the linking settings.
First, link the Policy registered at "" with the Policy set registered at "".
Next, link the Terraform Workspace registered at "" with the Policy set registered at "".
At work execution time, the Policy set and the Policy linked to it are applied to the Workspace linked to the Movement.
# Function and Operation Description
This chapter describes the functions of each menu used by Terraform Cloud/EP driver.

## Basic Console
Operation list
-*****************
In Basic Console --> Operation List, you manage the operations to be executed by the orchestrator. Work is selected from within the Basic Console menu.
For details on the registration method, refer to "" in the related manual.

## Terraform Cloud/EP Menu
This section describes operations in the Terraform Cloud/EP driver menus.
-*******************
1. In Terraform Cloud/EP --> Interface Information, you can maintain (view/update) the information of the Terraform linked with ITA.
If the interface information is unregistered, or if multiple records are registered, an unexpected error occurs when work is executed.
-*Item**                          | **Description**                     | **Required\   | **Input method** | **Constraints**    |
For the method of issuing a User Token, refer to\      |           |              |                 |
Set this if required for\    |           |              |                 |
NULL Linkage                          | Sets whether, when the parameter\  | o         | List selection   | -              |
value's concrete value is NULL\  |           |              |                 |
(blank) in the Automatic Assignment Value Registration Setting, the registration to Assignment Value Management\  |           |              |                 |
is performed with a NULL (blank) value.\  |           |              |                 |
This value is applied when "NULL\  |           |              |                 |
Organization Management
-***************
1. In Terraform Cloud/EP --> Organization Management, you maintain (view/register/update/discontinue) Organizations used by Terraform.
You can also link (register/update/delete) an Organization registered in ITA to Terraform.
If work is executed while an Organization is not linked (registered) to Terraform, \ **the work execution results in an unexpected error**\ .
If the "Hostname" and "User Token" registered in "6.2.1 Interface Information" are incorrect, the linkage with Terraform fails, and the following message is displayed in the linkage status.
      Terraform linkage (Organization Management)
-*Item**                          | **Description**                     | **Required\   | **Input method** | **Constraints**    |
Workspace Management
-************
1. In Terraform Cloud/EP --> Workspace Management, you maintain (view/register/update/discontinue) Workspaces used by Terraform.
You can also link (register/update/delete) a Workspace registered in ITA to Terraform, and perform resource deletion (terraform destroy).
If work is executed while a Workspace is not linked (registered) to Terraform, \ **the work execution results in an unexpected error**\ .
If the "Hostname" and "User Token" registered in "6.2.1 Interface Information" are incorrect, the linkage with Terraform fails, and the following message is displayed in the linkage status.
The same message is also displayed if the selected Organization is not linked (registered) to Terraform.
      Terraform linkage (Workspace Management)
-*Item**                          | **Description**                     | **Required\   | **Input method** | **Constraints**    |
The registered Organization name is\    |           |              |                 |
The latest version at the time of linkage\  |           |              |                 |
Resources configured and managed per Workspace\   |           |              |                 |
Movement list
-***********
1. In Terraform Cloud/EP --> Movement List, you maintain (view/register/update/discontinue) Movement names.
Because a Movement must be linked to an Organization:Workspace as Terraform usage information, you must first register the target in "" "".
Movement name            | Mov\      | o         | Manual input  | Maximum length\   |
Registered in \ |           |           |           |
-***********
1. In Terraform Cloud/EP --> Module Material Collection, you maintain (view/register/update/discontinue) Modules created by the user.
1. The item list of the Module Material Collection is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Module material name
        - Enter the Module material name to be managed by ITA.
        - o
        - Manual input
        - Maximum length 255 bytes
- Module material
        - Upload the created Module material.
        - o
        - File selection
        - Maximum size 100 megabytes
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
**Timing for extracting variables defined within a Module file (a file with the .tf extension)**
Variables defined within a registered Module file (a file with the .tf extension) are extracted by internal processing.
Extracted variables can then have their concrete values registered in "".
Because the extraction timing is not real-time, it **may take time** before the variables can be used in "".
Policy Management
-*********
1. In Terraform Cloud/EP --> Policy Management, you maintain (view/register/update/discontinue) Policies created by the user.
1. The item list of Policy Management is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Policy name
        - | Enter the Policy name to be managed by ITA.
        - o
        - Manual input
        - Maximum length 255 bytes
- Policy material
        - Upload the created Policy file.
        - o
        - File selection
        - Maximum size 100 megabytes
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
Policy Set Management
-*************
1. In Terraform Cloud/EP --> Policy set Management, you maintain (view/register/update/discontinue) Policy sets.
1. The item list of Policy set Management is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Policy set name
        - | Enter the Policy set name to be managed by ITA.
        - o
        - Manual input
        - Maximum length 255 bytes
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
-********************
1. In Terraform Cloud/EP --> Policy set-Policy Link, you maintain (view/register/update/discontinue) the link between Policy sets registered in "" and Policies registered in "".
1. The item list of Policy set-Policy Link is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Policy set name
        - | Select a Policy set name registered in "".
        - o
        - List selection
        - -
- Policy name
        - | Select a Policy name registered in "".
        - o
        - List selection
        - -
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
-**********************
1. In Terraform Cloud/EP --> Policy set-Workspace Link, you maintain (view/register/update/discontinue) the link between Policy sets registered in "" and Workspaces registered in "".
1. The item list of Policy set-Workspace Link is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Policy set name
        - | Select a Policy set name registered in "".
        - o
        - List selection
        - -
- Workspace name
        - | Select a Workspace name (linked to an Organization) registered in "".
        - o
        - List selection
        - -
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
Movement-Module Link
-******************
1. In Terraform Cloud/EP --> Movement-Module Link, you maintain (view/register/update/discontinue) the link between Movements registered in "" and Module materials registered in "".
When a Movement is executed, the linked Module material is applied.
Multiple Module materials can be linked to a Movement.
1. The item list of Movement-Module Link is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Movement name
        - | Select a Movement name registered in "".
        - o
        - List selection
        - -
- Module material
        - | Select a Module material registered in "".
        - o
        - List selection
        - -
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
Variable Nesting Management
-*************
1. In Terraform Cloud/EP --> Variable Nesting Management, if the type of a variable defined in a tf file registered in the Module Material Collection is list or set, and that variable contains a list, set, tuple, or object defined within it, you can view and update the maximum iteration count of the member variables.
Because this menu manages records via internal functions based on the Module Material Collection, registration, discontinuation, and restoration cannot be performed.
For an example of the Variable Nesting Management flow, refer to "".
1. The item list of Variable Nesting Management is as follows.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- Variable name
        - Displays the variable used in the Module material registered in "".
        - -
        - Not enterable
        - -
- Member variable name (repeating)
        - If the Variable Nesting Management target is a member variable, the member variable name is displayed. The member variable name is displayed with the variables at each level concatenated by ".".
        - -
        - Not enterable
        - -
- Maximum iteration count
        - | Enter the maximum iteration count of the array, in the range 1 to 1024.
The upper limit of the maximum iteration count can be changed within the range 1 to 1024 via the setting value of identification ID "MAXIMUM_ITERATION_TERRAFORM-CLOUD-EP" from "Management Console - ".
The initial value is set to the iteration count obtained from the value described in the default of the tf file.
If the tf file has no default description, 1 is set.
If the last updater is not the "Terraform Cloud/EP Variable Update Function", the value will not be changed by an update of the Module material.
        - o
        - Manual input
        - Input value 1 to 1,024 (varies according to the setting value of "")
- Remarks
        - A free-text field.
        - -
        - Manual input
        - Maximum length 4000 bytes
※Because the initial registration and update of the iteration count are not real-time, it **may take time** before the variables can be used in "".
Automatic Assignment Value Registration Setting
-*****************
1. In Terraform Cloud/EP --> Automatic Assignment Value Registration Setting, you link the parameter sheet (with operation) created by the parameter sheet creation function with the variables of a Movement.
The registered information is reflected in "" via internal processing when work is executed.
-*Item**                          | **Description**                     | **Required\   | **Input method** | **Constraints**    |
Parameter Sheet\ | Menu Group\ | An item of a parameter sheet\  | o         | List selection   | -              |
(From)        | : Menu : Item\ | (with operation) created\  |           |              |                 |
              | by the parameter sheet creation function\  |           |              |                 |
The parameter sheet is\          |           |              |                 |
a parameter sheet (with operation)\    |           |              |                 |
created at Parameter Sheet Creation -->\  |           |              |                 |
Parameter Sheet Definition/Creation\          |           |              |                 |
              |        |              |                 |
Assignment Order        | Of the bundle sheet\  | ※1        | Manual input     | Integer from 1\  |
registered for the parameter sheet (with operation)\  |           |              | to 2147483647          |
created by the parameter sheet creation function\  |           |              |                 |
the assignment order registered\  |           |              |                 |
Registration Method                          | Whether to use a Value type: item setting value\  | o         | List selection   | -              |
as the concrete value of the linked variable\  |           |              |                 |
or select a concrete value of the variable\  |           |              |                 |
Movement Name                        | The Movements registered in "" are\ |           |              |                 |
displayed.     |           |              |                 |
IaC Variable (To)     | Movement name : Variable\| The member variable is displayed according to\       | ※2        | List selection   | -              |
Name : Member Variable | the format of the variable used in the material registered\  |           |              |                 |
via "terraform_cloud_ep_movement_module_link".\  |           |              |                 |
              |  |           |              |                 |
              |         |           |              |                 |
Select the variable.           |           |              |                 |
Assignment Order        | Required for variable names\  | ※3        | Manual input     | Blank or\ |
and member variables for which multiple\  |           |              | integer from\|
NULL Linkage                          | Sets whether to register\  | -        | List selection   | -              |
the concrete value of the parameter sheet to\  |           |              |                 |
Assignment Value Management with a NULL (blank)\       |           |              |                 |
value.       |           |              |                 |
even if\  |           |              |                 |
registration to Assignment Value Management is performed only if\  |           |              |                 |
set in "rmation".\  |           |              |                 |
※1: Required only if the parameter sheet bundle is enabled.
※2: Required if a member variable exists for the selected "Movement name: variable name", and only if "HCL Setting" is "False".
※3: Required only if the selected "Movement name: variable name" and "Movement name: variable name: member variable" are of a format that requires an assignment order.
**For a parameter sheet with bundle enabled**
When linking an item of a parameter sheet with bundle enabled to a variable of a Movement, you must enter the assignment order of the Parameter Sheet (From) in Terraform Cloud/EP --> Automatic Assignment Value Registration Setting.
      Automatic Assignment Value Registration Setting registration method when using a parameter sheet with bundle enabled
**About setting the member variable of IaC Variable (To)**
This must be set if the variable type is object or tuple.
When setting a member variable, also set the concrete values of all other member variables within the same variable.
The default value is not used for other member variables for which an assignment value was not set.
For details and specific examples, refer to "※1 ... Member variable target" in "".
**About the assignment order of IaC Variable (To)**
This must be set if the variable type is list or set.
For the items subject to linkage in Automatic Assignment Value Registration Setting, refer to "".
-*******
1. **Specifying the scheduled date/time**
Only a future date/time can be registered in "Scheduled Date/Time".
1. **Specifying the Movement**
Select a Movement registered in "".
1. **Specifying the operation**
Select an operation registered in "".
1. **Execution**
1. **Plan check**
1. **Checking parameters**
When work using a Module material that includes an Output block is executed from a Conductor, the content written in the Output block is saved as a json format file in the Conductor work directory path.
By using this file, values output by Terraform can be used by another Movement in the same Conductor.
-*File path**
[Conductor work directory path]/[Conductor instance ID]/terraform_output_[work No.].json
Conductor work directory path ... The Conductor work directory path for Ansible ITA's proprietary variable data linkage
Conductor instance ID ... The conductor instance ID of ""
-***********
1. **Execution status display**
For "Execution Type", "Plan Check" is set for a Plan check, "Resource Deletion" is set for the deletion of resources configured and managed per Workspace (executed from ""), and "Normal" is set otherwise.
If the status ends in an unexpected error, if the cause is a registration deficiency in "", the linkage (registration) with Terraform not having been performed in "" "", or another Web content registration deficiency, a message is displayed in the error log.
"Calling Conductor" displays which Conductor the work was executed from. It is left blank if executed directly from Terraform Cloud/EP driver.
The "RUN-ID" displayed in "Terraform Usage Information" is the ID of the execution management managed on the Terraform side, and is used during the internal linkage processing with Terraform.
※If "Execution Type" is "Resource Deletion", the following items are not set.
   - Calling Conductor
   - Movement
   - Operation
   - Submitted Data
1. **Checking assignment values**
1. **Emergency stop/canceling a reservation**
1. **Displaying execution logs**
1. **Log search**
The refresh display interval and maximum number of display lines for the execution log and error log can be set in "Status Monitoring Interval (in milliseconds)" and "Progress Status Display Line Count" in "".
1. **Submitted data**
You can download a zip format file containing a file obtained in json format of the list of executed Module materials, Policy materials, and the assignment values that were set.
- Folder name
        - File name
        - Description
- -
        - | (Submitted Module material file name)
        - | All submitted Module material files are stored directly under the zip file.
- -
        - | (Submitted Policy file name)
        - | All submitted Module material files are stored directly under the zip file.
- variables
        - | variables.json
        - | A file obtained in json format that describes the setting values of "variable name (key)", "concrete value (value)", "HCL Setting", and "Sensitive Setting" for each set assignment value.
If Sensitive Setting is ON (true), the concrete value is set to null.
1. **Result data**
- Folder name
        - File name
        - Description
- -
        - | plan.log
        - | A log file describing the content output by the execution log (plan.log).
- -
        - | policyCheck.log
        - | A log file describing the content output by the execution log (policyCheck.log).
- -
        - | apply.log
        - | A log file describing the content output by the execution log (apply.log).
- -
        - | error.log
        - | A log file describing the content output to the error log.
- -
        - | sv-XXXXXX.tfstate
        - | The state file generated by Terraform. Because the file name is created by Terraform, it differs for each execution.
Work Management
-*******
1. In Terraform Cloud/EP --> Work Management, you can view work history.
-*Item**                          | **Description**                                                                  |
"Normal", "Plan Check", and "Parameter Sheet Check" are available.                  |
Registration Date/Time                          | The date/time when the work was registered is displayed.                                        |
Movement        | ID              | The ID of the Movement is displayed.                                              |
Name            | The name of the Movement is displayed.                                            |
Delay Timer    | The delay timer value set for the Movement is displayed.                        |
Terraf\| Work\  | The ID of the Terraform Workspace set for the Movement is displayed.                 |
Organi\| The name of the Terraform Workspace (linked to a Terraform Organization) set for the Movement is displayed.  |
RUN-ID | The ID of the RUN managed by the linked Terraform is displayed.                        |
Operation  | No.             | The No. of the operation is displayed.                                       |
Name            | The name of the operation is displayed.                                      |
Assignment Value Management
-*********
1. In Terraform Cloud/EP --> Assignment Value Management, you can view the concrete values assigned to the variables of the Module material used by the Movement linked to the operation.
-*Item**                          | **Description**                                                                  |
Operation                    | The operation selected at work execution time is displayed.                        |
Movement Name                        | The Movement selected at work execution time is displayed.                              |
Movement Name:Variable Name                 | The variable name\ |
attached to the Movement selected in "" is displayed.                |
HCL Setting                           | The HCL Setting "False" or "True"\ |
selected in "" is displayed.              |
Also, for variables with a hierarchical structure in which "member variable" and "assignment order" have been entered\     |
If "True", the HCL setting of the Variables registered in the linked Terraform is enabled\      |
Movement Name:Variable Name:Member Variable    | The member variable name\ |
attached to the Movement selected in "" is displayed.        |
For the variable name and member variable attached to the Movement selected in ""\     |
Concrete Value          | Sensitive Setting   | "True" or "False" is displayed.                                   |
If "True", the Sensitive Setting of the Variables registered in the linked Terraform is\    |
Value              | The concrete value of the variable used by the operation/Movement is displayed.             |
Linked Terraform Management
-*******************
1. In Terraform Cloud/EP --> Linked Terraform Management, based on the information registered in "", ITA connects to Terraform and can display the lists of Organizations/Workspaces/Policies/Policy sets registered in Terraform.
From the displayed lists, you can delete from Terraform a target that is registered in ITA.
You can also perform deletion of resources configured and managed per Workspace.
※Operations performed on this page have no effect on the registration targets on the ITA side.
1. The item list displayed for each list retrieval is as follows.
   .. list-table:: Item list (Organization Registration Management)
- Item
        - Description
- Organization Name
        - The name of the Organization registered in Terraform.
- Email address
        - The Email address registered for the Organization.
- ITA Registration Status
        - If the target Organization Name is registered in "", "Registered" is displayed. If not registered, "Unregistered" is displayed.
- Delete
   .. list-table:: Item list (Workspace Registration Management)
- Item
        - Description
- Organization Name
        - The name of the Organization linked to the target Workspace.
- Workspace Name
        - The name of the Workspace registered in Terraform.
- ITA Registration Status
        - If the target Organization Name is registered in "", "Registered" is displayed. If not registered, "Unregistered" is displayed.
- Resource Deletion
- Delete
   .. list-table:: Item list (Policy Registration Management)
- Item
        - Description
- Organization Name
        - The name of the Organization linked to the target Policy.
- Policy Name
        - The name of the Policy registered in Terraform.
- ITA Registration Status
        - If the target Policy Name is registered in "", "Registered" is displayed. If not registered, "Unregistered" is displayed.
- Download Policy Code
- Delete
    Item list (PolicySet Registration Management)
-*Item**                          | **Description**                                                                  |
ITA Registration Status   | If the target Policy Set Name and Workspace Name are registered in "", "Registered" is displayed.\  |
If not registered, "Unregistered" is displayed.                          |
ITA Registration Status   | If the target Policy Set Name and Policy Name are registered in "", "Registered" is displayed.\     |
If not registered, "Unregistered" is displayed.                          |
ITA Registration Status                     | If the target Policy Set Name is\    |
registered in "", "Registered" is displayed. If not registered,\   |
"Unregistered" is displayed.                                                |
