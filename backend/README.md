# AlphaInvest AI Backend

Backend modular de AlphaInvest AI construido con Python 3.13, FastAPI, SQLAlchemy, PostgreSQL/Supabase, MongoDB y procesos de trabajo programados.

## 1. Requisitos

### Desarrollo local

- Python `>=3.13,<3.14`
- PostgreSQL compatible con la configuración del proyecto
- MongoDB 8 o Docker
- Git
- Docker Desktop, recomendado

Crear entorno virtual:

```bash
python -m venv .venv
```

En Git Bash:

```bash
source .venv/Scripts/activate
```

Instalar el proyecto con dependencias de desarrollo:

```bash
pip install -e ".[dev]"
```

## 2. Configuración

Crea el archivo:

```text
backend/.env
```

tomando como referencia:

```text
backend/.env.example
```

No almacenes `.env` en Git.

### Variables principales

```env
APP_NAME=AlphaInvest AI API
APP_VERSION=1.0.0
APP_ENV=local
APP_DEBUG=true
APP_API_V1_PREFIX=/api/v1
```

### PostgreSQL local

Ejemplo:

```env
APP_DATABASE_URL=postgresql+asyncpg://postgres:TU_CLAVE@localhost:5432/alphainvest_db
APP_DATABASE_SSL_MODE=disable
```

No utilices este ejemplo como credencial productiva.

### PostgreSQL remoto / Supabase

Para entornos remotos utiliza una URL PostgreSQL compatible con `asyncpg` y SSL habilitado:

```env
APP_DATABASE_URL=postgresql+asyncpg://USUARIO:CLAVE@HOST:5432/postgres
APP_DATABASE_SSL_MODE=require
```

La configuración admite:

```text
disable
require
verify-ca
verify-full
```

Para `verify-ca` o `verify-full` puede configurarse:

```env
APP_DATABASE_SSL_CA_FILE=/ruta/al/certificado-ca.crt
```

En producción no debe utilizarse `APP_DATABASE_SSL_MODE=disable`.

Para conexiones persistentes desde el backend hacia Supabase se utiliza un endpoint compatible con sesiones persistentes. Las credenciales reales nunca deben almacenarse en documentación ni commits.

### MongoDB

Local:

```env
APP_MONGODB_URI=mongodb://localhost:27017
APP_MONGODB_DATABASE=alphainvest_documents
APP_MONGODB_NEWS_COLLECTION=noticias
```

Docker Compose sustituye el host por:

```text
mongodb://mongo:27017
```

## 3. Seguridad

Configura una clave JWT segura:

```env
APP_JWT_SECRET_KEY=CLAVE_ALEATORIA_DE_AL_MENOS_32_CARACTERES
```

Configuración disponible:

```env
APP_JWT_ALGORITHM=HS256
APP_ACCESS_TOKEN_MINUTES=15
APP_REFRESH_TOKEN_DAYS=30
APP_MAX_FAILED_LOGIN_ATTEMPTS=5
APP_LOGIN_LOCK_MINUTES=15
APP_DEFAULT_ROLE=INVERSIONISTA
```

La configuración de producción rechaza configuraciones inseguras conocidas, incluyendo secretos JWT débiles y determinadas configuraciones incompatibles con producción.

Nunca publiques:

- `.env`
- contraseñas de PostgreSQL/Supabase
- JWT
- API keys
- credenciales de proveedores
- claves privadas

## 4. Arquitectura

Código principal:

```text
src/alphainvest/
├── api/
├── core/
├── infrastructure/
│   ├── database/
│   └── mongodb/
├── modules/
│   ├── ai/
│   ├── audit/
│   ├── auth/
│   ├── market/
│   ├── news/
│   ├── operation/
│   ├── portfolio/
│   ├── profile/
│   ├── reporting/
│   └── simulation/
├── shared/
└── worker/
```

Los módulos de negocio siguen una separación basada en:

```text
domain/
application/
infrastructure/
presentation/
```

Principios utilizados:

- Clean Architecture.
- SOLID.
- Repository Pattern.
- Separación de dominio e infraestructura.
- Inyección de dependencias.
- Persistencia asíncrona.
- Autorización basada en permisos.

## 5. PostgreSQL

Esquemas administrados por la aplicación:

```text
ai
audit
app_auth
market
operation
portfolio
profile
simulation
```

El esquema `reporting` contiene objetos SQL de reporting y no forma parte del metadata ORM administrado por Alembic.

`app_auth` es el esquema de autenticación propio de AlphaInvest AI.

No debe sustituirse por `auth` en Supabase, porque `auth` es un esquema administrado por la plataforma.

## 6. Scripts SQL

Los scripts oficiales están en:

```text
../database/postgresql/
```

Secuencia existente:

```text
00_create_database.sql
01_extensions.sql
02_schemas.sql
03_auth_tables.sql
04_ai_base_tables.sql
05_profile_tables.sql
06_market_tables.sql
07_portfolio_tables.sql
08_simulation_tables.sql
09_ai_analysis_tables.sql
10_audit_operation_tables.sql
11_indexes.sql
12_functions.sql
13_triggers.sql
14_seed_catalogs.sql
15_initial_data.sql
16_views.sql
17_materialized_views.sql
18_reporting.sql
19_security.sql
20_backup_restore.sql
21_test_data.sql
22_documentation.sql
23_seed_risk_questionnaire.sql
24_portfolio_permissions.sql
25_simulation_permissions.sql
26_ai_analysis_retry.sql
27_schema_release_metadata.sql
```

Supabase dispone además de:

```text
../database/postgresql/supabase/19_security_supabase.sql
```

````markdown
### Clasificación para instalaciones nuevas

El baseline estable del esquema PostgreSQL `1.1.0` está formado por:

01–20
22–25
27

Se excluyen del baseline:

00_create_database.sql
21_test_data.sql
26_ai_analysis_retry.sql

`00_create_database.sql` es un bootstrap exclusivo para PostgreSQL local.

`21_test_data.sql` contiene datos exclusivamente de desarrollo y pruebas.

`26_ai_analysis_retry.sql` es una migración incremental de compatibilidad histórica y no forma parte del baseline limpio cuando `09_ai_analysis_tables.sql` ya contiene la estructura definitiva.

`27_schema_release_metadata.sql` se ejecuta después del baseline funcional y registra la versión estable `1.1.0` del esquema en `operation.versiones_esquema`.

En Supabase, `19_security.sql` se sustituye por:

supabase/19_security_supabase.sql

### Script 00

`00_create_database.sql` corresponde al bootstrap de PostgreSQL local.

No debe ejecutarse como creación de base dentro de una instancia administrada de Supabase.

### Seguridad

Para PostgreSQL administrado localmente puede utilizarse:

```text
19_security.sql
```

En Supabase se utiliza la variante:

```text
supabase/19_security_supabase.sql
```

No ejecutes indiscriminadamente el script de seguridad local sobre Supabase.

## 7. Alembic

Alembic está configurado para múltiples esquemas.

Baseline actual:

```text
130add9be5fa
```

Archivo:

```text
alembic/versions/130add9be5fa_baseline_esquema_alphainvest_ai.py
```

El baseline representa el esquema estable construido mediante los scripts SQL y no ejecuta DDL.

Después de instalar el baseline SQL en una base nueva y verificar su estructura, la revisión puede registrarse mediante un procedimiento controlado de Alembic.

No utilices `alembic revision --autogenerate` como mecanismo automático para modificar la base sin revisar primero el SQL generado.

La configuración protege tablas SQL que no están representadas en `Base.metadata` y limita la reflexión a los esquemas administrados.

La tabla de versión de Alembic se almacena en:

```text
operation.alembic_version
```

## 8. Ejecutar la API localmente

Desde `backend/`:

