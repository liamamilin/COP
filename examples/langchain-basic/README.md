# LangChain Basic Agent：标准 COP 的第一个原型

目标不是打印 `created`，而是独立完成「明确配置 → 创建 → 调用 → 检查同一次真实回复」，并解释、修改这条路径。

这是 A1 的 Basic 子样板，不是完整 LangChain COP。无工具、记忆、检索或中间件；离线自检与真实能力、目标用户验收分开记录。现有已发布案例不被改写，本原型暂未导入产品数据库。

产品启动后可在 `/prototypes/langchain-basic` 只读预览：五个步骤、实际代码、备选、练习和来源。它不创建项目、不保存进度、不运行代码，也不代表已发布。

## 适用起点

你能编辑文件、在终端运行 Python；已有 Python 3.10+。主线命令面向 macOS/Linux，下面每条 `python` 命令都在本目录且已激活 venv。版本见 `requirements.txt`，它固定七个主要包，不是所有传递依赖的完整 lock。首次安装需要联网下载软件包，但不调用模型。

**不适合**：还没有 Python 3.10+ 或无法使用终端的环境（本课件不覆盖安装指导）；Windows 用户（激活命令不同，不在本次已验 profile 内）；需要图形界面或 IDE 集成的场景。

从仓库根目录进入并建立独立环境（已有 `.venv` 时不要覆盖它）：

```sh
cd examples/langchain-basic
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -c "import sys; from langchain.agents import create_agent; from langchain_openai import ChatOpenAI; print(sys.executable); print('imports ok')"
```

应看到本目录 `.venv` 的解释器路径和 `imports ok`。`python -c` 在此只测导入；真正任务使用 `agent.py`，不是几个彼此独立的一行命令。重新打开终端时，先回到本目录并再次激活 venv。

## 1. 显式配置，没有“盲找”

```sh
cp -n .env.example .env
chmod 600 .env
```

用编辑器打开 `.env`，填写自己的 `LC_API_KEY`、`LC_BASE_URL`、`LC_MODEL`；不在命令里写密钥。模板中的官方 URL 仅是示例；第三方服务须使用其控制台/文档的 base URL、模型 ID 和对应 key，不能混用。`LC_SYSTEM_PROMPT` 可自定义，缺省为 `Answer in one short sentence.`。

**.env 文件格式**：只使用简单 `key=value`，不加引号（如 `LC_API_KEY=sk-xxx` 而非 `LC_API_KEY="sk-xxx"`）；行首 `#` 是注释；不支持多行值或变量插值（`${NAME}` 会被拒绝）。

