# Flink CDC + MySQL → Elasticsearch 同步配置

> 配置时间：2026-03-26
> 更新日期：2026-03-31（整合所有问题修复）
> 同步表：db_stock.ts_saleoutmt（销售出库单）
> 数据量：24,056 条

---

## 一、最终完整版可直接运行 Flink SQL（复制即用）

- ✅ 时间格式兼容 ES
- ✅ 关闭错误静默吃掉
- ✅ 开启 Checkpoint
- ✅ 修复 TIMESTAMP 写入 ES 报错
- ✅ 修复数值溢出
- ✅ 稳定写入、可监控、可重启

### 1.1 直接在 Kibana → Dev Tools 执行的语句（如果已经有，没有请忽略）

作用：**删除旧索引 → 全新重建索引 → 100% 解决字段冲突 / 格式报错**

```bash
# 1. 删除旧索引（如果存在）
DELETE ts_saleoutmt

# 2. 全新创建索引（完美匹配你的 Flink 字段，不会再报日期/数值错误）
PUT ts_saleoutmt
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "id": { "type": "long" },
      "ctime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "utime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "mtime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "provider_id": { "type": "keyword" },
      "company_id": { "type": "integer" },
      "billNo": { "type": "integer" },
      "entId": { "type": "keyword" },
      "billCode": { "type": "keyword" },
      "ruleId": { "type": "keyword" },
      "dates": { "type": "keyword" },
      "onTime": { "type": "keyword" },
      "sysDates": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "isVat": { "type": "keyword" },
      "clientId": { "type": "keyword" },
      "client_code": { "type": "keyword" },
      "accptId": { "type": "keyword" },
      "saleManId": { "type": "keyword" },
      "payOrgId": { "type": "keyword" },
      "czy": { "type": "keyword" },
      "orgId": { "type": "keyword" },
      "deptId": { "type": "keyword" },
      "contractCode": { "type": "keyword" },
      "invoice": { "type": "keyword" },
      "delivery": { "type": "keyword" },
      "payType": { "type": "keyword" },
      "amount": { "type": "double" },
      "tax": { "type": "double" },
      "taxAmount": { "type": "double" },
      "profit": { "type": "double" },
      "retailAmt": { "type": "double" },
      "summaries": { "type": "text" },
      "remark": { "type": "text" },
      "saleClientId": { "type": "keyword" },
      "dedRate": { "type": "double" },
      "costAmt": { "type": "double" },
      "reqDate": { "type": "keyword" },
      "currencyId": { "type": "keyword" },
      "paijia": { "type": "double" },
      "isInvoice": { "type": "keyword" },
      "isDone": { "type": "keyword" },
      "curCode": { "type": "keyword" },
      "address": { "type": "text" },
      "isch": { "type": "keyword" },
      "ischwc": { "type": "keyword" },
      "oppContId": { "type": "keyword" },
      "pickUpManId": { "type": "keyword" },
      "wlbillcode": { "type": "keyword" },
      "ptname": { "type": "keyword" },
      "invoiceType": { "type": "keyword" },
      "kkdjlb": { "type": "keyword" },
      "isWithPic": { "type": "keyword" },
      "isscpz": { "type": "keyword" },
      "isscpz1": { "type": "keyword" },
      "yst_fp_hm": { "type": "keyword" },
      "yst_fp_dm": { "type": "keyword" },
      "ysb_settlement": { "type": "double" },
      "yst_fp_je": { "type": "double" },
      "is_auto": { "type": "keyword" },
      "saleBillType": { "type": "keyword" },
      "ysbPayTime": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "closeBinNo": { "type": "keyword" },
      "fhyName": { "type": "keyword" },
      "packName": { "type": "keyword" },
      "isscpz_sk": { "type": "keyword" },
      "yst_kprq": { "type": "keyword" },
      "reasontb": { "type": "text" },
      "localSHBillCode": { "type": "keyword" },
      "syncState": { "type": "keyword" },
      "bill_time": { "type": "date", "format": "strict_date_optional_time||epoch_millis" },
      "ext_1": { "type": "keyword" },
      "ext_2": { "type": "keyword" },
      "ext_3": { "type": "keyword" },
      "ext_4": { "type": "keyword" },
      "ext_5": { "type": "keyword" },
      "note0": { "type": "text" },
      "note1": { "type": "text" },
      "note2": { "type": "text" },
      "note3": { "type": "text" },
      "note4": { "type": "text" },
      "note5": { "type": "text" },
      "yst_fp_hm_hc": { "type": "keyword" },
      "yst_fp_dm_hc": { "type": "keyword" },
      "provider_identity": { "type": "integer" }
    }
  }
}

# 3. 查看索引是否创建成功
GET ts_saleoutmt
```

