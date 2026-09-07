FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv /opt/venv \
    && addgroup --system app \
    && adduser --system --ingroup app app

COPY pyproject.toml README.md ./
COPY src ./src

# Instala explícitamente la distribución CPU-only de PyTorch.
# Esto evita que `pip install .` descargue CUDA/NVIDIA dentro
# de una imagen destinada a ejecución CPU.
RUN pip install --upgrade pip \
    && pip install \
        "torch==2.13.0+cpu" \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install .

# Los modelos IA se registran en PostgreSQL mediante rutas relativas:
# artifacts/ai/<modelo>/<version>/<archivo>.
# WORKDIR=/app garantiza que esas rutas resuelvan a /app/artifacts/...
COPY --chown=app:app artifacts ./artifacts

USER app

EXPOSE 8000

CMD ["uvicorn", "alphainvest.main:app", "--host", "0.0.0.0", "--port", "8000"]