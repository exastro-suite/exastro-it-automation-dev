# menu-filter tool reference

## file parameter
- Specify "No" first.
- If you need to set the option to "Yes" because the file is required, you must specify `filter_conditions` that sufficiently narrow down the number of records, based on the list obtained when the option was set to "No".

## Filter Conditions Format
This section describes how to specify the `.filter_conditions` parameter.

### Supported Search Options
- **NORMAL**: Partial match - `{"column_name_rest": {"NORMAL": "exact_value"}}`
- **LIST**: Multiple values (exact match) - `{"column_name_rest": {"LIST": ["value1", "value2"]}}`
- **RANGE**: Range search - `{"column_name_rest": {"RANGE": {"START": "min", "END": "max"}}}`

### Examples
```json
// Exact match
{"operation_name": {"NORMAL": "operation name"}}

// Multiple values
{"status": {"LIST": ["Completed", "Executing"]}}

// Empty = get all records that are not discarded (discarded ones are excluded; see below)
{}
```

## Handling discarded records (important)
- **If `filter_conditions` does not specify `discard`, `{"discard": {"NORMAL": "0"}}` is added automatically and only non-discarded records are returned.** Even an empty `{}` does not include discarded records.
- When looking for discarded records (e.g. "restore X from discard"), specify `discard` explicitly.
  ```json
  // discarded only
  {"rule_name": {"NORMAL": "CPU Alert File Copy Rule"}, "discard": {"NORMAL": "1"}}
  // both discarded and active
  {"rule_name": {"NORMAL": "CPU Alert File Copy Rule"}, "discard": {"LIST": ["0", "1"]}}
  ```
- It is common for several discarded records to share the same name (one is left behind each time something is recreated). When choosing the record to restore, prefer the one with the newest `last_update_date_time`, and check that the records it references (e.g. a rule's `filter_a` / `action_id`) are active. If a referenced record has been discarded, that item is shown as `Failed to exchange ID. (<ID>)`. If there are several candidates, confirm with the user.