`config.py` 定义本课规则：进程 `LC_*` 优先于 **config.py 同目录** `.env`（空进程值也会覆盖并报错）；不找父目录、不展开 `${NAME}`、不读取 `OPENAI_*` 或 COP Studio 的服务配置。它读取文件后，将值明确传给 SDK；`.env` 本身不会自动生效。文件读取用法依据 [python-dotenv 文档](https://bbc2.github.io/python-dotenv/)，模型参数依据 [ChatOpenAI 集成文档](https://docs.langchain.com/oss/python/integrations/chat/openai)。

```sh
python config.py
```

应显示 `key_configured: true`、正确的 base URL/model/prompt，不显示 key。占位值、缺值、带凭据或 query 的 URL 会报错。base URL 不是 `/chat/completions` 请求完整地址；远程必须 HTTPS，本机才允许 HTTP。`.env` 已被本仓库忽略，别上传它或带密钥的截图。

如生效值不是刚填的文件值，可清除当前 shell 的课件覆盖变量后重新检查：

```sh
unset LC_API_KEY LC_BASE_URL LC_MODEL LC_SYSTEM_PROMPT
python config.py
```

没有凭据可以跳过真实路径，做离线工程自检，但不能认定 Goal 完成。

## 2. 创建：核心与运行外壳分开理解

默认核心在 `agent.py` 的 `build_agent`：显式构造 `ChatOpenAI`，再将模型、空工具列表、系统指令交给 `create_agent`。`main` 负责参数、保存和安全报错，暂不要求一次掌握整个 CLI 的实现。

本课版本的 `from langchain.agents import create_agent` 是合法导入；它不是所有旧版本的统一 API。其返回值是可执行图，`created` 是本课脚本打印的构造状态。[官方 Agents 文档](https://docs.langchain.com/oss/python/langchain/agents)

可选构造探针（不请求模型）：

```sh
python agent.py --create-only
```

构造成功只证明配置/对象可建立，不能证明 key 通过鉴权。对象在此进程退出时消失；下一次正常执行 `agent.py` 会在同一新进程里创建、调用并检查它。

不是只有一种模型初始化方式。需要统一 provider 初始化入口时，可选 `build_agent_from_identifier`：`init_chat_model` 接收模型名、`model_provider="openai"` 和显式 key/base URL，然后回到同一 `create_agent`。[官方 Models 文档](https://docs.langchain.com/oss/python/langchain/models)

```sh
python agent.py --model-init identifier --create-only
```

回接下一步时保留 `--model-init identifier`，Inspect 不变。`create_agent` 直接接收模型字符串也合法，但依赖集成的配置约定，本课不把未经说明的环境默认值作为主线。两种初始化不是两种 Agent 架构；ReAct、Tools 等在本课范围外。

## 3. 调用：先离线，再由你决定是否发真实请求

离线不需要 key，固定 Fake 模型仍经过真实 LangChain 图：

```sh
python agent.py --offline --message "Name one benefit of using an agent harness." --output offline-run.json
```

结果为 `mode=offline-fixture`，`human → ai`，固定回复 `This is a scripted offline reply, not an LLM response.`。换问题也不会真正推理；它只检查管线，不证明回复能力。SDK 不被调用，本课 invocation 关闭 LangSmith tracing，避免继承遥测配置产生额外发送。

真实能力路径需有效凭据、网络、额度、明确服务与预算；准备好且愿意产生请求费用才运行：

```sh
python agent.py --message "Name one benefit of using an agent harness." --output first-run.json
```

程序在同一进程创建/调用/检查一次，保存 `mode=provider-response` 的 JSON。默认 Chat Completions 路径、30 秒超时、自动重试为 0。第三方服务的兼容性需要真实验证；本次开发没有替你执行真实请求。

已有输出文件会在创建/调用前阻止运行；重跑选新文件名，不覆盖旧成果。如果想重跑同一文件名，先手动删除或移动旧文件，但不要为了重跑而删除之前需要保留的成果。失败只显示异常类型及 HTTP 状态，不打印 provider 原始异常或 key，也不写”成功”记录。

## 4. Inspect：不要再调用一次

```sh
python inspect_result.py offline-run.json
# 真实调用成功后才执行：
python inspect_result.py first-run.json
```

检验器只读保存文件，不读 key、不创建 Agent。它检查本课完成的无工具文本 profile：两条消息类型为 `human, ai`、首条等于本次 input、最后非空 ai 等于 answer。这个规则不能推广到工具、流式或多模态结果。

结构 `PASS` 不判断回答含义。真实任务还需人工确认：回复与问题相关、说出了一个 Agent harness 的收益、符合简短句子指令。答案措辞不必固定。检验器也不证明 JSON 没被手工改过。

## 5. 最小 Practice 与验收

交付 `agent.py/config.py/inspect_result.py/requirements.txt`、不含 key 的配置摘要、本次真实运行文件和检查记录。不要交付 `.env`；分享日志前确认输入不含个人敏感数据。

- 解释每项配置来源、优先级，为什么 `created` 不是服务接通证明，为什么 Inspect 不再 invoke。
- 近邻迁移：预测换问题会改变什么；在同一脚本用 `--message "What does a system prompt control?" --output second-run.json` 进行另一次真实运行（可能再收费），检查新输入/回复及语义。
- 诊断：复制已有 JSON 为新的文件，用编辑器将 `input` 改到与首条消息不一致；检验器应拒绝。解释结构错配与回答语义不相关的区别。

只有离线输出时，记录「工程自检通过；真实 provider/能力/学习者验收待完成」。填写 checkpoint 或点击完成不能替代真实结果与迁移能力。

常见失败：找不到 `python` 或 `command not found` 时，先确认 venv 是否激活（提示符应有 `(.venv)` 前缀），运行 `which python` 或 `sys.executable` 检查是否指向本目录 `.venv/bin/python`，未激活则重新 `source .venv/bin/activate`；导入错先核对 venv/版本；401 核对服务与 key；404 核对 base URL/model；429 停下来确认额度；连接/超时检查网络；已有文件改用新文件名。不要无限重试。结构 PASS 但回答不相关，记录语义失败并核对本次 prompt，而不是把检查结果当模型质量证明。

## 维护与离线回归

```sh
python -m unittest -v test_basic
python build_cop.py --write
```

测试包含真实框架 + 固定 Fake 模型、禁止网络的负例、配置/脱敏/防覆盖和独立验收器。不是生产安全沙箱，也不是对任意生成代码的自动执行授权。

构建器只生成独立的 `fixtures/langchain-basic-cop.json` 和来源摘要 sidecar；Stage 中代码直接来自本目录执行文件，避免两份实现漂移。来源是有官方链接的人工摘要，不冒充网页快照。验证结果见 `docs/validation/langchain-basic-prototype-2026-10-03.md`。

A1 的两个子样板（Basic + Tools）均已完成工程实现、离线验证和真实 Provider 验证（6/6 通过）。下一步为目标用户验收（B08）：从声明起点独立完成 Practice，记录卡点和迁移表现。Tools 样板见 `../langchain-tools/README.md`，对照总结见 `docs/validation/tools-basic-comparison-t08-2026-10-03.md`。
