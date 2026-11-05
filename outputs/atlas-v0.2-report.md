# P Atlas v0.2：个人创造与经营能力研究交付

记录时间：2026-11-05T13:43:03.114421+00:00。工作分支：`research/atlas-v0.2-personal-capabilities`。本文保存提交前的本地验证快照；最新提交、PR 和远端 CI 状态以 GitHub 为准。

第二版以软件开发和商业为主线，补充学习研究、自动化、数据判断和个人资产管理。新增 18 个主题，全部由用户指定的 **gpt-6-luna** 研究生成，主 agent 逐项检查来源上下文、结果粒度、依赖与元数据。现有 P Discovery Skill 与已发布的 20 个主题保持不变。

本轮保存 **179 项 source_supported 结果**、**237 条来源（237 个不同 URL）**、**316 处条目级摘录**。保留 327 条实际取回记录与 56 条未取得正文的尝试。数量只用于对账，不作为覆盖完整性或质量排名。

## 领域与个人用途

| 方向 | 个人要完成的事情 | 首批主题 |
| --- | --- | --- |
| 软件开发与产品交付 | 把构想做成可使用的应用与服务 | Next.js、FastAPI、Supabase、Cloudflare Workers |
| 商业与个人经营 | 发现需求、获取反馈、交付商品或内容 | 客户发现与需求验证、PostHog、WooCommerce、Ghost |
| 学习、研究与表达 | 制作复习材料、组织证据并发布成果 | Anki、Zotero、Quarto |
| 工作流与个人运营 | 持续执行重复流程与软件交付 | n8n、GitHub Actions |
| 数据分析与判断 | 查询手边数据、查看指标和共享报告 | DuckDB、Metabase |
| 个人资产、财务与数字安全 | 管理账户、文件副本与预算记录 | Bitwarden、Syncthing、Actual Budget |

选题范围和排序见 [主题计划](../docs/proposals/p-atlas-topics-v0.2.md)，可消费的版本目录见 [v0.2 catalog](../catalog/p-atlas-topics.v0.2.json)。目录保留原有领域与 20 个主题，添加 5 个领域，共 11 个导航领域、38 个 ready 主题。这里的 ready 表示研究资产已具备，不表示已在现有线上站点发布。

## 主题交付

| 主题 | P | 采用来源 | 定位摘录 |
| --- | ---: | ---: | ---: |
| [Next.js](nextjs/possibilities.md) · [JSON](nextjs/possibilities.json) | 15 | 17 | 17 |
| [FastAPI](fastapi/possibilities.md) · [JSON](fastapi/possibilities.json) | 10 | 11 | 12 |
| [Supabase](supabase/possibilities.md) · [JSON](supabase/possibilities.json) | 9 | 14 | 17 |
| [Cloudflare Workers](cloudflare-workers/possibilities.md) · [JSON](cloudflare-workers/possibilities.json) | 11 | 11 | 16 |
| [客户发现与需求验证](customer-discovery/possibilities.md) · [JSON](customer-discovery/possibilities.json) | 10 | 11 | 14 |
| [PostHog](posthog/possibilities.md) · [JSON](posthog/possibilities.json) | 9 | 13 | 13 |
| [WooCommerce](woocommerce/possibilities.md) · [JSON](woocommerce/possibilities.json) | 13 | 21 | 29 |
| [Ghost](ghost/possibilities.md) · [JSON](ghost/possibilities.json) | 11 | 18 | 23 |
| [n8n](n8n/possibilities.md) · [JSON](n8n/possibilities.json) | 10 | 10 | 10 |
| [GitHub Actions](github-actions/possibilities.md) · [JSON](github-actions/possibilities.json) | 8 | 13 | 16 |
| [Anki](anki/possibilities.md) · [JSON](anki/possibilities.json) | 11 | 10 | 11 |
| [Zotero](zotero/possibilities.md) · [JSON](zotero/possibilities.json) | 9 | 12 | 16 |
| [Quarto](quarto/possibilities.md) · [JSON](quarto/possibilities.json) | 9 | 13 | 19 |
| [DuckDB](duckdb/possibilities.md) · [JSON](duckdb/possibilities.json) | 10 | 12 | 19 |
| [Metabase](metabase/possibilities.md) · [JSON](metabase/possibilities.json) | 9 | 18 | 38 |
| [Bitwarden](bitwarden/possibilities.md) · [JSON](bitwarden/possibilities.json) | 9 | 11 | 13 |
| [Syncthing](syncthing/possibilities.md) · [JSON](syncthing/possibilities.json) | 6 | 10 | 11 |
| [Actual Budget](actual-budget/possibilities.md) · [JSON](actual-budget/possibilities.json) | 10 | 12 | 22 |

每个主题都有 possibilities.md、possibilities.json、validation-report.txt、discovery-log.md、source-coverage.json。发现记录保留无分类候选顺序、结果/案例/扩展视角、去重补漏、修订与停止依据。资料清单保留请求/最终 URL、取回时间、响应类型、哈希、未采用页及失败尝试。仅短摘录随成果交付，第三方来源全文缓存不作为阅读器运行依赖。

## 执行与质量复核

先让 Luna 并行研究 Next.js、n8n、PostHog，纠正试点发现的问题后，沿三条队列逐主题推进。生成与复核采用原 Skill；没有为不同软件编写新的 Skill 规则，也没有要求固定 P 数量。每份地图先提取无分类候选，归一化与补漏后再建立用途组。

主要复核修正包括：

