# P Atlas v0.1 实施验收

日期：2026-11-05。基线：`proposal/cop-capability-map-v0`，提案/目录基线提交 `d1d8041`。

## 已实现

- 独立 `apps/atlas` Vite + React + TypeScript 应用，不改造旧 COP Studio。
- 构建期读取 catalog 与 outputs；3 个已上线主题共 190 个 P（74 / 53 / 63），其中 1 项为待验证方向；17 个研究计划不读取或虚构成果。
- 图书馆、领域导航、全站/主题搜索、分类与组合筛选、唯一详情深链接、原文摘录与来源资料库、完整报告、固定版本 GitHub 原文链接、纯文本目标复制及失败后手动复制。
- 桌面三栏及收起操作，移动分类抽屉与独立详情，焦点/键盘操作，无全页横向溢出。
- Markdown 不执行原始 HTML，只保留严格匹配的安全命名锚点；来源仅允许 HTTP(S)，外链隔离打开。不调用 AI、数据库或其他后端 API。
- 独立 Actions 流程：内容校验、单元测试、真实构建、浏览器检查成功后才允许 Pages 部署；PR 不发布。

## 本地实际结果

| 检查 | 实际结果 |
|---|---|
| 既有 P Discovery 校验器 | 3/3 地图通过（随 Atlas 构建执行） |
| Atlas lint | 通过 |
| Atlas 单元检查 | 12/12 通过 |
| Atlas TypeScript 与生产构建 | 通过，静态 dist 已产出 |
| 桌面 Chromium / 移动 Chromium 仿真 | 22/22 通过 |
| axe 自动检查 | 首页与详情，桌面/移动均无违规 |
| 复制需求 | 浏览器剪贴板实际读写通过，拒绝权限后的完整文字手动复制通过 |
| 网络边界 | 验收页面仅请求同站静态资源，无 AI/第三方运行时请求 |
| 旧 Studio lint / typecheck / test / build | 均通过，54/54 测试通过 |
| 原始研究成果、Skill、旧 Studio 跟踪源文件 | 原有内容不改动 |

执行命令和运行说明见 `apps/atlas/README.md`。构建会调用原有 Python 校验器；生成内容不纳入 Git。构建统计/研究资料截点来自 JSON，不手写成果数据。

## 首轮发现并修复的问题

- 原报告含 HTML 锚点：直接禁用 HTML 会让目录链接失效。现在仅识别并转为静态命名锚点，其余 HTML 仍被过滤。
- 品牌可访问名称与可见文字不一致、两个搜索地标缺少区别：取消多余覆盖，补充搜索区域标签，通过 axe 复测。
- 点击 P 应保留分类与路径筛选：深链接包含相应查询参数，已加入端到端检查。
- 静态文件加载失败提供重试与原文入口；未知主题和 P 显式报错，不显示空白或伪完成页面。
- 大初始 JS 块拆分了稳定依赖，生产构建不再有 500 kB 单块告警。

## 部署记录

已实际部署并验证：[P Atlas](https://liamamilin.github.io/COP/)。首页 HTTP 请求返回 **200**，静态资源使用 `/COP/` 子路径。

- 部署的应用提交：[`017e5575b836b5d80ca05eea0b95f970686f8c34`](https://github.com/liamamilin/COP/commit/017e5575b836b5d80ca05eea0b95f970686f8c34)。
- [实际 push 部署工作流](https://github.com/liamamilin/COP/actions/runs/41987801804)：构建、检查与发布最终成功。现有 PR 的另一条运行只做检查、按设计跳过部署，未混同为发布结果。
- 首次启用 Pages 后，环境默认只允许 `main`。添加指定的 `proposal/cop-capability-map-v0` 分支规则并保留原规则后，只重试失败的 deploy 任务，成功发布。
- 对真实线上 URL 复跑 `ATLAS_TEST_URL=https://liamamilin.github.io/COP/ pnpm --filter @cop-studio/atlas test:e2e`，**22/22 通过**，含桌面和移动仿真、深链接刷新、真实剪贴板与失败回退、原文报告、来源、筛选和 axe 检查。
- HTTP 取回线上三个主题，逐一比对 map、完整 Markdown、原校验报告与 JSON SHA-256，均与仓库原始成果一致；构建 provenance 指向上述应用提交。
- 可直接打开：[ggplot2](https://liamamilin.github.io/COP/#/topic/ggplot2)、[LangChain Agent](https://liamamilin.github.io/COP/#/topic/langchain-agent)、[Obsidian](https://liamamilin.github.io/COP/#/topic/obsidian)。

本验收记录在上线后补充，不改动部署的应用代码；因此记录提交可以晚于站点构建提交。

## 仓库总 CI 的既有失败

Atlas 的独立工作流通过；全仓库旧 CI 仍有失败，未将其报告为通过。对照 [Atlas 实现前的 `d1d8041` 运行](https://github.com/liamamilin/COP/actions/runs/41984808225) 与 [当前应用提交的运行](https://github.com/liamamilin/COP/actions/runs/41987801603)，相同失败均已存在：

1. Schema consistency：`fixtures/reference-langchain-cop.json` 与 packaged reference artifact 漂移。
2. Backend：`app/domain/capability_map_v0.py`、`tests/test_capability_map_v0.py` 未满足 Ruff 格式检查。
3. 旧 End-to-end：`make local-db` 启动时 `psql` 提示 `fe_sendauth: no password supplied`，未能启动旧全栈。

这三项不属于静态 Atlas 的运行依赖。本轮保留旧系统源文件与基线内容，不通过改写参考数据或跳过检查来消除失败。

## 未实现项与验证限度

- v0.1 规格内功能无已知遗漏。没有数据库、账号、在线生成、图谱、评论、编辑或云端收藏，均属明确不做范围。
- 17 个主题只有研究计划，未生成新研究成果。
- 移动测试是 Chromium 视口/触控仿真，未声称真实 iOS Safari、Android 设备或全部浏览器验收。
- 自动可访问性检查不代替真实读屏用户测试。
- 未运行旧 Studio 的数据库/Worker 全栈浏览器套件；其前端 lint、类型检查、54 项单元测试与生产构建均实际通过。
- 原始研究的版本兼容、插件维护及实际结果限制全部保留；阅读产品的通过不构成对研究结论真实性或运行成功的认证。
