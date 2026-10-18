"""Build the independent Basic prototype from the SAME files learners execute.

This is a deterministic content builder, not a Harness generation or a publish.
Only --write updates the two explicitly named, generated local fixtures.
"""

# Long Chinese lesson paragraphs remain readable as adjacent string literals.
# ruff: noqa: E501

import argparse
import ast
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARTIFACT_PATH = ROOT / "fixtures/langchain-basic-cop.json"
SOURCES_PATH = ROOT / "fixtures/langchain-basic-sources.json"

SOURCES = [
    {
        "id": "basic-agents-docs",
        "title": "LangChain Agents · 人工摘要（非网页快照）",
        "original_uri": "https://docs.langchain.com/oss/python/langchain/agents",
        "text": "人工摘要，2026-10-02 核对官方页面：create_agent 是本版本合法的高层入口；"
        "model 可以是标识符或已初始化模型，system_prompt 用于系统指令。invoke 接受 messages 状态。"
        "本样板将范围限定为无工具、一次文本调用，不把该限制推广为所有 Agent 的消息形状。",
    },
    {
        "id": "basic-models-docs",
        "title": "LangChain Models · 人工摘要（非网页快照）",
        "original_uri": "https://docs.langchain.com/oss/python/langchain/models",
        "text": "人工摘要，2026-10-02 核对官方页面：init_chat_model 可以指定模型名和 provider，"
        "也可以直接使用对应的模型类。两者是初始化选择，不是新的 Agent 架构。",
    },
    {
        "id": "basic-openai-docs",
        "title": "ChatOpenAI integration · 人工摘要（非网页快照）",
        "original_uri": "https://docs.langchain.com/oss/python/integrations/chat/openai",
        "text": "人工摘要，2026-10-02 核对官方页面：ChatOpenAI 可显式传入 model、api_key 和 base_url。"
        "OpenAI-compatible 服务的兼容范围需由对应服务确认；不能因为构造对象成功就推断请求可用。",
    },
    {
        "id": "basic-dotenv-docs",
        "title": "python-dotenv · 人工摘要（非网页快照）",
        "original_uri": "https://bbc2.github.io/python-dotenv/",
        "text": "人工摘要，2026-10-02 核对官方页面：dotenv_values 返回文件配置而不修改进程环境。"
        "本样板指定文件路径并关闭变量插值，LC_* 的覆盖规则由 config.py 自己定义。",
    },
]


def file_detail(filename: str, action: str, expected: str, caution: str = "") -> dict:
    return {
        "title": f"保存 {filename}",
        "action": action,
        "command": (HERE / filename).read_text(encoding="utf-8"),
        "expected_result": expected,
        "caution": caution or "这是文件内容，不是让你逐行粘贴到 shell 的命令。",
    }


def command(title: str, action: str, code: str, expected: str, caution: str) -> dict:
    return {
        "title": title,
        "action": action,
        "command": code,
        "expected_result": expected,
        "caution": caution,
    }


