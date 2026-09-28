# 12 — Testing Strategy

## 1. Testing pyramid

### Unit tests

Backend:

- schema validation,
- ID generation,
- reference validation,
- versioning,
- shared-foundation utility,
- source adapters,
- provider adapters with mocks.

Frontend:

- artifact selectors,
- process ordering,
- settings precedence,
- form validation,
- stage rendering.

### Integration tests

- database migrations,
- source upload → extraction,
- run creation → worker execution,
- artifact save → publish,
- draft edit → validation,
- SSE event stream,
- export generation.

### End-to-end tests

Use Playwright.

Core E2E:

```text
Open app
→ Create project
→ Paste source text
→ Configure mocked provider
→ Run generation
→ Wait for completed artifact
→ Open Goal
→ Open Stage
→ Enter Learn Mode
→ Mark Stage complete
→ Export Markdown
```

## 2. LLM tests

Never make ordinary CI depend on paid external LLM calls.

Provide:

- deterministic mock provider,
- fixture responses,
- malformed response fixtures,
- timeout fixtures,
- rate-limit fixtures.

Optional manual test suite can call live provider.

## 3. Harness step tests

Every Harness step has:

- valid input fixture,
- expected output schema,
- invalid response repair test,
- cancellation test where meaningful.

## 4. Schema tests

Validate:

- canonical sample artifact,
- missing reference rejection,
- duplicate ID rejection,
- additional optional fields accepted where intended.

## 5. Failure tests

Must include:

- bad PDF,
- unreachable URL,
- provider auth failure,
- provider rate limit,
- invalid structured output,
- worker crash,
- API restart during generation,
- cancelled generation,
- publish invalid draft,
- missing source file.

## 6. Performance tests

At minimum:

- render artifact with 200 Stages/Concept cards,
- source text with several MB,
- 1000 generation events,
- version list with 100 versions.

## 7. Accessibility tests

Use automated checks plus keyboard manual test.

## 8. Definition of done

A feature is not complete unless:

- implementation exists,
- happy-path test exists,
- important failure state exists,
- UI state exists if user-facing,
- documentation is updated.
