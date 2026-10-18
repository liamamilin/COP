#!/bin/sh
# Restore a backup over the current database and data directory.
#
# Like backup, the stack runs on the host, so the services are stopped through
# this repository's own PID files. `dropdb` is used rather than a plain
# `CREATE DATABASE` because the session may still hold connections to the
# database being replaced, and a restore that half-succeeds is worse than one
# that fails loudly.
set -eu

backup_dir="${1:-}"
if [ -z "${backup_dir}" ] || [ ! -f "${backup_dir}/database.sql" ]; then
  echo "Usage: make restore BACKUP=backups/cop-studio-YYYYMMDD-HHMMSS" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

db_name="${LOCAL_DB_NAME:-cop_studio}"
db_host="${LOCAL_DB_HOST:-127.0.0.1}"
db_port="${LOCAL_DB_PORT:-5432}"
admin_db="${LOCAL_ADMIN_DB:-postgres}"
data_dir="${LOCAL_DATA_DIR:-${repo_root}/backend/data}"
psql="${PSQL_BIN:-/opt/homebrew/opt/postgresql@16/bin/psql}"
dropdb="${DROPDB_BIN:-/opt/homebrew/opt/postgresql@16/bin/dropdb}"
createdb="${CREATEDB_BIN:-/opt/homebrew/opt/postgresql@16/bin/createdb}"

# The database name comes from the manifest when present, so a backup taken
# against a different LOCAL_DB_NAME restores into the database it came from
# rather than silently overwriting the current one.
if [ -f "${backup_dir}/manifest.txt" ]; then
  recorded="$(sed -n 's/^db_name=//p' "${backup_dir}/manifest.txt" | head -1)"
  [ -n "${recorded}" ] && db_name="${recorded}"
fi

stop_services() {
  # Delegate to `make down` rather than reimplementing the lookup.
  #
  # This script used to kill by PID with a path check on the command line, which
  # silently matched nothing: `exec` rewrites the recorded venv path to the
  # interpreter's real one, so the API and the worker were never stopped, the
  # port stayed bound, and the restore "succeeded" into a stack that was not
  # running. One implementation, in the Makefile, is the only way to keep the two
  # from disagreeing.
  ( cd "${repo_root}" && make down >/dev/null 2>&1 ) || true
}

start_services() {
  # Report rather than swallow a failure. A restore that loaded correctly but left
  # the stack down looks like data loss to whoever is holding the terminal, and
  # the next thing they do is restore again.
  if ! ( cd "${repo_root}" && make up-local >/tmp/cop-restore-up.log 2>&1 ); then
    echo "restore: the data is loaded, but the stack did not come up." >&2
    echo "  See /tmp/cop-restore-up.log, then run 'make up'." >&2
    return 1
  fi
}

trap start_services EXIT INT TERM
stop_services
sleep 1

"${dropdb}" -h "${db_host}" -p "${db_port}" -U milin --if-exists --force "${db_name}"
"${createdb}" -h "${db_host}" -p "${db_port}" -U milin -O cop "${db_name}"
"${psql}" -h "${db_host}" -p "${db_port}" -U cop -d "${db_name}" \
  -v ON_ERROR_STOP=1 -q < "${backup_dir}/database.sql"

if [ -f "${backup_dir}/data.tar.gz" ]; then
  rm -rf "${data_dir}"
  mkdir -p "${data_dir}"
  tar -xzf "${backup_dir}/data.tar.gz" -C "${data_dir}"
fi

trap - EXIT INT TERM
start_services
echo "Backup restored from ${backup_dir}"
