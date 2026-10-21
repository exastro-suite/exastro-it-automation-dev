# rule reference

An OASE rule. Based on filter results, decides which action to execute and what conclusion event to generate. **`filter` and `action` must be created beforehand.** Of the six menus, this one should be created last.

## filter_a / filter_operator / filter_b columns (mutually exclusive, important)

- `filter_a` is required.
- `filter_b` and `filter_operator` must **both be specified, or both left unspecified**. Specifying only one of them results in an error.
- The same filter cannot be specified for both `filter_a` and `filter_b`.
- `filter_operator` can only take one of these 3 values:
  - `A and B`: condition is met only when both filter A and B match
  - `A xor B`: condition is met when exactly one of filter A or B matches **in that evaluation cycle** (it does not wait for the other; see the section "XOR correlation (A xor B)")
  - `A -> B`: condition is met when filter A matches, followed later by filter B matching (time-series correlation). "If B does not arrive" cannot be expressed (see the section "Time-series correlation (A -> B)")
- To judge based on a single filter only, specify only `filter_a` and leave `filter_b`/`filter_operator` empty.
- **The unique constraint is the combination of `filter_a` + `filter_operator` + `filter_b`.** In other words, **two rules with the same filter configuration cannot be created** (`The combination is incorrect.` / 499-00201 / MSG-00006).
  - When duplicating an existing rule for another host, **you cannot just add a rule; a separate filter is always required.** Create a new filter with an `_exastro_host` condition added to `filter_condition_json` and specify it as `filter_a` (see `filter.md`).
  - Conversely, if you set `event_collaboration` to `True` on the `action` so it runs on the host where the event occurred, neither the rule nor the filter needs to be duplicated (one set covers all hosts).

## Only one rule runs per event (important)

- An event that matches a rule **becomes reserved (evaluated) and is not used for evaluating other rules**. Even if one event satisfies the conditions of several rules, **only the single rule with the highest priority actually runs** (see the `rule_priority` section).
  - This holds whether the filters are the same or different. You cannot "run both rule A and rule B on the same event".
- A rule can specify only one `action_id`.
- Therefore a request such as "when the existing rule matches, run another Conductor **in addition to** the current action" cannot be met just by adding rules or filters. Use the method in the section "Running another Conductor when an existing rule matches" below.


## AND correlation (A and B) — acting only when two events occur "at the same time"

- `filter_operator: "A and B"` is satisfied when **both filter A and filter B have a valid event that has not been used yet**.
- **"At the same time" does not mean "at the same instant".** The event that arrived first keeps waiting until the event collection setting's `ttl` (default 3600 seconds) expires. If the other event arrives in the meantime, the rule is satisfied. In the proposal, explain that it means "act if both arrive within N seconds", citing the actual `ttl` value.
- One of the filters may reuse an existing one (e.g. for CPU high load). Create the labeling setting and filter for the other one (e.g. memory high load) if they do not exist.

### When sharing a filter with an existing single-filter rule (most important)

