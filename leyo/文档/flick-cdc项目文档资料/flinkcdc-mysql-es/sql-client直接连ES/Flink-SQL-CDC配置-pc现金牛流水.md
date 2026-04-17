# Flink CDC + MySQL → Elasticsearch 同步配置

> 配置时间：2026-03-31
> 同步表：db_pay.ts_cash_cow_withdraw_flow（现金牛提现流水）
> 数据来源：复杂关联查询 `pc_cash_cow_flow_by_id.sql`

---

## 一、ES 索引创建语句（Kibana Dev Tools 执行）

```json
DELETE pc_cash_cow_flow

PUT pc_cash_cow_flow
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "id": { "type": "long" },
      "ctime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "mtime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "createUser": { "type": "integer" },
      "status": { "type": "integer" },
      "providerId": { "type": "keyword" },
      "lyProductCode": { "type": "keyword" },
      "provDrugCode": { "type": "keyword" },
      "bindProductInfo": { "type": "keyword" },
      "supplierCode": { "type": "keyword" },
      "batchNo": { "type": "keyword" },
      "ownerId": { "type": "long" },
      "salesAmount": { "type": "double" },
      "cashCowPrice": { "type": "double" },
      "priceTaxP1": { "type": "double" },
      "priceTaxP0": { "type": "double" },
      "profitAmount": { "type": "double" },
      "withdrawProfitSum": { "type": "double" },
      "paidAmount": { "type": "double" },
      "notPaidAmount": { "type": "double" },
      "tradeType": { "type": "integer" },
      "uscCode": { "type": "keyword" },
      "saleDetailId": { "type": "long" },
      "supplierBankId": { "type": "integer" },
      "originId": { "type": "integer" },
      "yearAndMonth": { "type": "keyword" },
      "ysbBillCode": { "type": "keyword" },
      "saleOutNo": { "type": "keyword" },
      "sourceType": { "type": "integer" },
      "salesTime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "isSelectiveProduct": { "type": "integer" },
      "isSelectiveBatch": { "type": "integer" }
    }
  }
}
```

---

## 二、Flink SQL 完整执行脚本

