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
