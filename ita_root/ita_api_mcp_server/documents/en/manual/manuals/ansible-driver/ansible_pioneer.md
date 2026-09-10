# Ansible-Pioneer
# Introduction
This document explains the Pioneer functionality of the Ansible driver and how to operate it.
# Ansible-Pioneer Overview
Adds a proprietary module to Ansible, enabling configuration to be applied interactively.
# Ansible-Pioneer Menu Structure
This chapter explains the menu structure of Ansible-Pioneer.

## Menu/Screen List
1. **Basic Console menus**
The list of Basic Console menus used by Ansible-Pioneer is described below.
1. **Ansible Common menus**
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
1. **Ansible-Pioneer menus**
The list of Ansible-Pioneer menus is described below.
- No
     - Description
- 1
     - Movement List
     - Manages the list of Movements.
- 2
     - Dialogue Type
     - Manages the dialogue types that group together dialogue files with the same purpose.
- 3
     - OS Type
     - Manages the OS types of devices targeted for work from Pioneer.
- 4
     - Dialogue File Material Collection
     - Manages the OS types associated with a dialogue type and the work procedure files in the ITA system's proprietary format (hereafter referred to as "dialogue files").
- 5
     - Movement-Dialogue Type Association
     - Manages the dialogue types corresponding to the dialogue files included by a Movement.
- 6
     - Auto-Substitution Value Registration Settings
     - Manages the Movements and variables linked to the per-operation, per-host item values registered in the Parameter Sheet.
- 7
     - Work Execution
     - Selects the Movement and Operation to execute work, and instructs execution.
- 8
     - Work Management
     - Manages the work execution history.
- 9
     - Work Status Check
     - Displays the work execution status.
- 10
     - Work Target Hosts
     - Displays the work target hosts for each work execution.
- 11
     - Substitution Value Management
     - Displays the concrete values of variables for each work execution.
- 12
     - Movement-Variable Association (※1)
     - Manages the variables used by a Movement.
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
# Ansible-Pioneer Usage Procedure
This section explains the procedure for using Ansible-Pioneer.

## Ansible-Pioneer Work Flow
-  **Work flow details and references**
1. **Register the OS type**
Register the OS type of the work target from Ansible-Pioneer --> OS Type.
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
Register the Movement for the work from Ansible-Pioneer --> Movement List.
1. **Register the dialogue type**
Register the dialogue type from Ansible-Pioneer --> Dialogue Type.
1. **Register the dialogue file**
Register the dialogue file for the combination of dialogue type and OS type from Ansible-Pioneer --> Dialogue File Material Collection.
1. **Register global variables (if needed)**
Register the global variables used by the dialogue file from Ansible Common --> Global Variable Management and Ansible Common --> Global Variable (Sensitive) Management.
1. **Register template files (if needed)**
Register the template files and template-embedded variables used by the dialogue file from Ansible Common --> Template Management.
1. **Register file materials (if needed)**
Register the file materials and file-embedded variables used by the dialogue file from Ansible Common --> File Management.
1. **Register unmanaged variables (if needed)**
Register variables from Ansible Common --> Unmanaged Variable List for variables extracted from materials targeted for variable extraction that you do not want displayed in Movement Name:Variable Name of Ansible-Pioneer --> Auto-Substitution Value Registration.
1. **Register the dialogue file to the Movement**
Register the dialogue type corresponding to the dialogue file included by the registered Movement from Ansible-Pioneer --> Movement-Dialogue Type Association.
1. **Create the Parameter Sheet**
Create the Parameter Sheet used to register the data used for configuring the work target, from Parameter Sheet Creation/Definition.
1. **Register data to the Parameter Sheet**
Register the data used for configuring the work target from the Parameter Sheet created in the previous step.
1. **Auto-Substitution Value Registration Settings**
From Ansible-Pioneer --> Auto-Substitution Value Registration Settings, associate the setting values of the per-operation, per-host items registered in the Parameter Sheet with the Movement's variables.
1. **Work execution**
From Ansible-Pioneer --> Work Execution, select the Movement and Operation and execute the work.
1. **Check work status**
1. **Check work history**
From Ansible-Pioneer --> Work Management, the list of executed work is displayed, allowing you to check the history.
# Description of Ansible-Pioneer Menu Operations
This chapter explains the menus used in Ansible-Pioneer.

