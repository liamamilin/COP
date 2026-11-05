# Supabase 发现记录

## 范围

按 catalog 聚焦托管或自托管 Postgres、Auth、Storage、Realtime 和业务逻辑。区分 Supabase 平台能力与 Next.js/OpenAI、外部 OAuth、Docker/云主机等额外依赖。关注个人可以完成的数据后端和可用产品场景；未锁定 Supabase 各组件 semver。

## 第一轮：不分类候选

先从 official overview / way-to-build 记录：托管数据库、schema/API、直接前端读写、单用户数据保护、注册登录、Profile 管理、上传文件、实时变更、webhook/第三方 API、语义知识库查询、订阅计费、分支测试环境、本地 CLI、Docker 自托管。此时不按服务名组别，也不把每一 API 拆成候选。

## 第二轮：完整应用案例

### User Management App with Next.js

阅读全文后确认目标是一个用户资料应用：用 Supabase Auth 注册/登录，Postgres 保存 profile，用户可改资料，Storage 保存 profile photo。教程要求先建立托管 project/schema，再给 Next.js 安装 `supabase-js` 和 `@supabase/ssr` 并配置 key/URL；后者当前说明为 beta，不能把代码模式当作不变契约。该案例支持完整的 profile workflow，但不能证明任意生产应用自动安全。RLS 和 Storage 的 policy 需要开发者设计。

### Vector search with Next.js and OpenAI

阅读全文后确认一个可感知成果：用户对知识库提问，Next.js 应用通过 OpenAI 生成 query/doc embeddings，在 Postgres pgvector 做相似度搜索，再将相关片段交给模型回答并以流式方式显示。前提包括 Supabase CLI/托管 project、数据库 schema、Next.js 项目、Supabase/OpenAI key，部署的函数处理生成回答。此处模型 token/API 的供应商账单与 Supabase 费用分开；教程示例模型 ID 和 API 兼容性需重新核对。

## 第三轮：扩展和安全检查

- 官方 Database/way-to-build 来源说明每 project 是完整 Postgres，Data API 可以由 schema 生成；可做 internal tool、prototype、read-heavy app。浏览器可达数据表仍需 RLS，直接打开数据/API 不等于权限策略自动正确。
- Auth 来源确认密码、magic link、OTP、社交和 SSO 等路径，并说明按 MAU、第三方 MAU、SSO MAU、高级 MFA 等项计费；外部 OAuth 需 provider credentials。当前 pricing capture 显示 free plan 为 $0/月，但活跃项目和资源/使用额度会限制实际开发。
- RLS 专页警告 exposed schema 中没有 RLS 的 table 在 grants 允许时可读写。因此 P 单独强调逐表配置与审查；不声称数据默认安全。
- Storage quickstart 示范 bucket、上传/下载与 policy；Storage policy 不从 app-table RLS 自动继承，bucket public 会令文件可公开。确认文件交付，但标明授权单独配置。
- Realtime 文档区分 Broadcast 与 Postgres Changes，前者推荐用于更可扩展/安全方案，后者较简单但扩展性较低。将泛化 chat/协作收敛为直接有证据的“界面响应数据库变化”。
- Edge Functions 文档写明适合 webhook、Stripe 等第三方集成；运行环境是 Deno compatibility，机密要放 Project secrets，并有 cold starts/短任务建议。因此不把它描述为任意长任务 worker。
- Self-hosting 页说明可自有 Docker/云服务器，但托管平台的一些管理能力（如 PITR）不存在；运营方自理安全、升级、备份、监控和可用性。自托管不是免费免运维版托管服务。
- 把订阅支付、额外 OAuth provider、更多向量模型与本地测试环境识别为关联机会或外部能力；没有将其混同为 Supabase 自动附带的用户成果，因此未单列未经个别证据支持的 P。

## 归一化和分类

归一后 9 项按目的分组：建立数据后端、账号、数据隔离、资料应用、文件、实时更新、服务端集成、AI 搜索、自托管。将 database + generated API 合为一项；认证与 RLS 分开，因为前者确认身份，后者限定资源。将完整用户资料案例作为产品成果而非功能名；不把 profile picture 与通用 Storage 能力另拆出两个微小 P。

## 停止依据

结果视角覆盖 PostgreSQL/API、授权与 Auth；案例视角读了完整用户管理和 AI 文档搜索 app；扩展视角读 Storage、Realtime、Functions、pgvector、Docker self-hosting 和 pricing。每个规定能力家族均有当前官方专页/用户流程；候选如 payments、local/branching、more OAuth providers 均属额外服务或替换路线，不影响对 Supabase 本身用途的覆盖。末轮再看可加的框架语言 quickstarts 是同一 profile-management outcome 的换 frontend，实现路径重复；停止于这些用户结果覆盖完成，而非凑项目数量。

## 未知项

未在本机运行 Next.js 教程、CLI、Docker stack 或 AI search；未验证 RLS policies、文件访问、第三方 callback、model outputs、Realtime quotas、regional residency。托管价格/配额会变，需用上线时的项目配置重新估算。AI 教程中旧模型 ID/接口未按供应商当前 API 验证。

## 主 agent 来源复核

主 agent 已逐项阅读结果、条件和摘录的周边原文；按实际响应类型区分 Markdown、HTML 提取正文和源文本，并核对 GitHub 固定引用。类型标签累计修正 0 处；引文与原始缓存行号仍逐条匹配。这不授予 reviewed，不是独立人工审核或工具运行认证。

## 官方部署形态分类校准

su-09 的官方常规运行/自托管方式归为 core，主机、运行时、账号、成本与运维条件保持明确；额外业务能力的第三方集成仍使用 extension。

## 交付后复查（2026-11-05）

逐项将 Markdown 的结果、条件、能力标签与证据链接和 JSON 对齐，保留原有用途分组、覆盖说明及发现过程。报告采用条目级证据 URL；固定提交不退回移动分支。新增批次校验会拒绝报告与 JSON 的结果、限制或标签不一致。
