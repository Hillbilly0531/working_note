# providerid项目 按文件维度改动热区统计

- 生成时间：2026-05-09
- 数据来源：基于 `origin` 远端提交信息的风险归纳
- 说明：当前文档是“按改动热区类型”整理，不是自动 diff 逐文件计数版；适合你后续人工/脚本二次排查

## 一、最热改动区域总览

根据远端提交标题和说明，providerid 项目的高频热区主要集中在以下文件/层级：

### 热区 1：Mapper XML
高风险原因：
- 出现了多次“查询条件遗漏”“JOIN 漏改”“DAO SQL 未替换”“再次扫 XML select”相关提交
- 说明该层是漏改最密集区域

重点对象：
- `*Mapper.xml`
- 尤其是涉及：
  - 协议列表
  - 集团协议子协议
  - 返利组
  - 权限过滤
  - 黑白名单
  - 实收/应收统计

重点模式：
- `provider_id`
- `ysb_provider_id`
- `provider_identity`
- `join supplydoc`
- `join supplystaffs`
- 聚合统计子查询

---

### 热区 2：Rebate Group / Common Protocol 相关 Mapper
从远端提交直接可见的高频区域：

1. `CommonProtocolMapper`
   - 统计聚合过滤列替换
   - JOIN 侧关联字段替换

2. `SeparatePlanMapper`
   - JOIN 改为带 cast 的关联

3. `SprRebateGroupMatchMapper`
   - 插入语句字段精简，移除冗余 `provider_id`

4. `RebateAuthMapper`
   - 相关 SQL / 逻辑优化发生在 providerid 项目期间

5. `RebateGroupPO` 对应的 Mapper / 自动 SQL
   - 有提交明确修复自动 SQL 查询旧字段问题

判断：
- 这些文件非常可能是“漏改反复出现”的热点

---

### 热区 3：PO / Entity / DO
从提交看，PO 层至少发生过这些动作：

- `provider_id` 字段被注释为 `@TableField(exist = false)`
- 删除 PO 中已不存在字段
- 修复自动 SQL 仍引用旧字段

这说明 PO 层有三类风险：

1. 字段仍保留，但语义已失效
2. 字段虽然不查，但 ORM 自动 SQL 仍会引用
3. Java 字段与 XML/SQL 字段不一致

重点排查：
- 所有带 `provider_id` / `providerIdentity` / `ysbProviderId` 的 PO
- 生成 update/select 语句的 BaseMapper / 自动 SQL 场景

---

### 热区 4：Controller / Request 参数解析
从提交可知至少发生过：

- `providerId` 的空白/`"null"`/非法数字兼容
- `providerId` 从 String 过渡到 Integer
- 单 providerId 查询列表的泛型收窄

判断：
- Controller 层是“输入脏数据”和“类型不统一”的高发区

重点排查：
- `RebateInputController`
- 接口入参带 `providerId` / `ysbProviderId` 的 Request 类
- 参数解析工具方法

重点模式：
- `normalizeProviderId`
- `parseProviderId`
- `String.valueOf`
- `Integer.valueOf`
- `NULL_PROVIDER_ID_LITERAL`

---

### 热区 5：Service 组装 / copy / 保存链路
从远端提交可以确认的问题：

- `addRebateIntact` 需要从 `ysbProviderId` 回填 `providerIdentity`
- 批次保存路径需要补充 `creator / ysbProviderId / providerIdentity / rebateMethod`
- 复制、撤回、冲红等旁路场景出现过 providerIdentity 赋值问题

判断：
- 只要有对象 copy、请求组装、批量保存，这些地方就极容易漏

重点排查：
- `addRebateIntact`
- `fillProviderIdentityFromYsbProviderId`
- `saveBatch` / `addBatch`
- copyObject / convert / assembler / clone 相关方法
- 复制协议、撤回审批、实收录入、冲红、异步任务相关 Service

---

## 二、按“漏改类型”反推的热区文件

