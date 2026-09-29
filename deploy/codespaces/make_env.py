"""Genera el archivo de variables para el contenedor a partir de backend/.env.

Aplica los ajustes de producción (sin debug, CORS limitado a la URL pública)
y escribe KEY=VALUE sin comillas, como lo espera `docker run --env-file`.
Nunca imprime valores en pantalla; solo avisos.

Uso (lo llama levantar.sh):
    python3 deploy/codespaces/make_env.py --url https://... --output /tmp/alphainvest.env
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / "backend" / ".env"

# Variables que el contenedor no debe heredar del .env local.
SKIPPED_KEYS = {
    "APP_WORKER_ENABLED",  # lo fija start.sh por proceso
    "APP_WORKER_RUN_ONCE",
    "APP_DATABASE_SSL_CA_FILE",
}


def read_env(path: Path) -> dict[str, str]:
    """Lee KEY=VALUE; ignora comentarios. La última definición gana."""
    values: dict[str, str] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]

        values[key] = value

    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL pública de la app")
    parser.add_argument("--output", required=True, help="Archivo a generar")
    args = parser.parse_args()

    if not ENV_FILE.is_file():
        print("No encontré backend/.env", file=sys.stderr)
        return 1

    env = {
        key: value
        for key, value in read_env(ENV_FILE).items()
        if key.startswith("APP_") and value != "" and key not in SKIPPED_KEYS
    }

    env["APP_ENV"] = "production"
    env["APP_DEBUG"] = "false"
    env["APP_CORS_ORIGINS"] = json.dumps([args.url])

    if env.get("APP_DATABASE_SSL_MODE", "disable") == "disable":
        env["APP_DATABASE_SSL_MODE"] = "require"
        print("Nota: APP_DATABASE_SSL_MODE se fijó en 'require'.", file=sys.stderr)

    if len(env.get("APP_JWT_SECRET_KEY", "")) < 32:
        env["APP_JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
        print(
            "Nota: APP_JWT_SECRET_KEY era corta; se generó una nueva para la nube.",
            file=sys.stderr,
        )

    mongo_uri = env.get("APP_MONGODB_URI", "")

    if "localhost" in mongo_uri or "mongodb://mongo:" in mongo_uri:
        print(
            "APP_MONGODB_URI apunta a un Mongo local; pon la URI de MongoDB Atlas "
            "en backend/.env.",
            file=sys.stderr,
        )
        return 1

    output = Path(args.output)
    output.write_text(
        "".join(f"{key}={value}\n" for key, value in sorted(env.items())),
        encoding="utf-8",
    )
    output.chmod(0o600)
    print(f"Variables preparadas: {len(env)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
