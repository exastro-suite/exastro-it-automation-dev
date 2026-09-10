# Menu Export/Import
# Introduction
This document describes the functions and operation methods of Menu Export/Import in ITA.
# Overview of Menu Export/Import
This chapter describes Menu Export/Import.

## Details of Menu Export/Import

### About the Function
Menu Export/Import lets you select the ITA menus you want to migrate, and migrates the data by overwriting it, menu by menu.

### About Modes
The Menu Export function has two types of modes.
Exports all data for the specified menus. All data at the import destination is replaced.

### Usage Examples
This function is intended to be used as follows, using two environments, Workspace A and Workspace B.
-*Pattern ①: Duplicating an environment**
Duplicates all data registered in Workspace A into Workspace B.
[Procedure]
#. Export all of Workspace A's data using Environment Migration mode.
#. Import the data exported in step 1 into Workspace B.
※After environment migration, data can be registered/updated in Workspace B. Migrating data from Workspace A again afterward may cause inconsistencies, so this is not recommended.
-*Pattern ②: Separating the workspace where data is entered from the workspace where work is executed**
[Procedure]
#. Export all of Workspace A's data using Environment Migration mode.
#. Import the file exported in step 1 into Workspace B.
#. Every time data is updated in Workspace A, migrate the differential data to Workspace B using Time-Specified mode.
※If multiple data migrations are expected, registering/updating data in Workspace B may cause data inconsistencies, so this is not recommended. There is no impact if Workspace B is used only for executing work.

### About Resource Limitations During Menu Export/Import Processing
Resources during Menu Export/Import are controlled using the Resource Plan.
For configuration and how to apply it, refer to "  ".
About resource control during Menu Export/Import processing
 In accordance with the Resource Plan values, the input/output of the backend processing for Menu Export/Import is split and processed to control resources.
 Raising the Resource Plan setting value below shortens the processing time, but increases the amount of resources used.
 - ita.organization.menu_export_import.buffer_size
# Availability of Export/Import Depending on the Environment

## About Environment Differences (ITA Version and Installed Drivers)
- Case
     - Environment A version
     - Environment A driver
     - Environment B version
     - Environment B driver
     - | Environment difference
     - | Environment A → Environment B
     - Remarks
- A
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - No environment difference
     - 〇
     -
- B
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - Driver difference exists
     - 〇
     -
- C
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.Y
     - | CI/CD for IaC
     - Version difference exists
     - 〇
     -
- D
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.Y
     - | CI/CD for IaC
     - | Version difference exists (A:2.5.X < B:2.5.Y)
     - 〇
     -
- E
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - Driver difference exists
     - △※
     -
- F
     - 2.5.X
     - | CI/CD for IaC
     - 2.5.Y
     - | CI/CD for IaC
     - | Version difference exists (A:2.5.X < B:2.5.Y)
     - △※
     -
- G
     - 2.5.Y
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - | Version difference exists (A:2.5.Y > B:2.5.X)
     - ×
     -
- H
     - 2.5.Y
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - | Version difference exists (A:2.5.Y > B:2.5.X)
     - ×
     -
- I
     - 2.5.Y
     - | CI/CD for IaC
     - 2.5.X
     - | CI/CD for IaC
     - | Version difference exists (A:2.5.Y > B:2.5.X)
     - ×
     -
Using the driver install/uninstall function (  ),
Using the driver install/uninstall function (  ),
# Menus and Screen Configuration of Menu Export/Import

## Menu List
The menus of Menu Export/Import are shown below.
 ITA Menu List
1      | Export/Impo\| Menu Expo\| Menu dat\  |
2      |                      | Menu Import | Menu\      |
3      |                      | Menu Expo\| [Menu Ex\ |
port/Import Management | port] menu\ |
| port] menu, and man\ |
| the status of impo\  |
# Function and Operation Method Description

## Menu Export
Exports the data registered in the ITA system, menu by menu.
If you are moving data to a different ITA environment, data consistency may be broken unless all menus are included in the move.
Some menus are not eligible for export. The menus that are not eligible are as follows.
1      | Export/Import | Menu Export                                  |
2      |                          | Menu Import                                    |
3      |                          | Menu Export/Import Management                  |
6      |                          | Excel Bulk Export/Import Management                |
7      | Conductor                | Conductor Edit/Execute Work                                |
8      |                          | Conductor Work History                                     |
9      |                          | Conductor Work Confirmation                                     |
10     |                          | Conductor Instance List                             |
11     |                          | Conductor Node Instance List                         |
12     | Parameter Sheet Creation     | Parameter Sheet Definition/Creation                            |
13     |                          | Parameter Sheet Creation History                              |
18     |                          | Substitution Value Management                                            |
21     |                          | Work Management                                              |
23     |                          | Substitution Value Management                                            |
26     |                          | Work Management                                              |
28     |                          | Substitution Value Management                                            |
31     |                          | Work Management                                              |
35     |                          | Substitution Value Management                                            |
36     |                          | Linked Terraform Management                                   |
39     |                          | Work Management                                              |
40     |                          | Substitution Value Management                                            |
-*Name** | **Description**                                                 |
Inserts/overwrites based on the menu's unique item (ID, No., etc.). |
-*Name**   | **Description**                                                   |
- No.
     - Description
- 1
     - With History
     - Exports including history records.
- 2
     - Without History
     - Exports without including history records.
When performing an initial environment migration, or when a menu has been newly created using Parameter Sheet Creation, make sure to include the following menus in the export target.
- Menu Management
- Menu-Table Association Management
- Menu-Column Association Management
- Role-Menu Association Management

## Menu Import
Imports the data exported from the [Menu Export] menu.
The menus whose checkbox is checked are subject to import.
For menus that do not need to be imported, uncheck the checkbox.
(4) You are automatically taken to [Menu Export/Import Management], where you can check the import status.

## Menu Export/Import Management
Manages the status of exports executed from the [Menu Export] menu and imports executed from the [Menu Import] menu.
-*Item**   | **Description**                                                                                                     |
Process Type   | | Export ... Menu Export                                                                     |
Import ... Menu Import                                                                         |
Cannot be edited because it is automatically registered.                                                                         |
In Menu Export/Import Management, when Status becomes "Completed (Error)", a link to the file is displayed in Execution Log.
