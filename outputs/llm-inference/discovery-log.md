# 大模型推理（Inference） 发现记录

先建立无分类候选清单；从可得结果、完整示例、可选扩展三个视角提取；核对周边上下文后去重和归一化，最后才建立用途导航。以下顺序保留实际候选记录，不按最终分组排序。

1. `p-local`｜结果视角｜在自己的计算环境运行语言模型生成结果｜s-local
2. `p-hybrid-memory`｜结果视角｜把超过单独显存容量的模型分配给 CPU 与 GPU｜s-local
3. `p-api`｜结果视角｜把模型托管成应用可调用的 HTTP 服务｜s-online
4. `p-stream`｜结果视角｜在生成完成前逐步向调用者交付文本｜s-local-server
5. `p-batch`｜示例视角｜批量为一组离线输入生成结果｜s-batch
6. `p-multiuser`｜结果视角｜让模型服务并发处理多个用户请求｜s-local-server
7. `p-quantize`｜结果视角｜用较低权重精度换取更小模型内存占用｜s-quant
8. `p-reuse-prefix`｜结果视角｜避免为共享长提示反复计算相同前缀｜s-prefix
9. `p-speculate`｜结果视角｜为适合的生成负载缩短连续输出等待｜s-speculative
10. `p-model-sharding`｜结果视角｜把单设备装不下的模型分片到多卡或多节点｜s-parallel
11. `p-adapters`｜扩展视角｜在同一基座服务上按请求选用任务适配器｜s-lora
12. `p-structured`｜结果视角｜让生成输出符合指定结构或语法约束｜s-structured
13. `p-multimodal`｜扩展视角｜把图像、视频或音频作为模型推理输入｜s-multimodal
14. `p-transcribe`｜扩展视角｜把语音识别模型托管为转写接口｜s-online
15. `p-vectors`｜结果视角｜为检索和相似性分析生成向量表示｜s-pooling
16. `p-relevance`｜结果视角｜为查询与候选内容计算相似度或相关性分数｜s-pooling
17. `p-classify`｜结果视角｜把输入预测为预定义类别或标签｜s-pooling
18. `p-tool-requests`｜扩展视角｜让应用取得模型提出的函数调用请求｜s-tools
19. `p-monitor`｜结果视角｜观察部署中的负载、延迟和资源相关指标｜s-metrics
20. `p-benchmark`｜扩展视角｜用真实负载比较部署性能并交付测量报告｜s-benchmark
21. `p-omni-output`｜扩展视角｜为能生成多模态内容的模型搭建服务运行时｜s-omni
22. `p-replicas`｜补漏视角｜用多副本分担独立推理请求｜s-replicas

## 归一化、补漏与停止依据

从用户结果先发现本地生成、API 托管、离线加工、并发、多模态与非生成式模型服务，再观察资源和运行目标。
示例视角读取 vLLM Quickstart 的批处理与在线服务、llama-server 的多用户接口以及多模态输入示例，未把模型家族名或 API 名当作 P。
扩展视角补读低比特权重、前缀复用、投机解码、LoRA 请求、模型分片、指标、生产基准与 vLLM-Omni，明确它们不是所有推理产品通用配置。
去重时合并不同量化位宽、草稿算法、GPU 品牌与 HTTP 路由；保留模型内存约束、请求并发、结构约束和服务观测等不同结果。
补漏检查当前文档与纯跳转旧路径，另读数据并行部署；相关版本及环境差异保留在条件。后续新资料主要是同类后端和算法变体。

## 保留的未知项

- 未实测硬件矩阵、吞吐、延迟、显存、输出质量或不同技术组合的兼容性；没有使用未经本地复现的性能数字。
- 解码约束只控制格式；量化、投机解码、前缀缓存、分片与并发调度的收益和行为必须按实际负载评估。
- 推理服务返回工具请求不等于执行工具、访问业务系统、长期保存用户记忆或自动完成 Agent 任务。
- 多模态输入与媒体生成需要不同模型和运行时；vLLM-Omni、ASR、embedding 与分类模型未被混成单一通用 LLM 能力。
- 未覆盖所有边缘设备、云平台、无服务器计费和私有加速器；版本变动与已弃用参数需以目标发行版重新核对。

