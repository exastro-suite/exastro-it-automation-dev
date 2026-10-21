# filter reference

An OASE filter. Narrows down events by label conditions and determines which events are subject to rule evaluation. A single filter can be reused by multiple rules.

## filter_condition_json column

- The REST input value is a JSON string of a list of 3-element arrays: `[[label_name, condition_type, condition_value], ...]`.
  - `label_name`: the name of a label (one created in `label_creation`, or a fixed label such as `_exastro_type`).
  - `condition_type`: **only** `"=="` (equal) or `"≠"` (not equal). Other comparison operators (such as `<`) cannot be used in a filter.
  - `condition_value`: the value to compare against (string).
- Default value (initial value when unspecified): `[["_exastro_type", "≠", "conclusion"]]` (a standard condition that excludes conclusion events). Keep this condition when creating a new filter intended to target only normal events.
- Example: narrowing down to events from Zabbix whose event type is "high load alert":
  ```json
  [["_exastro_type", "≠", "conclusion"], ["event_type", "==", "high load alert"]]
  ```

## When you need a threshold (magnitude comparison) condition (important)

For requirements such as "target only events where CPU usage **exceeds** 80%" or "only when the response time is 1000 ms **or more**", **a filter has no magnitude comparison, so the comparison must be done on the `labeling` side and the filter then checks the resulting label with `==`**. This two-stage construction is the only way to achieve it in Exastro.

```
labeling (the comparison happens here)   filter (only == here)
  search_key_name:    event.cpu_usage
  type_name:          float          ─┐
  comparison_method:  >               ├─ only events above 80 get
  search_value_name:  80              │   cpu_over_80 = "true"
  label_key_name:     cpu_over_80    ─┘        │
  label_value_name:   true                     ▼
                                      [["cpu_over_80", "==", "true"], ...]
```

Steps:

1. Create a label key for the threshold decision in `label_creation` (e.g. `cpu_over_80`).
2. Create a **Pattern A (assign a fixed value only when a condition matches)** record in `labeling`. Set `comparison_method` to `>`/`>=`/`<`/`<=`, set `type_name` to `integer` or `float` for numeric values, and put a fixed value such as `true` in `label_value_name`. `labeling` does support `<`/`<=`/`>`/`>=` (unlike a filter). See `labeling.md` for details.
3. Add `[["cpu_over_80", "==", "true"]]` to the filter's `filter_condition_json`. Events below the threshold never get the label, so they do not match this condition and are excluded.

Notes:

- **Pattern C of `labeling` (value extraction, all fields `null`) cannot implement a threshold decision.** Even if you extract the value into a `cpu_usage` label, a filter cannot express `cpu_usage > 80`, so the requirement is not met. Always use Pattern A for threshold decisions.
- **"Configure the monitoring tool to send only alerts above 80%" is not an Exastro-side setting.** When the user is asking for the condition to be configured in Exastro, do not offer this workaround as the primary option (if you mention it at all, also present the Exastro-only method above as the recommended one).
- Thresholds can change, so ask the user whether to embed the threshold in `label_key_name` (e.g. `cpu_over_80`) or use a value-independent name such as `cpu_threshold_exceeded`.
- **When adding a threshold condition to existing filters, always confirm which filters to modify.** It narrows the firing condition of existing rules, so never update every filter silently.
- When issuing `Update` on an existing filter, always pass the `last_update_date_time` obtained from the immediately preceding `menu-filter`. Omitting it results in `{"0": {"Individual check": ["last_update_date_time is invalid (None)"]}}` (499-00201). Also, `Update` is validated using only the values you pass, so **re-send every unchanged column too** (`filter_name`, `search_condition_id`, `available_flag`, etc.).

## Fixed (built-in) labels - narrowing by host with `_exastro_host` (important)

In addition to labels created in `label_creation`, fixed labels built into Exastro can be specified in `label_name`. The list actually available can be retrieved via `list-menu-info-pulldown` under `filter_condition_json.label_name`.

