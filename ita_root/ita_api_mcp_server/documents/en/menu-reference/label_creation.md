# label_creation reference

A menu for defining OASE user label keys. It registers only the key name of an attribute to attach to events (the value is not decided here; attaching a value is done in the `labeling` menu).

## label_key_name column

- Only half-width alphanumeric characters, `_` (underscore) and `-` (hyphen) are allowed. The first character must be alphanumeric.
- Regular expression: `^[a-zA-Z0-9][a-zA-Z0-9_-]*$`
- Examples: `process`, `cpu_usage`, `host-group` are allowed; `_process`, non-ASCII characters, or names containing spaces are not.
- Label keys starting with `_exastro_` are reserved for Exastro's built-in system labels (`_exastro_type`, `_exastro_host`, etc.) and are referenced from a separate view (fixed labels). **Fixed labels do not need to be created here, and cannot be** — they start with an underscore, which violates the regular expression above, and fail with `The input value is an invalid value.`
- **Note: `_exastro_host` alone is not populated automatically.** To narrow events by host name, do not use `label_creation`; **create a `labeling` setting that copies the host name field of the event into `_exastro_host`** (see `filter.md` for the exact form).

## color_code column

- Only strings in `#RRGGBB` format (`#` + 6 hex digits) are allowed.
- Regular expression: `^#([0-9a-fA-F]{6})$`
- Example: `#FF0000`

## Minimal example for new registration

```json
{
  "menu": "label_creation",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "label_key_name": "cpu_usage",
        "color_code": "#FF0000"
      }
    }
  ]
}
```
