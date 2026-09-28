#!/bin/sh
set -eu

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_dir="backups/cop-studio-${timestamp}"
mkdir -p "${backup_dir}"

docker compose exec -T postgres pg_dump -U cop -d cop > "${backup_dir}/database.sql"

if [ -d data ]; then
  tar -czf "${backup_dir}/data.tar.gz" data
fi

echo "Backup created at ${backup_dir}"

