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
| `Unique` | Only a uniquely matching event is evaluated. If multiple events match, all are treated as undetected events | Prohibited | Prohibited |
| `Queuing` | When multiple events match, they are evaluated in order from oldest (note: a rule may match multiple times) | Prohibited | Prohibited |
| `Grouping` types | Consecutive events with the same attributes are treated as the same group, and only the first event is used | Both required | **Prohibited** with period extension / allowed without period extension (if omitted, the TTL of the first event is used) |

- If `Unique`/`Queuing` is selected, registration fails if a filter with the same `filter_condition_json` (excluding grouping types) already exists.
  - In other words, **two filters with exactly the same conditions cannot be created** (`Identical filter conditions cannot be specified.` / 499-00201). When duplicating an existing filter for another host, add an `_exastro_host` condition so the conditions differ; changing only the name will not register.
- If a grouping type is selected, registration fails if a filter with the same combination of `group_label_key_ids` + `group_condition_id` + `filter_condition_json` already exists.

## group_label_key_ids column

- The REST input value is a JSON string of an array of label names. Example: `["process", "host"]`

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