## Basic Console

## Ansible Common

## Ansible-Pioneer

#### OS Type
1. Performs maintenance (view/register/update/decommission) of the OS types of devices targeted for work.
No.                       | Displays a 36-character string automatically assigned at registration.                       | -                 | Automatic              | -                                              |

#### Movement List
1. Performs maintenance (view/register/update/decommission) of Movement information.
Item                                      | Description                                                                                                           | Required  | Input method | Constraints                                                   |
MovementID                                | Displays a 36-character string automatically assigned at registration.                                                               | -        | Automatic     | -                                                         |
Movement name                             | Enter the name of the Movement.                                                                                                | Yes         | Manual     | Max length 255 bytes                                            |
Delay timer                              | Sets the delay used by Ansible-\ when execution of the Movement is delayed for the specified period.                                                                | -        | Manual     | 0 to 2,147,483,647                                           |
Parallel execution count              | Specifies the option parameter of the ansible-playbook command\                                                                | -        | Manual     | 1 to 4,294,967,296                                           |
Ansible \   | Execution environment  | Selects the execution environment registered in `Ansible Common --> Execution Environment Definition` in which the exec\                             | -        | List select   | As noted in the description column.                                       |
Agent \     |           | (container) is built, and the Parameter Sheet "Execution\                               |           |              |                                                            |
Usage Info    |           | Environment Parameter Definition" is associated with it.                                                     |           |              |                                                            |
builder\  | Enter the ansible-builder parameters.                                                                       |           |              |                                                            |
Usage Info    |           | If not specified, the default execution environment configured in\ is used.                                                           |           |              |                                                            |

#### Dialogue Type
1. Performs maintenance (view/register/update/decommission) of dialogue types.
In Ansible-Pioneer, differences between "OS types" are defined per dialogue file, and dialogue files that share the same purpose are grouped as a "dialogue type," absorbing (abstracting) device-specific differences.
- Item
        - Description
        - Required
        - Input method
        - Constraints
- No.
        - Displays a 36-character string automatically assigned at registration.
        - -
        - Automatic
        - -
- Dialogue type name
        - Enter the dialogue type name.
        - Yes
        - List select
        - Max length 255 bytes
- Remarks
        - A free-text field.
        - -
        - Manual
        - Max length 4000 bytes

#### Dialogue File Material Collection
1. Performs maintenance (view/register/update/decommission) of dialogue files created by the user.
Register a dialogue file for each combination of dialogue type and OS type.
If you want one dialogue type to support multiple OSes, register a dialogue file for each OS type under the same dialogue type.
Item                              | Description                                                                                | Required  | Input method | Constraints            |
No.                               | Displays a 36-character string automatically assigned at registration.              | -        | Automatic    | -                     |
The Dialogue Type registered in\ is displayed.                               |           |              |                        |
Select the dialogue type for the dialogue file to register.                                        |           |              |                        |
OS type                           | The OS Type registered in Ansible-Pioneer --> OS Type \    | Yes         | List select   | As noted in the description column.   |
Select the OS type for the dialogue file to register.                                          |           |              |                        |
Target | Linux                | Select "*" if the Playbook can be used on Linux.                                      | -        | List select  | As noted in the description column.   |
Windows              | Select "*" if the Playbook can be used on Windows.                             | -        | List select   | As noted in the description column.   |
Other                | If the Playbook can be used for a purpose other than Linux or Windows, enter the intended purpose of the Playbook.    | -        | Manual     | Max length 4000 bytes       |
Description                       | Enter a description of the Playbook.                                                | -        | Manual     | Max length 4000 bytes       |
Description (en)                  | Enter a description of the Playbook in English.                                          | -        | Manual     | Max length 4000 bytes       |
**Timing of extracting variables defined within the dialogue file**
Internal processing extracts variables defined within the dialogue file. The extracted variables can then have concrete values registered in "  ".
Because extraction does not occur in real time, it may **take some time** before the variables become usable in "  ".

