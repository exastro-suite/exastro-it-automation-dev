# Ansible-LegacyRole
# Introduction
This document explains the LegacyRole functionality of the Ansible driver and how to operate it.
# Ansible-LegacyRole Overview
As with Legacy mode, configuration settings are applied to various hosts using standard Ansible functionality.
Construction code is registered as packages, and work patterns are composed of combinations of Roles.
# Ansible-LegacyRole Menu Structure
This chapter explains the menu structure of Ansible-LegacyRole.

## Menu/Screen List
1. **Basic Console menus**
The list of Basic Console menus used by Ansible-LegacyRole is described below.
1. **Ansible Common menus**
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
1. **Ansible-LegacyRole menus**
The list of Ansible-LegacyRole menus is described below.
- No
     - Description
- 1
     - Movement List
     - Manages the list of Movements.
- 2
     - Role Package Management
     - Manages role packages.
- 3
     - Movement-Role Association
     - Manages the role packages included by a Movement.
- 4
     - Variable Nesting Management
     - Manages the maximum number of repetitions of the array when a multi-level variable is composed of a repeating array.
- 5
     - Auto-Substitution Value Registration Settings
     - Manages the Movements and variables linked to the per-operation, per-host item values registered in the Parameter Sheet.
- 6
     - Work Execution
     - Selects the Movement and Operation to execute work, and instructs execution.
- 7
     - Work Management
     - Manages the work execution history.
- 8
     - Work Status Check
     - Displays the work execution status.
- 9
     - Work Target Hosts
     - Displays the work target hosts for each work execution.
- 10
     - Substitution Value Management
     - Displays the concrete values of variables for each work execution.
- 11
     - Role Name Management (※1)
     - Allows viewing the association between the role names registered inside the role package file ("zip") uploaded in Role Package Management and the role package.
- 12
     - Movement-Variable Association (※1)
     - Manages the variables used by a Movement.
- 13
     - Multi-Level Variable Member Management (※1)
     - Manages the structure of multi-level variables defined in the default variable definition file or ITA readme file inside the role package file ("zip") uploaded in Role Package Management.
- 14
     - Multi-Level Variable Array Combination Management (※1)
     - Manages the multi-level variable array combinations defined in the default variable definition file or ITA readme file inside the role package file ("zip") uploaded in Role Package Management.
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
# Ansible-LegacyRole Usage Procedure
This section explains the procedure for using Ansible-LegacyRole.

## Ansible-LegacyRole Work Flow
-  **Work flow details and references**
1. **Register connection information for the work target**
Register the connection information for the work target from Ansible Common --> Device List.
1. **Register the operation name**
Register the operation name for the work from Basic Console --> Operation List.
1. **Register Ansible Automation Controller host information (if needed)**
Register the Ansible Automation Controller host information from Ansible Common --> Ansible Automation Controller Host List.
1. **Register interface information**
From Ansible Common --> Interface Information, select which execution engine to use — Ansible Core, Ansible Automation Controller, or Ansible Execution Agent — and register the connection information for the execution engine's server.
1. **Register the execution environment definition template management (if needed)**
From Ansible Common --> Execution Environment Definition Template Management, register the template file of the execution environment definition file (execution-environment.yml) used when building the execution environment (container) with ansible-builder inside the Ansible Execution Agent.
When ITA is installed, a template file that allows adding python modules and ansible galaxy collections is registered.
1. **Register the Parameter Sheet "Execution Environment Parameter Definition" (if needed)**
Register the parameters to embed into the template file of the execution environment definition file (execution-environment.yml) registered from Ansible Common --> Execution Environment Definition Template Management.
When ITA is installed, a Parameter Sheet "Execution Environment Parameter Definition" is registered with the parameters to embed into the execution environment definition template file (execution-environment.yml).
1. **Register the execution environment management (if needed)**
Register the association between the execution environment definition file (execution-environment.yml) template file registered in Ansible Common --> Execution Environment Definition Template Management and the Parameter Sheet "Execution Environment Parameter Definition".
When ITA is installed, the association between the Parameter Sheet "Execution Environment Parameter Definition" and Ansible Common --> Execution Environment Definition Template Management is registered.
1. **Register the Movement**
Register the Movement for the work from Ansible-LegacyRole --> Movement List.
1. **Register the role package**
Register the role package used for the work from Ansible-LegacyRole --> Role Package Management.
1. **Register global variables (if needed)**
Register the global variables used within the role package from Ansible Common --> Global Variable Management and Ansible Common --> Global Variable (Sensitive) Management.
1. **Register template files (if needed)**
Register the template files and template-embedded variables used within the role package from Ansible Common --> Template Management.
1. **Register file materials (if needed)**
Register the file materials and file-embedded variables used within the role package from Ansible Common --> File Management.
1. **Register unmanaged variables (if needed)**
Register variables from Ansible Common --> Unmanaged Variable List for variables extracted from materials targeted for variable extraction that you do not want displayed in Movement Name:Variable Name of Ansible-LegacyRole --> Auto-Substitution Value Registration.
1. **Register the role package to the Movement**
Register the role package included by the registered Movement from Ansible-LegacyRole --> Movement-Role Association.
1. **Register the maximum repeat count of the multi-level variable (if needed)**
Register the maximum repeat count of the array for member variables defined as an array within a multi-level variable, from Ansible-LegacyRole --> Variable Nesting Management.
1. **Create the Parameter Sheet**
Create the Parameter Sheet used to register the data used for configuring the work target, from Parameter Sheet Creation/Definition.
1. **Register data to the Parameter Sheet**
Register the data used for configuring the work target from the Parameter Sheet created in the previous step.
1. **Auto-Substitution Value Registration Settings**
From Ansible-LegacyRole --> Auto-Substitution Value Registration Settings, associate the setting values of the per-operation, per-host items registered in the Parameter Sheet with the Movement's variables.
1. **Work execution**
From Ansible-LegacyRole --> Work Execution, select the Movement and Operation and execute the work.
1. **Check work status**
1. **Check work history**
From Ansible-LegacyRole --> Work Management, the list of executed work is displayed, allowing you to check the history.
# Description of Ansible-LegacyRole Menu Operations
This chapter explains the menus used in Ansible-LegacyRole.

