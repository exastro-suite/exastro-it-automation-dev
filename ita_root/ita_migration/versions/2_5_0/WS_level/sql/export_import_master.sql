-- ------------------------------------------------------------
-- T_COMN_MENU: UPDATE
-- ------------------------------------------------------------
UPDATE T_COMN_MENU SET WEB_PRINT_LIMIT = 10000, WEB_PRINT_CONFIRM = 1000 WHERE MENU_ID IN ('60101','60102','60103','60104','60105','60106');
UPDATE T_COMN_MENU_JNL SET WEB_PRINT_LIMIT = 10000, WEB_PRINT_CONFIRM = 1000 WHERE MENU_ID IN ('60101','60102','60103','60104','60105','60106');

-- ------------------------------------------------------------
-- T_COMN_MENU_TABLE_LINK: UPDATE
-- ------------------------------------------------------------
UPDATE T_COMN_MENU_TABLE_LINK
SET MENU_INFO_JA =  '下記の機能を提供しています。
    ・メニューエクスポート
            データをエクスポートするメニューを選択し、エクスポートボタンをクリックしてください。

            モード
            ・環境移行
                    指定メニューのすべてのデータをエクスポートします。インポート先のデータをすべて置き換えます。
            ・時刻指定
                    指定時刻以降のデータのみエクスポートします。インポート先のデータとIDが被った場合はエクスポートしたデータが優先してインポートされます。

            廃止情報
            ・廃止を含む
                    廃止したレコードを含めてエクスポートします。
            ・廃止を除く
                    廃止したレコードを除いてエクスポートします。

            履歴
            ・履歴あり
                    履歴のレコードを含めてエクスポートします。
            ・履歴なし
                    履歴のレコードを含めずにエクスポートします。',
MENU_INFO_EN = 'The following functions are provided.
   ・Menu export
      Select the menu that you want to export data from and click the "Export" button.

Mode
   ・Environment migration
      Exports all the data of the selected menu and replaces the data in the import destination.

   ・Time specification
      Exports the data at the specified time.
If the ID is the same as the data of the important destination, the exported data has priority over the imported data.

Abolition data
   ・All records
      Exports all records
   ・Exclude discarded records
      Exports without discarded records

history
   ・History available
      Exports include a record of history.
   ・No history
      Exports without the history record.',
LAST_UPDATE_TIMESTAMP = _____DATE_____
    WHERE MENU_ID = '60101';

UPDATE T_COMN_MENU_TABLE_LINK_JNL
SET MENU_INFO_JA =  '下記の機能を提供しています。
    ・メニューエクスポート
            データをエクスポートするメニューを選択し、エクスポートボタンをクリックしてください。

            モード
            ・環境移行
                    指定メニューのすべてのデータをエクスポートします。インポート先のデータをすべて置き換えます。
            ・時刻指定
                    指定時刻以降のデータのみエクスポートします。インポート先のデータとIDが被った場合はエクスポートしたデータが優先してインポートされます。

            廃止情報
            ・廃止を含む
                    廃止したレコードを含めてエクスポートします。
            ・廃止を除く
                    廃止したレコードを除いてエクスポートします。

            履歴
            ・履歴あり
                    履歴のレコードを含めてエクスポートします。
            ・履歴なし
                    履歴のレコードを含めずにエクスポートします。',
MENU_INFO_EN = 'The following functions are provided.
   ・Menu export
      Select the menu that you want to export data from and click the "Export" button.

Mode
   ・Environment migration
      Exports all the data of the selected menu and replaces the data in the import destination.

   ・Time specification
      Exports the data at the specified time.
If the ID is the same as the data of the important destination, the exported data has priority over the imported data.

Abolition data
   ・All records
      Exports all records
   ・Exclude discarded records
      Exports without discarded records

history
   ・History available
      Exports include a record of history.
   ・No history
      Exports without the history record.',
LAST_UPDATE_TIMESTAMP = _____DATE_____
    WHERE JOURNAL_SEQ_NO = '60101';

