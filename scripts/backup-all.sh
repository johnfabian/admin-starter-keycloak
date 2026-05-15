#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${BACKUP_ROOT:-./backups/postgres}"
TIMESTAMP="${BACKUP_TIMESTAMP:-$(date -u +"%Y%m%dT%H%M%SZ")}"
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

mkdir -p "${BACKUP_DIR}"

bash "${SCRIPT_DIR}/backup-local-default.sh" "${BACKUP_DIR}"
bash "${SCRIPT_DIR}/backup-local-traefik.sh" "${BACKUP_DIR}"

if find "${BACKUP_DIR}" -maxdepth 1 -type f | read -r _; then
  echo
  echo "Backup complete: ${BACKUP_DIR}"
  find "${BACKUP_DIR}" -maxdepth 1 -type f -print | sort
else
  echo
  echo "No running local Postgres containers were found. No backup files were created."
  rmdir "${BACKUP_DIR}"
fi
