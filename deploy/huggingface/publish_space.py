"""Publica AlphaInvest AI en un Space de Hugging Face (SDK Docker).

Uso, desde la RAÍZ del repositorio (Git Bash):

    pip install huggingface_hub
    hf auth login                     # token con permiso "Write"
    python deploy/huggingface/publish_space.py --space TU_USUARIO/alphainvest --dry-run
    python deploy/huggingface/publish_space.py --space TU_USUARIO/alphainvest

Qué hace:
  1. Crea el Space (si no existe) con SDK Docker y hardware gratuito.
  2. Copia las variables APP_* de backend/.env como *Secrets* del Space,
     con ajustes para producción. Nunca imprime sus valores.
  3. Define la variable VITE_API_BASE_URL con la URL pública del Space.
  4. Sube el código necesario (backend, modelos y frontend) en un solo commit.
     Cada subida hace que Hugging Face vuelva a construir la imagen.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOY_DIR = ROOT / "deploy" / "huggingface"
ENV_FILE = ROOT / "backend" / ".env"

# Carpetas y archivos del repo que necesita la imagen.
SOURCE_DIRS = ("backend/src", "backend/artifacts", "frontend")
SOURCE_FILES = ("backend/pyproject.toml", "backend/README.md")

# Archivos de deploy/huggingface → ruta dentro del Space.
DEPLOY_FILES = {
    "Dockerfile": "Dockerfile",
    "README.md": "README.md",
    "nginx.conf": "deploy/nginx.conf",
    "start.sh": "deploy/start.sh",
}

EXCLUDED_DIRS = {
    "node_modules",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "test-results",
    "playwright-report",
    "coverage",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log"}

# Variables que el Space no debe heredar del .env local.
SKIPPED_ENV_KEYS = {
    "APP_WORKER_ENABLED",  # lo fija start.sh por proceso
    "APP_WORKER_RUN_ONCE",
    "APP_DATABASE_SSL_CA_FILE",
}


def space_url(space_id: str) -> str:
    owner, _, name = space_id.partition("/")
    host = re.sub(r"[^a-z0-9]+", "-", f"{owner}-{name}".lower()).strip("-")
    return f"https://{host}.hf.space"


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


def build_secrets(env: dict[str, str], url: str) -> tuple[dict[str, str], list[str]]:
    notes: list[str] = []
    result = {
        key: value
        for key, value in env.items()
        if key.startswith("APP_") and value != "" and key not in SKIPPED_ENV_KEYS
    }

    result["APP_ENV"] = "production"
    result["APP_DEBUG"] = "false"
    result["APP_CORS_ORIGINS"] = json.dumps([url])

    if result.get("APP_DATABASE_SSL_MODE", "disable") == "disable":
        result["APP_DATABASE_SSL_MODE"] = "require"
        notes.append("APP_DATABASE_SSL_MODE se fijó en 'require' (Supabase exige TLS).")

    if len(result.get("APP_JWT_SECRET_KEY", "")) < 32:
        result["APP_JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
        notes.append(
            "APP_JWT_SECRET_KEY local era corta: se generó una nueva solo para el Space."
        )

    mongo_uri = result.get("APP_MONGODB_URI", "")

    if "localhost" in mongo_uri or "mongodb://mongo:" in mongo_uri:
        raise SystemExit(
            "APP_MONGODB_URI apunta a un Mongo local. Pon la URI de MongoDB Atlas "
            "en backend/.env antes de publicar."
        )

    return result, notes


def is_excluded(relative: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True

    if relative.name.startswith(".env"):
        return True

    return relative.suffix in EXCLUDED_SUFFIXES


def collect_files() -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []

    for directory in SOURCE_DIRS:
        base = ROOT / directory

        if not base.is_dir():
            raise SystemExit(f"No existe la carpeta {directory}")

        for path in sorted(base.rglob("*")):
            relative = path.relative_to(ROOT)

            if path.is_file() and not is_excluded(relative):
                files.append((path, relative.as_posix()))

    for file_name in SOURCE_FILES:
        files.append((ROOT / file_name, file_name))

    for source, target in DEPLOY_FILES.items():
        files.append((DEPLOY_DIR / source, target))

    missing = [target for path, target in files if not path.is_file()]

    if missing:
        raise SystemExit(f"Faltan archivos: {', '.join(missing)}")

    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--space", required=True, help="usuario/nombre-del-space")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo muestra qué se subiría; no cambia nada en Hugging Face.",
    )
    parser.add_argument(
        "--skip-secrets",
        action="store_true",
        help="Sube el código sin tocar los Secrets ni las Variables.",
    )
    args = parser.parse_args()

    if "/" not in args.space:
        raise SystemExit("--space debe tener la forma usuario/nombre")

    url = space_url(args.space)
    files = collect_files()
    total_mb = sum(path.stat().st_size for path, _ in files) / 1_000_000

    print(f"Space: {args.space}")
    print(f"URL pública: {url}")
    print(f"Archivos a subir: {len(files)} ({total_mb:,.1f} MB)")

    secret_values: dict[str, str] = {}

    if not args.skip_secrets:
        if not ENV_FILE.is_file():
            raise SystemExit("No encontré backend/.env")

        secret_values, notes = build_secrets(read_env(ENV_FILE), url)
        print(f"Secrets a configurar ({len(secret_values)}): {', '.join(sorted(secret_values))}")

        for note in notes:
            print(f"  Nota: {note}")

    if args.dry_run:
        print("\n--dry-run: no se cambió nada.")
        return 0

    from huggingface_hub import CommitOperationAdd, HfApi

    api = HfApi()
    api.create_repo(
        repo_id=args.space,
        repo_type="space",
        space_sdk="docker",
        exist_ok=True,
    )

    if not args.skip_secrets:
        for key, value in secret_values.items():
            api.add_space_secret(repo_id=args.space, key=key, value=value)

        api.add_space_variable(repo_id=args.space, key="VITE_API_BASE_URL", value=url)
        print("Secrets y variable VITE_API_BASE_URL configurados.")

    operations = [
        CommitOperationAdd(path_in_repo=target, path_or_fileobj=str(path))
        for path, target in files
    ]

    print("Subiendo archivos (el modelo pesa ~440 MB, puede tardar varios minutos)...")
    api.create_commit(
        repo_id=args.space,
        repo_type="space",
        operations=operations,
        commit_message="Publicar AlphaInvest AI",
    )

    print(f"\nListo. Revisa la construcción en https://huggingface.co/spaces/{args.space}")
    print(f"Cuando diga 'Running', abre: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
