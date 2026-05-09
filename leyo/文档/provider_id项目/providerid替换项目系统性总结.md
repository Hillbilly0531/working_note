# Provider ID 替换项目系统性总结

> 基于 2026-03-30 至 2026-04-17 工作笔记的综合分析

---

## 一、项目概述

Provider ID 替换项目是一项大规模技术债务清理工程，核心目标是将系统中分散的 `provider_id` / `ysb_provider_id` 等多种 provider 字段口径统一为 `provider_identity`。项目涉及 SQL 改写、PO 类调整、CDC 链路改造、Maven 环境修复等多个技术领域。

---

## 二、技术难点、风险及解决方案（"坑"汇总）

### 2.1 SQL 层 Provider 字段混用问题

#### 坑点 1：分页查询中 Provider 字段口径不一致
- **现象**：`MyBatisSystemException`，`queryTotal` 包装 SQL 报错，提示参数绑定失败
- **根因**：`getListPageV2` 中 WHERE 条件使用 `tr.ysb_provider_id in (...)`，而 JOIN 关联使用 `tr.provider_identity`，同一 SQL 中混用不同口径
- **影响**：分页查询的 count 语句与 list 语句参数绑定不一致，导致 MyBatis 报错
- **解决方案**：
  - 统一替换为 `tr.provider_identity`
  - 同步修复 `getListV2` 中同类条件
- **文件位置**：`src/main/resources/mapper/RebateMapper.xml`

#### 坑点 2：JOIN 关联字段类型不匹配
- **现象**：供应商与商品负责人关联查询结果异常
- **根因**：`char` / `int` 类型混连，provider 字段在不同表中类型定义不一致
- **风险**：隐式类型转换导致索引失效、关联结果集错误
- **解决方案**：
  - 统一为 `int` / `provider_identity` 优先的关联方式
  - 对 `ts_supplystaffs` / `ts_staffdoc` 关联进行修正
- **涉及文件**：
  - `RebateAuthMapper.xml`
  - `IRebateAuthMapper.java`

#### 坑点 3：SELECT 投影与表达式内部 Provider 字段
- **现象**：仅改写了 WHERE 条件，但 SELECT 中的 `CASE WHEN` / `CONCAT` 表达式仍使用旧字段
- **风险**：查询结果字段名与预期不符，下游消费方解析失败
- **解决方案**：
  - 扩展优化规则，覆盖 SELECT 投影、CASE/CONCAT 表达式
  - 强制保留原输出字段名（别名不变）

---

### 2.2 PO/Entity 层持久化字段问题

#### 坑点 4：PO 类字段与数据库列不同步
- **现象**：`RebateGroupPO` 被 MyBatis-Plus 自动查询时报错，提示 `provider_id` 列不存在
- **根因**：
  - 数据库表 `ts_rebate_group` 已删除 `provider_id` 列
  - 但 `RebateGroupPO` 类中仍有该字段的 `@TableField` 映射
  - MyBatis-Plus 的 `selectById` 等自动方法会生成包含该字段的 SQL
- **解决方案**：
  - 将 `RebateGroupPO.providerId` 改为非持久化字段：`@TableField(exist = false)`
  - 补充单元测试 `RebateGroupPOTest` 验证映射行为
- **风险等级**：高（运行时自动 SQL 查询不存在的列）

---

### 2.3 CDC（Change Data Capture）到 ES 链路问题

#### 坑点 5：CDC 配置未正确加载
- **现象**：`MultiCdcJobManager` 读到 0 个任务，`CdcTaskConfig.tasks` 保持默认空列表
- **根因**：`cdc-tasks.yml` 不属于 Spring Boot 默认自动加载配置文件，未被纳入配置源
- **解决方案**：
  - 实现 Spring/Nacos 到 CDC Definition 的配置补全桥接层
  - 拆分 CDC Job 的加载期校验与运行期最终校验
  - 精简任务 YAML，仅保留任务定义字段

#### 坑点 6：CDC 完全不启动（坏编译产物）
- **现象**：应用能启动但 CDC 完全不启动，`err.log` 中缺失 CDC 日志
- **根因**：`CdcJobBootstrapService.class` 是 IDEA 生成的坏编译产物，字节码内包含 `Unresolved compilation problem` stub
- **诊断难点**：
  - 不是源码错误，而是编译产物问题
  - 应用启动不报错，但 CDC 逻辑实际不按源码执行
