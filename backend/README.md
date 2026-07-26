# AlphaInvest AI Backend — Entregable 02

Infraestructura de persistencia para consumir la base PostgreSQL existente sin modificar su estructura.

## Incluye

- SQLAlchemy asíncrono (`AsyncEngine`, `AsyncSession`, `asyncpg`).
- Pool de conexiones y `pool_pre_ping`.
- Unit of Work transaccional.
- Contrato base de repositorios.
- Alembic configurado para múltiples esquemas.
- Separación ligera por dominios: `auth`, `profile`, `ai`, `market`, `portfolio`, `simulation`, `audit`, `operation` y `reporting`.
- Health checks `/live` y `/ready`.
- Docker conectado al PostgreSQL local mediante `host.docker.internal`.

## Actualización desde el Entregable 01

Copia el contenido de esta carpeta `backend/` sobre tu carpeta `backend/` actual y conserva tu archivo `.env`. Luego actualízalo tomando como referencia `.env.example`.

```bash
source .venv/Scripts/activate
pip install -e ".[dev]"
```

Configura en `.env`:

```env
APP_DATABASE_URL=postgresql+asyncpg://postgres:TU_CLAVE@localhost:5432/alphainvest_db
```

Prueba la conexión:

```bash
python scripts/check_database.py
```

Arranca la API:

```bash
uvicorn alphainvest.main:app --reload
```

Endpoints:

- `GET /api/v1/health/live`: comprueba el proceso FastAPI.
- `GET /api/v1/health/ready`: comprueba FastAPI y PostgreSQL.
- `GET /api/v1/health`: alias de readiness.

## Docker

Agrega al `.env` estas variables para Docker Compose:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=TU_CLAVE
POSTGRES_PORT=5432
POSTGRES_DB=alphainvest_db
```

Detén Uvicorn local si ocupa el puerto 8000 y ejecuta:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f api
```

PostgreSQL debe aceptar conexiones TCP desde Docker Desktop. Si PostgreSQL está en Windows, `host.docker.internal` apunta al host.

## Alembic: regla de seguridad

La base ya existe. No ejecutes `alembic revision --autogenerate` ni `alembic upgrade head` todavía. Primero se mapearán y validarán las tablas reales por dominio. Tampoco uses `stamp head` porque aún no existe una revisión basal aprobada.

Los scripts SQL `00`–`22` siguen siendo la fuente de verdad de la estructura actual.


## Entregable 03 — Autenticación

Endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.

Antes de probar, configura `APP_JWT_SECRET_KEY` con una clave aleatoria de al menos 32 caracteres. El registro asigna el rol `INVERSIONISTA` y conserva el estado `PENDIENTE_VERIFICACION` definido por PostgreSQL. Para probar login temporalmente, activa y verifica el usuario desde un flujo administrativo o SQL controlado; no se omite la verificación del estado en el backend.

No ejecutes migraciones Alembic: los modelos reflejan tablas existentes y no son una autorización para alterar el esquema.
