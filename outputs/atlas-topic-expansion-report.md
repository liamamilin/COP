# P Atlas：17 个计划主题研究交付

资料和检查截点：2026-11-05T11:01:02.477087+00:00。工作分支：`research/atlas-topic-expansion`。

17 个主题均已生成 Markdown、JSON 和校验报告，并新增发现记录与资料取回清单。合计 **357 项 source_supported 结果**、**287 条来源记录（284 个不同来源 URL）**；资料取回记录共 350 条。引用原文逐条与本次实际取回正文匹配。没有自授 reviewed 状态，也未以文档校验冒充安装运行。

原有 ggplot2、LangChain Agent、Obsidian 三份研究及现有 P Discovery Skill 的 14 个受保护文件 SHA-256 全部保持一致。未新增 Obsidian 等专用 Skill 规则。

## 主题入口

| 主题 | P | 确认来源记录 |
| --- | ---: | ---: |
| [Agent Harness](agent-harness/possibilities.md) · [JSON](agent-harness/possibilities.json) | 18 | 12 |
| [LangGraph](langgraph/possibilities.md) · [JSON](langgraph/possibilities.json) | 21 | 17 |
| [Model Context Protocol (MCP)](mcp/possibilities.md) · [JSON](mcp/possibilities.json) | 18 | 15 |
| [大模型推理（Inference）](llm-inference/possibilities.md) · [JSON](llm-inference/possibilities.json) | 22 | 17 |
| [大模型微调](llm-finetuning/possibilities.md) · [JSON](llm-finetuning/possibilities.json) | 19 | 17 |
| [Ollama](ollama/possibilities.md) · [JSON](ollama/possibilities.json) | 22 | 19 |
| [Codex](codex/possibilities.md) · [JSON](codex/possibilities.json) | 21 | 19 |
| [Claude Code](claude-code/possibilities.md) · [JSON](claude-code/possibilities.json) | 21 | 15 |
| [OpenCode](opencode/possibilities.md) · [JSON](opencode/possibilities.json) | 19 | 16 |
| [Playwright](playwright/possibilities.md) · [JSON](playwright/possibilities.json) | 18 | 18 |
| [AI 视频生成](ai-video-generation/possibilities.md) · [JSON](ai-video-generation/possibilities.json) | 22 | 18 |
| [AI 音乐制作](ai-music-production/possibilities.md) · [JSON](ai-music-production/possibilities.json) | 22 | 19 |
| [AI 语音](ai-voice/possibilities.md) · [JSON](ai-voice/possibilities.json) | 18 | 15 |
| [R 数据分析](r-data-analysis/possibilities.md) · [JSON](r-data-analysis/possibilities.json) | 26 | 26 |
| [Paperless-ngx](paperless-ngx/possibilities.md) · [JSON](paperless-ngx/possibilities.json) | 25 | 9 |
| [changedetection.io](changedetection/possibilities.md) · [JSON](changedetection/possibilities.json) | 19 | 13 |
| [研究工作流](research-workflows/possibilities.md) · [JSON](research-workflows/possibilities.json) | 26 | 22 |

每个主题目录均有：

- `possibilities.md`：分组结果、依赖条件、来源链接和已知缺口。
- `possibilities.json`：每项 P 的证据、来源时间和哈希、用途分类及能力边界。
- `validation-report.txt`：现有 Skill 校验的实际结果。
- `discovery-log.md`：无分类候选的记录顺序、结果／案例／扩展视角、归一化与补漏。
- `source-coverage.json`：请求与最终地址、取回时间、响应字节哈希（PR body 例外单独标注）、固定提交、未采用来源和未取得正文的尝试。

## 审查发现与修复

本轮对 68 项 P 的薄弱摘录或结果措辞作了修订，并为全部 357 项 P 增补实际章节与行号。重点修正 Paperless 自定义字段、研究 Agent 和 Quarto 等原先仅以局部名词或代码片段确认整条结果的条目；摘录以原文上下文说明支持范围，不能把短字符串匹配当作语义评审。

30 条 GitHub main/master 文件来源涉及 29 个不同文件、18 个仓库。现已固定为与首次取回字节哈希一致的 40 位提交地址，并重新联网核对全部文件与引文行号。来源清单保留原请求地址、取回时间、固定地址、原始哈希和验证时间。PR 正文的哈希仅针对 API body UTF-8 字节；合入提交描述实现版本，不使 PR 正文不可编辑。其他网页和 Wiki 同样可能更新。

Agent Harness 的 `p-context` 现在只描述把大型工具结果外部化和按需回读；`p-compaction` 负责会话历史摘要与接续，结果和条件均已消除交叉。

