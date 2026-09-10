# CI/CD For IaC Function
-*******
This document describes the functions and operation methods of the CI/CD For IaC function.
Definition of Terms
-*********
Represents the materials within a Git repository linked via the IaC function.     |
From the following menus of "Terraform-CLI-Driver"\            |
- Ansible-Legacy/Playbook Material Collection                        |
- Ansible-LegacyRole/Role Package Management              |
- Ansible Common/File Management                             |
- Ansible Common/Template Management                         |
- Terraform-Cloud-EP/Policy Management                        |
Overview of the CI/CD For IaC Function
-**********************
# Function Overview
The CI/CD For IaC function is broadly divided into two functions.
1. Git Linkage Function
Detects updates to the linked source material periodically via a clone, and creates a list in ITA's "Remote Repository Material" menu.
1. Material Linkage Function
Registers the linkage between the linked source material and the linked destination material, and registers an operation and Movement for verifying the operation of the linked destination material.
When the linked source material is updated, the linked destination material is automatically updated, and work is executed using the operation and Movement for verifying the operation.
# Function Overview Diagram
CI/CD For IaC Function Menu Structure
-*****************************
This chapter describes the menu structure of the CI/CD For IaC function.
# Menu/Screen List
The list of menus for the CI/CD For IaC function is described below.
 Table 2.1-1 CI/CD For IaC Function Menu List
-*No** | **Menu\     | **Menu\       | **Overview**      |
Repository  | Manages the information  |
| Manages the material information  |
| Menu\   |
| Manages the linkage information\ |
CI/CD For IaC Function Usage Procedure
-*************************
This section describes the usage procedure for the CI/CD For IaC function.
# Work Flow
The standard work flow for the CI/CD For IaC function is as follows.
-*Work Flow Details and References**
1. Registering the Remote Repository
Register the information of the Git repository to be linked.
For details, refer to the "" menu.
1. Registering the Material Linkage
Register the linkage between the linked source material and the linked destination material.
For details, refer to the "" menu.
1. Registering the Operation+Movement Information in the Material Linkage
Register an operation and Movement when verifying the operation of the updated linked destination material.
For details, refer to the "" menu.
1. Confirming the Automatic Material Update and Operation Verification
Also, when an operation and Movement are registered, confirm that work is executed automatically.
For details, refer to the "" menu.
CI/CD For IaC Function Menu Operation Description
-********************************
This chapter describes the menu operations of the CI/CD For IaC function.
# CI/CD For IaC Menu
This section describes the operation of the menus displayed when the CI/CD For IaC function is installed.

## Remote Repository
1. In the "Remote Repository" menu, register the information of the Git repository to be linked.
-*Item**      | **Description**                         | **Required\  | **Input\         | **Constraints\           |
Remote\     | In each menu of the CI/CD For IaC function,\| Yes       | Manual       | Max length 255 bytes |
Framework\| set in the key file used\  |          |               |                 |
Parameter\  | Enter the parameter to set in\ |          |               |                 |
      | the environment variable "GIT_SSH_COMMAND".     |          |               |                 |
The environment variable available in this version\|          |               |                 |
If it is older, the configured parameter\|          |               |                 |
The environment variable "GIT_SSH_COMMAND" is\   |          |               |                 |
set with the following parameter by\|          |               |                 |
The configured parameter is added after this\|          |               |                 |
If hCommand is not configured, the following\|          |               |                 |
parameter is set.         |          |               |                 |
If mand is configured, include the\ |          |               |                 |
following parameter.       |          |               |                 |
Configured for connectivity to the Git\ server\ |          |               |                 |
Configured for connectivity to the Git server\|          |               |                 |
- Item
        - Description
        - Remarks
- Status
        - | Displays the synchronization status with the Git repository using the following four states.
Blank: The state when a record has been newly registered, updated, or restored from discontinuation
        -
- Detailed Information
        - | If the status becomes abnormal, the cause of the abnormality is displayed.
        -
- Last Date/Time
        - | Displays the date and time the last synchronization with the Git repository was performed.
        -
        -

## Material Linkage
1. In the "Material Linkage" menu, link the linked source material with the linked destination material, and register an operation and Movement for verifying the operation of the linked destination material.
When the linked source material is updated, the linked destination material is automatically updated by an internal function, work is executed using the operation and Movement for verifying the operation, and the processing result is displayed.
-*Item**      | **Description**                                          | **Required\  | **Input\         | **Constraints\           |
Linked destination material name  | The material name registered in the linked destination material\                 | Yes       | Manual      | Max length 255 bytes |
is linked to the item of the following menu, based on\                 |          |               |                 |
input rules equivalent to the item of each menu\                 |          |               |                 |
Menu name           | Item name            |      |          |               |                 |
/Role Package Management|                   |      |          |               |                 |
Ansible Common/File\ | File-embedded variable\ |      |          |               |                 |
Management               | name                |      |          |               |                 |
Ansible Common/Template\ | Template-embedded variable name |      |          |               |                 |
Management           |                   |      |          |               |                 |
Policy Management          |                   |      |          |               |                 |
Depending on conditions such as whether the material name entered in the linked destination material name\ is registered or not\ |          |               |                 |
Gi\| Material path\| "" menu\| Yes       | List select    |                 |
t\ |          | The material path of the Remote Repository registered\   |          |               |                 |
t\+          | in the "Role Package Management" menu, sets "Abnormal" in the "Material Synchronization Information/Status" item and the error cause in the "Material Synchronization Information/Detailed Information" item of the "cicd_for_iac_file_link`" menu.
※5 Sets "Abnormal" in the "Material Synchronization Information/Status" item of the "" menu, and the error cause in the "Delivery Information/Detailed Information" item.
※6 Sets "Normal" in the "Material Synchronization Information/Status" item of the "" menu.
# CI/CD For IaC Hidden Menus
This section describes the operation of the menus not displayed when the CI/CD For IaC function is installed.
To access each menu, restore each menu in "Management Console/Role-Menu Association Management" to make it appear.

## Remote Repository Material
1. The "Remote Repository Material" menu displays a list of linked source materials.
The information displayed in the "Remote Repository Material" menu is updated by an internal function.
-*Item**      | **Description**      | **Required\| **Input\    | **Constraints**  |
registered in\ |        |            |               |
the y`" menu\ |        |            |               |
configured\ |        |            |               |
-***
# Notes on Registering Materials to a Git Repository
The notes on registering materials to a Git repository are described below.
1. If a Git repository containing a material name of 256 bytes or more is registered in the "" menu, the Git clone command will terminate abnormally.
1. If a Git repository containing a material name of 4096 bytes or more, including the file path, is registered in the "" menu, the Git clone command will terminate abnormally.
# Notes on Registering Materials Linked to Role Package Management to a Git Repository
The notes on registering materials linked to the "Ansible-LegacyRole/Role Package Management" menu to a Git repository are described below.
1. Create a directory that contains a directory named roles, and place the files and directories required for the role package under this directory.
The material that is packaged as a zip for the role package is under the parent directory of the roles directory. However, even if a directory named roles is created directly under the root directory of the Git repository, it is not recognized as a roles directory linked to the "Ansible-LegacyRole/Role Package Management" menu.
-  roles          ......... Not recognized as a roles directory.
- sample
- roles       ......... Recognized as a roles directory.
- test_role
- defaults
- tasks
"sample/roles" is displayed in the material path of the "" menu. For the material path to link to the "Ansible-LegacyRole/Role Package Management" menu, select "sample/roles".
