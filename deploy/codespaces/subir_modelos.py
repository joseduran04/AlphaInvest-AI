"""Sube backend/artifacts (modelos de IA) a un repositorio de modelos de Hugging Face.

Los modelos no están en Git (pesan ~440 MB). Se guardan una sola vez en
Hugging Face (gratis) y el Codespace los descarga al arrancar.

Uso, desde la RAÍZ del repositorio en tu computadora (Git Bash):
    pip install huggingface_hub
    hf auth login                 # token tipo "Write"
    python deploy/codespaces/subir_modelos.py --repo joseduran04/alphainvest-artifacts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "backend" / "artifacts"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="usuario/nombre del repo de modelos")
    args = parser.parse_args()

    model_file = ARTIFACTS / "ai" / "analisis_sentimiento" / "0.1.0" / "model.safetensors"

    if not model_file.is_file():
        print("No encontré los modelos en backend/artifacts/ai", file=sys.stderr)
        return 1

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id=args.repo, repo_type="model", exist_ok=True)

    print("Subiendo modelos (~440 MB); puede tardar varios minutos...")
    api.upload_folder(
        repo_id=args.repo,
        repo_type="model",
        folder_path=str(ARTIFACTS),
        allow_patterns=["ai/**"],
        commit_message="Modelos de AlphaInvest AI",
    )

    print(f"Listo: https://huggingface.co/{args.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
