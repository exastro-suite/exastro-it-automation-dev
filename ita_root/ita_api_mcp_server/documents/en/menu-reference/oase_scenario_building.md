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
- Consequently, if an existing filter is shared by two rules as-is, for every host's event **only the single higher-priority rule** runs (one event is used by only one rule; see "Only one rule runs per event" in `rule.md`). As a result, **the response runs on hosts unrelated to the event, and the other rule never runs**.
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

## Extracting an arbitrary event field as a label

Procedure for a request like "make the <field name> of <event type> usable as a label" — i.e. **just adding one more value that can be used in conditions**. There is no need to touch all six menus.

### Only two menus are needed

| Menu | Handling |
|---|---|
| `event_collection` | **Reuse.** Use the existing collection setting (no new one needed) |
| `label_creation` | **Newly create.** Add one label key |
| `labeling` | **Newly create.** Add one record that copies the event field's value into the label value |
| `filter` / `action` / `rule` | **Leave untouched.** They only become necessary when the extracted label is actually used as a condition |

- Creating only `label_creation` does not populate any value. **Always propose it together with `labeling`.**
- Conversely, creating only `labeling` fails if the label key does not exist. The order is `label_creation` -> `labeling`.

### Steps

1. Retrieve the existing `label_creation` and `labeling` records with `menu-filter`.
    - If the same label key already exists, no new one is needed (tell the user so).
    - Look at the `search_key_name` of existing `labeling` records (e.g. `event.type`) as a hint about the event JSON structure.
2. **Retrieve `documents-menu/labeling.md` with `get-document` before building the proposal.** There are three assignment patterns, and this request is "Pattern C (extract the event field's value as-is)". Do not emulate it with Pattern A by creating one record per possible value.
3. Register the label key in `label_creation`.
4. Register the Pattern C record in `labeling` (specify only `search_key_name`; pass `type_name`/`comparison_method`/`search_value_name`/`label_value_name` all as `null`).
5. Tell the user that the label can now be used in `filter` conditions, and finish.

### Notes

- **The event-side field name is often a guess.** State explicitly that it is a guess and confirm with the user. Trying to inspect real data in the `event_history` menu fails with `System Error (999-99999)`, so do not attempt it as a verification method.
- There is no need to ask the user "which values will arrive". A single Pattern C record covers every value of that field.

## Targeting events only when a label value exceeds a threshold

The procedure for a request that **narrows events by a numeric threshold**, such as "I only want to target it when XX (e.g. CPU usage) exceeds YY (e.g. 80%)".

### A filter has no magnitude comparison (most important)

A filter's `condition_type` has only the two values `==` and `≠`; `>` and `>=` do not exist. Therefore **the threshold decision must be made on the `labeling` side, and the `filter` checks the resulting label with `==`** - a two-stage construction. This is the only way to achieve it in Exastro.

```
labeling (magnitude comparison here)            filter (only == here)
  event.cpu_usage > 80 (float)  ──▶  cpu_over_80 = "true"  ──▶  ["cpu_over_80","==","true"]
                                     (events at or below 80
                                      never get the label)
```

| Menu | Work |
|---|---|
| `label_creation` | **Create**. Add one label key for the threshold decision (e.g. `cpu_over_80`) |
| `labeling` | **Create**. Pattern A (conditional fixed value) with `>` etc. in `comparison_method` |
| `filter` | **Update**. Add an `==` condition on that label to the existing `filter_condition_json` |
| `event_collection` / `action` / `rule` | **Leave untouched** |

### Steps

1. **Before building the proposal, retrieve `documents-menu/filter.md` and `documents-menu/labeling.md` with `get-document`.** Confirm that the filter side has no magnitude comparison, and check Pattern A of `labeling` (the `type_name` × `comparison_method` combination).
2. Retrieve the existing `label_creation` / `labeling` / `filter` records with `menu-filter`. **Never ask the user something you can find out yourself with `menu-filter`, such as "have you already configured OASE?".** Build the proposal on the existing configuration you retrieved yourself.
3. Register the label key for the threshold decision in `label_creation`.
4. Register a Pattern A record in `labeling`.
    - `search_key_name`: the event field holding the number to compare (e.g. `event.cpu_usage`)
    - `type_name`: `float` (use `integer` only if you know only integers arrive)
    - `comparison_method`: `>` (use `>=` for "or more"; confirm with the user which one they mean)
    - `search_value_name`: the threshold (e.g. `80`)
    - `label_value_name`: a fixed value such as `true`