-- ------------------------------------------------------------
-- T_COMN_MENU_COLUMN_LINK: INSERT
-- ------------------------------------------------------------
INSERT INTO T_COMN_MENU_COLUMN_LINK (COLUMN_DEFINITION_ID,MENU_ID,COLUMN_NAME_JA,COLUMN_NAME_EN,COLUMN_NAME_REST,COL_GROUP_ID,COLUMN_CLASS,COLUMN_DISP_SEQ,REF_TABLE_NAME,REF_PKEY_NAME,REF_COL_NAME,REF_SORT_CONDITIONS,REF_MULTI_LANG,REFERENCE_ITEM,SENSITIVE_COL_NAME,FILE_UPLOAD_PLACE,BUTTON_ACTION,COL_NAME,SAVE_TYPE,AUTO_INPUT,INPUT_ITEM,VIEW_ITEM,UNIQUE_ITEM,REQUIRED_ITEM,AUTOREG_HIDE_ITEM,AUTOREG_ONLY_ITEM,INITIAL_VALUE,VALIDATE_OPTION,VALIDATE_REG_EXP,BEFORE_VALIDATE_REGISTER,AFTER_VALIDATE_REGISTER,DESCRIPTION_JA,DESCRIPTION_EN,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES('6010315','60103','履歴情報','Journal Type','journal_type',NULL,'7',60,'T_DP_JOURNAL_TYPE','ROW_ID','JOURNAL_TYPE_NAME',NULL,'1',NULL,NULL,NULL,NULL,'JOURNAL_TYPE',NULL,'0','3','1','0','0','1','0',NULL,NULL,NULL,NULL,NULL,'履歴情報には以下が存在します。
・履歴あり
・履歴なし','The following history information exists:
・History available
・No history',NULL,'0',_____DATE_____,1);
INSERT INTO T_COMN_MENU_COLUMN_LINK_JNL (JOURNAL_SEQ_NO,JOURNAL_REG_DATETIME,JOURNAL_ACTION_CLASS,COLUMN_DEFINITION_ID,MENU_ID,COLUMN_NAME_JA,COLUMN_NAME_EN,COLUMN_NAME_REST,COL_GROUP_ID,COLUMN_CLASS,COLUMN_DISP_SEQ,REF_TABLE_NAME,REF_PKEY_NAME,REF_COL_NAME,REF_SORT_CONDITIONS,REF_MULTI_LANG,REFERENCE_ITEM,SENSITIVE_COL_NAME,FILE_UPLOAD_PLACE,BUTTON_ACTION,COL_NAME,SAVE_TYPE,AUTO_INPUT,INPUT_ITEM,VIEW_ITEM,UNIQUE_ITEM,REQUIRED_ITEM,AUTOREG_HIDE_ITEM,AUTOREG_ONLY_ITEM,INITIAL_VALUE,VALIDATE_OPTION,VALIDATE_REG_EXP,BEFORE_VALIDATE_REGISTER,AFTER_VALIDATE_REGISTER,DESCRIPTION_JA,DESCRIPTION_EN,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES(6010315,_____DATE_____,'INSERT','6010315','60103','履歴情報','Journal Type','journal_type',NULL,'7',60,'T_DP_JOURNAL_TYPE','ROW_ID','JOURNAL_TYPE_NAME',NULL,'1',NULL,NULL,NULL,NULL,'JOURNAL_TYPE',NULL,'0','3','1','0','0','1','0',NULL,NULL,NULL,NULL,NULL,'履歴情報には以下が存在します。
・履歴あり
・履歴なし','The following history information exists:
・History available
・No history',NULL,'0',_____DATE_____,1);

-- ------------------------------------------------------------
-- T_COMN_MENU_COLUMN_LINK: UPDATE
-- ------------------------------------------------------------
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 70, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010306';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 80, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010307';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 90, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010308';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 120, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010309';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 130, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010310';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 140, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010311';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 150, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010312';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 100, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010313';
UPDATE `T_COMN_MENU_COLUMN_LINK` SET `COLUMN_DISP_SEQ` = 110, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `COLUMN_DEFINITION_ID` = '6010314';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 70, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010306';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 80, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010307';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 90, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010308';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 120, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010309';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 130, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010310';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 140, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010311';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 150, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010312';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 100, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010313';
UPDATE `T_COMN_MENU_COLUMN_LINK_JNL` SET `COLUMN_DISP_SEQ` = 110, `LAST_UPDATE_TIMESTAMP` = _____DATE_____ WHERE `JOURNAL_SEQ_NO` = '6010314';


-- ------------------------------------------------------------
-- T_DP_JOURNAL_TYPE: INSERT
-- ------------------------------------------------------------
INSERT INTO T_DP_JOURNAL_TYPE (ROW_ID,JOURNAL_TYPE_NAME_JA,JOURNAL_TYPE_NAME_EN,DISP_SEQ,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES(1,'履歴あり','History available',10,NULL,'0',_____DATE_____,1);
INSERT INTO T_DP_JOURNAL_TYPE (ROW_ID,JOURNAL_TYPE_NAME_JA,JOURNAL_TYPE_NAME_EN,DISP_SEQ,NOTE,DISUSE_FLAG,LAST_UPDATE_TIMESTAMP,LAST_UPDATE_USER) VALUES(2,'履歴なし','No history',20,NULL,'0',_____DATE_____,1);

