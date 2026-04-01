---
name: "db-data-modifier"
description: "基于公司数据库刷数据规范，优化SQL语句并生成规范的邮件申请模板。Invoke when user provides INSERT/UPDATE/DELETE statements that need to be formatted according to company database modification standards."
---

# 数据库刷数据工具

这是一个基于公司数据库刷数据规范的 SQL 优化和邮件生成工具，帮助开发人员快速生成符合规范的 SQL 语句和邮件申请模板。

## ⚠️ 重要前置步骤（必须先执行）

**在生成任何 SQL 语句之前，必须先获取目标表的表结构！**

### 为什么需要表结构？

1. **字段类型匹配**：不同的字段类型（varchar/char/text/datetime/int/decimal等）需要不同的 IFNULL 处理方式
2. **避免 SQL 错误**：错误的字段类型处理会导致执行失败
3. **NULL 值处理**：根据字段是否允许 NULL，选择正确的默认值

### 获取表结构的 SQL

```sql
-- 方式1：查看表结构（推荐）
DESCRIBE 数据库名.表名;

-- 方式2：查看完整建表语句
SHOW CREATE TABLE 数据库名.表名;

-- 方式3：查询 information_schema
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = '数据库名' AND TABLE_NAME = '表名'
ORDER BY ORDINAL_POSITION;
```

### 字段类型处理规则

| 字段类型 | IFNULL 处理 | 示例 | 说明 |
|---------|------------|------|------|
| **NOT NULL** | 直接使用（不加 IFNULL） | `providerId` | 必须有值，不能为 NULL |
| **TEXT** | `IFNULL(col, NULL)` | `IFNULL(remark, NULL)` | TEXT 类型不能用 '' |
| **char(n)** | `IFNULL(col, NULL)` | `IFNULL(status, NULL)` | char 类型不能用 '' |
| **varchar(n)** | `IFNULL(col, '')` | `IFNULL(name, '')` | varchar 可以用 '' |
| **int/bigint** | `IFNULL(col, 0)` | `IFNULL(id, 0)` | 数值型用 0 |
| **decimal** | `IFNULL(col, 0)` | `IFNULL(amount, 0)` | 数值型用 0 |
| **datetime/timestamp** | `IFNULL(col, NULL)` | `IFNULL(create_time, NULL)` | 时间型用 NULL |
| **tinyint** | `IFNULL(col, 0)` | `IFNULL(is_active, 0)` | 数值型用 0 |
| **double/float** | `IFNULL(col, 0)` | `IFNULL(rate, 0)` | 数值型用 0 |
| **date** | `IFNULL(col, NULL)` | `IFNULL(birth_date, NULL)` | 日期型用 NULL |

**关键点：**
- ❌ **不能用 `'NULL'` 字符串**：这会导致类型错误，应该是 `NULL`（无引号）
- ❌ **TEXT/char 不能用 `''`**：必须用 `NULL`
- ✅ **数值型用 `0`**：如 `IFNULL(col, 0)`
- ✅ **NOT NULL 字段不加 IFNULL**：确保不会传入 NULL

---

## 核心规范要点

### 1. SQL 语句基本要求

- **必须单行执行**且命中主键或唯一索引
- **禁止无 WHERE 条件**或使用非限制性条件（如模糊查询）执行更新或删除
- **数据值要求显式体现在 SQL 中**
- **禁止联表更新（UPDATE）和联表删除（DELETE）**
- 错误示例：
  ```sql
  -- 联表更新（禁止）
  UPDATE db_info.ts_businessdoc a 
  JOIN db_info.ts_clientdoc b ON a.provider_id=b.provider_id 
  SET a.businesscode='bdwe234' WHERE a.id=2324;

  -- 联表删除（禁止）
  DELETE a FROM db_info.ts_businessdoc a 
  JOIN db_info.ts_clientdoc b ON a.provider_id=b.provider_id 
  WHERE a.id=2324;
  ```
- 正确示例：
  ```sql
  -- 单表更新
  UPDATE db_info.ts_businessdoc SET businesscode='bdwe234' WHERE id=2324;

  -- 单表删除
  DELETE FROM db_info.ts_businessdoc WHERE id=2324;
  ```

### 2. 备份要求

