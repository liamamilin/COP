# 大模型微调 可能性地图

范围：面向模型应用与训练工程人员，研究因果语言模型、对话模型和视觉语言模型的任务适配、偏好训练、资源受限训练、评估及部署工件；采用 TRL、PEFT、Transformers、Accelerate 等具名路线，不把全部深度学习任务泛化为 LLM 微调。

资料截点：2026-11-05。本图有 19 项来源支持的结果，来自 17 个实际取回来源。source_supported 表示资料直接声称或展示该结果；未安装实测，未由独立人工评审，未使用 reviewed 状态。

## 能力与依赖边界

本主题为方法类别，没有统一软件“内置”基线。全部 P 使用 extension 标识具名工具链路线，需对应数据、可训练权重、算力、训练脚本和评估。原文声称的性能提升未被当作普遍保证。

## 地图导航

- [形成贴合数据与任务的模型](#g-task-fit)
- [用偏好、奖励与教师反馈塑造行为](#g-feedback)
- [在资源约束下完成适配](#g-resources)
- [复用和交付可部署的适配结果](#g-artifacts)
- [评估、选择并接续训练](#g-verify)

<a id="g-task-fit"></a>
## 形成贴合数据与任务的模型

### `p-dialogue` 让语言模型适配目标任务的示范对话

用合适的问答、指令回复或对话样本进行监督适配，形成可在目标任务上评估的模型。

**扩展／具名实现路线 · 有来源支持。** 具名路线为 TRL SFTTrainer；需可训练基座、合规数据与聊天模板。训练完成不保证达到预期质量。

来源：[s-sft：Hugging Face TRL · SFTTrainer · 页面正文；本次 HTML 提取正文第 79–79 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/sft_trainer)。

### `p-domain` 让生成模型适应一类专门文本语料

在目标语料上继续训练语言建模任务，再用适配后的模型执行文本生成。

**扩展／具名实现路线 · 有来源支持。** Transformers 因果语言建模教程示范 DistilGPT2 与 ELI5；替换为大模型需核对架构、算力和训练策略。

来源：[s-causal：Causal language modeling · Hugging Face · 页面正文；本次 HTML 提取正文第 82–82 行（不是 HTML 源码行号）](https://huggingface.co/docs/transformers/en/tasks/language_modeling)。

### `p-vision` 让视觉语言模型适配图像和对话样本

用带图像的指令或对话样本训练视觉语言模型，使其针对目标视觉任务形成适配权重。

**扩展／具名实现路线 · 有来源支持。** 需受支持 VLM、image/images 样本及足够资源；截断不能误删图像 token，不能推定所有图像模型兼容。

来源：[s-sft：Hugging Face TRL · SFTTrainer · 页面正文；本次 HTML 提取正文第 253–253 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/sft_trainer)。

### `p-tools` 让模型适配带工具调用和返回结果的任务

把工具 schema、调用与响应纳入训练样本，让模型学习目标工具交互格式和任务行为。

**扩展／具名实现路线 · 有来源支持。** 需聊天模板支持工具消息；真实工具执行、鉴权和权限控制仍由运行时提供，不会由训练自动生成。

来源：[s-sft：Hugging Face TRL · SFTTrainer · 页面正文；本次 HTML 提取正文第 248–248 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/sft_trainer)。

### `p-json-catalog` 把商品标题和描述适配成目标语言结构化目录

利用完整示例，把非结构化商品信息转换成波斯语 JSON 商品目录所需的模型行为。

**扩展／具名实现路线 · 有来源支持。** Hugging Face 社区作者 Cookbook 案例，包含数据和训练流程；旧示例依赖需适配，JSON 格式和字段准确率需单独验证。

来源：[s-example：Hugging Face Cookbook · Persian product catalogs in JSON · 页面正文；本次 HTML 提取正文第 61–61 行（不是 HTML 源码行号）](https://huggingface.co/learn/cookbook/fine_tuning_llm_to_generate_persian_product_catalogs_in_json_format)。

### `p-private-code` 让代码模型适配组织自己的代码与约定

用组织允许使用的代码样本训练代码模型，使其更贴近项目的语境和内部库。

**扩展／具名实现路线 · 有来源支持。** 社区作者 Cookbook 路线；代码许可、敏感信息清理、数据拆分和记忆泄漏风险需评估。示范单卡条件不适用于任意模型规模。

来源：[s-code-example：Hugging Face Cookbook · Fine-tuning a code LLM on a single GPU · 页面正文；本次 HTML 提取正文第 62–62 行（不是 HTML 源码行号）](https://huggingface.co/learn/cookbook/fine_tuning_code_llm_on_single_gpu)。

<a id="g-feedback"></a>
## 用偏好、奖励与教师反馈塑造行为

### `p-preferences` 以偏好样本定向调整模型回答行为

提供更受欢迎和不受欢迎的回复对，让训练目标向已标注偏好倾斜。

**扩展／具名实现路线 · 有来源支持。** TRL DPO 路线，需 chosen/rejected 等成对数据与匹配基座；偏好标签质量和泛化须实测。

来源：[s-dpo：Hugging Face TRL · DPOTrainer · 页面正文；本次 HTML 提取正文第 67–67 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/dpo_trainer)。

### `p-reward-task` 训练面向可计算任务奖励的模型

把解题正确性、可执行代码或其他自定义评分转成奖励，让模型围绕该任务目标训练。

**扩展／具名实现路线 · 有来源支持。** TRL GRPO；需能可靠运行的奖励函数、生成预算和任务数据。避免把奖励得分当成真实业务效用的充分证明。

来源：[s-grpo：Hugging Face TRL · GRPOTrainer · 页面正文；本次 HTML 提取正文第 309–309 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/grpo_trainer)。

### `p-judge` 训练对候选回复进行质量评分的模型

从偏好数据训练 reward model，用于后续候选比较、筛选或训练反馈。

**扩展／具名实现路线 · 有来源支持。** TRL RewardTrainer；评分只反映训练目标与数据，不能自动认定回答真实、安全或符合用户偏好。

来源：[s-reward：Hugging Face TRL · RewardTrainer · 页面正文；本次 HTML 提取正文第 68–68 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/reward_trainer)。

### `p-distill` 把教师模型行为蒸馏到较小学生模型

利用教师反馈或分布训练较小模型，得到面向较低推理成本目标的候选学生模型。

**扩展／具名实现路线 · 有来源支持。** TRL DistillationTrainer；需教师可访问性、兼容词表或分布接口及训练预算，质量与成本变化须评估。

来源：[s-distill：Hugging Face TRL · DistillationTrainer · 页面正文；本次 HTML 提取正文第 68–68 行（不是 HTML 源码行号）](https://huggingface.co/docs/trl/en/distillation_trainer)。

<a id="g-resources"></a>
## 在资源约束下完成适配

### `p-small-adapter` 用较少可训练参数完成任务适配

冻结大部分基座参数，以较小的适配模块保存目标任务变化，减少训练和保存全部权重的需求。

**扩展／具名实现路线 · 有来源支持。** PEFT/LoRA 等具体实现；资源收益取决于基座和策略，不能保证任意模型都能在消费级硬件完成。

来源：[s-peft：PEFT · Hugging Face · 页面正文；本次 HTML 提取正文第 65–65 行（不是 HTML 源码行号）](https://huggingface.co/docs/peft/en/index)。

### `p-quantized-training` 在量化权重上继续做任务适配

把低比特基座与可训练适配器结合，开展受到显存约束的大模型任务训练。

**扩展／具名实现路线 · 有来源支持。** PEFT 与兼容量化后端，如 bitsandbytes/QLoRA；量化格式、硬件、梯度和模块支持需匹配。

来源：[s-quant：Hugging Face PEFT · Quantization · 页面正文；本次 HTML 提取正文第 70–70 行（不是 HTML 源码行号）](https://huggingface.co/docs/peft/en/developer_guides/quantization)。

### `p-multigpu` 把单机放不进一张卡的训练状态分摊到多卡

通过模型参数与优化器状态的分片，利用单节点多 GPU 完成更大模型的训练配置。

**扩展／具名实现路线 · 有来源支持。** Accelerate + FSDP 或 DeepSpeed；该对比教程限定单节点多 GPU，不能据此保证跨节点部署或线性加速。

来源：[s-multigpu：FSDP vs DeepSpeed · Hugging Face · 页面正文；本次 HTML 提取正文第 68–68 行（不是 HTML 源码行号）](https://huggingface.co/docs/accelerate/en/concept_guides/fsdp_and_deepspeed)。

<a id="g-artifacts"></a>
## 复用和交付可部署的适配结果

### `p-portable-adapter` 以较小适配器工件共享任务变化

保存适配器权重与配置，接收方可在匹配基座上重新加载，而不必分发整份基座。

**扩展／具名实现路线 · 有来源支持。** 需 PEFT checkpoint 与正确的原基座及版本；适配器许可、权重格式和再分发权限仍需核对。

来源：[s-checkpoints：Hugging Face PEFT · Checkpoint format · 页面正文；本次 HTML 提取正文第 71–71 行（不是 HTML 源码行号）](https://huggingface.co/docs/peft/en/developer_guides/checkpoint)。

### `p-merge-task-models` 组合多个适配器形成候选多任务模型

使用加权组合或 TIES、DARE 等路线融合已有适配器，并检查组合后的目标任务表现。

**扩展／具名实现路线 · 有来源支持。** PEFT 模型融合；通常需兼容基座、层和适配器格式。融合后不能保证保留所有单项能力或无需评估。

来源：[s-adapters：Model merging · Hugging Face · 页面正文；本次 HTML 提取正文第 65–65 行（不是 HTML 源码行号）](https://huggingface.co/docs/peft/en/developer_guides/model_merging)。

### `p-standalone` 导出合并权重以便独立推理部署

把兼容适配器合并回基座，得到不依赖分离适配器加载方式的模型工件。

**扩展／具名实现路线 · 有来源支持。** PEFT LoRA merge 路线；需确认适配器可合并和目标推理框架支持，量化及特殊变体可能有限制。

来源：[s-lora：Hugging Face PEFT v0.21.0 · LoRA reference · 页面正文；本次 HTML 提取正文第 335–335 行（不是 HTML 源码行号）](https://huggingface.co/docs/peft/v0.21.0/package_reference/lora)。

<a id="g-verify"></a>
## 评估、选择并接续训练

### `p-evaluate` 为适配结果计算可重复的任务指标

对模型输出与参考答案计算所选指标，形成决定是否采用微调版本的评估依据。

**扩展／具名实现路线 · 有来源支持。** Evaluate 等工具与保留测试集；指标需符合任务，不能把单一分数等同于真实用户效果或排除数据泄漏。

来源：[s-evaluate：A quick tour · Hugging Face · 页面正文；本次 HTML 提取正文第 59–59 行（不是 HTML 源码行号）](https://huggingface.co/docs/evaluate/en/a_quick_tour)。

### `p-training-selection` 按验证结果保存和选择训练检查点

在训练过程中执行验证并保留检查点，按所配置指标选出继续评估或部署的版本。

**扩展／具名实现路线 · 有来源支持。** Transformers Trainer 示例；需设置验证数据、保存策略和比较指标。最优仅指该指标与候选集合。

来源：[s-training：Fine-tuning · Hugging Face · TrainingArguments；本次 HTML 提取正文第 124–126 行（不是 HTML 源码行号）](https://huggingface.co/docs/transformers/en/training)。

### `p-resume` 从保存状态接续被打断的训练

保存并恢复模型、优化器及相关训练状态，在适当位置继续训练而非从头开始。

**扩展／具名实现路线 · 有来源支持。** Accelerate checkpointing；训练脚本需保存、恢复必要状态和数据迭代位置，环境、随机性和分布式配置仍须匹配。

来源：[s-resume：Hugging Face Accelerate · Checkpointing · 页面正文；本次 HTML 提取正文第 100–100 行（不是 HTML 源码行号）](https://huggingface.co/docs/accelerate/en/usage_guides/checkpoint)。

## 资料覆盖与发现过程

结果视角先提取目标对话/领域适配、偏好、可计算奖励、评分模型与小模型蒸馏等不同产物，而不是先按训练库的 API 分类。
示例视角读取波斯语商品 JSON 目录、私有代码适配和因果语言建模完整流程，记录数据、硬件及旧依赖限制。
扩展视角补查 PEFT、量化训练、FSDP/DeepSpeed、多模态/工具样本、适配器工件与融合，区分训练结果和部署能力。
去重时把 LoRA 变体、不同训练 CLI 和超参数写进实现条件；保留可计算奖励、较少训练参数、量化基座和工件交付等不同用户目的。
补漏追加训练选择、评估和断点恢复后，后续页面主要是同类训练/适配器变体；剩余质量、数据和兼容问题列为待验证，不以成功示例代替实测。

资料取回与未采用来源另见 [source-coverage.json](source-coverage.json)。

完整来源短摘录、取回时间、正文哈希及条目级 evidence_refs 见 [possibilities.json](possibilities.json)。候选发现顺序与取舍见 [discovery-log.md](discovery-log.md)。分组用于导航，不表示各组完全独立。

## 未解决问题与待验证内容

- 未运行大规模 GPU 训练或逐模型复现案例，不能保证训练后的准确率、风格、稳定性、推理成本或显存占用。
- 未把微调视作实时知识库更新、权限控制、可靠事实检索或自动消除幻觉的替代。
- 实际取回文档横跨多个版本；部分页面或旧 Cookbook 用不同 API，依赖、模板、量化后端与模型家族必须在项目中核对。
- 尚未深入比较所有偏好算法、在线反馈闭环、训练数据治理和跨节点容错；没有按算法变体或超参数拆分微小 P。
- 医疗、法律等领域模型即使能够训练，也未被据此确认可作实际专业决策；授权数据、隐私、基座许可和发布许可仍需独立验证。

## 校验边界

结构校验通过仅证明字段、ID、引用和摘录匹配满足现有契约；不证明运行成功、事实全面正确或效果达到特定水平。未对价格、地区可用性、插件维护、未来版本、模型准确率或生产兼容性作保证。

## 本轮审查修订

逐条补充章节和取回正文行号；HTML 行号属于本次提取正文，不是页面源码行号。GitHub 主干文件引用固定到与首次取回字节哈希一致的提交，并提供可点击的原文行链接。其他网页、Wiki 和 PR 正文仍可能编辑；取回时间与哈希仅记录本次状态。短摘录之间以 `[…]` 标记省略，完整上下文应打开来源阅读。此项核对不等于实际安装运行或独立人工评审。
