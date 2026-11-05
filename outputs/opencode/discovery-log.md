# OpenCode 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `oc-01`｜结果视角｜解释代码而保持文件不变｜s-v2-agents
2. `oc-02`｜完整示例视角｜完成指定代码修改并执行现有测试｜s-v2-tools
3. `oc-03`｜结果视角｜审查改动并按严重程度定位问题｜s-v2-agents
4. `oc-04`｜结果视角｜生成或维护仓库说明文档｜s-v2-tools
5. `oc-05`｜结果视角｜结合截图或附件理解任务材料｜s-v2-attachments
6. `oc-06`｜结果视角｜检索最新资料并给出带来源的答复｜s-v2-websearch
7. `oc-07`｜结果视角｜在开发任务中引用其他仓库和共享文档｜s-v2-refs
8. `oc-08`｜结果视角｜在后续任务中持续使用团队规范｜s-v2-instructions
9. `oc-09`｜扩展视角｜复用有资源支持的专业工作流程｜s-v2-skills
10. `oc-10`｜结果视角｜把常用审查要求变成团队快捷工作流｜s-v2-commands
11. `oc-11`｜结果视角｜连接外部工具和资料系统完成任务｜s-v2-mcp
12. `oc-12`｜结果视角｜按任务选择可访问的模型与推理服务｜s-v2-providers
13. `oc-13`｜结果视角｜把长任务推进到原上下文窗口之外｜s-v2-compaction
14. `oc-14`｜结果视角｜撤回近期对话及受跟踪文件修改｜s-v2-snapshots
15. `oc-15`｜结果视角｜控制代理访问和修改的范围｜s-v2-permissions
16. `oc-16`｜结果视角｜在编辑后自动统一代码格式｜s-v2-format
17. `oc-17`｜结果视角｜制作任务需要的图像资产｜s-v2-tools
18. `oc-18`｜结果视角｜制作适合团队的工具与界面扩展｜s-v2-plugins
19. `oc-19`｜结果视角｜在浏览器接续本机 OpenCode 界面｜s-v2

## 归一化、补漏与停止依据

先遍历任务、代理、媒体与外部资料的结果，再沿 V2 导航补查命令、压缩、格式化和快照。
归一化：把 grep/read/edit/shell 合并为可验证工程修改；模型选择与接入合并为可选推理路线，不罗列每个供应商。
补漏发现 V1 与 V2 并存、插件及 server API 有破坏性变更、外部目录默认行为不同，均保留来源和未知边界。
引用当前迁移说明核实兼容范围；未据搜索到的旧版示例保证新版本行为。

## 保留的未知项

- 未安装 OpenCode 2 或运行提供方、插件、MCP 与图像模型。
- V1 GitHub 自动化和 SDK 文档有示例，但 V2 server/client 契约已改变；本轮未确认完整 V2 接入路线，不列为通用已确认结果。
- 未验证桌面平台、第三方提供方账户和所有遗留字段的实际迁移行为；官方兼容意图不等于运行证书。
- 工作示例主要来自官方工具任务、只读 reviewer 和 release Skill，尚缺独立用户的可重复端到端评测。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-agents](https://opencode.ai/docs/agents/) | 2026-11-05T08:56:29.105713+00:00 | 否 |
| [s-github](https://opencode.ai/docs/github/) | 2026-11-05T08:56:30.732676+00:00 | 否 |
| [s-mcp](https://opencode.ai/docs/mcp-servers/) | 2026-11-05T08:56:29.780946+00:00 | 否 |
| [s-overview](https://opencode.ai/docs/) | 2026-11-05T08:56:28.818175+00:00 | 否 |
| [s-permissions](https://opencode.ai/docs/permissions/) | 2026-11-05T08:56:30.914668+00:00 | 否 |
| [s-plugins](https://opencode.ai/docs/plugins/) | 2026-11-05T08:56:31.749716+00:00 | 否 |
| [s-providers](https://opencode.ai/docs/providers/) | 2026-11-05T08:56:29.722356+00:00 | 否 |
| [s-sdk](https://opencode.ai/docs/sdk/) | 2026-11-05T08:56:31.253009+00:00 | 否 |
| [s-skills](https://opencode.ai/docs/skills/) | 2026-11-05T08:56:30.211144+00:00 | 否 |
| [s-tools](https://opencode.ai/docs/tools/) | 2026-11-05T08:56:29.458665+00:00 | 否 |
| [s-v2-agents](https://opencode.ai/v2/docs/agents/) | 2026-11-05T09:06:11.112158+00:00 | 是 |
| [s-v2-attachments](https://opencode.ai/v2/docs/attachments/) | 2026-11-05T09:35:56.307188+00:00 | 是 |
| [s-v2-commands](https://opencode.ai/v2/docs/commands/) | 2026-11-05T09:35:56.807058+00:00 | 是 |
| [s-v2-compaction](https://opencode.ai/v2/docs/compaction/) | 2026-11-05T09:35:58.028393+00:00 | 是 |
| [s-v2-format](https://opencode.ai/v2/docs/formatters/) | 2026-11-05T09:35:58.003842+00:00 | 是 |
| [s-v2-instructions](https://opencode.ai/v2/docs/instructions/) | 2026-11-05T09:35:56.889213+00:00 | 是 |
| [s-v2-mcp](https://opencode.ai/v2/docs/mcp-servers/) | 2026-11-05T09:06:12.677679+00:00 | 是 |
| [s-v2-migration](https://opencode.ai/v2/docs/migrate-v1/) | 2026-11-05T09:35:57.136185+00:00 | 否 |
| [s-v2-models](https://opencode.ai/v2/docs/models/) | 2026-11-05T09:32:29.155321+00:00 | 否 |
| [s-v2-permissions](https://opencode.ai/v2/docs/permissions/) | 2026-11-05T09:06:11.174974+00:00 | 是 |
| [s-v2-plugins](https://opencode.ai/v2/docs/plugins/) | 2026-11-05T09:32:28.999640+00:00 | 是 |
| [s-v2-providers](https://opencode.ai/v2/docs/providers/) | 2026-11-05T09:32:30.392762+00:00 | 是 |
| [s-v2-refs](https://opencode.ai/v2/docs/references/) | 2026-11-05T09:35:56.403114+00:00 | 是 |
| [s-v2-skills](https://opencode.ai/v2/docs/skills/) | 2026-11-05T09:06:11.119305+00:00 | 是 |
| [s-v2-snapshots](https://opencode.ai/v2/docs/snapshots/) | 2026-11-05T09:06:12.444033+00:00 | 是 |
| [s-v2-tools](https://opencode.ai/v2/docs/tools/) | 2026-11-05T09:32:29.944996+00:00 | 是 |
| [s-v2-websearch](https://opencode.ai/v2/docs/websearch/) | 2026-11-05T09:35:56.715523+00:00 | 是 |
| [s-v2](https://opencode.ai/v2/docs/) | 2026-11-05T09:06:10.980025+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`oc-06`、`oc-08`、`oc-13`、`oc-16`、`oc-19`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