必须选择一种备份方式：
1. **导出 Excel**：导出修改前数据生成 Excel，适用于文件小于 50MB
2. **历史表留存**：在 tidb db_import 库插入历史表
3. **INSERT 语句备份**：将删除的数据复制为 INSERT 语句，适用于行数小于 50 行

**INSERT 操作的备份策略（特殊情况）：**

- INSERT 操作本身不需要"备份前数据"
- 但需要准备**回滚方案**（DELETE 语句）以应对插入错误
- 建议生成对应的 DELETE 语句用于紧急回滚
- 对于重要数据插入，建议准备完整的 INSERT 语句以便重新执行
- **INSERT 语句必须使用 `SELECT CONCAT` 形式生成**，禁止直接手写 INSERT 语句

### 3. TAPD 链接要求

除修改历史数据且一次性修改外，**必须提供 TAPD 链接**。

### 4. 审批流程

1. 申请人提交邮件
2. 开发组长审核
3. DBA 复核和执行脚本
4. DBA 邮件回复执行结果

---

## 使用流程

### 步骤 1：用户提供目标表结构

**必须先执行！** 用户需要提供以下信息：
1. **目标表名**：如 `db_erp.ts_ysb_spfl_log`
2. **表结构**：使用 `DESCRIBE 表名` 或 `SHOW CREATE TABLE 表名` 获取
3. **原始 SQL**：需要执行的 INSERT/UPDATE/DELETE 语句

### 步骤 2：分析 SQL 类型

识别 SQL 操作类型：
- **INSERT**：插入新数据
- **UPDATE**：更新现有数据
- **DELETE**：删除数据
- **批量修复**：复杂的数据修改场景

### 步骤 3：检查并优化 SQL

按照规范检查并优化：

1. **检查是否命中主键或唯一索引**
   - 如果原 SQL 没有 WHERE 条件或使用模糊查询，需要补充
   - 如果原 SQL 使用联表操作，需要拆分为单表操作

2. **生成规范的单行 SQL**
   - 每个 SQL 单独一行
   - 显式写出数据值
   - 确保有 WHERE 条件且命中索引
   - **根据表结构字段类型，正确使用 IFNULL 处理 NULL 值**

3. **生成备份 SQL**
   - 对于 UPDATE：生成对应的 SELECT 语句查看修改前数据
   - 对于 DELETE：生成对应的 INSERT 语句用于恢复
   - 对于 INSERT：生成对应的 SELECT 或 DELETE 语句

### 步骤 4：生成邮件模板

按照标准格式生成邮件，包括：
- 标题
- 申请原因
- 操作类型
- 目标表
- 影响行数
- SQL 脚本
- TAPD 链接
- Bug 状态
- Bug 预期解决时间
- 是否排查全量历史数据

---

## 邮件申请模板

```markdown
标题：【刷数据】xxxxxx

xxxx：

现申请一次刷数据操作，具体信息如下，烦请协助审批或安排执行。

**申请原因：**
（描述数据修改的原因和背景）

**操作类型：**
更新（UPDATE）/ 插入（INSERT）/ 删除（DELETE）/ 批量修复

**目标表：**
db_name.table_name

**影响行数：**
（预计影响的行数）

**sql脚本：**
（按照规范格式的 SQL 语句）

**tapd链接：**
（如果适用）

**bug状态：**
（Bug 的当前状态）

**bug预期解决时间：**
（预计完成时间）

**是否排查全量历史数据：**
（是/否）
```

---

## 输出示例

### 示例 1：UPDATE 语句优化

**用户提供的信息：**
- 目标表：`db_info.ts_goodsdoc`
- 表结构：
  ```
  id: bigint(20), NOT NULL, PRI
  goodscode: varchar(50), NOT NULL
  goodsname: varchar(200), YES
  status: char(1), NOT NULL, DEFAULT 'Y'
  createtime: datetime, YES
  mtime: timestamp, NOT NULL, DEFAULT CURRENT_TIMESTAMP
  ```

**原始 SQL（不符合规范）：**
```sql
UPDATE goods SET status='N' WHERE name LIKE '%test%'
```

**优化后（符合规范）：**
```sql
-- 先查询需要修改的数据
SELECT id, goodscode, goodsname, status FROM db_info.ts_goodsdoc WHERE goodsname LIKE '%test%';

-- 生成规范的单行 UPDATE 语句（根据表结构使用正确的 IFNULL 处理）
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1234;
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1235;
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1236;
```