#### Movement-Dialogue Type Association
1. Performs maintenance (view/register/update/decommission) of the dialogue types corresponding to the dialogue files included by a Movement.
- Dialogue type
        - Description
        - Required
        - Input method
        - Constraints
- No.
        - Displays a 36-character string automatically assigned at registration.
        - -
        - Automatic
        - -
- Movement
        - | The Movement name registered in Ansible-Pioneer --> Movement List is displayed.
Select the Movement.
        - Yes
        - List select
        - As noted in the description column.
- Dialogue type
        - | The dialogue type registered in Ansible-Pioneer --> Dialogue Type is displayed.
Select the dialogue type corresponding to the dialogue file to be included by the Movement.
        - Yes
        - List select
        - As noted in the description column.
- Include order
        - | Enter the execution order (1 or higher) of the dialogue type.
        - Yes
        - Manual
        - 1 to 2,147,483,647
- Remarks
        - A free-text field.
        - Yes
        - Manual
        - Max length 4000 bytes

#### Auto-Substitution Value Registration Settings
1. Manages the association (view/register/update/decommission) between the setting values of Parameter Sheet items and the Movement's variables.
Registered information is reflected in Ansible-Pioneer --> Substitution Value Management and Ansible-Pioneer --> Work Target Hosts when work is executed.
Item                              | Description                                                       | Required                                     | Input method | Constraints                    |
No.                               | Displays a 36-character string automatically assigned at registration.                   | -                                           | Automatic     | -                          |
Parameter Shee\ | Menu Grou\ | The items of the Parameter Sheet are displayed.                             | Yes                                            | List select   | As noted in the description column.        |
t (From)      | p:Menu:Item|                                                                    |                                              |              |                             |
The Parameter Sheets available for selection are\                                  |                                              |              |                             |
Parameter Sheet Creation --> \                         |                                              |              |                             |
Parameter Sheet Definition/Creation --> Creation target\                          |                                              |              |                             |
those items of the Parameter Sheet created by selecting\                 |                                              |              |                             |
a Parameter Sheet (with host/operation).               |                                              |              |                             |
Substitution order        | If the Parameter Sheet is a bundle,\                                |                                |              |                             |
Registration method               | Selects the content to set for the concrete value\             | Yes                                            | List select   | As noted in the description column.        |
of the variable selected in IaC Variable (To).                                       |                                              |              |                             |
If the item's setting value is the variable selected in IaC Variable (To)\  |                                              |              |                             |
If the item's name is the variable selected in IaC Variable (To)\    |                                              |              |                             |
Movement name                     | The Movement name registered in\      | Yes                                            | List select   | As noted in the description column.        |
Ansible-Pioneer --> Movement List is displayed.                       |                                              |              |                             |
Select the Movement.                                             |                                              |              |                             |
IaC Variable (To)   | Movement Name\     | The variables used in the material registered in\     | Yes                                            | List select   | As noted in the description column.        |
:Variable Name         | Ansible-Pioneer --> Movement-Dialogue Type Association are displayed.                     |                                              |              |                             |
Select the variable to associate with the concrete value\  |                                              |              |                             |
of the item selected in Parameter Sheet (From).                                     |                                              |              |                             |
Substitution order        | Enter this if the variable is a multiple-value variable.                       |      | Manual     | 1 to 2,147,483,647            |
NULL linkage                      | Selects whether to register a NULL (blank)\                                        |                                              | List select   | As noted in the description column.        |
value in Ansible-Pioneer --> Substitution Value Management\                |                                              |              |                             |
when the Parameter Sheet's concrete value is NULL (blank).                         |                                              |              |                             |
Registration occurs in Ansible-Pioneer --> Substitution Value Management\     |                                              |              |                             |
regardless of the value in the Parameter Sheet.                                             |                                              |              |                             |
Registration occurs in Substitution Value\                                    |                                              |              |                             |
Management if a value has been entered in the Parameter Sheet.                                     |                                              |              |                             |
※1: Required only when using a Parameter Sheet (bundle)
When associating an item with repeat settings in a Parameter Sheet (bundle) with a Movement's variable, you must enter the substitution order for the Parameter Sheet (From) in Ansible-Pioneer --> Auto-Substitution Value Registration Settings.
In Ansible-Pioneer, if the substitution order is left blank, the variable is treated as a normal variable.
If a substitution order is entered, the variable is treated as a multiple-value variable. For multiple-value variables, multiple
It is fine for the substitution order not to be consecutive for a particular multiple-value variable.
e.g.) Executing work by entering a substitution order for a multiple-value variable
1. In Ansible-Pioneer --> Auto-Substitution Value Registration Settings, associate the setting values of items registered in the Parameter Sheet with the variables inside the dialogue file.
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
If a variable used in the dialogue file is not registered in Auto-Substitution Value Registration Settings during work execution, the work execution results in an error.
**Example of using file-embedded variables and template-embedded variables associated with dialogue file variables**
e.g.) Using the file-embedded variable CPF_test and template-embedded variable TPF_sample associated with a dialogue file variable via Auto-Substitution Value Registration Settings
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
1. In Ansible-Pioneer --> Auto-Substitution Value Registration Settings, associate the setting values of the items registered in the Parameter Sheet in step 2 with the dialogue file's variables, and execute the work from Ansible-Pioneer --> Work Execution.
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
"Calling Conductor" displays which Conductor the work was executed from, if it was executed from a Conductor. It is blank if executed directly from Ansible-Pioneer.
1. **Work target host check**
1. **Substitution value check**
1. **Emergency stop/Cancel reservation**
1. **Execution log display**
Additionally, specifying the number of job slices in the Option Parameters of Ansible Common --> Interface Information further splits each grouped work target by the number of job slices, and the Playbook is executed and the ansible execution log split accordingly.
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
Concrete value     | String    | Sensitive setting    | Displays "True" or "False".                                                                     |
Value               | Displays the concrete value of the variable at work execution.                                                                    |
| + | When Sensitive setting is "True"                                                         |
|   | The concrete value entered in the Parameter Sheet is encrypted and not displayed in ITA.\                                  |
|     The concrete value of the variable is set with content encrypted by ansible-vault.                                           |
| + | When Sensitive setting is "False"                                                        |
|   | The concrete value entered in the Parameter Sheet is displayed.                                                        |
File                     | Displays the file name associated with the variable of the work execution.                                                            |
Substitution order                                  | Displays the substitution order for multiple-value variables.                                                            |
# How to Write a Dialogue File (Ansible-Pioneer)
- Term
        - Description
