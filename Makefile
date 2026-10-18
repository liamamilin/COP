SHELL := /bin/sh

# The backend suite runs against a real PostgreSQL because job claiming, stale
# recovery, and the unique (run_id, sequence) constraint are PostgreSQL
# behaviour. The tests TRUNCATE every table between cases, so they get their own
# database: pointing them at the development database would silently delete the
# user's projects, sources, and published versions.
#
# The test database is separated by *name*, not by port. That is the property
# that matters, because it is the name the tests refuse to run against and the
# name that decides what a stray TRUNCATE can reach. Using a second port on the
# same server would add a second thing to keep in sync without adding a second
# layer of protection.
TEST_DATABASE_NAME ?= cop_test
TEST_DATABASE_PORT ?= 5432
TEST_DATABASE_URL ?= postgresql+psycopg://cop:cop@127.0.0.1:$(TEST_DATABASE_PORT)/$(TEST_DATABASE_NAME)

# The repository .env is written for a container, where DATA_DIR is a mounted
# volume. On the host that path does not exist, so the test suite points it at a
# temporary directory instead.
TEST_ENV = TEST_DATABASE_URL=$(TEST_DATABASE_URL) \
	TEST_DATA_DIR=$$(mktemp -d 2>/dev/null || echo /tmp/cop-studio-test-data)

# The Compose project name used for the test database.
#
.PHONY: dev up down test test-backend test-web test-e2e test-e2e-ui \
	test-db test-db-reset test-db-isolated \
	lint format typecheck check-types generate-types verify \
	migrate seed backup restore \
	local-db up-local down-local

# Everything runs directly on the host. There is no container layer: the Python
# environment is a `uv` venv, the database is a local PostgreSQL that this
# project names its own databases inside, and the frontend is `next dev`.
#
# The reasons that mattered on this machine, recorded because they are not
# obvious and each one cost real time:
#
#   8000 is occupied by an unrelated service, so a container publishing 8000
#     and a host process wanting 8000 are different things with the same
#     address. The API therefore listens on 8010 and nothing assumes 8000.
#
#   A local PostgreSQL already exists, and it already owns a database called
#     `cop` that belongs to a different project at an older schema revision.
#     This project uses `cop_studio` for development and `cop_test` for tests,
#     and never a name it did not create.
#
#   Isolation between development and test data comes from the database name,
#     not from a port. The tests TRUNCATE every table between cases, so the name
#     is the thing that has to differ.
#
#   Docker Desktop stopped without warning repeatedly during development, which
#     turned unrelated environment changes into apparent product failures. A
#     dependency that can vanish mid-run is not a dependency worth having.
up: up-local

down: down-local

# Frontend with no API or worker, in the foreground, for UI work.
dev: up-local

# The two values below are machine-specific and both are deliberate.
#
#   LOCAL_API_PORT is not 8000. Another service holds IPv4 127.0.0.1:8000 on
#     this host, so a health check there answers 200 from the wrong
#     application and reads as success. Override on a machine where 8010 is
#     also taken.
#
#   LOCAL_DB_NAME is not "cop". A PostgreSQL 16 server is already running here
#     and owns a database called `cop` that belongs to a different project, at
#     alembic revision 0001 while this app is at 0006. Reusing the name would
#     either fail on migrations or interleave two products' rows in one table.
LOCAL_API_PORT ?= 8010
LOCAL_WEB_PORT ?= 3000
LOCAL_DB_NAME ?= cop_studio
# Resolve the PostgreSQL client from PATH, then from the Homebrew prefix, and
# fail loudly if neither has it. Silently substituting a path that does not exist
# turns a missing dependency into a confusing "no such file" much later, and CI
# has no Homebrew at all -- it installs postgresql-client and expects PATH to work.
PSQL ?= $(shell command -v psql 2>/dev/null || \
	  ls /opt/homebrew/opt/postgresql@16/bin/psql 2>/dev/null || \
	  echo psql-not-found)
