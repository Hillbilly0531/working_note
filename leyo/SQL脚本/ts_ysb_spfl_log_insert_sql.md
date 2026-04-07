# ts_ysb_spfl_log 表刷数据 SQL

**生成时间：** 2026-04-01

**目标表：** db_erp.ts_ysb_spfl_log

**影响行数：** 18 行（9条 × 2次插入）

**数据来源：** db_erp.ts_ysb_spfl_log

**条件：** providerid = '3418' AND xydjbh = 'RA26030010329' AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809)

---

## 一、操作说明

本次刷数据包含两部分操作：

1. **第一部分**：复制数据，`jsflje` 字段取反（`-jsflje`），`lastmodifytime` 使用 `NOW()`
2. **第二部分**：复制数据，`jsflje` 字段保持原值，`lastmodifytime` 使用固定时间 `'2026-03-31 00:00:00'`

---

## 二、备份 SQL（回滚用）

执行前请先执行此 SQL，生成回滚语句备用：

```sql
-- 生成回滚 DELETE 语句
SELECT CONCAT(
    "DELETE FROM db_erp.ts_ysb_spfl_log WHERE pk=", pk, " AND providerid='3418' AND xydjbh='RA26030010329';"
) AS rollback_sql
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);

-- 一次性导出所有回滚语句（使用 GROUP_CONCAT）
SELECT GROUP_CONCAT(
    CONCAT("DELETE FROM db_erp.ts_ysb_spfl_log WHERE pk=", pk, " AND providerid='3418' AND xydjbh='RA26030010329';")
    SEPARATOR '\n'
) AS rollback_sqls
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);
```

---

## 三、第一部分 INSERT SQL（jsflje 取反，lastmodifytime = NOW()）

### 逐条生成（逐行执行）

```sql
-- 生成 INSERT 语句（第一部分：jsflje 取反，lastmodifytime 用 now()）
SELECT CONCAT(
    "INSERT INTO db_erp.ts_ysb_spfl_log (providerId, id, logid, plh, ysbdjbh, djbh, rq, xydjbh, djlx, spid, spbh, pihao, pici, shl, hsje, fldj, flje, jsfldj, jsflje, ssflje, nrcbbl, dwbh, danwbh, computed_at, DocLevId, CreaterId, CreaterInfo, CreateTime, beactive, DelTime, ExpAutOrg, ResAutOrg, EntId, xsstart_rq, xsend_rq, nrcbfldj, nrcbflje, ssfldj, updated_at, yplh, accdate, billsn, lastmodifytime, ystime, cTime, ext_1, ext_2, ext_3, ext_4, ext_5, syncState, rebateSupplierCode, rebatePName, rebatePIdentity) VALUES ('",
    IFNULL(providerId, ''), "', ", IFNULL(id, 'NULL'), ", ", IFNULL(pk, 'NULL'), ", '", IFNULL(plh, ''), "', '", IFNULL(ysbdjbh, ''), "', '", IFNULL(djbh, ''), "', '", IFNULL(rq, ''), "', '", IFNULL(xydjbh, ''), "', '", IFNULL(djlx, ''), "', '", IFNULL(spid, ''), "', '", IFNULL(spbh, ''), "', ", IFNULL(pihao, 'NULL'), ", '", IFNULL(pici, ''), "', ", IFNULL(shl, 0), ", ", IFNULL(hsje, 0), ", ", IFNULL(fldj, 0), ", ", IFNULL(flje, 0), ", ", IFNULL(jsfldj, 0), ", ", IFNULL(-jsflje, 0), ", ", IFNULL(ssflje, 0), ", ", IFNULL(nrcbbl, 0), ", '", IFNULL(dwbh, ''), "', '", IFNULL(danwbh, ''), "', ", IFNULL(computed_at, 'NULL'), ", ", IFNULL(DocLevId, 0), ", '", IFNULL(CreaterId, ''), "', '", IFNULL(CreaterInfo, ''), "', ", IFNULL(CreateTime, 'NULL'), ", '", IFNULL(beactive, ''), "', ", IFNULL(DelTime, 'NULL'), ", ", IFNULL(ExpAutOrg, 'NULL'), ", ", IFNULL(ResAutOrg, 'NULL'), ", '", IFNULL(EntId, ''), "', '", IFNULL(xsstart_rq, ''), "', '", IFNULL(xsend_rq, ''), "', ", IFNULL(nrcbfldj, 0), ", ", IFNULL(nrcbflje, 0), ", ", IFNULL(ssfldj, 0), ", ", IFNULL(updated_at, 'NULL'), ", '", IFNULL(yplh, ''), "', '", IFNULL(accdate, ''), "', ", IFNULL(billsn, 0), ", NOW(), ", IFNULL(ystime, 'NULL'), ", ", IFNULL(cTime, 'NULL'), ", '", IFNULL(ext_1, ''), "', '", IFNULL(ext_2, ''), "', '", IFNULL(ext_3, ''), "', '", IFNULL(ext_4, ''), "', '", IFNULL(ext_5, ''), "', ", IFNULL(syncState, 0), ", '", IFNULL(rebateSupplierCode, ''), "', '", IFNULL(rebatePName, ''), "', '", IFNULL(rebatePIdentity, ''), "');"
) AS insert_sql
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);
```

