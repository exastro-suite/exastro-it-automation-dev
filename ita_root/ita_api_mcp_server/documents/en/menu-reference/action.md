# action reference

An OASE action. Defines the response process to execute when a rule matches, running an Ansible playbook etc. via a Conductor. A single action can be reused by multiple rules.

## Execution mode table (mutually exclusive, important)

An action has two execution modes, and **only one** should be specified. Mixing fields from both modes results in a registration error.

| Mode | operation_id | event_collaboration | host_id | parameter_sheet_id |
|---|---|---|---|---|
| A: Operation execution mode | **specify** | `False` (always pass the key) | Prohibited | Prohibited |
| B: Direct Conductor execution mode | Do not specify | **always pass the key**: `True` for event collaboration, `False` when using `host_id` | required when `event_collaboration` is `False` | **Required** |

- `event_collaboration` is **always required** on registration, in both modes. Omitting the key fails with `{"event_collaboration": ["Required fields."]}` (499-00201), so pass `"False"` explicitly even when you do not use event collaboration.
- In mode A, specify `operation_id` (a Movement-type operation) plus `event_collaboration: "False"`. Do not specify `host_id` / `parameter_sheet_id`.
- In mode B, instead of `operation_id`, choose one of:
  - set `event_collaboration` to `True` (uses the value of the source event's `_exastro_host` label as the target host), **or**
  - set `event_collaboration` to `False` and specify `host_id` to explicitly set the target host,
  and in either case `parameter_sheet_id` (the parameter sheet to use) must be specified.
  `event_collaboration=True` and specifying `host_id` at the same time is not allowed.
- `conductor_class_id` (Conductor class) is required in both modes.

## host_id column

- Value format is `[H]<host name>` (`[H]` prefix + host name). Example: `[H]web-server-01`
- Pulldown candidates can be retrieved with the `list-menu-info-pulldown` tool.

## parameter_sheet_id column

- Specify, by name, the parameter sheet (menu) to execute against the target host.

## Minimal example for new registration (direct Conductor execution mode, host specified)

```json
{
  "menu": "action",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "action_name": "Restart service",
        "conductor_class_id": "Ansible Execution",
        "event_collaboration": "False",
        "host_id": "[H]web-server-01",
        "parameter_sheet_id": "Restart httpd"
      }
    }
  ]
}
```
