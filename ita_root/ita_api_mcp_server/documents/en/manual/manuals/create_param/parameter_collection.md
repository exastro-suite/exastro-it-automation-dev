# Parameter Collection
# Introduction
This document describes the functions and operation methods of the ITA Parameter Collection.
# Overview of the Parameter Collection
This chapter describes the functions and operation methods of the Parameter Collection.

## Details of the Parameter Collection

### About the function
The Parameter Collection allows you to retrieve multiple parameter sheets created with the Parameter Sheet Creation menu based on search conditions, or to register data to a parameter sheet.
# Parameter Collection Menus and Screen Layout

## List of menus
The menus of the Parameter Collection are shown below.
.. list-table:: List of ITA menus
- No
     - Description
- 1
     - Parameter Collection
     - You can retrieve multiple already-created parameter sheets based on search conditions, or register data to a parameter sheet.
# Function and Operation Description

## Displaying parameters
Retrieves parameter sheets based on search conditions.
   Initial display of the Parameter Collection
(1) ① Select the parameter mode.
The list of parameter modes is shown below.
.. list-table:: List of parameter modes
- Name
     - Description
- Host
     - Selects a single host associated with the parameter sheet, and retrieves data for multiple operations of the parameter sheet based on that host.
- Operation
     - Selects a single operation associated with the parameter sheet, and retrieves data for multiple hosts of the parameter sheet based on that operation.
(2) ② Select the operation.
Select the operation from the operation timeline.
When the parameter mode is Host, select one or more operations.
When the parameter mode is Operation, select only one operation.
(3) ③ Select the target parameters.
Only parameter sheets for which the "Association" item is set to "Maintainable" or "View only" in the Role/Menu Association Management menu can be selected.
For parameter sheets that use host groups, select the parameter sheet for automatic assignment value registration.
The selected parameter sheets can be reordered by dragging.
When the parameter mode is Host, select only one target host (including "No host") from the selected hosts.
When the parameter mode is Operation, the selected hosts become the retrieval targets, and you choose whether to include "No host" as a retrieval target.
Only hosts registered in the parameter sheet can be selected.
(5) ⑤ Execute the parameter display.
When the parameter mode is Host, the value of each item of the parameter sheet is displayed for each operation.
When the parameter mode is Operation, the value of each item of the parameter sheet is displayed for each host.
The display order matches the order of the target parameters.
When the parameter mode is Operation, the display order of hosts matches the order of the target hosts (with "No host" displayed last).
Under the following search conditions, the parameter display is executed automatically.
① When the parameter mode and target parameters are already selected, and a target host is selected
② When the parameter mode and target host are already selected, and a target parameter is selected
③ When the parameter mode is Operation, and the target parameters and target host are already selected, and the operation is changed
   Executing the parameter display when the parameter mode is Host
   Executing the parameter display when the parameter mode is Operation

## Parameter item display direction settings
(1) You can select the display direction of the parameter sheet items.
   Parameter item display direction settings

## Preset registration
(1) You can register search conditions as a preset.
Registered presets can be updated, renamed, and deleted.
Presets are registered per workspace.
   Preset registration

## Operation timeline display settings
(1) You can show or hide the operation timeline.

## Parameter sheet maintenance (register/update/discontinue/restore)
(1) You can maintain (register/update/discontinue/restore) the data of the parameter sheet.
Users for whom the "Association" item is set to "View only" in the Role/Menu Association Management menu cannot edit.
For parameter sheets that use host groups, the parameter sheet for input is displayed.

## Printing the parameter display execution results
(1) You can print the parameter display execution results.
After executing the parameter display, click the Print tab.
Depending on the parameter display execution results, the content may be cut off horizontally.

## Exporting the parameter display execution results to Excel
(1) You can export the parameter display execution results to Excel.
After executing the parameter display, click the Excel Download tab.
Each parameter sheet is output as a separate sheet.
The sheets are output in the order in which the parameter display results are shown.
# Appendix

## When the parameter display execution results are cut off horizontally
   The parameter display execution results are cut off horizontally
   1.  Click :guilabel:`Detailed Settings`.
   1.  Click :guilabel:`Detailed Settings`.
   1.  Click :guilabel:`Detailed Settings`.