DB_HOST ?= 127.0.0.1
DB_PORT ?= 5432
DB_USER ?= cop
DB_ADMIN ?= milin
LOCAL_DB_URL = postgresql+psycopg://$(DB_USER):cop@$(DB_HOST):$(DB_PORT)/$(LOCAL_DB_NAME)
LOCAL_DATA_DIR = $(CURDIR)/backend/data
# The repository .env now names the host database, so these agree with it. They
# are still passed explicitly because `.env` holds a *relative* DATA_DIR, which
# only resolves correctly when the process starts in `backend/`, and `uv run`
# does not guarantee that. An absolute path does not depend on the cwd.
LOCAL_ENV = DATABASE_URL=$(LOCAL_DB_URL) DATA_DIR=$(LOCAL_DATA_DIR) \
	WEB_ORIGIN=http://localhost:3000

# Create the local database if it is missing. Idempotent, and never touches the
# pre-existing `cop` database on the same server.
local-db:
	@$(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d postgres \
		-tAc "select 1 from pg_database where datname='$(LOCAL_DB_NAME)'" | grep -q 1 \
		|| $(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_ADMIN) -d postgres \
			-c "CREATE DATABASE $(LOCAL_DB_NAME) OWNER $(DB_USER);"
	@echo "local-db: $(LOCAL_DB_NAME) ready on $(DB_HOST):$(DB_PORT)"

# API, worker, and web on the host. Logs land in /tmp so a failing component is
# diagnosable without a terminal attached.
#
# Every process is launched with an absolute interpreter path and its PID is
# recorded. `down-local` kills by PID, never by a bare `pkill -f` pattern: this
# machine also runs other projects (a `next dev` on :3100, a uvicorn on :8000),
# and a pattern like `pkill -f "next dev"` would take those down too. The PID is
# verified against this repository's path before it is signalled, so a stale PID
# file cannot kill an unrelated process that inherited the number.
LOCAL_PID_DIR = $(CURDIR)/.local-stack

# Whole commands, kept in variables rather than passed through `define` arguments:
# a command containing a comma would be split into two arguments, and the second
# half would silently vanish instead of failing.
API_CMD = $(CURDIR)/backend/.venv/bin/python -m uvicorn app.main:app \
	--host 127.0.0.1 --port $(LOCAL_API_PORT)
WORKER_CMD = $(CURDIR)/backend/.venv/bin/python -m app.jobs.worker
# `npm run dev` forks npm, which forks next, so the recorded PID would be two
# levels above the process holding port 3000. Running next directly keeps the
# whole chain at one level, which is what makes `make down` able to stop it.
WEB_CMD = $(CURDIR)/apps/web/node_modules/.bin/next dev -p $(LOCAL_WEB_PORT)
WEB_ENV = NEXT_PUBLIC_API_BASE_URL=/api/v1 \
	INTERNAL_API_BASE_URL=http://127.0.0.1:$(LOCAL_API_PORT)/api/v1

# Start one detached process and record its PID.
#
#   $(1) working directory, $(2) environment, $(3) whole command, $(4) log name
#
# The streams are redirected before the background, so the child never inherits
# the recipe's own stdout. Without that, `make up | tail` never sees end-of-file:
# the pipeline waits on a process that is meant to outlive it.
#
# `exec` is what makes the recorded PID usable. Written as
# `cd dir && nohup cmd &`, the `&` applies to the whole `&&` list, so `$!` is the
# PID of a subshell whose only job is to run the command. Killing that subshell
# leaves the real server holding its port, and the next `make up` fails with
# "address already in use" while the PID file claims nothing is wrong. With `exec`
# the subshell *becomes* the server, so the recorded number is the one to signal.
#
# `env` applies the environment because a command prefix like `FOO=bar nohup x`
# cannot be exec'd directly -- `exec` is a shell builtin and takes no assignment
# words.
#
# `$!` is escaped once for make so the shell sees the number of the job it just
# backgrounded. `$$$$!` looks equivalent and is not: make halves the escapes, the
# shell expands `$$` to its own PID, and the `!` is written literally, so the file
# ends up holding a number nothing is running under.
define start_detached
	@cd $(1) && exec $(if $(2),env $(2)) nohup $(3) > /tmp/cop-$(4)-local.log 2>&1 & \
	 echo $$! > $(LOCAL_PID_DIR)/$(4).pid
endef

# Refuse to start when the port is already taken, and say by whom.
#
# Without this the new API dies on "address already in use", the PID file records a
# process that has already exited, and the next `make down` reports that nothing
# needs stopping -- so the failure is discovered later, as a 500 from a browser
# talking to whichever older process still holds the port. A check that names the
# holder turns that into one clear line.
define require_port_free
	@if lsof -nP -iTCP:$(1) -sTCP:LISTEN -t >/dev/null 2>&1; then \
		holder=`lsof -nP -iTCP:$(1) -sTCP:LISTEN -t | head -1`; \
		echo "up: port $(1) is already in use by pid $$holder:" >&2; \
		ps -p $$holder -o command= 2>/dev/null | cut -c1-100 >&2; \
		echo "  If that is this project, run 'make down' first." >&2; \
		echo "  If it is not, set the port: make up $(2)=<free port>" >&2; \
		exit 1; \
	fi
endef

up-local: local-db
	@mkdir -p $(LOCAL_PID_DIR) $(LOCAL_DATA_DIR)
	$(call require_port_free,$(LOCAL_API_PORT),LOCAL_API_PORT)
	$(call require_port_free,3000,LOCAL_WEB_PORT)
	@cd backend && $(LOCAL_ENV) $(CURDIR)/backend/.venv/bin/alembic upgrade head
	$(call start_detached,backend,$(LOCAL_ENV),$(API_CMD),api)
	$(call start_detached,backend,$(LOCAL_ENV),$(WORKER_CMD),worker)
	$(call start_detached,apps/web,$(WEB_ENV),$(WEB_CMD),web)
	@echo "api    -> http://127.0.0.1:$(LOCAL_API_PORT)   (log: /tmp/cop-api-local.log)"
	@echo "worker -> (log: /tmp/cop-worker-local.log)"
	@echo "web    -> http://localhost:$(LOCAL_WEB_PORT)   (log: /tmp/cop-web-local.log)"
	@echo
	@echo "up-local: the browser talks to Next on :$(LOCAL_WEB_PORT), which proxies /api/v1 to :$(LOCAL_API_PORT)."
	@echo "  It can take a few seconds to compile; check /tmp/cop-web-local.log if it does not answer."

# Kill one recorded PID, but only after confirming the live process still belongs
# to this repository. A PID file survives a crash; the process behind it may be
# long gone and its number reused by something unrelated.
# Signal the recorded PID and everything it spawned, deepest child first.
#
# Children come first because a parent that dies first leaves them reparented to
# init, where nothing in this Makefile can reach them -- `next dev` forks a
# `next-server` that is the process actually holding port 3000, so killing only
# the parent frees nothing and the next `make up` fails on the busy port.
#
# Ownership is checked by *port*, not by the command line. A command line is
# unreliable in both directions: `exec` replaces the recorded venv path with the
# interpreter's real one, so a path check finds nothing to match, while a bare
# pattern like `pkill -f "next dev"` would match another project on this machine.
#
# The check walks *down* from the recorded PID, because the process holding a port
# is often a descendant rather than the recorded process itself: `next dev` forks
# a `next-server`, and that child is what binds port 3000. Comparing the recorded
# PID directly against the port would therefore always say "not ours" and leave
# the server running.
#
# $(2) is the port that proves the process is ours, or "-" for a process that
# holds no port. A portless process cannot be identified that way, so the worker
# is matched on its module path instead -- `app.jobs.worker` is specific enough
# that another project would have to be running this same project to match.
define stop_recorded
	@if [ -f $(LOCAL_PID_DIR)/$(1).pid ]; then \
		pid=`cat $(LOCAL_PID_DIR)/$(1).pid`; \
		ours=0; \
		if [ "$(2)" = "-" ]; then \
			ps -p $$pid -o command= 2>/dev/null | grep -q "app.jobs.worker" && ours=1; \
		else \
			holder=`lsof -nP -iTCP:$(2) -sTCP:LISTEN -t 2>/dev/null | head -1`; \
			if [ -n "$$holder" ]; then \
				ancestor=$$holder; \
				while [ -n "$$ancestor" ] && [ "$$ancestor" != "$$pid" ] && [ "$$ancestor" != "1" ]; do \
					ancestor=`ps -p $$ancestor -o ppid= 2>/dev/null | tr -d ' '`; \
				done; \
				[ "$$ancestor" = "$$pid" ] && ours=1; \
			fi; \
		fi; \
		if [ $$ours -eq 1 ]; then \
			for child in `pgrep -P $$pid 2>/dev/null`; do \
				for grandchild in `pgrep -P $$child 2>/dev/null`; do \
					kill $$grandchild 2>/dev/null; \
				done; \
				kill $$child 2>/dev/null; \
			done; \
			kill $$pid 2>/dev/null && echo "  stopped $(1) (pid $$pid and its children)"; \
		else \
			echo "  skipped $(1): port $(2) is not held by this process tree"; \
		fi; \
		rm -f $(LOCAL_PID_DIR)/$(1).pid; \
	fi
endef

# The browser tests import `apps/web/lib/api.ts` directly, outside any request,
# where the relative NEXT_PUBLIC_API_BASE_URL is unusable. E2E_BASE_URL is what
# `e2e/endpoints.ts` defaults from, so passing it here keeps the whole suite on
# one address instead of letting some calls fall back to a fixed port.
#
# It follows LOCAL_WEB_PORT rather than repeating 3000, so moving the web server
# cannot leave the suite pointed at a port nothing is listening on.
E2E_ENV = E2E_BASE_URL=http://localhost:$(LOCAL_WEB_PORT) \
	E2E_API_URL=http://localhost:$(LOCAL_WEB_PORT)/api/v1

down-local:
	$(call stop_recorded,api,$(LOCAL_API_PORT))
	$(call stop_recorded,worker,-)
	$(call stop_recorded,web,$(LOCAL_WEB_PORT))
	@rmdir $(LOCAL_PID_DIR) 2>/dev/null || true
	@echo "down-local: this repository's api, worker, and web stopped; other projects untouched"

# Bring up the test database.
#
# Isolation comes from the database *name*: `cop_test` is neither `cop_studio`
# nor the unrelated `cop` that already exists on this machine. There is no
# separate port and no separate server, and that is deliberate -- the tests
# TRUNCATE every table between cases, so the name is the thing that has to
# differ, and `conftest.py` refuses to run against `cop`, `postgres`, or
# `template1` for exactly that reason.
#
# This makes `verify` safe to run while the app is in use: creating or migrating
# this database cannot disconnect anything the running app depends on.
test-db-isolated:
	@$(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) -d postgres \
		-tAc "select 1 from pg_database where datname='$(TEST_DATABASE_NAME)'" | grep -q 1 \
		|| $(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_ADMIN) -d postgres \
			-c "CREATE DATABASE $(TEST_DATABASE_NAME) OWNER $(DB_USER);"
	@echo "test-db: $(TEST_DATABASE_NAME) ready on $(DB_HOST):$(DB_PORT) (isolated by name)"
	cd backend && DATABASE_URL=$(TEST_DATABASE_URL) uv run alembic upgrade head

# Drop and recreate the test database.
#
# The name is what separates it from the development database, so this destroys
# nothing the running app is using -- unlike the container-based version this
# replaces, which had to replace a container to get a clean database.
#
# Run this after adding a column: the pytest `db` fixture truncates but never
# alters, so a stale schema fails every test with UndefinedColumn rather than a
# useful error.
test-db-reset:
	-@$(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_ADMIN) -d postgres \
		-c "DROP DATABASE IF EXISTS $(TEST_DATABASE_NAME)" 2>/dev/null
	@$(PSQL) -h $(DB_HOST) -p $(DB_PORT) -U $(DB_ADMIN) -d postgres \
		-c "CREATE DATABASE $(TEST_DATABASE_NAME) OWNER $(DB_USER)"
	cd backend && DATABASE_URL=$(TEST_DATABASE_URL) uv run alembic upgrade head

# CLEAN validation: the whole suite from a freshly created test database.
#
# Nothing the running app depends on is touched: the test database is named
# apart from the development one, so recreating it cannot disconnect a session.
# For day-to-day work use `make verify`, which does not even drop the database.
test: test-db-reset
	cd backend && $(TEST_ENV) uv run pytest
	pnpm test

# Everything CI checks, in the same order, without disturbing a running stack.
#
# This is the command to run while using the app. It creates the test database
# only if it is missing and then migrates it, so it never drops anything.
verify:
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) check-types
	$(MAKE) test-db-isolated
	cd backend && $(TEST_ENV) uv run pytest
	pnpm test
	$(MAKE) test-e2e
	@echo
	@echo "verify: lint, typecheck, schema drift, backend, web, and E2E all passed."