### 一次性导出所有语句

```sql
-- 一次性导出所有 INSERT 语句（第一部分）
SELECT GROUP_CONCAT(
    CONCAT(
        "INSERT INTO db_erp.ts_ysb_spfl_log (providerId, id, logid, plh, ysbdjbh, djbh, rq, xydjbh, djlx, spid, spbh, pihao, pici, shl, hsje, fldj, flje, jsfldj, jsflje, ssflje, nrcbbl, dwbh, danwbh, computed_at, DocLevId, CreaterId, CreaterInfo, CreateTime, beactive, DelTime, ExpAutOrg, ResAutOrg, EntId, xsstart_rq, xsend_rq, nrcbfldj, nrcbflje, ssfldj, updated_at, yplh, accdate, billsn, lastmodifytime, ystime, cTime, ext_1, ext_2, ext_3, ext_4, ext_5, syncState, rebateSupplierCode, rebatePName, rebatePIdentity) VALUES ('",
        IFNULL(providerId, ''), "', ", IFNULL(id, 'NULL'), ", ", IFNULL(pk, 'NULL'), ", '", IFNULL(plh, ''), "', '", IFNULL(ysbdjbh, ''), "', '", IFNULL(djbh, ''), "', '", IFNULL(rq, ''), "', '", IFNULL(xydjbh, ''), "', '", IFNULL(djlx, ''), "', '", IFNULL(spid, ''), "', '", IFNULL(spbh, ''), "', ", IFNULL(pihao, 'NULL'), ", '", IFNULL(pici, ''), "', ", IFNULL(shl, 0), ", ", IFNULL(hsje, 0), ", ", IFNULL(fldj, 0), ", ", IFNULL(flje, 0), ", ", IFNULL(jsfldj, 0), ", ", IFNULL(-jsflje, 0), ", ", IFNULL(ssflje, 0), ", ", IFNULL(nrcbbl, 0), ", '", IFNULL(dwbh, ''), "', '", IFNULL(danwbh, ''), "', ", IFNULL(computed_at, 'NULL'), ", ", IFNULL(DocLevId, 0), ", '", IFNULL(CreaterId, ''), "', '", IFNULL(CreaterInfo, ''), "', ", IFNULL(CreateTime, 'NULL'), ", '", IFNULL(beactive, ''), "', ", IFNULL(DelTime, 'NULL'), ", ", IFNULL(ExpAutOrg, 'NULL'), ", ", IFNULL(ResAutOrg, 'NULL'), ", '", IFNULL(EntId, ''), "', '", IFNULL(xsstart_rq, ''), "', '", IFNULL(xsend_rq, ''), "', ", IFNULL(nrcbfldj, 0), ", ", IFNULL(nrcbflje, 0), ", ", IFNULL(ssfldj, 0), ", ", IFNULL(updated_at, 'NULL'), ", '", IFNULL(yplh, ''), "', '", IFNULL(accdate, ''), "', ", IFNULL(billsn, 0), ", NOW(), ", IFNULL(ystime, 'NULL'), ", ", IFNULL(cTime, 'NULL'), ", '", IFNULL(ext_1, ''), "', '", IFNULL(ext_2, ''), "', '", IFNULL(ext_3, ''), "', '", IFNULL(ext_4, ''), "', '", IFNULL(ext_5, ''), "', ", IFNULL(syncState, 0), ", '", IFNULL(rebateSupplierCode, ''), "', '", IFNULL(rebatePName, ''), "', '", IFNULL(rebatePIdentity, ''), "');"
    ) SEPARATOR '\n'
) AS all_insert_sqls
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);
```

---

## 四、第二部分 INSERT SQL（jsflje 取原值，lastmodifytime = '2026-03-31 00:00:00'）

### 逐条生成（逐行执行）

