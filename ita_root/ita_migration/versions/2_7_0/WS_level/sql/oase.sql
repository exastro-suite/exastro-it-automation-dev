-- 重複排除
CREATE TABLE IF NOT EXISTS T_OASE_DEDUPLICATION_SETTINGS
(
    DEDUPLICATION_SETTING_ID        VARCHAR(40),                                -- 重複排除設定ID
    DEDUPLICATION_SETTING_NAME      VARCHAR(255),                               -- 重複排除設定名
    SETTING_PRIORITY                INT,                                        -- 優先順位
    EVENT_SOURCE_REDUNDANCY_GROUP   TEXT,                                       -- 冗長グループ（イベント収集先）
    CONDITION_LABEL_KEY_IDS         TEXT,                                       -- ラベル
    CONDITION_EXPRESSION_ID         VARCHAR(40),                                -- 式
    NOTE                            TEXT,                                       -- 備考
    DISUSE_FLAG                     VARCHAR(1)  ,                               -- 廃止フラグ
    LAST_UPDATE_TIMESTAMP           DATETIME(6)  ,                              -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(DEDUPLICATION_SETTING_ID)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;

CREATE TABLE IF NOT EXISTS T_OASE_DEDUPLICATION_SETTINGS_JNL
(
    JOURNAL_SEQ_NO                  VARCHAR(40),                                -- 履歴用シーケンス
    JOURNAL_REG_DATETIME            DATETIME(6),                                -- 履歴用変更日時
    JOURNAL_ACTION_CLASS            VARCHAR (8),                                -- 履歴用変更種別
    DEDUPLICATION_SETTING_ID        VARCHAR(40),                                -- 重複排除設定ID
    DEDUPLICATION_SETTING_NAME      VARCHAR(255),                               -- 重複排除設定名
    SETTING_PRIORITY                INT,                                        -- 優先順位
    EVENT_SOURCE_REDUNDANCY_GROUP   TEXT,                                       -- 冗長グループ（イベント収集先）
    CONDITION_LABEL_KEY_IDS         TEXT,                                       -- ラベル
    CONDITION_EXPRESSION_ID         VARCHAR(40),                                -- 式
    NOTE                            TEXT,                                       -- 備考
    DISUSE_FLAG                     VARCHAR(1)  ,                               -- 廃止フラグ
    LAST_UPDATE_TIMESTAMP           DATETIME(6)  ,                              -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(JOURNAL_SEQ_NO)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;

-- 重複排除条件式マスタ
CREATE TABLE IF NOT EXISTS T_OASE_DEDUPLICATION_CONDITION_EXPRESSION
(
    EXPRESSION_ID                   VARCHAR(2),                                 -- 条件式ID
    EXPRESSION_JA                   VARCHAR(255),                               -- 条件式（JA）
    EXPRESSION_EN                   VARCHAR(255),                               -- 条件式（EN）
    DISP_SEQ                        INT,                                        -- 表示順序
    NOTE                            TEXT,                                       -- 備考
    DISUSE_FLAG                     VARCHAR(1),                                 -- 廃止フラグ
    LAST_UPDATE_TIMESTAMP           DATETIME(6),                                -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(EXPRESSION_ID)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;