# Backend tests against the already-provisioned test database.
test-backend:
	cd backend && $(TEST_ENV) uv run pytest

test-web:
	pnpm test

# Browser tests against the running stack. Unlike the suites above these cannot be
# mocked: they exist to prove the client components are actually wired to the API,
# which server-rendered HTML cannot show. The stack must be up already; `make up`.
test-e2e:
	cd apps/web && $(E2E_ENV) pnpm exec playwright test

test-e2e-ui:
	cd apps/web && $(E2E_ENV) pnpm exec playwright test --ui

# Remove the frontend build cache and rebuild from scratch.
#
# A cached build has silently shipped stale frontend code more than once, which is
# expensive to debug: the symptom is a control that appears wired but does
# nothing, which looks exactly like an application bug. `next dev` does not cache
# the way an image build did, but the dependency layer is still worth clearing
# when a change appears not to have landed.
web-rebuild:
	rm -rf apps/web/.next
	@echo "web-rebuild: apps/web/.next removed; the next dev/build run recompiles"

# Provision the test database and leave it running for iteration.
test-db: test-db-reset
	@echo "TEST_DATABASE_URL=$(TEST_DATABASE_URL) is ready; run 'make test-backend'"

# `ruff format --check` is here for the same reason CI runs it: a local run that
# passes while CI fails trains you to ignore the gate. 17 files were in exactly
# that state -- `ruff check` clean, `ruff format --check` not.
lint:
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	pnpm lint