def function_source(filename: str, name: str) -> str:
    text = (HERE / filename).read_text(encoding="utf-8")
    node = next(
        item
        for item in ast.parse(text).body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    return ast.get_source_segment(text, node)


def stage(
    key: str,
    title: str,
    goal: str,
    why: str,
    outcome: str,
    details: list[dict],
    example: dict,
    sources: list[str],
    branches: list[str] | None = None,
) -> dict:
    return {
        "id": f"stage.{key}",
        "title": title,
        "local_goal": goal,
        "why_it_exists": why,
        "local_outcome": outcome,
        "concept_refs": [f"concept.{key}"],
        "operation_refs": [f"operation.{key}"],
        "branch_refs": branches or [],
        "implementation_details": details,
        "example": example,
        "evidence_refs": [{"source_id": item} for item in sources],
    }


def build_artifact() -> dict:
    stages = [
        stage(
            "foundation.install",
            "准备独立 Python 环境",
            "得到能导入本课 API 的独立解释器和固定依赖。",
            "必须先约定工作目录和版本，避免终端装到一个 Python、脚本却由另一个 Python 运行。",
            "产物：langchain-basic-lesson/.venv 与 requirements.txt；后续终端命令均在课件目录内运行。",
            [
                command(
                    "建立课件目录与虚拟环境",
                    "本主线面向 macOS/Linux shell；能编辑文本文件、使用终端，已安装 Python 3.10+。"
                    "从你选定的父目录执行；langchain-basic-lesson 必须尚不存在。命令成功后继续留在此目录。",
                    "python3 --version\nmkdir langchain-basic-lesson\ncd langchain-basic-lesson\npython3 -m venv .venv\nsource .venv/bin/activate",
                    "Python 3.10 或更高；提示符进入独立 venv。mkdir 失败时停止，选择新的目录名，不覆盖旧练习。",
                    "Windows 的激活命令不同，不在本次已验 profile 内。venv 不会安装 Python 本身。",
                ),
                file_detail(
                    "requirements.txt",
                    "在当前课件目录新建 requirements.txt，保存下面的完整内容。",
                    "文件含七个固定版本；这是本次兼容 profile，不是所有传递依赖的完整 lock。",
                ),
                command(
                    "安装并检查导入",
                    "在刚建立的课件目录、已激活的 venv 执行。",
                    "python -m pip install -r requirements.txt\npython -m pip check\npython -c \"import sys; from langchain.agents import create_agent; from langchain_openai import ChatOpenAI; print(sys.executable); print('imports ok')\"",
                    "pip check 无冲突，解释器路径位于当前 .venv，最后输出 imports ok。",
                    "安装会联网下载依赖，但不会调用模型。这里 python -c 只作导入探针，不是 Agent 主线实现。"
                    "新开终端时先 cd 回此课件目录并重新激活 venv。",
                ),
            ],
            {
                "summary": "导入探针只证明包和解释器可用。",
                "input": "在已激活的独立 venv 执行上面的检查。",
                "output": "<课件目录>/.venv/bin/python\nimports ok",
                "note": "路径示意，不是所有机器的逐字输出。此时没有模型调用。",
            },
            ["basic-agents-docs"],
        ),
        stage(
            "foundation.model",
            "显式配置 key、endpoint、model",
            "能指出每项配置从哪里来，并安全检查最终生效值。",
            "COP Studio 的服务器配置和本地学习脚本不是同一个进程。文件存在也不等于 SDK 会自动读取它。",
            "产物：config.py、同目录 .env 和一份不包含密钥的配置摘要；下一步由脚本读取。",
            [
                file_detail(
                    "config.py",
                    "在课件目录保存 config.py。读 load_settings 即可理解配置入口，其他代码是输入检查。",
                    "只读取 config.py 旁的 .env；不会搜索父目录、修改 os.environ 或展开 ${NAME}。",
                ),
                file_detail(
                    ".env.example",
                    "在同目录保存 .env.example；它是模板，不是真实配置。",
                    "模板没有真实密钥。LC_* 是本课自定义变量，SDK 不会直接读取它们。",
                ),
                command(
                    "填写私密配置",
                    "在课件目录执行复制后，用文本编辑器打开 .env。填入你自己的服务 key、服务 base URL 和"
                    "服务实际支持的模型 ID。示例官方 URL 不适用于所有第三方；第三方要填其文档指定的 base URL。",
                    "cp -n .env.example .env\nchmod 600 .env\npython config.py",
                    "替换占位值后显示 key_configured=true、base_url、model、system_prompt；不显示 key。"
                    "占位值未替换则报 Configuration error，先修配置再继续。",
                    "不把 key 写进脚本/终端历史/截图/提交。独立课件若使用 Git，请将 .env 加入 .gitignore。"
                    "进程 LC_* 优先于文件，即使为空也会覆盖并报错；不读取 OPENAI_*、COP Studio 设置或父目录 .env。"
                    "base URL 不带 /chat/completions、不夹 key/query；只允许远程 HTTPS 或本机 HTTP。",
                ),
                command(
                    "未取得服务凭据时",
                    "不需要伪造 key；先进入下一 Stage 保存 agent.py，再做 Invoke Stage 中的 --offline 自检。"
                    "但真实能力验收仍待有效凭据、网络、额度和明确预算。",
                    "",
                    "当前可完成环境准备与配置规则阅读；固定回复不证明服务接通。",
                    "暂不发模型请求。离线自检的命令和验收位于 Invoke Stage。",
                ),
            ],
            {
                "summary": "安全配置摘要的形状。",
                "input": "python config.py（填好你自己的配置后）",
                "output": '{"key_configured": true, "base_url": "<服务 base URL>", "model": "<模型 ID>", "system_prompt": "Answer in one short sentence."}',
                "note": "形状示意，不是对第三方 provider 的兼容性证明。LC_SYSTEM_PROMPT 缺省才使用课件默认值。",
            },
            ["basic-openai-docs", "basic-dotenv-docs"],
        ),
        stage(
            "basic.create-agent",
            "创建 Agent：默认脚本，备选初始化",
            "把明确配置的模型装入一个无工具 Agent。",
            "模型负责回复，create_agent 提供运行外壳；构造成功不等于服务已响应。"
            "创建、调用、检查在同一个 agent.py 进程内，不靠上一个 python -c 留下变量。",
            "产物：agent.py；运行时的 model 和 agent 对象仅存于当前进程。",
            [
                file_detail(
                    "agent.py",
                    "在与 config.py 相同的课件目录保存完整 agent.py。先关注 build_agent 的三步："
                    "显式初始化 ChatOpenAI → create_agent → 返回 agent。main 是运行/保存/错误处理外壳，暂不要求逐行掌握。",
                    "默认为 ChatOpenAI 对象 + create_agent(model=model, tools=[], system_prompt=...)。"
                    "create_agent 返回可 invoke 的图，不是字符串 created。",
                    "没有工具、记忆、检索、流式、多模态；"
                    "本课固定使用 Chat Completions 兼容路径，max_retries=0、超时 30 秒，并关闭本课调用的 LangSmith tracing。"
                    "第三方服务仍需真实测试，不能由此声称所有服务兼容。",
                ),
                command(
                    "先理解文件中的核心，而不是全部 CLI",
                    "这是上面 agent.py 内的 build_agent 原样摘录；无需另存一个重复文件，也不直接粘到 shell 执行。"
                    "观察 config.py 的 Settings 如何成为明确模型参数，以及 Agent 如何取得 system_prompt。",
                    function_source("agent.py", "build_agent"),
                    "返回的 Agent 等待同一脚本里的 invoke_agent 调用；构造阶段没有回复。",
                    "下面保存/参数/报错部分是运行外壳，可按需再展开完整文件阅读。",
                ),
                command(
                    "可选：只测构造，不请求模型",
                    "完成配置后，在课件目录执行。输出是程序自己打印的构造摘要。",
                    "python agent.py --create-only",
                    "mode=construction-only、status=created；没有回复，也没有运行结果交给 Inspect。",
                    "进程退出后 agent 对象消失。下一 Stage 正常运行 agent.py 会在同一新进程中重新创建并调用。",
                ),
                command(
                    "备选：按标识符初始化模型",
                    "需要统一 provider 初始化入口时选它；其他情况沿默认主线。"
                    "build_agent_from_identifier 显式调用 init_chat_model(model, model_provider='openai', api_key, base_url)，"
                    "之后仍调用同一个 create_agent。先用构造探针，再回到 Invoke Stage。",
                    "python agent.py --model-init identifier --create-only",
                    "仍为 construction-only；参数没有从父进程 OPENAI_* 盲取。真实调用时保留 --model-init identifier。",
                    "这是模型初始化备选，不是另一 Agent 架构。直接把 model 字符串交给 create_agent 也合法，"
                    "但它会依赖集成的配置约定；本课不用未说明的默认 key/endpoint。旧版 ReAct API 不作为此版本默认教程。",
                ),
            ],
            {
                "summary": "构造探针和完整调用是不同证据。",
                "input": "python agent.py --create-only",
                "output": '{"mode": "construction-only", "status": "created", "configuration": "<脱敏配置摘要>", "note": "No provider request. This object ends when this process exits."}',
                "note": "简化形状。created 是本课脚本输出；不代表模型推理、工具调用或本次尚未执行的真实服务已验。",
            },
            ["basic-agents-docs", "basic-models-docs", "basic-openai-docs"],
            ["branch.basic.identifier"],
        ),
        stage(
            "basic.invoke",
            "调用一次并保存这次结果",
            "让同一进程中的 Agent 接收用户输入，把其结果交给下一阶段。",
            "invoke 的输入是 messages 状态。保存结果可避免 Inspect 为了查看结果又触发另一次收费请求。",
            "产物：offline-run.json（固定本地回复）或 first-run.json（真实服务返回），二者不能混作同一种证据。",
            [
                command(
                    "先做离线连通性自检",
                    "在课件目录执行；FakeMessagesListChatModel 会返回固定句子，不读 key、不请求 provider。",
                    'python agent.py --offline --message "Name one benefit of using an agent harness." --output offline-run.json',
                    "mode=offline-fixture；两条消息 human → ai；输入等于命令里的问题，回复明确标注 scripted offline reply。",
                    "即使换了问题也只返回固定句子，所以它不算达成回复能力。已有输出文件会在调用前报错；重跑使用新文件名。",
                ),
                command(
                    "真实能力路径：有凭据且同意费用后",
                    "完成 Foundation 配置，先确认服务、模型、额度与预算；"
                    "愿意发起本次模型请求时才运行。在课件目录执行。若选了标识符分支，在命令里追加 --model-init identifier。",
                    'python agent.py --message "Name one benefit of using an agent harness." --output first-run.json',
                    "mode=provider-response；human 输入与命令相同；ai 是非空文本。实际措辞不固定，需由你判断是否回答了问题、"
                    "是否符合一短句的 system_prompt。",
                    "这是联网且可能收费的步骤。本次开发没有代你执行；"
                    "不自动重试（max_retries=0）。鉴权/限流/连接失败返回安全类型和状态码，不输出 key 或成功报告。",
                ),
            ],
            {
                "summary": "实际离线路径的固定回复；真实回复不编造。",
                "input": "Name one benefit of using an agent harness.",
                "output": '{"mode": "offline-fixture", "messages": [{"type": "human", "content": "Name one benefit of using an agent harness."}, {"type": "ai", "content": "This is a scripted offline reply, not an LLM response."}]}',
                "note": "摘录；完整 JSON 还含 input、answer、configuration、note。真实 LLM 成果仍待验，不要求与此文本相同。",
            },
            ["basic-agents-docs"],
            ["branch.basic.offline"],
        ),
        stage(
            "basic.inspect",
            "检查同一次回复，完成任务验收",
            "独立核对输入、消息类型、最终 answer 之间的关系，再判断任务是否完成。",
            "有一条 ai 消息不等于完成；空内容、输入错配、查看旧文件和无关回答都不能通过真实能力验收。",
            "产物：同一次 JSON 的结构检查记录、人工语义判断及 checkpoint 回答；不再创建或调用 Agent。",
            [
                file_detail(
                    "inspect_result.py",
                    "在课件目录保存 inspect_result.py。它只用标准库读取已有文件，"
                    "不依赖 config.py，不创建模型，不再调用 API。",
                    "能检查 mode、human → ai、input 一致、非空最后 ai 与 answer 一致。",
                ),
                command(
                    "检查已存在的离线文件",
                    "使用上一 Stage 的 offline-run.json，不生成新结果。",
                    "python inspect_result.py offline-run.json",
                    "mode: offline-fixture；message types: human -> ai；PASS；LIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED。",
                    "PASS 只代表本课已完成无工具文本调用的结构和链接；不自动给语义或学习能力打分。",
                ),
                command(
                    "检查真实文件并完成人工验收",
                    "仅在上一 Stage 真实调用成功后执行。人工检查问题与回答相关、"
                    "给出了一个收益、是简短句子；不比对某个预先编写的标准措辞。然后完成 Process 的 Practice。",
                    "python inspect_result.py first-run.json",
                    "mode: provider-response + 结构 PASS。语义合格才能认定基本回复任务完成；"
                    "若 provider 忽略指令，记录未通过，先检查 config 摘要再调整 prompt，不能只点完成。",
                    "不能用 construction-only 或 offline 文件冒充真实验收。inspect_result 本身不会证明文件未被人工改写，"
                    "也不能由回复推断模型版本、tool-use 或记忆能力。",
                ),
            ],
            {
                "summary": "离线记录可证明运行管线，不能证明真实能力。",
                "input": "python inspect_result.py offline-run.json",
                "output": "mode: offline-fixture\nmessage types: human -> ai\n...\nPASS: saved invocation shape and input/answer linkage; not a semantic answer grade.\nLIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED",
                "note": "摘录。真实路径需检查 first-run.json 的本次输入和真实回复，而不是再 invoke 一次。",
            },
            ["basic-agents-docs"],
        ),
    ]
    concept_specs = [
        (
            "foundation.install",
            "运行 Profile",
            "本课约定解释器、包版本、工作目录和操作系统边界；不是永远通用的安装法。",
            "保证后续代码在同一种执行环境里理解。",
        ),
        (
            "foundation.model",
            "显式配置",
            "LC_* 是本课接口；进程值优先于命名 .env 文件，脚本再将其显式传给 SDK。",
            "回答 key、endpoint、model 从哪里来，避免隐藏输入。",
        ),
        (
            "basic.create-agent",
            "模型与 Agent",
            "ChatOpenAI 是模型接口；create_agent 将它装配成可运行图。无工具 Agent 此处只做一次模型回复。",
            "区分构造成功与实际能力，理解以后为何加入工具。",
        ),
        (
            "basic.invoke",
            "一次调用的 messages",
            "本课输入为 user 消息字典，完成结果的标准化对象类型是 human、ai；它们是角色表示，不是变量名称。",
            "把一次输入及其最终回复作为连续成果传递。",
        ),
        (
            "basic.inspect",
            "分层验收",
            "结构一致、模型回答有效、学习者能迁移，是三种不同证据。固定 Fake 回复只能支持第一种的有限检查。",
            "防止把打印 created 或结构 PASS 误认成全部完成。",
        ),
    ]
    failures = {
        "foundation.install": [
            "ModuleNotFoundError：先看 sys.executable 是否为课件 .venv，重新激活，再用 python -m pip install -r requirements.txt。",
            "create_agent 导入失败：核对本课固定版本；不要把旧版 0.x 的教程当成当前 1.x API。",
            "pip check 冲突：在独立新 venv 安装，不向已有项目环境强行升级。",
        ],
        "foundation.model": [
            "Configuration error：按错误中的 LC_* 名称填写，删除 replace- 占位或 ${...}；空进程变量也会覆盖 .env。",
            "配置摘要仍是旧值：在终端 unset LC_API_KEY LC_BASE_URL LC_MODEL LC_SYSTEM_PROMPT 后重新检查（只清当前 shell 的课件覆盖值）。",
            "第三方 endpoint 不明：查对应服务文档/控制台，不猜 URL，也不因官方示例自动使用 api.openai.com。",
        ],
        "basic.create-agent": [
            "created 没有回答：这是 --create-only；它仅构造，去下一 Stage 正常调用。",
            "另一个进程找不到 a/result：变量不跨 python -c；用完整 agent.py 或保存的 JSON，不依赖之前终端变量。",
        ],
        "basic.invoke": [
            "AuthenticationError / HTTP 401：核对 key 属于该服务、权限有效；日志不提供 key，检查 .env 时也不截图泄露。",
            "NotFoundError / HTTP 404：核对 base URL 与该服务 model ID；不要在 base URL 后再填请求路径。",
            "RateLimitError / HTTP 429：查额度或限流，停下确认预算，不能无限重跑。",
            "APIConnectionError / APITimeoutError：检查网络/服务状态，失败没有可供 Inspect 的成功记录。",
            "--output already exists：用新的明确文件名；不要为了重跑删除之前成果。",
            "--offline 回答与问题无关：预期行为，它是固定 Fake 回复；不要用它评判真实模型。",
        ],
        "basic.inspect": [
            "FileNotFoundError：确认工作目录、输出文件名及上一 Stage 是否成功；不要临时再调用模型补一个不同的 result。",
            "Inspection failed：检查是否拿错了 construction-only 文件或修改了 input/answer；本课只接受完整的两消息文本 profile。",
            "结构 PASS 但回答不相关/不够短：人工语义验收失败，核对本次 configuration 和 prompt；不是检验器自动判定语义成功。",
        ],
    }
    return {
        "schema_version": "0.1",
        "artifact_id": "cop.langchain-basic.prototype.v1",
        "domain": {
            "name": "LangChain Basic Agent · 标准 COP 原型",
            "scope": "A1 的第一个最小单位：从独立环境、显式配置到一次无工具文本回复及同次结果验收。"
            "Python 3.10+、macOS/Linux shell、固定依赖、OpenAI-compatible Chat Completions。离线工程路径已测；真实服务及目标用户验收待完成。",
            "target_user": "能编辑和运行 Python 文件，但不应被要求知道 SDK 隐式环境变量的新手。",
            "non_goals": [
                "Tools、Memory、RAG、Middleware 尚未纳入本样板。",
                "不保证所有 provider/模型兼容；不验证流式或多模态。",
                "不是自动 Harness 产物，不是已发布完整案例；离线自检不替代真实能力和学习者验收。",
            ],
        },
        "mental_model": {
            "summary": "配置定义模型连接与系统指令；Agent 装配模型；一次 invoke 消耗输入、产生回复；"
            "保存结果再 Inspect。默认脚本维持一次运行的对象连续性，文件维持跨进程的证据连续性。",
            "flow": [
                "准备独立环境",
                "显式配置",
                "创建 Agent",
                "同进程 invoke 并保存",
                "同一文件 Inspect",
                "能力与迁移验收",
            ],
        },
        "goals": [
            {
                "id": "goal.basic",
                "title": "独立完成一次有指令的 Agent 回复",
                "outcome": "能运行 Python 脚本，使用明确服务配置向无工具 Agent 发消息，检查同一次真实回复，解释并修改输入/系统指令。",
                "why_it_matters": "为下一步 Tools 建立能运行、能判断成功且没有隐藏配置的最小基础。",
                "prerequisite_goal_refs": [],
                "evidence_refs": [{"source_id": "basic-agents-docs"}],
            }
        ],
        "shared_foundations": [
            {
                "id": "foundation.basic",
                "title": "Basic 环境与显式配置",
                "stage_refs": ["stage.foundation.install", "stage.foundation.model"],
            }
        ],
        "main_processes": [
            {
                "id": "process.basic",
                "goal_ref": "goal.basic",
                "title": "创建 → 调用 → 检查同一次回复",
                "start": {"type": "foundation", "ref": "foundation.basic"},
                "stage_refs": [
                    "stage.basic.create-agent",
                    "stage.basic.invoke",
                    "stage.basic.inspect",
                ],
                "outcome": "agent.py + 本次真实 JSON + 结构/人工语义检查 + checkpoint；只有离线文件时记录真实验收待完成。",
                "practice_ref": "practice.basic",
            }
        ],
        "stages": stages,
        "concepts": [
            {
                "id": f"concept.{key}",
                "name": name,
                "definition": definition,
                "role": role,
                "key_operation_refs": [f"operation.{key}"],
            }
            for key, name, definition, role in concept_specs
        ],
        "operations": [
            {
                "id": f"operation.{key}",
                "name": item["title"],
                "definition": item["local_goal"],
                "purpose": item["why_it_exists"],
                "acts_on_concept_refs": [f"concept.{key}"],
                "common_failures": failures[key],
            }
            for item in stages
            for key in [item["id"].removeprefix("stage.")]
        ],
        "branches": [
            {
                "id": "branch.basic.identifier",
                "type": "alternative",
                "title": "标识符初始化模型（可跳过）",
                "parent_stage_ref": "stage.basic.create-agent",
                "parent_process_ref": "process.basic",
                "description": "选用条件：希望统一模型初始化入口。Create Stage 已给完整 build_agent_from_identifier；"
                "使用 --model-init identifier，配置仍显式传入。回接 Invoke 时保留此参数，Inspect 不变。"
                "两种写法仍是同一种无工具 Agent，本课不罗列所有历史架构。",
            },
            {
                "id": "branch.basic.offline",
                "type": "alternative",
                "title": "无凭据：离线工程自检（不计真实能力通过）",
                "parent_stage_ref": "stage.basic.invoke",
                "parent_process_ref": "process.basic",
                "description": "没有凭据/暂不愿产生费用时用 --offline；固定 Fake 回复，保存 offline-run.json 并回接 Inspect。"
                "之后要达成 Goal，取得有效服务配置和费用许可，回到 Invoke 做真实路径，再检查新的 first-run.json。",
            },
        ],
        "practices": [
            {
                "id": "practice.basic",
                "title": "把同一个 Agent 的一次回复交付出来",
                "goal_ref": "goal.basic",
                "instructions": [
                    "从 Foundation 的独立目录开始，完成 requirements.txt、config.py、.env、agent.py、inspect_result.py；记录 python 版本与非秘密配置摘要。不得提交 .env/key。",
                    "先运行 --offline 并检查 offline-run.json；若只有这一步，记录工程自检通过、真实能力待验，不认定 Goal 完成。",
                    "凭据、网络、额度和费用许可齐备后运行真实命令，交付 first-run.json（先检查其中不含密钥/个人敏感问题）、结构检查和人工语义判断。回答是否说出了一个 Agent harness 的收益，是否符合一短句指令。",
                    "近邻迁移：先预测换用户问题会改变什么；用 --message 'What does a system prompt control?' 和新输出名 second-run.json 运行一次真实调用。检查本次输入与最终回复；不能复制固定离线回复来充数。该步骤可能再产生一次费用。",
                    "诊断任务（不联网）：复制已有报告为另一个文件，用编辑器将 input 改为与第一条消息不一致；检验器必须拒绝。解释这与回答内容不相关为何是不同问题。",
                ],
                "expected_outcome": "交付脚本、固定依赖、脱敏配置摘要、两次真实运行/检查与语义判定、失败变异结果和 checkpoint。"
                "不要求真实答案逐字相同；离线结构检查通过不等于学习能力通过。",
                "checkpoint_questions": [
                    "api_key、base_url、model、system_prompt 各来自哪里？若 shell 的 LC_MODEL 与 .env 不同，哪个生效？",
                    "为什么 --create-only 的 created 不能证明真实服务可用？进程退出后对象去了哪里？",
                    "messages 的输入 role=user 与结果 type=human/ai 是什么关系？Inspect 为何不再 invoke？",
                    "如果第二次回复不够短，你会检查什么？为什么结构 PASS 不能替你给语义或学习能力打分？",
                ],
            }
        ],
        "expansion_map": [
            {
                "title": "Tools：让模型调用一个可验证函数",
                "description": "Basic 真实能力验收后进入 A1 的第二样板；新增 tool call/结果消息与行为判据，不能沿用本课两消息规则。",
                "from_goal_ref": "goal.basic",
            },
            {
                "title": "Memory：显式保存跨调用状态",
                "description": "后续单独学习 checkpointer/thread_id 与状态生命周期；当前脚本没有记忆，不把 JSON 日志当作会话记忆。",
                "from_goal_ref": "goal.basic",
            },
        ],
        "metadata": {
            "language": "zh",
            "generated_at": "2026-10-02",
            "generator": "manual-basic-prototype-v1",
            "source_ids": [item["id"] for item in SOURCES],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="Regenerate only the two named Basic fixtures."
    )
    args = parser.parse_args()
    artifact = build_artifact()
    if args.write:
        for path, data in ((ARTIFACT_PATH, artifact), (SOURCES_PATH, SOURCES)):
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(path)
    else:
        print(json.dumps(artifact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