## Basic Console

## Ansible Common

## Ansible-LegacyRole

#### Movement List
1. Performs maintenance (view/register/update/decommission) of Movement information.
Item                                | Description                                                                       | Required  | Input method | Constraints                                          |
MovementID                          | Displays a 36-character string automatically assigned at registration.           | -         | Automatic    | -                                                    |
Movement name                       | Enter the name of the Movement.                                                   | Yes       | Manual       | Max length 255 bytes                                 |
Delay                               | Sets the delay used by Ansible-\ when execution of the Movement is delayed for the specified period.                  | -        | Manual     | 0 to 2,147,483,647                                    |
Header\               | The section from the beginning of the parent Playbook that ITA automatically generates, up to tasks\                                       | -        | Manual     | Max length 4000 bytes                                      |
※1 When "become: yes" is set in the header section
The following setting is required on the work target.
Configure the login user's sudo privilege with NOPASSWD in `/etc/sudoers`.
**Demo_user ALL=(ALL) NOPASSWD:ALL**

#### Role Package Management
1. Performs maintenance (view/register/update/decommission) of role package files (zip) created by the user.
The role package file must be registered as a zip archive of the directory level that contains "roles". For details on the role package directory structure, see "  ".
Item                              | Description                                                                          | Required  | Input method | Constraints            |
No.                               | Displays a 36-character string automatically assigned at registration.              | -        | Automatic    | -                     |
Role package name                 | Enter the role package name managed by ITA.                                          | Yes       | Manual       | Max length 255 bytes  |
The Playbook files contained in the role package file to be uploaded must be created with\ |           |              |                        |
Target | Linux                | Select "*" if the Playbook can be used on Linux.                                      | -        | List select  | As noted in the description column.   |
Windows              | Select "*" if the Playbook can be used on Windows.                                    | -        | List select  | As noted in the description column.   |
Other                | If the Playbook can be used for a purpose other than Linux or Windows, enter the intended purpose of the Playbook.    | -        | Manual       | Max length 4000 bytes       |
Description                       | Enter a description of the Playbook.                                                  | -        | Manual       | Max length 4000 bytes       |
Description (en)                  | Enter a description of the Playbook in English.                                       | -        | Manual       | Max length 4000 bytes       |
**Timing of extracting variables defined within the role package**
Internal processing extracts variables defined within the role package. The extracted variables can then have concrete values registered in "  ".
Because extraction does not occur in real time, it may **take some time** before the variables become usable in "  ".
Unique management of variable names per Movement
In Ansible-LegacyRole, variable names extracted from materials targeted for variable extraction are managed uniquely per Movement.
If the same variable name is used across roles within the same role package but the variable structures differ, an error occurs when registering in Ansible-LegacyRole --> Role Package Management.
Specifically, if the same variable name is used for a normal variable and a multi-level variable, or between multi-level variables with different multi-level structures, a registration error occurs.
Note that if the role packages differ, registration is possible even in the above cases.
1            | package_A              | role1        | | VAR_SAMPLE:                                                            | Yes        | | · Same variable name                                                 |
|                                                                          |           | | · Same definition of multi-level variable member variables                           |
| |  - { VAR_001: "aaaa" , \VAR_002:\ "bbbb" }                             |           | | · Different order in which the member variables are described                               |
2            | package_A              | role1        | | VAR_SAMPLE:                                                            | No         | | · Same variable name                                                 |
|                                                                          |           | | · Different definition of multi-level variable member variables                         |
3             | package_A              | role1        | | VAR_SAMPLE:                                                            | No         | | · Same variable name                                                 |
|                                                                          |           | | · Normal variable and multi-level variable coexist                             |

