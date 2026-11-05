# OpenCode 可能性地图

范围：以当前 OpenCode 2 官方文档为主；V1 文档仅用于对照迁移，不把旧 SDK、插件或 GitHub 示例视为 V2 自动兼容的确认能力。

资料截点：2026-11-05。本图有 19 项来源支持的结果，来自 16 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

OpenCode 是需要模型和工具的开源编码代理；免费开源客户端不代表推理、搜索或外部服务免费。当前 V2 的配置、权限、快照和插件边界须按版本核验。

## 地图导航

- [理解和交付工程任务](#engineering)
- [结合资料与外部系统工作](#information)
- [复用规范和团队流程](#reuse)
- [控制和接续任务](#continuity)
- [使用合适的模型生产结果](#inference)

<a id="engineering"></a>
## 理解和交付工程任务

### `oc-01` 解释代码而保持文件不变

使用具有只读约束的专用代理调查并解释代码，形成理解结果。

**内置／核心能力 · 有来源支持。** 需要相应代理与权限配置；不能把提示词中的只读要求代替实际工具权限。

来源：[s-v2-agents：Agents · 页面正文；本次 HTML 提取正文第 31–31 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/agents/)。

### `oc-02` 完成指定代码修改并执行现有测试

从问题定位、修改到运行相关验证，交付可检查的工程变更。

**内置／核心能力 · 有来源支持。** 需要可用模型、工具和工程依赖；官方超时配置任务示例支持流程，不保证任意任务成功。

来源：[s-v2-tools：Tools · 页面正文；本次 HTML 提取正文第 4–4 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/tools/)。

### `oc-03` 审查改动并按严重程度定位问题

让专门 reviewer 检查正确性与回归，返回带文件和行号的问题。

**内置／核心能力 · 有来源支持。** 代理定义和权限需自行配置；审查发现仍需核实。

来源：[s-v2-agents：Agents · 页面正文；本次 HTML 提取正文第 16–16 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/agents/)。

### `oc-04` 生成或维护仓库说明文档

根据任务编写 Markdown 等文本交付物，并与项目内容对照。

**内置／核心能力 · 有来源支持。** 需要提供准确上下文和人工核验，不保证说明与运行行为天然一致。

来源：[s-v2-tools：Tools · 页面正文；本次 HTML 提取正文第 45–45 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/tools/)。

### `oc-16` 在编辑后自动统一代码格式

接入项目可用格式化器，让工具修改后的文件遵循已有格式规范。

**扩展／具名实现路线 · 有来源支持。** 默认关闭；需启用并安装对应命令或项目依赖，不替代类型检查和语义测试。

来源：[s-v2-format：Formatters · Formatters；本次 HTML 提取正文第 2–3 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/formatters/)。

<a id="information"></a>
## 结合资料与外部系统工作

### `oc-05` 结合截图或附件理解任务材料

把受支持图片、PDF 或文本交给可接收相应输入的模型，辅助解释资料或实现修改。

**内置／核心能力 · 有来源支持。** 格式、数量和体积受客户端及模型限制；HTTP 附件 URL 当前不支持，不能假定所有模型都能看图。

来源：[s-v2-attachments：Attachments · 页面正文；本次 HTML 提取正文第 9–9 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/attachments/)。

### `oc-06` 检索最新资料并给出带来源的答复

连接搜索提供方，搜索当前信息、读取结果并返回来源链接。

**扩展／具名实现路线 · 有来源支持。** 需要配置搜索服务和可能的凭据；搜索结果并不自动成为可靠事实。

来源：[s-v2-websearch：Web search · Web search；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/websearch/)。

### `oc-07` 在开发任务中引用其他仓库和共享文档

为当前项目附加命名的本地目录或远程 Git 引用，读取设计系统、公共库和文档。

**内置／核心能力 · 有来源支持。** 需要路径或 Git 访问权限；授权范围与当前目录限制需自行检查。

来源：[s-v2-refs：References · 页面正文；本次 HTML 提取正文第 17–18 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/references/)。

### `oc-11` 连接外部工具和资料系统完成任务

使用本地或远程 MCP 服务提供的工具、资料和提示资源参与任务。

**扩展／具名实现路线 · 有来源支持。** 需服务器、认证、权限和上下文预算；V2 配置位于 mcp.servers，不能直接假定旧扩展无需迁移。

来源：[s-v2-mcp：MCP servers · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/mcp-servers/)。

<a id="reuse"></a>
## 复用规范和团队流程

### `oc-08` 在后续任务中持续使用团队规范

把构建、架构、风格和验证要求写入 AGENTS.md，供项目任务读取。

**内置／核心能力 · 有来源支持。** V2 识别 AGENTS.md；不同目录指导会合并，冲突并不自动解决。

来源：[s-v2-instructions：OpenCode 2 · Instructions · Instructions；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/instructions/)。

### `oc-09` 复用有资源支持的专业工作流程

建立按需加载的 Skill，把说明、脚本和参考资料一起提供给任务。

**扩展／具名实现路线 · 有来源支持。** 技能需要可信来源与实际工具依赖；官方 Git release 示例仅为可配置工作流。

来源：[s-v2-skills：Skills · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/skills/)。

### `oc-10` 把常用审查要求变成团队快捷工作流

通过命令模板参数化重复提示，指定代理或模型执行相同检查流程。

**扩展／具名实现路线 · 有来源支持。** 需要自行定义模板；它复用要求，不等于确定性审查程序。

来源：[s-v2-commands：Commands · 页面正文；本次 HTML 提取正文第 4–4 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/commands/)。

### `oc-18` 制作适合团队的工具与界面扩展

以插件加入工具、Hook、命令、代理或桌面面板，整合团队工作方式。

**扩展／具名实现路线 · 有来源支持。** 需要开发插件并核对 API；V1 插件实现不能直接在 V2 运行，GUI 插件为实验接口。

来源：[s-v2-plugins：Plugins · 页面正文；本次 HTML 提取正文第 104–104 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/plugins/)。

<a id="continuity"></a>
## 控制和接续任务

### `oc-13` 把长任务推进到原上下文窗口之外

利用会话压缩摘要和保留的近期内容继续任务。

**内置／核心能力 · 有来源支持。** 压缩有损；长期准确性仍依赖文件化状态、上下文预算和检查点。

来源：[s-v2-compaction：Compaction · Compaction；本次 HTML 提取正文第 2–3 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/compaction/)。

### `oc-14` 撤回近期对话及受跟踪文件修改

用快照回退最近 AI 工作，再修改提示并重新推进。

**内置／核心能力 · 有来源支持。** 文件快照需 Git，捕获为 best effort，局限活动目录和大小／忽略规则；不回滚数据库、进程或 Git 元数据。

来源：[s-v2-snapshots：OpenCode 2 · Snapshots · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/snapshots/)。

### `oc-15` 控制代理访问和修改的范围

按动作与资源设置允许、拒绝或询问，减少未经预先授权的工具执行。

**内置／核心能力 · 有来源支持。** 最后匹配规则生效；未匹配会询问，V2 外部目录默认允许。宿主 shell 本身拥有用户权限，不是强沙箱保证。

来源：[s-v2-permissions：Permissions · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/permissions/)。

### `oc-19` 在浏览器接续本机 OpenCode 界面

用配对连接进入已有服务的 Web 界面，在另一界面指导任务。

**内置／核心能力 · 有来源支持。** 需要当前服务可访问且一次性配对链接有效；并不意味着浏览器能脱离宿主运行仓库。

来源：[s-v2：Intro · Web；本次 HTML 提取正文第 31–31 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/)。

<a id="inference"></a>
## 使用合适的模型生产结果

### `oc-12` 按任务选择可访问的模型与推理服务

为项目或单次任务连接不同提供方，也可使用自定义兼容端点完成编码。

**扩展／具名实现路线 · 有来源支持。** 需要模型和运行包确实兼容；不保证任何 OpenAI-compatible 端点支持全部工具和媒体能力。

来源：[s-v2-providers：OpenCode 2 · Providers · 页面正文；本次 HTML 提取正文第 66–66 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/providers/)。

### `oc-17` 制作任务需要的图像资产

在有图像模型的提供方上从提示生成或修改图片，返回可用文件。

**扩展／具名实现路线 · 有来源支持。** experimental_image_generate 是实验能力，需支持图像生成的连接与权限；不保证未来接口稳定或可商用许可。

来源：[s-v2-tools：Tools · 页面正文；本次 HTML 提取正文第 95–95 行（不是 HTML 源码行号）](https://opencode.ai/v2/docs/tools/)。

## 资料覆盖与发现过程

先遍历任务、代理、媒体与外部资料的结果，再沿 V2 导航补查命令、压缩、格式化和快照。
归一化：把 grep/read/edit/shell 合并为可验证工程修改；模型选择与接入合并为可选推理路线，不罗列每个供应商。
补漏发现 V1 与 V2 并存、插件及 server API 有破坏性变更、外部目录默认行为不同，均保留来源和未知边界。
引用当前迁移说明核实兼容范围；未据搜索到的旧版示例保证新版本行为。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未安装 OpenCode 2 或运行提供方、插件、MCP 与图像模型。
- V1 GitHub 自动化和 SDK 文档有示例，但 V2 server/client 契约已改变；本轮未确认完整 V2 接入路线，不列为通用已确认结果。
- 未验证桌面平台、第三方提供方账户和所有遗留字段的实际迁移行为；官方兼容意图不等于运行证书。
- 工作示例主要来自官方工具任务、只读 reviewer 和 release Skill，尚缺独立用户的可重复端到端评测。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
