# GitHub Actions 发现记录

范围来自 catalog：个人代码库构建、测试、发布和维护自动化；核对 runner、仓库权限、费用与外部 Actions 依赖。

## 无分类候选（首次发现顺序）

1. 代码 push/PR 时自动构建和测试，多版本矩阵。（结果视角）
2. 保留测试/coverage/build files 为 artifacts，以供后续查看或下载。（完整教程）
3. 向 Azure Web App 部署 Node.js 应用。（完整 starter workflow）
4. 按 semver tag 构建并发布 Docker image；PR 不推送。（完整 starter workflow）
5. CodeQL 在 push/PR 周期扫描代码，将问题报告为 code scanning alert。（功能文档）
6. 将一个可配置工作流供多个仓库复用。（扩展/规模化视角）
7. 用 Dependabot 自动提出工作流 Actions 依赖更新 PR。（维护视角）
8. Scheduled workflow 定期执行；筛选与频率依任务选择。（触发器文档候选，未单列结果）
9. 生产部署前要求 Environment reviewer approval。（部署保护候选，归入部署P的条件）
10. 用自托管 runner 构建私有软件或接入自有硬件。（扩展候选，安全风险高，未独立设P）

## 三轮发现

- **结果视角：** 官方 CI 教程与 Node.js workflow 描述多版本依赖安装、build、tests；artifact 教程说明将检查产物保存；部署手册覆盖环境、并发和审批；CodeQL 结果进入代码扫描告警。
- **完整案例视角：** 不只读 Actions 模板目录。Pinned starter-workflows 仓库快照下读取完整 `ci/node.js.yml`、`ci/docker-publish.yml`、`deployments/azure-webapps-node.yml`。Node workflow 对 push 和 pull_request 运行多个 Node 版本的安装/构建/测试。Azure 文件明确要先有 App Service 和发布 profile secret，并将构建与部署拆为两个 jobs，通过 artifact 传递。Docker 文件对 semver tags 发布、PR 不推送，同时使用 GHCR、外部 Docker actions 和 Sigstore 签名。
- **扩展/生态视角：** reusable workflows 可抽象跨库的构建/发布模板并传 inputs/secrets；Dependabot 能自动维护第三方 Actions 版本。CodeQL、Azure Web Apps Deploy、Docker actions、setup-node、checkout 都是外部 action/工具，不把其存在视为 GitHub Actions 核心功能保证。Self-hosted runners 可接入自有环境，但要管理容量、隔离和安全。

## 归一化与补漏

发布路线分成应用部署与容器镜像发布，因为目标产物和凭据权限不同。build/test 与 artifact 按两个用户结果保留：一个是反馈代码质量，一个是保留可下载/传递的构建结果。CodeQL 与依赖升级属于维护/安全结果。Deployment approval 并入 Azure 部署条件，不将一个环境设置拆成P。push、pull_request、tag、schedule 和手动触发本身是触发机制；除与 Docker/CI 结果结合外，不当作独立用户结果。

## 固定提交工作流样例核验

通过官方 GitHub API 首先读取 `actions/starter-workflows` 的 main commit 元数据，再解析到提交 `e3c451d60f119b71caebf13c98ac45da6e15b4b7`。之后请求三个 raw 路径均使用这个实际40位 SHA，响应无跳转，逐行检查原始 YAML。源 URL 固定在 commit，不引用 main/master。该提交中的 action version 与当前文档有差异，样例仅作为可行的完整案例快照，不作为当前最佳实践背书。

## 保留的限制与未知项

私有仓库 GitHub-hosted runners 的 included compute 与 artifact/cache storage 根据 GitHub 账户计划而异，超过免费额度会计费；公开仓库标准 runner、自托管 runner 的计费规则不同。未依用户方案计算费用。自托管 runner 不是默认安全/省钱选择：不可信 PR 可取得主机可见 secrets 或影响持久 runner；需要强隔离和责任人维护。CodeQL 私有库需 Code Security 许可且仅支持特定语言；action 外部维护者的供应链风险需按具体版本评估。未执行任何工作流，模板中占位符与凭据必须由用户配置。

## 停止依据

已覆盖关键用户结果的官方手册、完整工作流范本、代码扫描/复用/依赖维护资料及计费安全边界。其余诸如 Azure Functions、GKE、PyPI、iOS签名、各语言矩阵都是同类模板或需额外服务，可按项目有针对性扩展；本轮不穷举模板目录。

## 实际资料取回

请求 URL、最终地址、Content-Type、取回时间和原始响应 SHA-256 见 [source-coverage.json](source-coverage.json)。文档页的行号为提取 HTML 正文行；固定提交 raw YAML 引文行对应原始响应文本行。采纳外的 API 解析/候选页面保留在覆盖记录。

## 主 agent 来源复核

主 agent 已逐项阅读结果、条件和摘录的周边原文；按实际响应类型区分 Markdown、HTML 提取正文和源文本，并核对 GitHub 固定引用。类型标签累计修正 0 处；引文与原始缓存行号仍逐条匹配。这不授予 reviewed，不是独立人工审核或工具运行认证。

## 交付后复查（2026-11-05）

逐项将 Markdown 的结果、条件、能力标签与证据链接和 JSON 对齐，保留原有用途分组、覆盖说明及发现过程。报告采用条目级证据 URL；固定提交不退回移动分支。新增批次校验会拒绝报告与 JSON 的结果、限制或标签不一致。

- 将依赖 Docker、registry 和 Docker/Sigstore actions 的容器发布结果改标 extension；运行器本身不提供镜像构建工具或 registry。
