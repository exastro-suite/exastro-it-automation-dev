# Ansible Legacy Default Playbook - Net_Tools_Basics_uri_get-workspaces_using_basic.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 10
- **playbook_name**: ~[Exastro standard] API call/Basic authentication
- **playbook_file**: Net_Tools_Basics_uri_get-workspaces_using_basic.yml
## Overview
Sends an HTTP GET request to the Exastro platform-auth workspaces API using HTTP Basic authentication and registers the JSON response for later use.
## Description
"ITA_DFLT_Organization_ID": the organization ID used to build the target API URL path.
"ITA_DFLT_Basic_Username": the username used for HTTP Basic authentication against the API.
"ITA_DFLT_Basic_Password": the password used for HTTP Basic authentication against the API.
The task expects an HTTP 200 response and stores the result in the `ITA_DFLT_API_Response` register variable for use by subsequent tasks.
## Keyword
- REST API call
- connectivity check
- workspace list retrieval
- authentication test
- uri module
## Playbook
```yaml
- name: Interacts with webservices using password
  uri:
    url: "http://platform-auth:8000/api/{{ ITA_DFLT_Organization_ID }}/platform/workspaces"
    force_basic_auth: yes
    user: "{{ ITA_DFLT_Basic_Username }}"
    password: "{{ ITA_DFLT_Basic_Password }}"
    status_code: 200
    method: GET
  register: ITA_DFLT_API_Response
```
