# AlphaInvest AI

AlphaInvest AI es una plataforma financiera educativa orientada al análisis de mercados, gestión de portafolios virtuales, simulación de inversiones y generación de análisis y recomendaciones mediante modelos de inteligencia artificial.

El proyecto utiliza una arquitectura backend modular basada en FastAPI, PostgreSQL/Supabase y MongoDB, con procesos asíncronos para tareas financieras, simulaciones, análisis de IA, noticias y operaciones programadas.

## Estado del proyecto

El backend planificado se encuentra funcionalmente implementado.

Módulos principales:

- Autenticación y autorización.
- Perfil de riesgo.
- Mercado y activos financieros.
- Precios históricos.
- Indicadores técnicos.
- Fuentes financieras.
- Portafolios virtuales.
- Simulaciones históricas.
- Modelos y versiones de IA.
- Análisis financieros.
- Noticias financieras.
- Análisis de sentimiento.
- Recomendaciones.
- Análisis integral.
- Notificaciones.
- Reportes.
- Auditoría y operación.
- Worker y trabajos programados.

## Arquitectura general

```text
Clientes
   |
   v
FastAPI REST API
   |
   +-------------------------+
   |                         |
   v                         v
PostgreSQL / Supabase     MongoDB
   |                         |
   |                         +-- Noticias/documentos
   |
   +-- Autenticación
   +-- Perfil de riesgo
   +-- Mercado
   +-- Portafolios
   +-- Simulaciones
   +-- Inteligencia artificial
   +-- Auditoría
   +-- Operación
   +-- Reporting

              Worker
                |
                +-- Precios
                +-- Indicadores
                +-- Simulaciones
                +-- Análisis IA
                +-- Recomendaciones
                +-- Noticias
```

El backend sigue una organización inspirada en Clean Architecture y separación por dominios.

Cada módulo puede contener:

```text
domain/
application/
infrastructure/
presentation/
```

## Tecnologías principales

### Backend

- Python 3.13
- FastAPI
- Pydantic 2
- SQLAlchemy 2
- asyncpg
- psycopg
- Alembic
- PyJWT
- Argon2
- APScheduler

### Datos

- PostgreSQL
- Supabase PostgreSQL
- MongoDB 8

### Inteligencia artificial y análisis

- NumPy
- scikit-learn
- XGBoost
- PyTorch
- Transformers
- yfinance
- exchange-calendars

### Calidad

- pytest
- pytest-asyncio
- Ruff
- mypy

### Infraestructura

- Docker
- Docker Compose

## Estructura principal

```text
AlphaInvest-AI/
├── backend/
│   ├── alembic/
│   ├── artifacts/
│   ├── docs/
│   ├── scripts/
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
├── database/
│   └── postgresql/
│
├── docker-compose.yml
└── README.md
```

## Backend

La documentación técnica de instalación, configuración y operación se encuentra en:

```text
backend/README.md
```

## API

La API utiliza el prefijo:

```text
/api/v1
```

Documentación interactiva con la aplicación en ejecución:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI:

```text
http://localhost:8000/openapi.json
```

El contrato OpenAPI validado contiene:

- 87 paths.
- 98 operaciones HTTP.
- 141 schemas.

La referencia detallada se encuentra en:

```text
backend/docs/API_REFERENCE.md
```

La matriz de endpoints, permisos y roles se encuentra en:

```text
backend/docs/ENDPOINT_PERMISSION_MATRIX.md
```

## Seguridad y RBAC

AlphaInvest AI utiliza autenticación Bearer con JWT y autorización basada en permisos.

Roles definidos:

- `ADMINISTRADOR`
- `ANALISTA`
- `AUDITOR`
- `INVERSIONISTA`
- `OPERADOR`

La instalación validada contiene 58 permisos y 142 asignaciones rol-permiso.

La matriz documental indica qué operaciones están disponibles para cada rol.

## Persistencia

### PostgreSQL / Supabase

PostgreSQL contiene la información transaccional y relacional del sistema.

Esquemas principales:

```text
app_auth
profile
market
portfolio
simulation
ai
audit
operation
reporting
```

El nombre `app_auth` se utiliza para evitar conflictos con el esquema administrado `auth` de Supabase.

### MongoDB

MongoDB se utiliza para información documental, principalmente noticias financieras.

Base documental:

```text
alphainvest_documents
```

Colección principal:

```text
noticias
```

## Docker

Para levantar MongoDB y la API:

```bash
docker compose up --build -d mongo api
```

Estado:

```bash
docker compose ps
```

Readiness:

```bash
curl http://localhost:8000/api/v1/health/ready
```

El worker utiliza un perfil separado:

```bash
docker compose --profile worker up -d worker
```

## Health checks

```text
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

`/ready` comprueba la disponibilidad de:

- API.
- PostgreSQL.
- MongoDB.

## Base de datos

La definición SQL se encuentra en:

```text
database/postgresql/
```

Existen scripts numerados desde `00` hasta `27`, además de una variante de seguridad específica para Supabase.

La versión estable actual del backend/API es `1.0.0`.

El esquema PostgreSQL mantiene un versionado independiente y su release estable actual es `1.1.0`, registrado mediante `27_schema_release_metadata.sql`.

El baseline limpio de base de datos utiliza `01–20`, `22–25` y `27`; `21_test_data.sql` es exclusivo de pruebas y `26_ai_analysis_retry.sql` se conserva únicamente como migración incremental de compatibilidad histórica.

Los scripts de prueba, compatibilidad histórica y bootstrap local no deben tratarse automáticamente como parte de una instalación productiva.

Consulta `backend/README.md` antes de ejecutar una instalación desde cero.

## Pruebas y calidad

Desde `backend/`:

```bash
pytest -v
```

```bash
ruff check src tests scripts
```

```bash
mypy src
```

El backend cuenta con pruebas unitarias, pruebas de integración y validaciones E2E controladas contra Supabase.

## Proyecto académico

AlphaInvest AI forma parte de un proyecto modular orientado a aplicar ingeniería de software, bases de datos, seguridad, análisis financiero e inteligencia artificial en una plataforma educativa de inversión.

El sistema no sustituye asesoría financiera profesional ni garantiza rendimientos futuros.
