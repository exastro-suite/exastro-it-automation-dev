# movement_list_ansible_legacy reference
## host_specific_format column
- 対象デバイスの `device_list` メニューにおける設定値によって決定されます
    - `ip_address` が設定されており、かつ `host_dns_name` が設定されていない場合は、`IP` を設定します
    - `host_dns_name` が設定されており、かつ `ip_address` が設定されていない場合は、`Host name` を設定します

## header_section column
- root権限が必要かどうかに基づいて、`become: true` を追加するかどうかを判断してください
- 実行するタスクにroot権限が必要かどうか判断が付かない場合は、ルート権限が必要かユーザーに確認して`become: true` を追加するかを判定してください

