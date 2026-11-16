# FastAPI 发现记录

## 范围与前提

针对个人开发者把 Python 数据与业务能力做成可调用服务，研究官方入口所列 API、验证、文件、流式/实时服务、集成和部署。区分 FastAPI 本体、其 Starlette/Pydantic 基础、以及数据库、认证库、消息队列、文件存储、前端和托管产品。未确认当前 semver。

## 第一轮：未分类候选

先按结果记录：提供可试用的 API 文档；校验请求并整理响应；为私有 API 登录；连接 SQL 数据库；接受文件；传送大文件或逐步生成输出；通过 WebSocket 实时聊天/通知；响应后发邮件或处理；生成外部语言 API 客户端；运行后台管理 API/前端；把 API 部署给用户；另检验是否有 webhook 能力。暂不按框架模块或菜单分类。

## 第二轮：Outcome / 官方完整应用案例

官方功能页确认 OpenAPI 文档交互 UI，Swagger UI 可直接调用和测试端点；Pydantic 请求体和 response_model 可以校验/过滤形状；安全指南演示带 password hashing 的 JWT 流程。SQLModel 指南说明可用 SQLModel/SQLAlchemy 连各种数据库，同时明确 FastAPI 不强迫某一数据库。

读完官方 Full Stack FastAPI Template 固定提交 README：它把 FastAPI 作为 Python API、React 作为前端、PostgreSQL/SQLModel 作为存储、JWT 登录、管理页面和自动生成前端 client 放在同一项目，并列出 FastAPI Cloud 与 Docker Compose 自托管部署。把它归一成“从全栈模板启动管理后台”，没有把模板附属栈说成 FastAPI 原生能力，也没有把页面截图推断成未证明的完整业务 CRUD。SHA 来自 GitHub API 对仓库实际默认分支/master 的解析，README raw 正文来自该 40 位提交。首次直接问 commits/main 得到 422，未把 main 当真。

## 第三轮：扩展与遗漏检查

- Request Files 直接示例说明需要额外 `python-multipart`；UploadFile 是接收入口，不自动创建存储桶、病毒扫描或权限系统，因此 P 只写接收并由应用处理。
- WebSocket 教程展示可广播的聊天连接管理器；同文说明其内存列表仅在单进程有效，明确标出多实例需共享组件。
- BackgroundTasks 允许返回后做轻量工作；文档说明跨进程/服务器或较重作业应考虑 Redis/RabbitMQ 等队列和 Celery 等任务方案，避免把内存回调误当耐久任务队列。
- Custom Response 说明 StreamingResponse 对生成器逐步输出、FileResponse 异步传文件；将两个相关传输结果并成一项。直接 Response 会绕过部分自动转换/文档生成，这个实现边界列在条件中。
- Deployment 指南确认应用如何面向用户部署；FastAPI Cloud/主机/反向代理仍是外部交付依赖。
- 尝试官方 `advanced/webhooks/` 入口返回 404，故不以 webhook 做 P。已检查自动生成客户端线索，但生成器是外部工具、其用例未在本轮获得清楚产品案例，暂不单列。

## 归一化与分组

结果归成 10 项：交互式 API 说明；请求/响应数据合同；登录/访问保护；数据库 API；文件上传；实时 WebSocket；短后台工作；流/文件响应；远端部署；模板式完整后台。Pydantic 模型和过滤同属服务数据契约，没有按输入/输出拆碎；Stream/File response 合并为数据传输；WebSocket 和轻量任务有重要生产扩展边界。按最终目的分成连客户端、数据处理、访问控制、自动化、交付。

## 停止依据

结果轮次覆盖官方功能与主要指南；案例轮次读完固定提交的官方全栈模板 README；扩展轮次检查 SQLModel、python-multipart、PyJWT/pwdlib、队列、共享 WebSocket 广播、ASGI hosting。补漏后 candidate families 都已证据确认或明确降为外部需求。继续寻找更多数据库驱动/云平台只会替换集成选项，逐个列举会把 P 拆成包清单；因此停止。

## 未知项

未核对 FastAPI semver、完整模板文件行为、数据库迁移和 auth 安全配置；未本地安装、跑测试、上传大文件、模拟多进程 socket、执行任务队列或部署。API 调用可靠性、安全、性能和服务费需实际环境验证。官方 `advanced/webhooks/` 请求 404；它不支撑本结果集。

## 主 agent 来源复核

主 agent 已逐项阅读结果、条件和摘录的周边原文；按实际响应类型区分 Markdown、HTML 提取正文和源文本，并核对 GitHub 固定引用。类型标签累计修正 0 处；引文与原始缓存行号仍逐条匹配。这不授予 reviewed，不是独立人工审核或工具运行认证。

## 官方部署形态分类校准

fa-09 的官方常规运行/自托管方式归为 core，主机、运行时、账号、成本与运维条件保持明确；额外业务能力的第三方集成仍使用 extension。

## 交付后复查（2026-11-05）

逐项将 Markdown 的结果、条件、能力标签与证据链接和 JSON 对齐，保留原有用途分组、覆盖说明及发现过程。报告采用条目级证据 URL；固定提交不退回移动分支。新增批次校验会拒绝报告与 JSON 的结果、限制或标签不一致。

- s-sql 改用直接支持用户结果的原文，定位为本次捕获第 7 行；原始来源、时间与响应哈希保持不变。
- s-deployment 改用直接支持用户结果的原文，定位为本次捕获第 4 行；原始来源、时间与响应哈希保持不变。
