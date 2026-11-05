# P Atlas v0.1 — 静态可能性地图阅读产品

> 状态：实施规格，尚未完成前端实现。工作名称：P Atlas / Possibility Atlas。
> 产品目标：让用户浏览、理解和使用已有 P Discovery 成果。**生产是 Codex + p-discovery Skill 的职责，阅读端绝不生成 P 或调用模型。**
> 开发基线：`proposal/cop-capability-map-v0`，现有三个内容资产位于 `outputs/ggplot2/`、`outputs/langchain-agent/`、`outputs/obsidian/`。

## 1. 两个系统各负其责

```
研究资料 → Codex + p-discovery Skill → 人工审核/校验 → outputs/<slug>/possibilities.{json,md}
                                                          ↓ git commit / PR
                                catalog/p-atlas-topics.v0.1.json + 静态构建
                                                          ↓
                                 P Atlas（无后台、无数据库、无模型调用）
                                                          ↓
                           浏览主题 → 探索 P → 看限制/来源 → 复制目标
```

P Discovery 是研究能力；P Atlas 是只读知识产品；Git/GitHub 是发布与版本来源。不要重建抓取器、Agent Harness、任务队列、登录、评论或内容编辑系统。

## 2. 最小产品体验

### 首页：主题图书馆
- 标题和一句用户价值表述：「探索一个主题可以做成什么」。
- 展示 **已上线** 的 ggplot2 / LangChain Agent / Obsidian；分组导航、关键词筛选、主题卡片。
- 卡片展示主题名、简介、领域标签、P 数（从 JSON 实际计算）、分类数、资料截点、研究状态「有来源支持 ≠ 已实测」。
- **待研究** 主题来自 catalog；可置于次要的「研究计划」区域，不与已完成主题混淆。绝不渲染空白地图。
- 核心使用无需账户、API Key、数据库或登录。

### 主题页：可能性浏览器
- 左侧用途分类导航（`groups`），中间 P 条目，详情区域展示：标题、可实现结果 `result`、条件与边界 `conditions`、`core / extension / unknown`、可选 `capability_layer` / `required_components`、来源和原文摘录。
- 支持当前主题内检索标题、结果、别名、关键词；筛选内置/扩展/待核实。允许一项 P 跨分组，但详情 ID 唯一。
- 所有「有来源支持」条目都应该显示「来源支持，未必实测」；仅具真实人工审阅记录才显示「人工复核」。不能拿结构校验当真实性认证。
- 复制「给 AI / coding agent 的目标描述」：包括当前主题、P 的观察结果、必要前提和来源 URL；**只是复制纯文本，不发给任何模型，不自动生成实现方案**。
- 提供可分享地址（静态站可用 URL hash / query 或构建期生成路径），刷新和直接打开都能定位主题及 P。

### 完整报告
- 提供「地图视图 / 研究报告」切换。报告来自同目录 `possibilities.md`，在浏览器内安全渲染 Markdown（外链可点，未受信任 HTML 不执行）。
- 视图保留原文所述研究方法、覆盖缺口、例外和冲突。始终可以打开 GitHub 上的原始 Markdown/JSON。
- 不重新合成研究内容，不在 UI 添加未经来源支撑的解释。

### 视觉与交互
- 专业、克制、阅读优先；沿用仓库现有的暖白/深色中性色风格，但不依赖旧 COP Studio 的动态页面代码。
- 桌面三栏可收起；手机单栏、分类抽屉、详情独立区域；不允许横向滚动遮住正文。
- 清晰的字号层级、长标题截断策略、键盘可操作、焦点可见、对比度合理、链接可访问。
- 不做复杂知识图谱、动画背景、用户系统、收藏同步、算法推荐、统计榜单。

## 3. 技术边界与数据契约

**建议新增** `apps/atlas`（独立 Vite + React + TypeScript 静态应用）而不是将现有 `apps/web` 的 Next `output: standalone`、FastAPI、数据库移植到 GitHub Pages。保持旧系统完全可运行。

