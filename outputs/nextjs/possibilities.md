# Next.js 能交付什么

**范围：**面向独立开发者，研究 App Router 的可交付 Web 软件、内容和商业成果。核心框架能力与第三方依赖分别说明。当前官方页面日期截至 2026 年，未锁定单一 semver。需要基本 Web、JavaScript 和 React 知识。本研究以文档和示例判断可行性，没有安装运行或生产实测。

## 发布与触达用户

- **发布可被搜索与分享的内容站**（核心）——为页面生成 SEO 与社交分享所需元数据，也可制作动态 OG 图像。 条件：Next.js 提供 Metadata API；排名、社交站点的实际展示和流量效果不作保证。动态内容仍依赖内容源。 来源：[Metadata and OG images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images)。
- **提供多语言路由与本地化页面**（核心）——按语言路由并渲染相应语言内容，让不同 locale 的访客访问对应站点版本。 条件：路由和渲染可用 Next.js；译文、locale 字典、缺译处理需自行提供，具体翻译服务/第三方 i18n 库是可选扩展。国际 SEO 标签也需按需处理。 来源：[Internationalization](https://nextjs.org/docs/app/guides/internationalization)。
- **用 Markdown/MDX 发布文档或博客**（扩展）——把 MDX 内容转成 Next.js 路由页面，并在文章中嵌入 React 组件。 条件：需安装并配置 `@next/mdx` 等相关包；App Router 还需 `mdx-components.tsx`。内容由本地文件维护；本条不意味着具备非技术编辑用的 CMS。 来源：[How to use markdown and MDX in Next.js](https://nextjs.org/docs/app/guides/mdx)。
- **搭建由编辑维护的 CMS 内容站**（扩展）——让内容编辑者通过 Sanity Studio 管理结构化内容，Next.js 前台负责读取、渲染和路由。 条件：依赖 Sanity 项目、Studio/内容 schema、`next-sanity` 集成和环境配置；Sanity 价格/额度未核实。Sanity 能力不是 Next.js 内建。 来源：[Sanity and Next.js](https://www.sanity.io/docs/nextjs/introduction)。

## 运营数据型应用

- **交付读取真实数据的应用页面**（扩展）——从服务端组件读取异步数据并渲染页面；搭配 Supabase 可查询托管数据库并显示记录。 条件：Next.js 提供数据读取/渲染方式；Supabase 项目、表结构、URL、密钥与访问策略需另行配置。托管服务费用随计划与用量而定，本轮未核价。 来源：[Fetching Data](https://nextjs.org/docs/app/getting-started/fetching-data)、[Use Supabase with Next.js](https://supabase.com/docs/guides/getting-started/quickstarts/nextjs)。
- **处理服务端表单提交**（核心）——使用 React Server Actions 在服务端接收表单提交。 条件：这是表单提交机制；具体业务逻辑、字段验证、认证授权、数据持久化或通知需要自行实现或接入其他服务。未将预约、留言等具体业务当作该来源已证明的功能。 来源：[How to create forms with Server Actions](https://nextjs.org/docs/app/guides/forms)。
- **为应用加入账号与访问控制**（扩展）——实现注册登录、会话管理及依据用户身份限制数据/路由访问。 条件：Next.js/React 提供服务端机制；官方建议生产应用用认证库或身份服务处理认证，会话和授权。需供应商配置、密钥/回调及安全实现；供应商费用未核实。 来源：[How to implement authentication in Next.js](https://nextjs.org/docs/app/guides/authentication)。
- **交付可管理发票的财务仪表板**（扩展）——官方完整课程案例涵盖公开首页、登录、受保护的仪表板和发票新增/编辑/删除，数据库使用 Postgres。 条件：这是官方学习课程展示的完整应用任务，不代表开箱即有。课程用身份认证和 Postgres；课程列出 React/JavaScript、Node.js 20.9+、GitHub 与 Vercel 账号为前提。需要自行完成实施与部署。 来源：[Next.js Foundations course: Dashboard App](https://nextjs.org/learn/dashboard-app)。

## 连接外部系统

- **提供应用 API 与远程操作接口**（核心）——建立 HTTP 端点，访问数据源并执行远端数据更新等副作用。 条件：用 Next.js Route Handlers；官方明确 BFF/API 层不是完整后端替代品。认证、授权、校验、持久化和运行维护仍需落实。 来源：[How to use Next.js as a backend for your frontend](https://nextjs.org/docs/app/guides/backend-for-frontend)。
- **交付可登录并保存会话的 AI 聊天应用**（扩展）——扩展 Next.js 与 AI SDK/模型提供商，用户提交消息后流式生成回复并把会话消息保存到数据库。 条件：这是 AI SDK 团队维护的开源应用样板，不是 Next.js 内建 AI。需模型提供商 API key（按模型用量计费可能产生费用）、数据库及认证配置；文件附件还需对象存储，API 应做限流。 来源：[AI SDK Chatbot](https://chatbot.ai-sdk.dev/docs)、[Chatbot architecture](https://chatbot.ai-sdk.dev/docs/architecture)。

## 收款与经营

- **搭建品牌在线商店前台**（扩展）——用 Next.js 交付店面界面，连接由 Shopify 提供的商品目录、购物车、结账和客户账户。 条件：Vercel Shop 模板采用 Shopify；需 Shopify 店铺、Storefront 凭证和环境变量。Next.js 本身不提供这些商业能力；Shopify 计划/交易费用未核实。 来源：[Vercel Shop](https://vercel.com/templates/next.js/vercel-shop)。
- **接受一次性线上付款**（扩展）——借助 Stripe Checkout 收取一次性捐款或单次付款，并将支付流程连接到 Next.js 服务端操作与回调。 条件：Next.js 官方仓库示例需 Stripe 账户、publishable/secret key、Webhook secret 与 Stripe CLI/线上 webhook 设置；真实交易费、税务与退款要求按地区/业务核实。示例运行于测试模式，测试成功不代表生产支付已配置。 来源：[Example using Stripe with TypeScript and react-stripe-js](https://github.com/vercel/next.js/blob/d768085563d520882e200a244a90e068f71a6571/examples/with-stripe-typescript/README.md#L40-L40)。
- **交付带订阅管理的 SaaS 产品**（扩展）——以 Next.js SaaS Starter 为基础提供定价页、Stripe Checkout、登录用户仪表板与 Stripe 客户门户订阅管理。 条件：这项由官方组织模板结合 Stripe、Postgres、Drizzle 与认证组成，需各服务账号、数据库连接、webhook 与环境变量。模板不是 Next.js 核心功能；Stripe/托管价格与计费条件未核实。 来源：[Next.js SaaS Starter](https://vercel.com/templates/next.js/next-js-saas-starter)。

## 面向移动访问

- **让网站可安装到手机主屏并发送推送**（扩展）——制作可作为 PWA 添加到手机主屏的站点，并向订阅用户发送 Web Push 通知。 条件：需配置 Web App Manifest、Service Worker、HTTPS、VAPID 密钥、推送订阅持久化/发送；用户浏览器及系统需支持。官方指南标明 iOS 需 16.4+ 且添加到主屏才能用 Web Push。离线缓存不在此能力承诺内。 来源：[How to build a Progressive Web Application (PWA) with Next.js](https://nextjs.org/docs/app/guides/progressive-web-apps)。

## 部署与交付

- **部署并交付可访问的网站**（核心）——将应用部署为 Node.js 服务、Docker 容器或静态导出网站。 条件：Node/Docker 支持完整 Next.js 功能；静态导出功能受限。托管、域名、云额度和运维成本依平台而定，未核价。 来源：[Deploying](https://nextjs.org/docs/app/getting-started/deploying)。

## 资料覆盖与缺口

核对了官方概览、国际化、PWA、MDX、数据获取、认证、表单、BFF、元数据、部署指南；并阅读完整 Dashboard App 课程、Vercel Shop、Stripe 的 Next.js 示例/SaaS Starter，以及 Sanity 和 AI SDK 的集成/应用架构资料。完整应用案例具体覆盖发票管理和登录式 AI 聊天，因而能够从实际用户任务而非框架概述识别产品结果。

CMS、Stripe 与 MDX 均有可核对的扩展来源；数据库、认证、支付、CMS、模型、商店和托管服务不归为 Next.js 内建能力。未做运行/部署、安全和交易实测，也未核实供应商当前费用与地区条件。PWA 离线能力由第三方 Serwist 扩展，本图未确认离线交付。

## 原研究保留的未解决问题

- 未固定当前稳定版 semver；官方页面更新日和示例模板版本不能视为统一兼容矩阵。
- PWA 离线缓存没有列为确认 P：指南指向 Serwist 扩展，并要求其 webpack 配置；浏览器和离线策略仍需独立验证。
- CMS 与 SaaS/Stripe 各有直接集成指南或模板证据，但未独立完成模板的安装运行、内容发布、支付/退款/webhook 或生产部署测试。
- 未核实各供应商当前价格、额度、交易费、国家/地区可用性与税务合规要求；AI 模型消耗尤其会随实际调用产生费用。
- 本轮研究确认的是资料描述的可实现结果，不保证特定项目性能、准确性、安全审查、收入或交付时长。
