# Collection Function
# Introduction
This document explains ITA's collection function and how to operate it.
# Overview of the Collection Function
This chapter explains the collection function.

## About the Collection Function
The collection function is a function that automatically registers values into the Parameter Sheet based on work execution results (source files output in a defined format) performed in ITA.
This function targets the Ansible-Driver.
For details on the Parameter Sheet, see "".

#### Overview Diagram of the Collection Function

#### Overview Diagram of the Collection Function's Data Registration Process
Registration and updates to the Parameter Sheet are performed according to the settings for the file storage location and collection item value management.
※For examples of how the collection function handles data types, see "  ".

## About How Data Is Registered to the Parameter Sheet
The collection function registers and updates the values of the target files into the Parameter Sheet based on the registered setting values.

#### Operating Requirements of the Collection Function
The following settings must be configured in ITA.
- | In Parameter Sheet Definition/Creation, a Parameter Sheet (with host/operation) has been created
- | In Collection Item Value Management, the association between the work execution result (source file) and the Parameter Sheet items has been configured
- | The device (host name) targeted for collection is already registered in the Device List
After work execution, registration to the Parameter Sheet is performed if the following conditions are met.
- | The work execution completed successfully
- | The output result of the work execution has directories and files placed in the defined structure
Each user must prepare the IaC (Playbook, Role) that generates the source files used as the basis for registering into the Parameter Sheet.
Reference: Ansible Playbook Collection (OS Configuration Collection)
# Directory/File Structure and Variable Handling in the Collection Function
This chapter explains the directories, file structure, and variables handled by the collection function.

## Directory/File Structure Targeted for Collection
         - key: PermitRootLogin
         - key: PasswordAuthentication
Regarding the directory targeted for collection, the directory path targeted for collection (as the output destination of the source file) can be handled within the IaC (Playbook, Role) using the following variables.
.. list-table:: ITA-Specific Variables for the Directory Targeted by the Collection Function
- ITA-specific variable
     - Variable specification content
     - Remarks
- __parameter_dir__
     -  Converted to the path of "_parameters" under the work result directory.
     -
- __parameters_file_dir__
     -  Converted to the path of "_parameters_file" under the work result directory.
     -
- __parameters_dir_for_epc__
     -  Converted to the path of "_parameters" under the work directory.
     -
- __parameters_file_dir_for_epc__
     -  Converted to the path of "_parameters_file" under the work directory.
     -
-  _parameters           ※1
-  _parameters_file      ※4
-  test.txt      ※5
- | Remarks
※2 Host name (only hosts registered in the Device List are targeted for collection)
When creating the Playbook that generates the source file, if "" is not used for the output destination, the Playbook must be written to recognize the following structure.
- Mode
     - Mode-specific identifier
     - Directory hierarchy
     - Remarks
- Ansible-Legacy
     - legacy
     - /<parent directory (Ansible)>/legacy/
     -
- Ansible-Pioneer
     - pioneer
     - /<parent directory (Ansible)>/pioneer/
     -
- Ansible-LegacyRole
     - legacy_role
     - /<parent directory (Ansible)>/legacy_role/
     -
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters/localhost/SAMPLE.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters/localhost/OS/RH_snmpd.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/in/_parameters_file/localhost/TEST.txt
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters/localhost/SAMPLE.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters/localhost/OS/RH_snmpd.yml
     - /storage/Organization/Workspace/driver/ansible/legacy/00000000-0000-0000-0000-000000000001/out/_parameters_file/localhost/TEST.txt
If a Parameter Sheet with a file upload item is targeted for collection, the value (file name/file path) of the source file's variable and the corresponding file must be placed under _parameters_file.
For the settings of Collection Item Value Management, see "Collection Item Value Management".
The following methods are available for specifying an upload target file placed under _parameters_file.
.. list-table:: Methods for Specifying an Upload Target File
- Specification method
     - How to write it in the YAML file
     - Remarks
- File name specification
     - VAR_FILE_NAME : '<file name>'
     -
- File path specification (suffix match)
     - VAR_FILE_NAME : '/<levelX>/<file name>'
     -
     - VAR_FILE_NAME : '/<parent directory>/_parameters_file/localhost/<levelX>/<file name>'
     -
■ e.g.) Directory structure and source file content for a variable with a normal variable structure
-  _parameters
-  _parameters_file
-  config               ※Upload target file

