# OASE Management
# Introduction
This document explains the features and operation methods of OASE Management.
# Agent Overview

## About the Agent
The agent is independent of Exastro IT Automation (hereinafter, ITA) and functions as an intermediary between ITA OASE and external services.
The agent retrieves the event collection settings for the target external service from ITA, and uses those settings to obtain events from the external service. Through this process, the obtained events are sent to ITA.
# Agent Usage Procedure
This chapter explains the usage procedure for the agent (Exastro OASE Agent).

## Work Flow
-  **Work Flow Details and References**
1. **Event Collection Settings**
1. **Label Settings**
1. **Installing and Starting the Agent**
# Notification Template (Common) Overview
The following is an overview of the event types used by the OASE notification feature and their operational specifications.
# Notification Template (Common) Usage Procedure
The work flow required to use the OASE notification feature is as follows.
-  **Work Flow Details and References**
1. **Maintaining (Viewing/Updating) the Notification Template (Common)**
1. **Registering Notification Destination Settings**
Log in to the Exastro system as an organization administrator and register from Notification Management in the menu.
1. **(For Email Notification Destinations Only) Configuring the Mail Sending Server**
Log in to the Exastro system as an organization administrator and register from Mail Sending Server Settings in the menu.
# Menu Structure
This chapter explains the menu structure used in OASE Management.

## Menu/Screen List
The list of menus for OASE Management is described below.
1      | OASE Management     | Event Collection    | Manages information on event collection targets.   |
2      |                      | Notification Template (Common) | Manages information used in OASE notifications. |
# Feature Menu Operation Instructions
This chapter explains the menu operation instructions for the OASE Management feature.

## About the Menu
This section describes the operation of the menus displayed once OASE Management is installed.

## Event Collection
1. In OASE Management --> Event Collection, you can maintain (view/register/update/decommission) the connection method, authentication method, TTL, etc. of the event collection targets (configured on the agent).
-*Item**                           | **Description**                                               | **Required** | **Input Method** | **Constraints**    |
Event collection setting name                 | Enter an arbitrary event collection setting name.                 | Yes           | Automatic entry     | Maximum length 255 bytes |
Connection method                           | Select the connection method to the event collection target.             | Yes           | List selection   | *2              |
- Reserved variables can be used in Jinja2 format.                 |              |              |                 |
For details of the available reserved variables, see\                          |              |              |                 |
- Reserved variables can be used in Jinja2 format.                 |              |              |                 |
For details of the available reserved variables, see\                          |              |              |                 |
Parameters                         | - Enter in JSON format.                               | -           | Manual entry     | Maximum length 255 bytes |
- Reserved variables can be used in Jinja2 format.                 |              |              |                 |
Query parameters (values after the "?" appended to the destination)\    |              |              |                 |
- For details of the available reserved variables, see\                          |              |              |                 |
*1 This is a setting for the event collection target.
- Connection method
     - Request method
     - Authentication information
- IMAP password authentication
     - - IMAP: Plaintext
     - | - Username
- Bearer authentication
     - | - GET
     - - Authentication token
- Password authentication
     - | - GET
     - | - Username
- Arbitrary authentication
     - | - GET
     - - Described in parameters

## Notification Template (Common)
1. In OASE Management --> Notification Template (Common), you can maintain (view/register/update/decommission) the templates used by the OASE notification feature.
Change the content of the default notification template or add items according to the notification method being used (  ).
When using a notification method other than email, adjusting the format of the notification template is required.
- Item
     - Description
     - Required
     - Input Method
     - Constraints
- Event type
     - | Select the event type for which the template is used.
     - Yes
     - List selection
     - -
- Template
     - | You can edit the template used for notifications.
     - Yes
     - Manual entry
     - Maximum size 2MB
- Notification destination
     - | Select the notification destination for which the template is used.
A notification destination cannot be set for the default template.
     - -
     - List selection
     - -
- Default
     - For an event type, the default template is used when sending to a notification destination that has no record.
     - -
     - -
     - -
- Remarks
     - A free-text field.
     - -
     - Manual entry
     - Maximum length 4000 bytes