#### Movement-Role Association
1. Performs maintenance (view/register/update/decommission) of the role packages included by a Movement.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- No.
        - | Displays a 36-character string automatically assigned at registration.
        - -
        - Automatic
        - -
- Movement
        - | The Movement name registered in Ansible-LegacyRole --> Movement List is displayed.
Select the Movement.
        - Yes
        - List select
        - -
- Role package name:role name
        - | The role names contained in the role package file (ZIP format) registered in Ansible-LegacyRole --> Role Package Management are displayed.
Select the role of the role package to be included by the Movement.
Multiple role packages cannot be registered for the same Movement.
        - Yes
        - List select
        - -
- Include order
        - | Enter the execution order (1 or higher) of the role.
        - Yes
        - Manual
        - 1 to 2,147,483,647
- Remarks
        - A free-text field.
        - -
        - Manual
        - Max length 4000 bytes

#### Variable Nesting Management
1. Performs maintenance (view/update) of the maximum repeat count of the array for member variables that have a repeating array defined within a multi-level variable defined in the role package file (ZIP format) registered in Ansible-LegacyRole --> Role Package Management.
For usage instructions, see "  ".
- Item
        - Description
        - Required
        - Input method
        - Constraints
- No.
        - | Displays a 36-character string automatically assigned at registration.
        - -
        - Automatic
        - -
- Maximum repeat count
        - | Enter the maximum repeat count of the array, in the range 1 to 1,024.
The upper limit of the maximum repeat count can be changed within the range 1 to 1024 via the setting value for identification ID "MAXIMUM_ITERATION_ANSIBLE-LEGACYROLE" from "Management Console - ".
        - Yes
        - Manual
        - Input value 1 to 1,024 (varies depending on the setting value of "")
- Remarks
        - A free-text field.
        - -
        - Manual
        - Max length 4000 bytes
**Timing of initial registration and updates to the repeat count**
Internal processing performs the initial registration of the repeat count for member variables defined within a repeating array of a multi-level variable defined in the role package. After initial registration, the repeat count can be updated in Variable Nesting Management.
Note that initial registration and updates to the repeat count do not occur in real time, so it may **take some time** before the variables become usable in "  ".

#### Auto-Substitution Value Registration Settings
1. Manages the association (view/register/update/decommission) between the setting values of Parameter Sheet items and the Movement's variables.
Registered information is reflected in Ansible-LegacyRole --> Substitution Value Management and Ansible-LegacyRole --> Work Target Hosts when work is executed.
Item                              | Description                                                       | Required                                     | Input method | Constraints                    |
No.                               | Displays a 36-character string automatically assigned at registration.                   | -                                           | Automatic     | -                          |
Parameter Shee\ | Menu Grou\ | The items of the Parameter Sheet are displayed.                             | Yes                                            | List select   | As noted in the description column.        |
t (From)      | p:Menu:Item|                                                                    |                                              |              |                             |
The Parameter Sheets available for selection are\                                  |                                              |              |                             |
Parameter Sheet Creation --> \                         |                                              |              |                             |
Parameter Sheet Definition/Creation --> Creation target\                          |                                              |              |                             |
those items of the Parameter Sheet created by selecting\                 |                                              |              |                             |
a Parameter Sheet (with host/operation).               |                                              |              |                             |
Substitution order        | If the Parameter Sheet is a bundle,\                                      |                                |              |                             |
Registration method               | Selects the content to set for the concrete value\             | Yes                                            | List select   | As noted in the description column.        |
of the variable selected in IaC Variable (To).                                       |                                              |              |                             |
If the item's setting value is the variable selected in IaC Variable (To)\  |                                              |              |                             |
If the item's name is the variable selected in IaC Variable (To)\    |                                              |              |                             |
Movement name                     | The Movement name registered in\   | Yes                                            | List select   | As noted in the description column.        |
Ansible-LegacyRole --> Movement List is displayed.                       |                                              |              |                             |
Select the Movement.                                             |                                              |              |                             |
IaC Variable (To)   | Movement Name\     | The variables used in the material registered in\    | Yes                                            | List select   | As noted in the description column.        |
:Variable Name         | Ansible-LegacyRole --> Movement-Role Association are displayed.                     |                                              |              |                             |
Select the variable to associate with the concrete value\  |                                              |              |                             |
of the item selected in Parameter Sheet (From).                                     |                                              |              |                             |
Movement Name:Variable\  | If a multi-level variable is selected in Movement Name:Variable Name, the\     |         | List select   | As noted in the description column.        |
Name:Member\  | member variables of the multi-level variable are displayed.                             |                                              |              |                             |
Variable            |                                                                    |                                              |              |                             |
Select the member variable.                                         |                                              |              |                             |
Substitution order        | Required when the variable allows multiple concrete values.             |   | Manual     | 1 to 2,147,483,647            |
NULL linkage                      | Selects whether to register a NULL (blank)\                                        | -                                           | List select   | As noted in the description column.        |
value in Ansible-LegacyRole --> Substitution Value Management\             |                                              |              |                             |
when the Parameter Sheet's concrete value is NULL (blank).                         |                                              |              |                             |
Registration occurs in Ansible-LegacyRole --> Substitution Value Management\  |                                              |              |                             |
regardless of the value in the Parameter Sheet.                                             |                                              |              |                             |
Registration occurs in Substitution Value\                                    |                                              |              |                             |
Management if a value has been entered in the Parameter Sheet.                                       |                                              |              |                             |
※1: Required only when using a Parameter Sheet (bundle)
When associating an item with repeat settings in a Parameter Sheet (bundle) with a Movement's variable, you must enter the substitution order for the Parameter Sheet (From) in Ansible-LegacyRole --> Auto-Substitution Value Registration Settings.
※2: Required only when the selected variable is a multi-level variable
Selection of a member variable is required only for multi-level variables. Only variables that require a concrete value are shown as member variables.
The member variable name is displayed by joining the variables of each level with ".".
For repeating arrays, the repeat position (starting from 0) is joined using "[ ]". The number of repeating arrays is set in Ansible-LegacyRole --> Variable Nesting Management.
e.g.) Checking the member variables selectable in Auto-Substitution Value Registration Settings, and the member variables selectable after updating the maximum repeat count in Variable Nesting Management
1. Define the variables as shown below in the role package's variable definition file (defaults/main.yml), and register the role package from Ansible-LegacyRole --> Role Package Management.
**Content of the variable definition file**
           - name: alice
               - craete_dir: /dir
               - craete_pass:
                   - sample_pass: pass1
               - craete_pass:
                   - sample_pass: pass2
                 - craete_users:
                     - prod_user: user1
                     - dev_user: user2
