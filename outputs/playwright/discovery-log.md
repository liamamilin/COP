# Playwright 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `pw-01`｜结果视角｜自动验证用户的网页操作流程｜s-writing-tests
2. `pw-02`｜结果视角｜检查同一应用在不同浏览器中的表现｜s-intro
3. `pw-03`｜结果视角｜验证移动布局与地区环境差异｜s-emulation
4. `pw-04`｜结果视角｜在已登录状态下稳定验证业务流程｜s-auth
5. `pw-05`｜结果视角｜脱离真实后端测试前端异常和边界｜s-network
6. `pw-06`｜完整示例视角｜验证 REST API 并准备端到端测试数据｜s-api-testing
7. `pw-07`｜结果视角｜从 CI 失败记录还原网页操作过程｜s-trace-viewer
8. `pw-08`｜结果视角｜发现界面截图的视觉回归｜s-test-snapshots
9. `pw-09`｜结果视角｜把常见无障碍问题纳入自动回归｜s-accessibility-testing
10. `pw-10`｜结果视角｜检查多环境与多身份的同一业务行为｜s-test-projects
11. `pw-11`｜结果视角｜缩短大型测试集的执行等待｜s-test-sharding
12. `pw-12`｜结果视角｜生成适合人工和 CI 消费的测试报告｜s-test-reporters
13. `pw-13`｜结果视角｜把手工操作记录为可维护测试起点｜s-codegen-intro
14. `pw-14`｜结果视角｜验证文件下载并保存生成的交付物｜s-downloads
15. `pw-15`｜结果视角｜验证用户上传与复杂表单输入｜s-input
16. `pw-16`｜结果视角｜从已渲染页面提取任务所需数据｜s-evaluating
17. `pw-17`｜结果视角｜借助 AI 工具形成并维护网页测试｜s-test-agents
18. `pw-18`｜结果视角｜把网页输出为可分享的 PDF｜s-page

## 归一化、补漏与停止依据

先遍历实际测试结果，再阅读认证、网络、文件、报告与完整示例，最后补查可选 AI 和无障碍扩展。
归一化：将定位、等待和具体输入动作并入端到端结果；并行和分片合并为缩短大型测试等待。
发现后才按验证对象、失败调查和测试生产维护整理；跨浏览器、仿真与真实设备的边界独立记录。

## 保留的未知项

- 没有在本次研究中实测全部浏览器、设备参数和第三方测试集成。
- 无障碍、性能与安全的完整审计不能从端到端测试通过推导。
- Electron、真实手机和通用全站采集没有足够的本轮证据，未作为确认能力扩写；PDF 仅依据已取回的 Page API，不代表所有浏览器均支持。
- 真实任务证据以官方 API 测试、认证、网络与 Codegen 完整示例为主，未以项目流行度代替任务效果证据。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-accessibility-testing](https://playwright.dev/docs/accessibility-testing) | 2026-11-05T09:09:46.113621+00:00 | 是 |
| [s-api-testing](https://playwright.dev/docs/api-testing) | 2026-11-05T09:09:44.516520+00:00 | 是 |
| [s-auth](https://playwright.dev/docs/auth) | 2026-11-05T09:09:44.496080+00:00 | 是 |
| [s-codegen-intro](https://playwright.dev/docs/codegen-intro) | 2026-11-05T09:09:47.629950+00:00 | 是 |
| [s-downloads](https://playwright.dev/docs/downloads) | 2026-11-05T09:09:47.895092+00:00 | 是 |
| [s-emulation](https://playwright.dev/docs/emulation) | 2026-11-05T09:09:44.478736+00:00 | 是 |
| [s-evaluating](https://playwright.dev/docs/evaluating) | 2026-11-05T09:09:49.069038+00:00 | 是 |
| [s-input](https://playwright.dev/docs/input) | 2026-11-05T09:09:49.083782+00:00 | 是 |
| [s-intro](https://playwright.dev/docs/intro) | 2026-11-05T09:09:43.733730+00:00 | 是 |
| [s-network](https://playwright.dev/docs/network) | 2026-11-05T09:09:44.113738+00:00 | 是 |
| [s-page](https://playwright.dev/docs/api/class-page) | 2026-11-05T09:36:04.748664+00:00 | 是 |
| [s-test-agents](https://playwright.dev/docs/test-agents) | 2026-11-05T09:09:48.876425+00:00 | 是 |
| [s-test-parallel](https://playwright.dev/docs/test-parallel) | 2026-11-05T09:09:47.208772+00:00 | 否 |
| [s-test-projects](https://playwright.dev/docs/test-projects) | 2026-11-05T09:09:47.069114+00:00 | 是 |
| [s-test-reporters](https://playwright.dev/docs/test-reporters) | 2026-11-05T09:09:47.820148+00:00 | 是 |
| [s-test-sharding](https://playwright.dev/docs/test-sharding) | 2026-11-05T09:09:47.036114+00:00 | 是 |
| [s-test-snapshots](https://playwright.dev/docs/test-snapshots) | 2026-11-05T09:09:45.942529+00:00 | 是 |
| [s-trace-viewer](https://playwright.dev/docs/trace-viewer) | 2026-11-05T09:09:45.680819+00:00 | 是 |
| [s-writing-tests](https://playwright.dev/docs/writing-tests) | 2026-11-05T09:09:43.998147+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：`pw-09`、`pw-10`、`pw-11`、`pw-12`、`pw-15`、`pw-16`。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
