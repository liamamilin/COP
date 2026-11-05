# Claude Code 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `claude-01`｜结果视角｜理解陌生代码库并定位相关实现｜s-workflows
2. `claude-02`｜结果视角｜实现跨文件功能并运行验证｜s-overview
3. `claude-03`｜结果视角｜排查与修复程序错误｜s-overview
4. `claude-04`｜结果视角｜重构现有实现｜s-workflows
5. `claude-05`｜结果视角｜编写与维护项目测试｜s-workflows
6. `claude-06`｜结果视角｜准备和更新项目文档｜s-workflows
7. `claude-07`｜结果视角｜审查 GitHub PR 并定位反馈｜s-review
8. `claude-08`｜完整示例视角｜通过仓库自动化处理 Issue 和 PR｜s-actions
9. `claude-09`｜结果视角｜用真实浏览器验证和调试网页｜s-browser
10. `claude-10`｜结果视角｜自动填写表单并提取网页资料｜s-browser
11. `claude-11`｜结果视角｜将重复的专业流程做成可共享 Skill｜s-skills
12. `claude-12`｜结果视角｜把高噪声调查委托给专门子代理｜s-subagents
13. `claude-13`｜结果视角｜利用外部业务资料完成工程任务｜s-mcp
14. `claude-14`｜结果视角｜在生命周期事件执行确定性项目检查｜s-hooks
15. `claude-15`｜结果视角｜在需要输入时接收任务提醒｜s-hooks
16. `claude-16`｜结果视角｜撤回近期 AI 编辑并调整任务方向｜s-checkpoints
17. `claude-17`｜结果视角｜把开发分析放入脚本或 CI 批处理｜s-headless
18. `claude-18`｜结果视角｜跨会话复用团队规范和个人项目经验｜s-memory
19. `claude-19`｜结果视角｜从另一设备继续本机正在运行的任务｜s-remote
20. `claude-20`｜结果视角｜在当前会话中定期跟进长任务｜s-scheduled
21. `claude-21`｜结果视角｜将团队扩展打包分发｜s-plugins

## 归一化、补漏与停止依据

从日常开发结果逐项发现，再检查浏览器和事件自动化完整示例、MCP 与 Skill 等扩展。
归一化：把单次读写、命令、会话恢复合并入用户任务；保留可撤回修改、跨设备接续和外部系统协作等独立结果。
补漏区分受管理 Code Review 与 GitHub Actions、session loop 与持久任务、命令 Hook 与模型判断 Hook；避免把集成和模型效果混成内置保证。

## 保留的未知项

- 未登录安装客户端或实测各付费、托管和第三方连接能力。
- 当前公开资料未支持把检查点称为完整备份，也未支持把模型审查当作安全认证。
- 未穷尽企业托管、云 Routines、Channels 与每个平台的独占功能；这些路线的账户、组织和版本限制需专项验证。
- 完整任务示例以官方 common-workflows、Chrome 和 GitHub Action 配方为主；未把示例可行性升级为独立用户成功率统计。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-actions](https://code.claude.com/docs/en/github-actions.md) | 2026-11-05T08:56:27.770168+00:00 | 是 |
| [s-browser](https://code.claude.com/docs/en/chrome.md) | 2026-11-05T08:56:26.081715+00:00 | 是 |
| [s-checkpoints](https://code.claude.com/docs/en/checkpointing.md) | 2026-11-05T08:56:27.622062+00:00 | 是 |
| [s-headless](https://code.claude.com/docs/en/headless.md) | 2026-11-05T08:56:28.174933+00:00 | 是 |
| [s-hooks](https://code.claude.com/docs/en/hooks-guide.md) | 2026-11-05T08:56:26.540013+00:00 | 是 |
| [s-mcp](https://code.claude.com/docs/en/mcp.md) | 2026-11-05T08:56:27.021505+00:00 | 是 |
| [s-memory](https://code.claude.com/docs/en/memory.md) | 2026-11-05T09:26:49.771125+00:00 | 是 |
| [s-overview](https://code.claude.com/docs/en/overview.md) | 2026-11-05T08:56:24.675810+00:00 | 是 |
| [s-plugins](https://code.claude.com/docs/en/plugins.md) | 2026-11-05T09:26:50.049060+00:00 | 是 |
| [s-remote](https://code.claude.com/docs/en/remote-control.md) | 2026-11-05T09:26:49.775954+00:00 | 是 |
| [s-review](https://code.claude.com/docs/en/code-review.md) | 2026-11-05T09:26:49.443361+00:00 | 是 |
| [s-scheduled](https://code.claude.com/docs/en/scheduled-tasks.md) | 2026-11-05T09:26:49.557719+00:00 | 是 |
| [s-skills](https://code.claude.com/docs/en/skills.md) | 2026-11-05T08:56:26.759214+00:00 | 是 |
| [s-subagents](https://code.claude.com/docs/en/sub-agents.md) | 2026-11-05T08:56:26.842453+00:00 | 是 |
| [s-workflows](https://code.claude.com/docs/en/common-workflows.md) | 2026-11-05T08:56:26.070306+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`claude-02`、`claude-03`、`claude-07`、`claude-08`、`claude-10`、`claude-11`、`claude-14`、`claude-15`、`claude-17`、`claude-20`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