- **解决方案**：
  - 修复日志调用兼容性（改为 `Object[]` 写法）
  - 手工重新编译该类
  - 增加超时诊断线程：当 `MySqlSource.builder().build()` 超过 10 秒未返回时，自动打印线程栈

#### 坑点 7：CDC 链路验证困难
- **现象**：无法执行单元测试，Maven 私服父 POM 返回 `401 Unauthorized`
- **解决方案**：
  - 手动编译相关源码子集与新增测试
  - 通过 `org.junit.runner.JUnitCore` 运行测试
  - 新增 `PrimaryKeyRoutingFlatMapFunctionTest`（6 个测试用例全部通过）
  - 新增 `LookupBatchingEsSinkTest` 验证 `_bulk` 请求体

#### 坑点 8：CDC 实现风险识别
- **风险 1**：低流量场景缓冲区可能长期不 flush
- **风险 2**：ES Bulk 200 响应下的局部失败未校验
- **风险 3**：DELETE 事件被忽略（当前只处理 insert/update）
- **缓解措施**：增加诊断日志，覆盖事件接收、路由成功、忽略原因、flush、SQL 回查、ES bulk 摘要

---

### 2.4 Maven / IDEA 环境问题

#### 坑点 9：Maven 401 Unauthorized
- **现象**：无法解析父 POM `com.leyo:leyo-springboot-parent:3.0.0-SNAPSHOT`
- **根因**：未使用带 nexus 凭据的 `settings.xml`
- **解决方案**：
  - 为项目补充本地 Maven 配置，自动指向 `D:\settings.xml`
  - 新增 `.mvn/maven.config`（使用 ASCII 无 BOM 写入，否则 Maven 3.8.9 报 `Unrecognized maven.config entries`）
  - 清理 `pom.xml` 中重复的 `leyo-core` 依赖声明

#### 坑点 10：IDEA JDK 配置错误
- **现象**：`java.jdt.ls.java.home` 指向 `D:\Program Files\java1.8`，提示 `SpringApplication cannot be resolved`
- **根因**：该目录仅包含 Java 8 运行时而非完整 JDK，缺少 `javac.exe`
- **解决方案**：
  - 更新为正确路径 `D:\Program Files\Java\jdk1.8.0_361`
  - 更新 `.vscode/settings.json`：
    - `java.configuration.runtimes[].path`
    - `java.jdt.ls.java.home`
    - Maven 终端环境变量 `JAVA_HOME`

#### 坑点 11：坏编译产物（Unresolved compilation problem）
- **现象**：`target/classes` 下的 `.class` 文件包含 `Unresolved compilation problem` stub
- **根因**：IDEA 增量编译污染 `target/classes`，生成 Eclipse 风格的错误桩 class
- **解决方案**：
  - 执行 `mvn clean compile`
  - 重启 IDEA 进程
  - 避免 IDEA 增量编译配置错误
- **识别方法**：使用 `javap -c` 查看 class 文件，若包含 `Unresolved compilation problem` 字符串即为坏产物

---

### 2.5 二次 Review 发现的风险

#### 坑点 12：for update 误改
- **风险**：带有 `FOR UPDATE` 的 SQL 被错误改写，可能导致锁表范围变化

#### 坑点 13：待审批统计 key 错位
- **风险**：待审批统计的 key 映射错位，导致统计结果不准确

#### 坑点 14：内部 PO 语义污染
- **风险**：内部使用的 PO 类被外部 SQL 引用，语义边界模糊

#### 坑点 15：公开列表漏改
- **风险**：部分公开列表接口的 provider 条件未改写，存在遗漏

---

## 三、核心技能、技术方法与最佳实践

### 3.1 Provider SQL 优化与审查体系

#### 技能文档沉淀
| 文档 | 路径 | 内容 |
|------|------|------|
| provider-sql-optimizer | `.cursor/skills/provider-sql-optimizer/SKILL.md` | SQL 改写规则、SELECT/表达式识别、别名保留 |
| provider-sql-reviewer | `.cursor/skills/provider-sql-reviewer/SKILL.md` | 审查项、分页一致性校验、运行时异常优先规则 |
| SQL 优化总结 | `SQL优化总结.md` | 优化范围、规则说明、风险清单 |
| SQL 优化审查报告 | `SQL优化审查报告.md` | 审查结果、问题分类、修复建议 |

#### 核心规则
1. **关联条件统一**：JOIN/ON/WHERE 中的 provider 条件统一使用 `provider_identity`
2. **投影字段统一**：SELECT 中的 provider 字段、CASE/CONCAT 表达式内部统一改写
3. **别名保留**：必须保留原输出字段名，避免下游消费方解析失败
4. **分页一致性**：`queryTotal` 与 `queryList` 的 provider 条件口径必须一致
5. **运行时优先**：运行库实际状态优先于 reference 文档

