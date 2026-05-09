# providerid项目 远端关键提交清单

- 生成时间：2026-05-09
- 数据来源：`origin` 远端分支与远端提交历史
- 仓库：`D:\IdeaProjects\pms_rebate2`

## 一、远端主线分支判断

本次 providerid 项目相关的远端主线分支，按阶段可分为三段：

### 1. 第一阶段：双写过渡期

- `origin/feat-V25.4.0`
- `origin/dev-rewrite-providerIdentity`
- `origin/dev-providerId-doubleWrite-2`
- `origin/rc-doubleWrite-2`
- `origin/gray-doubleWrite-2`

这一阶段的核心目标是：
- 开始引入 `providerIdentity`
- 对部分链路进行 `providerId / providerIdentity` 双写兼容
- 修复双写过程中赋值、回填、撤回审批、复制协议等问题

### 2. 第二阶段：批量漏改修复期

- `origin/agent-provider-identity-alignment`
- `origin/dev-providerid-cxt`

这一阶段的核心目标是：
- 批量修复 `provider_id` / `ysb_provider_id` 遗漏替换
- 将 SQL / XML / PO / Mapper / 业务逻辑统一收口到 `provider_identity`
- 修复类型不一致、查询条件遗漏、关联字段遗漏、空值污染等问题

### 3. 第三阶段：主干合入期

已合入：
- `origin/master`
- `origin/gray-prod`
- `origin/rc-prod`
- `origin/test`

说明：
- `origin/master` 当前头提交：`1c38e2bda95fc2a2a2220cd216a00d84963c3711`
- 提交信息：`Merge branch 'dev-providerid-cxt' into 'master'`

---

## 二、最关键的远端分支

### A. `origin/agent-provider-identity-alignment`

- 最新提交：`03882b99682711891ef8e13f67c6ee2f596d2cb4`
- 时间：`2026-04-08 12:24:57 +0800`
- 作者：`cxt`
- 标题：`批量修复provider_id修改漏了的情况`

判断：
- 这是“批量扫漏改”的关键分支
- 非常适合作为你分析“漏改模式”的起点

### B. `origin/dev-providerid-cxt`

- 最新提交：`56c8892e67cca3c648e065ca8f36001a0b8d9850`
- 时间：`2026-05-09 11:46:22 +0800`
- 作者：`cxt`
- 标题摘要：将集团协议子协议统计相关三条聚合查询的供应商过滤列从 `ysb_provider_id` 改为 `provider_identity`

判断：
- 这是 providerid 项目的主收尾分支
- 大量“遗漏修复”“查询条件替换”“字段类型统一”“回填修复”都发生在该分支

### C. `origin/dev-providerId-doubleWrite-2`

- 最新提交：`59a63417d098349f047e3cd7f123951929aa668f`
- 时间：`2025-10-09 17:46:38 +0800`
- 作者：`caimingzhi`
- 标题：`Merge remote-tracking branch 'origin/master' into dev-providerId-doubleWrite-2`

判断：
- 这是双写第二批改造分支
- 适合用来定位“从旧字段向新字段迁移的过渡逻辑”

### D. `origin/dev-rewrite-providerIdentity`

- 最新提交：`86a6d76579e74e28b84312ed3882953c2cf8febd`
- 时间：`2025-09-09 18:26:17 +0800`
- 作者：`xuyueqin`
- 标题：`dev(rebate): 解决双写providerIdentity的问题`

判断：
- 这是 providerIdentity 双写问题的集中修复分支
- 对“赋值、回填、双写一致性”排查价值高

---

## 三、建议优先关注的关键提交

以下提交最适合拿来做“providerid 项目漏改点”分析。

### 1. 批量扫漏改

1. `03882b99682711891ef8e13f67c6ee2f596d2cb4`
   - `批量修复provider_id修改漏了的情况`
   - 价值：批量修复入口，适合找出首批扫到的高频漏改点

2. `a8600ed120537fdb72b450329dcbf9f729fc0bf0`
   - `修复providerid漏网之鱼`
   - 价值：说明第一轮替换后仍有残留

