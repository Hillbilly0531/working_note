# providerid项目 漏改高风险提交汇总

- 生成时间：2026-05-09
- 数据来源：`origin` 远端提交历史
- 目标：用于分析 providerid 项目还可能漏改的点

## 一、最高优先级风险结论

根据远端提交信息，providerid 项目的漏改风险主要集中在以下 6 类：

1. **XML / SQL 查询条件漏改**
2. **关联字段从 `ysb_provider_id` / `provider_id` 切到 `provider_identity` 时未全链路替换**
3. **双写阶段留下的脏数据与兼容逻辑问题**
4. **只传旧字段 `ysbProviderId`，未回填 `providerIdentity`**
5. **`providerId` / `providerIdentity` 的 String / Integer 类型不一致**
6. **统计/聚合/旁路流程未同步改造**

---

## 二、P0 级高风险提交

### 1. `aece987e770980bc78a0af86cfa40a1b17b34bb2`

标题摘要：
- `ysbProviderId` 链路迁移到 `providerIdentity`
- 明确发现 2 条 P0

风险点：
1. 新增路径未再回填 `ysbProviderId`
2. `providerIdentity == null` 被静默写成 `0`

为什么高风险：
- 这两个问题都不是“看起来报错”的问题，而是“能继续跑但数据变脏”的问题
- 最容易形成后续难排查的串数据、错匹配、旧链路失效

建议排查：
- 所有新增/保存/复制/批量保存路径是否同时处理 `ysbProviderId` 与 `providerIdentity`
- 是否存在 `null -> 0` 的兜底写法
- 下游是否仍依赖旧字段做查询、联表或推送

---

### 2. `b71d36fb3fb33ccaac17061b73b0f41718b82664`

标题摘要：
- 从 `ysbProviderId` 解析并回填 `providerIdentity`

风险点：
- 某些入口只传旧字段，不传新字段
- 如果这个回填逻辑只在一条链路加了，其他链路仍可能漏掉

建议排查：
- `addRebateIntact` 之外是否还有新增/更新入口
- 复制、导入、批量、撤回后重提、异步回放是否也有同类对象组装
- request / dto / vo copy 时是否丢失新字段

---

### 3. `56c8892e67cca3c648e065ca8f36001a0b8d9850`

标题摘要：
- 聚合查询的供应商过滤列从 `ysb_provider_id` 改为 `provider_identity`

风险点：
- 主查询可能已经改了，但金额、实收、汇总统计仍在用旧字段
- 会出现“列表能查到，但金额为0 / 统计不对 / 数量不对”的情况

建议排查：
- 所有 sum/count/group by 子查询
- 列表页 + 汇总卡片 + 导出统计 是否使用同一套字段
- 是否存在“展示维度已改，过滤维度仍旧”的情况

---

## 三、SQL / XML 漏改高风险提交组

### 1. `a2bec7cc41a3a0c13d3dcef88420c6f87091ab45`
- `再次查询所有的xml文件看下select 的关联条件有没有遗漏的，先保证xml文件没有遗漏`

结论：
- 开发者已经明确指出：**XML 文件中的 select / join / 关联条件存在大面积漏改风险**

### 2. `08e9891dada821ba14d97efa676eebd46cbe8e1a`
- `修复DAO下面的SQL没有替换成provider_identity的`

结论：
- 风险不只在 XML，也在 DAO 自定义 SQL

### 3. `4a4dcce3c769f01aff1aa16ff49ae0a34db633cb`
- `8个 Mapper XML 中调整 JOIN；CommonProtocolMapper 中 JOIN 侧由 ysb_provider_id 改为 provider_identity`

结论：
- 多个 Mapper 同时改 JOIN，说明联表键替换不彻底

### 4. `3339218aeb81715d53594cffcbae3a245d72101f`
- `修复RebateGroupPO自动SQL查询旧字段问题`

结论：
- 即便手写 SQL 改完，也可能被 ORM / 自动 SQL / PO 字段映射拖回来

### 5. `d85068971d6f06078677fb5c9d00f5033fbb91cf`
- `修改遗漏查询条件providerId`

### 6. `7b92c57bf49fd55d0fa494ef7f4235cb540c2ecf`
- `修改遗漏查询条件`

### 7. `28fda28e54880d25aba147234974a40b7f63c373`
- `修改遗漏查询条件`

### 8. `f4abfa115ff0862219d85a198f99f4d6d709d072`
- `修正查询条件中的字段名错误`

建议重点排查：
- 所有 XML 中的：`where`、`join on`、`exists`、`in`、`group by`、`order by`
- 所有手写 SQL 中的供应商关联列
- 自动拼接查询条件、Wrapper、自定义条件构造器

---

## 四、双写阶段遗留高风险提交组

### 1. `1e476dfe9d1800e09779b8fffca2c272db417e3e`
- `双写providerIdentity`

### 2. `d6950fe856f43501d2bf1f36a2b62779f9392387`
- `双写providerIdentity, 但是集团协议中这个字段是没有意义的，赋0`

### 3. `172825813b55d2265b3d83b29e5c42b68f60d1cb`
- `双写providerIdentity, 但是集团协议中这个字段是没有意义的，赋0`

### 4. `20e9a7fb70b6f654e90d3c7f7a9c0d11e254e3b6`
- `解决双写providerIdentity的问题`

### 5. `86a6d76579e74e28b84312ed3882953c2cf8febd`
- `解决双写providerIdentity的问题`