```sql
-- =============================================
-- 【必开】全局配置：解决 ES 不刷新、不写入问题
-- =============================================
SET execution.runtime-mode = streaming;
SET execution.detached = true;
SET execution.checkpointing.interval = 30s;
SET execution.checkpointing.timeout = 10min;
SET execution.checkpointing.tolerable-failed-checkpoints = 2;
SET table.exec.sink.upsert-materialize = NONE;

-- =============================================
-- Step 1: 创建 MySQL CDC 源表（主表：现金牛提现流水）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_cash_cow_withdraw_flow;
CREATE TABLE mysql_ts_cash_cow_withdraw_flow (
    id BIGINT,
    create_time TIMESTAMP(3),
    update_time TIMESTAMP(3),
    create_user BIGINT,
    status INT,
    ysb_provider_id STRING,
    ly_product_code STRING,
    prov_drug_code STRING,
    batch_no STRING,
    owner_id BIGINT,
    sales_amount DECIMAL(18,6),
    batch_p1_price DECIMAL(18,6),
    batch_p0_price DECIMAL(18,6),
    cash_cow_price DECIMAL(18,6),
    profit_amount DECIMAL(18,6),
    withdraw_profit_sum DECIMAL(18,6),
    trade_type INT,
    usc_code STRING,
    sale_order_detail_id BIGINT,
    supplier_bank_id INT,
    origin_id INT,
    year_and_month STRING,
    ysb_bill_code STRING,
    saleout_no STRING,
    paid_amount DECIMAL(18,6),
    not_paid_amount DECIMAL(18,6),
    source_type INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_pay',
    'table-name' = 'ts_cash_cow_withdraw_flow',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000',
    'debezium.snapshot.lock.timeout.ms' = '10000'
);

-- =============================================
-- Step 2: 创建 MySQL CDC 源表（关联表1：ts_provider_auth）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_provider_auth;
CREATE TABLE mysql_ts_provider_auth (
    id BIGINT,
    providerId STRING,
    expiry_date TIMESTAMP(3),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_admin',
    'table-name' = 'ts_provider_auth',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 3: 创建 MySQL CDC 源表（关联表2：ts_supplier）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_supplier;
CREATE TABLE mysql_ts_supplier (
    id BIGINT,
    usc_code STRING,
    supplier_code STRING,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_pay',
    'table-name' = 'ts_supplier',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 4: 创建 MySQL CDC 源表（关联表3：ts_purchased_order_detail）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_purchased_order_detail;
CREATE TABLE mysql_ts_purchased_order_detail (
    id BIGINT,
    ysb_provider_id STRING,
    batch_no STRING,
    io_type INT,
    label INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_pay',
    'table-name' = 'ts_purchased_order_detail',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 5: 创建 MySQL CDC 源表（关联表4：ts_product_label）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_product_label;
CREATE TABLE mysql_ts_product_label (
    id BIGINT,
    provider_id STRING,
    prov_drug_code STRING,
    label INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_data_center',
    'table-name' = 'ts_product_label',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 6: 创建 MySQL CDC 源表（关联表5：ts_bill_detail_balance）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_bill_detail_balance;
CREATE TABLE mysql_ts_bill_detail_balance (
    id BIGINT,
    company_id STRING,
    angle_code_erp STRING,
    io_type INT,
    owner_id BIGINT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_biz_dc',
    'table-name' = 'ts_bill_detail_balance',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 7: 创建 MySQL CDC 源表（关联表6：ts_sales_order_detail）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_sales_order_detail;
CREATE TABLE mysql_ts_sales_order_detail (
    id BIGINT,
    sales_time TIMESTAMP(3),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_pay',
    'table-name' = 'ts_sales_order_detail',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 8: 创建 MySQL CDC 源表（关联表7：ts_sales_order_detail_new）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_sales_order_detail_new;
CREATE TABLE mysql_ts_sales_order_detail_new (
    id BIGINT,
    sales_time TIMESTAMP(3),
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '${MYSQL_HOST}',
    'port' = '3306',
    'username' = '${MYSQL_USERNAME}',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_biz_dc',
    'table-name' = 'ts_sales_order_detail_new',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000'
);

-- =============================================
-- Step 9: 创建 Elasticsearch 目标表
-- =============================================
DROP TABLE IF EXISTS es_pc_cash_cow_flow;
CREATE TABLE es_pc_cash_cow_flow (
    id BIGINT,
    ctime STRING,
    mtime STRING,
    createUser BIGINT,
    status INT,
    providerId STRING,
    lyProductCode STRING,
    provDrugCode STRING,
    bindProductInfo STRING,
    supplierCode STRING,
    batchNo STRING,
    ownerId BIGINT,
    salesAmount DECIMAL(18,6),
    cashCowPrice DECIMAL(18,6),
    priceTaxP1 DECIMAL(18,6),
    priceTaxP0 DECIMAL(18,6),
    profitAmount DECIMAL(18,6),
    withdrawProfitSum DECIMAL(18,6),
    paidAmount DECIMAL(18,6),
    notPaidAmount DECIMAL(18,6),
    tradeType INT,
    uscCode STRING,
    saleDetailId BIGINT,
    supplierBankId INT,
    originId INT,
    yearAndMonth STRING,
    ysbBillCode STRING,
    saleOutNo STRING,
    sourceType INT,
    salesTime STRING,
    isSelectiveProduct INT,
    isSelectiveBatch INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'elasticsearch-7',
    'hosts' = '${ELASTIC_HOSTS}',
    'username' = '${ELASTIC_USERNAME}',
    'password' = '${ELASTIC_PASSWORD}',
    'index' = 'pc_cash_cow_flow',
    'document-id.key-delimiter' = '$',
    'sink.bulk-flush.max-actions' = '1000',
    'sink.bulk-flush.max-size' = '2mb',
    'sink.bulk-flush.interval' = '5000',
    'sink.bulk-flush.backoff.strategy' = 'CONSTANT',
    'sink.bulk-flush.backoff.delay' = '1000',
    'sink.bulk-flush.backoff.max-retries' = '3',
    'failure-handler' = 'fail',
    'format' = 'json'
);

-- =============================================
-- Step 10: 启动同步（关联查询）
-- =============================================
INSERT INTO es_pc_cash_cow_flow
SELECT
    tccwf.id,
    DATE_FORMAT(tccwf.create_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''') as ctime,
    DATE_FORMAT(tccwf.update_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''') as mtime,
    tccwf.create_user as createUser,
    tccwf.status,
    tccwf.ysb_provider_id as providerId,
    tccwf.ly_product_code as lyProductCode,
    tccwf.prov_drug_code as provDrugCode,
    CONCAT_WS(':', tccwf.ysb_provider_id, tccwf.prov_drug_code, tccwf.ly_product_code) as bindProductInfo,
    IFNULL(ts.supplier_code, '') as supplierCode,
    tccwf.batch_no as batchNo,
    tbdb.owner_id as ownerId,
    tccwf.sales_amount as salesAmount,
    tccwf.batch_p1_price as priceTaxP1,
    tccwf.batch_p0_price as priceTaxP0,
    tccwf.cash_cow_price as cashCowPrice,
    tccwf.profit_amount as profitAmount,
    tccwf.withdraw_profit_sum as withdrawProfitSum,
    tccwf.trade_type as tradeType,
    tccwf.usc_code as uscCode,
    tccwf.sale_order_detail_id as saleDetailId,
    tccwf.supplier_bank_id as supplierBankId,
    tccwf.origin_id as originId,
    tccwf.year_and_month as yearAndMonth,
    tccwf.ysb_bill_code as ysbBillCode,
    tccwf.saleout_no as saleOutNo,
    tccwf.paid_amount as paidAmount,
    tccwf.not_paid_amount as notPaidAmount,
    tccwf.source_type as sourceType,
    CASE tccwf.source_type
        WHEN 1 THEN DATE_FORMAT(tsod.sales_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')
        WHEN 2 THEN DATE_FORMAT(tsod1.sales_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')
        WHEN 3 THEN DATE_FORMAT(tsodn.sales_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')
        WHEN 8 THEN DATE_FORMAT(tsod8.sales_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')
        WHEN 9 THEN DATE_FORMAT(tccwf.create_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')
        ELSE NULL
    END as salesTime,
    IF(tpl.label = 1, 1, 0) as isSelectiveProduct,
    tpod.label as isSelectiveBatch
FROM mysql_ts_cash_cow_withdraw_flow tccwf
LEFT JOIN mysql_ts_provider_auth tpa ON CAST(tccwf.ysb_provider_id AS STRING) = tpa.providerId AND tpa.expiry_date > CURRENT_TIMESTAMP
LEFT JOIN mysql_ts_supplier ts ON ts.usc_code = tccwf.usc_code
LEFT JOIN mysql_ts_purchased_order_detail tpod ON tpod.ysb_provider_id = tccwf.ysb_provider_id AND tpod.batch_no = tccwf.batch_no AND tpod.io_type = 1
LEFT JOIN mysql_ts_product_label tpl ON tpl.provider_id = tccwf.ysb_provider_id AND tpl.prov_drug_code = tccwf.prov_drug_code
LEFT JOIN mysql_ts_bill_detail_balance tbdb ON CAST(tccwf.ysb_provider_id AS STRING) = tbdb.company_id AND tccwf.batch_no = tbdb.angle_code_erp AND tbdb.io_type = 1
LEFT JOIN mysql_ts_sales_order_detail tsod ON tsod.id = tccwf.sale_order_detail_id AND tccwf.source_type = 1
LEFT JOIN mysql_ts_sales_order_detail tsod1 ON tsod1.id = tccwf.sale_order_detail_id AND tccwf.source_type = 2
LEFT JOIN mysql_ts_sales_order_detail_new tsodn ON tsodn.id = tccwf.sale_order_detail_id AND tccwf.source_type = 3
LEFT JOIN mysql_ts_sales_order_detail_new tsod8 ON tsod8.id = tccwf.sale_order_detail_id AND tccwf.source_type = 8
```

