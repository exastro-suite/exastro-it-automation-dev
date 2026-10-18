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

## Duplicating / extending an existing rule for another host

Procedure for a request such as "create the same configuration as <existing rule name> for <host name> as well".

### Step 0: read the existing configuration first

Use `menu-filter` to retrieve the target rule and, following its references, the `filter` / `action`, and further the `labeling` / `label_creation` / `event_collection`. **Determine which menus can be reused and which must be newly created before making a proposal.**

### Step 1: decide whether duplication is needed at all (important)

**If the requirement is merely "respond on the host where the event occurred", there is no need to duplicate per host.** Setting `event_collaboration` to `True` on the `action` makes the event's originating host (fixed label `_exastro_host`) the execution target directly, so **a single set of settings covers all hosts**.

Therefore, present the following two options and let the user choose with `ask_user_choice`.

| Option | Content | Suited for |
|---|---|---|
| Option A: consolidate with event collaboration | Update the existing action to `event_collaboration: True` (leave `host_id` unspecified). No additional filter or rule is needed | The response is common across hosts and you do not want to add settings as hosts increase |
| Option B: duplicate per host | Add one set of `filter` / `action` / `rule` for the new host | You want different response content or parameter sheets per host |

### Step 2 (for Option B): separate what is reused from what is newly created

| Menu | Handling when duplicating |
|---|---|
| `event_collection` | **Reuse.** No addition needed if fetching from the same monitoring tool |
| `label_creation` | **Reuse.** Label keys can be shared |
| `labeling` | **Reuse as a rule.** However, if there is no setting that assigns `_exastro_host`, **a new one is required** (see Step 3-2 below) |
| `filter` | **Must be newly created** (see the reason below) |
| `action` | **Newly create**, with `host_id` set to the new host |
| `rule` | **Newly create**, linking the new filter and the new action |

### Step 3 (for Option B): why the filter must not be reused (important)

- `action.host_id` only specifies "**which host the Conductor is executed against**" and **has no effect on which events match**.
- Consequently, if an existing filter is shared by two rules as-is, **both rules fire on events from every host**, so the response runs even on unrelated hosts (and if `rule_priority` is identical, the behaviour becomes indeterminate).
- The correct approach is to **create a new filter whose `filter_condition_json` includes a condition on the fixed label `_exastro_host`**.
- **In addition, add an `_exastro_host` condition to the original filter as well (`Update`).** Forgetting this leaves the original rule picking up events from the new host too, so the discrimination does not take effect. Because this update changes the behaviour of an existing setting, always include it in the proposal and obtain the user's approval.
- Note that two filters with exactly the same conditions cannot be created (`Identical filter conditions cannot be specified.` / 499-00201). Changing only the name will not register, so the conditions themselves must differ.
- The unique constraint of a rule is also `filter_a` + `filter_operator` + `filter_b`, so **two rules using the same filter cannot be created either** (`The combination is incorrect.` / MSG-00006). Creating a new filter is unavoidable.

### Step 3-2 (both options): check whether a `labeling` setting assigns `_exastro_host` (important)

- `_exastro_host` is a fixed label, but **its value is not set automatically**. A `labeling` setting that copies the host name field of the event into `_exastro_host` is required.
- If the `labeling` records fetched in Step 0 contain no record whose `label_key_name` is `_exastro_host`, **include creating one in your proposal**. Without it:
  - Option B: a filter with an `_exastro_host` condition will never match
  - Option A: even with `event_collaboration: True`, the execution target host cannot be determined
- For the form that covers every host with a single record (specify only `search_key_name`, pass the rest as `null`), see `filter.md` via `get-document`. Never try to create `_exastro_host` in `label_creation` (names starting with `_exastro_` violate the `label_key_name` regular expression and fail).
- The event-side field name given in `search_key_name` depends on the actual event structure, so if you guessed it, say so explicitly and confirm with the user.

### Step 4 (for Option B): concrete call examples

Existing: rule `CPU alert response rule` -> filter `High load alert filter` (no host condition) -> action (`host_id: [H]web-server-01`)
Request: create the same for `web-server-02`

**4-0. [Required before any write] Determine first whether Option B is even possible**

Actions have a unique constraint, and **older versions only look at the three columns `operation_id` + `conductor_class_id` + `event_collaboration`** (`host_name` is not included). Consequently, "an action with the same Conductor as the existing one, differing only in host" cannot be registered and fails with `The combination is incorrect.` (499-00201).

**Before writing a single record**, retrieve the existing actions with `menu-filter` (`menu: "action"`) and determine the following.