1. If the role package is registered with the variables defined as in step 1, the following is registered in Ansible-LegacyRole --> Variable Nesting Management, and by default the following member variables can be selected in Ansible-LegacyRole --> Auto-Substitution Value Registration Settings.
      .. list-table:: Registered content of Variable Nesting Management
- Variable name
           - Member variable name
           - Maximum repeat count
- VAR_aaaa
           - 0
           - 1
- VAR_aaaa
           - 0.directory
           - 1
- VAR_aaaa
           - 0.password
           - 1
- VAR_aaaa
           - 0.password.sample
           - 1
- VAR_aaaa
           - 0.user.root
           - 1
- VAR_aaaa
           - 0.user.root.dev
           - 1
- VAR_aaaa
           - 0.user.root.prod
           - 1
      .. list-table:: Member variables selectable in Auto-Substitution Value Registration Settings
- Variable name
           - Member variable name
- VAR_aaaa
           - [0].directory[0].create_dir
- VAR_aaaa
           - [0].name
- VAR_aaaa
           - [0].object
- VAR_aaaa
           - [0].password[0].create_pass
- VAR_aaaa
           - [0].password[0].sample[0].sample_pass
- VAR_aaaa
           - [0].user.root[0].create_users
- VAR_aaaa
           - [0].user.root[0].dev[0].dev_user
- VAR_aaaa
           - [0].user.root[0].prod[0].prod_user
1. In Ansible-LegacyRole --> Variable Nesting Management, update the maximum repeat count of member variable "0.user.root.prod" from the initial value "1" to "3".
      .. list-table:: Update to Variable Nesting Management
- Variable name
           - Member variable name
           - Maximum repeat count
- VAR_aaaa
           - 0.user.root.prod
           - 3
1. When the member variable is updated as in step 3, the member variables selectable in Ansible-LegacyRole --> Auto-Substitution Value Registration Settings are also updated as shown below.
(The member variables [0].user.root[0].prod[1].prod_user and [0].user.root[0].prod[2].prod_user were added to the dropdown.)
      .. list-table:: Member variables selectable in Auto-Substitution Value Registration Settings
- Variable name
           - Member variable name
- VAR_aaaa
           - [0].directory[0].create_dir
- VAR_aaaa
           - [0].name
- VAR_aaaa
           - [0].object
- VAR_aaaa
           - [0].password[0].create_pass
- VAR_aaaa
           - [0].password[0].sample[0].sample_pass
- VAR_aaaa
           - [0].user.root[0].create_users
- VAR_aaaa
           - [0].user.root[0].dev[0].dev_user
- VAR_aaaa
           - [0].user.root[0].prod[0].prod_user
- VAR_aaaa
           - [0].user.root[0].prod[1].prod_user
- VAR_aaaa
           - [0].user.root[0].prod[2].prod_user
