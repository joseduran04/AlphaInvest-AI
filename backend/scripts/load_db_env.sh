#!/usr/bin/env bash

# AlphaInvest AI
# Carga exclusivamente las variables PostgreSQL necesarias
# desde backend/.env sin ejecutar el archivo como código Bash.
#
# Uso:
#   source scripts/load_db_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${BACKEND_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
    echo "ERROR: No se encontró:"
    echo "${ENV_FILE}"
    return 1 2>/dev/null || exit 1
fi

read_env_var() {
    local variable_name="$1"
    local line
    local value

    line="$(
        grep -m1 -E "^${variable_name}=" "${ENV_FILE}" 2>/dev/null || true
    )"

    if [[ -z "${line}" ]]; then
        return 1
    fi

    value="${line#*=}"

    # Eliminar CR si el archivo utiliza CRLF.
    value="${value%$'\r'}"

    # Eliminar comillas exteriores simples o dobles.
    if [[ "${value}" == \"*\" && "${value}" == *\" ]]; then
        value="${value:1:${#value}-2}"
    elif [[ "${value}" == \'*\' && "${value}" == *\' ]]; then
        value="${value:1:${#value}-2}"
    fi

    printf '%s' "${value}"
}

POSTGRES_USER="$(read_env_var POSTGRES_USER || true)"
POSTGRES_PASSWORD="$(read_env_var POSTGRES_PASSWORD || true)"
POSTGRES_PORT="$(read_env_var POSTGRES_PORT || true)"
POSTGRES_DB="$(read_env_var POSTGRES_DB || true)"

required_vars=(
    POSTGRES_USER
    POSTGRES_PASSWORD
    POSTGRES_PORT
    POSTGRES_DB
)

missing_vars=()

for var_name in "${required_vars[@]}"; do
    if [[ -z "${!var_name:-}" ]]; then
        missing_vars+=("${var_name}")
    fi
done

if (( ${#missing_vars[@]} > 0 )); then
    echo "ERROR: Faltan variables PostgreSQL en:"
    echo "${ENV_FILE}"

    for var_name in "${missing_vars[@]}"; do
        echo "  - ${var_name}"
    done

    return 1 2>/dev/null || exit 1
fi

export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_PORT
export POSTGRES_DB

# Variable reconocida por psql.
export PGPASSWORD="${POSTGRES_PASSWORD}"

# Base aislada utilizada en Fresh Install.
export FRESH_DB="alphainvest_fresh_install"

echo "AlphaInvest AI - entorno PostgreSQL cargado"
echo
echo "POSTGRES_USER=${POSTGRES_USER}"
echo "POSTGRES_PORT=${POSTGRES_PORT}"
echo "POSTGRES_DB=${POSTGRES_DB}"
echo "FRESH_DB=${FRESH_DB}"
echo
echo "PGPASSWORD configurado: SI"
echo "Contraseña mostrada: NO"