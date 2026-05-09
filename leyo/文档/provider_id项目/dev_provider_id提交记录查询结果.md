# origin 上 providerid 项目提交记录查询结果

- 查询时间：2026-05-09
- 仓库路径：`D:\IdeaProjects\pms_rebate2`
- 远端：`origin -> http://g.leyopharm.com:8070/leyo/pms/pms_rebate.git`

## 说明

本次已按你的意思改为查询 `origin` 远端提交历史，而不是只看本地工作区。
已先执行 `git fetch origin --prune` 拉取最新远端引用后，再基于远端分支检索。

## 针对 `dev_provider_id` 的直接查询结果

执行过以下查询：

1. `git log --remotes=origin -S "dev_provider_id"`
2. `git log --remotes=origin -G "dev_provider_id"`

结论：

- `origin` 全部远端分支历史中，**没有检索到字面量 `dev_provider_id` 的提交记录**。

这说明：

1. 远端历史里大概率没有直接使用过 `dev_provider_id` 这个精确命名；或
2. 相关改造是围绕 `provider_id / providerId / providerIdentity / ysb_provider_id` 进行，而不是 `dev_provider_id`。

## providerid 项目高相关远端线索

从 `origin` 的提交信息检索到，providerid 项目主线主要集中在以下远端分支：

- `origin/dev-providerid-cxt`
- `origin/agent-provider-identity-alignment`
- `origin/dev-providerId-doubleWrite-2`
- `origin/gray-doubleWrite-2`
- `origin/rc-doubleWrite-2`

其中，**`origin/dev-providerid-cxt` 是这次 providerid 替换项目的主线分支**。

## 重点分支：origin/dev-providerid-cxt 关键提交

以下是从远端分支 `origin/dev-providerid-cxt` 中筛出的高相关提交，适合用来分析“漏改点”：

| 时间 | 提交人 | Commit | 提交说明 |
|---|---|---|---|
| 2026-05-09 11:46:22 +0800 | cxt | `56c8892e67cca3c648e065ca8f36001a0b8d9850` | 同一 Mapper 内将集团协议子协议统计相关三条聚合查询的供应商过滤列从 `ysb_provider_id` 改为 `provider_identity` |
| 2026-05-09 11:26:56 +0800 | cxt | `b71d36fb3fb33ccaac17061b73b0f41718b82664` | 在 `addRebateIntact` 链路补齐 `providerIdentity` 回填，避免下游出现 `"null"` |
| 2026-05-08 19:37:10 +0800 | cxt | `4a4dcce3c769f01aff1aa16ff49ae0a34db633cb` | 8 个 Mapper XML 调整 join，`ysb_provider_id` / `provider_identity` 关联策略修正 |
| 2026-05-08 18:29:33 +0800 | cxt | `7b92c57bf49fd55d0fa494ef7f4235cb540c2ecf` | 修改遗漏查询条件 |
| 2026-05-08 18:26:23 +0800 | cxt | `28fda28e54880d25aba147234974a40b7f63c373` | 修改遗漏查询条件 |
| 2026-05-08 18:14:58 +0800 | cxt | `d85068971d6f06078677fb5c9d00f5033fbb91cf` | 修改遗漏查询条件 `providerId` |
| 2026-05-08 17:43:48 +0800 | cxt | `81e2c7573d627dd4a2dbb7c7640319fa8c2120eb` | `RebateInputController` 中统一处理 `providerId` / `"null"` / 数字解析 |
| 2026-05-08 16:18:07 +0800 | cxt | `aece987e770980bc78a0af86cfa40a1b17b34bb2` | 阶段性总结：指出 2 条 P0，涉及 `ysbProviderId` 未回填、`providerIdentity == null` 被写成 0 |
| 2026-05-08 14:29:24 +0800 | cxt | `f3963559c3139fdc156a8aaf0d7c37ea76715f39` | `updateRabateLimit` 相关补充 |
| 2026-05-08 11:15:19 +0800 | cxt | `bb38c3707cae56b40add0fa6afd1f8fb350aded9` | fix: 统一处理 `providerIdentity` 字段，增加空值判断 |
| 2026-05-07 18:55:21 +0800 | cxt | `6d453cd1246741ae82889d48b0b72ec80fbf9876` | 修复 `providerId` 与 `providerIdentity` 字段不一致 |
| 2026-05-07 16:18:27 +0800 | cxt | `b3bbe60731d20a0442f2e304b508a2cc479659ce` | 修复异步任务异常处理和 `providerIdentity` 类型转换问题 |
| 2026-05-07 15:36:45 +0800 | cxt | `f4abfa115ff0862219d85a198f99f4d6d709d072` | 修正查询条件中的字段名错误 |
| 2026-05-07 14:00:16 +0800 | cxt | `9a16871e0a0a4e758752c1a8fff86337e42b2c27` | 修改遗漏 `providerid` |
| 2026-05-07 13:56:37 +0800 | cxt | `4f623520fed586f83ef5297f7eb7ed25fca18946` | 修改遗漏 `providerid` |
| 2026-05-07 11:45:40 +0800 | cxt | `d2e82848ea42f0dad01c5db0d976a474095521fd` | 修改遗漏 `providerid` |
| 2026-04-21 16:21:38 +0800 | cxt | `1d48013c5f20de4e5953c583c14786013cfd0aed` | `provider-id` 修改遗漏 |
| 2026-04-21 16:17:32 +0800 | cxt | `ab9b5555ad19985ae98bc9837b31b540d36005eb` | `provider_id` 修改遗漏 |
| 2026-04-20 16:39:43 +0800 | cxt | `25eb31bf28a2fa6d75e96e33882436c2dbf21896` | `providerId` 参数改为整型以匹配方法签名 |
| 2026-04-16 11:15:32 +0800 | cxt | `21d141154849ff7cbe4232f5bf7b66f753b7b448` | 将 `providerId` 改为 `providerIdentity` 使用整型标识 |
| 2026-04-16 10:43:17 +0800 | cxt | `9125eb299b7895ebe72d162e445ca76d1545ce84` | 移除重复的 `provider_id` 字段，仅保留 `provider_identity` |
| 2026-04-13 10:53:49 +0800 | cxt | `c879e366b7af1f2d0e8c00f073e711f564a2fa53` | 删除漏改的 `provider_id` |
| 2026-04-08 16:48:24 +0800 | cxt | `a8600ed120537fdb72b450329dcbf9f729fc0bf0` | 修复 `providerid` 漏网之鱼 |
| 2026-04-08 15:25:05 +0800 | cxt | `a2bec7cc41a3a0c13d3dcef88420c6f87091ab45` | 再次检查所有 xml 的 select 关联条件是否遗漏 |
| 2026-04-08 14:31:59 +0800 | cxt | `5f1a53cf17d43e54b708c6c557c9166433336f28` | 移除冗余 `provider_id` 字段并统一使用 `provider_identity` |
| 2026-04-08 12:24:57 +0800 | cxt | `03882b99682711891ef8e13f67c6ee2f596d2cb4` | 批量修复 `provider_id` 修改漏了的情况 |
| 2026-04-08 10:18:42 +0800 | cxt | `c2775c6012164899576fe03c4777d517f34b78ea` | 修复关联类型问题 |
| 2026-04-08 09:42:11 +0800 | cxt | `1617675370b265f971902286d35150a5bf067958` | 所有 PO 类把 `provider_id` 用 `@TableField(exist = false)` 注释掉 |
| 2026-04-07 17:41:56 +0800 | cxt | `e68a53224a246bd689d92a22d55b1d746e047d77` | 统一将 `ysb_provider_id` 重命名为 `provider_identity` |
| 2026-04-07 14:54:53 +0800 | cxt | `fe345f55522a4dd5583ec2155f61de0fd3a04e2e` | providerid 项目改 select 涉及的相关 providerId |