| Fixed label | Meaning | How the value is set |
|---|---|---|
| `_exastro_host` | **The target host name of the event.** Use this to discriminate events per host | **Not set automatically. It must be assigned with `labeling`** (see below) |
| `_exastro_type` | Event type. `conclusion` means a conclusion event (normally excluded with `≠ conclusion`) | Automatic |
| `_exastro_event_collection_settings_id` | ID of the event collection setting that fetched the event | Automatic |
| `_exastro_fetched_time` / `_exastro_end_time` | Fetched time / end time of the event | Automatic |
| `_exastro_agent_name` / `_exastro_agent_version` | Name / version of the source agent | Automatic |

### The value of `_exastro_host` must be filled in by `labeling` (required)

- Fixed labels **do not need to be (and cannot be) registered in `label_creation`**. Names starting with `_exastro_` violate the `label_key_name` regular expression (must start with an alphanumeric character), so trying to create one in `label_creation` fails with `The input value is an invalid value.`
- However, `_exastro_host` alone **is not populated automatically**. Only labels such as `_exastro_type` are attached automatically to collected events; `_exastro_host` stays empty.
- Therefore, **whenever you use `_exastro_host` in a filter condition, you must also create a `labeling` setting that copies the host name field of the event into `_exastro_host`.** Just specify `_exastro_host` as `label_key_name` (fixed labels are included in the label-key pulldown).
- **You do not need one setting per host.** Specify only `search_key_name` and pass `type_name` / `comparison_method` / `search_value_name` / `label_value_name` **all as `null`**; the value of that field then becomes the label value as-is (copy-only pattern). One setting covers every host, so prefer this.
  ```json
  {
    "menu": "labeling",
    "records": [{
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "Assign target host label",
        "event_collection_settings_name": "Zabbix monitoring event collection",
        "search_key_name": "host.name",
        "type_name": null,
        "comparison_method": null,
        "search_value_name": null,
        "label_key_name": "_exastro_host",
        "label_value_name": null
      }
    }]
  }
  ```
  - **The keys themselves cannot be omitted.** Omitting them gives `Required keys ['type_name', 'comparison_method', 'search_value_name', 'label_value_name'] are missing.` (499-00201), and passing an empty string `""` gives `The input value is an invalid value.(input value:)`. Always pass `null`.
  - The field name given in `search_key_name` (e.g. `host.name`) **depends on the actual event JSON structure**, so if you guessed it, say so and confirm with the user.
- `event_collaboration: True` on an `action` (execute on the host where the event occurred) also uses the value of the `_exastro_host` label, so **without this `labeling` setting the execution target host cannot be determined**.

- **Important** A requirement like "only target events that occurred on this host" **must always be implemented with an `_exastro_host` condition in `filter_condition_json`**. The `host_id` column of the `action` menu specifies "which host the Conductor is executed against" and **has no effect whatsoever on which events match**.
  ```json
  [["_exastro_type", "≠", "conclusion"], ["event_type", "==", "high load alert"], ["_exastro_host", "==", "web-server-01"]]
  ```
- The `condition_value` for `_exastro_host` must be **the host name only**. Do not add the `[H]` prefix used by `action.host_id`.
- A filter without a host condition **matches events from all hosts**. In a configuration that splits rules per host, you must add an `_exastro_host` condition **to the existing filter as well**, not only to the new one; otherwise the existing rule keeps picking up events from every host.

## search_condition_id column (search method)

Whether `group_label_key_ids` / `group_condition_id` / `group_period` are required or prohibited changes depending on the selected search method.

**The number of choices differs by version** (some environments have a single `Grouping`, others split it into `Grouping (Period Extension)` / `Grouping (No Period Extension)`). **Always retrieve the actual choices with `list-menu-info-pulldown` before registering, and specify a value exactly as it appears there.**

