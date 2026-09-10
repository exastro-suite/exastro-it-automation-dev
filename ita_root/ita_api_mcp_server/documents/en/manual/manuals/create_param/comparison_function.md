# Comparison Function
# Comparison Function Overview
This document describes the ITA comparison function and its operation methods.

### About the comparison function
The comparison function is a function that compares parameter sheets created with the ITA parameter sheet creation function and outputs the differences.
This function targets "parameter sheets (with host/operation)".
For details about parameter sheets, refer to "".
-*****************
-*****************
The comparison result is output according to the comparison settings, comparison detailed settings, and the conditions specified at execution time.
-*****************
For details about the comparison settings and comparison detailed settings, refer to "".
- Association of parameter sheets (when the items of the parameter sheets being compared match)
   When the items of the parameter sheets being compared match
- Association of parameter sheets (when the items of the parameter sheets being compared do not match)
   When the items of the parameter sheets being compared do not match

### About the reference date and time
The reference date and time is the "Last Execution Date/Time" if the relevant operation has ever been executed in the past, or the "Scheduled Execution Date/Time" if it has never been executed.
The following is an example of search results when a search is performed in the "For Reference" menu group using ①–③ as the reference date and time.
① As of 1/1, no value has been set, so there are no search results. "None"
② As of 3/15, the value set in Operation 1 is displayed in the search results. "Parameter A: 100"
③ As of 5/15, the value set in Operation 4 is displayed in the search results. "Parameter A: 200"

### About parameter sheet comparison
The comparison function performs a value comparison based on the item information of the target parameter sheets associated in the comparison settings and comparison detailed settings.
Requirements for executing the comparison function
-*****************
The following settings must be configured in ITA.
- | The parameter sheet (with host/operation) has been created in Parameter Sheet Definition/Creation.
- | The association between the parameter sheets to be compared has been configured in Comparison Settings.
- | The association between the items to be compared has been configured in Comparison Detailed Settings.
Comparison Detailed Settings can only be configured when the Detailed Settings Flag is set to "True" in Comparison Settings.
If the number of items and item names of the parameter sheets being compared match (Detailed Settings Flag is "False"), configuring Comparison Detailed Settings is not required.
Comparison execution parameters
-*****************
You can execute a comparison by setting the following parameters.
For Comparison Settings, refer to "" below.
.. list-table:: Comparison execution parameters
- | Parameter
     - | Description
     - | Required
     - | Input format
     - | Constraints
- | Comparison settings selection
     - | Select the comparison settings.
     - | ○
     - | List selection
     - |
- | Reference date/time 1
     - | Of the parameter sheet selected as Target Parameter Sheet 1 in the comparison settings,
     - |
     - | Manual input
     - | If not entered, the latest reference date/time is applied.
- | Reference date/time 2
     - | Of the parameter sheet selected as Target Parameter Sheet 2 in the comparison settings,
     - |
     - | Manual input
     - | If not entered, the latest reference date/time is applied.
- | Host selection
     - | Select the target host.
     - |
     - | List selection
     - |
# Target Items in the Comparison Function

### Comparison target items
Items of the parameter sheets to be compared
-*******************************
The following are the parameter sheet items that can be used with the comparison function.
.. list-table:: Parameter sheet comparison target items
- | Item type
     - | Constraints
- | String \(single line\)
     - |
- | String \(multiple lines\)
     - |
- | Integer
     - |
- | Decimal
     - |
- | Date and time
     - |
- | Date
     - |
- | Pulldown selection
     - | Comparison is performed using the value of the selected list.
- | File upload
     - | When comparing file uploads with each other, the comparison is performed
- | Link
     - |
- | Parameter sheet reference
     - | Comparison is performed using the value of the referenced parameter sheet.
-***********************************
This is a list of combinations of parameter sheet items that can be compared.
- |
     - | String
     - | String
     - | Integer
     - | Decimal
     - | Date and time
     - | Date
     - | Pulldown
     - | File
     - | Link
     - | Parameter sheet
- | String
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | String
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | Integer
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | Decimal
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | Pulldown
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | File
     - | ○※1
     - | ○※1
     - | ○※1
     - | ○※1
     - | ○※1
     - | ○※1
     - | ○※1
     - | ○
     - | ○※1
     - | ○※1
- | Link
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
- | Parameter sheet
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○
     - | ○※1
     - | ○
     - | ○
# Comparison Function Menu Structure
This chapter describes the menu structure of the comparison function.

### Menu/screen list
The list of comparison menus is described below.
   List of comparison menus
- | No
     - | Menu group
     - | Description
- | 1
     - | Comparison
     - | Comparison Settings
     - | Creates the name of the settings used to execute a comparison.
Associates the target parameter sheets to be compared.
Setting the Detailed Settings Flag to "True" enables the configuration of Comparison Detailed Settings.
- | 2
     - | Comparison
     - | Comparison Detailed Settings
     - | For the items of the parameter sheets being compared,
configures the association at the individual parameter sheet item level.
- | 3
     - | Comparison
     - | Comparison Execution
     - | Based on the settings configured in Comparison Settings and Comparison Detailed Settings,
performs the comparison.
# Comparison Function Usage Procedure
This section describes the procedure for using the comparison function.

