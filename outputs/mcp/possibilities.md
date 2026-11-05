# Model Context Protocol (MCP) 可能性地图

范围：研究 MCP 协议与具体服务器生态支持的用户结果；协议参照实际取回的 2026-07-28 文档，单独标明 MCP Apps、Tasks、官方参考服务器和第三方应用。

资料截点：2026-11-05。本图有 18 项来源支持的结果，来自 15 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

core 仅表示协议定义的交互机制；它仍需宿主和服务器实现。extension 表示官方扩展、独立目录服务或具名服务器路线。所有外部读写、模型和服务权限都需分别配置。

## 地图导航

- [建立可复用的工具与资料连接](#g-connect)
- [让用户参与并控制跨服务任务](#g-participate)
- [处理本地资料、网页和记忆](#g-documents)
- [支持代码协作与浏览器操作](#g-engineering)
- [接入数据分析与数字创作](#g-specialized)

<a id="g-connect"></a>
## 建立可复用的工具与资料连接

### `p-connect` 让兼容 AI 应用连接同一套外部能力

为工具、数据和提示建立可被兼容客户端使用的统一连接入口，减少每个应用各做一份集成。

**内置／核心能力 · 有来源支持。** 宿主、客户端与服务器须兼容相应协议版本及能力；协议不会自动提供账号、业务实现或授权。

来源：[s-intro：What is the Model Context Protocol (MCP)? · What is the Model Context Protocol (MCP)?；取回 Markdown第 7–7 行](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro.md)。

### `p-context` 把文件、数据库结构或知识资料作为可读上下文提供

通过 Resources 让应用取回资料并决定怎样提供给模型，而不必把只读数据伪装成执行操作。

**内置／核心能力 · 有来源支持。** 需服务器暴露资源，宿主负责选择、读取和使用；是否联网、检索与引用取决于应用实现。

来源：[s-server：Understanding MCP servers · Core Server Features；取回 Markdown第 18–18 行](https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts.md)。

### `p-actions` 让模型调用外部系统来执行用户请求的动作

通过具备输入输出定义的 Tools 请求执行操作，并把执行结果回传给应用。

**内置／核心能力 · 有来源支持。** 具体动作由服务器实现；宿主需决定允许范围与审批，协议不保证工具调用正确或已经完成用户最终目标。

来源：[s-server：Understanding MCP servers · Core Server Features；取回 Markdown第 17–17 行](https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts.md)。

### `p-prompt-reuse` 在不同交互中复用服务器提供的任务提示

向用户暴露可选择的提示模板，把常用分析、摘要或写作任务和对应工具资源连接起来。

**内置／核心能力 · 有来源支持。** 需宿主支持 Prompts 并由用户选择；提示模板不替代真实数据接入或结果核查。

来源：[s-server：Understanding MCP servers · Core Server Features；取回 Markdown第 19–19 行](https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts.md)。

### `p-discover` 查找和发布可连接服务器的安装元数据

通过官方 Registry 发布或发现服务器描述、包位置和配置所需信息，为客户端连接做准备。

**扩展／具名实现路线 · 有来源支持。** Registry 当前 preview；它提供元数据，不代表安全审核、托管服务、维护承诺或自动授权安装。

来源：[s-registry：The MCP Registry · The MCP Registry；取回 Markdown第 17–17 行](https://modelcontextprotocol.io/registry/about.md)。

<a id="g-participate"></a>
## 让用户参与并控制跨服务任务

### `p-ask-user` 在任务执行过程中向用户补问结构化信息

由服务器请求所缺信息，让用户补充偏好、参数等内容以继续当前工作。

**内置／核心能力 · 有来源支持。** 使用 Elicitation；需宿主支持并正确展示请求，不应用普通表单收集密码等不合适的敏感数据。

来源：[s-client：Understanding MCP clients · Core Client Features；取回 Markdown第 17–17 行](https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts.md)。

### `p-account-auth` 让远端工具在用户授权身份下访问受限服务

通过 HTTP 传输层授权流程代表资源所有者发起请求，连接需要身份凭据的服务。

**内置／核心能力 · 有来源支持。** HTTP 授权为可选实现；需相应 OAuth 流程、scope、服务端校验和凭据管理。stdio 不沿用同一授权流程。

来源：[s-auth：Authorization · Purpose and Scope；取回 Markdown第 12–13 行](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization.md)。

### `p-interactive-ui` 在对话中查看和操作服务器返回的交互界面

让数据可视化、表单或仪表板出现在支持 MCP Apps 的宿主界面中，并与上下文和工具交互。

**扩展／具名实现路线 · 有来源支持。** MCP Apps 是扩展，需支持它的宿主和实现 UI 资源的服务器；CSP、iframe 与宿主权限约束依实现而定。

来源：[s-apps：MCP Apps · MCP Apps；取回 Markdown第 14–14 行](https://modelcontextprotocol.io/extensions/apps/overview.md)。

### `p-long-task` 跟踪长操作并在重新连接后取回结果

用持久任务句柄代替一直等待的调用，后续查询进度、提供所需输入或取回最终结果。

**扩展／具名实现路线 · 有来源支持。** MCP Tasks 扩展；客户端与服务器都须支持，任务持久性、保留期和取消语义依实现，不是普通 Tools 自动具备。

来源：[s-tasks：Tasks · Tasks；取回 Markdown第 17–17 行](https://modelcontextprotocol.io/extensions/tasks/overview.md)。

<a id="g-documents"></a>
## 处理本地资料、网页和记忆

### `p-files` 让助手在限定目录中整理和修改本地资料

通过文件服务器读取、搜索、创建或移动资料，把基于对话的文件任务连接到实际目录。

**扩展／具名实现路线 · 有来源支持。** 另运行 Filesystem 参考服务器并配置 allowed directories；只读模式与访问控制需显式设置，参考实现不是生产安全认证。

来源：[s-files：Filesystem MCP Server · Features；取回 Markdown第 9–9 行](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/filesystem/README.md#L9-L9)。

### `p-web-read` 把网页正文转成适合助手阅读的材料

从网页取得内容并转为 Markdown，必要时分块读取较长页面。

**扩展／具名实现路线 · 有来源支持。** 需 Fetch 参考服务器和网络；默认地址保护并非对所有 DNS、代理和内容风险的完整保证，不承诺绕过登录或付费墙。

来源：[s-fetch：Fetch MCP Server · Fetch MCP Server；取回 Markdown第 5–5 行](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/fetch/README.md#L5-L5)。

### `p-memory` 为助手保存可检索的实体关系记忆

通过 Memory 服务器把人物、事实和关系保存成可后续访问的知识图谱资料。

**扩展／具名实现路线 · 有来源支持。** 需另运行 Memory 参考服务器并配置数据文件；保存的记录仍需校正，协议不使模型参数自动学习或保证记忆正确。

来源：[s-memory：Knowledge Graph Memory Server · Knowledge Graph Memory Server；取回 Markdown第 3–3 行](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/memory/README.md#L3-L3)。

<a id="g-engineering"></a>
## 支持代码协作与浏览器操作

### `p-git` 通过助手检查 Git 历史和待提交改动

把仓库状态、差异和历史读取操作提供给模型，支持基于真实 Git 数据的代码讨论与操作。

**扩展／具名实现路线 · 有来源支持。** 需 Git 参考服务器、仓库路径和对应权限；当前 README 标为 early development，Python SDK 版本要求以该项目为准。

来源：[s-git：mcp-server-git: A git MCP server · Overview；取回 Markdown第 7–7 行](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/git/README.md#L7-L7)。

### `p-browser` 让助手通过网页结构完成浏览器交互

通过可访问性快照理解网页并操作页面，用于探索网站或完成需要浏览器的任务。

**扩展／具名实现路线 · 有来源支持。** 需 Microsoft Playwright MCP、浏览器和可用宿主；站点账号、授权与可自动化程度仍受具体环境限制。

来源：[s-browser：Microsoft Playwright MCP — 项目说明 · Playwright MCP；取回 Markdown第 3–3 行](https://github.com/microsoft/playwright-mcp/blob/50b004fb3d3ee17f9710f067ed1b6d59fd16e4a1/README.md#L3-L3)。

### `p-github-collaboration` 在对话中处理代码库、Issue 和 PR 工作

使用 GitHub 提供的 MCP Server 读取代码并创建、更新或管理协作对象。

**扩展／具名实现路线 · 有来源支持。** 需 GitHub MCP Server、账号令牌与相应仓库权限；具体工具由启用的 toolsets 和凭据 scope 决定。

来源：[s-github：GitHub MCP Server · GitHub MCP Server；取回 Markdown第 5–5 行](https://github.com/github/github-mcp-server/blob/99d6d6503a7b2a133e2f8a595d6d0ba24b4086d3/README.md#L5-L5)。

### `p-github-ci` 让助手查看构建失败并分析开发流水线

取得 GitHub Actions 运行和构建失败信息，用于解释流水线问题及推进工程处理。

**扩展／具名实现路线 · 有来源支持。** 需启用支持的 GitHub MCP toolsets 和仓库权限；读取日志不等于自动完成修复或部署。

来源：[s-github：GitHub MCP Server · Use Cases；取回 Markdown第 11–11 行](https://github.com/github/github-mcp-server/blob/99d6d6503a7b2a133e2f8a595d6d0ba24b4086d3/README.md#L11-L11)。

<a id="g-specialized"></a>
## 接入数据分析与数字创作

### `p-database` 让助手跨数据库查询业务数据

用 DBHub 的统一 MCP 接口连接数据库，为模型提供实际查询数据的途径。

**扩展／具名实现路线 · 有来源支持。** 需第三方 DBHub、数据库驱动与连接凭据；必须按部署限制读写权限、查询范围和敏感数据，不能由协议推定只读。

来源：[s-database：DBHub — database MCP server README · 页面概述；取回 Markdown第 47–47 行](https://github.com/bytebase/dbhub/blob/280c0ed734864e45515b38a5daa273c5372592d4/README.md#L47-L47)。

### `p-3d` 通过对话驱动 Blender 中的场景创作

让助手借助 BlenderMCP 连接 Blender，创建或修改 3D 场景内容。

**扩展／具名实现路线 · 有来源支持。** 第三方 BlenderMCP 插件和服务器、兼容 Blender 及宿主；外部资产或生成服务另有账号、费用和许可条件。

来源：[s-blender：MCP for Blender — project README · 页面概述；取回 Markdown第 10–10 行](https://github.com/ahujasid/mcp-for-blender/blob/2e4b0bc294694b1570d76ed01be657c22e6d02a0/README.md#L10-L10)。

## 资料覆盖与发现过程

结果视角先提取连接、资料上下文、外部动作、提示复用、补问信息和授权结果；未把每个 JSON-RPC 方法名列成 P。
示例视角实际读取文件、Git、网页 Fetch、Playwright、GitHub、Memory、DBHub 与 BlenderMCP 的项目说明，将具体业务能力归给服务器而非协议本身。
扩展视角补读官方 Registry、MCP Apps 与 Tasks，并记录版本迁移及废弃特性。
去重时合并同一文件服务器的小操作，把同一客户端的安装方式和传输参数写成条件；保留交互 UI、长任务接续、数据库和 3D 创作等不同结果。
对协议、扩展和代表项目交叉复查后，新增资料主要变为更多同类服务器；本轮停止在可举证的代表结果，并保留兼容、授权与生态长尾缺口。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 没有逐一安装服务器或实测各宿主兼容矩阵；协商成功不表示所有工具、UI、授权或任务扩展都支持。
- 2026-07-28 文档把 Roots 和 Sampling 标为 deprecated；本图没有把旧教程中的这两项当作当前所有客户端的基础能力。
- 官方服务器仓库明确称参考实现不等于生产就绪。部分旧示例已归档，目录收录不证明持续维护或安全性。
- 未把自动绕过权限、可信网页内容、绝对安全、跨服务事务一致性或任意服务即插即用列为已确认能力。
- 除所列代表实现外，行业服务器、私有部署与全部 SDK 的覆盖仍不充分；工具权限与数据治理必须按真实服务验证。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