**生成邮件：**
```markdown
标题：【刷数据】禁用名称包含'test'的商品数据

xxx：

现申请一次刷数据操作，具体信息如下，烦请协助审批或安排执行。

**申请原因：**
清理测试数据，需要禁用名称包含'test'的商品

**操作类型：**
更新（UPDATE）

**目标表：**
db_info.ts_goodsdoc

**影响行数：**
3

**sql脚本：**
-- 先查询需要修改的数据
SELECT id, goodscode, goodsname, status FROM db_info.ts_goodsdoc WHERE goodsname LIKE '%test%';

-- 生成规范的单行 UPDATE 语句
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1234;
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1235;
UPDATE db_info.ts_goodsdoc SET status='N', mtime=NOW() WHERE id=1236;

**tapd链接：**
https://www.tapd.cn/xxx（如果适用）

**bug状态：**
（Bug 的当前状态）

**bug预期解决时间：**
（预计完成时间）

**是否排查全量历史数据：**
（是/否）
```

### 示例 2：使用 SELECT CONCAT 生成 UPDATE（需要表结构）

**用户提供的信息：**
- 目标表：`db_erp.ts_ysb_spfl_log`
- 表结构：
  ```
  pk: bigint(20), NOT NULL, PRI, AUTO_INCREMENT
  ysb_bill_code: varchar(50), YES
  djlx: char(3), YES
  rq: datetime, YES
  spid: bigint(20), YES
  spbh: varchar(50), YES
  pihao: char(20), YES
  pici: int(11), YES
  dwbh: bigint(20), YES
  danwbh: varchar(50), YES
  DocLevId: bigint(20), YES
  CreateTime: datetime, YES
  beactive: tinyint(1), NOT NULL, DEFAULT 1
  updated_at: timestamp, NOT NULL, DEFAULT CURRENT_TIMESTAMP
  accdate: date, YES
  ext_1: varchar(100), YES
  ext_2: varchar(100), YES
  ext_3: int(11), YES
  ext_4: varchar(100), YES
  ext_5: bigint(20), YES
  rebateSupplierCode: varchar(50), YES
  rebatePName: varchar(100), YES
  rebatePIdentity: varchar(100), YES
  jsflje: decimal(18,2), YES
  ```

**生成的 SELECT CONCAT UPDATE 语句：**
```sql
-- 根据表结构生成 UPDATE 语句（注意 IFNULL 处理方式）
SELECT CONCAT(
    "UPDATE db_erp.ts_ysb_spfl_log SET ",
    "ysb_bill_code = ", IFNULL(CONCAT("'", b.receive_bill_code, "'"), 'NULL'), ", ",
    "djlx = ", IFNULL(CONCAT("'", SUBSTR(b.bill_code, 1, 3), "'"), 'NULL'), ", ",
    "rq = ", IFNULL(CONCAT("'", b.dates, "'"), 'NULL'), ", ",
    "spid = ", IFNULL(b.goods_id, 0), ", ",
    "spbh = ", IFNULL(CONCAT("'", b.goods_code, "'"), 'NULL'), ", ",
    "pihao = ", IFNULL(CONCAT("'", b.batch_code, "'"), 'NULL'), ", ",
    "pici = ", IFNULL(b.angle_id, 0), ", ",
    "dwbh = ", IFNULL(b.supplierid, 0), ", ",
    "danwbh = ", IFNULL(CONCAT("'", b.suppliercode, "'"), 'NULL'), ", ",
    "DocLevId = ", IFNULL(b.id, 0), ", ",
    "CreateTime = ", IFNULL(CONCAT("'", b.CreateTime, "'"), 'NULL'), ", ",
    "beactive = 1, ",
    "updated_at = NOW(), ",
    "accdate = ", IFNULL(CONCAT("'", b.acc_date, "'"), 'NULL'), ", ",
    "ext_1 = ", IFNULL(CONCAT("'", d.agreement_method, "'"), 'NULL'), ", ",
    "ext_2 = ", IFNULL(CONCAT("'", d.ysb_rebate_supplier, "'"), 'NULL'), ", ",
    "ext_3 = 0, ",
    "ext_4 = ", IFNULL(CONCAT("'", e.rebate_person, "'"), 'NULL'), ", ",
    "ext_5 = ", IFNULL(c.contactor_id, 0), ", ",
    "rebateSupplierCode = ", IFNULL(CONCAT("'", d.rebate_supplier_code, "'"), 'NULL'), ", ",
    "rebatePName = ", IFNULL(CONCAT("'", d.rebate_person_identity, "'"), 'NULL'), ", ",
    "rebatePIdentity = ", IFNULL(CONCAT("'", d.rebate_person_name, "'"), 'NULL'), ", ",
    "jsflje = ", IFNULL(b.jsflje, 0), " ",
    "WHERE pk = ", a.pk, ";"
) AS update_sql
FROM db_erp.ts_ysb_spfl_log a
LEFT JOIN db_biz_dc.ts_rebate_receive b ON a.providerId = b.provider_id AND a.xydjbh = b.receive_bill_code AND a.djbh = b.bill_code AND a.billsn = b.bill_sn
JOIN db_biz_dc.ts_rebate_agreement d ON b.provider_id = d.provider_id AND b.receive_bill_code = d.bill_code
LEFT JOIN db_pms.ts_drug_operator c ON c.providerId = b.provider_id AND c.prov_drug_code = b.goods_code
JOIN db_pms.ts_rebate e ON e.id = d.rebate_id
WHERE a.pk IN (148227999, 148228000, ...);
```

