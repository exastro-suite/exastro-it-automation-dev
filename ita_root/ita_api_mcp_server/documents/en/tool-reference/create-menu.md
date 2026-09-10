# `create-menu` tool reference
This section describes the basic parameters of the create-menu tool.
If more detailed parameters are needed, refer to `create-menu-full-parameter.md`.

## Important
- Some items are added automatically, so after running `create-menu`, use `list-menu-info` to re-fetch the list of items.
- Some of the automatically added items are `IDColumn` items, so use `list-menu-info-pulldown` to get the values that can be specified.

## Required workflow before `create-menu`
1. Use search_docs to fetch menu_definition_and_creation.md and refer to the section on bundles/unique constraints.
2. Check the types of the variables used in the playbook, and if any list types exist, consider setting vertical:1.
3. Before calling create-menu, present the above judgment to the user and obtain their agreement.

## Required workflow for `create-menu`
**Before registering data with `maintenance-all`, be sure to follow the steps below.**

1. Call `list-menu-info` to retrieve the menu structure and field definitions.
    - Identify the value of `column_name_rest` (not `column_name`).
    - Check `required_item: "1"` for required fields.
    - Identify fields of type IDColumn.

2. To get the exact format of the values that can be selected for IDColumn items, call `list-menu-info-pulldown`.
    - Do not use only the ID or display name, and do not guess.
    - Specify the display value for IDColumn items.

3. After steps 1-2 are complete, call `maintenance-all` to register the data.

**Why this matters:** Skipping steps 1 and 2 will cause validation errors and require retries.

## Minimal Working Example
```json
{
    "menu_definition": {
        "menu": {
            "menu_name": "Simple Parameter Sheet",
            "menu_name_rest": "simple_param_sheet",
            "description": "A simple parameter sheet",
            "sheet_type_id": "1",
            "hostgroup": "0",
            "vertical": "0",
        },
        "column": {
            "c1": {
                "item_name": "A text field",
                "item_name_rest": "a_text_field",
                "required": "1",
                "column_class": "SingleTextColumn",
                "single_string_maximum_bytes": "256",
            },
            "c2": {
                "item_name": "B file field",
                "item_name_rest": "b_file_field",
                "required": "1",
                "column_class": "FileUploadColumn",
                "file_upload_maximum_bytes": "1024000"
            }
        }
    }
}
```

## Explanation of parameters
### menu_definition.menu.sheet_type_id
- 1: Parameter Sheet(Host/Operation)
        - Parameter sheet used with Ansible Legacy
- 2: Data Sheet
        - Sheet used for the data accumulation/collection feature
- 3: Parameter Sheet(Operation)

### menu_definition.menu.vertical
0: Do not use bundle format, 1: Use bundle format

### menu_definition.menu.hostgroup
0: Do not use host group, 1: Use host group

### menu_definition.column
Define using keys in the format `c` + a sequential number

### column_class
- `SingleTextColumn`: String field
- `MultiTextColumn`: Multi-line string field
- `NumColumn`: Integer field
- `FloatColumn`: Floating-point number field
- `DateTimeColumn`: Date and time field
- `DateColumn`: Date field
- `IDColumn`: field such as Check ON/OFF, Yes/No, True/False, etc.
- `PasswordColumn`: Sensitive field such as passwords
- `FileUploadColumn`: Field for storing file

### column_class=SingleTextColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "SingleTextColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "single_string_maximum_bytes": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=MultiTextColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "MultiTextColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "multi_string_maximum_bytes": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=NumColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "NumColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "integer_minimum_value": { "type": "string" },
        "integer_maximum_value": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=FloatColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "FloatColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "decimal_minimum_value": { "type": "string" },
        "decimal_maximum_value": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=DateTimeColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "DateTimeColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=DateColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "DateColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=IDColumn definition
```json
{
    "type": "object",
    "properties": {
        "column_class": { "type": "string", "const": "IDColumn" },
        "column_class_id": { "type": "string", "const": "7" },
        "pulldown_selection": { "type": "string", "enum":["Parameter sheet create:Selection 1:*-(blank)", "Parameter sheet create:Selection 2:Yes-No", "Parameter sheet create:Selection 2:True-False"] },
    },
    "required": ["item_name", "item_name_rest", "column_class", "pulldown_selection"]
```

### column_class=PasswordColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "PasswordColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "password_maximum_bytes": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```

### column_class=FileUploadColumn definition
```json
{
    "type": "object",
    "properties": {
        "item_name": { "type": "string" },
        "item_name_rest": { "type": "string" },
        "column_class": { "type": "string", "const": "FileUploadColumn" },
        "required": { "type": "string", "enum": ["0", "1"], "description": "1: true" },
        "file_upload_maximum_bytes": { "type": "string" }
    },
    "required": ["item_name", "item_name_rest", "column_class"]
}
```
