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

## action_id column

- Specify the name of an action already created in the `action` menu. Optional (a rule can also be created that only generates a conclusion event without executing any action).

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

- An integer, minimum value 1. When multiple rules match at the same time, the rule with the larger (higher priority) value takes precedence.

## ttl column

- In seconds. Minimum 10, maximum 2147483647. Default 3600.

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
