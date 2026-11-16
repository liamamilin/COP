# FastAPI 能交付什么

**范围：**面向个人开发者，聚焦 API 服务、验证、文件、流式/实时能力、集成和部署。FastAPI 核心与 ORM、身份实现、队列、存储、前端和主机等依赖分开说明。所查官方文档于 2026-11-05 取回；未核定当前 semver。需要 Python 基础，部署和生产使用仍须按运行环境配置。

## 连接客户端与服务

- **提供可交互探索的 API 文档**（核心）——让 API 使用者从浏览器查看接口说明并直接调用、测试端点。 条件：FastAPI 默认基于 OpenAPI 提供 Swagger UI 与 ReDoc；产品上线时应检查是否公开敏感 schema 或调试端点。 来源：[Features](https://fastapi.tiangolo.com/features/)。
- **提供 WebSocket 实时消息通道**（核心）——创建浏览器、移动客户端与 API 之间的双向消息通道，也可广播给已连接客户端。 条件：FastAPI 基于 Starlette 支持 WebSockets。官方简例将连接保存在单进程内存；多进程/多实例广播需 Redis、PostgreSQL 或其他共享消息组件。客户端与协议认证需另外配置。 来源：[WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)。
- **流式传送文件或生成内容**（核心）——以迭代器逐段响应客户端，或异步发送服务器上的文件，适合较大下载/逐步生成内容。 条件：StreamingResponse/FileResponse 提供响应机制；数据生成、文件访问控制、缓存、取消和客户端兼容需应用处理。直接返回 Response 时部分自动响应文档行为不适用。 来源：[Custom Response — HTML, Stream, File, others](https://fastapi.tiangolo.com/advanced/custom-response/)。
- **接收用户上传的文件**（扩展）——创建接收一个或多个 multipart 文件的 API 端点，后续可进行解析、校验或转存。 条件：需额外安装 `python-multipart`；存储、杀毒、文件类型/大小限制、权限及对象存储不是上传参数自动提供的能力。 来源：[Request Files](https://fastapi.tiangolo.com/tutorial/request-files/)。

## 验证与处理业务数据

- **验证请求数据并约束响应格式**（核心）——接收由 Pydantic 模型描述的请求数据，并按声明类型校验、转换和过滤 API 响应。 条件：FastAPI 依赖 Pydantic；复杂业务规则、数据库一致性和授权仍由应用处理。响应模型过滤不等于完整的数据泄露审计。 来源：[Request Body](https://fastapi.tiangolo.com/tutorial/body/)、[Response Model — Return Type](https://fastapi.tiangolo.com/tutorial/response-model/)。
- **交付连接关系型数据库的 API**（扩展）——通过 SQLModel/SQLAlchemy 把 API 操作连接到 SQLite、PostgreSQL 等关系型数据库。 条件：FastAPI 不自带数据库或 ORM；示例需额外 SQLModel，PostgreSQL 还需要数据库实例、驱动、凭证、迁移和备份。可选其他 SQL/NoSQL 库。 来源：[SQL (Relational) Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)。

## 控制访问与自动化

- **为 API 加入 Bearer/JWT 身份验证**（扩展）——为 API 实现用户名密码登录流程，并用带哈希的凭证和 JWT Bearer 令牌保护请求。 条件：FastAPI 提供 OAuth2/依赖项工具；官方示例安装并使用 `pwdlib[argon2]`、`PyJWT` 等组件，用户表、密钥轮换、撤销、账号恢复和威胁建模需自行设计。不是托管身份服务。 来源：[OAuth2 with Password, hashing, Bearer JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)。
- **在响应后执行轻量后台任务**（核心）——先返回 HTTP 响应，再执行短时通知或文件处理工作。 条件：FastAPI/Starlette 的进程内 BackgroundTasks 适用于简单、短任务。官方建议重型/跨进程工作使用 Celery 等任务系统和 RabbitMQ/Redis 等队列；该类属于扩展。 来源：[Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)。

## 上线与交付

- **部署可供真实用户调用的 API**（核心）——将 FastAPI 服务放到自管机器或云部署平台，使远程用户可访问。 条件：需要 ASGI 运行时/服务器、进程管理、HTTPS、环境变量、日志/监控和部署主机；FastAPI Cloud 与自托管 Docker 是不同路线。主机账户、额度和费用依平台而定，本轮未核价。 来源：[Deployment](https://fastapi.tiangolo.com/deployment/)。
- **从全栈模板启动管理后台应用**（扩展）——以官方 Full Stack FastAPI Template 为起点，获得 FastAPI API 后端和展示管理条目的前端页面。 条件：模板同时包含 React、SQLModel、PostgreSQL、JWT 登录、自动生成前端客户端及 Docker Compose/FastAPI Cloud 等路线；需按当前固定提交检查依赖和环境变量，并自备数据库/部署服务。模板组件不属于 FastAPI 核心。 来源：[Full Stack FastAPI Template README](https://github.com/fastapi/full-stack-fastapi-template/blob/aabb90126964a164e02aff39e7c385bb0598236d/README.md#L8-L8)、[Full Stack FastAPI Template README](https://github.com/fastapi/full-stack-fastapi-template/blob/aabb90126964a164e02aff39e7c385bb0598236d/README.md#L38-L38)。

## 资料覆盖与缺口

研究了官方功能概览、请求体/响应模型、SQL 数据库、OAuth2/JWT、文件上传、WebSocket、后台任务、流响应和部署指南，并读了固定 Git commit 的官方全栈模板 README。模板把 API 后端、管理条目页面、数据库和认证等组合成一个可继续定制的个人项目起点，但没有逐页审查、安装或验证运行。

FastAPI 不自带数据库、托管身份、队列、对象存储、React 前端或生产主机。WebSocket 官方内存广播示例只适用于单进程；大型任务需要外部队列；文件上传需 `python-multipart`。价格、地区限制、当前稳定版、性能和生产安全都未核验。

## 原研究保留的未解决问题

- 未固定 FastAPI 当前稳定版 semver；官方页面内容与模板固定提交的依赖版本需在实施时锁定。
- FastAPI 是 API 框架，不提供应用数据库、任务持久化队列、对象存储、托管身份、客户端前端或运行主机。
- 官方全栈模板 README 展示管理条目 UI 和技术栈，但本研究未逐页审查模板的 CRUD 行为、安装运行或安全配置。
- 未核实 FastAPI Cloud、数据库/队列/邮件/存储/主机供应商现价和地区支持。
- 未安装、运行、压力测试或部署示例；不能据此保证吞吐、可靠性、安全性或消息送达。