**注意：**
- `varchar` 类型使用 `IFNULL(col, '')`
- `char` 类型使用 `IFNULL(col, NULL)`
- `datetime/date` 类型使用 `IFNULL(col, NULL)`
- `int/bigint` 类型使用 `IFNULL(col, 0)`
- `decimal` 类型使用 `IFNULL(col, 0)`
- `tinyint` 类型使用 `IFNULL(col, 0)`
- `NOT NULL` 字段（如 beactive, updated_at）不需要 IFNULL

### 示例 3：DELETE 语句优化

**原始需求：**
删除 goods 表中 id 为 1001, 1002, 1003 的记录

**优化后：**
```sql
-- 先备份数据（生成 INSERT 语句）
SELECT CONCAT("INSERT INTO db_info.ts_goodsdoc (id, name, status) VALUES (", id, ", '", name, "', '", status, "');") 
FROM db_info.ts_goodsdoc WHERE id IN (1001, 1002, 1003);

-- 生成规范的单行 DELETE 语句
DELETE FROM db_info.ts_goodsdoc WHERE id=1001;
DELETE FROM db_info.ts_goodsdoc WHERE id=1002;
DELETE FROM db_info.ts_goodsdoc WHERE id=1003;
```

### 示例 4：INSERT 语句优化

INSERT 语句同样需要遵循规范，使用 `SELECT CONCAT` 形式生成规范化 SQL。

**规范格式：**
```sql
SELECT CONCAT("INSERT INTO 数据库名.表名 (字段1, 字段2, 字段3) VALUES ('", 字段1值, "', '", 字段2值, "', '", 字段3值, "');") FROM 数据来源表 WHERE 条件;
```

**⚠️ NULL 值处理（重要）：**

当字段值为 NULL 时，`CONCAT` 函数会返回 NULL，导致生成的 SQL 不完整。

**解决方案：使用 `IFNULL` 函数处理 NULL 值**

**重要：必须根据字段类型选择正确的默认值！**

