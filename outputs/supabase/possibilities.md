# Supabase 能交付什么

**范围：**面向个人开发者，研究数据、账号、文件、实时数据、服务端逻辑、向量搜索与部署。Supabase 自有服务和 Next.js/OpenAI/Docker/第三方身份提供者分别说明。资料于 2026-11-05 取回；价格、配额、托管功能可能变化。

## 建立数据后端

- **使用托管 Postgres 与自动生成的数据 API**（核心）——为应用创建托管 Postgres 数据库，并让数据库 schema 自动生成 REST API，作为数据驱动应用的后端。 条件：需 Supabase 账号和 project。捕获的官方价格页显示免费计划 $0/月；项目数量、计算资源和用量受计划约束，费用页面可能变化。托管服务替开发者管理基础设施，但数据库 schema 和安全规则仍由开发者设计。 来源：[Supabase Platform](https://supabase.com/docs/guides/platform)、[Database](https://supabase.com/docs/guides/database/overview)、[The Supabase way to build](https://supabase.com/docs/guides/getting-started/the-supabase-way-to-build)、[Supabase Pricing & Fees](https://supabase.com/pricing)。

## 管理账号与身份

- **为应用加入账号注册与登录**（核心）——为用户提供认证和授权能力，可采用密码、magic link、一次性密码、社交登录或 SSO。 条件：需要 Supabase project；社交 OAuth/SSO 需要对应第三方身份提供者与回调配置。Supabase 对 MAU、第三方 MAU、SSO MAU 和高级 MFA 等项目计费，具体价格依当前计划。 来源：[Auth](https://supabase.com/docs/guides/auth)。
- **交付可登录并编辑资料的用户管理应用**（扩展）——官方 Next.js 完整教程让用户登录并更新个人资料，后端用 Supabase Database/Auth/Storage 组合完成。 条件：需要一个 Next.js 前端项目和 Supabase project；这是一条框架集成路线，不是 Supabase 单独生成的完整 UI。教程使用 `@supabase/ssr`；当前 SSR 指南说明该包处于 beta，API 不稳定、可能有破坏性变化。 来源：[Build a User Management App with Next.js](https://supabase.com/docs/guides/getting-started/tutorials/with-nextjs)、[Server-Side Rendering](https://supabase.com/docs/guides/auth/server-side)。

## 保护数据

- **按用户限制数据库行的读写**（核心）——用 Postgres RLS policy 在数据库层控制不同用户可读取或修改哪些行。 条件：需为暴露给浏览器/移动端的数据表设置合适的 grants 和 RLS policies；没有匹配 policy 时请求会被拒绝，错误配置可能泄露或误开放数据。应逐表审查并测试。 来源：[Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)。

## 管理文件

- **存储并提供用户文件**（核心）——将图片、视频或文档上传到 bucket，再由应用下载或提供文件访问链接。 条件：Supabase Storage 是项目服务；需要创建 bucket 和文件访问 policy。公开 bucket 可被任何人读取，私有/用户自有文件需配置独立 Storage RLS rules。存储和流量受当前计划配额/费用影响。 来源：[Storage Quickstart](https://supabase.com/docs/guides/storage/quickstart)。

## 实时协作与更新

- **让应用界面实时反映数据库变化**（核心）——订阅数据库新增、更新或删除事件，让仪表板或协作界面在数据变化时刷新。 条件：需配置 Realtime 通道、表 publication/触发器和授权。官方区分 Broadcast（更推荐扩展性与安全性）和设置更简单但扩展性较低的 Postgres Changes；具体流量/连接限制依计划。 来源：[Subscribing to Database Changes](https://supabase.com/docs/guides/realtime/subscribing-to-database-changes)。

## 运行集成逻辑

- **运行第三方 webhook 与服务端集成**（核心）——用 Edge Function 接收 webhook 或代表应用调用 Stripe 等第三方 API。 条件：Supabase 项目包含 Edge Functions；函数用 Deno 兼容的 TypeScript runtime，第三方 secret 要放在 project secrets。执行可能冷启动，应设计短时、幂等操作；长任务应交给后台 worker。Stripe 等账户和费用另计。 来源：[Edge Functions](https://supabase.com/docs/guides/functions)。

## 构建 AI 数据能力

- **为知识库应用构建语义问答搜索**（扩展）——用 pgvector 保存内容与查询的 embeddings，搭配 Next.js 和 OpenAI 构建可回答文档问题的检索体验。 条件：依赖 Postgres `pgvector`、Next.js 示例工程和 OpenAI API key/模型；OpenAI 用量单独计费，需按当前可用模型更新教程示例。embedding 同一索引必须使用兼容的模型/维度；未运行或核对模型质量。 来源：[AI & Vectors](https://supabase.com/docs/guides/ai)、[Vector search with Next.js and OpenAI](https://supabase.com/docs/guides/ai/examples/nextjs-vector-search)。

## 部署与运维

- **在自有服务器运行 Supabase**（核心）——将 Supabase 服务栈部署在自己的电脑、服务器或云基础设施上，自己掌握数据库所在环境。 条件：需 Docker、服务器、网络、安全加固、备份、升级、监控和高可用运维。自托管不是托管平台的等价替代；管理备份/PITR 等若干托管能力不提供。自托管成本转为自己的基础设施与运维。 来源：[Self-Hosting](https://supabase.com/docs/guides/self-hosting)。

## 资料覆盖与缺口

查阅了官方 Platform、Database、Auth、RLS、Storage、Realtime、Edge Functions、AI、Self-Hosting 指南和当前定价页，并读完用户资料管理与 Next.js/OpenAI 向量搜索教程。案例覆盖了登录和维护用户资料的真实应用任务，以及从知识库文档到向量检索和流式回答的端到端 AI 搜索思路。

Supabase 可以作为独立的后端服务，但 RLS policy、bucket policy、Auth 配置、外部凭据和模型费用仍须自行管理。自托管要求 Docker/服务器运维，且功能不等同于托管方案。未实测安装、查询、支付、webhook、安全策略或生产负载；费用与配额需按上线时套餐核算。

## 原研究保留的未解决问题

- 没有逐项固定托管产品内部组件的 semver，也未运行托管或 Docker 安装。
- 没有验证实际 RLS policy、Auth 回调、对象权限、Realtime channel、Edge Function webhook 签名等安全实现。
- 免费和付费套餐配额与价格会变动；捕获的价格页说明免费层级，但具体项目的存储、流量、计算、Auth MAU、Edge Function 用量应按当前 dashboard 估算。
- AI 文档搜索教程引用的 OpenAI 模型/SDK 示例未运行；服务 API 和价格可能与示例不同，答复质量和延迟不作保证。
- 自托管负责方要自行维护升级、备份、监控、HA 与安全；本研究未核算基础设施成本。