※3: Required only when the selected variable is a variable for which multiple concrete values can be set
It is fine for the substitution order not to be consecutive for a particular multiple-value variable.
e.g.) Executing work by entering a substitution order for a multiple-value variable
1. Define the variables as shown below in the role package's variable definition file (defaults/main.yml), and register the role package from Ansible-LegacyRole --> Role Package Management.
**Content of the variable definition file**
           - user-name
           - group-name
           - meta-name
           - login
           - authorized
           - space
           - cluster
1. In Ansible-LegacyRole --> Auto-Substitution Value Registration Settings, associate the setting values of items registered in the Parameter Sheet with the variables inside the Role.
       Registered content of the Parameter Sheet
**Host Name**   | **Operation Name**   | **Parameter**                            |
      .. list-table:: Registered content of Auto-Substitution Value Registration Settings
- Menu name
           - Item
           - Variable name
           - Substitution order
- sample-menu
           - Item 1
           - VAR_substitutionA
           - 30
- sample-menu
           - Item 2
           - VAR_substitutionA
           - 10
- sample-menu
           - Item 3
           - VAR_substitutionA
           - 20
- sample-menu
           - Item 1
           - VAR_substitutionB
           - 2
- sample-menu
           - Item 2
           - VAR_substitutionB
           - 4
- sample-menu
           - Item 3
           - VAR_substitutionB
           - 1
- sample-menu
           - Item 4
           - VAR_substitutionB
           - 3
1. During work execution, the variables registered in Auto-Substitution Value Registration Settings are output to the host variable file (host_vars/test-host) as follows.
**Content output to the host variable file**
           - value2
           - value3
           - value1
           - value3
           - value1
           - value4
           - value2
**Output to the host variable file**
Only the variables registered in Auto-Substitution Value Registration Settings are output to the host variable file during work execution.
The same applies to multi-level variables — only the member variables for which a concrete value has been registered are output.
e.g.) Checking the variables for which concrete values were registered in Auto-Substitution Value Registration Settings and the variables that are output to the host variable file during work execution
1. Define the variables as shown below in the role package's variable definition file (defaults/main.yml), and register the role package from Ansible-LegacyRole --> Role Package Management.
**Content of the variable definition file**
           - name: alice
                 - craete_users:
                     - prod_user: user1
                     - dev_user: user2
1. In Ansible-LegacyRole --> Auto-Substitution Value Registration Settings, associate the setting values of items registered in the Parameter Sheet with the variables inside the Role.
       Registered content of the Parameter Sheet
Host Name       | Operation Name       | Parameter          |
      .. list-table:: Registered content of Auto-Substitution Value Registration Settings
- Menu name
           - Item
           - Variable name
           - Member variable name
- sample-menu
           - Item 1
           - VAR_output
           - [0].name
- sample-menu
           - Item 2
           - VAR_output
           - [0].user.root[0].dev[0].dev_user
1. During work execution, the variables registered in Auto-Substitution Value Registration Settings are output to the host variable file (host_vars/test-host) as follows.
**Content output to the host variable file**
           - name: value1
               - dev:
                 - dev_user: value2
**Example of using file-embedded variables and template-embedded variables associated with Playbook variables**
e.g.) Using the file-embedded variable CPF_test and template-embedded variable TPF_sample associated with a Playbook variable via Auto-Substitution Value Registration Settings
1. Register the following in Ansible Common --> File Management / Ansible Common --> Template Management.
      .. list-table:: Registered content of File Management
- File-embedded variable name
           - File material
- CPF_test
           - test_file.txt
      .. list-table:: Registered content of Template Management
- Template-embedded variable name
           - Template material
- TPF_sample
           - sample.tpl
1. After creating a Parameter Sheet in Parameter Sheet Definition/Creation with "Ansible Common:File Management:File-Embedded Variable Name" and "Ansible Common:Template Management:Template-Embedded Variable Name" as Parameter Sheet items, register the file-embedded variable and template-embedded variable as the item setting values in the Parameter Sheet.
       Registered content of the sample Parameter Sheet
**Host Name**   | **Operation Name**   | **Parameter**                        |
- **File Management**| **Template Management**|
1. In Ansible-LegacyRole --> Auto-Substitution Value Registration Settings, associate the setting values of the items registered in the Parameter Sheet in step 2 with the Playbook's variables, and execute the work from Ansible-LegacyRole --> Work Execution.
      .. list-table:: Registered content of Auto-Substitution Value Registration Settings
- Menu name
           - Item
           - Variable name
- Sample Parameter Sheet
           - File Management
           - VAR_filetest
- Sample Parameter Sheet
           - Template Management
           - VAR_temptest
         Substitution Value Management in Work Status Check
 For items covered by Auto-Substitution Value Registration Settings, see .

#### Work Execution
Select the target Movement from the Movement list.
Select the target operation from the Operation list.
1. **Work execution**
1. **Dry run**
When a dry run is performed, the behavior is equivalent to running the ansible-playbook command with the --check parameter specified.
1. **Parameter check**