#### 二次 Review 机制
- 第一轮：自动化改写
- 第二轮：静态审查，重点检查 for update、待审批统计、内部 PO、公开列表

---

### 3.2 CDC 到 ES 实现模式

#### 核心数据链路
```
MySQL Binlog -> Flink CDC -> Debezium JSON -> 主键提取 -> SQL 回查 -> ES Bulk 写入
```

#### 关键组件
| 组件 | 职责 | 文件 |
|------|------|------|
| `CdcJobBootstrapService` | 启动时扫描并拉起 enabled 任务 | `CdcJobBootstrapService.java` |
| `LocalCdcJobDefinitionLoader` | 加载本地 YAML 任务定义 | `LocalCdcJobDefinitionLoader.java` |
| `SpringCdcJobDefinitionResolver` | 从 Spring/Nacos 补全配置 | `SpringCdcJobDefinitionResolver.java` |
| `PrimaryKeyRoutingFlatMapFunction` | Debezium 事件解析、insert/update 过滤、主键提取 | `PrimaryKeyRoutingFlatMapFunction.java` |
| `LookupBatchingEsSink` | 按主键批量回查 SQL 并写入 ES | `LookupBatchingEsSink.java` |

#### 配置补全规则
- MySQL 连接：从 `spring.datasource.dynamic.datasource.slave_1.*` 解析，自动去掉 `jdbc:p6spy:` 前缀
- ES 连接：从 `spring.data.elasticsearch.*` 读取，自动为未带协议的 host 补全 `http://`

#### 诊断能力
- 超时诊断：当 `MySqlSource.builder().build()` 超过 10 秒时，自动打印 CDC/Debezium/MySQL/Flink/Kafka 相关线程栈
- 日志覆盖：事件接收、路由成功、忽略原因、flush、SQL 回查、ES bulk 响应摘要

---

### 3.3 Maven 多模块项目环境管理

#### 本地配置
```
.mvn/maven.config          # 指向 settings.xml
.vscode/settings.json      # IDE JDK 配置
pom.xml                    # 清理重复依赖
```

#### 关键注意点
- `maven.config` 必须使用 ASCII 无 BOM 写入
- `JAVA_HOME` 必须指向完整 JDK（含 `javac.exe`），而非仅 JRE
- 私服认证信息配置在 `settings.xml` 的 `<servers>` 段

---

### 3.4 坏编译产物诊断与修复

#### 识别标志
- 运行时抛出 `Unresolved compilation problem`
- class 文件包含 `Unresolved compilation problem` 字符串
- 应用行为与源码逻辑不符

#### 修复步骤
1. 执行 `mvn clean compile`
2. 重启 IDEA 进程
3. 检查 IDEA 的 Maven 导入与编译器配置
4. 避免 IDEA 增量编译污染 `target/classes`

---

### 3.5 事务回调机制

#### 核心概念
- `TransactionSynchronizationManager.registerSynchronization` 注册事务同步回调
- `afterCommit` 在事务提交后执行，**不等于**仍在事务中执行业务提交
- 适用场景：事务后置处理、异步通知、手工重推机制

---

## 四、知识沉淀核查

### 4.1 已完整沉淀的内容

| 知识项 | 沉淀位置 | 状态 |
|--------|----------|------|
| Provider SQL 优化规则 | `.cursor/skills/provider-sql-optimizer/` | ✅ 完整 |
| Provider SQL 审查规则 | `.cursor/skills/provider-sql-reviewer/` | ✅ 完整 |
| CDC 实现模式 | `solar-sql-self-chk/README.md` + 单元测试 | ✅ 完整 |
| CDC 诊断日志 | `PrimaryKeyRoutingFlatMapFunction.java` / `LookupBatchingEsSink.java` | ✅ 完整 |
| Maven 环境配置 | 工作日志 04-02、04-16 | ✅ 记录 |
| 坏编译产物处理 | 工作日志 04-16、04-17 | ✅ 记录 |
| 28.28.0 需求拆分方法 | `AI开发拆分/` 目录 | ✅ 完整 |

### 4.2 建议进一步沉淀的内容

