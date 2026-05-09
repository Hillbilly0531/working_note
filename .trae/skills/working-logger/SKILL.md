---
name: working-logger
description: Use when any user message starts or continues a conversation, when working_note/working-note/working-logger is mentioned, or when work should be recorded as a daily Chinese work log.
---

# 工作日志记录器（Obsidian 双层产物）

## 核心原则

每轮用户消息都要把「本轮做了什么、改了哪里、验证了什么、有哪些经验候选」记录到固定工作日志。产物采用 **Obsidian Flavored Markdown**：YAML properties、层级标签、`[[wikilink]]`、callout。历史文件若无 frontmatter，只追加新条目，不批量改写全文。

## 强制触发

遇到以下任一情况，必须立即使用本技能：

- 收到用户任意消息（新会话或继续）
- 上下文出现 `working_note`、`working-note.md`、`working-logger`、`工作日志`
- 用户要求总结、复盘、记录、整理经验、继续上次工作

不要把「这轮只是询问」当成跳过理由。只要有判断、读文件、改文件、跑命令或产生待办，都要写入日志。

## 固定落盘位置

**每日工作日志（必选）：**

```text
D:\IdeaProjects\working_note\setting\leyo\working_note\{YYYY-MM-DD}.md
```

**月度经验索引（可选，有可复用经验时追加）：**

```text
D:\IdeaProjects\working_note\setting\leyo\working_note\experience\{YYYY-MM}.md
```

禁止把正式日志写入 `.working_logger`。若无法写入目标文件，须在回复中说明「日志未能落盘」及应补写内容。

## 双层关系

1. **每日日志**：记录事实、验证证据、`经验候选` callout（一句话即可）。
2. **经验索引**：只收录跨任务可复用的结论；从「经验候选」筛选后写入当月 `experience/{YYYY-MM}.md`，并用 `[[日期#标题]]` 反链来源。
3. 不强制每天更新经验索引；无值得沉淀的结论则跳过。

## 执行流程

1. 对话开始：读取当天日志；无文件则按「每日日志完整模板」新建（含 YAML）。
2. 对话过程：维护主题、完成项、进行中项、变更路径、验证结果、经验候选。
3. 阶段结束：在 `## 对话记录` 末尾追加一条 Obsidian 格式记录（时间顺序）。
4. 若本轮 `经验候选` 值得跨任务复用：在 `experience/{当月}.md` 增加或更新对应「经验卡片」，来源链回当日条目。
5. 落盘后确认路径；未写入则不得声称已记录。

## 模板文件（权威正文）

日志 Markdown **完整正文**与本 skill 同目录下的 `templates/` 保持一致（复制到落盘路径后替换占位符）。写入日志时优先读取对应模板再落盘：

| 用途 | 文件 |
| --- | --- |
| 新建当日完整文件（含 YAML frontmatter） | `templates/daily-work-log-new.md` |
| 仅在已有日文件末尾追加一条（不改文件头） | `templates/daily-entry-append.md` |
| 新建当月经验索引 `experience/{YYYY-MM}.md` | `templates/experience-index-month.md` |

路径示例：
- 本仓库：`{仓库根}/.trae/skills/working-logger/templates/`
- Trae 全局：`%USERPROFILE%\.trae-cn\skills\working-logger\templates\`
- Cursor 全局：`%USERPROFILE%\.cursor\skills\working-logger\templates\`

**规则**：当日文件已存在但无 frontmatter 时，勿强行插入 YAML；仅用「单条追加」模板。Obsidian 内部链接用 `[[wikilink]]`，外部 URL 用 Markdown 链接。

## 每日日志完整模板（新建文件时用）

若当日文件已存在但无 frontmatter，勿强行插入 YAML；仅在新建文件时使用 **`templates/daily-work-log-new.md`** 全文。

## 每日日志单条追加（已有文件、无 frontmatter 时）

使用 **`templates/daily-entry-append.md`**：在 `## 对话记录` 末尾追加，不必改写文件头部。

## 月度经验索引模板

路径：`experience/{YYYY-MM}.md`。首次创建当月文件时使用 **`templates/experience-index-month.md`** 全文。

## 经验沉淀写法

- **触发/落盘**：为什么漏触发、目录冲突、`description` 应写「何时使用」。
- **代码**：根因、修复点、验证命令或未验证原因。
- **文档**：模板字段、验收口径、待定项。
- **审查**：P0/P1、RULE-ID、复查入口。

## 常见错误

| 错误           | 正确做法                               |
| -------------- | -------------------------------------- |
| 只读技能不落盘 | 阶段结束前写入每日日志                 |
| 写入 `.working_logger` | 只写 `setting/leyo/working_note` |
| 经验只写流水   | 有价值时写入 `experience/{月}.md`    |
| 无验证却写完成 | 验证结果写明未执行原因                 |

## 自检清单

- [ ] 已读或确认当天 `setting/leyo/working_note/{YYYY-MM-DD}.md`
- [ ] 新文件含 YAML；旧文件仅追加条目不破坏历史
- [ ] 条目含元信息、摘要、任务、变更、验证、经验候选 callout
- [ ] 有可复用经验时已更新 `experience/{YYYY-MM}.md`
- [ ] 未写入 `.working_logger`