5. `Update` the filter to add `["<label key>", "==", "true"]` to `filter_condition_json`.
6. Explain the mechanism to the user - events below the threshold never get the label, so they do not match the condition - and finish.

### Notes

- **Pattern C (value extraction, all fields `null`) cannot satisfy the requirement.** Even if you extract the value into a `cpu_usage` label, a filter cannot express `cpu_usage > 80`, so it cannot narrow anything. Always use Pattern A for threshold decisions.
- **"Configure the monitoring tool to send only alerts above 80%" is not an Exastro-side setting.** When the user asks for the condition to be configured in Exastro, do not present it as the first or recommended option.
- Confirm with the user whether they mean "exceeds (`>`)" or "or more (`>=`)", and whether to embed the threshold in `label_key_name` (`cpu_over_80`) or use a value-independent name (`cpu_threshold_exceeded`).
- The field name holding the number is often a guess. State explicitly that it is a guess and confirm.
- **Always confirm which existing filters should receive the threshold condition.** It narrows the firing condition of existing rules, so never update every filter silently.
- On a filter `Update`, always pass the `last_update_date_time` obtained from the immediately preceding `menu-filter`; omitting it results in `last_update_date_time is invalid (None)` (499-00201). Re-send unchanged columns too (`filter_name`, `search_condition_id`, `available_flag`, etc.).

## Running another Conductor when an existing rule matches

Procedure for requests like "when rule X matches, run Conductor Y". For details, see the section "Running another Conductor when an existing rule matches (replace / add)" in `rule.md`, and `action.md`.

### Specifications to grasp first (most important)

- **Only one rule runs per event** (a matched event becomes reserved and is not passed to other rules). For `rule_priority`, **a smaller number means a higher priority**.
- **A rule can specify only one action.**
- Therefore "run Y in addition to the current action" cannot be achieved just by adding rules or filters. Chaining via the conclusion event is required.

### Steps

1. **Before drafting a proposal, retrieve `documents-menu/rule.md` and `documents-menu/action.md` with `get-document`.**
2. Retrieve the target rule, existing actions and filters with `menu-filter`, and determine which action is currently linked to the rule (do not ask the user).
3. If the existing rule already has an action, **confirm with `ask_user_choice` whether to replace (run Y instead of the current action) or add (also run Y after the current action)**. State the following in the options:
    - Replace: the current action (e.g. Sleep) will no longer run
    - Add: because the rules are chained via the conclusion event, **Y runs only when the current Conductor completes successfully, sequentially after it**
4. If an existing action uses Y's `conductor_class_id`, reuse it. Otherwise create a new action.
    - If Y's parameter sheet is not in the `parameter_sheet_id` list of `list-menu-info-pulldown` (e.g. a host-group-enabled sheet), **only Mode A (operation execution) can be used**.
    - In Mode A, confirm with the user whether to reuse an existing operation or create a new one. When reusing, look up the operation's registered parameters (target host, etc.) with `menu-filter` and show them.
5. For replace: `Update` the existing rule changing only `action_id` (pass every unchanged column and `last_update_date_time` too).
6. For add: following the chaining steps in `rule.md`, register in the order `label_creation` (chain label) → update the existing rule's `conclusion_label_settings` → new `filter` for the conclusion event → `action` → new `rule`.

### Notes

- "Creating a second rule with the same filter" or "creating another filter with the same conditions" cannot be registered because of unique constraints. Even if it could, only one rule runs per event.
- `_exastro_rule_name` cannot be used in the chaining filter condition (it is not in the pulldown). Always add your own label key through `conclusion_label_settings`.
- Pass `records` of `maintenance-all` as an array. Passing it as a JSON string results in `Records array is required`.

## Discarding OASE settings / restoring them from discard

Procedure for requests like "discard rule X" or "restore X from discard". For the call format, see the "Discard / Restore" section of `documents-tools/maintenance-all.md`; for finding discarded records, see "Handling discarded records" in `documents-tools/menu-filter.md`.

### Specifications to grasp first (most important)

