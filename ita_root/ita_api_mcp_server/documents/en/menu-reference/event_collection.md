# event_collection reference

OASE event collection settings. Defines where and how an agent such as a monitoring tool connects to retrieve events. Read this reference before operating this menu with `maintenance-all` etc.

## connection_method_name column

- The required fields differ depending on the connection method. Always check the table below before registering/updating.

| connection_method_name | Allowed request_method_name | Required fields | Prohibited |
|---|---|---|---|
| `No Agent Used` | - | - | `url` is not required |
| `Bearer Authentication` | `GET` / `POST` | `url`, `auth_token` (on new registration) | Must not include `authorization:` in `request_header` (case-insensitive) |
| `password authentication` (Basic) | `GET` / `POST` | `url`, `username`, `password` (on new registration) | Must not include `authorization:` in `request_header` |
| `Optional Authentication` | `GET` / `POST` | `url` | Authentication information must be described in `parameter` yourself |
| `IMAP password authentication` | `IMAP: Plaintext` only | `url`, `username`, `password` (on new registration) | - |

- **Important** The available choices differ by version (some connection methods do not exist in older environments; for example the shared-key method `Authentication SharedKeyLite` has been removed and does not appear in the pulldown of current environments). **Always retrieve the actual choices with `list-menu-info-pulldown` before registering, and specify a value exactly as it appears there.** Never guess a value that is not in the table, nor a literal translation of the user's wording (e.g. "arbitrary authentication" -> `Arbitrary authentication`); the correct value is `Optional Authentication`.
- If anything other than `No Agent Used` is selected, `url` (connection destination) must not be empty.
- When `connection_method_name` is `IMAP password authentication`, `response_list_flag` is automatically forced to `True` (any specified value is overwritten).
- If the connection method is changed on update and `password` is not specified, the existing `password` is cleared (it must be re-entered).
- In an update that does not change the connection method (e.g. changing only `ttl`), credential items that are not sent **keep their existing values** (confirmed in the database). `menu-filter` returns `null` for them, but that does not mean they were cleared, so there is no need to ask the user to re-enter or check them.

## request_header column

- Specify either a JSON object or a Jinja2 template (a string containing `{{ ... }}` or `{% ... %}`). Any other format results in an error.
- When `connection_method_name` is `Bearer Authentication` / `password authentication` / `Optional Authentication`, the string `authorization:` (case-insensitive) must not be included (authentication information is managed by a separate field).

## parameter column

- Like `request_header`, specify either a JSON object or a Jinja2 template.

## ttl column

- In seconds. Minimum 10, maximum 2147483647.
- **Required on registration via the API.** Omitting it fails with `{"ttl": ["Required fields."]}` (499-00201). The screen pre-fills `3600`, but `maintenance-all` does not apply that default, so always pass it explicitly (`3600` is a reasonable value).

## Always pass request_header and parameter explicitly (important)

- When `connection_method_name` is one of `Bearer Authentication` / `password authentication` / `Optional Authentication`, **omitting the `request_header` / `parameter` keys from `maintenance-all` makes the registration fail with an opaque `System Error (999-99999)`** instead of a validation message.
- Therefore always include both keys. If you have nothing to set, pass an empty JSON object as a string:
  ```json
  "request_header": "{}",
  "parameter": "{}"
  ```
- The same applies to `username` (for `password authentication`): include the key even when the value is empty.
- If you do get `System Error (999-99999)` on this menu, do not retry the same payload; add the missing `request_header` / `parameter` keys and retry once.

## Minimal example for new registration (Bearer authentication, GET)

```json
{
  "menu": "event_collection",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "event_collection_settings_name": "Zabbix monitoring event collection",
        "connection_method_name": "Bearer Authentication",
        "request_method_name": "GET",
        "url": "https://zabbix.example.com/api/events",
        "auth_token": "xxxxxxxx",
        "request_header": "{}",
        "parameter": "{}",
        "ttl": "3600"
      }
    }
  ]
}
```

## Creating a new event collection setting based on an existing one (duplication)

- `event_collection_settings_name` is **unique**. Give the copy a different name.
- **Credential items are not returned by `menu-filter` (they come back as `null`), so they cannot be copied from the existing setting.** Always confirm them for the copy with the user, and never register guessed or dummy values. The items concerned are:
  - `auth_token`
  - `password`
  - `secret_access_key`
- If the monitoring tool is a different machine, `url` should also differ, so confirm `url` with the user as well. `connection_method_name` / `request_method_name` / `request_header` / `parameter` / `ttl` / `response_key` / `event_id_key` and so on may be reused from the existing values (state in the proposal that they are reused).
- Adding an event collection setting alone does not attach any labels. Labeling settings are required per event collection setting, so also see the section "Copying existing labeling settings to another event collection setting" in `labeling.md`.

## Collection interval (how often the agent fetches events)

- **This menu has no collection interval field.** The only field in seconds is `ttl`, which is how long an event is treated as a target for rule evaluation, not the collection interval. Shortening `ttl` does not make detection faster; it shortens the wait of AND correlation and "if ... does not arrive" rules and changes how existing rules behave, so never change `ttl` for a collection interval request.
- The collection interval is determined by the environment variable (`.env`) `EXECUTE_INTERVAL` (seconds) of the OASE agent, which runs separately from ITA. The behavior confirmed in the product code (`agent/agent_init.py`) is as follows.
    - The default when not specified is **5 seconds**. A value of 3 or less becomes 3 seconds (lower limit 3 seconds).
    - One agent cycles through all collection settings listed in `EVENT_COLLECTION_SETTINGS_NAMES` at the same interval. **The interval cannot be set per collection setting.** To change it for only one collection setting, run a separate agent dedicated to that collection setting and remove it from the original agent's `EVENT_COLLECTION_SETTINGS_NAMES`.
    - Every `ITERATION` loops (default 10, rounded into 10-120), the agent re-fetches the collection settings from ITA. If `EXECUTE_INTERVAL x ITERATION` is 86400 seconds or more, `ITERATION` is reduced automatically.
    - To change it, edit `.env` (or the container environment variables) on the server running the agent and restart the agent. **The MCP tools can neither change it nor read its current value.**
- A collection setting whose `connection_method_name` is `No Agent Used` is not polled by an agent (events are sent from outside to the ITA API). The collection interval does not apply; timing depends on the sender.

### When asked "detection is slow, so change the collection interval to N seconds"

1. Retrieve the target collection setting with `menu-filter` and check `connection_method_name` (if it is `No Agent Used`, there is no interval setting as described above).
2. Tell the user that the collection interval cannot be changed in the ITA settings, and that `ttl` is a different thing and will not be changed.
3. **Check whether the requested value is really "shorter".** The default is 5 seconds, so unless the agent setting has been changed, "shorten it to 30 seconds" actually makes it **longer and detection even slower**. The current value is not visible from MCP, so ask the user to have the person who manages the agent check the current `EXECUTE_INTERVAL`, and do not assert that it becomes shorter while the current value is unknown.
4. Tell the user that it also applies to the other collection settings handled by the same agent (and show how to change only that collection setting).
5. Among causes of delay other than the interval, investigate **the ones that can be checked in ITA** with `menu-filter` and show them. In particular, check whether rules that use events from that collection setting are AND correlation (`A and B`) or an absorb configuration (the "AND correlation" and "XOR correlation" sections of `rule.md`), which make one event wait up to `ttl` seconds. Also mention that the evaluation interval on the monitoring tool side and the execution interval of ITA's evaluation process may be causes.
