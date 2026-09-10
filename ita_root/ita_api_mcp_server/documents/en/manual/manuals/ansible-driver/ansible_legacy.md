# Ansible-Legacy
# Introduction
This document explains the Legacy functionality of the Ansible driver and how to operate it.
# Ansible-Legacy Overview
Applies configuration settings to various hosts using standard Ansible functionality.
Construction code is registered as individual YAML files, and work patterns are composed by combining them.
This is intended for use in tasks such as environment configuration for servers, storage, and network devices.
# Ansible-Legacy Menu Structure
This chapter explains the menu structure of Ansible-Legacy.

## Menu/Screen List
1. **Basic Console menus**
The list of Basic Console menus used by Ansible-Legacy is described below.
1. **Ansible Common menus**
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
1. **Ansible-Legacy menus**
The list of Ansible-Legacy menus is described below.
- No
     - Description
- 1
     - Movement List
     - Manages the list of Movements.
- 2
     - Playbook Material Collection
     - Manages Playbook files.
- 3
     - Movement-Playbook Association
     - Manages the Playbooks included by a Movement.
- 4
     - Auto-Substitution Value Registration Settings
     - Manages the Movements and variables linked to the per-operation, per-host item values registered in the Parameter Sheet.
- 5
     - Work Execution
     - Selects the Movement and Operation to execute work, and instructs execution.
- 6
     - Work Management
     - Manages the work execution history.
- 7
     - Work Status Check
     - Displays the work execution status.
- 8
     - Work Target Hosts
     - Displays the work target hosts for each work execution.
- 9
     - Substitution Value Management
     - Displays the concrete values of variables for each work execution.
- 10
     - Movement-Variable Association (※1)
     - Manages the variables used by a Movement.
※1 Hidden menus are menus used for internal processing.
They are set so that they are not displayed in a default ITA installation.
To display a hidden menu, restore the menu in Management Console --> Role/Menu Association Management. For details, see "  ".
Do not register anything to menus used for internal processing.
# Ansible-Legacy Usage Procedure
This section explains the procedure for using Ansible-Legacy.

## Ansible-Legacy Work Flow
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
Register the Movement for the work from Ansible-Legacy --> Movement List.
1. **Register the Playbook**
Register the Playbook used for the work from Ansible-Legacy --> Playbook Material Collection.
1. **Register global variables (if needed)**
Register the global variables used by the Playbook from Ansible Common --> Global Variable Management and Ansible Common --> Global Variable (Sensitive) Management.
1. **Register template files (if needed)**
Register the template files and template-embedded variables used by the Playbook from Ansible Common --> Template Management.
1. **Register file materials (if needed)**
Register the file materials and file-embedded variables used by the Playbook from Ansible Common --> File Management.
1. **Register unmanaged variables (if needed)**
Register variables from Ansible Common --> Unmanaged Variable List for variables extracted from materials targeted for variable extraction that you do not want displayed in Movement Name:Variable Name of Ansible-Legacy --> Auto-Substitution Value Registration.
1. **Register the Playbook to the Movement**
Register the Playbook included by the registered Movement from Ansible-Legacy --> Movement-Playbook Association.
1. **Create the Parameter Sheet**
Create the Parameter Sheet used to register the data used for configuring the work target, from Parameter Sheet Creation/Definition.
1. **Register data to the Parameter Sheet**
Register the data used for configuring the work target from the Parameter Sheet created in the previous step.
1. **Auto-Substitution Value Registration Settings**
From Ansible-Legacy --> Auto-Substitution Value Registration Settings, associate the setting values of the per-operation, per-host items registered in the Parameter Sheet with the Movement's variables.
1. **Work execution**
From Ansible-Legacy --> Work Execution, select the Movement and Operation and execute the work.
1. **Check work status**
1. **Check work history**
From Ansible-Legacy --> Work Management, the list of executed work is displayed, allowing you to check the history.
# Description of Ansible-Legacy Menu Operations
This chapter explains the menus used in Ansible-Legacy.

## Basic Console

## Ansible Common

## Ansible-Legacy

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