The default settings for the template are as follows.
    When configuring notification settings using a Jinja2 template, please note the following points.
    - Definition of required elements: The template **must** contain the **[TITLE]** and **[BODY]** elements that define the notification title and body.
    - Notification failure due to missing syntax: If a required element ([TITLE] or [BODY]) is missing, or if there is an error in how an element is written, the notification execution **will fail**.
    - Where to edit: When changing the output content, edit **only the inside of the [TITLE] and [BODY] elements**. Do not delete or change these elements themselves.
    - Reference for Jinja2 syntax: For details on the variables and control syntax used within the template, refer to the official Jinja2 documentation.
# Appendix

## Processing Flow of the OASE Agent and .env Configuration Values
- Processing flow of the OASE Agent
- Some of the configuration values set in .env when installing the OASE Agent
- Parameter
   - Description
- AGENT_NAME
   - Used as the name of the OASE Agent to be started and as the file name of the internal database.
- EXASTRO_URL
   - Used as the request destination when making API requests to ITA.
- EXASTRO_ORGANIZATION_ID
   - Used to identify the organization when making API requests to ITA.
- EXASTRO_WORKSPACE_ID
   - | Used to identify the workspace when making API requests to ITA.
This must be a workspace linked to the organization set in EXASTRO_ORGANIZATION_ID.
- EXASTRO_REFRESH_TOKEN
   - | Used as the authentication token for Bearer authentication when making API requests to ITA.
※The user's role must be able to maintain the OASE - Event - Event History menu.
- EXASTRO_USERNAME
   - | Used as the username for Basic authentication when making API requests to ITA.
※The user's role must be able to maintain the OASE - Event - Event History menu.
- EXASTRO_PASSWORD
   - | Used as the password for Basic authentication when making API requests to ITA.
- EVENT_COLLECTION_SETTINGS_NAMES
   - Based on the values set in this parameter, event collection settings are retrieved from ITA and a configuration file is generated.
- ITERATION
- EXECUTE_INTERVAL

## Immediate Application of Event Collection Settings
This section describes how to have changes to event collection settings applied immediately to the OASE Agent.
1. Delete the configuration file "event_collection_settings.json".
If the configuration file "event_collection_settings.json" does not exist, the OASE Agent retrieves the event collection settings from ITA and creates the configuration file.
Deleting the configuration file allows the latest settings to be applied.
※If this operation is not performed, the changed settings will not be applied until the loop process, repeated the number of times indicated by "ITERATION" shown in  , has finished.

## About the Agent's Decoding Process

### Verified Character Encodings
-*Sending Method**             | **Mail Header**                                                        |
-*Format**  | **Language**     | **Content-Transfer-Encoding** | **Content-Type**                          |

## Response Key and Event ID Key

### Response Key
- Monitoring software has a feature that allows alerts and metrics (states) issued on the monitored machine to be obtained via an HTTP API,

### JMESPath
Regarding how to specify JMESPath,

### Response List Flag

### Event ID Key
- Item name
   - Configuration value
- Response key
   - :program:`value`
- Response list flag
   - :program:`True`
The following settings are appropriate for OASE Management --> Event Collection.
- Item name
   - Configuration value
- Response key
   - :program:`value`
- Response list flag
   - :program:`True`
- Event ID key
   - :program:`id`
   .. list-table:: Incorrect Event ID Key Setting
- Item name
        - Configuration value
- Response key
        - :program:`value`
- Response list flag
        - :program:`True`
- Event ID key
        - :program:`value[].id`

## Event Collection Setting Examples by Monitoring Software
This section describes configuration examples for OASE Management --> Event Collection when using the representative monitoring software :dfn:`Zabbix` and :dfn:`Grafana` for event collection.
Next, the cURL parameters are explained in the order in which they are set in OASE Management --> Event Collection.
Check the HTTP API specifications of the version you are using, and configure OASE Management --> Event Collection accordingly.

### Zabbix
This section describes a configuration example for OASE Management --> Event Collection to retrieve events from :dfn:`Zabbix`.
   --url http://<Zabbix IP Address or Domain>/zabbix/api_jsonrpc.php \
   --header 'content-type: application/json-rpc' \
   --data "{\"jsonrpc\": \"2.0\",\"method\": \"problem.get\",\"id\": 1,\"params\": {},\"auth\": \"<Zabbix API token>"}"
(Details of the <Zabbix API token> in the command/parameters are described later.)
1. Example event collection settings for retrieving events from :dfn:`Zabbix`
Based on the cURL command above, the OASE Management --> Event Collection setting values for performing an equivalent retrieval are configured as follows.
.. list-table:: Zabbix Configuration Example
- Item name
     - Configuration value
