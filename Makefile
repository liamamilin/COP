SHELL := /bin/sh

# The backend suite runs against a real PostgreSQL because job claiming, stale
# recovery, and the unique (run_id, sequence) constraint are PostgreSQL
# behaviour. The tests TRUNCATE every table between cases, so they get their own
# database: pointing them at the development database would silently delete the
# user's projects, sources, and published versions.
# Port 5432 is often already occupied by a local PostgreSQL install, in which
# case `localhost:5432` silently reaches that server instead of the Compose
# container. The test database therefore uses its own port, and the Compose
# postgres publishes it there for the duration of the test run.
POSTGRES_HOST_PORT ?= 5432
TEST_DATABASE_NAME ?= cop_test
TEST_DATABASE_PORT ?= 55432
TEST_DATABASE_URL ?= postgresql+psycopg://cop:cop@localhost:$(TEST_DATABASE_PORT)/$(TEST_DATABASE_NAME)

# The repository .env targets Docker Compose, where DATA_DIR is the container's
# /data volume. On the host that path is absent or read-only, so the test suite
# points it at a temporary directory instead.
TEST_ENV = TEST_DATABASE_URL=$(TEST_DATABASE_URL) \
	TEST_DATA_DIR=$$(mktemp -d 2>/dev/null || echo /tmp/cop-studio-test-data)

.PHONY: dev up down test test-backend test-web test-e2e test-e2e-ui web-rebuild \
	test-db test-db-reset lint format typecheck generate-types migrate seed backup restore

dev:
	docker compose up --build

up:
	docker compose up --build -d

down:
	docker compose down

# Start the Compose postgres on the test port and create the test database.
# Uses its own port so a local PostgreSQL cannot intercept the connection.
test-db-reset:
	POSTGRES_HOST_PORT=$(TEST_DATABASE_PORT) docker compose up -d postgres
	@for attempt in $$(seq 1 30); do \
		if docker compose exec -T postgres pg_isready -U cop -d cop >/dev/null 2>&1; then break; fi; \
		sleep 1; \
	done
	@docker compose exec -T postgres psql -U cop -d postgres -tc \
		"SELECT 1 FROM pg_database WHERE datname='$(TEST_DATABASE_NAME)'" \
		| grep -q 1 \
		|| docker compose exec -T postgres createdb -U cop $(TEST_DATABASE_NAME)
	cd backend && DATABASE_URL=$(TEST_DATABASE_URL) uv run alembic upgrade head
	@echo "Test database is migrated. Run this after adding a column: the pytest" \
		"'db' fixture truncates but never alters, so a stale schema fails every" \
		"test with UndefinedColumn rather than a useful error."

# Full suite: provision the test database, run backend tests, restore the
# development port, run web tests. The development database is never touched.
test: test-db-reset
	cd backend && $(TEST_ENV) uv run pytest
	@POSTGRES_HOST_PORT=$(POSTGRES_HOST_PORT) $(MAKE) --no-print-directory down
	pnpm test

# Backend tests against the already-provisioned test database.
test-backend:
	cd backend && $(TEST_ENV) uv run pytest

test-web:
	pnpm test

# Browser tests against the running Compose stack. Unlike the suites above these
# cannot be mocked: they exist to prove the client components are actually wired
# to the API, which server-rendered HTML cannot show. The stack must be up
# already; `make up` first.
test-e2e:
	cd apps/web && pnpm exec playwright test

test-e2e-ui:
	cd apps/web && pnpm exec playwright test --ui

# Rebuild the web image from scratch. Use this after any frontend change.
#
# The cached build has silently shipped stale frontend code more than once,
# which is expensive to debug: the symptom is a control that appears wired but
# does nothing, which looks exactly like an application bug.
web-rebuild:
	docker compose build --no-cache web
	docker compose up -d web

# Provision the test database and leave it running for iteration.
test-db: test-db-reset
	@echo "TEST_DATABASE_URL=$(TEST_DATABASE_URL) is ready; run 'make test-backend'"

lint:
	cd backend && uv run ruff check .
	pnpm lint

typecheck:
	pnpm typecheck

generate-types:
	python3 scripts/generate-types.py

format:
	cd backend && uv run ruff format .
	pnpm --filter @cop-studio/web exec prettier --write .

migrate:
	cd backend && uv run alembic upgrade head

seed:
	cd backend && uv run python -m app.scripts.seed

backup:
	./scripts/backup.sh

restore:
	./scripts/restore.sh "$(BACKUP)"
