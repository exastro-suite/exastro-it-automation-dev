# About API access (authentication)
For the endpoints, parameters, and details of the API you intend to use, please refer to the「」and「」for each user.
   - The language information from the last login is referenced.
   - Since settings have not been configured after the first login, an authentication error will occur.
# Examples of executing the registration/edit API and related APIs
Below are examples of executing the registration/edit API and related APIs.
- -  
How to check the menu name used in the API endpoint
   - Check the record of the relevant menu from「Admin Console --> Menu Management」and use the value of「Menu Name (rest)」.
Supplementary information on JSON data and FORM data used in parameters
Format and specification method when specifying parameters
Please respond appropriately according to the content type, the parameter specification method, the curl execution environment, etc.
    - Save the JSON data as a JSON file and specify the JSON file as the parameter
    - If a single quote「'」cannot be used in the JSON data, change the notation to use double quotes「"」instead, and escape any double quotes used internally
    - Change the trailing「\\」and「^」to whatever is appropriate for your environment
For details on how to specify parameters depending on the content type, refer to「」below.
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -H "Content-Type: application/json" \
       --data-raw [ { \"file\": { \"playbook_file\": \"LSBuYW1lOiBydW4gImVjaG8iCiAgY29tbWFuZDogZWNobyB7eyBWQVJfU1RSXzEgfX0=\" }, \"parameter\": { \"discard\": \"0\", \"item_no\": null, \"playbook_name\": \"echo\", \"playbook_file\": \"echo.yml\", \"remarks\": null, \"last_update_date_time\": null, \"last_updated_user\": null }, \"type\": \"Register\" } ]
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -H "Content-Type: application/json" \
       -d @playbook_files_sample.json
       -H "Authorization: Basic dXNlcl9pZDpwYXNzd29yZA==" \
       -F "json_parameters=[{\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}] " \
       -F "0.playbook_file=@echo.yml"

## List retrieval (Menu Filter: retrieving records)
    BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
      -H "Authorization: Basic ${BASE64_BASIC}" \
      -H "Authorization: Basic ${BASE64_BASIC}" \
      -H "Content-Type: application/json" \
      --data-raw "{\"discard\":{\"LIST\":[\"0\"]}}"
The search methods available for specifying conditions are described below.
- **Option**
       - **Description**
       - **Setting example**
       - **Constraints**
- NORMAL
       - | Performs a fuzzy search.
       - {"target key":{"NORMAL":"search condition"}}
       -
- LIST
       - | Performs an exact match search.
       - {"target key":{"LIST":["search condition"]}}
       -
- RANGE
       - | Performs a search using a range specification.
       - {"target key":{"RANGE":{"START":"search condition","END":"search condition"}}}
       -
Example of search parameters with specified conditions for the device list:
  - Not including discarded records
  - Host name contains "host"
  - Last update date/time is between "2023/01/01 00:00:00" and "2023/12/31 00:00:00"
   - | Refers to the logical deletion status of a record.
   - | The discard value of each record indicates the logical deletion status of that record.
- "0": Valid record
- "1": Discarded record
   - Records in a discarded state are not included in validation.
   - File data is output as a base64-encoded string. Please base64-decode it as needed for use.
   - Some items, such as passwords, are stored in encrypted form.
   - Values output by the list retrieval API will be null, and the registered values will not be output.
※For items stored in encrypted form, please refer to the manual for each menu.

## Registration/edit (Menu Maintenance: bulk operation of All records)
The following Content-Types can be selected as the parameter specification method for the registration/edit API.
- application/json format
  - Parameters are sent as JSON data.
  - File data is written within the parameters as a base64 string and sent.
- multipart/form-data format
  - Parameters and files are sent as form data.
  - The key for the file's form data is constructed by connecting the index of the parameter's JSON data and the target key with a ".".
The following samples use Basic authentication to call the record operation APIs for「Ansible Common --> Device List」and「Ansible-Legacy --> Playbook Material Collection」.
- About validation during registration/edit
   - For validation of each item, please refer to the manual for each menu.

### Differences in parameter structure by Content-Type
The following explains the parameter structure for each Content-Type.
For how to obtain and check the target keys used in parameters, refer to「」.
- Content-Type: application/json
- Content-Type: multipart/form-data
Examples of parameters for registration and update are described below.
- Sample registration for「Ansible-Legacy --> Playbook Material Collection」
- Sample update for「Ansible-Legacy --> Playbook Material Collection」
   - For last_update_date_time, use the value of the latest corresponding record obtained via FILTER.
   - If it does not match the latest value, the record will not be updated.
   - | How to register/update a file
Specify the value to register or update in the designated key under parameter and file.
   - | How to change a file name
   - | How to delete a file
   - | How to register/update a file
Specify the value to register or update in the designated key under parameter.
   - | How to change a file name
   - | How to delete a file
   - Change only the value of the target item to be changed under parameter, and update without specifying a file under file or via -F and without including the key of the target item.
   - For pulldown items, refer to the information obtainable via「 」for the target and available values.

### Ansible Common - Device List
   BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -H "Content-Type: application/json" \
     --data-raw "[{ \"file\": {\"ssh_private_key_file\": \"\", \"server_certificate\": \"\"}, \"parameter\": { \"authentication_method\": \"Password authentication\", \"connection_options\": null, \"connection_type\": \"machine\", \"discard\": \"0\", \"host_dns_name\": null, \"host_name\": \"exastro-test\", \"hw_device_type\": null, \"instance_group_name\": null, \"inventory_file_additional_option\": null, \"ip_address\": \"127.0.0.1\", \"lang\": \"utf-8\", \"login_password\": \"password\", \"login_user\": \"root\", \"os_type\": null, \"passphrase\": null, \"port_no\": null, \"protocol\": \"ssh\", \"remarks\": null, \"server_certificate\": null, \"ssh_private_key_file\": null }} ]"
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -F 'json_parameters="[ { "parameter": { "discard": "0", "managed_system_item_number": null, "hw_device_type": null, "host_name": "exastro-test", "host_dns_name": null, "ip_address": "127.0.0.1", "login_user": "root", "login_password": "asdfghjkl", "ssh_private_key_file": "ssh_key_file.pem", "authentication_method": "Password authentication","port_no": null, "server_certificate": "certificate_file.crt", "protocol": "ssh", "os_type": null, "lang": "utf-8", "connection_options": null, "inventory_file_additional_option": null, "instance_group_name": null,"connection_type": "machine", "remarks": null,"last_update_date_time": null, "last_updated_user": null}, "type": "Register" }]"' \
     -F '0.ssh_private_key_file=@/ssh_key_file.pem' \
     -F '0.server_certificate=@/certificate_file.crt' \

### Ansible-Legacy - Playbook Material Collection
   BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
     -H "Authorization: Basic ${BASE64_BASIC}" \
     -H "Content-Type: application/json" \
     --data-raw "[{\"file\":{\"playbook_file\":\"LSBuYW1lOiBydW4gImVjaG8iCiAgY29tbWFuZDogZWNobyB7eyBWQVJfU1RSXzEgfX0=\"},\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}]"
    -H "Authorization: Basic ${BASE64_BASIC}" \
    -F "json_parameters=[{\"parameter\":{\"discard\":\"0\",\"item_no\":null,\"playbook_name\":\"echo\",\"playbook_file\":\"echo.yml\",\"remarks\":null,\"last_update_date_time\":null,\"last_updated_user\":null},\"type\":\"Register\"}] " \
    -F "0.playbook_file=@echo.yml"

## API parameter-related information (Menu Info: retrieving menu information)
About creating parameters for bulk record operations
For the structure of parameters and items for bulk record operations, refer to the following.
- -  

### Menu information
You can retrieve the menu's configuration information, column groups, and setting values for the columns used in.
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/
     MENU="target menu"
     BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
                     "column_name_rest": "", # Item name specified in the API parameter
About menu item information and setting values related to bulk record operation parameters
Keys and setting values of the item information (column_info) returned by the menu information retrieval API
    .. list-table:: Keys and setting values of menu item information
- **Key**
         - **Description**
         - **Setting value**
- column_name
         - String
- column_name_rest
         - Item name specified in the API parameter
         - String
- auto_input
         - | Auto-input flag
         - | "0": Not applicable
- input_item
         - | Input target flag
Input target item when executing the registration/edit API
         - | "0": Not applicable
- view_item
         - | Output target flag
         - | "0": Not applicable
- required_item
         - | Required input flag
Required input item when executing the registration/edit API
         - | "0": Not applicable
- unique_item
         - | Unique constraint flag
Unique constraint target item when executing the registration/edit API
         - | "0": Not applicable
※For validation, please refer to the manual for each menu.

### Parameter item information
You can retrieve the parameter information used in.
If you want to check more detailed settings, also refer to.
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/column/
     MENU="target menu"
     BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
  - | Example: Response for "Playbook Material Collection"
             "playbook_file": "Playbook material",
             "playbook_name": "Playbook material name",

### List of available values for pulldown items
- | /api/{organization_id}/workspaces/{workspace_id}/ita/menu/{menu}/info/pulldown/
     MENU="target menu"
     BASE64_BASIC=$(echo -n "Set your username:Set your password" | base64)
       -H "Authorization: Basic ${BASE64_BASIC}" \
  - | Example: Response for "Device List"
# Parameter Apply (API)
This API performs everything from operation generation to parameter application, and executes the Conductor work. It does not, however, confirm the completion of the Conductor work execution. Please check completion from Conductor --> Conductor Work History.

## Request format
- Item
     - Description
- API category
     - Apply
- API name
     - Parameter Apply
- URL
     - /api/{organizaiton_id}/workspaces/{workspace_id}/ita/apply/
- method
     - POST
- headers
     - | content-type: application/json
- Request body
     - | Please refer to Request body.

## Request body
conductor_class_name                   | Conductor name            | ○    | String           | | Specify the Conductor name requesting the work execution.                                                                                 |
|                  | | For Conductor name, specify a Conductor name registered in Conductor --> Conductor List.|
|                  | | An error occurs if you specify a Conductor name that is not registered in Conductor --> Conductor List.              |
operation_name                         | Operation name       |      | String           | | Specify the operation name for the work to be executed.                                                                                |
|                  | + | Existing operation                                                                                                        |
|                  |   | Specify an operation name registered in Basic Console --> Operation List.|
|                  | + | New operation                                                                                                        |
|                  |   | An operation name not registered in Basic Console --> Operation List \           |
|                  |   | The specified operation_name will be registered in Basic Console --> Operation List.                      |
|                  | + | Automatic operation numbering                                                                                                    |
|                  |   | If operation_name is not specified or is omitted, an operation name is assigned using the following numbering rule and\            |
|                  |     registered in Basic Console --> Operation List.                                                 |
schedule_date                          | Scheduled date/time               |      | String           | | Specify the scheduled date/time for the Conductor work execution in yyyy/mm/dd hh:mi:ss format.                                                            |
parameter_info                         | Parameter information         |      | Array             | | Specify the parameter information for performing register/update/discard/restore operations.                                                                 |
|                  | | If multiple menus are targeted and order needs to be considered, adjust using the order of the array.                                          |
|                  | | Omit this if you are only executing the Conductor work.                                                                           |
※1             | (menu_name_rest)      | Menu name (REST)       |      | Array             | | Specify the Menu Name (Rest) from Admin Console --> Menu Management.                      |
|                        |      |                  | | For registration: Register                                                                                                       |
parameter    | Parameter             |      | Dictionary             | | Specify the combination of column keys and values for the target menu.                                                                      |
|                        |      |                  | | If "New operation" or "Automatic operation numbering" is specified for operation_name, the value corresponding to the operation name\               |
|                        |      |                  | | Also, if a Conductor name that includes a Conductor call function (hereinafter referred to as a sub-Conductor) is specified for conductor_class_name\    |
|                        |      |                  |   and it is necessary to explicitly specify an individual operation of the sub-Conductor, specify the corresponding operation name.                 |

## Specific examples of Request body

### Conductor work execution using registered parameters with an existing operation

### Conductor scheduled execution using registered parameters with an existing operation

### Conductor work execution with parameter application on an existing operation
About specifying the operation "operation_name_select"
For an existing operation, the value to set for the operation "operation_name_select" is specified as "Scheduled Date" (YYYY/MM/DD hh:mm)_"Operation Name" of the relevant operation.

### Conductor work execution with parameter application on a new operation
About specifying the operation "operation_name_select"
For a new operation, specifying the operation "operation_name_select" is not required.

### Conductor scheduled execution with parameter application using automatic operation numbering
About specifying the operation "operation_name_select"
For automatic operation numbering, specifying the operation "operation_name_select" is not required.

### Conductor work execution with parameter application for multiple records across multiple menus

### Conductor work execution with parameter application by explicitly specifying an individual operation of a sub-Conductor

## response body
     Example of an error occurring due to an invalid character count in the value specified for key: column_1 of the 1st record (0-origin) of menu name (REST): sample_menu_001 specified in the Request body
             "1": {                                                                                    The record number of the menu name (REST) is displayed starting from 0.
                "column_1": [ "Character length error (threshold: value<=8byte, value: 30byte), menu : sample_menu_001"]  Key: REST name of the item that caused the error, Value: error content, menu: menu name (REST) that caused the error

## Points to note
This API can apply parameters to menus that are updatable in ITA.

### Applying parameters to a host group
When parameters are applied to "Host Group Management", the Conductor work execution is performed in a state where host analysis for the specified host group has not been processed.
For applying parameters to "Host Group Management", please register in advance using the record operation API below.

### Applying parameters to menus subject to variable extraction
When parameters are applied to a menu subject to variable extraction, the Conductor work execution is performed in a state where the variables used within the specified parameters have not been extracted.
For applying parameters to menus subject to variable extraction, please register in advance using the record operation API below.
For menus subject to variable extraction, see「 -> 」\

### Rollback on error
