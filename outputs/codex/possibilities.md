# Codex 可能性地图

范围：当前官方文档中的 Codex 编码工作流；覆盖 CLI、IDE、桌面与 Cloud 的结果，明确独立 SDK、插件和客户端的依赖。

资料截点：2026-11-05。本图有 21 项来源支持的结果，来自 19 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

核心能力需要可用模型、客户端、项目环境和授权；SDK、MCP、Skill 和 Security 的附加结果按条目标明。模型可完成的工程工作依赖可复现环境和用户核验。

## 地图导航

- [理解与交付工程改动](#engineering)
- [持续推进和跨设备协作](#continuity)
- [复用项目背景与专业流程](#team)
- [把任务接入自动化和自有工具](#automation)
- [专项安全调查](#security)

<a id="engineering"></a>
## 理解与交付工程改动

### `codex-01` 理解陌生仓库与定位修改入口

让 Codex 阅读仓库、解释模块关系及故障相关代码，形成后续修改的依据。

**内置／核心能力 · 有来源支持。** 需要可读取的代码与足够任务上下文。

来源：[s-noninteractive：Non-interactive mode · Basic usage；取回 Markdown第 24–24 行](https://learn.chatgpt.com/docs/non-interactive-mode.md)。

### `codex-02` 修复故障并补充回归测试

围绕具体失败复现、修改实现并添加测试；把可验证的修复作为交付物。

**内置／核心能力 · 有来源支持。** 必须提供或构造验证条件；模型建议和测试通过均不等于无遗漏。

来源：[s-goals：Using Goals in Codex: Persistent Objectives for Long-Running Work · Using Goals in Codex: Persistent Objectives for Long-Running Work；取回 Markdown第 7–7 行](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex.md)。

### `codex-03` 在编辑器上下文中实现功能修改

利用打开的文件和选区提出修改，在同一工作流检查差异并继续迭代。

**内置／核心能力 · 有来源支持。** 需要受支持 IDE 集成；复杂任务依赖环境、工具和账户。

来源：[s-ide：Codex IDE extension · Why use Codex IDE extension；取回 Markdown第 19–19 行](https://learn.chatgpt.com/docs/codex/ide.md)。

### `codex-04` 审查代码变更并形成可定位的问题反馈

结合变更及周边代码调查潜在问题，准备审查意见。

**内置／核心能力 · 有来源支持。** GitHub 支持与 GitLab 预览状态有区别；审查结果需要核实。

来源：[s-review：Code review · Code review；取回 Markdown第 6–6 行](https://learn.chatgpt.com/docs/code-review.md)。

### `codex-21` 迭代修复陈旧文档中的 API 示例

按官方 Cookbook 的检测、修复、验证闭环，识别过时示例并用运行反馈逐次改进。

**扩展／具名实现路线 · 有来源支持。** 这是具名工作流示例；需要自行提供文档解析、运行环境及验证器，不能保证对任意仓库直接复用。

来源：[s-repair：Build iterative repair loops with Codex · Build iterative repair loops with Codex；取回 Markdown第 7–7 行](https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex.md)。

<a id="continuity"></a>
## 持续推进和跨设备协作

### `codex-05` 让远程任务持续完成并产出可审查改动

把调查或开发任务交给有仓库和工具的云环境，在本机休眠时继续，返回后检查文件与测试结果。

**内置／核心能力 · 有来源支持。** 需要 Codex Cloud、已发布环境及仓库访问权；不是本地进程休眠后仍执行。

来源：[s-cloud：Codex Cloud · Why use Codex Cloud；取回 Markdown第 18–18 行](https://learn.chatgpt.com/docs/cloud.md)。

### `codex-06` 并行推进互不干扰的仓库任务

通过 Git worktree 为独立任务提供工作目录，再审查和整合各自变更。

**内置／核心能力 · 有来源支持。** 需要 Git 仓库、本机可用环境；目录隔离不等于依赖和外部状态全部隔离。

来源：[s-worktrees：Worktrees · Worktrees；取回 Markdown第 5–5 行](https://learn.chatgpt.com/docs/environments/git-worktrees.md)。

### `codex-07` 从手机跟进并指导已启动任务

在手机查看进度、处理审批并继续向云端或已连接电脑上的任务发送指令。

**内置／核心能力 · 有来源支持。** 依赖账户可用性、云环境或在线电脑；工作树不在手机上运行。

来源：[s-mobile：Codex on mobile · Start, guide, and review tasks from your phone；取回 Markdown第 7–7 行](https://learn.chatgpt.com/docs/mobile.md)。

### `codex-08` 让长期任务围绕验收条件持续迭代

把目标、成功判据与约束作为持久目标，依据调查和验证反馈继续工作。

**内置／核心能力 · 有来源支持。** 不是无限执行或必然成功；需要适用版本、预算与可检查的完成条件。

来源：[s-goals：Using Goals in Codex: Persistent Objectives for Long-Running Work · Using Goals in Codex: Persistent Objectives for Long-Running Work；取回 Markdown第 5–5 行](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex.md)。

### `codex-13` 对独立子任务分工并收敛结果

按明确请求将代码探索、测试或方案调查交给专门子代理，再合并结论。

**内置／核心能力 · 有来源支持。** 本地版本和客户端支持有条件；额外模型与工具工作消耗更多 token，写入需协调。

来源：[s-subagents：Subagents · Subagents；取回 Markdown第 5–6 行](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)。

<a id="team"></a>
## 复用项目背景与专业流程

### `codex-09` 将团队规范带入仓库任务

用分层项目说明为任务提供代码规范、测试要求和工作约定。

**内置／核心能力 · 有来源支持。** AGENTS.md 是指导信息，不能代替权限控制或确定性校验。

来源：[s-instructions：Custom instructions with AGENTS.md · Custom instructions with AGENTS.md；取回 Markdown第 5–5 行](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md)。

### `codex-10` 把反复完成的专业工作包装为可复用流程

以 Skill 的说明和资源复用研究、评审或制作过程，减少重复交代。

**扩展／具名实现路线 · 有来源支持。** 需要编写或安装可信 Skill；Plugin 可附加工具，能力取决于具体资源。

来源：[s-skills：Skills & Plugins · Skills & Plugins；取回 Markdown第 13–13 行](https://learn.chatgpt.com/docs/skills-and-plugins.md)。

### `codex-11` 在后续工作中复用已积累的项目背景

启用本地记忆后，让符合条件的既往聊天提炼背景供后续任务参考。

**内置／核心能力 · 有来源支持。** 本地 Codex 记忆与 ChatGPT 网页记忆分开；默认、启用范围和延迟见当前文档，不作为唯一规范来源。

来源：[s-memories：Memories · Memories；取回 Markdown第 5–6 行](https://learn.chatgpt.com/docs/customization/memories.md)。

### `codex-12` 利用外部系统的信息完成开发任务

通过配置好的 MCP 服务检索工单、文档等资料或调用外部工具。

**扩展／具名实现路线 · 有来源支持。** 需要相应服务器、授权及依赖；每个外部服务的写入能力与权限不同。

来源：[s-mcp：Model Context Protocol · Model Context Protocol；取回 Markdown第 5–5 行](https://learn.chatgpt.com/docs/extend/mcp.md)。

<a id="automation"></a>
## 把任务接入自动化和自有工具

### `codex-14` 在任务结束点自动执行自定义检查

以 Hook 调用本地校验脚本，收集或阻止不符合项目要求的结果。

**扩展／具名实现路线 · 有来源支持。** 用户需实现脚本并信任非托管 Hook；并发 Hook 的执行不能假定串行防护。

来源：[s-hooks：Hooks · Hooks；取回 Markdown第 11–11 行](https://learn.chatgpt.com/docs/hooks.md)。

### `codex-15` 批量生成机器可处理的仓库分析结果

在脚本中运行非交互任务，用 JSON Schema 约束最终报告，交给下游流程处理。

**内置／核心能力 · 有来源支持。** 需要 CLI、认证、预设权限及对结果内容的验证；结构化不代表语义正确。

来源：[s-noninteractive：Non-interactive mode · Create structured outputs with a schema；取回 Markdown第 94–94 行](https://learn.chatgpt.com/docs/non-interactive-mode.md)。

### `codex-16` 把编码任务接入现有 CI 或内部工具

使用 Codex SDK 在程序中启动任务、追踪结果并组织自己的工程流程。

**扩展／具名实现路线 · 有来源支持。** SDK 是开发集成路线，仍需运行环境、认证、成本与失败处理。

来源：[s-sdk：Codex SDK · Codex SDK；取回 Markdown第 9–9 行](https://learn.chatgpt.com/docs/codex-sdk.md)。

### `codex-17` 构建有会话与审批的自有 Codex 客户端

通过 app-server 接入认证、会话历史、审批和流式事件，制作定制交互界面。

**扩展／具名实现路线 · 有来源支持。** 需要开发客户端并管理协议兼容性；旧 codex mcp-server 已移除，不能照旧教程直接使用。

来源：[s-appserver：Codex App Server · Codex App Server；取回 Markdown第 5–5 行](https://learn.chatgpt.com/docs/app-server.md)。

### `codex-18` 定期执行本地项目巡检和报告任务

安排周期任务在项目目录或隔离工作树执行，再检查运行结果。

**内置／核心能力 · 有来源支持。** 本地文件任务要求电脑开机且应用运行；账户、工作区及云端任务能力不同。

来源：[s-automations：Scheduled tasks · Scheduled tasks；取回 Markdown第 5–5 行](https://learn.chatgpt.com/docs/automations.md)。

### `codex-19` 为 GitHub PR 自动触发审查反馈

配置 GitHub 集成，让 PR 或指定评论触发 Codex 审查，形成仓库内反馈。

**扩展／具名实现路线 · 有来源支持。** 需要连接仓库、正确权限与审查配置；与独立 Security 服务区分。

来源：[s-github：Review GitHub pull requests with Codex · Request a Codex review；取回 Markdown第 68–68 行](https://learn.chatgpt.com/docs/third-party/github.md)。

<a id="security"></a>
## 专项安全调查

### `codex-20` 对仓库生成有证据的安全发现报告

安装 Codex Security 插件，在仓库执行扫描并取得证据和修复指导。

**扩展／具名实现路线 · 有来源支持。** 独立插件能力；本地与 Cloud 插件分开，访问资格及使用条件需另核实，不保证发现所有漏洞。

来源：[s-security-plugin：Codex Security plugin quickstart · Codex Security plugin quickstart；取回 Markdown第 7–7 行](https://learn.chatgpt.com/docs/security/plugin.md)。

## 资料覆盖与发现过程

结果遍历从仓库理解、修改、验证和审查开始，随后检查云端、自动化、扩展与完整修复案例。
归一化：将命令调用、文件读写合并入实际开发结果；移动端保留为跨设备接续这一独立结果。
补漏发现当前集成路线为 app-server，旧 MCP server 命令已移除；本地记忆与网页记忆、Security 与普通审查分别核实。
按所有候选的实际目的建立导航；未因已有主题的分类结构或预定数量停止。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未安装运行各客户端、SDK、Security 或 Cloud 环境；这些条目是文档支持，不是本次执行证书。
- 没有把 ChatGPT Work 专属的联网办公、事件任务、Computer History 等直接视为 Codex 通用能力。
- 版本迁移后官方文档位于 learn.chatgpt.com；不同客户端、计划和工作区的功能开放范围需部署前再确认。
- 真实案例以官方迭代修复 Cookbook 为主；未获得独立第三方项目成效的可重复评测。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