## 适合用于“漏改分析”的重点类型

从远端历史看，这次 providerid 项目最容易漏改的点主要有：

1. **Mapper XML 的 join / where / select / 聚合 SQL**
   - 特别是 `ysb_provider_id`、`provider_id`、`provider_identity` 混用
   - 聚合统计 SQL 容易只改列表主查询，漏改 count / sum / amount 子查询

2. **Java 参数类型不一致**
   - `String providerId`、`Integer providerIdentity`、`List<Integer>` 混用
   - `"null"` 字符串、空串、trim、数字解析异常等边界值容易漏

3. **对象字段双写/回填链路**
   - 只传 `ysbProviderId` 未回填 `providerIdentity`
   - `providerIdentity == null` 被错误写成 `0`
   - 老字段保留但新字段未同步赋值

4. **PO / DTO / Request / Response 字段残留**
   - `provider_id` 物理字段已废弃，但 Java 对象仍保留旧属性
   - `@TableField(exist = false)`、序列化字段、swagger 返回值容易漏

5. **统计/权限/关联条件**
   - 列表能查出，但统计金额为 0
   - 主查询和子查询使用的过滤键不一致
   - 权限服务组装的是 `providerIdList`，但 SQL 实际过滤的是 `provider_identity`

## 建议的下一步

如果你是为了系统性分析“providerid 项目漏改点”，建议下一步继续做两件事：

1. **导出这些关键 commit 的改动文件清单**
   - 可以按 commit 统计出涉及了哪些 Java / XML / PO / DTO / Service 文件
   - 有助于总结“高风险模块名单”

2. **从远端分支直接提取所有包含以下关键词的提交**
   - `provider_id`
   - `providerId`
   - `providerIdentity`
   - `ysb_provider_id`
   - `ysbProviderId`
   - `修改遗漏`
   - `漏改`

这样可以形成一份更适合排查漏改的“提交索引表”。

---

如果你要，我下一步可以直接继续帮你生成：

- **providerid项目_远端关键提交清单.md**
- **providerid项目_漏改高风险提交汇总.md**
- **providerid项目_按文件维度的改动热区统计.md**
