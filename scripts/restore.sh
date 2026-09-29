#!/bin/sh
set -eu

backup_dir="${1:-}"
if [ -z "${backup_dir}" ] || [ ! -f "${backup_dir}/database.sql" ]; then
  echo "Usage: make restore BACKUP=backups/cop-studio-YYYYMMDD-HHMMSS" >&2
  exit 2
fi

restart_services() {
  docker compose up -d api worker web >/dev/null
}
trap restart_services EXIT INT TERM

# Restore replaces the current database and data volume. Keeping the API and
# worker stopped prevents a request from seeing the half-restored state.
docker compose stop api worker web >/dev/null
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U cop -d cop \
  < "${backup_dir}/database.sql"

if [ -f "${backup_dir}/data.tar.gz" ]; then
  docker compose run --rm --no-deps -T api python -c \
    'from pathlib import Path; import shutil; root=Path("/data"); [shutil.rmtree(p) if p.is_dir() else p.unlink() for p in root.iterdir()]'
  docker compose run --rm --no-deps -T api \
    sh -c 'tar -xzf - -C /data' < "${backup_dir}/data.tar.gz"
fi

trap - EXIT INT TERM
restart_services
echo "Backup restored from ${backup_dir}"