- **The six OASE menus do not check references when discarding.** A filter or action used by an active rule can still be discarded. The rule then **stops working without any error** (during evaluation it is skipped because its filter is missing).
- **Restoring does not check whether referenced records are active either.** Restoring a rule whose filter or action is still discarded leaves the rule non-functional.
- When a referenced record is discarded, the referencing item is shown as `Failed to exchange ID. (<ID>)`.

### Dependencies and order

```
label_creation ◀── labeling ◀── filter ◀── rule ──▶ action
(label key)       (labeling)    (filter)   (rule)   (action)
```

- **Discard**: stop the user side first. `rule` → (`filter` / `action`) → `labeling` → `label_creation`
- **Restore**: bring back the used side first. `label_creation` → `labeling` → (`filter` / `action`) → `rule`

### Steps

1. **Retrieve `documents-tools/maintenance-all.md` and `documents-tools/menu-filter.md` with `get-document`.**
2. Retrieve the target with `menu-filter`. For restore, add `{"discard": {"NORMAL": "1"}}`. If several discarded records share the name, narrow down by `last_update_date_time` and by whether the referenced records are active; if still not unique, confirm with the user.
3. **Investigate and present the impact.**
    - When discarding a filter / action: look for active `rule`s using it with `menu-filter`. If any, explain that the rule will stop working, and confirm with `ask_user_choice` whether to discard the rule too or only the filter / action.
    - When restoring a rule: check that `filter_a` / `filter_b` / `action_id` are active. If they are discarded, explain that they must be restored first.
    - When discarding a label key: check the `labeling`, `filter` conditions and `rule` `conclusion_label_settings` that use it.
4. Execute `Discard` / `Restore` after obtaining the user's approval. Put **only the primary key and `last_update_date_time`** in `parameter`; do not include `discard`.
5. **Re-read with `menu-filter` and confirm that the `discard` value changed before reporting completion.**

### Notes

- "Discard" and "physical delete (`Delete`)" are different. When the user says "discard" (廃止), use `Discard`.
- The filter and action linked to a discarded rule remain. Tell the user they can be discarded next if unnecessary (do not discard them on your own).
- If another rule's `conclusion_label_settings` adds a label for this rule (as in the chaining setup of scenario 1-5), that label remains unused (harmless). Mention it if you notice it.

## Adding a new event collection setting and reusing existing labeling settings by copying them

Procedure for requests like "copy the same labeling settings as X (existing collection) to the newly added Y (collection)". This is the typical pattern when increasing the number of monitoring tools of the same kind.

### Steps

1. **Retrieve `documents-menu/event_collection.md` and `documents-menu/labeling.md` with `get-document`** (their "duplication" / "copy" sections).
2. Retrieve the source event collection setting and all of its labeling settings with `menu-filter`.
3. For the new collection, **confirm `url` and the credentials (`auth_token`, etc.) with the user**. Credentials cannot be obtained with `menu-filter`, so they cannot be copied from the existing setting. Reuse the existing values for the other items and say so in the proposal.
4. **Investigate with `menu-filter` how the existing filters and rules will apply to events from the new collection, and only then explain it** (see "How to think about the impact" below). Do not assert guesses such as "the filters have no host condition" without checking.
5. After approval, register in the order `event_collection` (new) → `labeling` (copies, one `Register` each).
6. Re-read with `menu-filter` and confirm that the destination labeling settings have the same count and contents as the source before reporting.

### How to think about the impact (important)

- **Filters and rules do not distinguish event collection settings.** A filter only looks at label values, so if the labels of an event from the new collection satisfy the conditions, existing rules fire.
- Therefore look at the existing filter conditions and explain as follows:
    - If there is an `_exastro_host` condition: events from the new monitoring tool fire only when the host name matches that value. Events from non-matching hosts just get labels and no rule runs. If a response is needed for the new hosts, adding filters and rules (scenario "Duplicating / extending an existing rule for another host") is required separately.
    - If there is no `_exastro_host` condition: existing rules run for events from any host of the new monitoring tool.
- If you want to separate responses per event collection setting, the fixed label `_exastro_event_collection_settings_id` (its value is the collection setting ID) can be used in filter conditions.

### Notes

- If you only add the collection setting without copying the labeling settings, events from the new collection get no labels at all, including `_exastro_host`, and match no rule.
- Give the destination `labeling_settings_name` a name distinguishable from the source (e.g. append ` (zabbix-02)`).