- `catalog/p-atlas-topics.v0.1.json`：人工维护的主题元数据（标题、领域、简短范围、优先级、`ready/planned`），不存 P 内容。
- 构建时仅对 `ready` 的主题读取 `outputs/<slug>/possibilities.json` 和 `possibilities.md`，校验输入并生成前端静态资产及主题索引；`planned` 不要求有文件。
- **JSON 是交互视图唯一内容来源**；Markdown 是原文阅读来源。禁止把 3 份 P 手工复制成前端组件或另外维护一套手写内容。
- 3 份 JSON 共同字段：`topic.name/scope`、`sources[id,title,url,evidence]`、`groups[id,name]`、`possibilities[id,title,result,status,availability,conditions,source_ids,evidence_refs,group_ids,aliases]`、`coverage_gaps`。某些可选字段和来源类型名称不一致（`source_type` 或 `source_class`）；只按共有字段强制校验，其他显示时安全降级。
- `status` 只读：`source_supported`、`proposed`、`reviewed`；`availability`: `core`、`extension`、`unknown`。不要用「验证通过」来指代 `source_supported`。
- 仅允许外部 `http(s)` 来源链接且安全打开；不要渲染 Markdown/JSON 为可执行 HTML。即便站点静态化，来自网页抓取的内容仍视作不可信数据。
- 可采用 hash 路由规避 GitHub Pages 子路径深链接刷新 404（如 `/COP/#/topic/obsidian/p/p-knowledge-network`）；正确设置 `base`，不要把根路径写死。
- 初始内容无浏览器运行时 API 依赖；复制使用浏览器剪贴板能力，可提供复制失败后的手动选中方案。
- 避免使用「从 GitHub 动态读取最新文件」作为默认方式，以免线上看到尚未审阅的内容。新主题由 Codex 交付、经仓库审阅后随构建发布。

## 4. 质量和验收

- 三个现有地图都能完整打开；各自 P 数为 ggplot2=74、LangChain Agent=53（52 source_supported + 1 proposed）、Obsidian=63。**数量用于对账而不是质量排名**。
- 主题分类、P 检索、内置/扩展筛选、详情、来源跳转、全文报告、复制目标全部可用。
- LangChain 的未证实生成式 UI 必须与 confirmed 分离；Obsidian 的官方插件不被误称内置；ggplot2 的第三方扩展不被错归核心。
- 记录「研究资料截点」「未经独立人工验收」「未经运行实测」的区别；不能删去限制信息。
- 构建检查 `ready` 主题的所有文件完整、JSON 可解析、引用有效；复用 `.agents/skills/p-discovery/scripts/validate.py`（最好在构建或 CI 中检查）。
- 建议自动化测试：空结果/错误 JSON/未知来源、多组标签、搜索结果、筛选、深链接、复制目标、Markdown 不可信 HTML、移动布局。
- 本地可执行 `pnpm --filter @cop-studio/atlas dev` 和 `pnpm --filter @cop-studio/atlas build`；项目其他现有的 lint/test/build 不得回归。
- GitHub Pages 静态部署，优先利用 Actions。推送新的已审阅 `outputs/<slug>` + catalog 改动后能自动重建。第一次部署是否配置成功必须如实报告。

## 5. 明确不做

不生成新 P；不搜索网页；不把 Codex 接入浏览器；不接 AI API；不上传用户文档；不管理 prompt/Agent；不展示测试没完成的绿色认证；不建立数据库；不把旧 COP Studio 强改为新语义；不为了好看引入结构复杂的关系图。

## 6. 推荐实施顺序

先让 ggplot2、LangChain Agent、Obsidian 三份 JSON 正确消费 → 搭建真实可读的首页与 P 浏览器 → 加报告/复制/深链接 → 做响应式与回归 → GitHub Pages 发布 → 再按照 catalog 的下一批主题增加内容。

**验收重点不是页面数量，而是用户通过产品确实更容易发现、理解和使用 P。**