### Work flow
The standard flow for performing the comparison function is as follows.
Comparison function execution flow
-***********************
The following is the flow up to executing a comparison of parameter sheets.
- Work flow details and references
1. Creating a parameter sheet
1. Registering data to the parameter sheet
Register data to the parameter sheet created in "Creating a parameter sheet".
1. Creating the comparison settings
1. Configuring the comparison detailed settings
1. Executing the comparison
# Comparison Function Operation Description
This chapter describes each menu used in the comparison function.

### Comparison
Comparison Settings
-*******
1.  In Comparison Settings, you register and update the settings information (association of the target parameter sheets) used when executing a comparison.
1. Register Comparison Settings from List --> Register or Edit.
.. list-table:: List of Comparison Settings items
- | Item
     - | Description
     - | Required
     - | Input format
     - | Constraints
- | Comparison name
     - | Enter the comparison name.
     - | ○
     - | Manual input
     - | Maximum length is 255 bytes.
- | Target parameter sheet 1
     - | Select the target parameter sheet.
     - | ○
     - | List selection
     - |
- | Target parameter sheet 2
     - | Select the target parameter sheet.
     - | ○
     - | List selection
     - |
- | Detailed settings flag
     - | Whether the item names and number of items of Target Parameter Sheet 1 and Target Parameter Sheet 2
\ False: Comparison Detailed Settings is not required.
\ True: Comparison Detailed Settings is required.
     - | -
     - | Selection
     - | ※1
- | Remarks
     - | This is a free-text field.
     - | -
     - | Manual input
     - |
※1  If the Detailed Settings Flag is "False", configuring Comparison Detailed Settings is not required. The number of items and item names of the selected parameter sheets must match exactly.
Comparison Detailed Settings
-***********
1.  In Comparison Detailed Settings, you configure the association between the comparison target item names and the parameter sheet items.
1. Register comparison items from List --> Register or Edit.
- | Item
     - | Description
     - | Required
     - | Input format
     - | Constraints
- | Comparison name
     - | Select the comparison settings
     - | ○
     - | List selection
     - | ※1
- | Comparison item name
     - | Enter the item name to display.
     - | ○
     - | Manual input
     - | Maximum length is 255 bytes.
- | Target item 1
     - | Select the target item.
     - | ○
     - | List selection
     - | ※2
- | Target item 2
     - | Select the target item.
     - | ○
     - | List selection
     - | ※3
- | Display order
     - | Enter the display order.
     - | ○
     - |
     - | The input range is 0 to 2,147,483,647.
- | Remarks
     - | This is a free-text field.
     - | -
     - |
     - |
※1  Items for which the Detailed Settings Flag is set to "True" in Comparison Settings are displayed in the list.
※2  Select an item that belongs to Target Parameter Sheet 1 registered in Comparison Settings.
※3  Select an item that belongs to Target Parameter Sheet 2 registered in Comparison Settings.
-*******
Comparison Execution compares parameter sheets based on the definition information configured in Comparison Settings and Comparison Detailed Settings.
- The list of Comparison Names registered in Comparison Settings is displayed.
- When comparing parameter sheets that use bundles, the comparison is performed between items with the same item name, or between items with the same assignment order that are associated in Comparison Detailed Settings.
- | Parameter
     - | Description
     - | Required
     - | Input format
     - | Constraints
- | Comparison settings selection
     - | Select the comparison settings.
     - | ○
     - | List selection
     - |
- | Reference date/time 1
     - | Of the parameter sheet selected as Target Parameter Sheet 1 in the comparison settings,
     - |
     - | Manual input
     - | If not entered, the latest reference date/time is applied.
- | Reference date/time 2
     - | Of the parameter sheet selected as Target Parameter Sheet 2 in the comparison settings,
     - |
     - | Manual input
     - | If not entered, the latest reference date/time is applied.
- | Host selection
     - | Select the target host.
     - | -
     - | List selection
     - | -
※2 By default, hosts are not narrowed down. The comparison results for all hosts in the target parameter sheets associated within the comparison settings are output.
- | Comparison of parameter sheets
- | Comparison of parameter sheets (when using bundles)
- | Comparison of parameter sheets (file upload items)
         - | You can view the differences in content between text-based files.
         - | You cannot view the differences in content between files that contain binary data.
- | Target host
- | Item
     - | Description
     - | Constraints
- | Target host
     - | Displays the target host name.
     - |
- | Difference
     - | Displays the comparison execution result. If there is a difference, it is displayed with a "✓".
     - |
- | Comparison result
- | Item
     - | Description
     - | Constraints
- | Item
     - | Displays the item name.
     -
- | Difference
     - | Displays the comparison result of the item.
     - | If there is a difference, it is displayed with a "✓".
- | Comparison target parameter sheet 1
     - | Displays the value of comparison target parameter sheet 1.
     - | The parameter sheet name is displayed in the header.
- | Comparison target parameter sheet 2
     - | Displays the value of comparison target parameter sheet 2.
     - | The parameter sheet name is displayed in the header.
- | Remarks
     - | Displayed when there is other information when each item is compared.
         - | Comparison items are displayed in the format item name[assignment order].
         - | Comparison is performed between items with the same item name, or between items with the same assignment order that are associated in Comparison Detailed Settings.
         - | No., Host name, Operation name, and Reference date/time are not displayed.
