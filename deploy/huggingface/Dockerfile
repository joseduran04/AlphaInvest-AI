# Imagen única de AlphaInvest AI para la nube (Hugging Face Spaces o GitHub Codespaces).
#
# Un Space solo ejecuta un contenedor y expone un puerto (7860), así que
# esta imagen reúne las tres piezas de AlphaInvest AI:
#   - nginx sirve el frontend compilado y reenvía /api/ a la API.
#   - uvicorn ejecuta la API FastAPI en 127.0.0.1:8000.
#   - el worker ejecuta las tareas programadas (precios, noticias, simulaciones).
# start.sh arranca los tres procesos; si uno cae, el contenedor se reinicia.
#
# PostgreSQL (Supabase) y MongoDB (Atlas) viven fuera del Space.
# La configuración llega como "Secrets" del Space; nunca se copia un .env.

# ---------- 1. Frontend ----------
FROM node:24-alpine AS frontend

WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

# Variable del Space (Settings → Variables): la URL pública del Space.
ARG VITE_API_BASE_URL
RUN test -n "$VITE_API_BASE_URL" \
    || (echo "Falta la variable VITE_API_BASE_URL en el Space" && exit 1)
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build


# ---------- 2. Backend + nginx ----------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH" \
    HOME=/tmp

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

WORKDIR /app

# PyTorch CPU (igual que backend/Dockerfile) para no descargar CUDA.
# Va en su propia capa: un cambio en el código no vuelve a descargarlo.
RUN pip install --upgrade pip \
    && pip install "torch==2.13.0+cpu" --index-url https://download.pytorch.org/whl/cpu

COPY backend/pyproject.toml backend/README.md ./
COPY backend/src ./src
RUN pip install .

# Los modelos se registran en PostgreSQL con rutas relativas
# artifacts/ai/<modelo>/<version>/..., que resuelven desde /app.
COPY backend/artifacts ./artifacts

COPY --from=frontend /build/dist /app/static
# En el Space los archivos viven en deploy/; en el repo, en deploy/huggingface/.
ARG DEPLOY_DIR=deploy
COPY ${DEPLOY_DIR}/nginx.conf ${DEPLOY_DIR}/start.sh /app/deploy/
# Por si Git en Windows convirtió los finales de línea a CRLF.
RUN sed -i 's/\r$//' /app/deploy/start.sh /app/deploy/nginx.conf

# Hugging Face ejecuta el contenedor con el usuario 1000.
RUN useradd --create-home --uid 1000 user \
    && chown -R user:user /app

USER user

EXPOSE 7860

CMD ["bash", "/app/deploy/start.sh"]
