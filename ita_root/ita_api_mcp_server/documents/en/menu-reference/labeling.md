# labeling reference

OASE labeling settings. Based on the value of a specific field in a received event, assigns a value to a label key created in `label_creation` (or a fixed label). **`event_collection` (collection settings) and `label_creation` (label key) must be created beforehand.**

## event_collection_settings_name column

- Specify the name of a collection setting already created in the `event_collection` menu (specifying a non-existent name results in an error).

## There are three assignment patterns (decide which one you need first)

The behaviour of `labeling` changes depending on which combination of fields you specify. **Work backwards from what you want to achieve and pick the pattern.**

| | What you want | `search_key_name` | `type_name`/`comparison_method`/`search_value_name` | `label_value_name` |
|---|---|---|---|---|
| Pattern A | Assign a fixed value only when a condition matches | specified | specified | specified |
| Pattern B | Always assign a fixed value, without a condition | **blank** | **all blank** | required |
| Pattern C | **Use the event field's value itself as the label value (value extraction)** | specified | **all `null`** | **`null`** |

- A request like "I want to take the XX field of the event out as a label so it can be used in conditions" is **Pattern C**. Trying to emulate it with Pattern A means creating one record per possible value, which does not scale.
- See the "Pattern C" section below for details.

## Pattern C: extracting an event field's value into a label as-is

- Specify only `search_key_name` and pass `type_name`/`comparison_method`/`search_value_name`/`label_value_name` as **explicit `null`**; the value of that field then becomes the label value as-is.
- **There is no need to create one record per possible value. A single record covers every value of that field.**

```json
{
  "menu": "labeling",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "Severity label assignment",
        "event_collection_settings_name": "Zabbix monitoring event collection",
        "search_key_name": "event.severity",
        "type_name": null,
        "comparison_method": null,
        "search_value_name": null,
        "label_key_name": "severity",
        "label_value_name": null
      }
    }
  ]
}
```

- **The keys themselves must not be omitted.** Omitting them results in `{"0": {"Individual check": ["Required keys ['type_name', 'comparison_method', 'search_value_name', 'label_value_name'] are missing."]}}` (499-00201).
- **Empty strings `""` must not be used either.** They result in `{"0": {"type_name": ["The input value is an invalid value.(input value:)"], "comparison_method": ["The input value is an invalid value.(input value:)"]}}` (499-00201). Always pass JSON `null`.
- Unless it is a fixed label, the destination `label_key_name` **must be created in `label_creation` beforehand**. Creating the label key alone does not populate any value, so always propose `label_creation` and `labeling` together.

## search_key_name column

- Specify a key inside the received event JSON using JMESPath format.
- Allowed characters: regular expression `^[a-zA-Z0-9!#%&()*+,-.;<=>?@[\]^_{|}~]+$`
- **Which field name applies depends on the actual event JSON structure.** If you guessed it, say so explicitly and confirm with the user. If an existing `labeling` record for the same collection setting has a `search_key_name` (e.g. `event.type`), following its prefix is the safer choice.
- Note that trying to inspect received event data in the `event_history` menu does not work: `menu-filter` fails with `System Error (999-99999)`. **Do not try `event_history` as a way to learn the event structure** (it only wastes turns).
- If left blank, `type_name`/`comparison_method`/`search_value_name` must also all be blank (Pattern B: always attaches a fixed label value without using a search condition). In that case `label_value_name` is required.

## type_name column and comparison_method column (compatibility table)

The data type of the value and the comparison method must be combined correctly. Combinations not in the table below result in a validation error.

| type_name (data type of the value) | Allowed comparison_method |
|---|---|
| `string`, `integer`, `float` | Any of `==` (equal), `≠` (not equal), `<`, `<=`, `>`, `>=` (regular-expression types are not allowed) |
| `bool`, `object`, `array`, `falsy` | `==` or `≠` only |
| `any` (other) | Only `RegExp` (regular expression, no option), `RegExp(DOTALL)`, or `RegExp(MULTILINE)` |

- When `type_name` is `integer`, `search_value_name` must be convertible to an integer. When `float`, it must be convertible to a float. When `bool`, it must be either `"true"` or `"false"` (case-insensitive).
- When `type_name` is `object`, `search_value_name` must be valid JSON starting with `{` and ending with `}`. When `array`, it must be valid JSON starting with `[` and ending with `]`.
- When `type_name` is `falsy`, `search_value_name` must be empty (specifying a value is an error). Also, when `comparison_method` is `≠`, `label_value_name` is required.
- When using a regular expression with `type_name` set to `any`, `search_value_name` must be a valid regular expression (an error occurs if it fails to compile).
- **There is no partial-match / substring comparison method.** Values such as `Contains`, `contains`, `LIKE` or `in` do not exist and fail with `{"comparison_method": ["The input value is an invalid value.(input value:Contains)"]}` (499-00201). To match on a substring (e.g. "the trigger name contains `CPU`"), use `type_name: "any"` + `comparison_method: "RegExp"` + `search_value_name: ".*CPU.*"`.
- The exact set of accepted values can be confirmed with `list-menu-info-pulldown` on this menu.

## label_key_name column

- Required. Specify the destination label key name (one created in `label_creation`, or a fixed label).

## label_value_name column

- The label value to assign.
- When using a regular expression (`RegExp` type), capture groups can be referenced as `\1`, `\2`, etc. If left blank, the entire match result is used as-is.
- Passing `null` selects Pattern C (the field value at `search_key_name` is assigned as-is). An empty string `""` and `null` mean different things; do not confuse them.

## Minimal example for new registration (Pattern A: assign the measured value to label_value when CPU usage exceeds 80)

```json
{
  "menu": "labeling",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "labeling_settings_name": "CPU usage label assignment",
        "event_collection_settings_name": "Zabbix monitoring event collection",
        "search_key_name": "cpu.usage",
        "type_name": "float",
        "comparison_method": ">",
        "search_value_name": "80",
        "label_key_name": "cpu_usage",
        "label_value_name": ""
      }
    }
  ]
}
```