- Event collection name
     - <A name indicating Zabbix failure retrieval>
- Connection method
     - Arbitrary authentication
- Request method
     - POST
- Connection destination
     - | http://<Zabbix IP Address or Domain>/zabbix/api_jsonrpc.php
- Request header
- Parameters
- Response key
     - result
- Response list flag
     - True
- Event ID key
     - eventid
The <Zabbix API token> configured in Parameters is authentication information for a Zabbix user,
  1. | In a browser, sign in to :dfn:`Zabbix` as an administrator
The default administrator login information is,
  2. | Select side menu > Users > Users
     --url http://<Zabbix IP Address or Domain>/zabbix/api_jsonrpc.php \
     --header "Content-Type: application/json-rpc" \
     --data "{\"auth\":null,\"method\":\"user.login\",\"id\":1,\"params\":{\"user\":\"<username>\",\"password\":\"<password>\"},\"jsonrpc\":\"2.0\"}" \
Paste the <Zabbix API token> into the <Zabbix API token> field of Parameters in OASE Management --> Event Collection.
After logging in via the browser, you can create it from :guilabel:`Create API token` under side menu > User settings > API tokens.

### Grafana
This section describes a configuration example for OASE Management --> Event Collection to retrieve events with :dfn:`Grafana`.
   --url 'http://<Grafana IP address or Domain>:3000/api/prometheus/grafana/api/v1/alerts' \
   --header 'authorization: Bearer <authentication token>' \
   --header 'Content-Type: application/json'
(Details of the <authentication token> in the command/parameters are described later.)
1. Example event collection settings for retrieving events from :dfn:`Grafana`
Based on the cURL command above, the OASE Management --> Event Collection setting values for performing an equivalent retrieval are configured as follows.
.. list-table:: Grafana Configuration Example
- Item name
     - Configuration value
- Event collection name
     - <A name indicating Grafana alert retrieval>
- Connection method
     - Bearer authentication
- Request method
     - GET
- Connection destination
     - | http://<Grafana IP address or Domain>:3000/api/prometheus/grafana/api/v1/rules
- Request header
- Authentication token
     - <authentication token>
- Response key
     - data.alerts
- Response list flag
     - True
- Event ID key
     - activeAt
This can be obtained using the following procedure.
By default,
  9. | Paste the authentication token from the clipboard into the Authentication Token field in OASE Management --> Event Collection.

## List of Available Reserved Variables
In OASE Management --> Event Collection, reserved variables can be used in the following items.
- :dfn:`Connection destination`
- :dfn:`Request header`
- :dfn:`Parameters`

### Reserved Variables
- Variable name
     - Description
     - Output example
- EXASTRO_LAST_FETCHED_TIMESTAMP
     - Date and time of the previous retrieval (UNIX timestamp)
     - 1704817434
- EXASTRO_LAST_FETCHED_DD_MM_YY
     - Date and time of the previous retrieval (DD/MM/YY HH:MM:SS format)
     - 10/01/24 01:23:45
- EXASTRO_LAST_FETCHED_YY_MM_DD
     - Date and time of the previous retrieval (YYYY/MM/DD HH:MM:SS format)
     - 2024/01/10 01:23:45
- EXASTRO_LAST_FETCHED_EVENT_IS_EXIST
     - Flag indicating whether the previously retrieved event exists
     - True, False
- EXASTRO_LAST_FETCHED_EVENT
     - Object containing the raw data of the previously retrieved event
     - | (Example: for Zabbix)
For usage, see  
- EXASTRO_EVENT_COLLECTION_SETTING
     - Object containing the items of the event collection setting
     - See  
- EXASTRO_LAST_FETCHED_TIME
     - | Date and time of the previous retrieval (YYYY-MM-DD HH:MM:SS format)
     - 2025-09-19 10:45:34
- EXASTRO_CURRENT_TIME
     - | Current time (YYYY-MM-DD HH:MM:SS format)
     - 2025-09-19 10:45:34
-*〇Usage example**
An example of retrieving the clock item from this data and setting it as a parameter of the Zabbix API's event.get method is shown below.
The information registered in   can be referenced as reserved variables.
Below is a list of the available items and their corresponding variable names.
- Item name
     - Variable name.attribute
- Event collection setting name
     - EXASTRO_EVENT_COLLECTION_SETTING.EVENT_COLLECTION_SETTINGS_NAME
