# rule reference

An OASE rule. Based on filter results, decides which action to execute and what conclusion event to generate. **`filter` and `action` must be created beforehand.** Of the six menus, this one should be created last.

## filter_a / filter_operator / filter_b columns (mutually exclusive, important)

- `filter_a` is required.
- `filter_b` and `filter_operator` must **both be specified, or both left unspecified**. Specifying only one of them results in an error.
- The same filter cannot be specified for both `filter_a` and `filter_b`.
- `filter_operator` can only take one of these 3 values:
  - `A and B`: condition is met only when both filter A and B match
  - `A xor B`: condition is met when exactly one of filter A or B matches
  - `A -> B`: condition is met when filter A matches, followed later by filter B matching (time-series correlation)
- To judge based on a single filter only, specify only `filter_a` and leave `filter_b`/`filter_operator` empty.
- **The unique constraint is the combination of `filter_a` + `filter_operator` + `filter_b`.** In other words, **two rules with the same filter configuration cannot be created** (`The combination is incorrect.` / 499-00201 / MSG-00006).
  - When duplicating an existing rule for another host, **you cannot just add a rule; a separate filter is always required.** Create a new filter with an `_exastro_host` condition added to `filter_condition_json` and specify it as `filter_a` (see `filter.md`).
  - Conversely, if you set `event_collaboration` to `True` on the `action` so it runs on the host where the event occurred, neither the rule nor the filter needs to be duplicated (one set covers all hosts).

## Only one rule runs per event (important)

- An event that matches a rule **becomes reserved (evaluated) and is not used for evaluating other rules**. Even if one event satisfies the conditions of several rules, **only the single rule with the highest priority actually runs** (see the `rule_priority` section).
  - This holds whether the filters are the same or different. You cannot "run both rule A and rule B on the same event".
- A rule can specify only one `action_id`.
- Therefore a request such as "when the existing rule matches, run another Conductor **in addition to** the current action" cannot be met just by adding rules or filters. Use the method in the section "Running another Conductor when an existing rule matches" below.

## action_id column

- Specify the name of an action already created in the `action` menu. Optional (a rule can also be created that only generates a conclusion event without executing any action).

## Running another Conductor when an existing rule matches (replace / add)

A request like "when rule X matches, run Conductor Y" has two possible meanings, and **you must always confirm with the user which one is meant**. Never silently replace the `action_id` of a rule that already has an action.

| | Intent | Method | Menus touched |
|---|---|---|---|
| Replace | Run Y **instead of** the current action | Prepare an `action` for Y and replace the existing rule's `action_id` with `Update` | `action` (new or reuse existing), `rule` (update) |
| Add | Also run Y **after** the current action | Chain rules via the conclusion event (below) | `label_creation`, `rule` (update existing + new), `filter` (new), `action` |

- If an action using Y's `conductor_class_id` already exists, reuse it instead of creating a new one (check with `menu-filter`, `menu: "action"`).
- For the replacing `Update`, re-send every unchanged column as in the example in the section "Caution when `Update`-ing an existing rule" below.

### Add: chaining rules via the conclusion event

A rule with an action generates a **conclusion event** (an event whose `_exastro_type` is `conclusion`) **when its Conductor completes successfully**. Pick up that conclusion event with another filter and run Y with a second rule.

```
monitoring event ─▶ existing rule (runs the current action; unchanged)
                       │ Conductor completed successfully
                       ▼
                   conclusion event (conclusion_label_settings adds chain_xxx=true)
                       │
                       ▼
                   new filter [["_exastro_type","==","conclusion"],["chain_xxx","==","true"]]
                       │
                       ▼
                   new rule ─▶ action for Y
```

1. Create a label key for chaining in `label_creation` (e.g. `file_copy_trigger`).
2. `Update` the existing rule and set `conclusion_label_settings` to `[["file_copy_trigger", "true"]]` (re-send every unchanged column).
3. Create a new `filter` with `filter_condition_json` `[["_exastro_type", "==", "conclusion"], ["file_copy_trigger", "==", "true"]]`.
4. Prepare an `action` for Y (reuse an existing one if available).
5. Create a new `rule` linking the filter from step 3 and the action from step 4.

Notes:

- **Y runs only when the first Conductor completes successfully.** If the first one ends abnormally, no conclusion event is created and Y does not run. Execution is also **sequential** (after the first completes), not simultaneous. Always explain this behaviour to the user in the proposal.
- The conclusion event also automatically gets `_exastro_rule_name` (the original rule's `rule_label_name`), but **`_exastro_rule_name` cannot be used as a filter condition** (it is not in the `filter_condition_json.label_name` pulldown). To chain, you must add your own label key through `conclusion_label_settings` as above.
- Make sure the existing filter contains `["_exastro_type", "≠", "conclusion"]`. Without it, the conclusion event could match the existing rule itself again.

## before_notification_destination / after_notification_destination columns

- When specifying notification destinations (multi-select), the corresponding notification template (`before_notification`/`after_notification`, a file-upload field) and `action_id` must always be specified together. Specifying only the destination without a template or action_id results in an error.
- The notification template file must contain both a `[TITLE]` and a `[BODY]` section (Jinja2 syntax may also be used).

## conclusion_label_settings column

- The REST input value is a JSON string of a list of 2-element arrays: `[[label_key, label_value], ...]`. Defines the labels to attach to the conclusion event generated on a match.
- **Required on registration**, so always pass the key. Omitting it fails with `{"conclusion_label_settings": ["Required fields."]}` (499-00201).
- **`label_value` must not be empty.** `[["_exastro_host", ""]]` is rejected with `{"conclusion_label_settings": ["Value is required."]}` (499-01707) — the screen shows that row as a blank-value default, but the API does not accept it.
- When you do not need any conclusion label, pass an empty list as a string:
  ```json
  "conclusion_label_settings": "[]"
  ```
- `label_key` must be an existing label key registered in `label_creation` (or a reserved key such as `_exastro_host`); check the valid keys with `list-menu-info-pulldown`. An unknown key fails with `MSG-00032`.
- Example: to attach `severity=high` to the conclusion event:
  ```json
  "conclusion_label_settings": "[[\"severity\", \"high\"]]"
  ```

## rule_label_name column

- The name set on the `_exastro_rule_name` label of the conclusion event.
- **Cannot be changed after registration.** Attempting to change it to a different value on update results in an error.

## rule_priority column

- An integer, minimum value 1. **A smaller number means a higher priority** (`1` is the highest). The on-screen column description also says "Prioritize the one with the smaller number."
- When one event satisfies the conditions of several rules, only the highest-priority rule runs and the event is consumed there (it is not passed to other rules).

## ttl column

- In seconds. Minimum 10, maximum 2147483647. Default 3600.

## Caution when `Update`-ing an existing rule (important)

- On an `Update` via `maintenance-all`, **validation is evaluated using only the values passed in this request**. Values already stored on the existing record are not filled in automatically.
- Therefore, if you pass only one field intending to swap out `action_id`, `filter_a` / `filter_b` are treated as unspecified and you get:
  ```
  {"0": {"Individual check": ["Duplicate filters are selected."]}}  (499-00201)
  ```
- **Retrieve the existing record with `menu-filter` first and pass every unchanged column too** (`rule_name` / `rule_label_name` / `rule_priority` / `filter_a` / `conclusion_label_settings` / `action_label_inheritance_flag` / `event_label_inheritance_flag` / `ttl` / `available_flag`).
- Pass `last_update_date_time` as retrieved by the immediately preceding `menu-filter` (the value changes on every update, so re-fetch it for each consecutive write).
- Example of an `Update` that only swaps the action:
  ```json
  {
    "menu": "rule",
    "records": [{
      "type": "Update",
      "parameter": {
        "rule_id": "<existing rule_id>",
        "last_update_date_time": "<the value retrieved with menu-filter, as-is>",
        "available_flag": "True",
        "rule_name": "<same as existing>",
        "rule_label_name": "<same as existing>",
        "rule_priority": "1",
        "filter_a": "<same filter name as existing>",
        "action_id": "<new action name>",
        "conclusion_label_settings": "[]",
        "action_label_inheritance_flag": "True",
        "event_label_inheritance_flag": "False",
        "ttl": "3600"
      }
    }]
  }
  ```

## Minimal example for new registration

```json
{
  "menu": "rule",
  "records": [
    {
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
    }
  ]
}
```