#### Playbook Material Collection
1. Performs maintenance (view/register/update/decommission) of Playbooks created by the user.
For how to write Playbooks, see "  ".
Sample Playbooks are registered in the Playbook Material Collection by default to improve usability.
The material names of sample Playbooks are prefixed with "~[Exastro standard]".
Sample Playbooks can be used by associating them with a Movement.
Item                              | Description                                                                          | Required  | Input method | Constraints            |
No.                               | Displays a 36-character string automatically assigned at registration.              | -        | Automatic    | -                     |
Playbook material name            | Enter the Playbook material name managed by ITA.                                     | Yes       | Manual       | Max length 255 bytes  |
Playbook material                 | Upload the created Playbook file.                                                     | Yes       | File select  | Max size 100 MB       |
The Playbook file to upload must be created with UTF-8 encoding without a BOM.  |           |              |                        |
Target | Linux                | Select "*" if the Playbook can be used on Linux.                                      | -        | List select  | As noted in the description column.   |
Windows              | Select "*" if the Playbook can be used on Windows.                                    | -        | List select  | As noted in the description column.   |
Other                | If the Playbook can be used for a purpose other than Linux or Windows, enter the intended purpose of the Playbook.    | -        | Manual       | Max length 4000 bytes       |
Description                       | Enter a description of the Playbook.                                                  | -        | Manual       | Max length 4000 bytes       |
Description (en)                  | Enter a description of the Playbook in English.                                       | -        | Manual       | Max length 4000 bytes       |
**Timing of extracting variables defined in the Playbook**
Internal processing extracts variables defined within the Playbook file. The extracted variables can then have concrete values registered in "  ".
Because extraction does not occur in real time, it may **take some time** before the variables become usable in "  ".

#### Movement-Playbook Association
1. Performs maintenance (view/register/update/decommission) of the Playbooks included by a Movement.
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
        - | The Movement name registered in Ansible-Legacy --> Movement List is displayed.
Select the Movement.
        - Yes
        - List select
        - As noted in the description column.
- Playbook material
        - | The Playbook material name registered in Ansible-Legacy --> Playbook Material Collection is displayed.
Select the Playbook material to be included by the Movement.
        - Yes
        - List select
        - As noted in the description column.
- Include order
        - | Enter the execution order (1 or higher) of the Playbook material.
        - Yes
        - Manual
        - 1 to 2,147,483,647
- Remarks
        - A free-text field.
        - -
        - Manual
        - Max length 4000 bytes