---

## 三、简化版本（如果关联表数据量大）

如果关联表数据量很大，可以考虑只 CDC 主表，然后通过 Lookup Join 来获取关联数据：

```sql
-- 使用 Lookup Join 的简化版本
INSERT INTO es_pc_cash_cow_flow
SELECT
    tccwf.id,
    DATE_FORMAT(tccwf.create_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''') as ctime,
    DATE_FORMAT(tccwf.update_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''') as mtime,
    tccwf.create_user as createUser,
    tccwf.status,
    tccwf.ysb_provider_id as providerId,
    tccwf.ly_product_code as lyProductCode,
    tccwf.prov_drug_code as provDrugCode,
    CONCAT_WS(':', tccwf.ysb_provider_id, tccwf.prov_drug_code, tccwf.ly_product_code) as bindProductInfo,
    IFNULL(ts.supplier_code, '') as supplierCode,
    tccwf.batch_no as batchNo,
    tbdb.owner_id as ownerId,
    tccwf.sales_amount as salesAmount,
    tccwf.batch_p1_price as priceTaxP1,
    tccwf.batch_p0_price as priceTaxP0,
    tccwf.cash_cow_price as cashCowPrice,
    tccwf.profit_amount as profitAmount,
    tccwf.withdraw_profit_sum as withdrawProfitSum,
    tccwf.trade_type as tradeType,
    tccwf.usc_code as uscCode,
    tccwf.sale_order_detail_id as saleDetailId,
    tccwf.supplier_bank_id as supplierBankId,
    tccwf.origin_id as originId,
    tccwf.year_and_month as yearAndMonth,
    tccwf.ysb_bill_code as ysbBillCode,
    tccwf.saleout_no as saleOutNo,
    tccwf.paid_amount as paidAmount,
    tccwf.not_paid_amount as notPaidAmount,
    tccwf.source_type as sourceType,
    NULL as salesTime,
    IF(tpl.label = 1, 1, 0) as isSelectiveProduct,
    tpod.label as isSelectiveBatch
FROM mysql_ts_cash_cow_withdraw_flow tccwf
LEFT JOIN mysql_ts_supplier FOR SYSTEM_TIME AS OF tccwf.create_time AS ts ON ts.usc_code = tccwf.usc_code
LEFT JOIN mysql_ts_purchased_order_detail FOR SYSTEM_TIME AS OF tccwf.create_time AS tpod ON tpod.ysb_provider_id = tccwf.ysb_provider_id AND tpod.batch_no = tccwf.batch_no AND tpod.io_type = 1
LEFT JOIN mysql_ts_product_label FOR SYSTEM_TIME AS OF tccwf.create_time AS tpl ON tpl.provider_id = tccwf.ysb_provider_id AND tpl.prov_drug_code = tccwf.prov_drug_code
LEFT JOIN mysql_ts_bill_detail_balance FOR SYSTEM_TIME AS OF tccwf.create_time AS tbdb ON CAST(tccwf.ysb_provider_id AS STRING) = tbdb.company_id AND tccwf.batch_no = tbdb.angle_code_erp AND tbdb.io_type = 1
```

