-- ------------------------------------------------------------
-- T_OASE_ACTION_LOG: ALTER - Add ACTION_RESULT Column
-- ------------------------------------------------------------
-- アクション結果カラムを追加（アクションの起動・実行時の詳細を保存）
ALTER TABLE T_OASE_ACTION_LOG ADD COLUMN ACTION_RESULT LONGTEXT AFTER ACTION_NAME;
ALTER TABLE T_OASE_ACTION_LOG_JNL ADD COLUMN ACTION_RESULT LONGTEXT AFTER ACTION_NAME;

