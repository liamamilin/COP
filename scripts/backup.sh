#!/bin/sh
# Back up the database and the data directory.
#
# Writers are stopped first so the two artefacts describe one moment. That used to
# mean `docker compose stop`, but the stack runs on the host now, and the
# equivalent is this repository's own API and worker -- not the whole machine.
# Only the PIDs recorded by `make up-local` are signalled, and only after
# confirming they still belong to this repository, so another project running
# `next dev` on this machine is never touched.
set -eu

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_dir="backups/cop-studio-${timestamp}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"

db_name="${LOCAL_DB_NAME:-cop_studio}"
db_host="${LOCAL_DB_HOST:-127.0.0.1}"
db_port="${LOCAL_DB_PORT:-5432}"
data_dir="${LOCAL_DATA_DIR:-${repo_root}/backend/data}"
psql="${PSQL_BIN:-/opt/homebrew/opt/postgresql@16/bin/psql}"
pg_dump="${PG_DUMP_BIN:-/opt/homebrew/opt/postgresql@16/bin/pg_dump}"

mkdir -p "${backup_dir}"

stop_writers() {
  # `make down` owns the lookup; see the note in restore.sh. This script only
  # needs the API and worker quiet, and stopping the web server too is harmless
  # for the length of a dump.
  ( cd "${repo_root}" && make down >/dev/null 2>&1 ) || true
}

start_writers() {
  ( cd "${repo_root}" && make up-local >/dev/null 2>&1 ) || true
}

trap start_writers EXIT INT TERM
stop_writers
# Give a closing transaction time to finish rather than dumping a half-written one.
sleep 1

"${pg_dump}" -h "${db_host}" -p "${db_port}" -U cop -d "${db_name}" \
  --clean --if-exists --no-owner --no-privileges \
  > "${backup_dir}/database.sql"

if [ -d "${data_dir}" ]; then
  tar -czf "${backup_dir}/data.tar.gz" -C "${data_dir}" .
  data_entry="data.tar.gz"
else
  data_entry=""
fi

cat > "${backup_dir}/manifest.txt" <<EOF
created_at=${timestamp}
database=database.sql
data=${data_entry}
db_name=${db_name}
EOF

trap - EXIT INT TERM
start_writers

echo "Backup created at ${backup_dir}"