- Command prompt
        - The string indicating that the system is waiting for command input, shown after connecting to the work target server via SSH from a terminal.
- Standard output
        - The output of a command's processing result, shown after a command is submitted to the work target server and before the next command prompt.

## Structure of a Dialogue File
conf             | Specifies the timeout value via the timeout parameter.  |
Write the timeout parameter of the conf session at the beginning of the dialogue file.
- | e.g.) Example of writing the timeout parameter of the conf session
- | e.g.) Example of writing password authentication
       - expect: '*assword'

## Dialogue Modules

#### expect Module
-***
-***
Parameter　         | Format                               | Required/Optional  | Description　                                                                             |
-*****
- | e.g.) Example of writing the expect module
     - expect: '*assword'

#### state Module
-***
-***
Parameter　         | Format                                     | Required/Optional  | Description　                                                                             |
-*****
- | e.g.) Example of writing the state module
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using success_exit
     # If a line containing 127.0.0.1 or localhost exists, it is judged as normal, but the "success_exit: yes" setting ends the dialogue file normally.
       - state: 'cat /etc/hosts'
           - '127.0.0.1'
           - 'localhost'
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using ignore_errors
     # If the target line is absent it is judged as abnormal, but the "ignore_errors: yes" setting proceeds to the next process.
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using shell
     # Passes the parameter value as a parameter of a user-created shell.
      - state: 'cat /etc/hosts'
          - '127.0.0.1'
          - 'localhost'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of a user shell (/tmp/grep.sh)
- | e.g.) Example of saving a file from the work target host to "Result Data" using the state module
     # The default shell is judged abnormal if the parameter is not set. To proceed to the next process, set "ignore_errors: yes".
      - state: 'cat /etc/hosts'
      - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

