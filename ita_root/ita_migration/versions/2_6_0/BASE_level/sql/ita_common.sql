-- ジョブ排他制御
CREATE TABLE IF NOT EXISTS T_COMN_JOB_EXCLUSIVE_CONTROL
(
    PRIMARY_KEY                 VARCHAR(40),                                -- 主キー
    JOB_NAME                    VARCHAR(255),                               -- ジョブ名
    ORGANIZATION_ID             VARCHAR(255),                               -- オーガナイゼーションID
    WORKSPACE_ID                VARCHAR(255),                               -- ワークスペースID
    LAST_UPDATE_TIMESTAMP       DATETIME(6),                                -- 最終更新日時
    PRIMARY KEY(PRIMARY_KEY)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;

-- インデックス
CREATE INDEX IND_T_COMN_JOB_EXCLUSIVE_CONTROL_01 ON T_COMN_JOB_EXCLUSIVE_CONTROL (JOB_NAME,ORGANIZATION_ID,WORKSPACE_ID);