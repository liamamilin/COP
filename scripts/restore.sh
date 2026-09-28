#!/bin/sh
set -eu

backup_dir="${1:-}"
if [ -z "${backup_dir}" ] || [ ! -f "${backup_dir}/database.sql" ]; then
  echo "Usage: make restore BACKUP=backups/cop-studio-YYYYMMDD-HHMMSS" >&2
  exit 2
fi

docker compose exec -T postgres psql -U cop -d cop < "${backup_dir}/database.sql"

if [ -f "${backup_dir}/data.tar.gz" ]; then
  tar -xzf "${backup_dir}/data.tar.gz"
fi

echo "Backup restored from ${backup_dir}"
