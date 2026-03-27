# Flink CDC + MySQL → Elasticsearch 同步配置

> 配置时间：2026-03-26
> 同步表：db_stock.ts_saleoutmt（销售出库单）
> 数据量：24,056 条

---

## 一、表结构分析

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

## 二、Flink SQL CDC配置（完整版）

### 2.1 创建MySQL CDC源表

```sql
-- =============================================
-- Step 1: 创建MySQL CDC源表（销售出库单）
-- =============================================
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
    'password' = 'Leyo@2022',
    'database-name' = 'db_stock',
    'table-name' = 'ts_saleoutmt',
    'scan.startup.mode' = 'initial',
    'server-time-zone' = 'Asia/Shanghai',
    'debezium.min.row.count.to.streaming.result' = '1000'
);
```

### 2.2 创建Elasticsearch目标表

```sql
-- =============================================
-- Step 2: 创建Elasticsearch目标表
-- =============================================
CREATE TABLE es_ts_saleoutmt (
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
    'connector' = 'elasticsearch-7',
    'hosts' = 'http://192.168.27.55:19200',
    'username' = 'elastic',
    'password' = 'leyo@@2021',
    'index' = 'ts_saleoutmt',
    'document-id.key-delimiter' = '$',
    'sink.bulk-flush.max-actions' = '1000',
    'sink.bulk-flush.max-size' = '2mb',
    'sink.bulk-flush.interval' = '10000',
    'sink.bulk-flush.backoff.strategy' = 'CONSTANT',
    'sink.bulk-flush.backoff.delay' = '1000',
    'sink.bulk-flush.backoff.max-retries' = '3',
    'failure-handler' = 'ignore',
    'format' = 'json'
);
```

### 2.3 启动数据同步

```sql
-- =============================================
-- Step 3: 启动数据同步（INSERT INTO）
-- =============================================
INSERT INTO es_ts_saleoutmt
SELECT 
    id,
    ctime,
    utime,
    mtime,
    provider_id,
    company_id,
    billNo,
    entId,
    billCode,
    ruleId,
    dates,
    onTime,
    sysDates,
    isVat,
    clientId,
    client_code,
    accptId,
    saleManId,
    payOrgId,
    czy,
    orgId,
    deptId,
    contractCode,
    invoice,
    delivery,
    payType,
    amount,
    tax,
    taxAmount,
    profit,
    retailAmt,
    summaries,
    remark,
    saleClientId,
    dedRate,
    costAmt,
    reqDate,
    currencyId,
    paijia,
    isInvoice,
    isDone,
    curCode,
    address,
    isch,
    ischwc,
    oppContId,
    pickUpManId,
    wlbillcode,
    ptname,
    invoiceType,
    kkdjlb,
    isWithPic,
    isscpz,
    isscpz1,
    yst_fp_hm,
    yst_fp_dm,
    ysb_settlement,
    yst_fp_je,
    is_auto,
    saleBillType,
    ysbPayTime,
    closeBinNo,
    fhyName,
    packName,
    isscpz_sk,
    yst_kprq,
    reasontb,
    localSHBillCode,
    syncState,
    bill_time,
    ext_1,
    ext_2,
    ext_3,
    ext_4,
    ext_5,
    note0,
    note1,
    note2,
    note3,
    note4,
    note5,
    yst_fp_hm_hc,
    yst_fp_dm_hc,
    provider_identity
FROM mysql_ts_saleoutmt;
```

---

## 三、Elasticsearch索引配置（可选）

### 3.1 预先创建ES索引（推荐）

```bash
curl -u elastic:leyo@@2021 -X PUT "http://192.168.27.55:19200/ts_saleoutmt" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "index.mapping.total_fields.limit": 2000,
    "index.refresh_interval": "5s"
  },
  "mappings": {
    "properties": {
      "id": {"type": "long"},
      "billCode": {"type": "keyword"},
      "billNo": {"type": "integer"},
      "dates": {"type": "date", "format": "yyyy-MM-dd"},
      "provider_id": {"type": "keyword"},
      "company_id": {"type": "integer"},
      "clientId": {"type": "keyword"},
      "client_code": {"type": "keyword"},
      "amount": {"type": "double"},
      "tax": {"type": "double"},
      "taxAmount": {"type": "double"},
      "profit": {"type": "double"},
      "ctime": {"type": "date"},
      "utime": {"type": "date"},
      "mtime": {"type": "date"},
      "bill_time": {"type": "date"},
      "ysbPayTime": {"type": "date"},
      "isDone": {"type": "keyword"},
      "isInvoice": {"type": "keyword"},
      "isVat": {"type": "keyword"},
      "remark": {"type": "text", "analyzer": "ik_max_word"},
      "summaries": {"type": "text", "analyzer": "ik_max_word"},
      "address": {"type": "text", "analyzer": "ik_max_word"}
    }
  }
}
'
```

### 3.2 验证ES索引

```bash
# 查看索引是否存在
curl -u elastic:leyo@@2021 http://192.168.27.55:19200/_cat/indices/ts_saleoutmt?v

# 查看索引mapping
curl -u elastic:leyo@@2021 http://192.168.27.55:19200/ts_saleoutmt/_mapping?pretty
```

---

## 四、CDC启动模式说明

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

## 五、数据验证SQL

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
curl -u elastic:leyo@@2021 "http://192.168.27.55:19200/ts_saleoutmt/_count"

