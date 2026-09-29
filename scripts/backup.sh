#!/bin/sh
set -eu

timestamp="$(date +%Y%m%d-%H%M%S)"
backup_dir="backups/cop-studio-${timestamp}"
mkdir -p "${backup_dir}"

restart_services() {
  docker compose up -d api worker >/dev/null
}
trap restart_services EXIT INT TERM

# Stop writers so the database dump and the file volume describe one moment.
docker compose stop api worker >/dev/null
docker compose exec -T postgres pg_dump \
  --clean --if-exists --no-owner --no-privileges \
  -U cop -d cop > "${backup_dir}/database.sql"

docker compose run --rm --no-deps -T api \
  sh -c 'tar -czf - -C /data .' > "${backup_dir}/data.tar.gz"

cat > "${backup_dir}/manifest.txt" <<EOF
created_at=${timestamp}
database=database.sql
data=data.tar.gz
EOF

trap - EXIT INT TERM
restart_services

echo "Backup created at ${backup_dir}"
