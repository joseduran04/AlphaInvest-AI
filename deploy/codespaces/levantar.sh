#!/usr/bin/env bash
# Levanta AlphaInvest AI dentro de un GitHub Codespace y la publica con HTTPS.
#
# Uso, en la terminal del Codespace:
#     bash deploy/codespaces/levantar.sh
#
# Requisitos:
#   - backend/.env dentro del Codespace (arrástralo al explorador de archivos
#     o guárdalo como secreto de Codespaces llamado ALPHAINVEST_ENV).
#   - Los modelos en Hugging Face (deploy/codespaces/subir_modelos.py).
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ -z "${CODESPACE_NAME:-}" ]; then
    echo "Este script es para GitHub Codespaces." >&2
    exit 1
fi

DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
URL="https://${CODESPACE_NAME}-7860.${DOMAIN}"
MODELS_REPO="${ALPHAINVEST_MODELS_REPO:-joseduran04/alphainvest-artifacts}"
ENV_OUT="/tmp/alphainvest.env"

echo "==> 1/5 Configuración"
if [ ! -f backend/.env ]; then
    if [ -n "${ALPHAINVEST_ENV:-}" ]; then
        printf '%s\n' "$ALPHAINVEST_ENV" > backend/.env
        echo "backend/.env creado desde el secreto ALPHAINVEST_ENV."
    else
        echo "Falta backend/.env. Arrástralo desde tu computadora a la carpeta backend/ del explorador." >&2
        exit 1
    fi
fi
python3 deploy/codespaces/make_env.py --url "$URL" --output "$ENV_OUT"

echo "==> 2/5 Modelos de IA"
if [ ! -f backend/artifacts/ai/analisis_sentimiento/0.1.0/model.safetensors ]; then
    if ! command -v hf >/dev/null 2>&1; then
        pip install --user --quiet huggingface_hub
        export PATH="$HOME/.local/bin:$PATH"
    fi
    hf download "$MODELS_REPO" --repo-type model --local-dir backend/artifacts
else
    echo "Ya están descargados."
fi

echo "==> 3/5 Construyendo la imagen (la primera vez tarda 10-15 minutos)"
docker build \
    -f deploy/huggingface/Dockerfile \
    --build-arg DEPLOY_DIR=deploy/huggingface \
    --build-arg VITE_API_BASE_URL="$URL" \
    -t alphainvest:latest \
    .

echo "==> 4/5 Iniciando el contenedor"
docker rm -f alphainvest >/dev/null 2>&1 || true
docker run -d \
    --name alphainvest \
    --restart unless-stopped \
    -p 7860:7860 \
    --env-file "$ENV_OUT" \
    alphainvest:latest >/dev/null

echo "==> 5/5 Haciendo pública la dirección"
if ! gh codespace ports visibility 7860:public -c "$CODESPACE_NAME" >/dev/null 2>&1; then
    echo "No pude cambiarla solo. Hazlo a mano: pestaña PORTS → puerto 7860 → clic derecho → Port Visibility → Public."
fi

echo
echo "Listo. En 1-2 minutos abre:"
echo "    $URL"
echo
echo "Ver logs:      docker logs -f alphainvest"
echo "Detener:       docker stop alphainvest"
