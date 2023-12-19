-- INSERT/UPDATE: -2.3.0
    -- T_COMN_ROLE_MENU_LINK: UPDATE
    -- T_COMN_MENU_COLUMN_LINK: UPDATE

-- T_COMN_ROLE_MENU_LINK: UPDATE
UPDATE T_COMN_ROLE_MENU_LINK SET PRIVILEGE='2' WHERE LINK_ID IN('50102', '50103', '50104', '50106', '50107');
UPDATE T_COMN_ROLE_MENU_LINK_JNL SET PRIVILEGE='2' WHERE LINK_ID IN('50102', '50103', '50104', '50106', '50107');

-- T_COMN_MENU_COLUMN_LINK: UPDATE
UPDATE T_COMN_MENU_COLUMN_LINK SET VALIDATE_REG_EXP='[^\/\\\\]+' WHERE COLUMN_DEFINITION_ID IN('5010303', '5010304', '5010403', '5010404');
UPDATE T_COMN_MENU_COLUMN_LINK_JNL SET VALIDATE_REG_EXP='[^\/\\\\]+' WHERE COLUMN_DEFINITION_ID IN('5010303', '5010304', '5010403', '5010404');