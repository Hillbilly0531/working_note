-- ============================================================
-- 凭证流水状态错误排查 SQL
-- 基于生产代码 VoucherFlowBillServiceImpl 中的状态判定规则
-- ============================================================

-- ----------------------------------------------------------
-- 一、原票（is_original=1）审批通过 状态错误
-- 认定规则：claimAmount vs amount
-- ----------------------------------------------------------
SELECT
    id,
    voucher_flow_code,
    flow_status                         AS 当前状态,
    COALESCE(amount, 0)                 AS 总金额,
    COALESCE(claim_amount, 0)           AS 认领金额,
    CASE
        WHEN COALESCE(claim_amount, 0) = 0                         THEN '应0-待认领'
        WHEN COALESCE(claim_amount, 0) = COALESCE(amount, 0)       THEN '应1-认领完毕'
        WHEN COALESCE(claim_amount, 0) < COALESCE(amount, 0)       THEN '应5-部分认领'
        ELSE                                                             '???认领金额超限'
    END                                 AS 期望状态
FROM db_pms.ts_voucher_flow_bill
WHERE is_original = 1
  AND status = 3
  AND (
       (COALESCE(claim_amount, 0) = 0                                    AND flow_status != 0)
    OR (COALESCE(claim_amount, 0) > 0
        AND COALESCE(claim_amount, 0) = COALESCE(amount, 0)              AND flow_status != 1)
    OR (COALESCE(claim_amount, 0) > 0
        AND COALESCE(claim_amount, 0) < COALESCE(amount, 0)              AND flow_status != 5)
  )
ORDER BY flow_status, id;


-- ----------------------------------------------------------
-- 二、副卡（is_original=0）审批通过 状态错误
-- 认定规则：
--   auditHandleType=1 → 4(已作废)
--   auditHandleType=2 → 11(旧返利凭证)
--   其他(type=0/4/null) → writeOff vs claimAmount
-- ----------------------------------------------------------
SELECT
    id,
    voucher_flow_code,
    flow_status                         AS 当前状态,
    COALESCE(audit_handle_type, -1)     AS 审批类型,
    COALESCE(claim_amount, 0)           AS 认领金额,
    COALESCE(write_off_amount, 0)       AS 核销金额,
    COALESCE(write_offing_amount, 0)    AS 核销中金额,
    CASE
        WHEN audit_handle_type = 1 THEN '应4-已作废'
        WHEN audit_handle_type = 2 THEN '应11-旧返利凭证'
        WHEN COALESCE(write_off_amount, 0) = 0
         AND COALESCE(write_offing_amount, 0) = 0                       THEN '应6-待核销'
        WHEN COALESCE(write_off_amount, 0) > 0
         AND COALESCE(write_off_amount, 0) < COALESCE(claim_amount, 0)  THEN '应2-部分核销'
        WHEN COALESCE(write_off_amount, 0) > 0
         AND COALESCE(write_off_amount, 0) = COALESCE(claim_amount, 0)  THEN '应3-全部核销'
        ELSE                                                                  '???核销金额超限'
    END                                 AS 期望状态
FROM db_pms.ts_voucher_flow_bill
WHERE is_original = 0
  AND status = 3
  AND (
       (audit_handle_type = 1 AND flow_status != 4)
    OR (audit_handle_type = 2 AND flow_status != 11)
    OR (COALESCE(audit_handle_type, 0) NOT IN (1, 2) AND (
            (COALESCE(write_off_amount, 0) = 0
             AND COALESCE(write_offing_amount, 0) = 0                   AND flow_status != 6)
         OR (COALESCE(write_off_amount, 0) > 0
             AND COALESCE(write_off_amount, 0) < COALESCE(claim_amount, 0) AND flow_status != 2)
         OR (COALESCE(write_off_amount, 0) > 0
             AND COALESCE(write_off_amount, 0) = COALESCE(claim_amount, 0) AND flow_status != 3)
    ))
  )
ORDER BY flow_status, id;


-- ----------------------------------------------------------
-- 三、数据异常检查（全量）
-- ----------------------------------------------------------

-- 3.1 原票认领金额超过总金额
SELECT id, voucher_flow_code, amount, claim_amount, '原票认领金额超限'
FROM db_pms.ts_voucher_flow_bill
WHERE is_original = 1 AND COALESCE(claim_amount, 0) > COALESCE(amount, 0);

-- 3.2 副卡核销金额超过认领金额
SELECT id, voucher_flow_code, claim_amount, write_off_amount, '副卡核销金额超限'
FROM db_pms.ts_voucher_flow_bill
WHERE is_original = 0
  AND COALESCE(write_off_amount, 0) > COALESCE(claim_amount, 0);

-- 3.3 审批通过但核销中金额未清零
SELECT id, voucher_flow_code, status, write_offing_amount, '审批通过但核销中金额>0'
FROM db_pms.ts_voucher_flow_bill
WHERE status = 3 AND COALESCE(write_offing_amount, 0) > 0;

-- 3.4 副卡金额为0
SELECT id, voucher_flow_code, amount, claim_amount, '副卡金额为0'
FROM db_pms.ts_voucher_flow_bill
WHERE is_original = 0 AND COALESCE(amount, 0) = 0;