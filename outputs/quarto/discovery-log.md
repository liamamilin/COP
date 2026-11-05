# Quarto 发现记录

范围来自 catalog：文档、报告、演示、网站、书籍与可执行分析；区分渲染环境、扩展和发布平台。

## 无分类候选（首次发现顺序）

1. 在说明文档中嵌入可执行 Python/R/Julia 运算并带出图表/汇总结果。（结果视角）
2. 对已有 Jupyter notebook 重新执行并渲染 HTML/PDF/DOCX。（端到端教程）
3. 通过项目 freeze 让大型批量渲染仅重算源文件变化的文档。（执行优化）
4. 从多个章节文件构建多格式、有自动交叉引用的书籍。（用户结果与示例视角）
5. 将论文和所用 notebook/计算过程一起提供给读者，附多格式投稿稿件。（研究发布视角）
6. 用 Markdown 标题生成 Reveal.js/PPTX/Beamer 演示。（结果视角）
7. 用 Gapminder 数据构建带散点、面积和折线图的响应式仪表板。（完整 walkthrough）
8. 将文章集合组织成有导航、搜索的网站或博客。（结果视角）
9. 将网站接到 GitHub Pages，在提交后自动渲染并发布。（发布/CI视角）
10. 通过 Shinylive 第三方扩展在文档中嵌入可运行、可编辑的 Shiny 应用。（具体扩展案例）
11. 在文档中混合静态数据表、图表、交互 widget。（dashboard/gallery 补充候选）
12. 用 Quarto CLI 渲染任意格式作为 CI 文件产物。（发布 CI 候选）
13. 更多社区模板、代码审阅注释、讲义和无服务器组件。（扩展目录候选，需逐个核实）

## 三轮发现

- **结果视角：** guide 与 format/docs 说明同一文档可产出 HTML/PDF/Word；presentation 说明 Reveal.js、PowerPoint、Beamer；website 能组织多篇内容导航/搜索；book 按章节编译；dashboard 从多个可视化/表格组合页面；manuscript 把文章、计算与审稿格式放在网站中。
- **完整案例视角：** dashboard 官方 walkthrough 以 Gapminder 指标数据生成 GDP/life-expectancy 动画散点图、人口面积图和寿命趋势图，展示 .qmd、分栏和 chart card；book docs 列出 R for Data Science 和 Python for Data Analysis 作为已制作书例；manuscript docs 示例展示 Word 版本、AGU 模板 PDF 和可浏览/下载的 notebook。GitHub Pages 页说明本地 publish 与 Action 自动渲染/发布两条路径。
- **扩展视角：** 社区目录列出许多具名作者扩展。选择 Shinylive，另读扩展作者页面具体嵌入 Python Shiny app、slider、plot 和编辑器。区分扩展不是 Quarto 核心，并保留 self-contained HTML 不支持的边界。Shiny dashboards 需外部 server；静态 dashboard 可直接托管。

## 归一化与补漏

把可执行报告和冻结重复计算分开：前者产出分析材料，后者管理大型项目全站渲染时的运行成本。书籍和学术 manuscript 分开，因前者是多章长篇出版工作流，后者是带同行审稿 formats/notebook 的论文网页。仪表板与普通网站分开，前者专为多可视化比较/交互布局；站点与 Pages 发布分开，后者额外依赖托管和触发器。演示各格式的 UI/交互能力不同，不能认为一次源文件渲染所有 format 都等价。

## 访问失败与未采用项

`https://quarto.org/docs/computations/` 初次请求返回 HTTP 404；后来按目录指向改查成功的 `/computations/python.html` 和 `/computations/execution-options.html`。`/docs/authoring/` 返回只有 Redirect 的薄页，改以直接的输出格式和交叉引用页覆盖。没有继续列出所有语言及 PDF 引擎的单独能力，也不根据扩展画廊条目名称推断第三方功能稳定。

官网扩展目录与 Gallery 页面被读取但没有作为 P 的唯一证据：名录只能说明有什么，Shinylive 作者文档则确实读到实际嵌入 app 和编辑步骤。通用 publishing-ci 说明用于背景和边界，具体 Pages outcome 由 Pages 教程支撑。

## 未知与版本/运行边界

- Quarto CLI 及 Python/R/Julia/Jupyter/TeX/Typst 的版本须按实际环境核验；没有安装或执行。
- Notebook 的已有输出、freeze cache、依赖锁定并不自动保证数据未变化或同一计算在所有机器上相同；具体 package/data drift 未测试。
- PDF 和 Office 输出的可达性和视觉一致性与模板、字体及系统工具有关。
- GitHub Pages、Netlify、Quarto Pub、Posit Connect 等托管服务的费用、访问控制、地区和外部账号/凭证条件未实际核验。
- Shinylive 页要求完整应用、不能 self-contained HTML；未测更复杂 app、浏览器版本或外部资源网络限制。

## 停止依据

已检查 Quarto 入口的主要结果家族、每种目标的具体指南、端到端 dashboard walkthrough、publication 例子、平台发布教程、项目级执行选项和具名扩展作者使用文档。再加的主题大多是同一格式的微配置、引擎适配或数百个社区扩展中的单点。保留这些为待按具体用户目标研究项，不称覆盖穷尽。

## 实际资料取回

最终 URL、HTTP 内容类型、缓存时间/原始响应 SHA-256 和采用状态见 [source-coverage.json](source-coverage.json)。HTML 行号对应提取的页面正文；引文只放在 JSON，Markdown 和日志不重复英文摘录。


## 主 agent 来源复核

主 agent 已逐项阅读结果、条件和摘录的周边原文；按实际响应类型区分 Markdown、HTML 提取正文和源文本，并核对 GitHub 固定引用。类型标签累计修正 0 处；引文与原始缓存行号仍逐条匹配。这不授予 reviewed，不是独立人工审核或工具运行认证。

## 交付后复查（2026-11-05）

逐项将 Markdown 的结果、条件、能力标签与证据链接和 JSON 对齐，保留原有用途分组、覆盖说明及发现过程。报告采用条目级证据 URL；固定提交不退回移动分支。新增批次校验会拒绝报告与 JSON 的结果、限制或标签不一致。
