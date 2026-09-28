# 22 — Repository Blueprint

## 1. Monorepo

Use `pnpm` workspaces for JavaScript packages and a separate Python backend environment.

```text
cop-studio/
├─ README.md
├─ .env.example
├─ .gitignore
├─ docker-compose.yml
├─ Makefile
├─ pnpm-workspace.yaml
├─ package.json
├─ apps/
│  └─ web/
│     ├─ app/
│     ├─ components/
│     ├─ features/
│     ├─ lib/
│     ├─ public/
│     ├─ tests/
│     └─ package.json
├─ backend/
│  ├─ app/
│  ├─ tests/
│  ├─ alembic/
│  ├─ alembic.ini
│  └─ pyproject.toml
├─ packages/
│  ├─ cop-types/
│  │  ├─ generated/
│  │  └─ package.json
│  └─ ui/
│     └─ package.json
├─ schemas/
│  ├─ cop-artifact.schema.json
│  └─ project-settings.schema.json
├─ fixtures/
│  └─ reference-langchain-cop.json
├─ scripts/
│  ├─ generate-types.*
│  ├─ seed.*
│  └─ backup.*
└─ docs/
```

## 2. Single schema source of truth

Canonical COP schema lives at:

```text
/schemas/cop-artifact.schema.json
```

Generate or maintain compatible:

- Pydantic models,
- frontend TypeScript/Zod types.

Do not hand-maintain three unrelated schemas.

Recommended approach:

1. Pydantic/domain model defines semantic validation.
2. JSON Schema is exported/checked in CI.
3. TypeScript type is generated from JSON Schema.
4. Zod is used only where runtime browser validation is needed.

If generation tooling is unreliable, keep a schema-consistency test.

## 3. Commands

Root `Makefile` or package scripts must support:

```text
make dev
make up
make down
make test
make lint
make format
make migrate
make seed
make backup
make restore
```

Equivalent documented commands are acceptable.

## 4. Docker Compose

Services:

```text
postgres
api
worker
web
```

PostgreSQL 16+.

Volumes:

```text
postgres_data
cop_data
```

## 5. Networking

Local defaults:

```text
web: 3000
api: 8000
postgres: internal / optional exposed dev port
```

Frontend calls FastAPI through configured base URL.

CORS only allows configured local frontend origin.

## 6. Environment variables

Example:

```env
APP_ENV=development
APP_SECRET=replace-me
DATABASE_URL=postgresql+psycopg://...
DATA_DIR=/data

NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

COP_PROVIDER_MODE=database
LOG_LEVEL=INFO
```

No provider API key is required when using Mock Provider.

## 7. Database seed

Seed command should:

- create sample project,
- import `reference-langchain-cop.json`,
- publish as v1,
- create no learning progress by default.

## 8. CI

Minimum pipeline:

```text
backend lint
backend tests
frontend lint
frontend unit tests
schema consistency
build frontend
Playwright with mock provider
```

## 9. Dependency policy

Prefer mature dependencies.

Avoid adding a library for trivial helpers.

Pin major versions and commit lockfiles.

## 10. Generated files

Clearly mark generated types.

CI should fail if canonical schema changed but generated types were not refreshed.
