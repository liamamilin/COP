# P Atlas v0.2

独立于 `apps/web` COP Studio 的静态阅读应用。只消费仓库内已有的研究资产，无服务端、数据库、登录或 AI 调用。

## 运行与检查

仓库根目录，需要 Node.js 22.12+、pnpm 11.17.0、Python 3。

```sh
pnpm install --frozen-lockfile
pnpm --filter @cop-studio/atlas dev
pnpm --filter @cop-studio/atlas lint
pnpm --filter @cop-studio/atlas test
pnpm --filter @cop-studio/atlas build
pnpm --filter @cop-studio/atlas test:e2e
pnpm --filter @cop-studio/atlas preview
```

开发地址：`http://127.0.0.1:5173/COP/`；生产构建预览：`http://127.0.0.1:4174/COP/`。

浏览器验收使用系统安装的 Google Chrome。运行 `test:e2e` 前先构建站点。

默认静态 base 为 `/COP/`。其他部署路径可在构建时设 `ATLAS_BASE=/your-path/`。hash 路由支持直接打开、刷新及浏览器返回，例如 `/COP/#/topic/obsidian/p/p-knowledge-network`。

## 内容来源

`scripts/content.mjs` 每次开发或构建时读取 `catalog/p-atlas-topics.v0.2.json`，当前包含 38 个主题、726 项可能性。对每个 `ready` 主题读取 `outputs/<slug>/possibilities.json`、`possibilities.md`、`validation-report.txt`，执行引用和证据检查后生成：

- `src/generated/library.json`：目录、统计及全站检索索引。
- `public/content/<slug>.json`：原始地图、完整报告、校验记录、正文摘要哈希及 Git 快照信息。

生成目录不进入 Git；没有第二套手写 P 数据。浏览器按需读取同站静态文件，不从 GitHub 动态取得未经发布的研究。原文链接固定到构建时的 Git commit。修改 catalog 或 outputs 后重新构建即可纳入内容。`planned` 只展示研究范围，不读取或虚构地图。

## 阅读交互

主题图书馆与领域导航；全站和主题内搜索；用途分类、路径及证据状态筛选；唯一 P 深链接；来源摘录、位置、元数据与相关 P；完整 Markdown 及原研究校验报告；纯文本目标复制与失败后的手动复制；桌面可收起导航/详情，移动分类抽屉与独立详情。

`source_supported` 显示“来源支持，未必实测”。`proposed` 单列。`reviewed` 必须保有人类审阅记录，不把自动校验当人工验收。所有可选字段按文本或原始 JSON 安全显示。

Markdown 使用 react-markdown + GFM，不启用原始 HTML；仅转换严格匹配的命名锚点，以保留原报告目录；其他原始 HTML 均不执行。外链只允许 HTTP(S)，以 `noopener noreferrer` 打开；相对成果链接指向固定 GitHub 原文。图片以文字说明显示，避免读报告自动连接外部站点。没有分析追踪或外部字体请求。

## 新增 P

主导航的「新增 P」打开 GitHub 提案表单。从主题页进入时会自动填写主题名。提交需要 GitHub 登录，提案通过审核并纳入研究文件后会随下一次构建发布。

## 部署

`.github/workflows/atlas-pages.yml` 在 `main` 分支相关内容更新时执行质量检查、构建、桌面/移动浏览器验收，成功后发布到 GitHub Pages；PR 只检查。Pages 应选择 GitHub Actions 作为发布来源，`github-pages` 环境须允许 `main` 分支部署。旧 Studio 的部署方式保持不变。

目标地址为 `https://liamamilin.github.io/COP/`；是否已成功发布必须以工作流和线上访问检查为准，不能仅凭此配置认定部署完成。

测试线上产物可使用：

```sh
ATLAS_TEST_URL=https://liamamilin.github.io/COP/ pnpm --filter @cop-studio/atlas test:e2e
```

## 验证边界

浏览器验收逐一打开 38 个主题，核对条目数量、详情、来源与报告，并检查搜索筛选、深链接、复制及失败恢复、静态网络请求、响应式宽度和 axe 自动可访问性。测试使用系统 Chrome 的桌面和移动仿真配置。研究结论的实际运行验证见各主题报告。
