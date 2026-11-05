# Cloudflare Workers：个人开发者可完成的成果

范围：Workers 代码运行与应用发布。各条目标明所需 Cloudflare 组件、前端工具或第三方服务。资料于 2026-11-05 抓取；未安装或实测，运行效果和生产容量不作保证。

## 发布网站与服务

### 发布面向网络请求的 API

接收 HTTP 请求并返回 API 响应，可作为网站或其他服务的边缘后端。 **核心**。

条件与边界：Workers 运行时与部署工具 Wrangler；需 Cloudflare 账户。具体套餐、请求和 CPU 限额依当前计划而定。

来源：[Cloudflare Workers](https://developers.cloudflare.com/workers/)。

### 部署带 API 的 React 单页应用

将 React 前端静态资源与 Worker API 一起部署，让浏览器前端调用同一应用中的 API。 **扩展**。

条件与边界：React 与 Vite 属第三方前端工具；教程还需要 @cloudflare/vite-plugin、Wrangler 与 Cloudflare 账户。

来源：[Tutorial - React SPA with an API](https://developers.cloudflare.com/workers/vite-plugin/tutorial/index.md)。

## 保存和读取应用数据

### 发布带持久化清单的待办应用

提供待办事项清单，并把应用数据保存在 Workers KV。 **扩展**。

条件与边界：需要单独创建并绑定 Workers KV 命名空间；教程使用 HTML/CSS/JavaScript 与 Cloudflare 账户。KV 的一致性与容量特性应按官方限制评估。

来源：[Build a todo list Jamstack application](https://developers.cloudflare.com/workers/tutorials/build-a-jamstack-app/index.md)。

### 交付可查询 SQL 数据库的应用

通过 Worker 查询部署后的 D1 数据库，可向客户端提供 SQL 数据结果。 **扩展**。

条件与边界：D1 是 Cloudflare 托管的 SQLite 语义 SQL 数据库，需建库并添加绑定；官方教程要求 Cloudflare 账户、Node.js 与 Wrangler。限制/费用依计划和用量变化。

来源：[Get started with D1](https://developers.cloudflare.com/d1/get-started/)。

### 从 Worker 读写大型对象文件

用 Worker API 读、列出、写入和删除 R2 对象，可为应用提供文件或媒体存取后端。 **扩展**。

条件与边界：需要单独创建 R2 bucket 并绑定 Worker；公开访问、访问控制、CORS、对象容量与费用需另外配置。

来源：[Use R2 from Workers](https://developers.cloudflare.com/r2/api/workers/workers-api-usage/)。

## 连接外部服务

### 把网站联系表单写入 Airtable

接受联系表单字段并异步存入 Airtable 表格，供后续查看。 **扩展**。

条件与边界：Airtable 是独立第三方服务，需 Airtable API 访问与密钥；Workers 侧需部署与密钥配置。账户、配额和价格以 Airtable 为准。

来源：[Handle form submissions with Airtable](https://developers.cloudflare.com/workers/tutorials/handle-form-submissions-with-airtable/index.md)。

## 支持实时互动

### 提供多人实时聊天室

让参与者通过 WebSocket 进入聊天室并将消息广播给其他用户。 **扩展**。

条件与边界：依赖 Cloudflare Durable Objects 管理房间；需部署官方 demo 并登录 Wrangler/Cloudflare。该教程还保存聊天历史，但此条目聚焦多人消息广播；示例未证明生产容量或隐私/审核功能。

来源：[Deploy a real-time chat application](https://developers.cloudflare.com/workers/tutorials/deploy-a-realtime-chat-app/index.md)。

## 处理后台与长流程

### 将请求中的工作排入后台队列

把请求触发的工作从同步请求中卸载，并用队列缓冲或批量处理消息。 **扩展**。

条件与边界：需要创建 Cloudflare Queues 并为 Worker 配置 producer/consumer；实际投递、重试、吞吐与费用依配置和计划确认。

来源：[Cloudflare Queues](https://developers.cloudflare.com/queues/)。

### 运行可恢复的多步骤业务流程

把需要跨分钟、小时或数周运行的多步任务持久化，并在失败时重试。 **扩展**。

条件与边界：依赖 Cloudflare Workflows（独立平台组件）与 Worker；配额及按使用计费可能适用。适合长流程，不等于任意代码无限期运行。

来源：[Cloudflare Workflows](https://developers.cloudflare.com/workflows/)。

## 运行 AI 应用

### 在请求流程中调用托管机器学习模型

通过 Workers AI 在 Cloudflare 提供的 serverless GPU 上运行模型推理。 **扩展**。

条件与边界：Workers AI 为 Cloudflare 独立产品，可由 Worker 或 API 调用；模型目录、额度、推理价格和定制模型可用性以当前服务政策为准。

来源：[Workers AI](https://developers.cloudflare.com/workers-ai/)。

### 托管可持久保存状态的实时 AI Agent

在 Cloudflare 托管可持久保存状态或本地 SQL 数据、保持实时连接并执行定时工作的 AI Agent。 **扩展**。

条件与边界：依赖 Cloudflare Agents SDK（建立在 Durable Objects 等平台能力上）；模型供应商、工具接入（如搜索/MCP/支付）需另行选择和配置。

来源：[Build Agents on Cloudflare](https://developers.cloudflare.com/agents/index.md)。

## 资料覆盖与缺口

- 已覆盖核心部署、静态前端/API、KV 待办完整教程、D1 查询教程、R2/队列/工作流/实时聊天/AI 产品与 Agent 扩展；未逐个验证所有支持框架的版本兼容和生产行为。
- 国际化、多语言内容管理/CMS、PWA/离线、认证、支付、邮件、搜索、数据分析等未形成足以确认具体成果的案例；不得据概念文档外推。
- 套餐、地区可用性、请求/CPU/存储限制和第三方服务费用可能变更；本次没有运行部署。
