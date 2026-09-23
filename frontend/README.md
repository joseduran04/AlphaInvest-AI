# AlphaInvest AI — Frontend

Frontend web de AlphaInvest AI, plataforma educativa orientada al análisis financiero, gestión de portafolios virtuales, simulación de inversiones y apoyo mediante modelos de inteligencia artificial.

## Estado actual

El frontend se encuentra funcionalmente implementado e integrado con la API de AlphaInvest AI.

Backend estable de referencia:

- API: `v1.0.0`
- Base API: `/api/v1`
- Swagger: `/docs`
- ReDoc: `/redoc`
- OpenAPI: `/openapi.json`

El frontend consume exclusivamente la API FastAPI. No se conecta directamente a PostgreSQL, Supabase ni MongoDB.

## Stack

- React 19
- TypeScript 5
- Vite 8
- React Router
- Vitest
- Playwright
- Oxlint
- Prettier
- npm
- Docker
- Nginx

## Requisitos

Para desarrollo local:

- Node.js 24 o una versión compatible con Vite 8
- npm

Para ejecución mediante contenedores:

- Docker Desktop
- Docker Compose

## Configuración

La variable utilizada para localizar la API es:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Utiliza como referencia:

```text
frontend/.env.example
```

Las variables `VITE_*` son incorporadas al frontend durante el proceso de build.

No almacenes archivos `.env` con credenciales o configuración privada en Git.

## Desarrollo local

Desde `frontend/`:

```bash
npm install
```

Iniciar Vite:

```bash
npm run dev
```

Por defecto, el entorno local se utiliza desde:

```text
http://localhost:5173
```

## Calidad

Desde `frontend/`:

```bash
npm run lint
npm run typecheck
npm run format:check
npm run build
```

Las pruebas automatizadas se ejecutan mediante los scripts definidos en `package.json`.

Las pruebas E2E utilizan Playwright y requieren que los servicios correspondientes estén disponibles.

## Build de producción

Generar los archivos estáticos:

```bash
npm run build
```

El resultado se genera en:

```text
frontend/dist/
```

## Docker

La imagen de producción utiliza un build multi-stage:

1. Node.js 24 construye la aplicación mediante `npm ci` y Vite.
2. Nginx sirve los archivos estáticos resultantes.

Construcción manual desde `frontend/`:

```bash
docker build \
  --build-arg VITE_API_BASE_URL=http://127.0.0.1:8000 \
  -t alphainvest-frontend:local .
```

El contenedor expone internamente el puerto `80`.

La configuración de Nginx incluye fallback hacia `index.html`, permitiendo acceder directamente a rutas administradas por React Router.

## Docker Compose

Desde la raíz del repositorio:

```bash
docker compose up --build -d mongo api frontend
```

Servicios principales:

```text
Frontend: http://127.0.0.1:8080
API:      http://127.0.0.1:8000
MongoDB:  red interna de Docker
```

Estado:

```bash
docker compose ps
```

Healthcheck del frontend:

```bash
curl http://127.0.0.1:8080/health
```

Readiness del backend:

```bash
curl http://127.0.0.1:8000/api/v1/health/ready
```

El worker es opcional y utiliza el profile `worker` definido en Docker Compose.

## CORS

Cuando el frontend se ejecuta mediante Docker en:

```text
http://127.0.0.1:8080
```

el backend debe permitir dicho origen mediante `APP_CORS_ORIGINS`.

Para desarrollo Vite también deben mantenerse los orígenes utilizados en el puerto `5173`.

Consulta:

```text
backend/.env.example
```

para la configuración de referencia.

## Arquitectura de integración

```text
Navegador
   |
   +-- http://127.0.0.1:8080
   |        |
   |        v
   |      Nginx
   |        |
   |        v
   |   React / Vite build
   |
   +-- http://127.0.0.1:8000
            |
            v
          FastAPI
            |
            +-- PostgreSQL / Supabase
            +-- MongoDB
```

El navegador realiza las solicitudes a FastAPI utilizando `VITE_API_BASE_URL`.

## Seguridad

No publiques:

- archivos `.env`
- credenciales
- tokens
- contraseñas
- API keys

La autorización de las funcionalidades del frontend se basa en la sesión autenticada y los permisos proporcionados por el backend.
