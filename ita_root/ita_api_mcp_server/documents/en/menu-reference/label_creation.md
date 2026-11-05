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

## When merging label keys with the same meaning into one

- Unless an administrator has enabled physical deletion, label keys can only be discarded (the "Physical delete (Delete)" section of `tool-reference/maintenance-all.md`). Settings that reference a discarded key show `Failed to exchange ID` on the screen, and there is no reference check. Therefore **re-point the settings that use it first, then discard the key**.
- Steps: (1) decide which key to keep and which to remove -> (2) find every setting using the key to remove with `menu-filter` (`label_key_name` of `labeling`, conditions and `group_label_key_ids` of `filter`, `conclusion_label_settings` of `rule`, `condition_labels` of `deduplication`) -> (3) re-point them -> (4) re-read and confirm that no setting uses the key to remove -> (5) discard the key.
- **While re-pointing, old and new keys are mixed.** If labeling is re-pointed first, events arriving from then on get only the new key, and filters still looking at the old key stop matching. Re-point filters and labeling one right after the other without a gap. Events already received (with the old key) do not get the new key.
- For reverting, keep a list of the values before re-pointing (which setting used which key).
