# Model Context Protocol (MCP) 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-connect`｜结果视角｜让兼容 AI 应用连接同一套外部能力｜s-intro
2. `p-context`｜结果视角｜把文件、数据库结构或知识资料作为可读上下文提供｜s-server
3. `p-actions`｜结果视角｜让模型调用外部系统来执行用户请求的动作｜s-server
4. `p-prompt-reuse`｜结果视角｜在不同交互中复用服务器提供的任务提示｜s-server
5. `p-ask-user`｜结果视角｜在任务执行过程中向用户补问结构化信息｜s-client
6. `p-account-auth`｜结果视角｜让远端工具在用户授权身份下访问受限服务｜s-auth
7. `p-discover`｜扩展视角｜查找和发布可连接服务器的安装元数据｜s-registry
8. `p-interactive-ui`｜扩展视角｜在对话中查看和操作服务器返回的交互界面｜s-apps
9. `p-long-task`｜扩展视角｜跟踪长操作并在重新连接后取回结果｜s-tasks
10. `p-files`｜示例视角｜让助手在限定目录中整理和修改本地资料｜s-files
11. `p-git`｜示例视角｜通过助手检查 Git 历史和待提交改动｜s-git
12. `p-web-read`｜示例视角｜把网页正文转成适合助手阅读的材料｜s-fetch
13. `p-browser`｜示例视角｜让助手通过网页结构完成浏览器交互｜s-browser
14. `p-github-collaboration`｜示例视角｜在对话中处理代码库、Issue 和 PR 工作｜s-github
15. `p-github-ci`｜示例视角｜让助手查看构建失败并分析开发流水线｜s-github
16. `p-memory`｜示例视角｜为助手保存可检索的实体关系记忆｜s-memory
17. `p-database`｜示例视角｜让助手跨数据库查询业务数据｜s-database
18. `p-3d`｜示例视角｜通过对话驱动 Blender 中的场景创作｜s-blender

## 归一化、补漏与停止依据

结果视角先提取连接、资料上下文、外部动作、提示复用、补问信息和授权结果；未把每个 JSON-RPC 方法名列成 P。
示例视角实际读取文件、Git、网页 Fetch、Playwright、GitHub、Memory、DBHub 与 BlenderMCP 的项目说明，将具体业务能力归给服务器而非协议本身。
扩展视角补读官方 Registry、MCP Apps 与 Tasks，并记录版本迁移及废弃特性。
去重时合并同一文件服务器的小操作，把同一客户端的安装方式和传输参数写成条件；保留交互 UI、长任务接续、数据库和 3D 创作等不同结果。
对协议、扩展和代表项目交叉复查后，新增资料主要变为更多同类服务器；本轮停止在可举证的代表结果，并保留兼容、授权与生态长尾缺口。

## 保留的未知项

- 没有逐一安装服务器或实测各宿主兼容矩阵；协商成功不表示所有工具、UI、授权或任务扩展都支持。
- 2026-07-28 文档把 Roots 和 Sampling 标为 deprecated；本图没有把旧教程中的这两项当作当前所有客户端的基础能力。
- 官方服务器仓库明确称参考实现不等于生产就绪。部分旧示例已归档，目录收录不证明持续维护或安全性。
- 未把自动绕过权限、可信网页内容、绝对安全、跨服务事务一致性或任意服务即插即用列为已确认能力。
- 除所列代表实现外，行业服务器、私有部署与全部 SDK 的覆盖仍不充分；工具权限与数据治理必须按真实服务验证。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-apps](https://modelcontextprotocol.io/extensions/apps/overview.md) | 2026-11-05T08:43:25.133398+00:00 | 是 |
| [s-auth](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization.md) | 2026-11-05T08:43:25.273080+00:00 | 是 |
| [s-blender](https://github.com/ahujasid/mcp-for-blender/blob/2e4b0bc294694b1570d76ed01be657c22e6d02a0/README.md) | 2026-11-05T08:50:00.253814+00:00 | 是 |
| [s-browser](https://github.com/microsoft/playwright-mcp/blob/50b004fb3d3ee17f9710f067ed1b6d59fd16e4a1/README.md) | 2026-11-05T08:47:25.042238+00:00 | 是 |
| [s-client](https://modelcontextprotocol.io/docs/2026-07-28/learn/client-concepts.md) | 2026-11-05T08:43:25.142981+00:00 | 是 |
| [s-database](https://github.com/bytebase/dbhub/blob/280c0ed734864e45515b38a5daa273c5372592d4/README.md) | 2026-11-05T08:49:59.836396+00:00 | 是 |
| [s-fetch](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/fetch/README.md) | 2026-11-05T08:47:25.011410+00:00 | 是 |
| [s-files](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/filesystem/README.md) | 2026-11-05T08:47:25.816836+00:00 | 是 |
| [s-git](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/git/README.md) | 2026-11-05T08:47:25.048636+00:00 | 是 |
| [s-github](https://github.com/github/github-mcp-server/blob/99d6d6503a7b2a133e2f8a595d6d0ba24b4086d3/README.md) | 2026-11-05T08:43:27.011051+00:00 | 是 |
| [s-intro](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro.md) | 2026-11-05T08:43:25.163033+00:00 | 是 |
| [s-memory](https://github.com/modelcontextprotocol/servers/blob/36380287ed3b15d115b55f546617d723072b1296/src/memory/README.md) | 2026-11-05T08:49:59.067761+00:00 | 是 |
| [s-registry](https://modelcontextprotocol.io/registry/about.md) | 2026-11-05T08:43:26.618025+00:00 | 是 |
| [s-security](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices.md) | 2026-11-05T08:43:30.885095+00:00 | 否 |
| [s-server](https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts.md) | 2026-11-05T08:43:25.317436+00:00 | 是 |
| [s-servers](https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md) | 2026-11-05T08:43:26.611788+00:00 | 否 |
| [s-tasks](https://modelcontextprotocol.io/extensions/tasks/overview.md) | 2026-11-05T08:43:29.801415+00:00 | 是 |
| [s-transports](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports.md) | 2026-11-05T08:43:25.152287+00:00 | 否 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：无额外措辞修订。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