```sql
-- 错误示例 1：字段为 NULL 时整个结果为 NULL
SELECT CONCAT("INSERT INTO table (col1, col2) VALUES ('", col1, "', '", col2, "');") 
FROM table WHERE id=1;
-- 如果 col1='aaa', col2=NULL，结果是 NULL！

-- 错误示例 2：数值字段使用 'NULL' 字符串（会导致类型错误）
SELECT CONCAT("INSERT INTO table (col1, col2) VALUES (", IFNULL(col1, 'NULL'), ", ", IFNULL(col2, 'NULL'), ");") 
FROM table WHERE id=1;
-- 如果 col1=123, col2=NULL，结果是 "INSERT INTO table (col1, col2) VALUES (123, NULL);"
-- ❌ 错误：NULL 不是字符串 'NULL'

-- 错误示例 3：TEXT/char 类型使用 '' 空字符串（会导致类型错误）
SELECT CONCAT("INSERT INTO table (col1, col2) VALUES ('", IFNULL(col1, ''), "', '", IFNULL(col2, ''), "');") 
FROM table WHERE id=1;
-- 如果 col1 是 TEXT 类型，col2=NULL，结果可能是错误

-- 正确示例：根据字段类型选择正确的默认值
SELECT CONCAT("INSERT INTO table (id, name, amount, created_at, description) VALUES (", 
    IFNULL(id, 0), ", '", IFNULL(name, ''), "', ", IFNULL(amount, 0), ", ", IFNULL(created_at, 'NULL'), ", ", IFNULL(description, 'NULL'), ");") 
FROM table WHERE id=1;
```

**场景 1：从备份表批量插入商品数据**

**原始需求：**
将 db_info.ts_goodsdoc_backup 备份表中的商品数据恢复到 db_info.ts_goodsdoc 表

**优化后：**
```sql
-- 首先生成 INSERT 语句（使用 SELECT CONCAT）
SELECT CONCAT(
    "INSERT INTO db_info.ts_goodsdoc (goodscode, goodsname, beactive, createtime, mtime) VALUES ('",
    goodscode, "', '", goodsname, "', '", beactive, "', NOW(), NOW());"
) AS insert_sql
FROM db_info.ts_goodsdoc_backup
WHERE beactive = 'Y';

-- 如果需要一次性导出所有语句（使用 GROUP_CONCAT）
SELECT GROUP_CONCAT(
    CONCAT(
        "INSERT INTO db_info.ts_goodsdoc (goodscode, goodsname, beactive, createtime, mtime) VALUES ('",
        goodscode, "', '", goodsname, "', '", beactive, "', NOW(), NOW());"
    ) SEPARATOR '\n'
) AS all_insert_sqls
FROM db_info.ts_goodsdoc_backup
WHERE beactive = 'Y';
```

**场景 2：根据指定条件批量插入订单数据**

**原始需求：**
为指定客户批量插入订单记录

**优化后：**
```sql
-- 先生成 INSERT 语句
SELECT CONCAT(
    "INSERT INTO db_info.ts_orderdoc (ordercode, customerid, orderamount, status, createtime) VALUES ('",
    ordercode, "', ", customerid, ", ", orderamount, ", 'PENDING', NOW());"
) AS insert_sql
FROM (
    SELECT 'ORD20260401001' AS ordercode, 1001 AS customerid, 1000.00 AS orderamount
    UNION ALL
    SELECT 'ORD20260401002' AS ordercode, 1002 AS customerid, 2000.00 AS orderamount
    UNION ALL
    SELECT 'ORD20260401003' AS ordercode, 1003 AS customerid, 3000.00 AS orderamount
) AS new_orders;

-- 导出所有语句
SELECT GROUP_CONCAT(
    CONCAT(
        "INSERT INTO db_info.ts_orderdoc (ordercode, customerid, orderamount, status, createtime) VALUES ('",
        ordercode, "', ", customerid, ", ", orderamount, ", 'PENDING', NOW());"
    ) SEPARATOR '\n'
) AS all_insert_sqls
FROM (
    SELECT 'ORD20260401001' AS ordercode, 1001 AS customerid, 1000.00 AS orderamount
    UNION ALL
    SELECT 'ORD20260401002' AS ordercode, 1002 AS customerid, 2000.00 AS orderamount
    UNION ALL
    SELECT 'ORD20260401003' AS ordercode, 1003 AS customerid, 3000.00 AS orderamount
) AS new_orders;
```

**INSERT 操作注意事项：**

1. **唯一性检查**：插入前必须确认主键或唯一索引不会冲突
   ```sql
   -- 检查重复
   SELECT id FROM db_info.ts_goodsdoc WHERE goodscode='G001';
   ```

2. **外键关联验证**：确保关联表数据存在
   ```sql
   -- 检查外键依赖
   SELECT id FROM db_info.ts_categorydoc WHERE id IN (10, 20, 30);
   ```

3. **数据格式规范**：
   - 金额字段：使用 DECIMAL 类型，避免浮点精度问题
   - 时间字段：使用 NOW() 函数或标准时间格式
   - 字符串字段：使用单引号包裹，避免 SQL 注入

