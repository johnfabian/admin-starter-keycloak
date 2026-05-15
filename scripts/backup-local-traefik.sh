#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/backup-lib.sh"

load_env_file "${REPO_ROOT}/.env.traefik"

BACKUP_DIR="${1:-${BACKUP_DIR:-./backups/postgres/$(date -u +"%Y%m%dT%H%M%SZ")}}"

backup_postgres_stack "local Traefik stack" "app-traefik-postgres" "-traefik" "${BACKUP_DIR}"
