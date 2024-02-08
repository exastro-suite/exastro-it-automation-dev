-- ------------------------------------------------------------
-- ▼VIEW UPDATE START
-- ------------------------------------------------------------
-- 比較対象カラムプルダウン1
CREATE OR REPLACE VIEW V_COMPARE_MENU_COLUMN_PULLDOWN_1 AS 
SELECT
    `TBL_1`.*,
    CONCAT(
        `TBL_2`.`MENU_NAME_JA`,
        ':',
        `TBL_5`.`FULL_COL_GROUP_NAME_JA`,
        '/',
        `TBL_1`.`COLUMN_NAME_JA`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_JA`,
    CONCAT(
        `TBL_2`.`MENU_NAME_EN`,
        ':',
        `TBL_5`.`FULL_COL_GROUP_NAME_EN`,
        '/',
        `TBL_1`.`COLUMN_NAME_EN`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_EN`,
    CONCAT(
        `TBL_2`.`MENU_NAME_REST`,
        ':',
        `TBL_1`.`COLUMN_NAME_REST`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_REST`
FROM
    `T_COMN_MENU_COLUMN_LINK` `TBL_1`
LEFT JOIN `T_COMN_MENU` `TBL_2` ON (`TBL_1`.`MENU_ID` = `TBL_2`.`MENU_ID`)
LEFT JOIN `T_COMN_MENU_TABLE_LINK` `TBL_3` ON (`TBL_1`.`MENU_ID` = `TBL_3`.`MENU_ID`)
LEFT JOIN `T_COMPARE_CONFG_LIST` `TBL_4` ON (`TBL_1`.`MENU_ID` = `TBL_4`.`TARGET_MENU_1`)
LEFT JOIN `T_COMN_COLUMN_GROUP` `TBL_5` ON (`TBL_1`.`COL_GROUP_ID` = `TBL_5`.`COL_GROUP_ID`)
WHERE (`TBL_3`.`SHEET_TYPE` = "1" or  `TBL_3`.`SHEET_TYPE` = "4" ) 
AND `TBL_1`.`COL_NAME` = "DATA_JSON"
AND `TBL_4`.`DETAIL_FLAG` = "1"
AND `TBL_1`.`DISUSE_FLAG` <> "1" 
AND `TBL_2`.`DISUSE_FLAG` <> "1"
AND `TBL_4`.`DISUSE_FLAG` <> "1" 
AND `TBL_5`.`DISUSE_FLAG` <> "1"
;



-- 比較対象カラムプルダウン2
CREATE OR REPLACE VIEW V_COMPARE_MENU_COLUMN_PULLDOWN_2 AS 
SELECT
    `TBL_1`.*,
    CONCAT(
        `TBL_2`.`MENU_NAME_JA`,
        ':',
        `TBL_5`.`FULL_COL_GROUP_NAME_JA`,
        '/',
        `TBL_1`.`COLUMN_NAME_JA`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_JA`,
    CONCAT(
        `TBL_2`.`MENU_NAME_EN`,
        ':',
        `TBL_5`.`FULL_COL_GROUP_NAME_EN`,
        '/',
        `TBL_1`.`COLUMN_NAME_EN`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_EN`,
    CONCAT(
        `TBL_2`.`MENU_NAME_REST`,
        ':',
        `TBL_1`.`COLUMN_NAME_REST`
    ) AS `MENU_COLUMN_NAME_PULLDOWN_REST`
FROM
    `T_COMN_MENU_COLUMN_LINK` `TBL_1`
LEFT JOIN `T_COMN_MENU` `TBL_2` ON (`TBL_1`.`MENU_ID` = `TBL_2`.`MENU_ID`)
LEFT JOIN `T_COMN_MENU_TABLE_LINK` `TBL_3` ON (`TBL_1`.`MENU_ID` = `TBL_3`.`MENU_ID`)
LEFT JOIN `T_COMPARE_CONFG_LIST` `TBL_4` ON (`TBL_1`.`MENU_ID` = `TBL_4`.`TARGET_MENU_2`)
LEFT JOIN `T_COMN_COLUMN_GROUP` `TBL_5` ON (`TBL_1`.`COL_GROUP_ID` = `TBL_5`.`COL_GROUP_ID`)
WHERE (`TBL_3`.`SHEET_TYPE` = "1" or  `TBL_3`.`SHEET_TYPE` = "4" ) 
AND `TBL_1`.`COL_NAME` = "DATA_JSON"
AND `TBL_4`.`DETAIL_FLAG` = "1"
AND `TBL_1`.`DISUSE_FLAG` <> "1" 
AND `TBL_2`.`DISUSE_FLAG` <> "1"
AND `TBL_4`.`DISUSE_FLAG` <> "1" 
AND `TBL_5`.`DISUSE_FLAG` <> "1"
;

-- ------------------------------------------------------------
-- ▲ VIEW UPDATE END
-- ------------------------------------------------------------