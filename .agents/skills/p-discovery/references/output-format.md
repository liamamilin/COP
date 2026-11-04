# P Discovery output format (v0.1)

This format is optional for conversation-only answers. If the user asks the agent to save results, write **both** `possibilities.md` (human-friendly) and `possibilities.json` (machine-checkable).

The canonical JSON structure for the first experiment is intentionally small. It is **not** a C/O ontology or a process tutorial.

```json
{
  "schema_version": "0.1",
  "topic": {
    "name": "ggplot2",
    "scope": "Static data visualization in R, with clearly labeled extensions"
  },
  "sources": [
    {
      "id": "s-ggplot2",
      "title": "ggplot2 reference",
      "url": "https://ggplot2.tidyverse.org/reference/",
      "evidence": "The reference documents the plotting grammar, layers, scales, and facets."
    }
  ],
  "groups": [
    {"id": "g-relationships", "name": "表达变量关系"}
  ],
  "possibilities": [
    {
      "id": "p-scatter",
      "title": "绘制散点图",
      "result": "用点的位置展示两个变量的关系",
      "status": "source_supported",
      "availability": "core",
      "conditions": "数据中有两个合适的变量",
      "source_ids": ["s-ggplot2"],
      "group_ids": ["g-relationships"],
      "aliases": ["点图"]
    }
  ],
  "coverage_gaps": ["尚未系统调查扩展生态"],
  "generated_at": ""
}
```

## Rules

- `schema_version`: `0.1`.
- `topic`: `name` and `scope` required; source collection must respect this boundary.
- `sources`: unique IDs, `title`, `url`, and a short `evidence` summary or extract. A URL alone does not verify a claim.
- `groups`: created **after** possibilities; ID + name. Cross-group P references are okay.
- `possibilities`: unique IDs and these required fields: `title`, `result`, `status`, `availability`, `source_ids`, `group_ids`. Use a verb + observable result for the title, rather than just the name of a concept, tool, or API function. `conditions` and `aliases` are recommended.
- `status`: `proposed` (not verified), `source_supported` (verified as claimed by sources), or `reviewed` (reviewed by a human, with source evidence).
- `availability`: `core`, `extension`, or `unknown`. For extension entries, explain the package/extra requirement in `conditions`.
- `source_ids`: references must match entries in `sources`. For `source_supported` and `reviewed`, provide at least one relevant source with evidence; do not use `source_supported` for speculation.
- `group_ids`: references must match `groups`. Empty group array is allowed while reviewing.
- `coverage_gaps`: honest coverage limits; no claim of exhaustive enumeration.
- `generated_at`: optional timestamp in UTC if reliably known; otherwise omit/leave empty.

## Markdown rendering

The Markdown should begin with topic and scope, followed by grouped possibilities. Each P should include one-sentence result, core/extension badge in plain text, and a linked source. Put speculative entries in a separate `待验证` section, and add `资料覆盖与缺口` at the end.

## Quick verification (optional)

From the repository root, if local shell execution is available:

```bash
python3 .agents/skills/p-discovery/scripts/validate.py outputs/ggplot2/possibilities.json
```

This validator checks local shape, IDs, references, and statuses. It **cannot** prove that sources semantically support the claims; that still requires evidence review.
