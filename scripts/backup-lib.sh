#!/usr/bin/env bash

load_env_file() {
  local env_file="$1"

  if [[ -f "${env_file}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${env_file}"
    set +a
  fi
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is required." >&2
    exit 1
  fi
}

has_container() {
  local container="$1"
  docker inspect -f '{{.State.Running}}' "${container}" >/dev/null 2>&1
}

is_running() {
  local container="$1"
  local running

  running="$(docker inspect -f '{{.State.Running}}' "${container}" 2>/dev/null || true)"
  [[ "${running}" == "true" ]]
}

dump_database() {
  local container="$1"
  local database="$2"
  local output="$3"
  local backup_dir="$4"
  local postgres_user="${POSTGRES_USER:-postgres}"

  echo "Backing up ${container}:${database} -> ${output}"
  docker exec "${container}" pg_dump -U "${postgres_user}" -d "${database}" -F c -f "/tmp/${output}"
  docker cp "${container}:/tmp/${output}" "${backup_dir}/${output}"
  docker exec "${container}" rm "/tmp/${output}"
}

dump_all_databases() {
  local container="$1"
  local output="$2"
  local backup_dir="$3"
  local postgres_user="${POSTGRES_USER:-postgres}"

  echo "Backing up ${container}:all-databases -> ${output}"
  docker exec "${container}" pg_dumpall -U "${postgres_user}" -f "/tmp/${output}"
  docker cp "${container}:/tmp/${output}" "${backup_dir}/${output}"
  docker exec "${container}" rm "/tmp/${output}"
}

backup_postgres_stack() {
  local label="$1"
  local container="$2"
  local suffix="$3"
  local backup_dir="$4"

  require_docker
  mkdir -p "${backup_dir}"

  if ! has_container "${container}"; then
    echo "Skipping ${label}: container ${container} does not exist."
    return 0
  fi

  if ! is_running "${container}"; then
    echo "Skipping ${label}: container ${container} is not running."
    return 0
  fi

  dump_database "${container}" "keycloak" "keycloak${suffix}.dump" "${backup_dir}"
  dump_database "${container}" "admin_starter" "admin_starter${suffix}.dump" "${backup_dir}"
  dump_all_databases "${container}" "all-databases${suffix}.sql" "${backup_dir}"
}

require_restore_confirmation() {
  local expected="$1"

  if [[ "${CONFIRM_RESTORE:-}" != "${expected}" ]]; then
    echo "Refusing to restore without confirmation." >&2
    echo "Run with CONFIRM_RESTORE=${expected}." >&2
    exit 1
  fi
}

restore_database() {
  local container="$1"
  local database="$2"
  local backup_file="$3"
  local postgres_user="${POSTGRES_USER:-postgres}"
  local remote_file="/tmp/restore-${database}.dump"

  require_docker

  if [[ ! -f "${backup_file}" ]]; then
    echo "Backup file does not exist: ${backup_file}" >&2
    exit 1
  fi

  if ! has_container "${container}"; then
    echo "Container ${container} does not exist." >&2
    exit 1
  fi

  if ! is_running "${container}"; then
    echo "Container ${container} is not running." >&2
    exit 1
  fi

  echo "Restoring ${backup_file} into ${container}:${database}"
  docker cp "${backup_file}" "${container}:${remote_file}"
  docker exec "${container}" dropdb -U "${postgres_user}" --if-exists "${database}"
  docker exec "${container}" createdb -U "${postgres_user}" "${database}"
  docker exec "${container}" pg_restore -U "${postgres_user}" -d "${database}" --clean --if-exists "${remote_file}"
  docker exec "${container}" rm "${remote_file}"
}