---

## 四、参数说明

| 参数 | 说明 | 示例值 |
|------|------|--------|
| MYSQL_HOST | MySQL 主机地址 | 192.168.27.54 |
| MYSQL_USERNAME | MySQL 用户名 | root |
| MYSQL_PASSWORD | MySQL 密码 | Leyo@2022 |
| ELASTIC_HOSTS | ES 连接地址 | http://192.168.27.55:19200 |
| ELASTIC_USERNAME | ES 用户名 | elastic |
| ELASTIC_PASSWORD | ES 密码 | leyo@@2021 |

---

## 五、CDC 启动模式

```sql
-- 模式1: initial（全量 + 增量同步）- 推荐首次同步
'scan.startup.mode' = 'initial'

-- 模式2: latest-offset（仅增量同步，从最新位置开始）
'scan.startup.mode' = 'latest-offset'

-- 模式3: specific-offset（从指定binlog位置开始）
'scan.startup.mode' = 'specific-offset'
'scan.startup.specific-offset.file' = 'mysql-bin.000001'
'scan.startup.specific-offset.pos' = '1234'
```

---

## 六、验证命令

```bash
# 验证 ES 连接
curl -u elastic:leyo@@2021 http://192.168.27.55:19200

# 查看 ES 中的文档数量
curl -u elastic:leyo@@2021 "http://192.168.27.55:19200/pc_cash_cow_flow/_count"

# 查看 Flink 任务状态
./bin/flink list -r
```
