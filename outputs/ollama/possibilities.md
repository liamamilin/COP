# Ollama 可能性地图

范围：面向个人、应用开发者与自托管使用者，研究 Ollama 本地运行、模型接口与管理，以及明确注明的云服务和外部应用路线；资料实际取回于 2026-11-05。

资料截点：2026-11-05。本图有 22 项来源支持的结果，来自 19 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

core 指 Ollama 本地运行及原生支持的接口能力；extension 包含可选 Ollama 云服务、公开模型分享、独立编程代理与第三方 WebUI。支持接口不等于模型具备同样能力，所有模型与硬件条件均需满足。

## 地图导航

- [让应用取得文本、图像和结构化结果](#g-model-results)
- [复用和分享适合自己的模型](#g-custom-models)
- [把模型接入应用并管理运行边界](#g-serving)
- [按需采用远端算力和当前网页信息](#g-cloud)
- [连接工程、桌面与资料工作场景](#g-applications)

<a id="g-model-results"></a>
## 让应用取得文本、图像和结构化结果

### `p-local` 在自己机器上运行开放模型回答问题

下载兼容模型后在本地处理提示，采用自己的计算资源进行文本交互。

**内置／核心能力 · 有来源支持。** 选择 local 模型并准备足够内存和兼容硬件；云模型和额外联网工具不是离线路线。

来源：[s-readme：Ollama · Ollama；取回 Markdown第 9–9 行](https://github.com/ollama/ollama/blob/a6d33251620eef7629c73b09e672f2df243eb363/README.md#L9-L9)。

### `p-chat` 把应用接到可多轮交互的聊天模型接口

应用提交会话消息并取得下一轮助手答复，用于自建聊天或任务界面。

**内置／核心能力 · 有来源支持。** 调用者须管理消息历史和上下文；可用模型、端点认证与本地或云端路线需匹配。

来源：[s-chat：Generate a chat message · Generate a chat message；取回 Markdown第 7–7 行](https://docs.ollama.com/api/chat.md)。

### `p-vision` 围绕图片进行描述、分类和问答

给视觉模型同时提供图片与文字，获得基于图像内容的回答。

**内置／核心能力 · 有来源支持。** 需支持图像的具体模型；图片格式、显存与上下文限制需核对，识别结果需验证。

来源：[s-vision：Vision · Vision；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/vision.md)。

### `p-fields` 把文本或图像信息提取为指定字段的 JSON

用 JSON Schema 约束回复结构，便于应用读取结构化字段并继续处理。

**内置／核心能力 · 有来源支持。** 当前文档明确云端不支持 structured outputs；本地需兼容模型和 schema，结构约束不保证字段事实正确。

来源：[s-structured：Structured Outputs · Structured Outputs；取回 Markdown第 11–11 行](https://docs.ollama.com/capabilities/structured-outputs.md)。

### `p-embeddings` 为语义检索和资料问答生成文本向量

把文字转成可索引和比较的向量，交给后续语义搜索或 RAG 流程使用。

**内置／核心能力 · 有来源支持。** 需要 embedding 模型；向量库、文档导入、检索和回答流程需另行建立，索引与查询使用匹配模型。

来源：[s-embed：Embeddings · Embeddings；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/embeddings.md)。

### `p-tool-work` 让模型在任务中请求工具并利用执行结果继续回答

把工具定义提供给模型，执行应用选定的调用，再把结果送回模型形成多步交互。

**内置／核心能力 · 有来源支持。** 需支持 tool calling 的模型；实际工具执行、权限、错误处理与循环预算由应用负责。

来源：[s-tools：Tool calling · Tool calling；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/tool-calling.md)。

### `p-thinking` 把思考输出与最终答复分别呈现

对支持的模型分别读取 thinking 字段与最终回复，选择在界面显示或隐藏中间过程。

**内置／核心能力 · 有来源支持。** 只适用于支持 thinking 的模型，控制值依模型而异；该输出不是事实正确或内部机制完整可见的证明。

来源：[s-thinking：Thinking · Thinking；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/thinking.md)。

### `p-decisions` 对文本作分类、是非判断或分级评分

给决策模型输入状态与判断标准，取得类别、概率或按序标准评分，供分流和筛选工作使用。

**内置／核心能力 · 有来源支持。** 需支持 decision 的模型；Nimble 路线要求 Ollama 0.35.0+，图像决策另有模型与版本要求。模型分数并非经过校准的业务事实。

来源：[s-decision：Decision · Decision；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/decision.md)。

### `p-speech` 把文字或模型回复播放并保存为语音

用语音模型边生成边播放朗读，或把结果写成可交付的音频文件。

**内置／核心能力 · 有来源支持。** 需 Ollama 0.40.9+ 与兼容 speech 模型；当前示例 Phonon 为英语，格式、声音和参数受模型限制，不推定支持所有语言或声音克隆。

来源：[s-speech：Speech · Speech；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/speech.md)。

<a id="g-custom-models"></a>
## 复用和分享适合自己的模型

### `p-presets` 保存具有固定行为约定的命名模型配置

把系统说明、提示模板和推理参数固化为可复用模型配置，供同类任务持续调用。

**内置／核心能力 · 有来源支持。** 通过 Modelfile 创建；这是配置和封装路线，不代表已进行参数微调或改变模型权重。

来源：[s-modelfile：Modelfile Reference · Modelfile Reference；取回 Markdown第 7–7 行](https://docs.ollama.com/modelfile.md)。

### `p-import` 运行自己准备的兼容模型权重

把受支持的 Safetensors 或 GGUF 权重导入本地模型管理，再通过 Ollama 使用。

**内置／核心能力 · 有来源支持。** 架构和文件必须受支持；GGUF 导入不会自动量化，需提前用兼容工具准备。

来源：[s-import：Importing a Model · Table of Contents；取回 Markdown第 10–10 行](https://docs.ollama.com/import.md)。

### `p-share-model` 把已创建的模型发布给其他用户试用

将有权发布的模型推送到 ollama.com 命名空间，让其他人取得同一模型。

**扩展／具名实现路线 · 有来源支持。** 需账户、网络与模型再分发许可；不得推定适配权重、训练数据或上游模型均可公开。

来源：[s-import：Importing a Model · Sharing your model on ollama.com；取回 Markdown第 59–59 行](https://docs.ollama.com/import.md)。

<a id="g-serving"></a>
## 把模型接入应用并管理运行边界

### `p-compatible-clients` 让已有 OpenAI 客户端改连 Ollama 模型

调整连接目标后复用支持的客户端调用形式，减少应用迁移时重写全部接口的工作。

**内置／核心能力 · 有来源支持。** 兼容的是明确列出的 API 子集；本地与云端支持不同，不能推定有完整 Responses 状态、内置网络搜索或全部工具回放。

来源：[s-openai：OpenAI compatibility · OpenAI compatibility；取回 Markdown第 7–7 行](https://docs.ollama.com/api/openai-compatibility.md)。

### `p-concurrency` 在资源允许时为多个请求或模型提供推理

同时处理多个请求，并按可用内存加载模型或排队等待资源。

**内置／核心能力 · 有来源支持。** 需足够系统内存或显存；并发数、上下文大小和队列限制要配置，不提供固定吞吐保证。

来源：[s-faq：FAQ · How does Ollama handle concurrent requests?；取回 Markdown第 327–327 行](https://docs.ollama.com/faq.md)。

### `p-network-service` 把自己的模型服务提供给网络中的应用

配置监听与反向代理，让其他设备或应用通过网络调用同一 Ollama 服务。

**内置／核心能力 · 有来源支持。** 默认绑定回环地址；访问控制、传输保护、认证和网络边界需在部署中实现，不能按本地默认设置推定远端可安全开放。

来源：[s-faq：FAQ · How can I use Ollama with a proxy server?；取回 Markdown第 192–192 行](https://docs.ollama.com/faq.md)。

### `p-local-only` 选择关闭云功能的纯本地使用路线

禁用 Ollama 云功能并使用本地模型，避免任务误选 Ollama 云模型或其网络搜索服务。

**内置／核心能力 · 有来源支持。** 需先取得本地模型并关闭云功能；这只描述 Ollama 本身，外部插件、浏览器或模型下载的网络行为需分别核对。

来源：[s-faq：FAQ · How do I disable Ollama's cloud features?；取回 Markdown第 166–166 行](https://docs.ollama.com/faq.md)。

<a id="g-cloud"></a>
## 按需采用远端算力和当前网页信息

### `p-cloud` 在不下载大模型的情况下调用远端模型

让终端或应用使用 Ollama 云模型，把本机装不下或不想下载的模型运行交给远端服务。

**扩展／具名实现路线 · 有来源支持。** 可直接调用云 API，需账户、API key、网络和当前服务权限；费用、限额与数据处理依服务条款。

来源：[s-cloud：Cloud · Cloud；取回 Markdown第 7–7 行](https://docs.ollama.com/cloud.md)。

### `p-web-current` 给回答流程补充当前网页搜索结果

使用 Ollama Web Search API 查找网页，把取回的结果交给模型处理。

**扩展／具名实现路线 · 有来源支持。** 这是联网服务，需 Ollama 账户及 API key；本地 only 模式会禁用，搜索与生成结果仍需核查。

来源：[s-websearch：Web search · Web search；取回 Markdown第 7–7 行](https://docs.ollama.com/capabilities/web-search.md)。

<a id="g-applications"></a>
## 连接工程、桌面与资料工作场景

### `p-code-agent` 把本地或云模型接入编程代理完成工程任务

将 Ollama 提供的模型供 Claude Code、OpenCode 等代理使用，由代理读取、修改和执行工程内容。

**扩展／具名实现路线 · 有来源支持。** 能力来自另装的编程代理与工具；需兼容集成、模型能力、上下文及权限，不能归为 Ollama 自身会编辑工程。

来源：[s-integrations：Overview · Launch a coding agent；取回 Markdown第 15–15 行](https://docs.ollama.com/integrations.md)。

### `p-desktop` 在支持的桌面 AI 应用中改用 Ollama 模型

通过 Ollama 桌面集成连接已有聊天应用，在其支持的场景中使用本地或云模型。

**扩展／具名实现路线 · 有来源支持。** 当前文档路径为 macOS Apps；ChatGPT 集成限定 Codex mode，常规 Chat 和语音仍走原连接。各应用安装与功能权限需核对。

来源：[s-overview：Quickstart · Connect a desktop app；取回 Markdown第 21–21 行](https://docs.ollama.com/quickstart.md)。

### `p-document-chat` 围绕上传的资料进行带检索上下文的问答

使用 Open WebUI 将本地或远端文档检索内容加入提示，再由 Ollama 等模型生成回复。

**扩展／具名实现路线 · 有来源支持。** 另行部署 Open WebUI，配置聊天及 embedding 模型、文档索引与合适上下文；提问结果和引用需核查。

来源：[s-webui-rag：Retrieval Augmented Generation (RAG) / Open WebUI · 页面正文；本次 HTML 提取正文第 157–157 行（不是 HTML 源码行号）](https://docs.openwebui.com/features/chat-conversations/rag/)。

### `p-web-interface` 为自己的模型提供可在浏览器使用的聊天界面

部署 Open WebUI 并连接独立或打包的 Ollama 服务，让用户通过网页访问模型交互。

**扩展／具名实现路线 · 有来源支持。** 这是第三方 WebUI，不是 Ollama 原生 API 自动产生的成品；需要部署、账户与网络访问配置。

来源：[s-webui：Open WebUI · Quick Start · 页面正文；本次 HTML 提取正文第 77–77 行（不是 HTML 源码行号）](https://docs.openwebui.com/getting-started/quick-start/)。

## 资料覆盖与发现过程

结果视角读取聊天、视觉、结构化输出、向量、工具调用、thinking 与运行配置，提取可观察结果而不复述 API 参数。
示例视角核对桌面和编程代理集成、Open WebUI 完整部署及资料问答，标明真正交付界面或工程任务的是扩展组件。
扩展视角补读云模型、网络搜索、模型导入与分享；将本地、云端、第三方服务的边界写入条件。
归一化时合并不同品牌模型和多个代码代理入口；保留结构化提取、文档问答、模型发布与远端服务等不同用户结果。
补漏复查 FAQ、CLI、Linux 服务部署与 Modelfile；补漏时发现 decision 与 speech 两项新的用户结果，读取专门指南后纳入；其他下载、列举、复制和停止等步骤不单独拆成 P。相关版本限制保留在条件与缺口。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未在各操作系统、GPU、模型家族和文件格式上安装实测；速度、上下文、内存占用与工具准确率不能由功能文档推定。
- 本地与云端接口并不相同。结构化输出、Responses 状态或工具回放等须按具体端点确认。
- 未把权重微调、任意模型兼容、自动量化导入 GGUF、完全替代所有 OpenAI API 或完全离线的外部插件列为内置能力。
- 未审计所列第三方应用的数据外传、认证与多用户隔离；Ollama 本地运行的声明不能外推到整个应用栈。
- CLI 的下载、列举、复制和删除视为模型管理步骤，没有为这些微操作单独增加 P；更多集成生态仍有长尾缺口。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