#### command Module
-***
④ Saves the content of the standard output to the register variable name specified by register.
⑦ Saves the content of the standard output to the register variable name specified by register.
-***
Parameter　         | Format                                     | Required/Optional  | Description　                                                                             |
-*****
- | e.g.) Example of writing the command module
The concrete values of variables used in the dialogue file's description and with_items are as follows.
  - | Content of the dialogue file
     - command: "systemctl  {{ item.0 }}  {{ item.1 }}"
         - '{{ VAR_status_list }}'    # item.0
         - '{{ VAR_service_list }}'   # item.1
         - '{{ VAR_prompt_list }}'    # item.2
         - '{{ VAR_timeout_list }}'   # item.3
  - | Concrete values of the variables used in with_items
       - start
       - start
       - httpd
       - mysql
     # Since there are 2 concrete values for the variable used in command,
     # the variables used in prompt and timeout need 3 concrete values.
       - command prompt
       - command prompt
       - command prompt
       - 10
       - 10
       - 10
- | e.g.) Example of using when
       - expect: 'password:'
       # If the ITA variable VAR_hosts_make is present in the host variable file (linked via Auto-Substitution Value Registration Settings, associating a Parameter Sheet item with a variable),
       - command: cat /etc/hosts
           - VAR_hosts_make is define
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using exec_when and register
       - expect: 'password:'
       # If a variable named VAR_hosts_make is present in the host variable file, cat the hosts file.
       - command: cat /etc/hosts
           - VAR_hosts_make is define
       # If a variable named VAR_hosts_make is present in the host variable file,
       # a command is submitted for each concrete value set in the with_items multiple-value variable.
       - command: 'echo {{ item.0 }}  {{ item.1 }} >> /etc/hosts'
           - VAR_hosts_make is define
           - '{{ VAR_hosts_ip }}'     # item.0
           - '{{ VAR_hosts_name }}'   # item.1
           - result_stdout no match({{ item.0 }} *{{ item.1 }})
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using failed_when
       - expect: 'password:'
       # A command is submitted for each concrete value set in the with_items multiple-value variable.
       # Configures automatic startup of the service.
       - command: 'systemctl enable {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
       # A command is submitted for each concrete value set in the with_items multiple-value variable.
       - command: 'systemctl start {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
       # A command is submitted for each concrete value set in the with_items multiple-value variable.
       # For example, if the concrete value of VAR_service_status_list is set to "running" and the service is running,
       - command: 'systemctl status {{ item.0 }}'
           - '{{ VAR_service_name_list }}'  # item.0
           - '{{ VAR_service_status_list }}'  # item.1
           - stdout match({{ item.1 }})
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'
- | e.g.) Example of using or/and conditions in when
       - expect: 'password:'
       - command: systemctl stop my_service
           - '{{ VAR_status }} == 10 OR {{ VAR_status }} == 11'
           - '{{ VAR_sub_status }} == 20 OR {{ VAR_sub_status }} == 21'
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

#### localaction Module
-***
-***
Parameter　         | Format                                     | Required/Optional  | Description　                                                                           |
-*****
- | e.g.) Example of writing localaction
       - expect: 'password:'
       # Creates a per-host directory in the directory shared by the Movement ({{ __workflowdir__ }}).
       - localaction: mkdir -p 0755 {{ __workflowdir__ }}/{{ __inventory_hostname__ }}
       - state: cat /etc/hosts
       - expect: '{{ __loginuser__ }}@{{ __inventory_hostname__ }}'

## Regular Expressions
Strings written in the following modules and parameters are evaluated as regular expressions.
- The expect parameter of the expect module
- The prompt parameter of the state module
- The prompt parameter of the command module
- match() in the when/exec_when/failed_when parameters of the command module
- Target character
     - After escaping
- \\
     - | \\\\
- \*
     - \\*
- \.
     - \\.
- \+
     - \\+
- ?
     - \\?
- \|
     - \\|
- { }
     - \\{ \\}
- ( )
     - \\( \\)
- [ ]
     - \\[ \\]
- ^
     - \\^
- $
     - \\$
