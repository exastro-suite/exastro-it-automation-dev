# deduplication reference

OASE deduplication settings. Merge events with the same content that arrive from redundant monitoring tools (several monitoring tools watching the same targets) into one. **The event collection settings (`event_collection`) to be merged and their labeling settings (`labeling`) must be created first.**

## How an event is judged to be a duplicate (important)

When an event is received, if an existing event satisfying all of the following exists, the event does not become a new event and is **merged into the event that arrived first** (which collection settings/agents it arrived from, and how many times, are added to the first event).
- It arrived from **another event collection setting in the redundancy group** (or another agent). Events from the same collection setting are never deduplicated against each other
- The first event is still within its expiry (the collection setting's `ttl`)
- The values of the user-assigned labels (labels assigned by labeling) match according to the condition (below)

Merged events are not thrown away; they remain as records on the first event. Only the first event is used for rule evaluation, so the response runs only once.
- Deduplication applies to **events received after the setting is registered**. Events already received are not merged.

## condition_labels column and condition_expression column (judgement condition)

| condition_labels | condition_expression | Condition for judging a duplicate |
|---|---|---|
| not specified | not specified | **All** user-assigned labels match |
| specified | `is matched` | **Only the specified labels** match (other labels are not looked at) |
| specified | `is ignored` | **All remaining labels except the specified ones** match |

- Specify **both or neither** of `condition_labels` and `condition_expression`. Specifying only one results in MSG-160001 ("both label and expression must be entered to specify a condition").
- Labels specified with `is matched` must **exist in the labeling settings of every collection setting in the redundancy group**. Otherwise MSG-160002 occurs.
- Labels specified with `is ignored` need only exist in the labeling settings of **one of** the collection settings in the redundancy group (otherwise MSG-160003).
- Guidelines for choosing:
    - The labels are completely identical between the monitoring tools → no condition (all match) is fine
    - Some labels have different values per monitoring tool (e.g. labels holding the tool's own event ID or fetch time) → set those labels to `is ignored`, or set only the labels that express identity (host, type, etc.) to `is matched`
    - Base the proposal on checking the labeling settings (`labeling`) with `menu-filter` to see whether each label has the same value across the monitoring tools. If you guessed, say so.

## event_source_redundancy_group column (redundancy group)

- Specify multiple event collection settings to be deduplicated.
- **One event collection setting can belong to only one deduplication setting.** If it is already used by another deduplication setting, MSG-160004 occurs. Check the existing settings with `menu-filter` (`menu: "deduplication"`) before registering.

## Passing multi-select items (important)

`event_source_redundancy_group` and `condition_labels` are multi-select items; pass **a JSON array of display names as a string**.
```json
"event_source_redundancy_group": "[\"Zabbix monitoring collection\", \"Zabbix monitoring collection (unit 2)\"]",
"condition_labels": "[\"_exastro_host\", \"alert_type\"]"
```
- **Passing a JSON array as-is results in an unexplained `System Error (999-99999)`.** Always pass it as a string.
- A string that cannot be read as JSON results in `JSON format is abnormal`.
- Check the display names with `list-menu-info-pulldown`. The values of `condition_expression` are `is matched` / `is ignored` (the display names change with the language setting, so use the pulldown values as-is).

## setting_priority column

- An integer. When several settings include common collection settings/labels and have the same priority, they are applied in ascending order of the deduplication setting name. `1` is usually fine (`1` is also set when omitted).

## Minimal example for new registration

```json
{
  "menu": "deduplication",
  "records": [{
    "type": "Register",
    "parameter": {
      "deduplication_setting_name": "Zabbix redundancy deduplication",
      "setting_priority": "1",
      "event_source_redundancy_group": "[\"Zabbix monitoring collection\", \"Zabbix monitoring collection (unit 2)\"]",
      "condition_labels": "[\"_exastro_host\", \"alert_type\"]",
      "condition_expression": "is matched"
    }
  }]
}
```