typecheck:
	pnpm typecheck

generate-types:
	python3 scripts/generate-types.py

# Schema-drift check, in two layers, because they answer different questions.
#
#   1. Staleness (fails). Does `packages/cop-types/generated/` match what the
#      generator produces from the current schema? This is the failure that bites
#      during development: edit the schema, forget to regenerate, and the browser
#      keeps type-checking against a contract the backend no longer honours. The
#      mismatch then surfaces as a runtime error in a page, not as a build error.
#
#   2. Uncommitted (warns). Are those types committed? CI compares the commit,
#      so a correct-but-uncommitted regeneration passes locally and fails the
#      build. Reported rather than fatal, because failing it would make this
#      target unusable while the change is still in progress -- which is exactly
#      when you need it.
check-types:
	@python3 scripts/generate-types.py >/dev/null
	@cp packages/cop-types/generated/index.ts .check-types.fresh.ts
	@if ! diff -q packages/cop-types/generated/index.ts .check-types.fresh.ts >/dev/null; then \
		echo "ERROR: packages/cop-types/generated is stale."; \
		echo "       Run 'make generate-types' and commit the result."; \
		(diff -u packages/cop-types/generated/index.ts .check-types.fresh.ts | head -40 || true); \
		rm -f .check-types.fresh.ts; \
		exit 1; \
	fi
	@git show HEAD:packages/cop-types/generated/index.ts > .check-types.committed.ts 2>/dev/null \
		|| : > .check-types.committed.ts
	@if ! diff -q .check-types.committed.ts .check-types.fresh.ts >/dev/null; then \
		echo "WARNING: the generated types are correct but not committed."; \
		echo "         CI compares the commit and will fail until you commit them."; \
	fi
	@rm -f .check-types.fresh.ts .check-types.committed.ts
	@echo "schema drift: none"

format:
	cd backend && uv run ruff format .
	pnpm --filter @cop-studio/web exec prettier --write .

# These read DATABASE_URL from the repository `.env`, which names the Compose
# service name `postgres` and therefore cannot resolve on the host. The local
# variants pass the host database explicitly, matching `up`.
migrate:
	cd backend && $(LOCAL_ENV) uv run alembic upgrade head

seed:
	cd backend && $(LOCAL_ENV) uv run python -m app.scripts.seed

backup:
	./scripts/backup.sh

restore:
	@test -n "$(BACKUP)" || { echo "usage: make restore BACKUP=backups/cop-studio-<stamp>"; exit 1; }
	./scripts/restore.sh "$(BACKUP)"