### 1. 查询条件遗漏型
对应提交：
- `修改遗漏查询条件providerId`
- `修改遗漏查询条件`
- `修正查询条件中的字段名错误`

高热文件类型：
- `*Mapper.xml`
- `*Mapper.java`
- `*QueryService.java`
- `*StatisticsService.java`

### 2. 联表键遗漏型
对应提交：
- `JOIN 侧由 ysb_provider_id 改为 provider_identity`
- `关联条件没有做转换导致SQL变慢`

高热文件类型：
- `CommonProtocolMapper.xml`
- `SeparatePlanMapper.xml`
- 各类含 `supplydoc` / `supplystaffs` 联表的 XML

### 3. 字段残留型
对应提交：
- `删除漏改的provider_id`
- `移除冗余provider_id`
- `修改所有PO类，把provider_id用@TableField(exist = false)注释掉`

高热文件类型：
- `*PO.java`
- `*DO.java`
- `*Entity.java`
- 自动 SQL 所依赖的基础实体

### 4. 类型不一致型
对应提交：
- `providerId类型从String改为Integer`
- `providerId改为providerIdentity以使用整型标识`

高热文件类型：
- `*Controller.java`
- `*Request.java`
- `*Response.java`
- `*DTO.java`
- `*VO.java`

### 5. 双写与回填型
对应提交：
- `双写providerIdentity`
- `解决双写providerIdentity的问题`
- `从ysbProviderId解析并回填providerIdentity`

高热文件类型：
- 新增/修改协议保存相关 Service
- 实收录入、冲红、撤回、复制相关 Service
- 转换器 / 装配器 / copy 工具

---

## 三、建议优先人工抽查的文件类别

如果你现在要“少看文件但尽快抓到漏改”，建议优先抽查以下类别：

### 第一批：一定优先看
1. 集团协议 / 子协议相关 `Mapper.xml`
2. 返利组相关 `Mapper.xml`
3. 实收/应收统计相关 `Mapper.xml`
4. `RebateInputController` 及其 request 解析
5. 协议保存/复制/撤回相关 Service

### 第二批：高概率有暗坑
1. PO / DO / Entity
2. 自动 SQL 相关 BaseMapper 场景
3. 导出 / 汇总 / 仪表台统计
4. 异步任务 / 批处理逻辑

### 第三批：补充排查
1. 权限过滤逻辑
2. 黑白名单关联逻辑
3. 旧接口版本分支
4. 测试用例是否仍按旧字段断言

---

## 四、按关键词搜文件的建议清单

你后续可以让人或脚本直接按以下关键词扫“热区文件”：

### 旧字段残留
- `provider_id`
- `ysb_provider_id`
- `ysbProviderId`

### 新旧混用
- `providerId`
- `providerIdentity`
- `String.valueOf(`
- `Integer.valueOf(`
- `parseInt(`

### 高风险语义
- `= 0`
- `"null"`
- `join supplydoc`
- `join supplystaffs`
- `providerIdList`
- `copyObject`
- `addBatch`
- `saveBatch`
- `cancel`
- `revoke`
- `withdraw`
- `statistics`
- `sum(`
- `count(`

---

## 五、热区判断结论

本项目真正的“文件改动热区”不是 Controller，而是：

1. **Mapper XML**
2. **协议/返利组相关 Service 组装链路**
3. **PO/自动 SQL 映射层**
4. **统计/聚合查询文件**

换句话说，最该怀疑的不是“接口有没有改”，而是：

- 这个接口背后的 SQL 有没有全改
- 统计 SQL 有没有跟着改
- copy/save/批量/撤回/复制有没有补回填
- 旧字段是不是还在 PO 和 ORM 里偷偷生效

---

## 六、给你的一句实战建议

如果后面你准备做代码级漏改排查，最省时间的路径是：

1. 先扫全部 `Mapper.xml`
2. 再扫所有带 `providerIdentity / ysbProviderId / providerId` 的 Service
3. 最后扫 PO / Request / DTO 的类型与旧字段残留

这个顺序命中率最高。