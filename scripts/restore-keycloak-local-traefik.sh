#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
source "${SCRIPT_DIR}/backup-lib.sh"

load_env_file "${REPO_ROOT}/.env.traefik"
require_restore_confirmation "keycloak"

BACKUP_FILE="${1:-}"

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "Usage: CONFIRM_RESTORE=keycloak bash scripts/restore-keycloak-local-traefik.sh <backup-file>" >&2
  exit 1
fi

restore_database "app-traefik-postgres" "keycloak" "${BACKUP_FILE}"