#### Work Status Check
1. **Execution status display**
"Execution type" displays "Normal" for a work execution, "Dry run" for a dry run, and "Parameter check" for a parameter check.
"Calling Conductor" displays which Conductor the work was executed from, if it was executed from a Conductor. It is blank if executed directly from Ansible-LegacyRole.
1. **Work target host check**
1. **Substitution value check**
1. **Emergency stop/Cancel reservation**
1. **Execution log display**
When executed with Ansible Automation Controller, the Playbook is executed in units of work targets grouped by the values of User, Password, SSH Private Key File, Passphrase, Connection Type, and Instance Group in the work target's Ansible Common --> Device List, and the ansible execution log is split accordingly.
Additionally, specifying the number of job slices in the Option Parameters of Ansible Common --> Interface Information or Ansible-LegacyRole --> Movement List further splits each grouped work target by the number of job slices, and the Playbook is executed and the ansible execution log split accordingly.
- Element
        - Content
- Group number
        - A sequential number starting from 1 for groups formed by grouping the work target's Ansible Common --> Device List values of User, Password, SSH Private Key File, Passphrase, Connection Type, and Instance Group.
- Sequence number
        - | A sequential number starting from 1 for the divisions within a group, based on the job slice count setting.
1. **Log search**
The refresh interval and maximum number of displayed lines for the execution log and error log can be configured in Status Monitoring Interval (in milliseconds) and Progress Display Line Count in Ansible Common --> Interface Information.
1. **Input data**
The executed Playbook and other files can be downloaded.
1. **Result data**

#### Work Management
Calling Conductor                                                             | Displays the Conductor name if executed from a Conductor.                    |
Movement            | ID                                                      | Displays the ID of the Movement selected for work execution.                |
Name                                                    | Displays the name of the Movement selected for work execution.              |
Delay timer                                            | Displays the delay timer of the Movement selected for work execution.       |
Ansible usage information               | Host specification format          | Displays the host specification format of the Movement selected for work execution.                   |
WinRM connection               | Displays the WinRM connection of the Movement selected for work execution.                        |
Header section      | Displays the header section of the Movement selected for work execution.               |
ansible.cfg             | Allows uploading the ansible.cfg of the Movement selected for work execution.              |
Ansible Execution Agent \     | Execution environment                | Displays the Ansible Execution Agent execution environment of the Movement selected for work execution.|
ansible-builder\        | Displays the ansible-builder parameters of the Movement selected for work execution.        |
Parameters              |                                                                              |
Ansible Automation \          | Execution environment                | Displays the execution environment of the Movement selected for work execution.                         |
Operation      | No.                                                     | Displays the ID of the Operation selected for work execution.                         |
Name                                                    | Displays the name of the Operation selected for work execution.                       |
Work status            | Scheduled date/time                                                | Displays the scheduled date/time if it was set when the work was executed.                   |
Collection status            | Status                                              | Displays the status of the collection function.                                           |
Collection log                                                | Allows downloading the collection function's log.                                       |
Conductor instance number                                                     | Displays the Conductor instance number if executed from a Conductor.         |

#### Work Target Hosts
1. Allows viewing the work target hosts for each work execution.
- Item
        - Description
- No.
        - Displays a 36-character string automatically assigned at work execution.
- Work No.
        - Displays the work No. of the work execution.
- Operation
        - Displays the operation of the work execution.
- Movement name
        - Displays the Movement of the work execution.
- Host name
        - Displays the target host of the work execution.
- Remarks
        - A free-text field.

#### Substitution Value Management
1. Allows viewing the concrete values of variables for each work execution.
Operation                            | Displays the operation of the work execution.                                                                  |
Movement name                             | Displays the Movement of the work execution.                                                                        |
Movement Name:Variable Name               | Displays the variable of the work execution.                                                                            |
Movement Name:Variable Name:Member Variable            | Displays the member variables of a multi-level variable.                                                                      |
Concrete value     | String    | Sensitive setting    | Displays "True" or "False".                                                                     |
Value               | Displays the concrete value of the variable at work execution.                                                                    |
| + | When Sensitive setting is "True"                                                         |
|   | The concrete value entered in the Parameter Sheet is encrypted and not displayed in ITA.\                                  |
|     The concrete value of the variable is set with content encrypted by ansible-vault.                                           |
| + | When Sensitive setting is "False"                                                        |
|   | The concrete value entered in the Parameter Sheet is displayed.                                                        |
File                     | Displays the file name associated with the variable of the work execution.                                                            |
Substitution order                                  | Displays the substitution order for multiple-value variables.                                                            |
# Writing Construction Code

## Writing the Role Package
- - | Files to include
     - How ITA handles it
- \(1)\  site.yml \(master Playbook)\
     - △
     - Because it is created by ITA, if present it is overwritten.
- \(2)\  hosts
     - △
     - Because it is created by ITA, if present it is overwritten.