### 1.2 Flink SQL 完整执行脚本

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
-- Step 1: 创建 MySQL CDC 源表（已优化）
-- =============================================
DROP TABLE IF EXISTS mysql_ts_saleoutmt;
CREATE TABLE mysql_ts_saleoutmt (
    id BIGINT,
    ctime TIMESTAMP(3),
    utime TIMESTAMP(3),
    mtime TIMESTAMP(3),
    provider_id STRING,
    company_id INT,
    billNo INT,
    entId STRING,
    billCode STRING,
    ruleId STRING,
    dates STRING,
    onTime STRING,
    sysDates TIMESTAMP(3),
    isVat STRING,
    clientId STRING,
    client_code STRING,
    accptId STRING,
    saleManId STRING,
    payOrgId STRING,
    czy STRING,
    orgId STRING,
    deptId STRING,
    contractCode STRING,
    invoice STRING,
    delivery STRING,
    payType STRING,
    amount DECIMAL(18,6),
    tax DECIMAL(18,6),
    taxAmount DECIMAL(18,6),
    profit DECIMAL(18,6),
    retailAmt DECIMAL(18,6),
    summaries STRING,
    remark STRING,
    saleClientId STRING,
    dedRate DECIMAL(18,6),
    costAmt DECIMAL(18,6),
    reqDate STRING,
    currencyId STRING,
    paijia DECIMAL(18,6),
    isInvoice STRING,
    isDone STRING,
    curCode STRING,
    address STRING,
    isch STRING,
    ischwc STRING,
    oppContId STRING,
    pickUpManId STRING,
    wlbillcode STRING,
    ptname STRING,
    invoiceType STRING,
    kkdjlb STRING,
    isWithPic STRING,
    isscpz STRING,
    isscpz1 STRING,
    yst_fp_hm STRING,
    yst_fp_dm STRING,
    ysb_settlement DECIMAL(12,6),
    yst_fp_je DECIMAL(14,6),
    is_auto STRING,
    saleBillType STRING,
    ysbPayTime TIMESTAMP(3),
    closeBinNo STRING,
    fhyName STRING,
    packName STRING,
    isscpz_sk STRING,
    yst_kprq STRING,
    reasontb STRING,
    localSHBillCode STRING,
    syncState STRING,
    bill_time TIMESTAMP(3),
    ext_1 STRING,
    ext_2 STRING,
    ext_3 STRING,
    ext_4 STRING,
    ext_5 STRING,
    note0 STRING,
    note1 STRING,
    note2 STRING,
    note3 STRING,
    note4 STRING,
    note5 STRING,
    yst_fp_hm_hc STRING,
    yst_fp_dm_hc STRING,
    provider_identity INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'mysql-cdc',
    'hostname' = '192.168.27.54',
    'port' = '3306',
    'username' = 'root',
    'password' = '${MYSQL_PASSWORD}',
    'database-name' = 'db_stock',
    'table-name' = 'ts_saleoutmt',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'scan.incremental.snapshot.chunk.size' = '2000',
    'debezium.snapshot.lock.timeout.ms' = '10000'
);