## Variables Handled and Their Types
There are three types of variables that can be used within the source files handled by the collection function.
- | Normal variable
A variable for which a single concrete value can be defined per variable name.
- | Multiple-value variable
A variable for which multiple concrete values can be defined per variable name.
      - root
      - mysql
- | Multi-level variable
A hierarchically structured variable.
       - user-name: alice      #member variable
For the variable name, any of the following ASCII characters (0x20 to 0x7e), excluding the 7 characters below, may be used.
Note that there are several characters that cannot be used at the beginning of a variable name unless enclosed in quotation marks.
# Collection Function Menu Structure
This chapter explains the menu structure of the collection function.

## Menu/Screen List
1. Ansible Common menus
The list of Ansible Common menus is described below.
- No
     - Menu group
     - Description
- 1
     - Ansible Common
     - Collection Item Value Management
     - | Configures the association between the work execution output result (source file) and the Parameter Sheet items,
managing the target parameters registered by the collection function.
1. Ansible driver menus
The list of menus corresponding to each menu group of the Ansible driver is described below.
- No
     - Menu group
     - Description
- 1
     - Ansible-Legacy
     - Work Management
     - Manages the work execution history. View the registration status of the Parameter Sheet by the collection function and the execution log.
- 2
     - Ansible-LegacyRole
     - Work Management
     - Manages the work execution history. View the registration status of the Parameter Sheet by the collection function and the execution log.
- 3
     - Ansible-Pioneer
     - Work Management
     - Manages the work execution history. View the registration status of the Parameter Sheet by the collection function and the execution log.
# Procedure for Using the Collection Function
This section explains the procedure for using the collection function.

## Work Flow
The standard flow for carrying out the collection function is as follows.
For how to use ITA's Ansible-Driver, see "".
For how to use ITA's Basic Console, see "".

#### Collection Function Work Flow
The following is the flow from executing work in Ansible to collecting values into the Parameter Sheet.
-  Work flow details and references
1. Create the Parameter Sheet (with host/operation)
1. Register Collection Item Value Management
1. Prepare the work
1. Execute the work
Select the execution date/time, target operation, Movement, and workflow, and instruct execution of the process.
1. Execute the collection function
Registration to the Parameter Sheet is performed, targeting the work No. for which work execution has completed, as the target of the collection function.
1. Check the collection status
# Explanation of Collection Function Operations
This chapter explains the functions of the menus used by the collection function.
For details on how to register, see "" in the related manual.

## Ansible Common

#### Collection Item Value Management
1. In Collection Item Value Management, configure the association between the collection items and the Parameter Sheet items.
1. From List --> Register or Edit, register the collection items.
- Item: Collection item (From)
     - Description
     - Required
     - Constraints
- Parsing format
     - YAML: Parses a file in YAML format and generates parameters.
     - Yes
     - ※1
- PREFIX (file name)
     - Enter the file name without the extension.
     - Yes
     - ※1
- Variable name
     - | Enter the variable name to be collected.
For array or hash structures, entering the member variable is required.
     - Yes
     - ※1
- Member variable
     - Enter this if the variable is a multiple-value variable or multi-level variable.
     -
     - ※1
- Item: Parameter Sheet (To)
     - Description
     - Required
     - Constraints
- Menu Group:Menu:Item
     - | Select the item.
It is displayed with the menu group name, menu name, and item name joined by ":".
     -
     - ※2
※1 Examples of input values for the file name, variable, and member variable
※2 If multiple "PREFIX (file name) - Variable name" settings are configured for the same "Parameter Sheet (To) - Menu Group:Menu:Item", processing is performed in file order. For details, see "".
■e.g.) Case of a variable with a normal variable structure
   ■Value that can be entered as the collection item (FROM) in Collection Item Value Management
   Variable name: VAR_sample_config_1
■ e.g.) Case of a variable with a multiple-value structure 1
     - SAMPLE1
     - SAMPLE2
     - SAMPLE3
   ■Value that can be entered as the collection item (FROM) in Collection Item Value Management
   Variable name: VAR_sample2_conf
   Member variable:  [0]
■ e.g.) Case of a variable with a multiple-value structure 2
     - key: PermitRootLogin
     - key: PasswordAuthentication
    ■Value that can be entered as the collection item (FROM) in Collection Item Value Management
    Variable name: VAR_RH_sshd_config:
    Member variable:  [0].key
