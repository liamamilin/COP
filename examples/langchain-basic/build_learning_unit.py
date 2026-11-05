"""Build the content-bound teaching sidecar for the Basic prototype.

Deterministic authoring, not Harness generation or a publish. Default is a check;
--write updates only the two explicitly named learning-unit fixtures. The source
COP artifact and executable implementation are read, never rewritten.
"""

# Long Chinese teaching paragraphs remain readable as adjacent literals.
# ruff: noqa: E501

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARTIFACT_PATH = ROOT / "fixtures/langchain-basic-cop.json"
UNIT_PATH = ROOT / "fixtures/langchain-basic-learning-unit.json"
MANIFEST_PATH = ROOT / "fixtures/langchain-basic-learning-unit.manifest.json"
sys.path.insert(0, str(ROOT / "backend"))

from app.domain.learning_unit import check_learning_unit, content_hash, unit_manifest  # noqa: E402

BOTH = ["offline", "provider"]
OFFLINE = ["offline"]
PROVIDER = ["provider"]


def original_hash() -> str:
    """The repository file's bytes, not a normalized form that could hide edits."""
    return hashlib.sha256(ARTIFACT_PATH.read_bytes()).hexdigest()


def qa(identifier, kind, prompt, hints, criteria, stages, paths=BOTH):
    return {
        "id": identifier, "kind": kind, "prompt": prompt, "hints": hints,
        "criteria": criteria, "stage_refs": stages, "path_ids": paths,
    }


