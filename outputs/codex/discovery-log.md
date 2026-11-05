# Codex 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `codex-01`｜结果视角｜理解陌生仓库与定位修改入口｜s-goals
2. `codex-02`｜结果视角｜修复故障并补充回归测试｜s-goals
3. `codex-03`｜结果视角｜在编辑器上下文中实现功能修改｜s-ide
4. `codex-04`｜结果视角｜审查代码变更并形成可定位的问题反馈｜s-review
5. `codex-05`｜结果视角｜让远程任务持续完成并产出可审查改动｜s-cloud
6. `codex-06`｜结果视角｜并行推进互不干扰的仓库任务｜s-worktrees
7. `codex-07`｜结果视角｜从手机跟进并指导已启动任务｜s-mobile
8. `codex-08`｜结果视角｜让长期任务围绕验收条件持续迭代｜s-goals
9. `codex-09`｜结果视角｜将团队规范带入仓库任务｜s-instructions
10. `codex-10`｜结果视角｜把反复完成的专业工作包装为可复用流程｜s-skills
11. `codex-11`｜结果视角｜在后续工作中复用已积累的项目背景｜s-memories
12. `codex-12`｜结果视角｜利用外部系统的信息完成开发任务｜s-mcp
13. `codex-13`｜结果视角｜对独立子任务分工并收敛结果｜s-subagents
14. `codex-14`｜结果视角｜在任务结束点自动执行自定义检查｜s-hooks
15. `codex-15`｜结果视角｜批量生成机器可处理的仓库分析结果｜s-noninteractive
16. `codex-16`｜结果视角｜把编码任务接入现有 CI 或内部工具｜s-sdk
17. `codex-17`｜结果视角｜构建有会话与审批的自有 Codex 客户端｜s-appserver
18. `codex-18`｜结果视角｜定期执行本地项目巡检和报告任务｜s-automations
19. `codex-19`｜结果视角｜为 GitHub PR 自动触发审查反馈｜s-github
20. `codex-20`｜结果视角｜对仓库生成有证据的安全发现报告｜s-security-plugin
21. `codex-21`｜完整案例视角｜迭代修复陈旧文档中的 API 示例｜s-repair

## 归一化、补漏与停止依据

结果遍历从仓库理解、修改、验证和审查开始，随后检查云端、自动化、扩展与完整修复案例。
归一化：将命令调用、文件读写合并入实际开发结果；移动端保留为跨设备接续这一独立结果。
补漏发现当前集成路线为 app-server，旧 MCP server 命令已移除；本地记忆与网页记忆、Security 与普通审查分别核实。
按所有候选的实际目的建立导航；未因已有主题的分类结构或预定数量停止。

## 保留的未知项

- 未安装运行各客户端、SDK、Security 或 Cloud 环境；这些条目是文档支持，不是本次执行证书。
- 没有把 ChatGPT Work 专属的联网办公、事件任务、Computer History 等直接视为 Codex 通用能力。
- 版本迁移后官方文档位于 learn.chatgpt.com；不同客户端、计划和工作区的功能开放范围需部署前再确认。
- 真实案例以官方迭代修复 Cookbook 为主；未获得独立第三方项目成效的可重复评测。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-approvals](https://learn.chatgpt.com/docs/agent-approvals-security.md) | 2026-11-05T09:21:26.014773+00:00 | 否 |
| [s-appserver](https://learn.chatgpt.com/docs/app-server.md) | 2026-11-05T09:26:48.509487+00:00 | 是 |
| [s-automations](https://learn.chatgpt.com/docs/automations.md) | 2026-11-05T09:21:25.850277+00:00 | 是 |
| [s-cloud](https://learn.chatgpt.com/docs/cloud.md) | 2026-11-05T09:21:22.784514+00:00 | 是 |
| [s-codex-index](https://learn.chatgpt.com/docs/llms.txt) | 2026-11-05T09:06:12.436620+00:00 | 否 |
| [s-cookbook-index](https://developers.openai.com/cookbook/llms.txt) | 2026-11-05T09:26:48.137248+00:00 | 否 |
| [s-customization](https://learn.chatgpt.com/docs/customization/overview.md) | 2026-11-05T09:21:26.669887+00:00 | 否 |
| [s-github](https://learn.chatgpt.com/docs/third-party/github.md) | 2026-11-05T09:21:24.728708+00:00 | 是 |
| [s-goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex.md) | 2026-11-05T08:56:24.681142+00:00 | 是 |
| [s-hooks](https://learn.chatgpt.com/docs/hooks.md) | 2026-11-05T09:21:23.194168+00:00 | 是 |
| [s-ide](https://learn.chatgpt.com/docs/codex/ide.md) | 2026-11-05T09:26:48.124294+00:00 | 是 |
| [s-index](https://developers.openai.com/llms.txt) | 2026-11-05T08:56:24.619578+00:00 | 否 |
| [s-instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md) | 2026-11-05T09:21:24.343519+00:00 | 是 |
| [s-mcp](https://learn.chatgpt.com/docs/extend/mcp.md) | 2026-11-05T09:21:23.015097+00:00 | 是 |
| [s-memories](https://learn.chatgpt.com/docs/customization/memories.md) | 2026-11-05T09:26:47.946745+00:00 | 是 |
| [s-mobile](https://learn.chatgpt.com/docs/mobile.md) | 2026-11-05T09:21:24.417442+00:00 | 是 |
| [s-noninteractive](https://learn.chatgpt.com/docs/non-interactive-mode.md) | 2026-11-05T09:26:48.125555+00:00 | 是 |
| [s-platform](https://developers.openai.com/blog/codex-as-a-platform.md) | 2026-11-05T08:56:24.676632+00:00 | 否 |
| [s-repair](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex.md) | 2026-11-05T08:56:24.933799+00:00 | 是 |
| [s-review](https://learn.chatgpt.com/docs/code-review.md) | 2026-11-05T09:21:22.814992+00:00 | 是 |
| [s-sdk](https://learn.chatgpt.com/docs/codex-sdk.md) | 2026-11-05T09:21:22.906093+00:00 | 是 |
| [s-security-plugin](https://learn.chatgpt.com/docs/security/plugin.md) | 2026-11-05T09:21:24.512209+00:00 | 是 |
| [s-security](https://learn.chatgpt.com/docs/security.md) | 2026-11-05T09:21:24.521264+00:00 | 否 |
| [s-skills](https://learn.chatgpt.com/docs/skills-and-plugins.md) | 2026-11-05T09:21:24.350901+00:00 | 是 |
| [s-subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md) | 2026-11-05T09:26:48.111329+00:00 | 是 |
| [s-worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees.md) | 2026-11-05T09:21:22.976414+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`codex-01`、`codex-08`、`codex-09`、`codex-10`、`codex-11`、`codex-14`、`codex-16`、`codex-18`、`codex-19`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
