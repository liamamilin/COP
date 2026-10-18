# LangChain Basic 标准 COP 原型：验证记录

验证日期：2026-10-03（Asia/Shanghai）。状态：**A1 / Basic 工程原型及离线验收通过；真实 provider、能力语义、目标用户验收待完成。** A1 还包含 Tools，不能因此宣称 A1、完整 LangChain case 或稳定自动生产已完成。

## 交付与边界

- 独立可运行课件：`examples/langchain-basic/`。默认 `.py` 脚本，不再依赖多个 `python -c` 之间不存在的变量传递。
- 独立 COP：`fixtures/langchain-basic-cop.json`，1 Goal、1 Process、2 Foundation Stage、3 主线 Stage、2 Branch、1 Practice、4 来源摘要。
- 只读预览：`http://127.0.0.1:3000/prototypes/langchain-basic`。不创建项目、保存学习进度、发布版本或自动运行代码。
- 来源 sidecar：`fixtures/langchain-basic-sources.json`，官方链接 + 明确标注的人工摘要，不冒充已存档网页原文、不伪造 quote_hint。
- 已保存的实际离线结果：`docs/validation/langchain-basic-offline-run-2026-10-03.json`。

本次不修改 Schema、不接入新 Harness 生成门禁、不覆盖原五目标 fixture、不修改已发布版本或开发数据库内容。不读取项目真实 `.env`，不使用用户密钥，不发真实 LLM/Exa 请求。依赖安装使用 PyPI；费用步骤在课件中明确由学习者决定。

## 教学契约

默认路径：独立 venv / 固定依赖 → 命名 `.env` / 显式配置 → 同进程创建 / invoke → 保存本次 JSON → 独立 Inspect → 真实能力与近邻迁移验收。

- `LC_API_KEY / LC_BASE_URL / LC_MODEL / LC_SYSTEM_PROMPT` 是课件自己的接口。进程值覆盖 config.py 同目录的 .env；空覆盖值也报错。不搜索父目录、不依赖 SDK 的 `OPENAI_*`、不展开 `${NAME}`。
- 默认构造 `ChatOpenAI` 对象；备选 `init_chat_model` 同样显式传 key/base URL，再回到同一个 create_agent 与后续 Stage。没有把模型字符串误说成非法参数，也没有把初始化方式包装成另一种 Agent 架构。
- `created` 只表示构造，Agent 对象不会跨进程保留；实际运行脚本在同一进程中创建、调用、检查。
- 离线 Fake 模型返回固定文本，仍经过真实 LangChain 图，但它不是 LLM 推理或 provider 兼容性证据。本课 invocation 关闭 LangSmith tracing。
- Inspect 不再次 invoke。只判断本课已完成、无工具、文本两消息 profile 的输入 / 最终回复链接；不自动判断语义，不证明文件未被改写。
- Practice 使用同一成果，要求真实运行/检查、语义判定、近邻换问题迁移与结构错误诊断；离线文件不能充作真实能力通过。
- 长代码默认折叠，核心函数由执行源码提取并单独展示；复制仍取完整文件。文件内容与 shell 命令明确区分。

## 已执行的检查

### 1. 干净安装与真实框架离线测试

新建临时独立环境：`/private/tmp/cop-basic-clean.tNdbAO/venv`。Python 3.10.13 / macOS arm64。

安装了课件 requirements 的七个固定包：langchain 1.4.3、langchain-openai 1.6.7、langchain-core 1.6.6、langgraph 1.2.12、openai 3.23.0、python-dotenv 1.2.4、langsmith 0.14.3。`pip check` 无冲突。这不是所有传递依赖的完整 lock，也不证明所有 Python 3.10+ / 操作系统组合都测试过。

在课件目录执行：

```sh
/private/tmp/cop-basic-clean.tNdbAO/venv/bin/python -m unittest -v test_basic
```

结果：**13/13 通过**，无静默 skip。包含：

- 命名文件、配置优先级（含空值覆盖）、不改环境、不读 SDK/父目录配置、占位/插值/危险 URL 拒绝。
- 真实 ChatOpenAI 两种初始化构造，检查 SDK 实际 base URL、key、模型、prompt、重试设置；不请求 provider。
- 真实 create_agent 图 + 固定 Fake 回复；模型节点实际收到 system prompt 和本次用户输入。
- 保存/独立 Inspect；从不同工作目录运行；直接复制 **COP 里的文件代码** 到新目录后配置、构造、离线调用、检查。
- 负例：空或错序输出、输入错配、伪造 answer、construction-only 冒充完整调用必须拒绝。
- 已有成果文件在调用前阻止覆盖；异常不泄露模拟 key、不写成功记录。
- 进程内 socket / HTTP 网络禁止断言，并故意启用父进程 LangSmith tracing，离线执行仍不发送。子进程使用不携带凭据/遥测的最小环境。

网络断言是测试手段，不是运行任意模型生成代码的生产沙箱。

### 2. COP 结构、内容同步与后端回归

从 backend 目录执行：

```sh
.venv/bin/python -m pytest tests/test_langchain_basic_prototype.py tests/test_operational_quality.py -q
```