def unit() -> dict:
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    return {
        "schema_version": "0.1-experimental",
        "unit_id": "unit.langchain-basic.private-agent",
        "title": "从显式配置到一次可检查的 Agent 回复",
        "outcome": "在声明的起点上，完成一次无工具 Agent 文本调用，核对同一次运行的结构与语义；能解释配置和调用的因果，诊断一类常见失败，并在不重复照抄的前提下修改指令。",
        "task_brief": "你不需要先成为 LangChain 专家。本单元让你亲手建立独立运行环境、写出显式配置、装配一个无工具 Agent、调用一次、保存并检查同一次结果。离线路径能完成真实工程练习，但不等于真实模型能力；完整路径还需你自己的服务凭据、网络和费用许可。",
        "binding": {
            "artifact_sha256": content_hash(artifact),
            "goal_ref": "goal.basic",
            "process_ref": "process.basic",
        },
        "profile": {
            "audience": "已能编辑、保存文件并在终端运行 Python，但没有被要求知道 SDK 隐式配置来源的初学者。",
            "prior_knowledge": [
                "能打开终端、切换目录并读懂报错中的文件路径。",
                "能编辑纯文本文件，不会把示例值当作自己已经拥有的凭据。",
                "理解变量和函数的基本概念；不要求用过 LangChain。",
            ],
            "environment": [
                "macOS/Linux shell，Python 3.10 或更高；Windows 激活命令不在本单元已验范围内。",
                "一个由你选定、尚不存在的课件目录；不覆盖旧练习。",
                "完整路径需要你的合法服务凭据、可用网络、额度与费用许可。不要向本页面输入密钥。",
            ],
            "exclusions": [
                "不覆盖 Tools、Memory、RAG、流式、多模态或生产部署。",
                "不保证所有 OpenAI-compatible 服务兼容；构造成功不代表请求可用。",
                "本页面不会执行你看到的命令，不创建项目，不保存到项目进度。",
            ],
            "resources": [
                {
                    "id": "entry.python",
                    "name": "Python 3.10+ 与终端",
                    "provenance": "你自己的机器；不是本页面提供的托管环境。",
                    "readiness_check": "运行 python3 --version，主版本不低于 3.10。",
                    "path_ids": BOTH,
                },
                {
                    "id": "entry.network",
                    "name": "依赖下载网络",
                    "provenance": "首次安装从包索引下载；离线路径也不等于无需安装依赖。",
                    "readiness_check": "确认网络可用且允许下载固定版本；命令失败时不要用不明来源的包替换。",
                    "path_ids": BOTH,
                },
                {
                    "id": "entry.provider",
                    "name": "你的模型服务配置与费用许可",
                    "provenance": "由你向服务确认的 key、base URL、模型 ID；本课件不提供也不必收集它们。",
                    "readiness_check": "完整路径先确认服务、模型、额度、网络和本次请求可能产生的费用；离线路径只阅读配置规则，不伪造凭据，也不把 key 交给本页面或写进笔记。",
                    "path_ids": BOTH,
                },
            ],
        },
        "paths": [
            {
                "id": "offline", "label": "Offline engineering path",
                "description": "用固定本地回复检查环境、脚本、保存与验收管线。它不请求模型，也不能证明真实回复能力；要完成 Goal，之后仍需完整路径。",
                "goal_scope": "partial", "needs_network": True, "may_cost": False,
            },
            {
                "id": "provider", "label": "Full provider path",
                "description": "在显式配置和费用许可下调用一次真实服务，检查同一次回复的结构与人工语义。需要你自己的凭据，费用由你的服务决定。",
                "goal_scope": "full", "needs_network": True, "may_cost": True,
            },
        ],
        "outputs": [
            {"id": "out.requirements", "name": "requirements.txt", "description": "七个主要包的固定版本；不是传递依赖的完整 lock。", "producer_stage_ref": "stage.foundation.install", "kind": "file", "persistence": "durable", "format": "text", "content_ref": {"stage_ref": "stage.foundation.install", "detail_index": 1}, "path_ids": BOTH},
            {"id": "out.config", "name": "config.py", "description": "只从脚本旁边的命名 .env 读取 LC_*，并拒绝占位值、凭据 URL 与非本机 HTTP。", "producer_stage_ref": "stage.foundation.model", "kind": "file", "persistence": "durable", "format": "python", "content_ref": {"stage_ref": "stage.foundation.model", "detail_index": 0}, "path_ids": BOTH},
            {"id": "out.env-example", "name": ".env.example", "description": "无真实密钥的配置模板；复制成 .env 后才填写私密值。", "producer_stage_ref": "stage.foundation.model", "kind": "file", "persistence": "durable", "format": "text", "content_ref": {"stage_ref": "stage.foundation.model", "detail_index": 1}, "path_ids": BOTH},
            {"id": "out.config-summary", "name": "脱敏配置摘要", "description": "显示 key_configured、base_url、model 和 system_prompt，不显示 key 值。", "producer_stage_ref": "stage.foundation.model", "kind": "evidence", "persistence": "durable", "format": "text", "content_ref": None, "path_ids": BOTH},
            {"id": "out.agent", "name": "agent.py", "description": "在同一进程内创建、调用、检查并保存；这是要读懂并修改的主文件。", "producer_stage_ref": "stage.basic.create-agent", "kind": "file", "persistence": "durable", "format": "python", "content_ref": {"stage_ref": "stage.basic.create-agent", "detail_index": 0}, "path_ids": BOTH},
            {"id": "out.offline-run", "name": "offline-run.json", "description": "固定本地回复的两消息记录，用于验证管线，不是真实模型能力。", "producer_stage_ref": "stage.basic.invoke", "kind": "evidence", "persistence": "durable", "format": "json", "content_ref": None, "path_ids": OFFLINE},
            {"id": "out.first-run", "name": "first-run.json", "description": "一次真实服务调用的输入、human→ai 消息、answer 与脱敏配置摘要；不自动重试。", "producer_stage_ref": "stage.basic.invoke", "kind": "evidence", "persistence": "durable", "format": "json", "content_ref": None, "path_ids": PROVIDER},
            {"id": "out.inspector", "name": "inspect_result.py", "description": "只用标准库读取已有 JSON，不再调用模型，不依赖 config.py。", "producer_stage_ref": "stage.basic.inspect", "kind": "file", "persistence": "durable", "format": "python", "content_ref": {"stage_ref": "stage.basic.inspect", "detail_index": 0}, "path_ids": BOTH},
            {"id": "out.inspection", "name": "结构检查 + 人工判断记录", "description": "同一次文件的结构检查输出，以及你自己记录的语义判断和未解决项；二者不能互相替代。", "producer_stage_ref": "stage.basic.inspect", "kind": "evidence", "persistence": "durable", "format": "text", "content_ref": None, "path_ids": BOTH},
        ],
        "steps": [
            {
                "stage_ref": "stage.foundation.install",
                "purpose": "先固定“由哪个解释器、哪组包、在哪个目录运行”，再开始写调用代码，避免后面的命令落到另一个 Python 环境。",
                "inputs": [
                    {"kind": "entry", "ref": "entry.python", "why_needed": "venv 只能使用已经存在的 Python 创建，不能替代安装 Python。", "readiness_check": "在终端运行 python3 --version，确认 3.10+。", "path_ids": BOTH},
                    {"kind": "entry", "ref": "entry.network", "why_needed": "安装固定依赖需要取得包；这一步仍不调用模型。", "readiness_check": "确认包下载可用；不从未知镜像安装被替换的包。", "path_ids": BOTH},
                ],
                "concepts": [
                    {"concept_ref": "concept.foundation.install", "plain_language": "运行 Profile 是一份“这次按什么条件运行”的约定：解释器、包版本、目录和操作系统。它像实验记录里的器材与条件，不是某台机器永远正确的证书。", "concrete_example": "本单元约定 macOS/Linux、Python 3.10+、课件目录 langchain-basic-lesson 里的 .venv，以及 requirements.txt 的七个固定版本。", "contrast": "它不是“只要装过 Python 就能运行”：系统 Python、另一个项目的 venv、不同 patch 版本都可能让导入结果不同。", "why_here": "下一步的 config.py 和 agent.py 只有在同一个已激活环境中运行时，报错才指向真正的问题。"},
                ],
                "causal_chain": [
                    {"concept_ref": "concept.foundation.install", "operation_ref": "operation.foundation.install", "before": "机器上可能有多个 Python，且没有本课专用目录。", "action": "新建课件目录，用它创建 .venv，并在其中安装 requirements.txt。", "because": "venv 把解释器和 site-packages 隔离，激活后 python 解析到本课环境；固定版本让导入行为可重现。", "after": "python 的路径位于课件 .venv，导入探针输出 imports ok，后续命令使用同一解释器。"},
                ],
                "methods": [
                    {"detail_index": 0, "teaching_note": "从你的父目录执行；目录必须尚不存在，避免覆盖旧练习。若 mkdir 报已存在，先停下另选目录。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 1, "teaching_note": "完整文件内容就在来源步骤里；原样保存为 requirements.txt，不要只挑几行。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 2, "teaching_note": "只在已激活的 .venv 中安装。安装会联网下载，但不调用模型；最后两行输出用于确认解释器和导入。", "optional": False, "path_ids": BOTH},
                ],
                "output_refs": ["out.requirements"],
                "worked_case": {"kind": "illustration", "input_refs": ["entry.python", "entry.network"], "output_refs": ["out.requirements"], "walkthrough": ["在一个尚不存在的目录名外层运行 mkdir langchain-basic-lesson 并进入。", "python3 -m venv .venv 后激活；提示符出现环境提示是环境线索，不是唯一证据。", "保存完整 requirements.txt，运行 pip install 与 pip check。", "用 python -c 打印 sys.executable 并只测两个导入。"], "observation": "示例期望看到当前 .venv 的解释器路径和 imports ok；这是导入探针，不是 Agent 回复。"},
                "checks": [{"output_ref": "out.requirements", "instruction": "核对文件保存在课件目录，且 python -m pip check 无冲突、sys.executable 指向本课 .venv。", "expected": "pip check 无冲突；导入探针输出本课 .venv 路径和 imports ok。", "why": "同一解释器与可解析依赖是后续代码能够运行的前提。", "limitation": "导入成功不证明服务可连接，也不证明包的所有 API 都与旧教程一致。", "on_failure": "ModuleNotFoundError 时先查 sys.executable；若不在 .venv，重新激活。版本冲突时不要向共享环境强行升级，回到新的独立 venv。", "path_ids": BOTH}],
                "practice": qa("q.install.predict", "predict", "如果 pip install 成功了，但新开终端后直接运行 python agent.py（尚未写）出现 ModuleNotFoundError，你最应先检查什么？为什么？", ["想想 venv 是一次进程还是跨终端的持久开关。", "检查 sys.executable 与终端是否重新激活。"], ["先检查解释器路径和当前目录，而不是立刻重装未知版本。", "说明 venv 激活不跨新终端自动保留。"], ["stage.foundation.install"]),
            },
            {
                "stage_ref": "stage.foundation.model",
                "purpose": "把服务连接和系统指令变成可核对的显式输入，确保你知道 key、endpoint、model 各来自哪里，并避免私密值泄漏。",
                "inputs": [
                    {"kind": "output", "ref": "out.requirements", "why_needed": "config.py 依赖 python-dotenv；必须在已安装本课依赖的环境里运行。", "readiness_check": "上一阶段的导入探针已通过，且当前仍在课件 .venv。", "path_ids": BOTH},
                    {"kind": "entry", "ref": "entry.provider", "why_needed": "完整路径需要真实服务值；离线路径只阅读规则，不需要伪造凭据。", "readiness_check": "完整路径先确认服务、模型、额度和费用；离线路径确认自己不会把占位值当真实 key。", "path_ids": BOTH},
                ],
                "concepts": [
                    {"concept_ref": "concept.foundation.model", "plain_language": "显式配置是“把隐藏默认值搬到桌面上”：脚本明确说使用哪个 key、哪个 base URL、哪个模型和哪句系统指令，而不是等 SDK 从环境或用户目录猜。", "concrete_example": "config.py 读取脚本旁边的命名 .env，进程中的 LC_API_KEY 优先于文件；Settings.public_summary() 只输出 key_configured=true/false，不输出 key 本身。", "contrast": "“文件存在”不等于“程序读到”：COP Studio 的服务器配置、父目录 .env、OPENAI_* 都不是本课输入；空进程变量也会覆盖文件值。", "why_here": "下一步创建 Agent 时，这些 Settings 会被逐项交给模型；配置错了，调用失败或回答不符合系统指令。"},
                ],
                "causal_chain": [
                    {"concept_ref": "concept.foundation.model", "operation_ref": "operation.foundation.model", "before": "服务 key、endpoint、模型与系统指令可能散落在 SDK 默认值、shell 和文档里。", "action": "保存 config.py 和 .env.example，复制为 .env，填入自己的值，再运行 config.py。", "because": "load_settings 只读取命名文件与进程 LC_*，显式校验 URL 和占位值，返回不含 repr 泄漏 key 的 Settings。", "after": "终端显示脱敏配置摘要，后续脚本从同一个 Settings 对象取得输入。"},
                ],
                "methods": [
                    {"detail_index": 0, "teaching_note": "这是 Python 文件内容，不是 shell 命令。先读 load_settings 的输入来源和三项拒绝条件，再保存整个文件。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 1, "teaching_note": "模板中只有占位值；它本身不是有效配置，也不要改成真实 key 后提交。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 2, "teaching_note": "复制后用编辑器填写 .env；不要在终端历史、截图或本页面记录真实 key。若暂无凭据，跳过真实值填写，沿离线路径继续。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 3, "teaching_note": "没有凭据时走这里：不要伪造 key，也不要把固定回复当成服务接通证据。", "optional": True, "path_ids": OFFLINE},
                    {"detail_index": 3, "teaching_note": "有合法凭据并同意可能费用时保留；申请凭据本身不属于本单元步骤。", "optional": True, "path_ids": PROVIDER},
                ],
                "output_refs": ["out.config", "out.env-example", "out.config-summary"],
                "worked_case": {"kind": "illustration", "input_refs": ["out.requirements", "entry.provider"], "output_refs": ["out.config", "out.env-example", "out.config-summary"], "walkthrough": ["保留 config.py 原样，注意它只使用脚本旁的 .env。", "把 .env.example 复制为 .env，用编辑器替换每个占位值。", "运行 python config.py，观察摘要字段。", "假设 base URL 误填成完整 /chat/completions 地址，配置检查会报错而不是带病继续。"], "observation": "示例只展示脱敏字段；真实 key 不出现在输出中。离线路径可以只完成文件与规则阅读，真实调用留待完整路径。"},
                "checks": [
                    {"output_ref": "out.config", "instruction": "打开保存的 config.py，确认它只读取同目录命名 .env、拒绝占位值并校验 URL；不要执行未知来源的修改版。", "expected": "完整文件已保存，读取入口和拒绝条件与来源一致。", "why": "配置规则必须在你实际运行的脚本里，而不是只出现在讲解中。", "limitation": "阅读和保存不证明脚本已经运行，也不证明第三方服务接受你的 URL。", "on_failure": "若文件被截断，重新保存完整内容；不要把讲解文字拼进 Python 文件。", "path_ids": BOTH},
                    {"output_ref": "out.env-example", "instruction": "确认 .env.example 仍是模板，不含真实 key；真实值只由你写入未提交的 .env。", "expected": "模板保留占位值，没有任何私密凭据。", "why": "模板与真实配置混用会把秘密带进截图、提交或共享文件。", "limitation": "模板不包含可用的服务配置，也不能证明你有权调用某个模型。", "on_failure": "若误把真实值写进模板，撤销该值并按服务建议轮换；不要把新值贴进笔记。", "path_ids": BOTH},
                    {"output_ref": "out.config-summary", "instruction": "运行 python config.py；检查 key_configured、base_url、model、system_prompt，并确认没有 key 值。", "expected": "完整路径显示 key_configured=true 与你自己确认的 base URL、模型；离线路径在未填凭据时不应声称配置已可用。", "why": "摘要把“脚本实际采用的值”变成可观察证据，避免把某处文件存在误当作输入。", "limitation": "摘要不联网，不证明 provider 接受这组值，也不证明模型可用。", "on_failure": "Configuration error 指向缺失/占位 LC_* 值时，按名称修正 .env；若仍显示旧值，检查当前 shell 的 LC_* 覆盖并只清理当前会话变量。", "path_ids": BOTH},
                ],
                "practice": qa("q.config.explain", "explain", "为什么 config.py 不允许 base URL 带 key、query 或 /chat/completions 后缀？请分别说明它在防止什么混淆。", ["想 key 会被日志/历史怎样记录。", "想 SDK 自己会拼接请求路径。"], ["说明凭据泄漏风险与日志/截图边界。", "区分 base URL 与具体请求端点。", "提到 query 或后缀可能让拼接结果错误。"], ["stage.foundation.model"]),
            },
            {
                "stage_ref": "stage.basic.create-agent",
                "purpose": "用已核对的 Settings 在同一脚本里装配一个无工具 Agent，并区分“构造出对象”和“模型已经回复”。",
                "inputs": [
                    {"kind": "output", "ref": "out.config", "why_needed": "build_agent 明确使用 Settings 的 key、base URL、模型和 system_prompt。", "readiness_check": "config.py 已保存且导入通过；完整路径的配置摘要已核对。", "path_ids": BOTH},
                    {"kind": "output", "ref": "out.requirements", "why_needed": "create_agent 和 ChatOpenAI 来自已安装的固定依赖。", "readiness_check": "当前终端仍使用课件 .venv。", "path_ids": BOTH},
                ],
                "concepts": [
                    {"concept_ref": "concept.basic.create-agent", "plain_language": "模型是负责产生回复的部分；Agent 是把它装进可调用运行外壳的对象。本课的 create_agent 把模型、空的工具列表和系统指令装配成一张可 invoke 的图。", "concrete_example": "build_agent 先用 ChatOpenAI 显式创建模型，再 create_agent(model=model, tools=[], system_prompt=settings.system_prompt)；返回对象等待同一进程的 invoke。", "contrast": "construction-only 的 status=created 只是“装配好了”；它不是模型回答，也不证明 endpoint 可用。", "why_here": "下一步 invoke 会把消息交给这个对象；如果创建、调用分开进程，Agent 对象不会跨进程保留。"},
                ],
                "causal_chain": [
                    {"concept_ref": "concept.basic.create-agent", "operation_ref": "operation.basic.create-agent", "before": "已有显式配置和依赖，但还没有可调用的运行对象。", "action": "保存完整 agent.py，阅读 build_agent；需要时运行 --create-only 探针。", "because": "ChatOpenAI 接收显式连接参数，create_agent 把模型包装为运行图；构造阶段不发出模型请求。", "after": "你得到一个等待 invoke 的 Agent 构造路径；进程退出后对象消失，跨进程依赖必须靠文件。"},
                ],
                "methods": [
                    {"detail_index": 0, "teaching_note": "保存完整 agent.py；重点看 build_agent 的三步：显式模型、create_agent、返回。main 是同一脚本的运行外壳。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 1, "teaching_note": "这是同一文件中的原样摘录，用来读清因果；不要另存一个重复文件，也不要粘到 shell。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 2, "teaching_note": "构造探针只输出 created；它可以排除语法和导入问题，但不是回复验收。", "optional": True, "path_ids": BOTH},
                    {"detail_index": 3, "teaching_note": "只有你需要统一初始化入口时才走这条备选；它仍是同一种 Agent，不是另一套架构。", "optional": True, "path_ids": PROVIDER},
                ],
                "output_refs": ["out.agent"],
                "worked_case": {"kind": "illustration", "input_refs": ["out.config", "out.requirements"], "output_refs": ["out.agent"], "walkthrough": ["保存完整 agent.py，确认它与 config.py 同目录。", "打开 build_agent，逐项对应 Settings 的四个字段。", "可选运行 python agent.py --create-only，看到 construction-only 和 created。", "注意记录明确写着 No provider request，且对象只活在当前进程；这一步不产出回复。"], "observation": "示例的 created 不是 LLM 回复，也不是本步骤必须产出的文件；真正的调用在下一步，并需要真实配置或显式离线模式。"},
                "checks": [
                    {"output_ref": "out.agent", "instruction": "阅读 build_agent 并核对它使用 model、tools=[]、system_prompt；确认保存的是完整脚本而不是摘录。", "expected": "agent.py 完整存在，构造路径与来源一致。", "why": "下一步需要在同一脚本内实际创建并调用对象，片段无法独立运行。", "limitation": "完整文件本身不证明导入成功，也不产生回复。", "on_failure": "若只有函数摘录，回到来源步骤保存完整 agent.py；不要依赖另一个进程里的变量。", "path_ids": BOTH},
                ],
                "practice": qa("q.agent.diagnose", "diagnose", "同学说“我运行了 --create-only，打印 created，所以 Agent 已经能回复了”。请指出证据缺口，并给出一个能区分构造与调用的最小检查。", ["created 字段来自哪条分支？", "哪一步才会调用 invoke 并产生消息？"], ["指出构造阶段没有模型请求或回复。", "提出运行正常调用或离线调用并检查 mode 与 human→ai 消息。"], ["stage.basic.create-agent"]),
            },
            {
                "stage_ref": "stage.basic.invoke",
                "purpose": "让同一进程中的 Agent 接收一条消息，并把本次结果保存为可供独立检查的 JSON。",
                "inputs": [
                    {"kind": "output", "ref": "out.agent", "why_needed": "只有完整脚本能在同一进程重新创建 Agent 并调用，变量不会从上一个进程自动保留。", "readiness_check": "agent.py 已保存，构造路径无语法错误。", "path_ids": BOTH},
                    {"kind": "output", "ref": "out.config", "why_needed": "完整路径通过 Settings 提供真实连接；离线路径仍按同一脚本显式选择本地 Fake 模型。", "readiness_check": "完整路径已核对配置摘要并同意本次费用；离线路径确认命令带 --offline。", "path_ids": BOTH},
                ],
                "concepts": [
                    {"concept_ref": "concept.basic.invoke", "plain_language": "一次调用就是把一条 user 消息交给 Agent，得到一个包含 human 和 ai 角色的结果。human/ai 是消息角色，不是你代码里的变量名。", "concrete_example": "invoke_agent 传入 {\"messages\": [{\"role\": \"user\", \"content\": message}]}；本课最终保存 [human, ai] 两条消息，answer 等于最后一条 ai 文本。", "contrast": "离线模式返回固定句子，即使你换了问题也不变；它验证管线，不验证模型是否理解问题。", "why_here": "下一步只检查这次保存的文件，不再调用模型；这样查看结果不会额外收费，也不会把不同运行混在一起。"},
                ],
                "causal_chain": [
                    {"concept_ref": "concept.basic.invoke", "operation_ref": "operation.basic.invoke", "before": "已有可在本进程构造的 Agent，但还没有本次输入与回复。", "action": "运行 agent.py（离线或真实），指定问题和新的输出文件名。", "because": "invoke 把 messages 状态送入运行图；脚本用 inspect_response 检查 human→ai 和非空 answer，再以独占方式写新 JSON。", "after": "磁盘上有一份本次运行的 offline-run.json 或 first-run.json，供下一步读取。"},
                ],
                "methods": [
                    {"detail_index": 0, "teaching_note": "先走离线自检。它不读 key、不请求 provider；固定回复只证明保存与消息形状。已有同名文件会阻止运行，换新文件名而不是删旧成果。", "optional": False, "path_ids": OFFLINE},
                    {"detail_index": 1, "teaching_note": "只有完成配置、网络与预算确认后才运行。这是一次联网且可能收费的请求；失败不会自动重试，也不会写入成功报告。", "optional": False, "path_ids": PROVIDER},
                ],
                "output_refs": ["out.offline-run", "out.first-run"],
                "worked_case": {"kind": "illustration", "input_refs": ["out.agent", "out.config"], "output_refs": ["out.offline-run", "out.first-run"], "walkthrough": ["离线路径运行带 --offline 与 --output offline-run.json 的命令。", "打开文件，确认 mode=offline-fixture、input 等于问题、消息类型为 human→ai。", "完整路径先确认预算，再运行不带 --offline 的命令并保存 first-run.json。", "不为了“看清楚”再调用一次；下一步只读取已有文件。"], "observation": "离线示例的 ai 内容固定且明确标注 scripted，真实回复的措辞不应被预先编造或与示例逐字比较。"},
                "checks": [
                    {"output_ref": "out.offline-run", "instruction": "打开 offline-run.json，核对 mode、input、消息角色与固定回复说明。", "expected": "mode=offline-fixture，human→ai，input 与命令一致，ai 标注为固定回复。", "why": "它验证脚本真的把本次输入传入并保存了可检查结果，而不是只打印 created。", "limitation": "它不证明真实模型能力、provider 兼容或回答质量。", "on_failure": "回答与问题无关时，先确认自己用了 --offline；这是预期固定行为。File exists 时用新文件名，不覆盖旧记录。", "path_ids": OFFLINE},
                    {"output_ref": "out.first-run", "instruction": "打开 first-run.json，核对 mode=provider-response、input 与命令一致、两条消息 human→ai、ai 非空。", "expected": "本次真实请求成功，保存文件的结构记录本次问题与非空回复；语义判断留给下一步人工验收。", "why": "把一次真实请求与其结果绑定，避免查看结果时再次收费或混用旧文件。", "limitation": "结构正确不证明回答相关、符合系统指令，也不证明服务没有暗中替换模型。", "on_failure": "401 查 key 所属与权限；404 查 base URL 和模型 ID；429 停下确认额度与预算；网络失败没有成功记录，不能拿旧 first-run.json 冒充本次。", "path_ids": PROVIDER},
                ],
                "practice": qa("q.invoke.transfer", "transfer", "把问题改成“用一句话说明系统指令如何影响回答”。为了不重复付费，你会怎样修改命令、文件名与后续检查？", ["哪些参数决定输入？", "已有结果应该被覆盖还是保留？"], ["使用新的 --message。", "指定新的输出文件名并继续用同一检查器查看该文件。", "不为了看结果再次调用模型。"], ["stage.basic.invoke"]),
            },
            {
                "stage_ref": "stage.basic.inspect",
                "purpose": "离线读取同一次保存结果，先做结构检查，再由你判断语义是否满足任务；区分管线通过、真实能力和学习迁移。",
                "inputs": [
                    {"kind": "output", "ref": "out.agent", "why_needed": "检查器与 agent.py 同目录运行，使用本课约定的两消息 profile。", "readiness_check": "当前终端仍在课件目录，使用同一 .venv。", "path_ids": BOTH},
                    {"kind": "output", "ref": "out.offline-run", "why_needed": "离线路径检查这次固定回复文件，不生成新结果。", "readiness_check": "offline-run.json 来自上一步且未被覆盖。", "path_ids": OFFLINE},
                    {"kind": "output", "ref": "out.first-run", "why_needed": "完整路径检查本次真实回复，不再调用模型。", "readiness_check": "first-run.json 来自本次成功请求，且你仍保有原始输入与配置摘要。", "path_ids": PROVIDER},
                ],
                "concepts": [
                    {"concept_ref": "concept.basic.inspect", "plain_language": "分层验收是把不同强度的证据分开：结构一致只说明记录形状和链接正确；有效回答要看语义；能迁移要看你能不能在新条件下作出选择。", "concrete_example": "inspect_result.py 对 offline-run.json 输出 PASS，同时明说 LIVE PROVIDER AND LEARNER ACCEPTANCE: NOT VERIFIED；真实文件即使结构 PASS，仍需你判断回答是否相关且符合一短句指令。", "contrast": "点击完成、看到 PASS 或文件存在，都不等于“已经学会”；Fake 回复也不能证明真实 provider 兼容。", "why_here": "这是你的任务验收点：先确认结构，再解释结果，最后处理一个相近变化。"},
                ],
                "causal_chain": [
                    {"concept_ref": "concept.basic.inspect", "operation_ref": "operation.basic.inspect", "before": "磁盘上已有本次运行记录，但尚未核对输入、角色和回答是否属于同一次运行。", "action": "保存 inspect_result.py，读取已有 JSON，并记录结构输出与人工语义判断。", "because": "检查器只解析文件，不重新调用模型；它验证 mode、human→ai、输入一致和非空 answer，语义仍由人判断。", "after": "你得到一份结构检查记录和明确的人工结论；未满足的项保持未通过，不被点击掩盖。"},
                ],
                "methods": [
                    {"detail_index": 0, "teaching_note": "这是只用标准库的独立检查器；保存完整文件，它不会创建模型，也不会发出请求。", "optional": False, "path_ids": BOTH},
                    {"detail_index": 1, "teaching_note": "离线路径只读取上一步文件；注意 PASS 后面的 NOT VERIFIED 边界。", "optional": False, "path_ids": OFFLINE},
                    {"detail_index": 2, "teaching_note": "完整路径检查 first-run.json，然后人工判断相关性、一短句指令和是否回答了问题；不比对某个标准措辞。", "optional": False, "path_ids": PROVIDER},
                ],
                "output_refs": ["out.inspector", "out.inspection"],
                "worked_case": {"kind": "illustration", "input_refs": ["out.agent", "out.offline-run", "out.first-run"], "output_refs": ["out.inspector", "out.inspection"], "walkthrough": ["保存 inspect_result.py。", "对离线文件运行 python inspect_result.py offline-run.json。", "看到结构 PASS 时，仍记录“真实 provider 与学习者验收未验证”。", "完整路径对 first-run.json 运行同一检查器，再人工判断回复是否相关并符合系统指令。"], "observation": "示例区分“保存的调用结构正确”和“真实、相关、可迁移”三层；只有你的记录和后续变式练习能支持后两层讨论。"},
                "checks": [
                    {"output_ref": "out.inspector", "instruction": "确认 inspect_result.py 完整保存且只依赖标准库；运行前阅读它不会创建模型或调用 API。", "expected": "检查器文件完整，读取已有 JSON 而不产生新请求。", "why": "查看结果不应触发第二次付费调用，也不应依赖 provider 是否在线。", "limitation": "文件完整不代表它的检查足以判断语义或证明结果未被人工修改。", "on_failure": "若文件缺失或被截断，重新保存完整内容；不要用一个临时 shell 命令替代结构检查。", "path_ids": BOTH},
                    {"output_ref": "out.inspection", "instruction": "保留检查器完整输出，并写下：本次文件属于哪条路径、结构是否 PASS、语义是否满足、还有什么未验证。", "expected": "结构输出与文件对应；离线路径明确记录真实能力未验；完整路径的语义判断有具体依据。", "why": "把机器能检查的结构事实与需要人判断的语义结论分开，避免 PASS 被误读成全部完成。", "limitation": "检查器不判断语义、不证明文件未被手改，也不能从一次回复推断模型版本或学习迁移。", "on_failure": "FileNotFoundError 先查目录和文件名，不要临时再调用模型补结果；Inspection failed 查是否拿了 construction-only 或改坏了 input/answer；结构 PASS 但回答不相关时记录语义失败并查配置与指令。", "path_ids": BOTH},
                ],
                "practice": qa("q.inspect.explain", "explain", "inspect_result.py 对固定 Fake 回复也返回结构 PASS。这个 PASS 能支持什么结论，不能支持什么结论？", ["分别想记录形状、服务真实性和人的理解。", "固定回复是否能说明模型读过问题？"], ["说明输入/角色/answer 链接的结构结论。", "明确不能证明真实 provider、回答质量或迁移。"], ["stage.basic.inspect"]),
            },
        ],
        "assessment": [
            qa("q.a.structure", "explain", "用你自己的话解释：为什么“构造成功”“结构 PASS”“真实语义合格”是三种不同证据？各举一个本单元中的例子。", ["回看 created、inspect_result 输出和人工判断。", "每种证据分别能排除什么错误？"], ["三种证据各自的对象清楚。", "例子来自本单元，且没有把结构证据外推为学习证据。"], ["stage.basic.create-agent", "stage.basic.inspect"]),
            qa("q.a.diagnose-provider", "diagnose", "完整路径中 first-run.json 没有生成，终端显示 AuthenticationError (HTTP 401)。你会依次检查什么？哪些做法会破坏证据或泄漏秘密？", ["先区分请求未成功与检查器失败。", "想 key、服务归属和日志边界。"], ["先确认请求未成功且没有成功报告。", "检查 key 是否属于该服务且有效，不在终端/截图暴露值。", "不把旧文件或离线文件当作本次成功。"], ["stage.foundation.model", "stage.basic.invoke"], PROVIDER),
            qa("q.a.transfer-instruction", "transfer", "把系统指令从“Answer in one short sentence.”改成“用中文回答，并且只给一个具体好处”。你会修改哪里，怎样在不重复调用的情况下判断变化是否生效？", ["配置入口在哪里？", "怎样保留本次证据？"], ["指出修改 .env 的 LC_SYSTEM_PROMPT（或显式进程覆盖）。", "使用新输出文件名保存下一次运行，再用同一检查器读取。", "说明需要人工判断语义，而不是直接重跑覆盖旧结果。"], ["stage.foundation.model", "stage.basic.invoke"]),
            qa("q.a.offline-diagnose", "diagnose", "离线路径输出结构 PASS，但固定回复与你的问题无关。这是 bug 吗？你会记录什么结论？", ["回看 --offline 使用什么模型。", "PASS 检查的是结构还是语义？"], ["说明固定 Fake 回复与问题无关是预期行为。", "记录管线通过但真实能力与语义未验证。", "不通过修改问题或重跑固定回复来伪造真实能力。"], ["stage.basic.invoke", "stage.basic.inspect"], OFFLINE),
            qa("q.a.offline-boundary", "transfer", "如果只能走离线路径，你能诚实地说完成了什么、还不能说什么？请给出下一步最小行动。", ["离线路径验证了哪些管线？", "Goal 要求真实回复吗？"], ["说明环境、脚本、保存、检查结构已练过。", "不声称真实模型能力或 Goal 已完成。", "在取得合法配置和费用许可后完成一次真实调用并检查新文件。"], ["stage.basic.invoke", "stage.basic.inspect"], OFFLINE),
        ],
        "sources": [
            {"id": "src.agents", "title": "LangChain Agents（2026-11-02 核对人工摘要）", "url": "https://docs.langchain.com/oss/python/langchain/agents", "scope": "支持 create_agent 的高层入口、model/system_prompt 的角色与 invoke 接收 messages；不证明本课固定依赖 profile 在今天的版本仍兼容。"},
            {"id": "src.models", "title": "LangChain Models（人工摘要）", "url": "https://docs.langchain.com/oss/python/langchain/models", "scope": "支持直接模型类与 init_chat_model 是初始化选择，不是两种 Agent 架构。"},
            {"id": "src.openai", "title": "ChatOpenAI integration（人工摘要）", "url": "https://docs.langchain.com/oss/python/integrations/chat/openai", "scope": "支持显式 model/api_key/base_url 参数；兼容范围仍需目标服务确认。"},
            {"id": "src.env", "title": "python-dotenv（人工摘要）", "url": "https://bbc2.github.io/python-dotenv/", "scope": "支持 dotenv_values 读取指定文件而不修改进程环境；本课 LC_* 覆盖规则由 config.py 自己定义。"},
            {"id": "src.offline", "title": "本仓库 Basic 离线验收（13 项，2026-11-02 重跑）", "url": "https://github.com/", "scope": "支持脚本、框架、Fake 模型、输入匹配、脱敏和不覆盖等离线工程行为；不是 live provider 或学习者验收。"},
        ],
        "limitations": [
            "这是手工编写并绑定内容版本的教学侧车，不是自动 Harness 产物，也不证明稳定自动生成。",
            "结构检查只验证引用、路径交接、内容映射与验收覆盖；它不判断事实、方法完整性、回答语义或学习效果。",
            "来源是人工摘要，不是网页快照；当前官方文档没有认证本仓库固定依赖 profile 的所有精确版本。",
            "离线路径验证工程管线，固定回复不是 LLM 能力证据；完整路径仍取决于你的服务、网络、额度和实际结果。",
            "页面不执行命令、不自动评分、不写项目进度；本地记录是未经验证的自我报告，真实学习效果必须由独立的人实际完成、解释、排错和迁移后才能判断。",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    source_hash = original_hash()
    artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    lesson = unit()
    issues = check_learning_unit(lesson, artifact)
    if issues:
        for item in issues:
            print(f"{item['code']} {item['ref']}: {item['message']}")
        raise SystemExit(f"Learning unit has {len(issues)} contract issue(s); nothing was written.")
    manifest = unit_manifest(lesson, artifact)
    if original_hash() != source_hash or content_hash(artifact) != lesson["binding"]["artifact_sha256"]:
        raise SystemExit("The source artifact changed during authoring; refusing to write.")
    if args.write:
        UNIT_PATH.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Learning unit valid; {len(issues)} issues. " + ("Wrote the two learning-unit fixtures." if args.write else "Check only."))


if __name__ == "__main__":
    main()