- \(3)\  group_vars
     - △
     - Because ITA does not handle this, if present it is deleted.
- \(4)\  host_vars
     - △
     - Because it is created by ITA, if present it is overwritten.
- \(5)\  ITA readme
     - △
     - | The ITA readme is defined per role. It is not an error if absent.
- \(6)\  roles
     - Yes
     - If the roles directory does not exist, an upload error occurs.
- \(7)\  roles/[role name①]
     - Yes
     - | If the role name directory does not exist, an upload error occurs.
- \(8)\  roles/[role name①]/readme.md
     - △
     - ITA does not concern itself with this.
- \(9)\  roles/[role name①]/tasks
     - Yes
     - | The tasks directory is required.
- \(10)\  roles/[role name①]/handlers
     - △
     - | ITA does not concern itself with whether the handlers directory exists.
- \(11)\  roles/[role name①]/templates
     - △
     - | ITA does not concern itself with whether the templates directory exists.
- \(12)\  roles/[role name①]/files
     - △
     - | ITA does not concern itself with whether the files directory exists.
- \(13)\  roles/[role name①]/vars
     - △
     - | ITA does not concern itself with whether the vars directory exists.
- \(14)\  roles/[role name①]/defaults
     - △
     - | ITA does not concern itself with whether the defaults directory exists.
- \(15)\  roles/[role name①]/meta
     - △
     - | ITA does not concern itself with whether the meta directory exists.

#### Master Playbook
The master Playbook created by ITA is composed of a header section and a roles section.
1. Header section
The header section has fixed default values, but these can be changed in Header Section of Ansible-LegacyRole --> Movement List.
        - hosts: all
1. Roles section
The roles inside the uploaded role package are executed as roles according to the Include Order in Ansible-LegacyRole --> Movement-Role Association.

#### Points to Note When the Role Names Inside the Role Package Use a Directory Hierarchy
1. A directory is recognized as a role if it contains a tasks directory.
   - parent/sample_role1
   - parent/sample_role2
   - sample_role6
1. Excluding directory hierarchies that contain multiple tasks directories

## Writing the ITA Readme
If you do not want to define variables directly in the Playbook, and a variable is not defined in the defaults variable definition file, you can define the variable in the ITA readme file so that its value can be specified using the Substitution Value Management function.

#### Naming Convention for the ITA Readme File Name
- Role name
     - File name to create
- mysql
     - ita_readme_mysql.yml
- mysql/install
     - ita_readme_mysql%install.yml

#### Format of the ITA Readme
The process by which the concrete values of variables defined in the ITA readme are output to the host variable file is hereafter referred to as "  ".
Also, if a variable definition overlaps between the ITA readme and the defaults variable definition file, the variable structure of the ITA readme is applied.
When a variable definition overlaps between the ITA readme and the defaults variable definition file, the following rules apply.
  .. list-table:: Variable adoption rules
- Defaults variable definition file
       - ITA readme
       - Source of the applied variable structure
- Defined
       - Not defined
       - Default variable definition file
- Not defined
       - Defined
       - ITA readme
- Defined
       - Defined
       - ITA readme
The variables and concrete values written in the ITA readme are never passed to ansible.

## Examples of Using "ita_readme"
- No.
     - Point
- 1
     - Using an externally obtained Ansible-LegacyRole without editing it
- 2
     - The role of "ita_readme"
- 3
     - About the variable definitions and default values described in "defaults/main.yml"
- 4
     - About the "host_vars file" and "ITA's Parameter Sheet"
- 5
     - A workaround for cases where you want to add to "defaults/main.yml"
- 6
     - Application to length evaluation in a Playbook
- 7
     - Application to defined evaluation in a Playbook
- | **Point 1: Using an externally obtained Ansible-LegacyRole without editing it**
By placing "ita_readme" outside the "roles" directory, you can supply parameters to the variables used within Ansible-LegacyRole (the "roles" directory) without editing it.
- | **Point 2: About the role of "ita_readme"**
"ita_readme" is a mechanism for conveying the variable name and variable type to ITA.
In other words, "ita_readme" is not a mechanism for defining the concrete value (parameter) of a variable (ITA does not recognize a concrete value even if written there).
The methods for supplying a concrete value are explained in the following points.
- | **Point 3: About the variable definitions and default values described in "defaults/main.yml"**
The variable definition and default value remain in effect unless defined in host_vars. (Example: "VAR_A: aaa")
- | **Point 4: About the "host_vars file" and "ITA's Parameter Sheet"**
The host_vars file is automatically created for each execution from ITA's Parameter Sheet.
- | **Point 5: A workaround for cases where you want to add to "defaults/main.yml"**
If you want to make changes to Ansible-LegacyRole (the "roles" directory), as a workaround you can describe the variable name and type in "ita_readme".
There is no need to redefine in "ita_readme" a variable that is already described in "defaults/main.yml".
If the same variable is defined in both files, the "ita_readme" side takes precedence.
- | **Point 6: Application to length evaluation in a Playbook**
Whether or not a variable has a concrete value can be used for conditional branching based on length evaluation.
For example, if "defaults/main.yml" has "VAR_C: []" and the variable "VAR_C" is executed without being given a concrete value, length = 0.
- | **Point 7: Application to defined evaluation in a Playbook**
Whether or not a concrete value is defined for a variable can be used for conditional branching based on defined evaluation.
For example, describe the definitions for variables "VAR_G" and "VAR_H", which are not defined in "defaults/main.yml", in "ita_readme". By describing them in "ita_readme", they become usable in ITA's Parameter Sheet.
If variable "VAR_G" is executed without being given a concrete value, it is not defined in "defaults/main.yml" or "host_vars", so defined → false.
Conversely, if variable "VAR_H" is given a concrete value of "kkk" and executed, it is defined in "host_vars", so defined → true.
# Appendix