- 补查 Next.js 的完整应用、CMS、移动访问、支付等方向；不把一次失效地址或壳页当作研究已穷尽。
- 将阅读案例、泛泛安装插件、另用未知备份工具等内容从独立 P 移至案例、边界或缺口。
- 区分产品原生能力、官方客户端/部署形态、付费资格与真正额外的服务或组件。
- 纠正 Markdown、HTML 提取正文和 YAML/源文本定位基准，核对文字行号与数字字段的一致性。
- 固定 GitHub 文件到真实提交，并将引用定位到相应源码行。
- 分清 Ghost 事务邮件 SMTP 与要求 Mailgun 的批量 newsletter；分清 Metabase Guest 与已认证嵌入计费。
- 核对 Syncthing 官方 Android wrapper 当前归档状态，避免把旧家庭案例中的手机用法当作当前原生支持保证。
- 明确 Actual Budget 浏览器模式仅适合快速开始，以及银行 token 与预算端到端加密的保护范围不同。

7 个 GitHub 来源文件涉及 5 个仓库，均已再次联网取回，字节 SHA-256 与记录一致，并匹配摘录行号。其他网页、案例与 API 元数据仍可能改变；时间/哈希只说明本次取回状态。

## 交付后复查

2026-11-05 再次检查并修正了以下问题，详见 [复查记录](atlas-v0.2-review.md)：

- 原批次校验只检查报告标题，未阻止 JSON 已修订而 Markdown 仍有旧限制的情况。现在逐条检查结果、条件、能力标签和精确证据链接；179 项报告均与 JSON 对齐。
- 清除了报告中的移动 GitHub 分支引用，使用 JSON 中固定提交及行号的证据 URL；Actual Budget 的服务器/桌面客户端备份边界也已同步到报告。
- 将 GitHub Actions 的 Docker 镜像发布标为扩展能力，补充 Anki FSRS Helper 假期重排会降低未来记忆保持率及撤销操作的作者提示。
- 将 Cloudflare Agent 的“记忆”明确为持久状态/本地 SQL 存储；替换 Next.js、FastAPI 和 Cloudflare 共 5 处过于间接的摘录，来源数量和条目数量未变。
- 新增拒绝报告限制丢失、结果过时、能力误标、浮动源码链接及改写原领域的回归用例；把新版目录通过真实内容收集器读取的检查纳入自动化测试。

## 实际验证

| 检查 | 结果 |
| --- | --- |
| 原 Skill validator | 38 份地图全部通过；仅刷新 18 个新增主题的校验报告 |
| 本轮来源/元数据/定位审计 | 18 个主题、179 项结果、237 个来源、316 处摘录全部通过 |
| 实际原始缓存核对 | 316 处摘录均在所记行号内匹配 |
| 固定 GitHub 文件联网复验 | 7 / 7 通过 |
| 原有研究、Skill 与 v0.1 目录 | 102 / 102 文件 SHA-256 保持一致 |
| P Discovery 原有质量测试 | 14 / 14 通过 |
| 新增拒绝/回归测试 | 13 / 13 通过 |
| 现有阅读器内容契约兼容检查 | 已纳入自动化：真实收集器通过临时目录链接原 outputs，读取 38 个主题、726 项 P；线上目录未切换 |
| 当前 Atlas lint、单元测试、类型与生产构建 | 全部通过；单元测试 14 / 14；构建入口仍为 v0.1 的 20 个主题 |
| 当前 Atlas 桌面/移动 Chrome 验收 | 62 / 62 通过；测试对象为当前 20 主题构建 |
| git diff --check | 通过 |

新增批次审计与拒绝案例已写入 Atlas 工作流配置；本轮尚未推送，因此不能声称新配置的远端 CI 已运行。拒绝案例覆盖伪造引文、错误行号、哈希不一致、移动 GitHub 分支、响应类型误标、报告与 JSON 漂移、原领域被改写及完整文件伪装为已交付。

## 边界与未完成的发布工作

所有新增 P 均为 source_supported，没有自授 reviewed；主 agent 与 Luna 的检查都不是独立人工审核。没有安装实测全部产品、运行所有模板、连接银行/支付/真实商户账户、验证学习成效或复现案例里的业务改善。官方/作者和厂商自述案例占主要证据，不能将其视为普遍成效。版本、计划、区域资格、服务费用、扩展维护及生产兼容性均按具体来源保留条件。

研究保留了未解决方向，包括更广泛的第三方生态、移动系统限制、完整恢复测试、数据库生产负载、模型/服务变更与不同输出格式的视觉表现。没有把这些未知项伪装成已确认结果。沟通表达、职业机会、健康及其他日常事务仍可作为后续选题，本轮没有为这些方向编造地图。

本次未改 Atlas 或旧 Studio 的运行代码，新增了新版内容收集器回归测试，未重跑 Studio 后端/全栈套件，也未进行新版 38 主题的浏览器验收。现有构建仍有约 712.07 kB 主脚本的非阻断体积提示，本轮没有抬高阈值。

当前阅读器仍使用 v0.1 的 20 个主题、547 项 P。本轮 v0.2 研究与目录保存在独立研究分支，提交这些资产不会自动切换线上目录。发布新版还需切换阅读器使用的目录、对新版做浏览器验收并通过实际部署；内容契约检查不能代替这些步骤。

校验命令与限制见 [验证记录](atlas-v0.2-validation.txt)，原文件保护基线见 [baseline](atlas-v0.2-protected-baseline.json)。
