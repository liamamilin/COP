# 09 — Settings

## 1. Settings philosophy

The product should work with sensible defaults.

Advanced settings exist, but the user should not need to configure every internal detail.

## 2. Settings levels

### App settings

Global defaults.

### Project settings

Override app defaults for one COP project.

### Run settings

Temporary override for one generation.

Precedence:

```text
Run > Project > App > Built-in default
```

## 3. AI provider settings

Fields:

- provider type,
- base URL,
- API key,
- model,
- optional reasoning/effort setting,
- request timeout,
- max retries.

OpenAI-compatible configuration:

```text
Provider: OpenAI Compatible
Base URL: https://...
API Key: ********
Model: ...
```

Include **Test Connection**.

## 4. API key storage

Never store plaintext keys in logs.

For local V1:

- encrypt API key using application secret,
- store ciphertext in database,
- allow environment-variable provider configuration as alternative.

## 5. COP generation defaults

### Language

- Auto
- Chinese
- English
- other explicit language string

### Depth

- Fast
- Standard
- Deep

### Learner level

- New to domain
- Some experience
- Advanced

### Detail density

- Compact
- Balanced
- Detailed

### Practices

- Off
- Priority processes
- All main processes

### Evidence density

- Minimal
- Key claims
- High

## 6. Structural defaults

Recommended defaults:

```text
Goals: 3–7
Stages per process: 3–8
Priority practices: enabled
Shared foundation extraction: enabled
Branch extraction: enabled
Implementation detail: collapsed
```

These are soft targets, not hard generation limits.

## 7. Review settings

- critic pass: on/off,
- max repair attempts,
- auto-run refinement after major critic issue,
- publish automatically: **off** by default.

V1 should not auto-publish over user work.

## 8. Source settings

- max upload size,
- URL timeout,
- allow remote URL fetching,
- PDF extraction mode,
- retain original uploads.

## 9. Learning settings

- default to Learn Mode after publish: off,
- show checkpoints: on,
- show implementation detail automatically: off,
- stage completion requires confirmation: on.

## 10. Appearance

- System
- Light
- Dark

Density:

- Comfortable
- Compact

## 11. Data settings

- local data directory,
- export directory,
- delete cached extracted text,
- clear generation logs.

## 12. Dangerous actions

Separated section:

- delete project,
- delete all local data,
- reset settings.

Require explicit confirmation.

## 13. Settings portability

Allow export/import of non-secret settings JSON.

Never include API keys in exported settings by default.