■e.g.) Case of a variable with a multiple-value structure 3
       - sec_name: "testsec"
       - sec_name: "local"
   ■Value that can be entered as the collection item (FROM) in Collection Item Value Management
   Variable name: VAR_RH_snmp_config:
   Member variable:  com2sec[0].sec_name

## Ansible-Legacy, Ansible-Pioneer, Ansible-LegacyRole

#### Checking the Collection Status
- Item
     - Description
     - Remarks
- Status
     - | Displays the execution status of the collection function
Not targeted: Not targeted by the collection function (no target file)
Collected: Collection function has been performed
Collected (with notification): There was a problem during registration/update
Collection error: There was a problem with the Movement's operation or host
     - ※
- Collection log
     - Downloads the log of the collection function execution
     -
- | Work status
     - Collection function target
     - Target file
     - | Collection status
     - Collection log
     - Remarks
- Other than completed
     - None
     - Not targeted
     - Blank
     - Blank
     -
- Other than completed
     - Present
     - Not targeted
     - Blank
     - Blank
     -
- Completed
     - None
     - Targeted
     - Not targeted
     - Log file present
     -
- Completed
     - Present
     - Targeted
     - Collected
     - Log file present
     -
- Completed
     - Present
     - Targeted
     - Collected (with notification)
     - Log file present
     -
- Completed
     - Present
     - Targeted
     - Collection error
     - Log file present
     -
If the work status is not "Completed," it is not targeted by the collection function, so the collection status is not updated and remains blank.
Even if registration processing fails due to a problem in Collection Item Value Management, the status becomes "Collected (with notification)." For details, see the example of log file output content below.
**Example of log file output content**

## BackYard Content
1. Overview of the registration process to the Parameter Sheet
1. Retrieves the list of work that completed successfully.
1. Retrieves the following information from the work No. targeted for collection.
- Operation information
- Target host
- Target source file
1. Checks whether the target host is registered in the Device List.
Registered: Targeted for collection
Not registered: Not targeted
1. Retrieves the menu ID of the target Parameter Sheet from the target source file and Collection Item Value Management.
1. Generates the parameters for registration/update from the information in steps 1 through 4.
Performs data verification against the target menu to determine whether to register or update.
Register: No unique data is registered for the operation/host combination
Update: Unique data is already registered for the operation/host combination
1. Registers/updates the data to the Parameter Sheet.
1. Updates the collection status status for the work No.
Note that the timing of data registration to the Parameter Sheet depends on the execution cycle of the Backyard process.
# Appendix

## Reference Materials
The following are reference examples of IaC (Playbook, Role).
1. Exastro Playbook Collection
1. Ansible config retrieval and parameter generation Playbook
       - name: make yaml file
      - name: get vconsole config
      - name: get yum config
When editing the "Header Section" of "Ansible-Legacy" - "Movement List", write the following.
For details on the configuration change, see "".
   - hosts: all

## Collection Execution Examples

#### Case Where the Same Menu Is Targeted by Multiple Files
This describes an example of the collection process when Collection Item Value Management has multiple "PREFIX (file name)-Variable name" settings configured for a single "Menu-Item," and multiple corresponding source files exist in the collection target directory of the target host.
-  _parameters
-  ita-sample01
-  SAMPLE_01.yml
-  SAMPLE_02.yml
**■ Collection Item Value Management setting**
- SAMPLE_01.yml
     - SAMPLE_02.yml
- | VAR_sample_config_1: 1
     - | VAR_sample_config_1: "A"
**■ Collection example of the Collection Item Value Management settings and the target menu item**
1. Collection Item Value Management settings and the target menu-item
   Collection Item Value Management settings and the Parameter Sheet
**■The collection process is executed per file, according to the target files and the Collection Item Value Management settings**
1. Registration process for SAMPLE_01.yml (register)
2. Registration process for SAMPLE_02.yml (update)
3. State of the record after the collection function completes

#### Handling of Values in the Collection Target File
For collection target files output in YAML format, the values are handled as follows when registered to the Parameter Sheet.
- No
     - Key
     - Value
     - Remarks
- 1
     - VAR_TEST
     - TEST
     -
- 2
     - VAR_STR_TEST1
     - 'TEST1'
     -
- 3
     - VAR_STR_TEST2
     - "TEST2"
     -
- 4
     - VAR_null
     - null
     -
