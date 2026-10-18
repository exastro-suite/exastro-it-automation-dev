# OASE: Building a bulk response configuration for a new monitoring event

When a user makes a request like "when XX (monitoring tool) reports YY (event type), make it handle it automatically", this describes the order in which to call the OASE menus to build the configuration end-to-end. For the details of each menu (required fields, mutually exclusive rules, JSON formats, etc.), do not rely on this document; use the `get-document` tool to look up the individual menu references (`event_collection.md`, `label_creation.md`, `labeling.md`, `filter.md`, `action.md`, `rule.md`).

## Creation order (dependencies exist, so follow this order)

```
1. event_collection  … Defines where events are retrieved from the monitoring tool
2. label_creation    … Defines the label keys to attach to events (can be done in parallel with 1)
3. labeling          … References 1 and 2; converts specific event field values into labels
4. filter            … Narrows down events using the label conditions created in 2
5. action            … Defines the response process, such as a Conductor execution (can be done in parallel with 1-4)
6. rule              … Ties the filter from 4 and the action from 5 together, fixing the behavior on a match
```

- `labeling` references both `event_collection` (collection settings ID) and `label_creation` (label key ID), so both must be created first.
- `rule` references both `filter` (filter_a/filter_b) and `action` (action_id), so it must always be created last.
- If an existing label, filter, or action already matches the requirement, reuse it instead of creating a new one (check existing records with the `menu-filter` tool).

## Tools used at each step

- Checking existing records: `menu-filter` (specify each REST name in `menu`)
- Checking pulldown candidates (Conductor name, host name, parameter sheet name, etc.): `list-menu-info-pulldown`
- Creating/updating: `maintenance-all`

## End-to-end example

Request: "When Zabbix reports a high load alert, automatically restart the service"

### Step 1: Collection settings (event_collection)
```json
{
  "menu": "event_collection",
  "records": [{
    "type": "Register",
    "parameter": {
      "event_collection_settings_name": "Zabbix monitoring event collection",
      "connection_method_name": "Bearer Authentication",
      "request_method_name": "GET",
      "url": "https://zabbix.example.com/api/events",
      "auth_token": "xxxxxxxx",
      "request_header": "{}",
      "parameter": "{}",
      "ttl": "3600"
    }
  }]
}
```

### Step 2: Label creation (label_creation)
```json
{
  "menu": "label_creation",
  "records": [{
    "type": "Register",
    "parameter": { "label_key_name": "event_type", "color_code": "#FF0000" }
  }]
}
```

### Step 3: Labeling — references the names created in Step 1 and Step 2
```json
{
  "menu": "labeling",
  "records": [{
    "type": "Register",
    "parameter": {
      "labeling_settings_name": "Event type label assignment",
      "event_collection_settings_name": "Zabbix monitoring event collection",
      "search_key_name": "alert.type",
      "type_name": "string",
      "comparison_method": "==",
      "search_value_name": "high load alert",
      "label_key_name": "event_type",
      "label_value_name": "high load alert"
    }
  }]
}
```

### Step 4: Filter — uses the label key created in Step 2 as a condition
```json
{
  "menu": "filter",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "filter_name": "High load alert filter",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"high load alert\"]]",
      "search_condition_id": "Unique"
    }
  }]
}
```

### Step 5: Action
```json
{
  "menu": "action",
  "records": [{
    "type": "Register",
    "parameter": {
      "action_name": "Restart service",
      "conductor_class_id": "Ansible Execution",
      "event_collaboration": "False",
      "host_id": "[H]web-server-01",
      "parameter_sheet_id": "Restart httpd"
    }
  }]
}
```

### Step 6: Rule — ties together the filter from Step 4 and the action from Step 5
```json
{
  "menu": "rule",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "rule_name": "High load alert response rule",
      "rule_label_name": "high_load_rule",
      "rule_priority": "1",
      "filter_a": "High load alert filter",
      "action_id": "Restart service",
      "conclusion_label_settings": "[]",
      "action_label_inheritance_flag": "True",
      "event_label_inheritance_flag": "False",
      "ttl": "3600"
    }
  }]
}
```

This completes the series of settings for "when Zabbix reports a high load alert, automatically restart the service". The execution results (judgement and action execution history) can be checked in the `evaluation_results` menu.
