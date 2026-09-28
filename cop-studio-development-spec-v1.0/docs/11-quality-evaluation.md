# 11 — COP Quality and Evaluation

## 1. Goal

The Harness is successful when it produces high-value COP material consistently.

It is not successful merely because JSON validates.

## 2. Evaluation dimensions

### Goal clarity

- capability is concrete,
- outcome is verifiable,
- not just a topic label.

### Mainline visibility

- user can identify the primary route quickly,
- process is not buried under alternatives.

### Stage coherence

- each Stage has one clear local outcome,
- Stage boundaries make sense.

### Concept quality

- concepts are structural,
- not every noun is promoted,
- important repeated objects are captured.

### Operation quality

- operations are meaningful actions,
- not raw API enumeration,
- useful across implementations.

### Cognitive compression

- much lower cognitive burden than source corpus,
- no large unexplained vocabulary wall.

### Operational usability

- user can act on the process,
- implementation detail exists when required.

### Mental model value

- artifact explains why the system works,
- learner can locate where new capabilities attach.

### Source fidelity

- claims are consistent with available evidence,
- uncertainty is represented,
- unsupported specifics are avoided.

## 3. Critic rubric

Each dimension can be scored internally:

```text
0 = broken
1 = weak
2 = usable
3 = strong
```

Do not expose a fake precision “overall intelligence score” to the user.

Use the rubric for internal refinement.

## 4. Structural checks

Automated:

- IDs unique,
- references valid,
- each process points to one Goal,
- process has at least one Stage,
- Stage has local goal,
- referenced Concepts exist,
- referenced Operations exist,
- branch type valid.

## 5. Heuristic checks

Possible deterministic warnings:

- Goal title starts with “Learn/Understand” and has no concrete outcome,
- process has > 10 Stages,
- Stage has > 12 Concepts,
- artifact has many Concepts unused by any Stage,
- repeated leading Stage titles across processes not extracted,
- implementation details appear in process titles,
- no practice for priority Goal.

Warnings do not automatically fail generation.

## 6. Golden-set evaluation

Maintain a small internal benchmark:

1. LangChain Agent Development
2. ggplot2 Data Visualization
3. Git Version Control
4. Docker Application Packaging
5. A non-software domain later

Each has:

- expected Goals,
- expected core process shape,
- must-have Concepts,
- known failure patterns.

Do not require exact string match.

## 7. Human acceptance test

A reviewer should answer:

- Can I understand the domain in 5 minutes?
- Can I identify the first useful Goal?
- Can I see the process without opening every detail?
- Can I explain why each major Stage exists?
- Could I execute the minimal practice?
- After reading, can I predict where an extension belongs?

## 8. Learning validation

Optional later telemetry:

- Stage completion,
- checkpoint answer self-rating,
- practice completion,
- time per Stage,
- “I still do not understand this Stage” feedback.

This can later improve generation prompts.

## 9. Regression prevention

Every prompt or harness change must run against golden fixtures.

Store:

- generated artifact,
- validation output,
- critic report,
- model metadata.

The objective is not identical output; it is stable structural quality.