- 5
     - VAR_NULL
     - NULL
     -
- 6
     - VAR_STR_null
     - "null"
     -
- 7
     - VAR_STR_NULL
     -  "NULL"
     -
- 8
     - VAR_true
     - true
     -
- 9
     - VAR_false
     - false
     -
- 10
     - VAR_STR_true
     -  "true"
     -
- 11
     - VAR_STR_false
     - "false"
     -
- 12
     - VAR_YES
     - YES
     -
- 13
     - VAR_NO
     - NO
     -
- 14
     - VAR_STR_YES
     - "YES"
     -
- 15
     - VAR_STR_NO
     - "NO"
     -
- 16
     - VAR_NON
     -
     -
- 17
     - VAR_Quotation
     - ``''``
     -
- 18
     - VAR_WQuotation
     - ``""``
     -
- 19
     - VAR_INT
     - 100
     -
- No
     - Collection target (key:value)
     - | Parameter Sheet
     - | REST API response
     - | REST API response
- 1
     - VAR_TEST: TEST
     - Parameter/VAR_TEST
     - "TEST"
     - string
     - TEST
- 2
     - VAR_STR_TEST1: 'TEST1'
     - Parameter/VAR_STR_TEST1
     - "TEST1"
     - string
     - TEST1
- 3
     - VAR_STR_TEST2: "TEST2"
     - Parameter/VAR_STR_TEST2
     - "TEST2"
     - string
     - TEST2
- 4
     - VAR_null: null
     - Parameter/VAR_null
     - null
     - null
     -
- 5
     - VAR_NULL: NULL
     - Parameter/VAR_NULL
     - null
     - null
     -
- 6
     - VAR_STR_null: "null"
     - Parameter/VAR_STR_null
     - "null"
     - string
     -  null
- 7
     - VAR_STR_NULL: "NULL"
     - Parameter/VAR_STR_NULL
     -  "NULL"
     -  string
     -  NULL
- 8
     - VAR_true: true
     - Parameter/VAR_true
     - "true"
     - string
     - true
- 9
     - VAR_false: false
     - Parameter/VAR_false
     - "false"
     - string
     - false
- 10
     - VAR_STR_true: "true"
     - Parameter/VAR_STR_true
     - "true"
     - string
     - true
- 11
     - VAR_STR_false: "false"
     - Parameter/VAR_STR_false
     - "false"
     - string
     - false
- 12
     - VAR_YES: YES
     - Parameter/VAR_YES
     - "true"
     - string
     - true
- 13
     - VAR_NO: NO
     - Parameter/VAR_NO
     - "false"
     - string
     - false
- 14
     - VAR_STR_YES: "YES"
     - Parameter/VAR_STR_YES
     - "YES"
     - string
     - YES
- 15
     - VAR_STR_NO: "NO"
     - Parameter/VAR_STR_NO
     - "NO"
     - string
     - NO
- 16
     - VAR_NON:
     - Parameter/VAR_NON
     - null
     - null
     -
- 17
     - VAR_Quotation: ''
     - Parameter/VAR_Quotation
     - ``""``
     - string
     -
- 18
     - VAR_WQuotation: ""
     - Parameter/VAR_WQuotation
     - ``""``
     - string
     -
- 19
     - VAR_INT: 100
     - Parameter/VAR_INT
     - "100"
     - string
     - 100
※The Parameter Sheet item is assumed to be a string (single line).
-  Retrieval result of the target Parameter Sheet via the REST API (filter)
                   "last_updated_user": "Collection Function",

#### Example of Specifying an Upload Target File When Multiple Files Have the Same File Name
-  _parameters
-  _parameters_file
-  APP001
-  config                   #①
-  APP002
-  config                   #②
-  APP003
-  config                   #③
-  APP002
-  config                   #④
- Collection item (FROM)/Variable name
     - Target file
     - Remarks
- VAR_upload_file_1
     - Randomly selected from files ①, ②, ③, ④
     -
- VAR_upload_file_2
     - Randomly selected from files ②, ④
     -
- VAR_upload_file_3
     - File ① is targeted
     -
- VAR_upload_file_4
     - File ④ is targeted
     -
     - File ② is targeted

#### Example of Description in a Collection Target File When Deleting a File
A file can be deleted by setting the value of the target variable name to an empty string.
-  _parameters
-  _parameters_file
