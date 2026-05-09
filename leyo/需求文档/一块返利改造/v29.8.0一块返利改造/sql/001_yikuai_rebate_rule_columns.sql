-- 正向 DDL
ALTER TABLE db_pms.ts_rebate
  ADD COLUMN return_rule TINYINT UNSIGNED NULL COMMENT '计退规则：0-不计退，1-计退',
  ADD COLUMN rebate_rule TINYINT UNSIGNED NULL COMMENT '返利规则：0-每1件返利，1-每满X件返利';

ALTER TABLE db_pms.ts_rebate_log
  ADD COLUMN return_rule TINYINT UNSIGNED NULL COMMENT '计退规则：0-不计退，1-计退',
  ADD COLUMN rebate_rule TINYINT UNSIGNED NULL COMMENT '返利规则：0-每1件返利，1-每满X件返利';

ALTER TABLE db_pms.ts_rebate_cp
  ADD COLUMN return_rule TINYINT UNSIGNED NULL COMMENT '计退规则：0-不计退，1-计退',
  ADD COLUMN rebate_rule TINYINT UNSIGNED NULL COMMENT '返利规则：0-每1件返利，1-每满X件返利';

ALTER TABLE db_pms.ts_rebate_limit
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

ALTER TABLE db_pms.ts_rebate_limit_log
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

ALTER TABLE db_pms.ts_rebate_limit_cp
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill_log
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill_cp
  ADD COLUMN per_x INT UNSIGNED NULL COMMENT '每满X件',
  ADD COLUMN rebate_amount DECIMAL(18,2) NULL COMMENT '每满X件返利金额';

-- 回滚 DDL
ALTER TABLE db_pms.ts_rebate
  DROP COLUMN return_rule,
  DROP COLUMN rebate_rule;

ALTER TABLE db_pms.ts_rebate_log
  DROP COLUMN return_rule,
  DROP COLUMN rebate_rule;

ALTER TABLE db_pms.ts_rebate_cp
  DROP COLUMN return_rule,
  DROP COLUMN rebate_rule;

ALTER TABLE db_pms.ts_rebate_limit
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;

ALTER TABLE db_pms.ts_rebate_limit_log
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;

ALTER TABLE db_pms.ts_rebate_limit_cp
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill_log
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;

ALTER TABLE db_pms.ts_rebate_goodsdoc_bill_cp
  DROP COLUMN per_x,
  DROP COLUMN rebate_amount;



INSERT INTO db_admin.ts_sys_config (`code`, `name`, `note`, `values`, `ctime`)
VALUES (
  'LUNAR_YIKUAI_PROVIDER_ID',
  '一块供应商ID配置',
  '用于应收明细计算识别一块供应商（销退/计退/useOutTime）',
  '20264',
  NOW()
)
ON DUPLICATE KEY UPDATE
  `name` = VALUES(`name`),
  `note` = VALUES(`note`),
  `values` = VALUES(`values`);