```bash
uvicorn alphainvest.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

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

Estas rutas de documentación están disponibles en entornos no productivos.

Cuando `APP_ENV=production` o `APP_ENV=prod`, Swagger, ReDoc y el endpoint OpenAPI se deshabilitan automáticamente como medida de hardening.

## 9. Health checks

```text
GET /api/v1/health
GET /api/v1/health/live
GET /api/v1/health/ready
```

Readiness:

```bash
curl http://localhost:8000/api/v1/health/ready
```

`ready` comprueba:

- FastAPI.
- PostgreSQL.
- MongoDB.

## 10. Docker

El `docker-compose.yml` se encuentra en la raíz del repositorio.

Desde:

```text
C:\Users\PRIDE OMEGA\Desktop\AlphaInvest-AI
```

levanta MongoDB y API:

```bash
docker compose up --build -d mongo api
```

Comprueba:

```bash
docker compose ps
```

Logs del API:

```bash
docker compose logs -f api
```

Readiness:

```bash
curl http://localhost:8000/api/v1/health/ready
```

### Contenedor API

El API ejecuta:

```text
uvicorn alphainvest.main:app --host 0.0.0.0 --port 8000
```

El contenedor se ejecuta con un usuario no privilegiado.

Los artifacts de IA se copian a:

```text
/app/artifacts
```

### MongoDB

Docker utiliza:

```text
mongodb://mongo:27017
```

y persiste la información mediante:

```text
mongo_data
```

## 11. Worker

El worker se instala mediante el entrypoint:

```text
alphainvest-worker
```

definido por:

```text
alphainvest.worker.main:main
```

El servicio utiliza un perfil Docker separado.

Arranque:

```bash
docker compose --profile worker up -d worker
```

Logs:

```bash
docker compose logs -f worker
```

El API fuerza:

```text
APP_WORKER_ENABLED=false
```

y el servicio worker:

```text
APP_WORKER_ENABLED=true
```

Esto evita que el scheduler se ejecute accidentalmente dentro del proceso HTTP.

Configuración relevante:

```env
APP_WORKER_TIMEZONE=America/Mexico_City
APP_WORKER_MAX_INSTANCES=1
APP_WORKER_MISFIRE_GRACE_SECONDS=300
```

El worker procesa tareas relacionadas con precios, indicadores, simulaciones, análisis de IA, recomendaciones y noticias, según las definiciones activas de operación.

## 12. Inteligencia artificial

Los artifacts se encuentran bajo:

```text
artifacts/ai/
```

El backend utiliza rutas relativas para los artifacts registrados en PostgreSQL.

En Docker:

```text
WORKDIR=/app
```

permite resolver:

```text
artifacts/ai/<modelo>/<version>/<archivo>
```

como:

```text
/app/artifacts/ai/<modelo>/<version>/<archivo>
```

Los scripts de análisis, entrenamiento, evaluación y carga se encuentran en:

```text
scripts/ai/
```

## 13. Mercado y proveedores

El backend dispone de integración con fuentes financieras y procesamiento de históricos.

Configuración Alpha Vantage:

```env
APP_ALPHA_VANTAGE_API_KEY=
APP_ALPHA_VANTAGE_BASE_URL=https://www.alphavantage.co
APP_ALPHA_VANTAGE_TIMEOUT_SECONDS=15
APP_ALPHA_VANTAGE_OUTPUT_SIZE=compact
```

Nunca publiques la API key.

Scripts auxiliares de mercado:

```text
scripts/market/
```

## 14. API y documentación

Prefijo:

```text
/api/v1
```

Snapshot OpenAPI utilizado durante el cierre:

```text
openapi_alphainvest.json
```

Contrato validado:

```text
87 paths
98 operaciones HTTP
141 schemas
```

Referencia:

```text
docs/API_REFERENCE.md
```

Matriz RBAC:

```text
docs/ENDPOINT_PERMISSION_MATRIX.md
```

La matriz contiene las 98 operaciones y sus requisitos de acceso.

## 15. Autenticación y autorización

Autenticación:

```text
Bearer JWT
```

Endpoints principales:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

El registro asigna por defecto el rol:

```text
INVERSIONISTA
```

En el estado actual del backend, el usuario registrado puede quedar operativo para autenticación mientras `correo_verificado` permanece como indicador independiente. Una futura integración real de verificación de correo puede reintroducir un estado pendiente dentro de ese flujo.

Roles:

```text
ADMINISTRADOR
ANALISTA
AUDITOR
INVERSIONISTA
OPERADOR
```

Catálogo validado:

```text
58 permisos
142 asignaciones rol-permiso
```

Consulta:

```text
docs/ENDPOINT_PERMISSION_MATRIX.md
```

para conocer los permisos de cada operación.

## 16. Reporting

El módulo de reporting utiliza vistas PostgreSQL y consultas parametrizadas.

La API dispone de reportes de:

- activos;
- portafolios;
- simulaciones;
- recomendaciones;
- usuarios;
- auditoría;
- trabajos operativos.

También dispone de exportación CSV según los permisos del usuario.

## 17. Noticias y MongoDB

MongoDB almacena información documental de noticias financieras.

Base:

```text
alphainvest_documents
```

Colección:

```text
noticias
```

El módulo `news` mantiene la integración entre referencias relacionales y contenido documental.

## 18. Pruebas

Ejecutar todas las pruebas:

```bash
pytest -v
```

Solo unitarias:

```bash
pytest tests/unit -v
```

Integración:

```bash
pytest tests/integration -v
```

El proyecto utiliza marcadores para:

```text
unit
integration
database
```

## 19. Calidad

Ruff:

```bash
ruff check src tests scripts
```

mypy:

```bash
mypy src
```

Compilación de un script específico:

```bash
python -m py_compile scripts/nombre_script.py
```

Antes de cerrar una implementación deben permanecer verdes las validaciones correspondientes.

## 20. E2E contra Supabase

Existe un script controlado de validación:

```text
scripts/e2e_supabase.py
```

Su objetivo es probar el flujo real del backend contra la base configurada, utilizando datos temporales y limpieza posterior.

No debe ejecutarse indiscriminadamente contra un entorno con información productiva sin revisar previamente su estrategia de creación y eliminación de datos.

## 21. Documentación generada

Generador de referencia API:

```text
scripts/generate_api_documentation.py
```

Generador de matriz RBAC:

```text
scripts/generate_endpoint_permission_matrix.py
```

Documentos resultantes:

```text
docs/API_REFERENCE.md
docs/ENDPOINT_PERMISSION_MATRIX.md
```

Los scripts de documentación no forman parte del runtime de la imagen Docker actual.

El `Dockerfile` copia:

```text
pyproject.toml
README.md
src/
artifacts/
```

por lo que `scripts/` y `docs/` permanecen como tooling del repositorio y no deben asumirse disponibles dentro de `/app`.

## 22. Comandos rápidos

### API local

```bash
uvicorn alphainvest.main:app --reload
```

### Docker API + MongoDB

Desde la raíz:

```bash
docker compose up --build -d mongo api
```

### Worker

```bash
docker compose --profile worker up -d worker
```

### Estado

```bash
docker compose ps
```

### Readiness

```bash
curl http://localhost:8000/api/v1/health/ready
```

### Tests

Desde backend:

```bash
pytest -v
```

### Ruff

```bash
ruff check src tests scripts
```

### mypy

```bash
mypy src
```

## 23. Reglas de mantenimiento

1. No asumir estructuras de PostgreSQL; verificar scripts y esquema real.
2. No modificar el esquema administrado `auth` de Supabase.
3. Mantener autenticación de AlphaInvest en `app_auth`.
4. No almacenar secretos en Git.
5. No ejecutar scripts de seguridad locales indiscriminadamente en Supabase.
6. Revisar manualmente cualquier migración Alembic antes de aplicarla.
7. Mantener las pruebas, Ruff y mypy en verde.
8. Actualizar OpenAPI y documentación cuando cambien endpoints.
9. Regenerar la matriz RBAC cuando cambien permisos o roles.
10. Mantener los artifacts requeridos por modelos activos disponibles en despliegue.

## 24. Aviso

AlphaInvest AI es una plataforma financiera educativa.

Los análisis, simulaciones, predicciones y recomendaciones generadas por el sistema no garantizan resultados futuros ni sustituyen asesoría financiera profesional.
````