- If the existing action is in "direct Conductor execution mode" (`operation_id` is `null`) and has the same `conductor_class_id` as the action you are about to create -> **Option B cannot be executed as-is.**
  - At this point, explain the situation to the user and let them choose with `ask_user_choice` among the following. **Settle this before writing, rather than fixing it after a failure.**
    1. **Switch to Option A** (update the existing action to `event_collaboration: True`; do not add a filter or rule) ... the simplest. Per-host filters and rules become unnecessary too
    2. **Create it in operation execution mode** (create a new operation for the host in `operation_list` and specify `operation_id` on the action; do not specify `host_id` / `parameter_sheet_id`)
        - If you create a new operation, retrieve `documents-menu/operation_list.md` with `get-document` beforehand (`scheduled_date_for_execution` is required; omitting it fails with `{"scheduled_date_for_execution": ["Required fields."]}`)
    3. **Use a different Conductor** (only when you actually want different response content)
  - **Important** If option 1 is chosen, neither creating a new filter nor updating the existing filter is **necessary**. Creating the filter first causes rework (having to discard it later), so **do not start writing until this determination is made**.
- If there is no conflict (the existing action is in operation execution mode, or you will use a different Conductor) -> proceed with 4-1 onward as written.

**Also, `Update` / `Discard` must always include the `last_update_date_time` obtained from the immediately preceding `menu-filter`.** This value changes on every update, so **re-fetch it with `menu-filter` each time when writing to the same record consecutively**. Using a stale value fails with `Processing was canceled because the record was updated from another session.`, and omitting it fails with `last_update_date_time is invalid (None)`.

**Furthermore, on an `Update` the validation is evaluated using only the values passed in this request** (values on the existing record are not filled in automatically). Therefore **pass every column, including the ones you are not changing**. Passing just one column fails, for example, with `Duplicate filters are selected.` on `rule` (because `filter_a` is treated as unspecified) or `If an Host/Event cooperation or Host/Host name is selected, necessary to set the usage Parameter Sheet Name.` on `action` (both 499-00201).

**4-1. Add a host condition to the existing filter (Update)**
```json
{
  "menu": "filter",
  "records": [{
    "type": "Update",
    "parameter": {
      "filter_id": "<existing filter_id>",
      "last_update_date_time": "<the value retrieved with menu-filter, as-is>",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"high load alert\"], [\"_exastro_host\", \"==\", \"web-server-01\"]]"
    }
  }]
}
```

**4-2. Create a filter for the new host**
```json
{
  "menu": "filter",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "filter_name": "High load alert filter (web-server-02)",
      "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"high load alert\"], [\"_exastro_host\", \"==\", \"web-server-02\"]]",
      "search_condition_id": "Unique"
    }
  }]
}
```
The value for `_exastro_host` is **the host name only** (do not add the `[H]` prefix).

**4-3. Create an action for the new host**

**Note** On older versions the action's unique constraint only looks at the three columns `operation_id` + `conductor_class_id` + `event_collaboration`, so **an action that uses the same Conductor as the existing action and differs only in host cannot be registered** (`The combination is incorrect.` / 499-00201). If the call below fails, switch to one of the workarounds in the "Unique constraint on actions" section of `action.md` (consolidate with event collaboration / switch to operation execution mode / use a different Conductor).
```json
{
  "menu": "action",
  "records": [{
    "type": "Register",
    "parameter": {
      "action_name": "Restart service (web-server-02)",
      "conductor_class_id": "<same Conductor as the existing action>",
      "event_collaboration": "False",
      "host_id": "[H]web-server-02",
      "parameter_sheet_id": "<same parameter sheet as the existing action>"
    }
  }]
}
```

**4-4. Create a rule for the new host**
```json
{
  "menu": "rule",
  "records": [{
    "type": "Register",
    "parameter": {
      "available_flag": "True",
      "rule_name": "CPU alert response rule (web-server-02)",
      "rule_label_name": "high_load_rule_web_server_02",
      "rule_priority": "1",
      "filter_a": "High load alert filter (web-server-02)",
      "action_id": "Restart service (web-server-02)",
      "conclusion_label_settings": "[]",
      "action_label_inheritance_flag": "True",
      "event_label_inheritance_flag": "False",
      "ttl": "3600"
    }
  }]
}
```
- `rule_label_name` must not duplicate the existing rule's value (it cannot be changed after registration).
- Because the filters are mutually exclusive via `_exastro_host`, the two rules can never match the same event simultaneously. Therefore `rule_priority` may keep the same value as the existing rule.

### Checklist when duplicating

Self-check all of the following before presenting a proposal.

1. **Before performing a single write**, was the action unique-constraint pre-check of Step 4-0 completed with `menu-filter` (determining whether Option B is possible)?
2. Does the new filter's `filter_condition_json` include `_exastro_host == <new host name>`?
3. **Does the proposal include an `Update` that adds `_exastro_host == <original host name>` to the existing filter as well?**
4. Is the new rule's `rule_label_name` free of duplication with existing rules?
5. Does the proposal explicitly state what is reused (event collection, label creation, labeling) and what is newly created (filter, action, rule)?
6. Was Option A (consolidation via `event_collaboration: True`) also presented as a choice?
7. Does every `Update` / `Discard` payload carry the `last_update_date_time` obtained from the immediately preceding `menu-filter`?
8. Does every `Update` payload include all columns, including the unchanged ones (since validation uses only the passed values)?