4. **批量插入策略**：
   - 如果必须使用批量插入（性能要求），建议使用规范的分隔符格式：
     ```sql
     INSERT INTO table (col1, col2) VALUES 
     ('val1', 'val2'),
     ('val3', 'val4'),
     ('val5', 'val6');
     ```
   - 但更推荐逐条插入，便于审计和问题追溯

5. **INSERT 备份策略**：
   - INSERT 操作不需要传统意义上的"备份前数据"
   - 但建议生成对应的 DELETE 语句用于回滚
   ```sql
   -- 生成回滚 DELETE 语句（如果需要撤销）
   SELECT CONCAT("DELETE FROM db_info.ts_goodsdoc WHERE goodscode='", goodscode, "';") 
   FROM db_info.ts_goodsdoc WHERE goodscode IN ('G001', 'G002', 'G003');

   -- 或者生成完整的回滚语句（使用 GROUP_CONCAT）
   SELECT GROUP_CONCAT(
       CONCAT("DELETE FROM db_info.ts_goodsdoc WHERE goodscode='", goodscode, "';")
       SEPARATOR '\n'
   ) AS rollback_sqls
   FROM db_info.ts_goodsdoc WHERE goodscode IN ('G001', 'G002', 'G003');
   ```

6. **INSERT 邮件申请内容**：
   - 需明确说明插入数据的来源和依据
   - 提供插入后的验证查询语句
   ```sql
   -- 插入后验证查询
   SELECT * FROM db_info.ts_goodsdoc WHERE goodscode IN ('G001', 'G002', 'G003');
   ```

7. **INSERT 语句规范要点**：
   - 禁止直接手写 INSERT 语句，必须通过 SELECT CONCAT 生成
   - 字段列表必须显式写出，禁止使用 `INSERT INTO table VALUES (...)` 省略字段
   - 字符串值必须使用单引号包裹
   - 数值型字段直接使用数值，不需要引号
   - 时间字段使用 NOW() 函数或标准时间格式 'YYYY-MM-DD HH:MM:SS'

---

## 注意事项

1. **资产类、敏感字段**的数据修改必须发起邮件由 DBA 进行修改
2. **涉及金额、数量**等资产类字段时需特别谨慎
3. **手机号、身份证、银行信息**等敏感字段修改需要特别说明
4. **批量修改前**务必先在测试环境验证
5. **确认备份方式**，确保数据可恢复

## 常见错误修正

### 错误 1：未获取表结构直接生成 SQL
- ❌ 错误：直接根据字段名猜测类型生成 SQL
- ✅ 正确：先执行 `DESCRIBE 表名` 获取准确字段类型

### 错误 2：字段类型处理错误
- ❌ 错误：`IFNULL(char_field, '')` 或 `IFNULL(text_field, '')`
- ✅ 正确：`IFNULL(char_field, NULL)` 或 `IFNULL(text_field, NULL)`

### 错误 3：使用模糊条件
- ❌ 错误：`UPDATE table SET col='value' WHERE name LIKE '%xxx%'`
- ✅ 正确：先查询出所有满足条件的数据，获取主键 ID，然后逐条更新
  ```sql
  SELECT id FROM table WHERE name LIKE '%xxx%';
  UPDATE table SET col='value' WHERE id=具体ID;
  ```

### 错误 4：联表操作
- ❌ 错误：`UPDATE t1 JOIN t2 ON ... SET t1.col='value' WHERE t1.id=xxx`
- ✅ 正确：拆分为两个独立的 SQL，先查询确认，再执行更新

### 错误 5：缺少备份
- ❌ 错误：直接执行修改，不做任何备份
- ✅ 正确：执行前必须选择一种备份方式

---

## 工具使用建议

1. **必须先获取表结构**：执行 `DESCRIBE 表名` 或 `SHOW CREATE TABLE 表名`
2. **先小批量测试**：先修改 1-2 条数据，验证无误后再执行全量
3. **保留原始数据**：修改前务必备份原始数据
4. **检查影响范围**：确认修改不会影响其他业务
5. **分批执行**：大量数据修改建议分批次进行
6. **沟通确认**：修改前与相关业务方确认数据准确性
