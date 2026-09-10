# Ansible Legacy Default Playbook - Net_Tools_Basics_uri_get-workspaces_using_oauth.yml
This playbook describes the playbooks initially registered in Exastro's playbook_list.
## Exastro Registration Info
- **item_no**: 20
- **playbook_name**: ~[Exastro standard] API call/OAuth authentication
- **playbook_file**: Net_Tools_Basics_uri_get-workspaces_using_oauth.yml
## Overview
Uses the `uri` module to obtain an OAuth access token via a refresh-token grant, then calls a workspaces REST API using that token as a Bearer credential.
## Description
This playbook performs OAuth-based authentication followed by an authenticated API call.
- `ITA_DFLT_Organization_ID`: The organization/realm identifier, used to build both the token endpoint URL and the workspaces API endpoint URL, and included as part of the OAuth `client_id`.
- `ITA_DFLT_Refresh_Token`: The OAuth refresh token submitted to the authentication server to obtain a new access token.
- `ITA_DFLT_Response`: The variable that stores the token endpoint's response; its `json.access_token` field is used as the Bearer token for the subsequent workspaces API call.
## Keyword
- OAuth 2.0
- REST API integration
- identity provider
- token endpoint
## Playbook
```yaml
- name: Get access token
  uri:
    url: "http://platform-auth:8000/auth/realms/{{ ITA_DFLT_Organization_ID }}/protocol/openid-connect/token"
    method: POST
    body_format: form-urlencoded
    body:
      client_id: "_{{ ITA_DFLT_Organization_ID }}-api"
      grant_type: "refresh_token"
      refresh_token: "{{ ITA_DFLT_Refresh_Token }}"
  register: ITA_DFLT_Response

- name: Interacts with webservices
  uri:
    url: "http://platform-auth:8000/api/{{ ITA_DFLT_Organization_ID }}/platform/workspaces" 
    headers:
      Accept: "application/json"
      Authorization: "Bearer {{ ITA_DFLT_Response.json.access_token }}"
      Content-Type: "application/json"
    status_code: 200
    method: GET
  register: ITA_DFLT_API_Response
```
