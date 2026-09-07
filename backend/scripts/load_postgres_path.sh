#!/usr/bin/env bash

# AlphaInvest AI
# Agrega PostgreSQL CLI al PATH de la terminal actual.
#
# Ejecutar con:
#   source scripts/load_postgres_path.sh

POSTGRES_BIN="/c/Program Files/PostgreSQL/18/bin"

if [[ ! -d "$POSTGRES_BIN" ]]; then
    echo "ERROR: No existe PostgreSQL en:"
    echo "$POSTGRES_BIN"
    echo
    echo "Busca psql.exe con:"
    echo 'find "/c/Program Files/PostgreSQL" -name psql.exe 2>/dev/null'
    return 1 2>/dev/null || exit 1
fi

export PATH="$POSTGRES_BIN:$PATH"

if ! command -v psql >/dev/null 2>&1; then
    echo "ERROR: PostgreSQL fue agregado al PATH pero psql no fue encontrado."
    return 1 2>/dev/null || exit 1
fi

echo "PostgreSQL CLI cargado correctamente"
echo "psql: $(command -v psql)"
psql --version