| 知识项 | 建议沉淀位置 | 优先级 |
|--------|--------------|--------|
| IDEA 坏编译产物处理指南 | `docs/troubleshooting/idea-bad-compilation-guide.md` | 高 |
| Maven 私服 401 问题速查 | `docs/troubleshooting/maven-401-cheat-sheet.md` | 中 |
| Provider ID 替换项目复盘 | `docs/retrospective/provider-id-migration.md` | 中 |

### 4.3 文档质量评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术难点记录 | ⭐⭐⭐⭐⭐ | 每个问题都有现象、根因、解决方案 |
| 风险识别 | ⭐⭐⭐⭐⭐ | 4 类主要风险已识别并记录 |
| 解决方案可复用性 | ⭐⭐⭐⭐⭐ | 形成 skill 文档，可复用 |
| 知识沉淀完整性 | ⭐⭐⭐⭐☆ | 核心技能已沉淀，部分最佳实践散落在日志中 |
| 文档可发现性 | ⭐⭐⭐☆☆ | skill 文档位置分散，建议建立索引 |

---

## 五、关键数据指标

### 5.1 问题统计
- SQL 层问题：4 个（分页混用、JOIN 类型不匹配、SELECT 投影、for update 误改）
- PO 层问题：1 个（字段映射不同步）
- CDC 层问题：4 个（配置未加载、坏编译产物、验证困难、实现风险）
- 环境问题：3 个（Maven 401、JDK 配置、坏编译产物）
- 合计：12 个主要"坑点"

### 5.2 产出文档
- Skill 文档：2 份（provider-sql-optimizer、provider-sql-reviewer）
- 设计文档：4 份（SQL 优化总结、审查报告、CDC 设计、28.28.0 拆分）
- 单元测试：4 个测试类（RebateGroupPOTest、RebateAuthProviderJoinGuardTest、PrimaryKeyRoutingFlatMapFunctionTest、LookupBatchingEsSinkTest）
- 工作日志：12 天完整记录

### 5.3 代码变更范围
- Mapper XML：RebateMapper.xml、RebateAuthMapper.xml、RebateReceiveDetailMapper.xml
- Java 类：RebateGroupPO、IRebateAuthMapper、CdcJobBootstrapService、CdcJobRunner、PrimaryKeyRoutingFlatMapFunction、LookupBatchingEsSink
- 配置：pom.xml、.mvn/maven.config、.vscode/settings.json、cdc/jobs/*.yml

---

## 六、经验总结与建议

### 6.1 技术债务清理的关键原则
1. **运行时优先**：数据库实际状态优先于文档，遇到冲突以运行库为准
2. **口径统一**：同一项目中同一业务概念必须使用统一字段名
3. **分页一致性**：MyBatis 分页查询的 count 和 list 必须保持完全一致的 WHERE 条件
4. **渐进式验证**：每改一处立即验证，避免批量改动后集中爆发问题

### 6.2 大规模 SQL 改写的最佳实践
1. **建立规则库**：将改写规则固化为 skill 文档，而非一次性脚本
2. **二次审查机制**：自动化改写后必须进行人工静态审查
3. **边界情况覆盖**：for update、内部 PO、公开列表等边界情况需重点检查
4. **回归测试**：每个改动点补充对应的单元测试

### 6.3 CDC 链路开发的注意事项
1. **配置分离**：任务定义与连接配置分离，便于环境切换
2. **诊断能力**：内置超时诊断和线程栈抓取，便于定位阻塞点
3. **异常处理**：ES Bulk 的局部失败需要显式校验，不能仅依赖 HTTP 状态码
4. **缓冲区管理**：低流量场景需要定时 flush 机制，避免数据滞留

### 6.4 环境问题的预防
1. **Maven 配置**：项目级 `.mvn/maven.config` 确保配置一致性
2. **JDK 校验**：启动脚本检查 `javac` 是否存在，避免 JRE 误用
3. **编译产物检查**：CI 流程中增加坏编译产物检测（检查 `Unresolved compilation problem` 字符串）
4. **IDE 配置**：统一团队 IDE 配置，避免个人设置污染项目

---

## 七、后续行动建议

1. **补充文档**：将 IDEA 坏编译产物处理指南、Maven 401 问题速查沉淀为独立文档
2. **建立索引**：创建 skill 文档总索引，提高知识可发现性
3. **完善测试**：补充 CDC 链路的集成测试，覆盖低流量 flush、ES 局部失败等场景
4. **团队分享**：组织技术分享会，将本项目经验推广到其他技术债务清理项目

---

*总结日期：2026-04-17*
*基于工作笔记：2026-03-30 至 2026-04-17*
