#!/usr/bin/env bash
# Arranca los tres procesos del Space en el mismo contenedor.
# Si cualquiera termina, el contenedor sale y Hugging Face lo reinicia.
set -uo pipefail

cd /app

APP_WORKER_ENABLED=false uvicorn alphainvest.main:app \
    --host 127.0.0.1 --port 8000 \
    --proxy-headers --forwarded-allow-ips=127.0.0.1 &

APP_WORKER_ENABLED=true alphainvest-worker &

nginx -e stderr -c /app/deploy/nginx.conf -g "daemon off;" &

wait -n
status=$?
echo "Un proceso terminó (código ${status}); el contenedor se reiniciará." >&2
exit 1