结果：**26/26 通过**，其中 5 项为本次新样板检查。JSON Schema / Pydantic 引用有效；已有 L1/L2/L3 检查无 issue；保存/读取保留课件内容；每个完整教学文件逐字等于执行文件；builder 再生成结果等于提交 fixture。现有 gate 主要检查存在性，不能单凭这些绿灯宣称真实能力有效。

曾扩展执行 `test_evidence_chain.py`，其中 11 项集成测试因未配置 `TEST_DATABASE_URL` 在 fixture 初始化前停止。没有跳过保护、没有将开发库当测试库、没有执行其 truncate。本轮不声称全套数据库集成或 E2E 通过；该套件与 Basic 原型的无库验证分开记录。

### 3. 前端

```sh
pnpm --dir apps/web test
pnpm --dir apps/web typecheck
pnpm --dir apps/web lint
```

结果：**54/54 单元/静态渲染测试通过**，typecheck、lint 通过。新增 6 项 Basic 导航/展示检查及 3 项复制检查。

- Foundation 顺序、普通 Stage 的全部前置入口、Foundation 结束后单 Process 接续 / 多 Process 显式选择、主线终点回 Practice。
- Learn 页在当前已选版本的 artifact 内展开 Foundation 内容，不通过新增入口跳到最新版本。
- Branch 由共享 StageContent 渲染，Learn 与阅读页不再分叉；长文件折叠不改变代码文本。
- 原型中的概念、操作、证据均指向真实本页锚点，没有伪项目链接或虚构来源就绪状态。
- 复制等待 writeText 完成，成功/不可用/失败有明确结果；不会因 API 存在就报告成功。

本次没有构建 production bundle、没有运行完整 Playwright E2E，不将单元测试混称为这些验证。

### 4. 浏览器只读体验

实际打开新原型的 Setup、Config、Create、Invoke、Inspect，核对适用起点、明示配置、核心代码、备选和验收边界。Create 页复制折叠文件后出现 Copied；读取受控剪贴板确认 146 行、包含 main、显式 key/base URL，不只是 13 行核心摘录。

在现有 Gate 1 发布案例上只读回归：Learn Foundation 能展开实际内容；普通 Stage 可进 Install/Configure；Install 有 Next；Configure 后提供五个 Process 选择。没有标记进度、填写回答或发布。**该旧案例的原教学错误仍然存在**，此回归只证明导航兼容，不证明旧内容已修正。

## 内容绑定

以下 SHA-256 绑定本次实际检查内容，改代码/内容后必须重验，不能沿用旧绿灯：

| 文件 | SHA-256 |
| --- | --- |
| fixtures/langchain-basic-cop.json | be61ef0cb42a31ffbb910072a00a65f6ee14b9db5d3c8317d4f47f96c1d5b0e0 |
| examples/langchain-basic/agent.py | 712cc0cffb8b178a00d57acbb360a3870fd9d4c03aaef8a9b48aacdadaa20287 |
| examples/langchain-basic/config.py | 3837e42e23ebd5ab7fa1414551c96d6b73f70e9429e715d111fde599dc430643 |
| examples/langchain-basic/inspect_result.py | f721b823236fd7d50a0b0f14718faa25f4a09e312fc154bb1dee7cda1bf0c875 |
| examples/langchain-basic/requirements.txt | 8296d0eee583617480ffad40be7a8072a26fe4ee66cc2129f12a0ba17d2911d7 |
| docs/validation/langchain-basic-offline-run-2026-10-03.json | 50cb94ab79d2de2b5640af10678bcf1d1a65495bd8637fdbfa8c4579391a940d |

## 内容审核与改进（2026-10-03 后续）

完整审核记录见 `docs/validation/langchain-basic-content-review-2026-10-03.md`。审核结论：S1–S9 标准与五视角均通过，无阻塞性问题。实施了以下非阻塞信息负担改进：

1. **README 适用起点**：增加「不适合」反向声明（无 Python 3.10+、Windows、需 GUI/IDE 的场景）。
2. **README .env 格式**：明确只使用简单 `key=value`，不加引号，行首 `#` 是注释，不支持多行值或变量插值。
3. **README 常见失败**：增加「找不到 python」的恢复指导（检查 venv 激活、`sys.executable` 路径）。
4. **config.py docstring**：说明 `environ` 参数仅供测试注入，正常使用不需要传。

COP fixture 已通过 `build_cop.py --write` 重新生成，包含更新后的 config.py 源码。上述改进不改变教学主线、验收判据或安全边界；config.py 的逻辑未变，仅增加文档字符串。改动后 config.py 和 fixture 的 SHA-256 已更新。

## 下一停靠点

1. 用户审核新原型，重点看默认路线、概念必要性、备选选择条件和信息负担；它尚未进入项目发布流程。
2. 在明确 provider / model / 凭据使用范围 / 请求次数和预算后进行受控真实验证；用户独立从声明起点完成 Practice，记录需要外部帮助的位置与迁移表现。
3. Basic 达到能力/用户验收要求后进入 Tools 样板，新增 tool call / tool result 的行为判据。之后才提炼最小 Schema 契约、扩展另外三个 Goal、升级 Harness 并测多次独立生成。

相关设计：`docs/proposals/cop-quality-standard-and-production-v1.md`；旧案例审查：`docs/validation/langchain-case-audit-2026-10-02.md`。