风险判断：
- 双写最怕“一个字段真实，一个字段填默认值”
- `赋0` 的策略极可能导致：
  - 查询误命中/误过滤
  - 权限范围错判
  - 数据后续被当成合法值继续流转

建议重点排查：
- 是否还有 `providerIdentity = 0` 的历史兜底
- 集团协议/普通协议/组合订单是否采用不同字段语义
- 读取逻辑是否对 `0`、`null`、空串做了不一致判断

---

## 五、字段类型不一致风险提交组

### 1. `21d141154849ff7cbe4232f5bf7b66f753b7b448`
- `将providerId改为providerIdentity以使用整型标识`

### 2. `848d337b7dec0bd3b713d9bab12798de9b6abc3b`
- `将providerId类型从String改为Integer`

### 3. `6d453cd1246741ae82889d48b0b72ec80fbf9876`
- `修复providerId与providerIdentity字段不一致问题`

### 4. `b3bbe60731d20a0442f2e304b508a2cc479659ce`
- `修复providerIdentity类型转换问题`

### 5. `81e2c7573d627dd4a2dbb7c7640319fa8c2120eb`
- 统一处理 `providerId = "null"` / 空白 / 非法数字

风险判断：
- 类型切换说明接口、VO、Controller、Service、Mapper 之间并不统一
- 最容易漏的是：
  - 请求入参仍是 String
  - SQL 参数要求 Integer
  - `String.valueOf(null)` 生成字符串 `"null"`
  - List 泛型收窄不彻底

建议重点排查：
- Controller 入参解析
- DTO / Request / Response 类型定义
- JSON copy / Bean copy 后字段类型是否匹配
- MyBatis parameterType / resultMap 是否仍按旧类型处理

---

## 六、旁路流程漏改高风险提交组

### 1. `1942759dbb872c45cfedbad938bab4355214e50a`
- 撤回审批增加 `providerIdentity` 赋值问题修复

### 2. `34ffbc2b215df379956194686113e3936d077d1c`
- 撤回审批增加 `providerIdentity` 赋值

### 3. `5493c3aacf81b0555b648dd493dee6ce73eb6ba9`
- 统管协议复制时查询 `providerIdentity` 赋值导致空列表问题

### 4. `0ac66eb05a8ad65ef291c244f862ba04cbfa38dc`
- 修复提供商标识比较逻辑错误

### 5. `b71d36fb3fb33ccaac17061b73b0f41718b82664`
- 批次保存路径补充 `creator / ysbProviderId / providerIdentity / rebateMethod`

### 6. `08af33bfefb37c7907bf683dc964e5d0ca505073`
- `单位关联判断没有使用编码来判断 漏改接口`

风险判断：
- 主路径改完后，复制、撤回、冲红、批量保存、异步任务、导入导出最容易漏
- 这些场景通常不会在第一轮全量替换里被覆盖

建议重点排查：
- 撤回审批
- 复制协议
- 批次保存
- 冲红 / 实收录入
- 异步任务
- 导出统计 / 详情回显
- 接口版本分支逻辑

---

## 七、最可能继续漏改的代码区域

结合远端提交信息，下面这些区域是你下一轮排查的重点：

### 1. Mapper XML
重点查：
- `join supplydoc`
- `join supplystaffs`
- `provider_id`
- `ysb_provider_id`
- `provider_identity`
- `providerIdList`
- 聚合子查询
- count/sum 统计语句

### 2. PO / DO / Entity / Mapper 自动 SQL
重点查：
- 旧字段是否仍保留但未完全失效
- `@TableField(exist = false)` 是否只是临时掩盖
- 自动生成 SQL 是否仍会把旧字段带出去

### 3. Controller / Request / DTO
重点查：
- `providerId` 是否仍以 String 接收
- 是否存在 `"null"` 字面量兼容
- 是否有只传 `ysbProviderId` 的入口

### 4. Service 组装链路
重点查：
- copyObject / convert / assembler
- saveBatch / addBatch / update / copy / clone
- 撤回重提 / 复制旧单据

### 5. 统计 / 汇总 / 导出
重点查：
- 列表查得出但金额为 0
- 汇总卡片与明细不一致
- 导出与页面不一致

---

## 八、推荐你的排查顺序

### 第 1 层：查旧字段残留
- `provider_id`
- `ysb_provider_id`
- `providerId`
- `ysbProviderId`

### 第 2 层：查“条件”和“关联”残留
- `where ... provider`
- `join ... provider`
- `in (...)`
- `group by`
- `sum/count`

### 第 3 层：查脏数据兼容逻辑
- `== 0`
- `"null"`
- `String.valueOf`
- `Integer.valueOf`
- `parseInt`
- 空值早退

### 第 4 层：查旁路流程
- copy
- revoke / withdraw / cancel
- batch
- async
- export
- statistics

---

## 九、最终结论

providerid 项目的远端提交历史说明：

- 这个项目不是单纯“字段改名”
- 它本质上是一次：
  - 字段语义替换
  - 数据兼容迁移
  - SQL 关联键切换
  - 类型体系调整
  - 旁路流程补漏

所以真正高风险的漏改点，不在“看得到的主流程”，而在：

1. 旧字段残留的 SQL / XML
2. 聚合统计查询
3. 复制 / 撤回 / 批量 / 异步流程
4. 双写阶段写入的脏值 `0` / `null`
5. 只传旧字段、未回填新字段的入口
6. String / Integer 类型混用

如果后面你要继续做实战排查，建议下一步直接基于这些高风险模式，对当前代码做“按模式搜索清单”输出。