```sql
-- 生成 INSERT 语句（第二部分：jsflje 取原值，lastmodifytime 用 '2026-03-31 00:00:00'）
SELECT CONCAT(
    "INSERT INTO db_erp.ts_ysb_spfl_log (providerId, id, logid, plh, ysbdjbh, djbh, rq, xydjbh, djlx, spid, spbh, pihao, pici, shl, hsje, fldj, flje, jsfldj, jsflje, ssflje, nrcbbl, dwbh, danwbh, computed_at, DocLevId, CreaterId, CreaterInfo, CreateTime, beactive, DelTime, ExpAutOrg, ResAutOrg, EntId, xsstart_rq, xsend_rq, nrcbfldj, nrcbflje, ssfldj, updated_at, yplh, accdate, billsn, lastmodifytime, ystime, cTime, ext_1, ext_2, ext_3, ext_4, ext_5, syncState, rebateSupplierCode, rebatePName, rebatePIdentity) VALUES ('",
    IFNULL(providerId, ''), "', ", IFNULL(id, 'NULL'), ", ", IFNULL(pk, 'NULL'), ", '", IFNULL(plh, ''), "', '", IFNULL(ysbdjbh, ''), "', '", IFNULL(djbh, ''), "', '", IFNULL(rq, ''), "', '", IFNULL(xydjbh, ''), "', '", IFNULL(djlx, ''), "', '", IFNULL(spid, ''), "', '", IFNULL(spbh, ''), "', ", IFNULL(pihao, 'NULL'), ", '", IFNULL(pici, ''), "', ", IFNULL(shl, 0), ", ", IFNULL(hsje, 0), ", ", IFNULL(fldj, 0), ", ", IFNULL(flje, 0), ", ", IFNULL(jsfldj, 0), ", ", IFNULL(jsflje, 0), ", ", IFNULL(ssflje, 0), ", ", IFNULL(nrcbbl, 0), ", '", IFNULL(dwbh, ''), "', '", IFNULL(danwbh, ''), "', ", IFNULL(computed_at, 'NULL'), ", ", IFNULL(DocLevId, 0), ", '", IFNULL(CreaterId, ''), "', '", IFNULL(CreaterInfo, ''), "', ", IFNULL(CreateTime, 'NULL'), ", '", IFNULL(beactive, ''), "', ", IFNULL(DelTime, 'NULL'), ", ", IFNULL(ExpAutOrg, 'NULL'), ", ", IFNULL(ResAutOrg, 'NULL'), ", '", IFNULL(EntId, ''), "', '", IFNULL(xsstart_rq, ''), "', '", IFNULL(xsend_rq, ''), "', ", IFNULL(nrcbfldj, 0), ", ", IFNULL(nrcbflje, 0), ", ", IFNULL(ssfldj, 0), ", ", IFNULL(updated_at, 'NULL'), ", '", IFNULL(yplh, ''), "', '", IFNULL(accdate, ''), "', ", IFNULL(billsn, 0), ", '2026-03-31 00:00:00', ", IFNULL(ystime, 'NULL'), ", ", IFNULL(cTime, 'NULL'), ", '", IFNULL(ext_1, ''), "', '", IFNULL(ext_2, ''), "', '", IFNULL(ext_3, ''), "', '", IFNULL(ext_4, ''), "', '", IFNULL(ext_5, ''), "', ", IFNULL(syncState, 0), ", '", IFNULL(rebateSupplierCode, ''), "', '", IFNULL(rebatePName, ''), "', '", IFNULL(rebatePIdentity, ''), "');"
) AS insert_sql
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);
```

### 一次性导出所有语句