- Connection destination
     - EXASTRO_EVENT_COLLECTION_SETTING.URL
- Port
     - EXASTRO_EVENT_COLLECTION_SETTING.PORT
- Request header
     - EXASTRO_EVENT_COLLECTION_SETTING.REQUEST_HEADER
- Proxy
     - EXASTRO_EVENT_COLLECTION_SETTING.PROXY
- Authentication token
     - EXASTRO_EVENT_COLLECTION_SETTING.AUTH_TOKEN
- Username
     - EXASTRO_EVENT_COLLECTION_SETTING.USERNAME
- Password
     - EXASTRO_EVENT_COLLECTION_SETTING.PASSWORD
- Mailbox name
     - EXASTRO_EVENT_COLLECTION_SETTING.MAILBOXNAME
- Parameters
     - EXASTRO_EVENT_COLLECTION_SETTING.PARAMETER
- Response key
     - EXASTRO_EVENT_COLLECTION_SETTING.RESPONSE_KEY
- Response list flag
     - EXASTRO_EVENT_COLLECTION_SETTING.RESPONSE_LIST_FLAG
- Event ID key
     - EXASTRO_EVENT_COLLECTION_SETTING.EVENT_ID_KEY
- TTL
     - EXASTRO_EVENT_COLLECTION_SETTING.TTL

### Configuration Examples
Examples of using reserved variables in each configuration location are shown below.
Embed the authentication token in the connection destination URL and pass it as a URL parameter.
Example of use in Parameters
1. **Specifying the current date/time or the previous retrieval date/time as a filter condition during event collection**
1. **Use with Zabbix Integration**
   - If a previously retrieved event exists: retrieve events after the previously retrieved event ID
   - If no previously retrieved event exists: retrieve events on or after the previous retrieval time

## Notification Template (Common) Configuration Examples

### Configuration Items (For ServiceNow (Record Registration))
This section explains the TITLE and BODY when ServiceNow (Record Registration) is selected as the notification method in Notification Template (Common).
When ServiceNow (Record Registration) is selected as the notification method, the content written in TITLE is not used.
When ServiceNow (Record Registration) is selected as the notification method, the BODY must be written in the format of the request body used when registering a record via the ServiceNow REST API.
- The template examples are merely examples. Please customize them as appropriate for your actual operations.
- | Regarding the parameters to use, refer to the manual and REST API reference for the ServiceNow application you are using.
  - Refer to the `ServiceNow Table API Manual <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html>`_
  - REST API Explorer
    - `https://<instance-name>.service-now.com/$restapi.do`
    -  For how to use the REST API Explorer, refer to the `ServiceNow manual <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/task/t_GetStartedAccessExplorer.html>`_

### Configuration Example for ServiceNow (Record Registration)
An example configuration of the Notification Template (Common) for performing ServiceNow (Record Registration) is shown below.
A configuration example for registering a record in the ServiceNow incident table
Here, based on the content of the default template, an example is shown in which the content of TITLE is set to ServiceNow's short_description, and the content of Event Raw Data and Agent are set in BODY to ServiceNow's description.
The content of Event Raw Data (raw_event_data) and Agent (exastro_agents) is set dynamically using loop processing in the Jinja template.
- | 1. Example template for New Event (on receipt): New(received).j2
- | 1. Example notification for New Event (on receipt)
- | 2. Example template for New Event (on consolidation): New(consolidated).j2
- | 2. Example notification for New Event (on consolidation)
When ServiceNow (Record Registration) is selected as the notification method, the content written in TITLE is not used.
When ServiceNow (Record Registration) is selected as the notification method, the content written in BODY is used as the request body.
For this reason, BODY must be written in the format of the request body used when registering a record via the ServiceNow REST API.
   - The template examples are merely examples. Please customize them as appropriate for your actual operations.
   - Regarding the parameters to use, refer to the manual and REST API reference for the ServiceNow application you are using.
     - Refer to the `ServiceNow Table API Manual <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html>`_
     - REST API Explorer
       - `https://<instance-name>.service-now.com/$restapi.do`
       -  For how to use the REST API Explorer, refer to the `ServiceNow manual <https://www.servicenow.com/docs/ja-JP/bundle/washingtondc-api-reference/page/integrate/inbound-rest/task/t_GetStartedAccessExplorer.html>`_
