# n8n 可能性地图

范围：个人与小团队使用 n8n 跨应用自动化、整理数据、通知协作和交付业务流程；以本次取回的 n8n 官方文档及模板案例为准。核心节点与依赖外部应用/模型的扩展路线分别标示；不是安装/运行认证。

## 按用户结果浏览

### 周期报告与复盘

- **定时生成简报并累积可查记录**（核心）——按固定时间拉取数据、整理成易读短报并追加保存，形成随时间增长的运行日志。 条件：官方入门示例使用每日天气 API 和 n8n Data Table；示例数据来自教程用 Mockingbird。接入真实数据需相应 API/账户凭据。 来源：[Build your first workflow | n8n Docs](https://docs.n8n.io/build-your-first-workflow)。

### 接入与触发

- **让外部事件启动工作流**（核心）——接收外部应用或服务发来的事件数据，并据此启动后续自动化；适合没有专用触发节点的服务。 条件：使用内置 Webhook；需将外部系统配置为调用该端点，并按部署方式提供可达的 HTTPS 地址。 来源：[Webhook | Nodes | n8n Docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook)。

### 跨系统数据

- **在工作流之间保存和复用结构化数据**（核心）——将结构化记录存放在 n8n 内部数据表，并在多个工作流中读取或维护。 条件：使用内置 Data Table。此条只确认内部表格和跨工作流使用；不据此推断它适合队列、查重或特定负载。应按官方数据表容量限制判断是否适用。 来源：[Data Table | Nodes | n8n Docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.datatable)。
- **把表格数据同步到数据库并用自然语言查询**（扩展）——作者模板展示将 Google Sheets/CSV 结构导入 PostgreSQL，再把自然语言财务问题转为 SQL 并返回数值结果；可选定期同步。 条件：需要 PostgreSQL 实例、Google Drive/Sheets 访问及模板所需模型连接；自然语言转 SQL 由外部模型执行。同步频率是可选的 Schedule Trigger 设置。模板页面未证明查询准确率或实际运行结果。 来源：[Query Google Sheets/CSV data through an AI agent using PostgreSQL | n8n workflow template](https://n8n.io/workflows/3079-query-google-sheetscsv-data-through-an-ai-agent-using-postgresql/)。

### 业务交付与协作

- **自动回复网站询盘并通知团队**（扩展）——作者模板展示网站线索经 Webhook 进入后自动回信并通知团队；流程还校验字段、去重并按优先级分流。 条件：此端到端模板组合 Webhook、Google Sheets、Gmail 与 Slack。节点由 n8n 提供，但结果依赖这些外部服务账户、OAuth 授权、表格字段和可用配额；模板页不是运行证明。 来源：[Capture and route real estate leads with Google Sheets, Gmail, and Slack | n8n workflow template](https://n8n.io/workflows/16740-capture-and-route-real-estate-leads-with-google-sheets-gmail-and-slack/)。
- **把支持邮件变成带时限的跟进任务**（扩展）——作者模板展示支持邮件分类、SLA 截止时间、日历跟进事件、工单记录、回复草稿和高优先级提醒。 条件：流程依赖 Gmail、Google Gemini、Calendar、Sheets 与 Discord 账户/授权和模型 API；模型分类与摘要是外部 Gemini 服务。模板说明不是运行或客户成效认证。 来源：[Triage support emails and schedule SLA tasks with Gmail, Gemini, Google Calendar, Sheets and Discord | n8n workflow template](https://n8n.io/workflows/19884-triage-support-emails-and-schedule-sla-tasks-with-gmail-gemini-google-calendar-sheets-and-discord/)。
- **把发票自动批准或转交人工审批**（扩展）——作者模板展示从 PDF 取数、校验和查重，到按条件自动批准或等待人工决定，再记录审批状态并通知相关人员。 条件：此案例依赖 OpenAI、Google Sheets、Gmail 与 Webhook 及各服务账户/凭据；抽取/分类是外部 OpenAI 服务。人工审批步骤由模板配置，结果未经运行验证。 来源：[Process, validate, and approve invoices with OpenAI GPT-4o and Google Sheets | n8n workflow template](https://n8n.io/workflows/19739-process-validate-and-approve-invoices-with-openai-gpt-4o-and-google-sheets/)。
- **把扫描 PDF 转成可编辑的整洁文档**（扩展）——作者模板展示通过公开表单收取 PDF，调用 OCR 提取并整理文本，再将结果写入 Google Docs。 条件：模板要求 Mistral Cloud OCR API key、Google Docs/Drive OAuth 凭据和目标文件夹 ID；页面说明的最大文件为 100 MB。OCR、云盘和文档能力来自外部服务。仅确认模板页面描述。 来源：[Turn any PDF into a clean Google Doc with Mistral OCR | n8n workflow template](https://n8n.io/workflows/6937-turn-any-pdf-into-a-clean-google-doc-with-mistral-ocr/)。

### 失败处理

- **在关联工作流失败时启动错误处理流程**（核心）——为工作流配置独立 Error Trigger；关联工作流自动失败时，错误流程会取得失败详情并运行，可在其中追加告警或记录步骤。 条件：使用 n8n 内置 Error Trigger。仅自动工作流发生错误时触发，手动执行失败不能用它测试；触发器节点自身失败时可用错误信息更少。通知渠道要另接相应服务。 来源：[Error Trigger | Nodes | n8n Docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger)。

### 部署与扩展

- **自托管自动化服务并选择许可版本**（核心）——在自有服务器、私有云或本地环境运行 n8n；无许可密钥时运行 Community edition，添加 Business 或 Enterprise 密钥可启用相应版本。 条件：需要自行负责部署、维护、升级和安全；商业版/企业版需要许可密钥。Cloud 与 self-host 的功能、价格和限额依当期方案。 来源：[Host n8n | Deploy | n8n Docs](https://docs.n8n.io/deploy/host-n8n)。

## 待验证方向

- CRM 多系统字段级双向同步：可能需要通用 API/HTTP Request 或第三方节点，但本轮没有取到足以证明端到端结果的案例。
- 自动监控个人网站/竞品页面并生成差异提醒：本轮未验证具体稳定工作流与服务条款边界。
- 社媒内容自动生成、排期和发布：未验证平台 API 权限、审批环节、账号计划与当前节点兼容性。

## 资料覆盖与缺口

来源覆盖官方入门、部署、核心节点文档，以及作者发布的线索、客服、发票、OCR 文档和 Sheets/CSV 到 PostgreSQL 查询模板。Gmail、Google Sheets、Slack、Calendar、OpenAI、Gemini、Mistral 与 PostgreSQL 是外部服务/账户；即使 n8n 有相应集成节点，完整结果仍依赖服务授权、计划及 API 可用性。

未安装或执行工作流，因此本图确认的是“资料有明确描述的可实现结果”，不是实际环境运行认证，也不保证模板导入即用。Cloud/self-host 的具体价格、限额和功能计划未作全面比价。

## 原研究保留的未解决问题

- 本轮未安装或实际运行 n8n；模板示例不构成对凭据、权限、错误处理或业务收益的实测保证。
- 未逐项测完所有官方节点、社区包、API 限额、云方案/许可价格和版本兼容矩阵；这些会随版本及供应商方案变化。
- 社区模板案例是作者发布的模板说明，不是已运行客户案例，不独立验证生产表现。
- 未纳入的作者自动重试模板使用 n8n API 登录并在 Set 节点配置实例 URL/用户名/密码；未核实当前版本的可用认证方式与安全配置，故不作为确认能力。
- 社区节点文档仅证明扩展机制及 Cloud 限制，不把“安装扩展”本身当作用户结果。
- 没有为缺乏充分原文支撑的 CRM 同步、自动社媒运营、网站监控抓取、个人知识库同步等方向做能力承诺。
