-- 添付ファイル
CREATE TABLE IF NOT EXISTS T_AI_ATTACHMENT_FILE
(
    UUID                            VARCHAR(40),                                -- UUID
    FILE_ID                         VARCHAR(50),                                -- FILE_ID
    SEQ_NO                          INT,                                        -- 連番
    FILE_NAME                       VARCHAR(255),                               -- ファイル名
    MIME_TYPE                       VARCHAR(255),                               -- Mime Type
    FILE_SIZE                       BIGINT,                                     -- サイズ
    FILE_DATA                       MEDIUMBLOB,                                 -- ファイルデータ
    LAST_UPDATE_TIMESTAMP           DATETIME(6),                                -- 最終更新日時
    LAST_UPDATE_USER                VARCHAR(40),                                -- 最終更新者
    PRIMARY KEY(UUID)
)ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;




-- インデックス
CREATE UNIQUE INDEX IND_T_AI_ATTACHMENT_FILE_01 ON T_AI_ATTACHMENT_FILE(LAST_UPDATE_USER,FILE_ID,SEQ_NO);
CREATE INDEX IND_T_AI_ATTACHMENT_FILE_02 ON T_AI_ATTACHMENT_FILE(LAST_UPDATE_TIMESTAMP);