## 实际资料取回清单

下表只记录取回情况。确认依据以 possibilities.json 为准；未采用页不代表新增能力。完整请求、最终地址、时间、哈希和失败尝试见 [source-coverage.json](source-coverage.json)。

| 来源 | 取回时间（UTC） | 用于确认条目 |
| --- | --- | --- |
| [s-batch](https://docs.vllm.ai/en/stable/getting_started/quickstart/) | 2026-11-05T09:11:35.945477+00:00 | 是 |
| [s-benchmark](https://docs.vllm.ai/en/stable/benchmarking/cli/) | 2026-11-05T09:11:36.127162+00:00 | 是 |
| [s-local-server](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/tools/server/README.md) | 2026-11-05T08:49:54.613337+00:00 | 是 |
| [s-local](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/README.md) | 2026-11-05T08:49:53.120884+00:00 | 是 |
| [s-lora](https://docs.vllm.ai/en/stable/features/lora/) | 2026-11-05T08:49:51.376721+00:00 | 是 |
| [s-metrics](https://docs.vllm.ai/en/stable/usage/metrics/) | 2026-11-05T08:49:53.861441+00:00 | 是 |
| [s-multimodal](https://docs.vllm.ai/en/stable/features/multimodal_inputs/) | 2026-11-05T08:49:53.633783+00:00 | 是 |
| [s-omni](https://github.com/vllm-project/vllm-omni/blob/fd82f6c84a464566e1c2b3780833706208084fce/README.md) | 2026-11-05T09:11:35.266234+00:00 | 是 |
| [s-online](https://docs.vllm.ai/en/stable/serving/online_serving/) | 2026-11-05T09:06:13.352374+00:00 | 是 |
| [s-overview](https://docs.vllm.ai/en/stable/) | 2026-11-05T08:49:51.246874+00:00 | 否 |
| [s-parallel](https://docs.vllm.ai/en/stable/serving/parallelism_scaling/) | 2026-11-05T09:11:35.874645+00:00 | 是 |
| [s-pooling](https://docs.vllm.ai/en/stable/models/pooling_models/) | 2026-11-05T08:49:53.658450+00:00 | 是 |
| [s-prefix](https://docs.vllm.ai/en/stable/features/automatic_prefix_caching/) | 2026-11-05T08:49:51.432952+00:00 | 是 |
| [s-quant](https://docs.vllm.ai/en/stable/features/quantization/) | 2026-11-05T08:49:52.742526+00:00 | 是 |
| [s-replicas](https://docs.vllm.ai/en/stable/serving/data_parallel_deployment/) | 2026-11-05T09:19:52.879324+00:00 | 是 |
| [s-server](https://docs.vllm.ai/en/stable/serving/openai_compatible_server/) | 2026-11-05T08:49:50.979167+00:00 | 否 |
| [s-speculate](https://docs.vllm.ai/en/stable/features/spec_decode/) | 2026-11-05T08:49:50.601775+00:00 | 否 |
| [s-speculative](https://docs.vllm.ai/en/stable/features/speculative_decoding/) | 2026-11-05T09:06:13.230774+00:00 | 是 |
| [s-structured](https://docs.vllm.ai/en/stable/features/structured_outputs/) | 2026-11-05T08:49:51.545868+00:00 | 是 |
| [s-tools](https://github.com/ggml-org/llama.cpp/blob/c55b094880bb70dacac0b50c6653790650e8dd2d/docs/function-calling.md) | 2026-11-05T09:11:35.255844+00:00 | 是 |

未取得正文的清单保留于 source-coverage.json；不据这些页面确认能力。

## 本轮审查修订（保留以上原始候选记录）

本主题修订了以下条目的摘录或结果边界：无额外措辞修订。所有条目均补上实际章节与正文行号；GitHub 主干文件固定提交并核对哈希。未将程序匹配称为语义或运行认证。