#### Auto-Substitution Value Registration Settings
1. Manages the association (view/register/update/decommission) between the setting values of Parameter Sheet items and the Movement's variables.
Registered information is reflected in Ansible-Legacy --> Substitution Value Management and Ansible-Legacy --> Work Target Hosts when work is executed.
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
Movement name                     | The Movement name registered in\       | Yes                                            | List select   | As noted in the description column.        |
Ansible-Legacy --> Movement List is displayed.                       |                                              |              |                             |
Select the Movement.                                             |                                              |              |                             |
IaC Variable (To)   | Movement Name\     | The variables used in the material registered in\      | Yes                                            | List select   | As noted in the description column.        |
:Variable Name         | Ansible-Legacy --> Movement-Playbook Association are displayed.                     |                                              |              |                             |
Select the variable to associate with the concrete value\  |                                              |              |                             |
of the item selected in Parameter Sheet (From).                                     |                                              |              |                             |
Substitution order        | Enter this if the variable is a multiple-value variable.                       |       | Manual     | 1 to 2,147,483,647            |
NULL linkage                      | Selects whether to register a NULL (blank)\                                        | -                                           | List select   | As noted in the description column.        |
value in Ansible-Legacy --> Substitution Value Management\                 |                                              |              |                             |
when the Parameter Sheet's concrete value is NULL (blank).                         |                                              |              |                             |
Registration occurs in Ansible-Legacy --> Substitution Value Management\      |                                              |              |                             |
regardless of the value in the Parameter Sheet.                                             |                                              |              |                             |
Registration occurs in Ansible-Legacy --> Substitution Value Management\                                    |                                              |              |                             |
only if a value has been entered in the Parameter Sheet.                                             |                                              |              |                             |
※1: Required only when using a Parameter Sheet (bundle)
When associating an item with repeat settings in a Parameter Sheet (bundle) with a Movement's variable, you must enter the substitution order for the Parameter Sheet (From) in Ansible-Legacy --> Auto-Substitution Value Registration Settings.
In Ansible-Legacy, if the substitution order is left blank, the variable is treated as a normal variable.
If a substitution order is entered, the variable is treated as a multiple-value variable. For multiple-value variables, multiple
It is fine for the substitution order not to be consecutive for a particular multiple-value variable.
e.g.) Executing work by entering a substitution order for a multiple-value variable
1. In Ansible-Legacy --> Auto-Substitution Value Registration Settings, associate the setting values of items registered in the Parameter Sheet with the variables in the Playbook.
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
Even if a variable used in the Playbook is not registered in Auto-Substitution Value Registration Settings, work execution still proceeds, but this may result in an "undefined variable" error during ansible execution.
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
1. In Ansible-Legacy --> Auto-Substitution Value Registration Settings, associate the setting values of the items registered in the Parameter Sheet in step 2 with the Playbook's variables, and execute the work from Ansible-Legacy --> Work Execution.
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
"Calling Conductor" displays which Conductor the work was executed from, if it was executed from a Conductor. It is blank if executed directly from Ansible-Legacy.
1. **Work target host check**
1. **Substitution value check**
1. **Emergency stop/Cancel reservation**
1. **Execution log display**
When executed with Ansible Automation Controller, the Playbook is executed in units of work targets grouped by the values of User, Password, SSH Private Key File, Passphrase, Connection Type, and Instance Group in the work target's Ansible Common --> Device List, and the ansible execution log is split accordingly.
Additionally, specifying the number of job slices in the Option Parameters of Ansible Common --> Interface Information or Ansible-Legacy --> Movement List further splits each grouped work target by the number of job slices, and the Playbook is executed and the ansible execution log split accordingly.
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
# Writing the Playbook (Ansible-Legacy)
The Playbook uploaded in "  " is executed in include format from the master Playbook generated by ITA.
The master Playbook created by ITA is composed of a header section and a tasks section.

## Header Section
The Playbook you upload does not need to include a header section.
The header section has fixed default values, but these can be changed in Header Section of Ansible-Legacy --> Movement List.
     - hosts: all

## Tasks Section
The uploaded Playbook is executed in include format from the master Playbook generated by ITA.
For basic Playbook syntax, see the official Ansible manual.
e.g.) Example of a Playbook to upload
   - name: comment
The uploaded Playbook is included according to the Include Order in Ansible-Legacy --> Movement-Playbook Association.
# Appendix

## Association Between Input Data Used During Ansible Execution and ITA Menus
ITA extracts information from each menu to build the input data required for Ansible execution. During this process, the Password in Ansible Common --> Device List and the concrete values of variables for which Sensitive Setting is set to "True" in Ansible-Legacy --> Substitution Value Management are encrypted with ansible-vault.
The relationship between the various data and ITA menus is as follows.

#### Ansible-Legacy Input Data
- Menu group
     - Menu
     - Item
     - Path when the directory is extracted
     - Remarks
- Ansible-Legacy
     - Playbook Material Collection
     - Playbook
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
- Ansible-Legacy
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
- Ansible-Legacy
     - Substitution Value Management
     - Variable Name/Concrete Value
     - /host_vars
     -
- Ansible-Legacy
     - Template Management
     - Template-embedded variable
     - /host_vars
     -
- Ansible-Legacy
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
- Ansible-Legacy
     - Movement List
     - Option parameters
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible Common
     - Device List
     - | Login User ID
     - | When Execution Engine in Ansible Common --> Interface Information is "Ansible Core" or "Ansible Automation Controller"
     -
- Ansible-Legacy
     - Movement-Playbook Association
     - Playbook Name/Include Order
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

#### List of Files Saved in Legacy Result Data
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