新增 [来源校验脚本](../scripts/verify_atlas_research.py)，离线核对记录、定位、报告一致性及短摘录额度；`--verify-pinned` 重新取回固定文件验证哈希与行号；`--cache-dir` 可核对本次原始缓存。离线检查已纳入 Atlas CI，不修改 P Discovery Skill。

## 研究范围与限制

从官方文档、维护者项目说明、完整示例与扩展路线发现任务结果，再去重、归一化和建立用途分类。不同主题按实际发现形成 4–6 个导航组，数量不构成覆盖或质量保证。领域类主题没有统一原生平台，结果以具名实现路线标记。

这些地图确认“来源声称或展示了什么”，没有安装测试所有产品、下载大模型或调用付费生成、克隆、电话、OCR 和托管服务。兼容性、维护状态、账户、地区、价格和实际效果需要使用时核实。官方案例和作者项目占主要案例证据；缺少独立用户的可重复成效评测已在各主题保留。

重要边界已分别处理：

- Codex 旧 MCP server 接入已移除；自定义客户端资料转向 app-server。OpenCode V1 / V2 并存，插件和 server API 不能假定直接兼容。
- Paperless-ngx 官网取回受限，改用官方主干文档的固定提交快照及已合入功能 PR；其中含 v3 及可选 AI 功能，不能保证已安装 2.x 都有。
- Google 视频预览模型关闭、Eleven Music 旧模型计划退役、Demucs 原仓库停止维护，均保留具体路线和限制。
- changedetection 的 Case Studies 页只有占位内容；图片引用变化不能说成像素视觉比较。
- 部分统计和生物信息案例较旧或页面显示开发版本；统计有效性和当前环境兼容均未从文档示例推定。
- Unpaywall 壳页、scite 403、无效或仅重定向的页面未被用作具体能力确认。

## Atlas 接入与验证

本地目录中 20 个主题均为 ready，共 547 项 P；其中 546 项 source_supported，1 项原有 proposed 保持不变。仅构建时读取 outputs，运行时没有新增模型或外部生成服务。

测试已改为按目录和实际 JSON 枚举全部主题；研究计划无需生成资产的契约测试仍保留。报告阅读新增发现记录与资料清单的安全文件链接。详情中的证据位置可以打开原文行，复制需求也会带上对应的精确来源链接。

| 检查 | 实际结果 |
| --- | --- |
| 20 份地图的现有 Skill 校验 | 全部 PASS |
| 新增摘录与实际取回正文逐条匹配 | 357 项 P、361 处摘录，全部 PASS |
| GitHub 固定文件再次联网核对 | 30 条来源记录、29 个不同文件；字节 SHA-256 和摘录行号全部 PASS |
| 可复跑的离线来源与报告一致性检查 | PASS；已加入 Atlas CI |
| 新增 Markdown / JSON 的 ID 与标题对应 | PASS |
| 受保护原成果和 Skill 文件 | 14 / 14 哈希一致 |
| P Discovery 质量回归测试 | 14 / 14 PASS |
| Atlas lint、TypeScript、单元测试、生产构建 | PASS；单元测试 13 / 13 |
| 系统 Chrome 桌面／移动端验收 | 62 / 62 PASS，16.9 秒 |
| 旧 Studio lint、类型检查、单元测试和生产构建 | PASS；单元测试 131 / 131 |
| git diff --check | PASS |

浏览器验收逐一打开 20 个主题的 P 列表、详情、全部来源和完整研究报告，并检查原有搜索、过滤、深链接、剪贴板、失败重试、键盘操作、静态请求与无障碍。

Atlas 构建有非阻断包体积提示：主脚本压缩后 712.07 KB，gzip 195.28 KB，超过 Vite 默认 500 KB 提示阈值。未通过抬高阈值掩盖提示，也未为本次研究引入额外架构。

旧 Studio 后端和完整业务端到端套件本轮未重跑：没有修改后端或 Studio 源码；上表不把前端检查说成整仓库远程 CI 已通过。

## 发布状态

交付分支为 `research/atlas-topic-expansion`，本报告随研究结果与修复一起版本化。以上检查均为提交前的本地验收；远端提交、PR 与 CI 状态以 GitHub 记录为准。

GitHub Pages 仅在合入 `main` 且部署工作流成功后更新。分支推送或 PR 创建不代表这 17 个新主题已经部署到线上。

完整检查汇总与原文件哈希见 [atlas-topic-expansion-validation.txt](atlas-topic-expansion-validation.txt)。