- | e.g.) Correct example
- | e.g.) Incorrect example

## Notes

#### Notes When Using the state Module and command Module
1. When a trailing wildcard regular expression "\.\*" is written in the prompt parameter
The state module and command module submit the command and then treat the data before the command prompt specified by the prompt parameter as standard output.
   - | e.g.) Example of using a trailing wildcard regular expression
       - state: echo 'saple data'
1. When processing an interactive command
   - | e.g.) Example of processing the interactive command "ssh-keygen"
        - expect: 'assword:'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
        # Set the path of the private key file
        - expect: 'id_rsa\):'
        # Set the passphrase
        - expect: ' passphrase\):'
        - expect: ' passphrase again:'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
        - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'

#### Notes When Using Multiple-Value Variables
The only parameter in a dialogue file that can use a multiple-value variable is the with_items parameter of the command module. Using one in any other location results in an error during work execution.

#### Notes at the End of a Dialogue File
- | e.g.) Example of submitting the "exit" command that ends the session at the last line of the dialogue file
       - expect: 'assword:'
       - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'
       - expect: '{{ __loginuser__ }}@{{ __loginhostname__ }}'

#### Notes When Writing a Dialogue File in YAML Format
Dialogue files are treated as YAML-format files. If the file contains content that does not conform to YAML format as shown below, an error occurs when registering the dialogue module.
- | If a variable is written in a module's parameter and the entire parameter is not enclosed in quotation marks.
- | If a parameter is written using only constants and the constant ends with "**:**", and the entire parameter is not enclosed in quotation marks.
Enclose the entire value of each module's parameter in quotation marks.

#### Notes About the LANG Setting of the Work Target's Login User
Configure the login user's "LANG" setting from LANG in Ansible Common --> Device List.
If "euc/shift_jis" is set, the dialogue file may not be processed correctly due to characteristics of the UTF-8 decoding performed by the pexpect module used for communication control with the work target.

#### Notes About the Termination Code of Commands Submitted to the Work Target
     - expect: 'password:'
     - command: '{{ VAR_command }}\r'
     - state: '{{ VAR_state }}\r'
        - '{{ VAR_parameter1 }}'
        - '{{ VAR_parameter2 }}'

#### Operating System Command Sequence
Depending on the work target, an Operating System Command sequence may be attached immediately before the command prompt sent from the work target. ITA removes the escape sequence that immediately precedes the string specified by the prompt parameter.
# Appendix

## Association Between Input Data Used During Ansible Execution and ITA Menus
ITA extracts information from each menu to build the input data required for Ansible execution. During this process, the Password in Ansible Common --> Device List and the concrete values of variables for which Sensitive Setting is set to "True" in Ansible-Pioneer --> Substitution Value Management are encrypted with ansible-vault.
The relationship between the various data and ITA menus is as follows.

#### Ansible-Pioneer Input Data
- Menu group
     - Menu
     - Item
     - Path when the directory is extracted
     - Remarks
- Ansible-Pioneer
     - Dialogue File Material Collection
     - Dialogue file
     - /child_playbooks
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
- Ansible-Pioneer
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
- Ansible-Pioneer
     - Substitution Value Management
     - Variable Name/Concrete Value
     - /host_vars
     -
- Ansible-Pioneer
     - Template Management
     - Template-embedded variable
     - /host_vars
     -
- Ansible-Pioneer
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
     - Interface Information
     - Option parameters
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible-Pioneer
     - Movement List
     - Parallel execution count
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible Common
     - Device List
     - | Host name
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible Common
     - Device List
     - Connection options
     - /host_vars
     -
- Ansible-Pioneer
     - Movement-Dialogue Type Association
     - | Dialogue file
     - /playbook.yml
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

#### List of Files Saved in Ansible-Pioneer Result Data
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
- xxx.pid
     - | File that records the process ID of the ansible-playbook command
     - Yes
     -
     - Yes
- pioneer.xxx
     - | File that records the process ID of the Pioneer module.
     - Yes
     - Yes
     - Yes
- xxx_private.log
     - | File that records the log of the Pioneer module.
     - Yes
     - Yes
     - Yes
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
