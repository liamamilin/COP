# 大模型推理（Inference） 可能性地图

范围：研究模型加载后能够交付的生成、理解、服务与运行优化结果；范围含语言/视觉语言模型和相关向量、分类、打分及 ASR 服务，采用 vLLM、llama.cpp、GuideLLM 和 vLLM-Omni 等具名路线，不包含训练。

资料截点：2026-11-05。本图有 22 项来源支持的结果，来自 17 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

推理是方法类别，所有条目以 extension 标注具名实现路线。模型、模型权重许可、硬件、服务部署和外围应用均需自行具备；同一框架也并非支持任意模型与任意功能组合。

## 地图导航

- [在可用设备和内存中运行模型](#g-runtime)
- [向应用和多个用户交付推理](#g-service)
- [取得任务需要的结构和模态结果](#g-results)
- [减少可复用计算和生成等待](#g-efficiency)
- [观察实际运行并比较部署选择](#g-evidence)

<a id="g-runtime"></a>
## 在可用设备和内存中运行模型

### `p-local` 在自己的计算环境运行语言模型生成结果

使用 llama.cpp 等运行时加载兼容权重，在本机或自管环境执行文本或视觉语言推理。

**扩展／具名实现路线 · 有来源支持。** 示范路线为 llama.cpp；需兼容模型格式和可用硬件，下载、许可证及外围工具联网行为另行核对。

来源：[s-local：llama.cpp · Description；取回 Markdown第 62–62 行](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/README.md#L62-L62)。

### `p-hybrid-memory` 把超过单独显存容量的模型分配给 CPU 与 GPU

通过混合推理部分加速更大的模型，在系统内存和显存之间做资源取舍。

**扩展／具名实现路线 · 有来源支持。** llama.cpp 的 CPU+GPU 路线；仍需足够总内存，速度与硬件、量化和分配方式有关。

来源：[s-local：llama.cpp · Description；取回 Markdown第 72–72 行](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/README.md#L72-L72)。

### `p-quantize` 用较低权重精度换取更小模型内存占用

选择受支持的量化权重或部署优化路线，使模型在不同内存预算设备上运行。

**扩展／具名实现路线 · 有来源支持。** vLLM 支持多种量化后端；格式与硬件支持需逐项核对，精度、速度和任务质量都可能变化。

来源：[s-quant：vLLM · Quantization · 页面正文；本次 HTML 提取正文第 461–461 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/quantization/)。

### `p-model-sharding` 把单设备装不下的模型分片到多卡或多节点

通过张量与流水线等并行方式分摊一个模型副本，使足够总显存参与同一模型的推理。

**扩展／具名实现路线 · 有来源支持。** vLLM Parallelism and Scaling；需匹配模型、GPU、运行时与节点网络，分片并不自动解决总内存不足。

来源：[s-parallel：vLLM · Parallelism and Scaling · 页面正文；本次 HTML 提取正文第 5–5 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/serving/parallelism_scaling/)。

<a id="g-service"></a>
## 向应用和多个用户交付推理

### `p-api` 把模型托管成应用可调用的 HTTP 服务

让多个应用通过支持的接口调用模型，而不是在各自应用中重复实现模型加载与推理。

**扩展／具名实现路线 · 有来源支持。** vLLM Online Serving；仅支持文档列出的接口和模型类型，兼容接口不等于完整复现其他云平台。

来源：[s-online：vLLM · Online Serving · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/serving/online_serving/)。

### `p-stream` 在生成完成前逐步向调用者交付文本

以流式响应发送新增生成内容，使聊天或任务界面能在最后一段生成前呈现进展。

**扩展／具名实现路线 · 有来源支持。** llama-server 文档以 SSE 流返回；客户端要处理流协议，实际首字与逐 token 延迟取决于模型及负载。

来源：[s-local-server：LLaMA.cpp HTTP Server · POST `/completion`: Given a `prompt`, it returns the predicted completion.；取回 Markdown第 617–617 行](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/tools/server/README.md#L617-L617)。

### `p-batch` 批量为一组离线输入生成结果

将多条提示交给推理引擎批处理，产出可供数据加工或离线评估使用的结果集合。

**扩展／具名实现路线 · 有来源支持。** vLLM 离线批处理路线；需准备输入、采样规则与足够资源，不等于无需维护生成内容质量。

来源：[s-batch：vLLM · Quickstart · 页面正文；本次 HTML 提取正文第 3–3 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/getting_started/quickstart/)。

### `p-multiuser` 让模型服务并发处理多个用户请求

使用并行解码和连续批处理，把多个用户的生成任务交给同一服务实例调度。

**扩展／具名实现路线 · 有来源支持。** llama-server；需规划槽位、上下文、内存和请求队列，不提供固定并发吞吐承诺。

来源：[s-local-server：LLaMA.cpp HTTP Server · LLaMA.cpp HTTP Server；取回 Markdown第 12–12 行](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/tools/server/README.md#L12-L12)。

### `p-adapters` 在同一基座服务上按请求选用任务适配器

针对不同请求加载或选择 LoRA 适配器，在共享基座上提供不同任务行为。

**扩展／具名实现路线 · 有来源支持。** vLLM 需支持 SupportsLoRA 的基座和兼容适配器；加载策略、显存、授权及版本必须验证。

来源：[s-lora：vLLM · LoRA Adapters · 页面正文；本次 HTML 提取正文第 486–486 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/lora/)。

### `p-replicas` 用多副本分担独立推理请求

把模型权重复制到不同实例或 GPU，让多个副本处理独立批次，并对在线请求进行负载分配。

**扩展／具名实现路线 · 有来源支持。** vLLM Data Parallel Deployment；需要足够副本资源与负载均衡，MoE 等配置还可能要求副本间同步。

来源：[s-replicas：vLLM · Data Parallel Deployment · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/serving/data_parallel_deployment/)。

<a id="g-results"></a>
## 取得任务需要的结构和模态结果

### `p-structured` 让生成输出符合指定结构或语法约束

在解码时使用 JSON、选择集合或语法约束，让下游应用更容易解析模型结果。

**扩展／具名实现路线 · 有来源支持。** vLLM 的 xgrammar/guidance 等后端；旧 guided_* 参数和后端可能已弃用，结构正确不代表字段内容真实。

来源：[s-structured：Structured Outputs - vLLM · 页面正文；本次 HTML 提取正文第 466–466 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/structured_outputs/)。

### `p-multimodal` 把图像、视频或音频作为模型推理输入

给支持的多模态模型提供相应媒体内容，取得模型基于这些输入生成的响应。

**扩展／具名实现路线 · 有来源支持。** vLLM 模型支持与输入格式依架构而异；需控制媒体 URL 访问、大小和资源，不能推定任意模型接受所有模态。

来源：[s-multimodal：vLLM · Multimodal Inputs · 页面正文；本次 HTML 提取正文第 508–508 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/multimodal_inputs/)。

### `p-transcribe` 把语音识别模型托管为转写接口

提供音频转写或音频翻译的服务入口，把兼容 ASR 模型结果交付给应用。

**扩展／具名实现路线 · 有来源支持。** vLLM 对应音频端点只适用于受支持 ASR 模型；语言、时长、音频质量与翻译能力需按模型验证。

来源：[s-online：vLLM · Online Serving · 页面正文；本次 HTML 提取正文第 20–20 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/serving/online_serving/)。

### `p-vectors` 为检索和相似性分析生成向量表示

使用兼容 embedding 模型把非结构化内容转成数值向量，供后续索引和比较。

**扩展／具名实现路线 · 有来源支持。** vLLM pooling 支持的模型与任务范围依实现；向量检索系统需另外构建，文档未保证优于专门框架的性能。

来源：[s-pooling：vLLM · Pooling Models · 页面正文；本次 HTML 提取正文第 590–590 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/models/pooling_models/)。

### `p-relevance` 为查询与候选内容计算相似度或相关性分数

通过打分模型计算输入对的分数，作为检索重排或匹配选择的依据。

**扩展／具名实现路线 · 有来源支持。** vLLM 支持的 cross-encoder、late-interaction 或 bi-encoder；排序逻辑、阈值和业务效果需应用验证。

来源：[s-pooling：vLLM · Pooling Models · 页面正文；本次 HTML 提取正文第 598–598 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/models/pooling_models/)。

### `p-classify` 把输入预测为预定义类别或标签

使用分类模型返回给定输入的候选类别，用于分流、筛选或信息标注。

**扩展／具名实现路线 · 有来源支持。** 这是相关 pooling/分类模型的推理，不代表所有生成式 LLM 都可用该任务接口；需标签定义与校验集。

来源：[s-pooling：vLLM · Pooling Models · 页面正文；本次 HTML 提取正文第 588–588 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/models/pooling_models/)。

### `p-tool-requests` 让应用取得模型提出的函数调用请求

把可用函数提供给兼容模型，取得结构化工具请求，再由应用决定和执行对应操作。

**扩展／具名实现路线 · 有来源支持。** llama-server 的模板与 handler 路线；模型能否正确调用、并行调用和控制参数需实测，推理引擎本身不替应用授权业务动作。

来源：[s-tools：Function Calling · Function Calling；取回 Markdown第 3–3 行](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/docs/function-calling.md#L3-L3)。

### `p-omni-output` 为能生成多模态内容的模型搭建服务运行时

采用 vLLM-Omni 等扩展承载文本、语音、图像或视频生成模型，交付对应媒体输出。

**扩展／具名实现路线 · 有来源支持。** 需单独 vLLM-Omni、受支持模型与匹配版本及资源；不是核心 vLLM 自动让任意语言模型生成媒体。

来源：[s-omni：vLLM-Omni — project README · 页面概述；取回 Markdown第 20–20 行](https://github.com/vllm-project/vllm-omni/blob/fd82f6c84a464566e1c2b3780833706208084fce/README.md#L20-L20)。

<a id="g-efficiency"></a>
## 减少可复用计算和生成等待

### `p-reuse-prefix` 避免为共享长提示反复计算相同前缀

在请求共享系统提示或资料前缀时重用 KV 缓存，减少该共享部分的重复预填充计算。

**扩展／具名实现路线 · 有来源支持。** vLLM Automatic Prefix Caching；收益依前缀命中、缓存容量、模型与负载，不能等同于所有生成步骤都被缓存。

来源：[s-prefix：Automatic Prefix Caching - vLLM · 页面正文；本次 HTML 提取正文第 465–465 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching/)。

### `p-speculate` 为适合的生成负载缩短连续输出等待

采用投机解码候选与验证机制，尝试降低中低请求负载中受内存限制时的逐 token 延迟。

**扩展／具名实现路线 · 有来源支持。** vLLM 具名方法；需兼容目标/草稿模型或提议器，收益取决于硬件与流量，不能保证更快或逐字输出完全相同。

来源：[s-speculative：Speculative Decoding¶ · 页面正文；本次 HTML 提取正文第 2–2 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/features/speculative_decoding/)。

<a id="g-evidence"></a>
## 观察实际运行并比较部署选择

### `p-monitor` 观察部署中的负载、延迟和资源相关指标

从推理服务导出可监控指标，追踪运行健康与请求表现，为容量和故障分析提供数据。

**扩展／具名实现路线 · 有来源支持。** vLLM /metrics 与相应监控系统；指标种类随版本变化，告警和归因分析须另行配置。

来源：[s-metrics：vLLM · Production Metrics · 页面正文；本次 HTML 提取正文第 470–471 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/usage/metrics/)。

### `p-benchmark` 用真实负载比较部署性能并交付测量报告

对选定输入和负载测试推理部署，取得用于选择配置的性能结果与报告。

**扩展／具名实现路线 · 有来源支持。** 文档对生产服务推荐 GuideLLM，另有 vLLM benchmark CLI；需代表性数据、硬件和配置，不能把他人基准外推到本环境。

来源：[s-benchmark：vLLM · Benchmark CLI · 页面正文；本次 HTML 提取正文第 6–6 行（不是 HTML 源码行号）](https://docs.vllm.ai/en/stable/benchmarking/cli/)。

## 资料覆盖与发现过程

从用户结果先发现本地生成、API 托管、离线加工、并发、多模态与非生成式模型服务，再观察资源和运行目标。
示例视角读取 vLLM Quickstart 的批处理与在线服务、llama-server 的多用户接口以及多模态输入示例，未把模型家族名或 API 名当作 P。
扩展视角补读低比特权重、前缀复用、投机解码、LoRA 请求、模型分片、指标、生产基准与 vLLM-Omni，明确它们不是所有推理产品通用配置。
去重时合并不同量化位宽、草稿算法、GPU 品牌与 HTTP 路由；保留模型内存约束、请求并发、结构约束和服务观测等不同结果。
补漏检查当前文档与纯跳转旧路径，另读数据并行部署；相关版本及环境差异保留在条件。后续新资料主要是同类后端和算法变体。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未实测硬件矩阵、吞吐、延迟、显存、输出质量或不同技术组合的兼容性；没有使用未经本地复现的性能数字。
- 解码约束只控制格式；量化、投机解码、前缀缓存、分片与并发调度的收益和行为必须按实际负载评估。
- 推理服务返回工具请求不等于执行工具、访问业务系统、长期保存用户记忆或自动完成 Agent 任务。
- 多模态输入与媒体生成需要不同模型和运行时；vLLM-Omni、ASR、embedding 与分类模型未被混成单一通用 LLM 能力。
- 未覆盖所有边缘设备、云平台、无服务器计费和私有加速器；版本变动与已弃用参数需以目标发行版重新核对。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