# 查询最近同步的数据
curl -u elastic:leyo@@2021 "http://192.168.27.55:19200/ts_saleoutmt/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {"match_all": {}},
  "sort": [{"mtime": "desc"}],
  "size": 10
}
'

# 按日期聚合统计
curl -u elastic:leyo@@2021 "http://192.168.27.55:19200/ts_saleoutmt/_search?pretty" -H 'Content-Type: application/json' -d'
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

## 六、运维监控

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

## 七、遇到的问题及解决方案

| 序号 | 问题描述 | 解决方案 | 日期 |
|------|---------|---------|------|
| 1 | `Unsupported options found for 'elasticsearch-7': sink.failure-handler` | 参数名错误，应使用 `'failure-handler'` 而非 `'sink.failure-handler'` | 2026-03-26 |
| 2 | `Object 'mysql_ts_saleoutmt' not found` | 执行顺序错误，必须先创建CDC源表，再创建ES目标表，最后执行INSERT INTO | 2026-03-26 |
| 3 | **CDC同步任务启动成功** | 按正确顺序执行：1)创建MySQL CDC源表 2)创建ES目标表 3)执行INSERT INTO | 2026-03-26 |
| 4 | **查看Flink任务列表** | 在Flink服务器执行 `./bin/flink list`，任务状态显示为 RUNNING | 2026-03-26 |
| 5 | **执行完INSERT后SQL客户端崩溃** | Flink 1.20.1存在icu4j依赖问题，执行完INSERT后需执行 `SHOW TABLES` 验证表是否创建成功 | 2026-03-26 |

---

## 八、经验总结

### 8.1 CDC执行技巧（重要）

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

### 8.2 CDC配置要点
1. ⚠️ **字段映射**：MySQL DECIMAL类型映射到ES时建议使用DOUBLE，避免精度问题
2. ⚠️ **时间字段**：DATETIME类型建议指定TIMESTAMP(3)，保留毫秒精度
3. ⚠️ **Bulk优化**：设置合理的bulk flush参数，避免频繁写入影响性能
4. ⚠️ **Index设置**：对于大数据量表，设置合适的shard数量（建议3-5个）

### 8.2 性能调优建议
1. **首次全量同步**：如果数据量大，建议在业务低峰期进行
2. **增量同步监控**：关注binlog产生的速度，避免堆积
3. **ES写入优化**：根据集群配置调整bulk size，通常1000-5000条/次
4. **Checkpoint配置**：建议30秒左右做一次checkpoint，避免数据丢失

---

## 九、问题汇总记录（2026-03-26）

### 9.1 常见问题

| 序号 | 问题 | 原因 | 解决方案/备注 |
|---|---|---|---|
| 1 | `flink list -a` 看不到同步任务 | 可能未成功执行 `INSERT INTO ... SELECT ...`，会话已断开 | 重新执行不带结果的 `INSERT INTO` 语句 |
| 2 | `Failed to cancelOperation` / `Can not find the submitted operation` | SQL Gateway 取消一个已结束/不存在的 operation | 重启集群，可后台看 TaskManager/JobManager 丢失栈 |
| 3 | 日志出现 `Missing resources ... ResourceProfile{UNKNOWN}` | 资源阶段的资源匹配提示 | 多次重启后如果失败，请确认已成功分配 slot 后开始运行 |
| 4 | `ClassNotFoundException: org.apache.flink.streaming.connectors.elasticsearch7.ElasticsearchSink` | ES7 connector 未正确加载到集群，缺包/版本/节点不一致！ | 统一升级 ES7 SQL connector 同步全集群 |
| 5 | `sql-client` 加载失败：`Elasticsearch7DynamicTableFactory` / `ElasticsearchConnectorOptions` 缺失 | 使用了错误的 connector 版本 jar，如 `3.10-1.20`！connector 和 sql uber jar | 使用 `flink-sql-connector-elasticsearch7-3.1.0-1.20.jar` |
| 6 | 只有一台节点的 jar 能运行成功 | jar 会被均匀调度到 TaskManager | 同步操作，让所有节点 `lib/` 保持一致 |

### 9.2 集群环境统一修复步骤

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

### 9.3 注意事项

1. Flink 1.20.x 对应 ES7 SQL connector 推荐版本是`3.1.0-1.20`，而非 `3.10-1.20`！
2. 在节点集群中，任意一个节点缺包都会导致同步任务失败！
3. 如果遇到故障重启时，请先看 `Caused by` 底层异常，主要看上级 `NoRestartBackoffTimeStrategy` 误导！

### 9.4 端口冲突补丁（2026-03-26 17:08）

| 序号 | 问题 | 原因 | 解决方案 |
|---|---|---|---|
| 7 | `Could not start actor system on any port in port range 6123` | JobManager RPC 端口 `6123` 被占用，可能是进程未正常退出导致冲突 | 停止集群，强制杀死该进程，释放 6123 端口！必要时修改 `high-availability.jobmanager.port` 为端口段 |

**推荐排查命令（在堡垒机节点执行）**

```bash
ss -lntp | grep 6123
jps | grep -E "TaskManagerRunner|StandaloneSessionClusterEntrypoint"

/opt/flink-1.20.1/bin/stop-cluster.sh
pkill -f TaskManagerRunner
pkill -f StandaloneSessionClusterEntrypoint

ss -lntp | grep 6123   # 验证已释放
/opt/flink-1.20.1/bin/start-cluster.sh
```

**端口冲突配置**

```yaml
# flink-conf.yaml
high-availability.jobmanager.port: 6123-6133
```
