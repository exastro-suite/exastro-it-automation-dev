# label_creation reference

A menu for defining OASE user label keys. It registers only the key name of an attribute to attach to events (the value is not decided here; attaching a value is done in the `labeling` menu).

## label_key_name column

- Only half-width alphanumeric characters, `_` (underscore) and `-` (hyphen) are allowed. The first character must be alphanumeric.
- Regular expression: `^[a-zA-Z0-9][a-zA-Z0-9_-]*$`
- Examples: `process`, `cpu_usage`, `host-group` are allowed; `_process`, non-ASCII characters, or names containing spaces are not.
- Label keys starting with `_exastro_` are reserved for system labels automatically attached by Exastro (`_exastro_type`, `_exastro_host`, etc.) and are referenced from a separate view (fixed labels). There is no need to create a user label with the same name.

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