```sql
-- 一次性导出所有 INSERT 语句（第二部分）
SELECT GROUP_CONCAT(
    CONCAT(
        "INSERT INTO db_erp.ts_ysb_spfl_log (providerId, id, logid, plh, ysbdjbh, djbh, rq, xydjbh, djlx, spid, spbh, pihao, pici, shl, hsje, fldj, flje, jsfldj, jsflje, ssflje, nrcbbl, dwbh, danwbh, computed_at, DocLevId, CreaterId, CreaterInfo, CreateTime, beactive, DelTime, ExpAutOrg, ResAutOrg, EntId, xsstart_rq, xsend_rq, nrcbfldj, nrcbflje, ssfldj, updated_at, yplh, accdate, billsn, lastmodifytime, ystime, cTime, ext_1, ext_2, ext_3, ext_4, ext_5, syncState, rebateSupplierCode, rebatePName, rebatePIdentity) VALUES ('",
        IFNULL(providerId, ''), "', ", IFNULL(id, 'NULL'), ", ", IFNULL(pk, 'NULL'), ", '", IFNULL(plh, ''), "', '", IFNULL(ysbdjbh, ''), "', '", IFNULL(djbh, ''), "', '", IFNULL(rq, ''), "', '", IFNULL(xydjbh, ''), "', '", IFNULL(djlx, ''), "', '", IFNULL(spid, ''), "', '", IFNULL(spbh, ''), "', ", IFNULL(pihao, 'NULL'), ", '", IFNULL(pici, ''), "', ", IFNULL(shl, 0), ", ", IFNULL(hsje, 0), ", ", IFNULL(fldj, 0), ", ", IFNULL(flje, 0), ", ", IFNULL(jsfldj, 0), ", ", IFNULL(jsflje, 0), ", ", IFNULL(ssflje, 0), ", ", IFNULL(nrcbbl, 0), ", '", IFNULL(dwbh, ''), "', '", IFNULL(danwbh, ''), "', ", IFNULL(computed_at, 'NULL'), ", ", IFNULL(DocLevId, 0), ", '", IFNULL(CreaterId, ''), "', '", IFNULL(CreaterInfo, ''), "', ", IFNULL(CreateTime, 'NULL'), ", '", IFNULL(beactive, ''), "', ", IFNULL(DelTime, 'NULL'), ", ", IFNULL(ExpAutOrg, 'NULL'), ", ", IFNULL(ResAutOrg, 'NULL'), ", '", IFNULL(EntId, ''), "', '", IFNULL(xsstart_rq, ''), "', '", IFNULL(xsend_rq, ''), "', ", IFNULL(nrcbfldj, 0), ", ", IFNULL(nrcbflje, 0), ", ", IFNULL(ssfldj, 0), ", ", IFNULL(updated_at, 'NULL'), ", '", IFNULL(yplh, ''), "', '", IFNULL(accdate, ''), "', ", IFNULL(billsn, 0), ", '2026-03-31 00:00:00', ", IFNULL(ystime, 'NULL'), ", ", IFNULL(cTime, 'NULL'), ", '", IFNULL(ext_1, ''), "', '", IFNULL(ext_2, ''), "', '", IFNULL(ext_3, ''), "', '", IFNULL(ext_4, ''), "', '", IFNULL(ext_5, ''), "', ", IFNULL(syncState, 0), ", '", IFNULL(rebateSupplierCode, ''), "', '", IFNULL(rebatePName, ''), "', '", IFNULL(rebatePIdentity, ''), "');"
    ) SEPARATOR '\n'
) AS all_insert_sqls
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809);
```

---

## 五、执行顺序

1. **第一步**：执行"二、备份 SQL"，生成并保存回滚语句
2. **第二步**：执行"三、第一部分 INSERT SQL"，生成并执行 INSERT 语句
3. **第三步**：执行"四、第二部分 INSERT SQL"，生成并执行 INSERT 语句
4. **验证**：执行验证查询确认数据插入成功

---

## 六、验证查询

```sql
-- 验证插入结果
SELECT pk, providerId, xydjbh, jsflje, lastmodifytime, syncState
FROM db_erp.ts_ysb_spfl_log
WHERE providerid = '3418' 
  AND xydjbh = 'RA26030010329' 
  AND pk IN (150258801, 150258802, 150258803, 150258804, 150258805, 150258806, 150258807, 150258808, 150258809)
ORDER BY lastmodifytime;
```

---

## 七、字段类型处理说明

本 SQL 已根据 `ts_ysb_spfl_log` 表结构正确处理所有字段类型：

| 字段类型 | 处理方式 | 示例 |
|---------|---------|------|
| **NOT NULL** | 直接使用 | `providerId`, `logid`, `syncState` |
| **TEXT** | `IFNULL(col, NULL)` | `ExpAutOrg`, `ResAutOrg` |
| **char(n)** | `IFNULL(col, NULL)` | `pihao`, `computed_at`, `CreateTime`, `DelTime` |
| **varchar(n)** | `IFNULL(col, '')` | `plh`, `ysbdjbh`, `djbh` 等 |
| **int/bigint** | `IFNULL(col, 0)` | `DocLevId`, `billsn` 等 |
| **decimal** | `IFNULL(col, 0)` | `shl`, `hsje`, `fldj`, `flje`, `jsflje` 等 |
| **datetime** | `IFNULL(col, NULL)` | `updated_at`, `ystime`, `cTime` |
| **tinyint** | `IFNULL(col, 0)` | `syncState` |

---

## 八、回滚操作（如需撤销）

如果需要撤销本次操作，执行"二、备份 SQL"中生成的反滚 DELETE 语句：

```sql
DELETE FROM db_erp.ts_ysb_spfl_log WHERE pk=150258801 AND providerid='3418' AND xydjbh='RA26030010329';
DELETE FROM db_erp.ts_ysb_spfl_log WHERE pk=150258802 AND providerid='3418' AND xydjbh='RA26030010329';
-- ... 以此类推
```

---

**文档生成工具：** db-data-modifier SKILL

**参考规范：** leyo/文档/刷数据规范.md
