# Claude Code 可能性地图

范围：Claude Code 日常开发结果、当前官方工作流与扩展生态；区分 CLI / 桌面 / 网页、Agent SDK、Chrome、GitHub Actions 和独立 Code Review。

资料截点：2026-11-05。本图有 21 项来源支持的结果，来自 15 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

Claude Code 的工具执行受账户、环境、授权与模型质量约束。原生工作流与独立扩展按条目标注；不会因为官方有示例就视为已在本仓库运行成功。

## 地图导航

- [理解、修改和说明软件](#development)
- [审查变更与浏览器验证](#verification)
- [复用知识、流程与外部信息](#reuse)
- [委托、接续和调整工作](#control)
- [事件与批量自动化](#automation)

<a id="development"></a>
## 理解、修改和说明软件

### `claude-01` 理解陌生代码库并定位相关实现

通过阅读、搜索和解释了解仓库结构，为具体开发问题找到入口。

**内置／核心能力 · 有来源支持。** 需要仓库访问权；生成的架构解释应与代码对照。

来源：[s-workflows：Common workflows · Understand new codebases；取回 Markdown第 24–24 行](https://code.claude.com/docs/en/common-workflows.md)。

### `claude-02` 实现跨文件功能并运行验证

按自然语言要求修改多个文件、执行工具，形成可运行功能改动。

**内置／核心能力 · 有来源支持。** 依赖模型、账户和工程环境，结果需测试和审查。

来源：[s-overview：Overview · Overview；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/overview.md)。

### `claude-03` 排查与修复程序错误

沿故障上下文调查、修改并验证修复，处理日常开发失败。

**内置／核心能力 · 有来源支持。** 测试和复现信息影响结果；不保证自动定位所有原因。

来源：[s-overview：Overview · Overview；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/overview.md)。

### `claude-04` 重构现有实现

在已有行为约束下调整代码组织和实现，配合现有验证检查回归。

**内置／核心能力 · 有来源支持。** 需明确兼容要求与测试；重构结果不自动保持全部语义。

来源：[s-workflows：Common workflows · Refactor code；取回 Markdown第 138–138 行](https://code.claude.com/docs/en/common-workflows.md)。

### `claude-05` 编写与维护项目测试

围绕目标行为创建或改进测试，并执行验证。

**内置／核心能力 · 有来源支持。** 需要可执行测试环境与可靠断言。

来源：[s-workflows：Common workflows · Work with tests；取回 Markdown第 178–178 行](https://code.claude.com/docs/en/common-workflows.md)。

### `claude-06` 准备和更新项目文档

读取现有代码与文档，形成说明、注释或维护文档的改动。

**内置／核心能力 · 有来源支持。** 需要核对运行行为，避免把生成说明当作权威。

来源：[s-workflows：Common workflows · Handle documentation；取回 Markdown第 240–240 行](https://code.claude.com/docs/en/common-workflows.md)。

<a id="verification"></a>
## 审查变更与浏览器验证

### `claude-07` 审查 GitHub PR 并定位反馈

使用 Code Review 对变更及周边代码审查，验证发现并以内联评论返回。

**扩展／具名实现路线 · 有来源支持。** 独立托管审查能力，官方标明 Team / Enterprise；具体授权及收费另核实。

来源：[s-review：Code Review · Code Review；取回 Markdown第 11–11 行](https://code.claude.com/docs/en/code-review.md)。

### `claude-08` 通过仓库自动化处理 Issue 和 PR

配置 GitHub Actions，让事件或 @claude 指令触发分析、修改及 PR 工作流。

**扩展／具名实现路线 · 有来源支持。** 需要工作流、凭据与权限；这是 GitHub Action 集成，不等于托管 Code Review。

来源：[s-actions：Claude Code GitHub Actions · Claude Code GitHub Actions；取回 Markdown第 7–7 行](https://code.claude.com/docs/en/github-actions.md)。

### `claude-09` 用真实浏览器验证和调试网页

连接 Chrome 扩展后测试本地 Web 应用、查看控制台并检查交互。

**扩展／具名实现路线 · 有来源支持。** 需要受支持 Claude in Chrome 扩展、账户及可见浏览器；登录或 CAPTCHA 需人工处理。

来源：[s-browser：Use Claude Code with Chrome · Use Claude Code with Chrome；取回 Markdown第 7–7 行](https://code.claude.com/docs/en/chrome.md)。

### `claude-10` 自动填写表单并提取网页资料

在获准访问的浏览器页面执行表单流程或把页面数据提取到任务中。

**扩展／具名实现路线 · 有来源支持。** 与网页测试共享扩展依赖；需有对应网站访问权，动态网页未必兼容。

来源：[s-browser：Use Claude Code with Chrome · Use Claude Code with Chrome；取回 Markdown第 7–7 行](https://code.claude.com/docs/en/chrome.md)。

<a id="reuse"></a>
## 复用知识、流程与外部信息

### `claude-11` 将重复的专业流程做成可共享 Skill

以说明和资源定义多步骤工作，在相关任务中按需加载或显式调用。

**扩展／具名实现路线 · 有来源支持。** 需要自己编写或安装可信技能；自定义命令已并入 Skill，不视为另一类用户结果。

来源：[s-skills：Extend Claude with skills · Extend Claude with skills；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/skills.md)。

### `claude-13` 利用外部业务资料完成工程任务

通过 MCP 连接问题追踪、监控、数据库等系统，读取和执行已授权工具。

**扩展／具名实现路线 · 有来源支持。** 依赖独立服务器、认证和具体工具；外部写操作仍需符合授权。

来源：[s-mcp：Connect Claude Code to tools via MCP · Connect Claude Code to tools via MCP；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/mcp.md)。

### `claude-18` 跨会话复用团队规范和个人项目经验

以 CLAUDE.md / AGENTS.md 提供持续指导，并使用 auto memory 保留纠正与偏好。

**内置／核心能力 · 有来源支持。** 文件规范与自动记忆有不同加载范围；不是每次都准确回忆的保证。

来源：[s-memory：How Claude remembers your project · How Claude remembers your project；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/memory.md)。

### `claude-21` 将团队扩展打包分发

用 Plugin 组合 Skill、代理、Hook 和 MCP 等扩展供团队复用。

**扩展／具名实现路线 · 有来源支持。** 插件需要可信来源与各自依赖，安装不等于所有工具可用。

来源：[s-plugins：Plugins overview · Plugins overview；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/plugins.md)。

<a id="control"></a>
## 委托、接续和调整工作

### `claude-12` 把高噪声调查委托给专门子代理

让独立上下文中的专门助手调查或执行子任务，向主会话返回摘要。

**内置／核心能力 · 有来源支持。** 可单独设置工具及权限；请求计入共同用量，不能把上下文隔离当作系统沙箱。

来源：[s-subagents：Create custom subagents · Create custom subagents；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/sub-agents.md)。

### `claude-16` 撤回近期 AI 编辑并调整任务方向

利用检查点回退对话和受跟踪文件改动，再从先前状态继续。

**内置／核心能力 · 有来源支持。** 主要覆盖编辑工具修改；不回滚 shell 产生的全部外部副作用或数据库，不替代 Git 和备份。

来源：[s-checkpoints：Checkpointing · Checkpointing；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/checkpointing.md)。

### `claude-19` 从另一设备继续本机正在运行的任务

通过 Remote Control 在浏览器或手机查看和指导本机 Claude Code 会话。

**内置／核心能力 · 有来源支持。** 需要本机任务与连接持续可用，以及受支持账户；不是将文件和执行迁移到手机。

来源：[s-remote：Continue local sessions from any device with Remote Control · Continue local sessions from any device with Remote Control；取回 Markdown第 7–7 行](https://code.claude.com/docs/en/remote-control.md)。

<a id="automation"></a>
## 事件与批量自动化

### `claude-14` 在生命周期事件执行确定性项目检查

通过用户编写的 Hook 脚本做格式化、命令校验或项目规则检查。

**扩展／具名实现路线 · 有来源支持。** 命令 Hook 需脚本与运行权限；提示词或代理 Hook 的判断不能当作确定性规则。

来源：[s-hooks：Automate actions with hooks · Automate actions with hooks；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/hooks-guide.md)。

### `claude-15` 在需要输入时接收任务提醒

通过 Hook 向自选通知系统提示等待输入或任务完成。

**扩展／具名实现路线 · 有来源支持。** 通知集成由用户配置，并受运行环境限制。

来源：[s-hooks：Automate actions with hooks · Get notified when Claude needs input；取回 Markdown第 84–84 行](https://code.claude.com/docs/en/hooks-guide.md)。

### `claude-17` 把开发分析放入脚本或 CI 批处理

通过非交互 CLI 处理输入并返回结构化结果，或用 Python / TypeScript Agent SDK 构建集成。

**扩展／具名实现路线 · 有来源支持。** SDK 包和 CLI 是不同接入方式；需要认证、权限、失败处理和内容核验。

来源：[s-headless：Run Claude Code programmatically · Run Claude Code programmatically；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/headless.md)。

### `claude-20` 在当前会话中定期跟进长任务

安排循环提示或一次性提醒，检查构建、PR 或部署状态。

**内置／核心能力 · 有来源支持。** /loop 依赖打开会话和本机在线；持久桌面任务及云 Routines 是另外的运行方式，不能混同。

来源：[s-scheduled：Run prompts on a schedule · Run prompts on a schedule；取回 Markdown第 9–9 行](https://code.claude.com/docs/en/scheduled-tasks.md)。

## 资料覆盖与发现过程

从日常开发结果逐项发现，再检查浏览器和事件自动化完整示例、MCP 与 Skill 等扩展。
归一化：把单次读写、命令、会话恢复合并入用户任务；保留可撤回修改、跨设备接续和外部系统协作等独立结果。
补漏区分受管理 Code Review 与 GitHub Actions、session loop 与持久任务、命令 Hook 与模型判断 Hook；避免把集成和模型效果混成内置保证。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未登录安装客户端或实测各付费、托管和第三方连接能力。
- 当前公开资料未支持把检查点称为完整备份，也未支持把模型审查当作安全认证。
- 未穷尽企业托管、云 Routines、Channels 与每个平台的独占功能；这些路线的账户、组织和版本限制需专项验证。
- 完整任务示例以官方 common-workflows、Chrome 和 GitHub Action 配方为主；未把示例可行性升级为独立用户成功率统计。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
