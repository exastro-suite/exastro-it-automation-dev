#### Register Preset

This is an input example for calling `register-parameter-collection-filter` as a new registration.
Since this is a new registration, empty strings are specified for `uuid` and `last_update_date_time`.
Even when `mode` is `host`, always set the UUID of the target operation.
If the target operation cannot be determined, confirm it with the user.

```json
{
    "uuid": "",
    "filter_name": "test",
    "filter_json": "{\"tableDirection\":\"horizontal\",\"mode\":\"operation\",\"mainHost\":\"\",\"operation\":[\"23971849-4fc5-41e5-9ca2-fe3772d995a9\"],\"mainOperation\":\"23971849-4fc5-41e5-9ca2-fe3772d995a9\",\"host\":[\"1\",\"3979ff2d-7393-49e8-b464-807e5d3145fc\",\"8dfb9e60-c9f2-499d-9267-6cad945c1391\"],\"parameter\":[\"c4c72fe6-479a-41a3-bc1f-0b04336bb61f\"]}",
    "last_update_date_time": ""
}
```

- `filter_name`: Display name of the search condition (must be unique)
- `filter_json`: JSON string representing the search conditions for the parameter collection
    - `mode`: Display mode, such as `"operation"` or `"host"`
    - `operation` / `mainOperation`: UUID of the target operation
    - `host`: List of IDs of the target hosts (the host's `managed_system_item_number`)
    - `parameter`: List of IDs of the target parameter sheets (the parameter sheet's `menu_id`)
        - The parameter collection selects by parameter sheet, not by column (item) inside a sheet, so do not specify column IDs.
    - For `operation` / `host` / `parameter`, specify only values that can be selected on the parameter collection screen. An ID that does not exist there does not cause an error, but is ignored on the screen.
- When updating, specify the values obtained with `get-parameter-collection-filter` for `uuid` and `last_update_date_time`

#### Return value

- `uuid`: UUID of the registered/updated preset. For a new registration it is looked up from the list by `filter_name` after registering; it is omitted if it could not be identified.
