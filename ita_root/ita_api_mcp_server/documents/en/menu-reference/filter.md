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

## search_condition_id column (search method)

Whether `group_label_key_ids` / `group_condition_id` / `group_period` are required or prohibited changes depending on the selected search method.

**The number of choices differs by version** (some environments have a single `Grouping`, others split it into `Grouping (Period Extension)` / `Grouping (No Period Extension)`). **Always retrieve the actual choices with `list-menu-info-pulldown` before registering, and specify a value exactly as it appears there.**

| search_condition_id | Behavior | group_label_key_ids / group_condition_id | group_period |
|---|---|---|---|
| `Unique` | Only a uniquely matching event is evaluated. If multiple events match, all are treated as undetected events | Prohibited | Prohibited |
| `Queuing` | When multiple events match, they are evaluated in order from oldest (note: a rule may match multiple times) | Prohibited | Prohibited |
| `Grouping` types | Consecutive events with the same attributes are treated as the same group, and only the first event is used | Both required | **Prohibited** with period extension / allowed without period extension (if omitted, the TTL of the first event is used) |

- If `Unique`/`Queuing` is selected, registration fails if a filter with the same `filter_condition_json` (excluding grouping types) already exists.
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