| search_condition_id | Behavior | group_label_key_ids / group_condition_id | group_period |
|---|---|---|---|
| `Unique` | Only a uniquely matching event is evaluated. If multiple events match **in the same evaluation cycle**, all are treated as undetected events (if they arrive one by one with time gaps, each is evaluated as it arrives) | Prohibited | Prohibited |
| `Queuing` | When multiple events match, they are evaluated in order from oldest (note: a rule may match multiple times) | Prohibited | Prohibited |
| `Grouping` types | Consecutive events with the same attributes are treated as the same group, and only the first event is used | Both required | **Prohibited** with period extension / allowed without period extension (if omitted, the TTL of the first event is used) |

- If `Unique`/`Queuing` is selected, registration fails if a filter with the same `filter_condition_json` (excluding grouping types) already exists.
  - In other words, **two filters with exactly the same conditions cannot be created** (`Identical filter conditions cannot be specified.` / 499-00201). When duplicating an existing filter for another host, add an `_exastro_host` condition so the conditions differ; changing only the name will not register.
- If a grouping type is selected, registration fails if a filter with the same combination of `group_label_key_ids` + `group_condition_id` + `filter_condition_json` already exists.

## group_label_key_ids column

- The REST input value is a JSON string of an array of label names. Example: `["process", "host"]`

## Merging frequently recurring events into one incident (grouping) (important)

Behaviour confirmed with the rule evaluation engine:

| Search method | When the same alert keeps arriving from the same host |
|---|---|
| `Unique` | If they arrive with time gaps, the rule runs **every time** (the response runs repeatedly). If several arrive in the same evaluation cycle, **all become undetected** and nothing runs |
| `Grouping` | **Only the first event** is used by the rule; the second and later ones are merged as "subsequent events" (the response runs once) |

- How groups are formed (`group_condition_id`):
    - `is the target`: events whose values of the labels specified in `group_label_key_ids` are the same belong to the same group. For "per host and per alert type", use `["_exastro_host", "alert_type"]`
    - is not a target: events whose values of the labels **other than** the specified ones (excluding system labels starting with `_exastro_`; `_exastro_host` is included) are the same belong to the same group
- Group period:
    - `Grouping` (with period extension; `search_condition_id` value `3`): the period is extended every time a subsequent event arrives. **As long as the next event arrives within `ttl` (the collection setting's value; default 3600 seconds) of the last event, it is the same incident**; an event arriving after a longer quiet period starts a new incident and the rule runs again. It is not "merge only for `ttl` seconds from the first event"
    - Without period extension (value `4`; may not be offered in some environments): merges only during `group_period` (the first event's `ttl` when omitted)
- **With `Grouping` (period extension), do not send the `group_period` key at all.** `menu-filter` results do not include `group_period`, but if you add `"group_period": null` yourself and `Update`, an unexplained `System Error (999-00003)` occurs (`""` gives `Not an integer value.`, and a value gives an error that the period cannot be specified with period extension).
- Changing an existing filter's search method from `Unique` to `Grouping` changes the behaviour of **every rule** using that filter (no response for subsequent events), so look up the affected rules with `menu-filter` and present them.

## Wildcard (`*`) usage

- Rules for using `"*"` (wildcard, matches any value) in the `condition_value` of `filter_condition_json`:
  - When `search_condition_id` is `Unique`/`Queuing`, **wildcards are prohibited** (this is a grouping-only feature).
  - When a grouping type is selected, wildcards are allowed. However, `"*"` cannot be used with a `condition_type` of `"≠"` (not equal); it can only be used with `"=="`.

## Minimal example for new registration (unique search, narrowed by event type)

```json
{
  "menu": "filter",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "available_flag": "True",
        "filter_name": "High load alert filter",
        "filter_condition_json": "[[\"_exastro_type\", \"≠\", \"conclusion\"], [\"event_type\", \"==\", \"high load alert\"]]",
        "search_condition_id": "Unique"
      }
    }
  ]
}
```