3. `c879e366b7af1f2d0e8c00f073e711f564a2fa53`
   - `删除漏改的provider_id`
   - 价值：说明旧字段仍残存在部分代码/实体/SQL 中

4. `ab9b5555ad19985ae98bc9837b31b540d36005eb`
   - `provider_id修改遗漏`

5. `1d48013c5f20de4e5953c583c14786013cfd0aed`
   - `provider-id修改遗漏`

6. `d2e82848ea42f0dad01c5db0d976a474095521fd`
   - `修改遗漏providerid`

7. `4f623520fed586f83ef5297f7eb7ed25fca18946`
   - `修改遗漏providerid`

8. `9a16871e0a0a4e758752c1a8fff86337e42b2c27`
   - `修改遗漏providerid`

### 2. SQL / XML / Join / 查询条件修复

1. `e68a53224a246bd689d92a22d55b1d746e047d77`
   - `统一将ysb_provider_id重命名为provider_identity`
   - 价值：字段替换主干提交

2. `5f1a53cf17d43e54b708c6c557c9166433336f28`
   - `移除冗余的provider_id字段并统一使用provider_identity`
   - 价值：SQL / Mapper 清理的重要依据

3. `a2bec7cc41a3a0c13d3dcef88420c6f87091ab45`
   - `再次查询所有的xml文件看下select 的关联条件有没有遗漏的，先保证xml文件没有遗漏`
   - 价值：说明 XML select / join 是漏改高发区

4. `08e9891dada821ba14d97efa676eebd46cbe8e1a`
   - `修复DAO下面的SQL没有替换成provider_identity的`
   - 价值：DAO SQL 仍有残留旧字段

5. `3339218aeb81715d53594cffcbae3a245d72101f`
   - `修复RebateGroupPO自动SQL查询旧字段问题`
   - 价值：自动生成 SQL / ORM 映射也可能残留旧字段

6. `4a4dcce3c769f01aff1aa16ff49ae0a34db633cb`
   - `8个 Mapper XML 中调整 JOIN；CommonProtocolMapper 中 JOIN 侧由 ysb_provider_id 改为 provider_identity`
   - 价值：Mapper XML 联表逻辑是重点排查区

7. `56c8892e67cca3c648e065ca8f36001a0b8d9850`
   - `聚合查询的供应商过滤列全部从 ysb_provider_id 改为 provider_identity`
   - 价值：统计/聚合查询不是只看主查询，也容易漏改

8. `d85068971d6f06078677fb5c9d00f5033fbb91cf`
   - `修改遗漏查询条件providerId`

9. `7b92c57bf49fd55d0fa494ef7f4235cb540c2ecf`
   - `修改遗漏查询条件`

10. `28fda28e54880d25aba147234974a40b7f63c373`
    - `修改遗漏查询条件`

11. `f4abfa115ff0862219d85a198f99f4d6d709d072`
    - `修正查询条件中的字段名错误`

### 3. 类型统一与语义统一

1. `21d141154849ff7cbe4232f5bf7b66f753b7b448`
   - `将providerId改为providerIdentity以使用整型标识`

2. `848d337b7dec0bd3b713d9bab12798de9b6abc3b`
   - `将providerId类型从String改为Integer`

3. `6d453cd1246741ae82889d48b0b72ec80fbf9876`
   - `修复providerId与providerIdentity字段不一致问题`

4. `b3bbe60731d20a0442f2e304b508a2cc479659ce`
   - `修复providerIdentity类型转换问题`

### 4. 回填 / 双写 / 空值污染修复

1. `aece987e770980bc78a0af86cfa40a1b17b34bb2`
   - 核心信息：`ysbProviderId -> providerIdentity` 迁移；发现两个 P0：
     - 新增路径未回填 `ysbProviderId`
     - `providerIdentity == null` 被静默写成 `0`
   - 价值：这是“漏改点分析”最重要提交之一

2. `b71d36fb3fb33ccaac17061b73b0f41718b82664`
   - `从 ysbProviderId 解析并回填 providerIdentity`
   - 价值：说明部分入口只传旧字段，需要补回填

