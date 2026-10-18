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
- **Important (common misunderstanding)** `host_id` specifies "**which host the Conductor is executed against**" and **has no effect whatsoever on which events match**.
  - Therefore, a requirement like "respond on host A for host A's events and on host B for host B's events" cannot be met simply by creating two actions that differ only in `host_id`. Because a filter without a host condition matches events from all hosts, both rules fire on the same event and **the response runs even on unrelated hosts**.
  - Narrowing events by host is done by adding a condition on the fixed label `_exastro_host` to `filter_condition_json` in the `filter` menu (see `filter.md`).
- Setting `event_collaboration` to `True` makes the event's originating host (`_exastro_host`) the execution target directly. Since this removes the need to duplicate actions per host, **prefer this option for the requirement "respond on the host where the event occurred"** (in that case, do not specify `host_id`).

## Unique constraint on actions (important - a common pitfall when duplicating)

- This menu has a unique constraint on a combination of columns, so two actions with the same combination cannot be created. A violation produces:
  ```
  The combination is incorrect. (Combination: {'operation_id': None, 'conductor_class_id': 'Sleep_Execution', 'event_collaboration': 'False'}, Target ID: [...])  (499-00201 / MSG-00006)
  ```
- **The columns included in the unique constraint differ by version.** Newer versions also include `host_name` (host) and `parameter_sheet_name` (parameter sheet), but **older versions only look at the three columns `operation_id` + `conductor_class_id` + `event_collaboration`**.
  - In other words, on older versions you **cannot create two "direct Conductor execution" actions that use the same Conductor and differ only in host**; it collides with the existing action and fails.
- **Important (pre-check)** **Before registering** a new action, always check existing actions with `menu-filter` (`menu: "action"`) and test whether the combination of `conductor_class_id` / `event_collaboration` / `operation_id` you are about to register matches an existing one. If it does, **do not attempt the registration**: pick a workaround from the table below and present it to the user together with the reason (avoid the error up front rather than fixing it after the fact).
- If the error still occurs, do not retry the same payload. Switch to one of the following (the `Target ID` in the error message is the ID of the conflicting existing action, so check it with `menu-filter` before deciding).

| Workaround | Content | Notes |
|---|---|---|
| 1. Consolidate with event collaboration | Update the existing action to `event_collaboration: True` and do not add an action | **First choice.** Execution happens on the event's originating host, removing the need to duplicate per host |
| 2. Switch to operation execution mode | Create a new operation for the host in `operation_list` and specify `operation_id` (do not specify `host_id` / `parameter_sheet_id`) | The differing `operation_id` satisfies the constraint |
| 3. Use a different Conductor | Change `conductor_class_id` | Only when you actually want different response content |

- Confirm the chosen workaround with the user. In particular, option 1 makes the response run on whichever host the event occurred on, so state that behavioural change explicitly.

## Caution when `Update`-ing an existing action (important)

- On an `Update` via `maintenance-all`, **the mutual-exclusion validation is evaluated using only the values passed in this request**. Values already stored on the existing record are not filled in automatically.
- Therefore, when changing `event_collaboration` to `True` or changing `host_id`, **always pass `parameter_sheet_id` in the same payload**. Omitting it produces:
  ```
  If an Host/Event cooperation or Host/Host name is selected, necessary to set the usage Parameter Sheet Name.  (499-00201)
  ```
- The safe approach is to retrieve the existing record with `menu-filter` first and **pass the unchanged columns too** (`conductor_class_id` / `parameter_sheet_id`, etc.).
- Example of an `Update` switching to event collaboration mode (set `host_id` explicitly to `null`):
  ```json
  {
    "menu": "action",
    "records": [{
      "type": "Update",
      "parameter": {
        "action_id": "<existing action_id>",
        "last_update_date_time": "<the value retrieved with menu-filter, as-is>",
        "event_collaboration": "True",
        "host_id": null,
        "parameter_sheet_id": "<same parameter sheet name as before>"
      }
    }]
  }
  ```

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
