#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/backup-lib.sh"

BACKUP_DIR="${1:-${BACKUP_DIR:-./backups/postgres/$(date -u +"%Y%m%dT%H%M%SZ")}}"

backup_postgres_stack "default local stack" "app-postgres" "" "${BACKUP_DIR}"