-- =============================================
-- Step 2: 创建 Elasticsearch 目标表（已修复所有坑）
-- =============================================
DROP TABLE IF EXISTS es_ts_saleoutmt;
CREATE TABLE es_ts_saleoutmt (
    id BIGINT,
    ctime STRING,
    utime STRING,
    mtime STRING,
    provider_id STRING,
    company_id INT,
    billNo INT,
    entId STRING,
    billCode STRING,
    ruleId STRING,
    dates STRING,
    onTime STRING,
    sysDates STRING,
    isVat STRING,
    clientId STRING,
    client_code STRING,
    accptId STRING,
    saleManId STRING,
    payOrgId STRING,
    czy STRING,
    orgId STRING,
    deptId STRING,
    contractCode STRING,
    invoice STRING,
    delivery STRING,
    payType STRING,
    amount DECIMAL(18,6),
    tax DECIMAL(18,6),
    taxAmount DECIMAL(18,6),
    profit DECIMAL(18,6),
    retailAmt DECIMAL(18,6),
    summaries STRING,
    remark STRING,
    saleClientId STRING,
    dedRate DECIMAL(18,6),
    costAmt DECIMAL(18,6),
    reqDate STRING,
    currencyId STRING,
    paijia DECIMAL(18,6),
    isInvoice STRING,
    isDone STRING,
    curCode STRING,
    address STRING,
    isch STRING,
    ischwc STRING,
    oppContId STRING,
    pickUpManId STRING,
    wlbillcode STRING,
    ptname STRING,
    invoiceType STRING,
    kkdjlb STRING,
    isWithPic STRING,
    isscpz STRING,
    isscpz1 STRING,
    yst_fp_hm STRING,
    yst_fp_dm STRING,
    ysb_settlement DECIMAL(12,6),
    yst_fp_je DECIMAL(14,6),
    is_auto STRING,
    saleBillType STRING,
    ysbPayTime STRING,
    closeBinNo STRING,
    fhyName STRING,
    packName STRING,
    isscpz_sk STRING,
    yst_kprq STRING,
    reasontb STRING,
    localSHBillCode STRING,
    syncState STRING,
    bill_time STRING,
    ext_1 STRING,
    ext_2 STRING,
    ext_3 STRING,
    ext_4 STRING,
    ext_5 STRING,
    note0 STRING,
    note1 STRING,
    note2 STRING,
    note3 STRING,
    note4 STRING,
    note5 STRING,
    yst_fp_hm_hc STRING,
    yst_fp_dm_hc STRING,
    provider_identity INT,
    PRIMARY KEY (id) NOT ENFORCED
) WITH (
    'connector' = 'elasticsearch-7',
    'hosts' = 'http://192.168.27.55:19200',
    'username' = 'elastic',
    'password' = '${ELASTIC_PASSWORD}',
    'index' = 'ts_saleoutmt',
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
-- Step 3: 启动同步（已修复时间格式，100%写入成功）
-- =============================================
INSERT INTO es_ts_saleoutmt
SELECT
    id,
    DATE_FORMAT(ctime, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    DATE_FORMAT(utime, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    DATE_FORMAT(mtime, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    provider_id,company_id,billNo,entId,billCode,ruleId,dates,onTime,
    DATE_FORMAT(sysDates, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    isVat,clientId,client_code,accptId,saleManId,payOrgId,czy,orgId,deptId,
    contractCode,invoice,delivery,payType,
    amount,tax,taxAmount,profit,retailAmt,summaries,remark,saleClientId,
    dedRate,costAmt,reqDate,currencyId,paijia,isInvoice,isDone,curCode,address,
    isch,ischwc,oppContId,pickUpManId,wlbillcode,ptname,invoiceType,kkdjlb,
    isWithPic,isscpz,isscpz1,yst_fp_hm,yst_fp_dm,
    ysb_settlement,yst_fp_je,is_auto,saleBillType,
    DATE_FORMAT(ysbPayTime, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    closeBinNo,fhyName,packName,isscpz_sk,yst_kprq,reasontb,
    localSHBillCode,syncState,
    DATE_FORMAT(bill_time, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z'''),
    ext_1,ext_2,ext_3,ext_4,ext_5,
    note0,note1,note2,note3,note4,note5,
    yst_fp_hm_hc,yst_fp_dm_hc,provider_identity
FROM mysql_ts_saleoutmt;
```

### 1.3 验证 ES 数据命令

```bash
curl -u elastic:${ELASTIC_PASSWORD} "http://192.168.27.55:19200/ts_saleoutmt/_count"
```

---

## 二、这份配置已经修复的所有问题（你前面踩过的坑）

1. **时间类型写入 ES 报错** ✅ 已全部转成 ES 支持的 ISO 格式
2. **failure-handler = ignore 吞错误** ✅ 改为 `fail`，报错立刻暴露
3. **不开启 Checkpoint → ES 永远不写入** ✅ 已开启
4. **TIMESTAMP 无法用 UNIX_TIMESTAMP** ✅ 改用 `DATE_FORMAT`
5. **datagen 生成无穷大数字** ✅ 已去掉，直接用业务源表
6. **任务一退出就停** ✅ 已开启 `detached` 后台运行
7. **ES 连接异常看不见** ✅ 失败直接抛异常

---

## 三、表结构分析

### 1.1 源表信息

```sql
-- 数据库：db_stock
-- 表名：ts_saleoutmt
-- 主键：id (bigint, auto_increment)
-- 数据量：24,056 条
```

### 1.2 关键字段说明

| 字段分类 | 字段名 | 类型 | 说明 |
|---------|--------|------|------|
| **主键** | id | BIGINT | 主键，用于CDC和ES文档ID |
| **业务字段** | billCode | VARCHAR(40) | 单据编号 |
| **业务字段** | billNo | INT | 单据序号 |
| **业务字段** | dates | CHAR(10) | 单据日期 |
| **业务字段** | provider_id | CHAR(11) | 供应商ID |
| **业务字段** | company_id | INT | 公司ID |
| **客户字段** | clientId | VARCHAR(40) | 客户ID |
| **客户字段** | client_code | VARCHAR(40) | 客户编码 |
| **金额字段** | amount | DECIMAL(18,6) | 金额 |
| **金额字段** | tax | DECIMAL(18,6) | 税额 |
| **金额字段** | taxAmount | DECIMAL(18,6) | 含税金额 |
| **金额字段** | profit | DECIMAL(18,6) | 利润 |
| **状态字段** | isDone | CHAR(1) | 是否完成 |
| **状态字段** | isInvoice | CHAR(1) | 是否开票 |
| **状态字段** | isVat | CHAR(1) | 是否增值税 |
| **时间字段** | ctime | DATETIME | 创建时间 |
| **时间字段** | utime | DATETIME | 更新时间 |
| **时间字段** | mtime | DATETIME | 修改时间 |
| **时间字段** | bill_time | DATETIME | 单据时间 |
| **时间字段** | ysbPayTime | DATETIME | 药师帮支付时间 |
| **备注字段** | remark | VARCHAR(255) | 备注 |
| **摘要字段** | summaries | VARCHAR(255) | 摘要 |
| **人员字段** | saleManId | VARCHAR(40) | 业务员ID |
| **人员字段** | czy | VARCHAR(40) | 操作员 |

---

## 五、CDC启动模式说明

### 4.1 启动模式选项

```sql
-- 模式1: initial（全量 + 增量同步）- 推荐首次同步
'scan.startup.mode' = 'initial'

-- 模式2: latest-offset（仅增量同步，从最新位置开始）
'scan.startup.mode' = 'latest-offset'

-- 模式3: specific-offset（从指定binlog位置开始）
'scan.startup.mode' = 'specific-offset'
'scan.startup.specific-offset.file' = 'mysql-bin.000001'
'scan.startup.specific-offset.pos' = '1234'

-- 模式4: timestamp（从指定时间开始）
'scan.startup.mode' = 'timestamp'
'scan.startup.timestamp-millis' = '1700000000000'
```

### 4.2 首次同步推荐步骤

1. **第一次启动**：使用 `initial` 模式，会先全量同步历史数据，然后增量监听binlog
2. **观察同步状态**：在Flink UI中观察任务状态和吞吐量
3. **数据验证**：同步完成后，在ES中验证数据量和数据完整性

---

## 六、数据验证SQL

### 5.1 MySQL源表验证

```sql
-- 查看总数据量
SELECT COUNT(*) FROM db_stock.ts_saleoutmt;

-- 查看最近更新的数据
SELECT id, billCode, dates, amount, mtime 
FROM db_stock.ts_saleoutmt 
ORDER BY mtime DESC 
LIMIT 10;

-- 按日期统计
SELECT dates, COUNT(*) as cnt 
FROM db_stock.ts_saleoutmt 
GROUP BY dates 
ORDER BY dates DESC;
```

### 5.2 Elasticsearch目标表验证

```bash
# 查看ES中的文档数量
curl -u elastic:${ELASTIC_PASSWORD} "http://192.168.27.55:19200/ts_saleoutmt/_count"

# 查询最近同步的数据
curl -u elastic:${ELASTIC_PASSWORD} "http://192.168.27.55:19200/ts_saleoutmt/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {"match_all": {}},
  "sort": [{"mtime": "desc"}],
  "size": 10
}
'

# 按日期聚合统计
curl -u elastic:${ELASTIC_PASSWORD} "http://192.168.27.55:19200/ts_saleoutmt/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_dates": {
      "terms": {"field": "dates.keyword", "size": 10},
      "aggs": {
        "total_amount": {"sum": {"field": "amount"}}
      }
    }
  }
}
'
```

---

## 七、运维监控

### 6.1 Flink任务监控

- 访问 Flink Web UI（默认端口：8081）
- 关注以下指标：
  - **Records sent**：已发送记录数
  - **Records received**：已接收记录数
  - **Latency**：处理延迟
  - **Checkpoint**：检查点状态

### 6.2 常见运维命令

```sql
-- 查看CDC正在读取的binlog位置
SHOW VARIABLES LIKE 'binlog_current_pos';

-- 查看binlog文件列表
SHOW MASTER LOGS;

-- 查看从库状态（如果有）
SHOW SLAVE STATUS\G;
```

---

## 八、遇到的问题及解决方案（完整问题清单）

### 8.1 初期配置问题（2026-03-26）

| 序号 | 问题描述 | 解决方案 | 日期 |
|------|---------|---------|------|
| 1 | `Unsupported options found for 'elasticsearch-7': sink.failure-handler` | 参数名错误，应使用 `'failure-handler'` 而非 `'sink.failure-handler'` | 2026-03-26 |
| 2 | `Object 'mysql_ts_saleoutmt' not found` | 执行顺序错误，必须先创建CDC源表，再创建ES目标表，最后执行INSERT INTO | 2026-03-26 |
| 3 | **CDC同步任务启动成功** | 按正确顺序执行：1)创建MySQL CDC源表 2)创建ES目标表 3)执行INSERT INTO | 2026-03-26 |
| 4 | **查看Flink任务列表** | 在Flink服务器执行 `./bin/flink list`，任务状态显示为 RUNNING | 2026-03-26 |
| 5 | **执行完INSERT后SQL客户端崩溃** | Flink 1.20.1存在icu4j依赖问题，执行完INSERT后需执行 `SHOW TABLES` 验证表是否创建成功 | 2026-03-26 |

### 8.2 ES Sink 不支持查询（2026-03-31）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 1 | Flink SQL 无法查询 ES 表（CannotPlanException） | Elasticsearch 连接器只支持 Sink（写入），不支持流模式 Source（查询） | 只使用 `INSERT INTO` 写入，不查询 ES 表 |

### 8.3 ES 连接与 Checkpoint 问题（2026-03-31）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 2 | ES 连接配置错误、无法连通 | hosts 写错、无权限、端口不通 | 确保 `hosts = "http://IP:PORT"`、账号密码正确、网络互通。验证：`curl -u elastic:${ELASTIC_PASSWORD} http://192.168.27.55:19200` |
| 3 | **未开启 Checkpoint → ES 数据不刷新、一直缓存** | Flink ES Sink 默认 Checkpoint 触发提交，不开 Checkpoint 数据永远不落地 ES | 必须开启：`SET execution.checkpointing.interval = 30s;` |
| 4 | **failure-handler = ignore → 错误被静默吃掉** | 写入 ES 失败但不报错、不打印日志 | 测试环境必须设为：`'failure-handler' = 'fail'` |

### 8.4 数据格式转换问题（2026-03-31）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 5 | 日期格式不兼容（strict_date_optional_time） | ES 不识别 `2026-03-31 12:00:00`，只认 ISO 格式或时间戳 | 使用 **毫秒时间戳 BIGINT** 或 **ISO 格式字符串** |
| 6 | datagen 生成无限大 DOUBLE → ES float 溢出报错 | datagen 默认生成超大浮点数（Infinity），ES float 无法存储 | 必须限制范围：`'fields.sale_amount.min' = '0.01' 'fields.sale_amount.max' = '1000.0'` |
| 7 | UNIX_TIMESTAMP 不支持 TIMESTAMP (3) 类型 | Flink SQL 中 `UNIX_TIMESTAMP` 只支持字符串，不支持时间类型 | 改用 `DATE_FORMAT(ts, 'yyyy-MM-dd''T''HH:mm:ss.SSS''Z''')` |

### 8.5 任务生命周期问题（2026-03-31）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 8 | 任务运行一会儿自动退出 | SQL Client 按了 Ctrl+C、关闭窗口、会话断开 | 提交前开启后台运行：`SET execution.detached = true;` |

### 8.6 集群部署问题（2026-03-26）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 1 | `ClassNotFoundException: org.apache.flink.streaming.connectors.elasticsearch7.ElasticsearchSink` | ES7 connector 未正确加载到集群，缺包/版本/节点不一致 | 统一升级 ES7 SQL connector 同步全集群 |
| 2 | `Elasticsearch7DynamicTableFactory` / `ElasticsearchConnectorOptions` 缺失 | 使用了错误的 connector 版本 jar | 使用 `flink-sql-connector-elasticsearch7-3.1.0-1.20.jar` |
| 3 | 只有一台节点的 jar 能运行成功 | jar 会被均匀调度到 TaskManager | 同步操作，让所有节点 `lib/` 保持一致 |

### 8.7 端口冲突问题（2026-03-26）

| 序号 | 问题描述 | 原因 | 解决方案 |
|------|---------|------|---------|
| 1 | `Could not start actor system on any port in port range 6123` | JobManager RPC 端口 `6123` 被占用，可能是进程未正常退出导致冲突 | 停止集群，强制杀死该进程，释放端口 |

**推荐排查命令：**

```bash
ss -lntp | grep 6123
jps | grep -E "TaskManagerRunner|StandaloneSessionClusterEntrypoint"

/opt/flink-1.20.1/bin/stop-cluster.sh
pkill -f TaskManagerRunner
pkill -f StandaloneSessionClusterEntrypoint

ss -lntp | grep 6123   # 验证已释放
/opt/flink-1.20.1/bin/start-cluster.sh
```

**端口冲突配置：**

```yaml
# flink-conf.yaml
high-availability.jobmanager.port: 6123-6133
```

---

## 九、经验总结

### 9.1 CDC执行技巧（重要）

1. **执行完INSERT后执行SHOW TABLES验证**
   - Flink 1.20.1 SQL客户端存在icu4j依赖问题，可能导致显示结果时崩溃
   - 即使看到崩溃信息，**任务可能已成功提交**
   - **验证方法**：执行 `SHOW TABLES` 查看表是否已创建

2. **Flink SQL执行顺序（必须严格遵守）**
   ```
   1️⃣ CREATE TABLE mysql_xxx  (CDC源表，必须先创建)
   2️⃣ CREATE TABLE es_xxx    (ES目标表)
   3️⃣ INSERT INTO ... SELECT * FROM ...  (启动同步)
   4️⃣ SHOW TABLES  (验证表是否创建成功)
   ```

3. **任务状态验证**
   - 在Flink服务器执行：`./bin/flink list -r` 查看运行中的任务
   - 查看任务ID和状态是否为RUNNING

---

### 9.2 CDC配置要点
1. ⚠️ **字段映射**：MySQL DECIMAL类型映射到ES时建议使用DOUBLE，避免精度问题
2. ⚠️ **时间字段**：DATETIME类型建议指定TIMESTAMP(3)，保留毫秒精度
3. ⚠️ **Bulk优化**：设置合理的bulk flush参数，避免频繁写入影响性能
4. ⚠️ **Index设置**：对于大数据量表，设置合适的shard数量（建议3-5个）
5. ⚠️ **全局配置**：必须开启 Checkpoint（`SET execution.checkpointing.interval = 30s;`）
6. ⚠️ **错误处理**：必须设为 `failure-handler = 'fail'`，禁止使用 `ignore`
7. ⚠️ **后台运行**：必须开启 `detached` 模式，避免会话断开导致任务终止

### 9.3 性能调优建议
1. **首次全量同步**：如果数据量大，建议在业务低峰期进行
2. **增量同步监控**：关注binlog产生的速度，避免堆积
3. **ES写入优化**：根据集群配置调整bulk size，通常1000-5000条/次
4. **Checkpoint配置**：建议30秒左右做一次checkpoint，避免数据丢失
5. **增量快照优化**：设置 `scan.incremental.snapshot.chunk.size = 2000` 提高大表同步效率

### 9.4 集群环境修复步骤

1. 所有节点（`swd133/swd134/swd135`）统一删除 ES connector jar：
   - `rm -f /opt/flink-1.20.1/lib/*elasticsearch*.jar`
2. 所有节点统一部署同一版本：
   - `flink-sql-connector-elasticsearch7-3.1.0-1.20.jar`
3. 全集群重启：
   - `./bin/stop-cluster.sh && ./bin/start-cluster.sh`
4. 重新在 `sql-client` 执行：
   - `INSERT INTO es_ts_saleoutmt SELECT ... FROM mysql_ts_saleoutmt;`
5. 验证：
   - `./bin/flink list -a`
   - 看 JobManager/TaskManager 日志中不再出现 `ClassNotFoundException: ElasticsearchSink`

### 9.5 注意事项

1. Flink 1.20.x 对应 ES7 SQL connector 推荐版本是`3.1.0-1.20`，而非 `3.10-1.20`！
2. 在节点集群中，任意一个节点缺包都会导致同步任务失败！
3. 如果遇到故障重启时，请先看 `Caused by` 底层异常，主要看上级 `NoRestartBackoffTimeStrategy` 误导！

---

## 十、最终结论

✅ **所有问题已全部定位并解决**

✅ **网络连通 → 正常**

✅ **ES 权限 → 正常**

✅ **Flink 写入 ES → 正常**

✅ **时间格式 → 正常**

✅ **数值溢出 → 修复**

✅ **Checkpoint 机制 → 开启**

✅ **错误不再静默 → 可观测**

**最终结果：Flink 可稳定将数据写入 Elasticsearch，不再丢数、不再报错。**

---

## 十一、验证命令汇总

### 11.1 验证 ES 连接

```bash
curl -u elastic:${ELASTIC_PASSWORD} http://192.168.27.55:19200
```

### 11.2 验证 ES 数据量

```bash
curl -u elastic:${ELASTIC_PASSWORD} "http://192.168.27.55:19200/ts_saleoutmt/_count"
```

### 11.3 验证 Flink 任务状态

```bash
# 查看运行中的任务
./bin/flink list -r

# 查看所有任务（包括历史）
./bin/flink list -a
```

### 11.4 常见运维命令

```bash
# 查看CDC正在读取的binlog位置
SHOW VARIABLES LIKE 'binlog_current_pos';

# 查看binlog文件列表
SHOW MASTER LOGS;

# 查看从库状态（如果有）
SHOW SLAVE STATUS\G;
```