3. `bb38c3707cae56b40add0fa6afd1f8fb350aded9`
   - `统一处理providerIdentity字段，增加空值判断`

4. `81e2c7573d627dd4a2dbb7c7640319fa8c2120eb`
   - `统一处理 providerId = "null" / 空白 / 非法格式`
   - 价值：前端或调用方脏数据是实际风险来源之一

### 5. 双写时期历史提交

1. `1e476dfe9d1800e09779b8fffca2c272db417e3e`
   - `双写providerIdentity`

2. `d6950fe856f43501d2bf1f36a2b62779f9392387`
   - `双写providerIdentity, 但是集团协议中这个字段没有意义，赋0`
   - 价值：这里就埋下了“0值污染”风险

3. `172825813b55d2265b3d83b29e5c42b68f60d1cb`
   - `双写providerIdentity, 但是集团协议中这个字段没有意义，赋0`

4. `20e9a7fb70b6f654e90d3c7f7a9c0d11e254e3b6`
   - `解决双写providerIdentity的问题`

5. `86a6d76579e74e28b84312ed3882953c2cf8febd`
   - `解决双写providerIdentity的问题`

6. `f8ae1731bf6ec95632864295cccc2a7fc794b7ad`
   - `providerId第二批改双写`

7. `88eee0154fc7df916c809871dcd3aea47806c81d`
   - `providerId第二批改双写，bug修改`

8. `2a323dded284374fef49ee0ddf1a1c60d84f4b2f`
   - `实收录入和冲红增加providerIdentity双写`

---

## 四、按问题类型初步归类

### 1. 容易漏改的位置

- Mapper XML 的 select / join / where
- DAO 层自定义 SQL
- 自动生成 SQL / PO 映射字段
- Controller 参数解析
- Service 内对象 copy / 组装 request 的链路
- 统计 / 聚合查询
- 审批撤回 / 复制协议 / 批次保存 / 异步任务等旁路流程

### 2. 容易漏改的字段组合

- `provider_id`
- `providerId`
- `provider_identity`
- `providerIdentity`
- `ysb_provider_id`
- `ysbProviderId`

### 3. 容易出问题的改法

- 只改主查询，漏改统计查询
- 只改 Java 字段，漏改 XML 条件
- 只改展示字段，漏改过滤条件
- 只改新增逻辑，漏改复制/撤回/异步/批量入口
- 将 `null` / 空串 / 非法值 写成 `0`
- `String` 与 `Integer` 混用
- 旧字段不再写入，但旧链路仍依赖旧字段

---

## 五、建议你下一步优先 diff 的提交

若要快速定位“还可能漏改的点”，建议按下面顺序看远端提交 diff：

1. `03882b99682711891ef8e13f67c6ee2f596d2cb4`
2. `e68a53224a246bd689d92a22d55b1d746e047d77`
3. `5f1a53cf17d43e54b708c6c557c9166433336f28`
4. `a2bec7cc41a3a0c13d3dcef88420c6f87091ab45`
5. `aece987e770980bc78a0af86cfa40a1b17b34bb2`
6. `b71d36fb3fb33ccaac17061b73b0f41718b82664`
7. `4a4dcce3c769f01aff1aa16ff49ae0a34db633cb`
8. `56c8892e67cca3c648e065ca8f36001a0b8d9850`
9. `6d453cd1246741ae82889d48b0b72ec80fbf9876`
10. `81e2c7573d627dd4a2dbb7c7640319fa8c2120eb`

---

## 六、结论

远端历史表明，providerid 项目不是一次性改完的，而是经历了：

1. 双写引入
2. 双写修复
3. 批量扫漏改
4. 再次补漏
5. 收尾修复统计/聚合/旁路逻辑

所以你要排查“漏改点”，不要只看：
- 主业务链路
- 主查询 SQL
- 新增接口

还要重点看：
- XML 聚合统计
- 复制/撤回/批量/异步/导入导出等旁路
- 旧字段仍被依赖的数据回填链路
- `null/0/空串/String-Integer` 的脏数据兼容逻辑
