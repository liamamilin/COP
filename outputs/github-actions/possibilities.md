# GitHub Actions 可能性地图

范围：个人代码库的构建、测试、发布及维护自动化；明确 runner、仓库权限、费用和外部 action 依赖。

## 按用户结果浏览

### 构建与质量检查

- **在每次代码变更时自动构建并运行测试**（核心）——对 Node.js 项目，在推送或拉取请求时运行干净依赖安装、构建和测试；可用版本矩阵检查多个 Node.js 版本。 条件：使用 GitHub-hosted 或自托管 runner；Node.js 示例模板依赖 actions/checkout 与 setup-node 等外部 Actions。固定提交中示例使用 v4 action，而当前官方文档可能展示更新版，不能原样复制后假设版本仍最新。公有仓库标准 GitHub-hosted runner 和自托管 runner免费；私有仓库的 runner 用量与存储取决于账户计划，超出额度会计费。 来源：[Building and testing Node.js - GitHub Docs](https://docs.github.com/en/actions/tutorials/build-and-test-code/nodejs)、[Node.js CI workflow template (pinned actions/starter-workflows commit)](https://github.com/actions/starter-workflows/blob/e3c451d60f119b71caebf13c98ac45da6e15b4b7/ci/node.js.yml#L1-L1)、[Billing and usage - GitHub Docs](https://docs.github.com/en/actions/concepts/billing-and-usage)。
- **保存构建和测试产物供下载或后续检查**（核心）——把构建产物、测试结果、日志或覆盖率文件作为 workflow artifact 保存，供后续查看或下载。 条件：通过 upload-artifact 等官方或外部 action 配置文件路径和保留时间。保留期受仓库、组织或企业设置上限约束；artifact 是 workflow 产物存储，不等同于可靠长期备份。 来源：[Store and share data with workflow artifacts - GitHub Docs](https://docs.github.com/en/actions/tutorials/store-and-share-data)。

### 发布与部署

- **把构建通过的 Node.js 应用部署到 Azure Web App**（扩展）——用完整的 Azure Web Apps workflow 模板，在默认分支推送后构建/测试应用、上传产物并部署到目标 Azure Web App。 条件：这是 GitHub 官方 starter-workflows 的具名部署模板，不是已运行的客户案例。需先创建 Azure App Service，配置应用名称和发布配置文件 secret；Azure 账号/资源和外部 azure/webapps-deploy Action 是额外依赖。模板的 action 版本可能落后，需审阅并更新；可用 GitHub Environment 增加人工审批和 secret 门控。 来源：[Azure Web App Node.js deployment workflow template (pinned actions/starter-workflows commit)](https://github.com/actions/starter-workflows/blob/e3c451d60f119b71caebf13c98ac45da6e15b4b7/deployments/azure-webapps-node.yml#L1-L1)、[Deploying with GitHub Actions - GitHub Docs](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments)。
- **在版本标签发布时构建并推送容器镜像**（扩展）——用 Docker 工作流在版本标签触发后构建镜像并推送到容器 registry；示例也展示 PR 检查时不推送。 条件：官方 starter-workflows 固定提交中的可配置模板，默认使用 GHCR、需要 package 写权限，并组合 Docker/Sigstore 第三方 actions；PR 不执行推送。仓库模板固定于已核实提交，但模板内 action 版本本身是另一个版本基准，复用前应审阅、更新并按需要锁定完整 action SHA；实际镜像发布尚未运行验证。 来源：[Docker build and publish workflow template (pinned actions/starter-workflows commit)](https://github.com/actions/starter-workflows/blob/e3c451d60f119b71caebf13c98ac45da6e15b4b7/ci/docker-publish.yml#L13-L13)、[Docker build and publish workflow template (pinned actions/starter-workflows commit)](https://github.com/actions/starter-workflows/blob/e3c451d60f119b71caebf13c98ac45da6e15b4b7/ci/docker-publish.yml#L72-L72)。

### 安全与维护

- **将代码扫描结果变成仓库安全告警**（扩展）——配置 CodeQL 分析代码，把发现的漏洞或编码问题显示为 GitHub code scanning alerts，帮助开发者定位和处理。 条件：使用 GitHub CodeQL/code-scanning 工作流并消耗 Actions 用量。公有仓库可用；私有仓库需有 GitHub Code Security 许可。CodeQL 仅分析其支持的语言和框架，扫描结果需要人工研判，不代表不存在未发现问题。 来源：[Code scanning with CodeQL - GitHub Docs](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning)。
- **在多个仓库复用同一套工作流规则**（核心）——将通用构建或发布流程做成 reusable workflow，由其他仓库调用并传入参数/secret，减少复制和分叉维护。 条件：被调用流程需声明 workflow_call；调用者需按规则传递 inputs/secrets 和权限。跨仓库调用需可访问目标 workflow，并应使用固定 SHA 或可信发布版本；调用端上下文决定 runner 与计费。 来源：[Reuse workflows - GitHub Docs](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)。
- **让 Dependabot 自动提出 Actions 依赖更新 PR**（扩展）——由 Dependabot 为 workflow 使用的 Actions 提交版本升级 PR，供团队审核合并，减少手动跟踪外部 action 发布的工作。 条件：需为仓库配置 Dependabot version updates。官方文档说明支持 GitHub repository syntax 引用，不能自动更新本地 `./.github/actions/...` 引用；升级 PR 仍需人工检查变更和权限/安全影响。 来源：[Secure use reference - GitHub Docs](https://docs.github.com/en/actions/reference/security/secure-use)。

### 实际个人项目案例

- **在代码提交后验证、构建并发布静态研究阅读器**（扩展）——一个真实的个人项目 workflow 在提交时运行资料定位校验、lint、test、build 和浏览器验收，随后上传 Pages artifact 并部署静态站点；成功运行记录显示部署完成，公开站点可访问。 条件：这是本仓库 P Atlas 的真实工作流与一次成功运行，不保证其他仓库直接复用即成功。该 workflow 对 main 上的 push 部署；pull_request 只执行检查，不部署。它依赖 GitHub Pages、Pages artifact/deploy actions、仓库权限和项目自有 build/e2e 环境。运行记录里的 action/runner 弃用通知表示需维护升级。此次读取运行详情中日志访问需登录，成功状态、提交短 SHA、时长、产物和部署 URL 可见；公开页面抓取只确认站点标题，未验证浏览器交互。 来源：[P Atlas static Pages workflow (fixed commit)](https://github.com/liamamilin/COP/blob/88be8cd5d14ccae200bb706dc7ab6e6982659464/.github/workflows/atlas-pages.yml#L85-L85)、[P Atlas static Pages workflow (fixed commit)](https://github.com/liamamilin/COP/blob/88be8cd5d14ccae200bb706dc7ab6e6982659464/.github/workflows/atlas-pages.yml#L87-L87)、[P Atlas GitHub Actions run #9 (successful deployment)](https://github.com/liamamilin/COP/actions/runs/42021785254)、[Published public P Atlas Pages site](https://liamamilin.github.io/COP/)。

## 能力边界与覆盖缺口

Actions 由仓库事件、定时或手动触发 workflow，并在 GitHub-hosted 或自托管 runner 执行。公开仓库使用标准 GitHub-hosted runner通常不收费；私有仓库配额和费用随计划、runner 类型与存储量变化。

云部署涉及目标平台、发布凭据、组织权限和第三方 action。可通过 GitHub Environments 限制分支、保管 secrets 并设置人工审批。starter-workflows 展示的是模板路线，不表示已部署成功或客户成果；工作流内引用的 action 版本需单独审查。

本轮查阅官方教程、billing/security/deployment/reusable-workflow 手册和固定提交下的 Node.js CI、Azure 部署、Docker 发布完整 workflow 文件。未运行工具、部署或计费模拟。

## 待验证方向

- 自托管 runner 上隔离运行个人私有仓库的构建任务；适用场景和安全边界需先评估，尤其不能让不可信 PR 接触敏感主机或 secrets。
- 更多语言包、移动端签名及不同云平台发布模板；本轮未逐一覆盖。

## 原研究保留的未解决问题

- 没有在真实仓库创建 workflow、运行 runner、测试 Azure/registry credentials、核验 approval gate 或复现构建和发布。
- 第三方 actions 由各维护者提供，不由 GitHub Docs/Actions 本身保证质量；固定提交里的样例 action 版本可能已经过时，copyable template 不等于生产安全配置。
- 私有仓库 GitHub-hosted runner/存储额度与超额费依账户方案、runner OS/规格和使用量而变；没有计算用户账单。
- 未穷尽部署到各云服务、包仓库、移动端签名/发布及自托管 runner 平台；这些需要云/发布凭据、权限及额外依赖。
- Self-hosted runner 需自己维护容量、安全与隔离；不应把来自不可信 PR 的代码放到能访问敏感 runner 或秘密的环境。