## Association Between Input Data Used During Ansible Execution and ITA Menus
ITA extracts information from each menu to build the input data required for Ansible execution. During this process, the Password in Ansible Common --> Device List and the concrete values of variables for which Sensitive Setting is set to "True" in Ansible-LegacyRole --> Substitution Value Management are encrypted with ansible-vault.
The relationship between the various data and ITA menus is as follows.

#### Ansible-LegacyRole Input Data
- Menu group
     - Menu
     - Item
     - Path when the directory is extracted
     - Remarks
- Ansible-LegacyRole
     - Role Package Management
     - Role package
     - /roles
     -
- Ansible Common
     - Template Management
     - Template material
     - /template_files
     -
- Ansible Common
     - File Management
     - File material
     - /copy_files
     -
- Ansible-LegacyRole
     - Substitution Value Management
     - Concrete value (file)
     - /upload_files
     -
- Ansible Common
     - Global Variable Management
     - Variable Name/Concrete Value
     - /host_vars
     -
- Ansible Common
     - Global Variable (Sensitive) Management
     - Variable Name/Concrete Value
     - /host_vars
     - ※Encrypted with ansible-vault
- Ansible-LegacyRole
     - Substitution Value Management
     - Variable Name/Concrete Value
     - /host_vars
     -
- Ansible-LegacyRole
     - Template Management
     - Template-embedded variable
     - /host_vars
     -
- Ansible-LegacyRole
     - File Management
     - File-embedded variable
     - /host_vars
     -
- Ansible Common
     - Device List
     - | Login User ID
     - /host_vars
     -
- Ansible Common
     - Device List
     - SSH authentication key file
     - /ssh_key_files
     -
- Ansible Common
     - Device List
     - | WinRM public key file
     - /winrm_key_files
     -
- Ansible Common
     - Device List
     - Server certificate
     - /winrm_ca_files
     -
- Ansible Common
     - Interface Information
     - Option parameters
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible-LegacyRole
     - Movement List
     - Option parameters
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible Common
     - Device List
     - | Login User ID
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible-LegacyRole
     - Movement-Role Association
     - Role Name/Include Order
     - /site.yml
     -
- Ansible Common
     - Execution Environment Definition Template Management
     - Template file
     - builder_executable_files/execution-environment.yml
     - Only when Execution Engine in Ansible Common --> Interface Information is "Ansible Execution Agent"
- Ansible Common
     - Parameter Sheet "Execution Environment Parameter Definition"
     - Various upload files
     - builder_executable_files/{{REST API item name}}_upload file name
     - Only when Execution Engine in Ansible Common --> Interface Information is "Ansible Execution Agent"
- Ansible Common
     - Execution Environment Management
     - Tag name
     - | builder_executable_files/builder.sh
     - Only when Execution Engine in Ansible Common --> Interface Information is "Ansible Execution Agent"

## Result Data Created During Ansible Execution

#### List of Files Saved in Ansible-LegacyRole Result Data
- File name
     - Recorded content
     - For Ansible Core
     - For Ansible Automation Controller
     - For Ansible Execution Agent
- result.txt
     - Records the Ansible execution result
     - Yes
     -
     -
- error.log
     - | File to which error messages during work execution are output
     - Yes
     - Yes
     - Yes
- exec.log.org
     - File to which the standard output of the ansible-playbook command is output
     - Yes
     - Yes
     - Yes
- exec.log
     - | File processed from exec.log.org
     - Yes
     - Yes
     - Yes
- exec_<work number>_<group number>
     - | Split execution log files
     -
     - Yes
     -
- forced.txt
     - Record file created when an emergency stop is performed
     - Yes
     -
     - Yes
- user_files
     - Output directory used when the executed Playbook outputs files using the ITA-specific variable "__workflowdir__".
     - Yes
     - Yes
     - Yes
- | child_exec.log
     - The execution log of ansible-builder
     -
     -
     - Yes