For example, if a rule that "runs on CPU high load alone" already exists and you add an AND correlation rule (CPU and memory) that uses the same CPU filter as `filter_a`, **one of the following happens depending on the priorities** (behaviour confirmed with the product's rule evaluation engine).

| Priority | CPU and memory both arrived within `ttl` | Only CPU arrived |
|---|---|---|
| AND correlation is higher (with equal priorities too, the AND rule, which has `filter_b`, is evaluated first) | The AND correlation runs | The single rule **does not run immediately**. It runs only when the CPU event times out after `ttl` (the response is delayed by up to `ttl` seconds) |
| The single rule is higher | The single rule uses the CPU event, so **the AND correlation does not run** | The single rule runs immediately |

- In other words, you cannot "keep the existing single rule and also have the AND correlation behave as expected". For a request like "act only when X and Y occur at the same time", **always confirm with the user how to handle the existing single rule**. The options are:
    1. **Change the existing rule into the AND correlation** (`Update` adding `filter_b` and `filter_operator`; re-send every column without changing `rule_label_name` etc.). Matches the "only when" requirement with no side effects. **First choice**
    2. Disable (`available_flag: False`) or discard the existing rule, and create a new AND correlation rule
    3. Keep the existing rule. In this case, explain the side effects in the table above (with the AND rule higher, the CPU-only response is delayed by up to `ttl` seconds; with the single rule higher, the AND correlation never runs) **with the concrete number of seconds**, and obtain the user's agreement
- Do not leave the priorities equal. With equal priorities, the evaluation order is decided by the order of filter IDs and the intent becomes unpredictable.


## XOR correlation (A xor B) — when asked for "only one of the two" (important)

**XOR does not mean "act when only one occurs, and do not act when both occur".** The behaviour confirmed with the product's rule evaluation engine is as follows (unlike AND correlation, it does not wait for the other event).

| How the events arrive | Result of a standalone XOR rule |
|---|---|
| Only one arrived | **Satisfied immediately within that evaluation cycle** (it does not wait within `ttl` to see whether the other arrives) |
| Both arrived in the same evaluation cycle | Both events become **undetected** and nothing runs (they are not passed to other rules either) |
| One arrived, and the other arrived a little later (within `ttl`) | **XOR is satisfied twice**, responding to both |

- In other words, XOR "runs every time each one arrives on its own, and does nothing only when both arrive in the same cycle". **Never explain it as "no response if both arrive within `ttl` seconds"** (the "wait until `ttl`" behaviour of AND correlation does not apply to XOR).
- When asked "act when only one of X or Y occurs", **confirm with the user which meaning is intended**:
    1. "Respond as soon as each occurs; it is fine to skip only when they occur almost simultaneously" → XOR is enough
    2. "Do not respond if both occur within a certain time; respond only when just one occurs" → XOR cannot do this. Guide the user to the "absorbing rule" configuration below
    3. "Respond whichever occurs (both if both)" → create two single-filter rules (equivalent to OR)

### Configuration that strictly implements "only one" (absorbing rule)

Place an AND correlation rule without an action at a higher priority, and the single-filter rules at a lower priority. Behaviour confirmed with the rule evaluation engine:

| Rule | Priority | Content |
|---|---|---|
| Absorbing AND correlation rule | Higher (e.g. 1) | `filter_a`=X, `filter_b`=Y, `A and B`, **no `action_id`** |
| Single rule for X | Lower (e.g. 2) | `filter_a`=X, the response action |
| Single rule for Y | Lower (e.g. 2) | `filter_a`=Y, the response action |

- Both arrive within `ttl` → the absorbing rule uses the matched events and nothing is done
- Only one arrives → it waits for the other until `ttl`; if the other does not come, the single rule runs at timeout. **The response is delayed by `ttl` seconds**
- Always tell the user about this delay (the number of seconds of the current collection setting's `ttl`) and obtain agreement.

### When sharing a filter with an existing single-filter rule

| Priority | Only X arrived | Only Y arrived | Both in the same cycle |
|---|---|---|---|
| XOR is higher | XOR runs. **The existing single rule never runs** | XOR runs | Both undetected. The existing rule does not run either |
| The existing single rule is higher | The single rule runs | **Nothing runs** (the XOR rule effectively never runs) | — |

- If you add XOR while keeping the existing single rule, neither priority order behaves as expected. Always confirm how to handle the existing rule (change it into XOR / disable it / reorganize into the absorbing configuration). **Do not apply the AND correlation table ("delayed by up to `ttl` seconds") to XOR.**


## Time-series correlation (A -> B) and "if Y does not arrive within N minutes" (important)

- `filter_operator: "A -> B"` is satisfied when an event of filter B arrives **after** an event of filter A (confirmed with the rule evaluation engine).
    - A then B (within `ttl`) → satisfied
    - Only A → nothing happens (A times out after `ttl`)
    - B then A (reverse order) → not satisfied
- In other words, `A -> B` expresses "**when the recovery notification arrives**"; "**if it does not arrive**" cannot be written directly.

### How to build "escalate if Y (recovery) does not arrive within N minutes after X occurs"

Place an `A -> B` rule without an action at a higher priority, and an escalation rule for A alone at a lower priority (confirmed with the rule evaluation engine).

| Rule | Priority | Content |
|---|---|---|
| Absorbing rule | Higher (e.g. 1) | `filter_a`=X (failure), `filter_b`=Y (recovery), `A -> B`, **no `action_id`** |
| Escalation rule | Lower (e.g. 2) | `filter_a`=X (failure) only, the escalation action |

| How the events arrive | Result |
|---|---|
| Recovery within `ttl` after the failure | The absorbing rule is satisfied; no escalation |
| Failure only (no recovery) | When the failure event times out after `ttl`, the escalation rule runs |
| Recovery later than `ttl` after the failure | Escalates when `ttl` expires (the late recovery is not absorbed) |
| A recovery was left over first, then a failure | Not absorbed. When the failure's `ttl` expires, it escalates **if the earlier recovery has already expired**. **If it is still valid, the failure is not passed to the escalation rule either and simply times out (nothing happens)** |

- If the failure and the recovery come from the same collection setting (same `ttl`), the earlier recovery always expires before the failure, so the last row of the table above results in escalation. **If the failure and the recovery have different expiry times (e.g. the failure side is a conclusion event with a short rule `ttl`), a leftover recovery silently prevents the escalation** (confirmed with the rule evaluation engine). In that case use the configuration in the "Automatic recovery, and notifying if it does not recover" section of `oase_scenario_building.md`.
- **(When the failure and the recovery come from the same collection setting) Do not use `A and B` for the absorbing rule.** AND ignores order, so if a recovery notification of a previous failure is left unused within `ttl`, a new failure is absorbed the moment it arrives and **is not escalated** (confirmed with the rule evaluation engine). Always use `A -> B` (`filter_a` is the failure, `filter_b` is the recovery).
- **The waiting time "N minutes" cannot be set on the rule.** The expiry of an event is decided by **the `ttl` of the event collection setting (`event_collection`)**, and the failure event times out after that many seconds. The rule's `ttl` column is the expiry of the conclusion event and has nothing to do with the waiting time.
    - If the requested "N minutes" differs from the collection setting's `ttl`, always say so and confirm which of the following to do:
        1. Change the collection setting's `ttl` to N minutes (in seconds). **This changes the expiry of every event from that collection, affecting the waiting time of AND / XOR correlations and the timeout timing of other rules**, so look up the affected rules with `menu-filter` and present them
        2. Keep the current `ttl` (the waiting time becomes `ttl` seconds)
    - Do not make "create another collection setting for the same monitoring tool with a different `ttl`" the first choice, because **the same events may be fetched twice** (only when the targets can be separated by the fetch conditions).
- **If an existing rule already uses the escalation rule's filter (failure only) on its own**, a second rule with the same filter configuration cannot be created because of the unique constraint. Confirm with the user how to handle the existing rule.
- If the escalation is done by notification, the rule's before/after notification (destination and notification template) must be configured. If no destination is configured, explain that it must be set up first.

## action_id column

- Specify the name of an action already created in the `action` menu. Optional (a rule can also be created that only generates a conclusion event without executing any action).

## Running another Conductor when an existing rule matches (replace / add)

A request like "when rule X matches, run Conductor Y" has two possible meanings, and **you must always confirm with the user which one is meant**. Never silently replace the `action_id` of a rule that already has an action.

| | Intent | Method | Menus touched |
|---|---|---|---|
| Replace | Run Y **instead of** the current action | Prepare an `action` for Y and replace the existing rule's `action_id` with `Update` | `action` (new or reuse existing), `rule` (update) |
| Add | Also run Y **after** the current action | Chain rules via the conclusion event (below) | `label_creation`, `rule` (update existing + new), `filter` (new), `action` |

- If an action using Y's `conductor_class_id` already exists, reuse it instead of creating a new one (check with `menu-filter`, `menu: "action"`).
- For the replacing `Update`, re-send every unchanged column as in the example in the section "Caution when `Update`-ing an existing rule" below.

### Add: chaining rules via the conclusion event

A rule with an action generates a **conclusion event** (an event whose `_exastro_type` is `conclusion`) **when its Conductor completes successfully**. Pick up that conclusion event with another filter and run Y with a second rule.

```
monitoring event ─▶ existing rule (runs the current action; unchanged)
                       │ Conductor completed successfully
                       ▼
                   conclusion event (conclusion_label_settings adds chain_xxx=true)
                       │
                       ▼
                   new filter [["_exastro_type","==","conclusion"],["chain_xxx","==","true"]]
                       │
                       ▼
                   new rule ─▶ action for Y
```

1. Create a label key for chaining in `label_creation` (e.g. `file_copy_trigger`).
2. `Update` the existing rule and set `conclusion_label_settings` to `[["file_copy_trigger", "true"]]` (re-send every unchanged column).
3. Create a new `filter` with `filter_condition_json` `[["_exastro_type", "==", "conclusion"], ["file_copy_trigger", "==", "true"]]`.
4. Prepare an `action` for Y (reuse an existing one if available).
5. Create a new `rule` linking the filter from step 3 and the action from step 4.

Notes:

- **Y runs only when the first Conductor completes successfully.** If the first one ends abnormally, no conclusion event is created and Y does not run. Execution is also **sequential** (after the first completes), not simultaneous. Always explain this behaviour to the user in the proposal.
- The conclusion event also automatically gets `_exastro_rule_name` (the original rule's `rule_label_name`), but **`_exastro_rule_name` cannot be used as a filter condition** (it is not in the `filter_condition_json.label_name` pulldown). To chain, you must add your own label key through `conclusion_label_settings` as above.
- Make sure the existing filter contains `["_exastro_type", "≠", "conclusion"]`. Without it, the conclusion event could match the existing rule itself again.

## Multi-stage judgement (secondary judgement using the conclusion event of a primary rule) (important)

"Use the result of rule X and further judge with condition Y" is built by picking up the primary rule's conclusion event with the secondary rule's filter (the chaining mechanism is the same as the section "Add: chaining rules via the conclusion event").

### Putting the labels used for the secondary judgement on the conclusion event

The labels on a conclusion event are decided as follows (confirmed in `ita_by_oase_conclusion/libs/action.py`):
- Labels specified in `conclusion_label_settings` (the value **can use Jinja2**; `A` is the labels of filter A's event, `B` of filter B's event)
- When `event_label_inheritance_flag` is `True`, additionally **all** labels of the original event (except some system labels starting with `_exastro_`; `_exastro_host` and user-assigned labels are inherited)

To use `severity` for the secondary judgement, do one of the following. **Option 1, passing only the required labels, has a smaller impact and is safer.**
1. Add `["severity", "{{ A.severity }}"]` to the primary rule's `conclusion_label_settings` (keep the existing chaining label)
2. Set the primary rule's `event_label_inheritance_flag` to `True` (all labels of the original event are put on the conclusion event, so check that it does not unintentionally match existing conclusion-event filters)

### Relationship with existing conclusion-event rules

- A conclusion event can also be used by only one rule. If another rule (e.g. the chained file copy) already uses the primary rule's conclusion event, you must decide which runs, that rule or the secondary judgement rule (prioritise the secondary judgement / add the condition to the existing one / chain further from the existing one's conclusion event). Confirm with the user.
- The secondary judgement runs only **when the primary rule's Conductor completes successfully**, **sequentially** (for a primary rule without an action, the conclusion event is created immediately).

### Preventing infinite loops (mandatory check)

If a conclusion event **again satisfies** the filter of the rule that created it (or of a rule in an earlier stage of the chain), it keeps running: rule → conclusion event → same rule... With the rule evaluation engine, a configuration where the secondary rule's conclusion event satisfies the secondary rule's own condition **made a single evaluation run never finish** (there is a loop limit `EVALUATE_LATENT_INFINITE_LOOP_LIMIT`, but do not rely on it). Before proposing, always check the following and write the result of the check in the proposal:
- Write down the labels of the conclusion event each stage's rule creates (including inherited ones), and check one by one **which conclusion-event filters (filters containing `_exastro_type == conclusion`) they match**. They must not match their own filter or an earlier stage's filter
- Give each stage a **different marker label** via conclusion labels (e.g. `stage=1` for the primary, `stage=2` for the secondary), and make each stage's filter use only the marker of the stage before it
- Do not set `event_label_inheritance_flag` to `True` on the secondary (last-stage) rule. The earlier stage's marker and the judgement-condition labels would be inherited and cause it to match itself again
- Put `["_exastro_type", "≠", "conclusion"]` in filters for monitoring events so that they do not pick up conclusion events

## before_notification_destination / after_notification_destination columns

- When specifying notification destinations (multi-select), the corresponding notification template (`before_notification`/`after_notification`, a file-upload field) and `action_id` must always be specified together. Specifying only the destination without a template or action_id results in an error.
- The notification template file must contain both a `[TITLE]` and a `[BODY]` section (Jinja2 syntax may also be used).

## Configuring rule notifications (before / after notification) (important)

### Notification destinations are registered in Exastro Platform

- The choices of `before_notification_destination` / `after_notification_destination` are **the notification destinations registered in the Exastro Platform workspace**. They are not an ITA menu, so **they cannot be registered with the MCP tools**.
    - Where to register: Exastro Platform menu "**Notification management**" → workspace list → target workspace → "New notification destination"
    - To send by email, "**Organization settings**" → "**Mail server settings**" is also required (no mail is sent if it is not configured)
- If `list-menu-info-pulldown` (`menu: "rule"`) shows no candidates for `before_notification_destination`, no destination is registered. Ask the user to register one as above and tell you **the name of the registered destination**. An email address cannot be put into `before_notification_destination` directly.
- Even without a registered destination, **the templates (`before_notification` / `after_notification`) can be registered first** (no notification is sent while the destination is empty). Specifying a destination requires a template and `action_id`.
- The template is a file-upload item: create the text with `create-text-file` to obtain a `file_id`, and pass it with `fileid` in `maintenance-all`. Because it is an `Update` of the rule, re-send every unchanged column too.

### Data passed to the template (different shape from the common templates)

The following data is passed together to the rule's before/after notification templates (confirmed in `ita_by_oase_conclusion/libs/notification_data.py`). **There is no top-level `labels`**, so using the variables of the common templates (`notification_template_common`, e.g. `{{ labels._exastro_host }}`) as-is renders blanks.

| Variable | Content |
|---|---|
| `events` | A **list** of the events used by the rule. Each element's `labels` holds the labels (`_exastro_host`, user-assigned labels, `_exastro_fetched_time` (converted to a date-time), `_exastro_event_collection_settings_name`, etc.), and `_exastro_events` holds the original event JSON |
| `rule` | `rule_name`, `filter_a_name`, `filter_b_name`, `filter_operator`, etc. |
| `action` | Before: `action_name`, `conductor_name`, `operation_name`, `host_id`, etc. / After: `operation_name`, `status`, etc. |
| `action_log` | Evaluation result (`rule_name`, `status`, `time_register`, etc.) |
| `conductor` | After notification only. `status`, `time_start`, `time_end`, etc. |

```
[TITLE]
[Ops team] CPU high load detected ({{ events[0].labels._exastro_host }})
[BODY]
Rule: {{ rule.rule_name }}
Response: {{ action.action_name }} (Conductor: {{ action.conductor_name }})
{% for event in events %}
- Host: {{ event.labels._exastro_host }} / Type: {{ event.labels.alert_type }} / Detected: {{ event.labels._exastro_fetched_time }}
{% endfor %}
```

### When asked to "also notify Y only when X" (adding a destination conditionally)

- Destinations are decided per rule, and the destination cannot be switched inside a template. Create a **dedicated filter and rule** with the extra condition (e.g. `severity == Critical`), and place the dedicated rule above the existing rule (lower the existing rule's priority).
- Events matched by the dedicated rule are **not processed by the existing rule** (only one rule runs per event). Therefore give the dedicated rule everything the existing rule has.
    - **Set the destinations to "the existing rule's destinations + Y".** With Y alone, **notifications stop reaching the original destination (e.g. the ops team) under that condition**. If the request is "**also** Y", include both; if it is "**only** Y", Y alone. Even if the existing rule has no destination yet, explain that when the original destination is set later, it must also be added to the dedicated rule
    - Make the action (`action_id`), notification templates and `conclusion_label_settings` (chaining labels) the same as the existing rule. If any is missing, the response or the chain stops only under that condition
- When lowering the existing rule's priority with `Update`, re-send every unchanged column too.

### When asked to "change notifications per event type"

- To change the text or destination per alert type (e.g. CPU high load) → configure the before/after notification of **the rule handling that alert**. Confirm which rule (if several rules handle the same alert) and whether before, after or both.
- The `event_type` of the common templates (`notification_template_common`) is **the OASE notification type** (new (received), new, known (evaluated), known (timeout), undetected, etc.), not the alert type. Rewriting a common template affects the notifications of **every alert**, so do not make it the first choice for a per-alert-type request.

## conclusion_label_settings column

- The REST input value is a JSON string of a list of 2-element arrays: `[[label_key, label_value], ...]`. Defines the labels to attach to the conclusion event generated on a match.
- **Required on registration**, so always pass the key. Omitting it fails with `{"conclusion_label_settings": ["Required fields."]}` (499-00201).
- **`label_value` must not be empty.** `[["_exastro_host", ""]]` is rejected with `{"conclusion_label_settings": ["Value is required."]}` (499-01707) — the screen shows that row as a blank-value default, but the API does not accept it.
- When you do not need any conclusion label, pass an empty list as a string:
  ```json
  "conclusion_label_settings": "[]"
  ```
- `label_key` must be an existing label key registered in `label_creation` (or a reserved key such as `_exastro_host`); check the valid keys with `list-menu-info-pulldown`. An unknown key fails with `MSG-00032`.
- Example: to attach `severity=high` to the conclusion event:
  ```json
  "conclusion_label_settings": "[[\"severity\", \"high\"]]"
  ```

## rule_label_name column

- The name set on the `_exastro_rule_name` label of the conclusion event.
- **Cannot be changed after registration.** Attempting to change it to a different value on update results in an error.

## rule_priority column

- An integer, minimum value 1. **A smaller number means a higher priority** (`1` is the highest). The on-screen column description also says "Prioritize the one with the smaller number."
- When one event satisfies the conditions of several rules, only the highest-priority rule runs and the event is consumed there (it is not passed to other rules).
- **When several rules use the same filter, events of that filter are first evaluated only by the highest-priority rule.** While that rule is not satisfied (e.g. an AND correlation waiting for the other event), lower rules cannot use the event, and **only when the event times out** is it passed to the lower rules. See the section "AND correlation (A and B)" for details.

## ttl column

- In seconds. Minimum 10, maximum 2147483647. Default 3600.

## Caution when `Update`-ing an existing rule (important)

- On an `Update` via `maintenance-all`, **validation is evaluated using only the values passed in this request**. Values already stored on the existing record are not filled in automatically.
- Therefore, if you pass only one field intending to swap out `action_id`, `filter_a` / `filter_b` are treated as unspecified and you get:
  ```
  {"0": {"Individual check": ["Duplicate filters are selected."]}}  (499-00201)
  ```
- **Retrieve the existing record with `menu-filter` first and pass every unchanged column too** (`rule_name` / `rule_label_name` / `rule_priority` / `filter_a` / `conclusion_label_settings` / `action_label_inheritance_flag` / `event_label_inheritance_flag` / `ttl` / `available_flag`).
- Pass `last_update_date_time` as retrieved by the immediately preceding `menu-filter` (the value changes on every update, so re-fetch it for each consecutive write).
- Example of an `Update` that only swaps the action:
  ```json
  {
    "menu": "rule",
    "records": [{
      "type": "Update",
      "parameter": {
        "rule_id": "<existing rule_id>",
        "last_update_date_time": "<the value retrieved with menu-filter, as-is>",
        "available_flag": "True",
        "rule_name": "<same as existing>",
        "rule_label_name": "<same as existing>",
        "rule_priority": "1",
        "filter_a": "<same filter name as existing>",
        "action_id": "<new action name>",
        "conclusion_label_settings": "[]",
        "action_label_inheritance_flag": "True",
        "event_label_inheritance_flag": "False",
        "ttl": "3600"
      }
    }]
  }
  ```

## Minimal example for new registration

```json
{
  "menu": "rule",
  "records": [
    {
      "type": "Register",
      "parameter": {
        "available_flag": "True",
        "rule_name": "High load alert response rule",
        "rule_label_name": "high_load_rule",
        "rule_priority": "1",
        "filter_a": "High load alert filter",
        "action_id": "Restart service",
        "conclusion_label_settings": "[]",
        "action_label_inheritance_flag": "True",
        "event_label_inheritance_flag": "False",
        "ttl": "3600"
      }
    }
  ]
}
```
