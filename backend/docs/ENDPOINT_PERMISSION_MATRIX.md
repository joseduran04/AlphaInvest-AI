# AlphaInvest AI — Matriz de endpoints y permisos

Documento generado a partir del OpenAPI real del backend y de las asignaciones RBAC activas almacenadas en PostgreSQL/Supabase.

## Información general

- **API:** AlphaInvest AI API
- **Versión:** 1.0.0
- **Base path:** `/api/v1`
- **Autenticación:** HTTP Bearer

## Convenciones

- `Público`: el endpoint no exige access token.
- `Autenticado`: exige una sesión Bearer válida, sin permiso granular adicional.
- Un código como `activos.leer` representa un permiso RBAC obligatorio.
- Los permisos separados por `+` deben cumplirse simultáneamente.
- `✅`: el rol posee todos los permisos necesarios para la operación.
- `—`: el rol no posee todos los permisos necesarios.
- La matriz refleja permisos RBAC; las reglas de propiedad del recurso continúan aplicando.

## Resumen RBAC

| Rol | Permisos activos |
|---|---:|
| ADMINISTRADOR | 58 |
| ANALISTA | 19 |
| AUDITOR | 20 |
| INVERSIONISTA | 21 |
| OPERADOR | 24 |
| **TOTAL** | **142** |

## Resumen de operaciones

- **Operaciones HTTP totales:** 98
- **Operaciones públicas:** 8
- **Solo autenticación:** 4
- **Protegidas por permiso RBAC:** 86

### Operaciones accesibles por rol

| Rol | Operaciones accesibles |
|---|---:|
| ADMINISTRADOR | 98 |
| ANALISTA | 63 |
| AUDITOR | 40 |
| INVERSIONISTA | 75 |
| OPERADOR | 47 |

## Matriz endpoint / permiso / rol

| Método | Endpoint | Módulo | Acceso | ADMINISTRADOR | ANALISTA | AUDITOR | INVERSIONISTA | OPERADOR |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|
| GET | `/api/v1/health/live` | Health | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/health/ready` | Health | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/health` | Health | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST | `/api/v1/auth/register` | Autenticación | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST | `/api/v1/auth/login` | Autenticación | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST | `/api/v1/auth/refresh` | Autenticación | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST | `/api/v1/auth/logout` | Autenticación | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/auth/me` | Autenticación | Autenticado | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/profile/questionnaire` | Perfil de riesgo | Público | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/profile/current` | Perfil de riesgo | Autenticado | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/profile/history` | Perfil de riesgo | Autenticado | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST | `/api/v1/profile/evaluations` | Perfil de riesgo | Autenticado | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/market/markets` | Mercado | `activos.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/market/asset-types` | Mercado | `activos.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/market/sources` | Mercado | `fuentes.leer` | ✅ | ✅ | ✅ | — | ✅ |
| GET | `/api/v1/market/assets` | Mercado | `activos.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/market/assets/{asset_id}` | Mercado | `activos.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/market/assets/{asset_id}/prices` | Mercado | `precios.leer` | ✅ | ✅ | — | ✅ | ✅ |
| GET | `/api/v1/market/assets/{asset_id}/latest-price` | Mercado | `precios.leer` | ✅ | ✅ | — | ✅ | ✅ |
| POST | `/api/v1/market/assets/{asset_id}/prices/sync` | Mercado | `precios.cargar` | ✅ | — | — | — | ✅ |
| POST | `/api/v1/market/assets/{asset_id}/indicators/calculate` | Mercado | `indicadores.calcular` | ✅ | ✅ | — | — | ✅ |
| GET | `/api/v1/market/assets/{asset_id}/indicators` | Mercado | `indicadores.leer` | ✅ | ✅ | — | ✅ | ✅ |
| GET | `/api/v1/market/synchronizations` | Mercado | `trabajos.leer` | ✅ | ✅ | ✅ | — | ✅ |
| GET | `/api/v1/market/synchronizations/{execution_id}` | Mercado | `trabajos.leer` | ✅ | ✅ | ✅ | — | ✅ |
| POST | `/api/v1/portfolios` | Portafolios | `portafolios.crear` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/portfolios` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| PATCH | `/api/v1/portfolios/{portfolio_id}` | Portafolios | `portafolios.actualizar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}/summary` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}/allocation/assets` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}/allocation/sectors` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/portfolios/{portfolio_id}/valuations` | Portafolios | `portafolios.actualizar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}/valuations` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/portfolios/{portfolio_id}/close` | Portafolios | `portafolios.cerrar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/portfolios/{portfolio_id}/positions` | Portafolios | `portafolios.actualizar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/portfolios/{portfolio_id}/positions` | Portafolios | `portafolios.leer` | ✅ | ✅ | — | ✅ | — |
| PATCH | `/api/v1/portfolios/{portfolio_id}/positions/{position_id}` | Portafolios | `portafolios.actualizar` | ✅ | — | — | ✅ | — |
| DELETE | `/api/v1/portfolios/{portfolio_id}/positions/{position_id}` | Portafolios | `portafolios.actualizar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/simulations/configurations` | Simulaciones | `simulaciones.crear` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/simulations/configurations` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/simulations/configurations/{configuration_id}` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| PATCH | `/api/v1/simulations/configurations/{configuration_id}` | Simulaciones | `simulaciones.actualizar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/simulations/configurations/{configuration_id}/archive` | Simulaciones | `simulaciones.archivar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/simulations/configurations/{configuration_id}/assets` | Simulaciones | `simulaciones.actualizar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/simulations/configurations/{configuration_id}/assets` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| PATCH | `/api/v1/simulations/configurations/{configuration_id}/assets/{asset_id}` | Simulaciones | `simulaciones.actualizar` | ✅ | — | — | ✅ | — |
| DELETE | `/api/v1/simulations/configurations/{configuration_id}/assets/{asset_id}` | Simulaciones | `simulaciones.actualizar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/simulations/configurations/{configuration_id}/distribution` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/simulations/configurations/{configuration_id}/ready` | Simulaciones | `simulaciones.actualizar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/simulations/executions` | Simulaciones | `simulaciones.ejecutar` | ✅ | — | — | ✅ | — |
| GET | `/api/v1/simulations/executions` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/simulations/executions/{execution_id}` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/simulations/executions/{execution_id}/result` | Simulaciones | `simulaciones.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/simulations/executions/{execution_id}/cancel` | Simulaciones | `simulaciones.ejecutar` | ✅ | — | — | ✅ | — |
| POST | `/api/v1/ai/analysis-requests` | Inteligencia artificial | `analisis.solicitar` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/analysis-requests/{request_id}` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/models` | Inteligencia artificial | `modelos.leer` | ✅ | ✅ | ✅ | ✅ | — |
| PATCH | `/api/v1/ai/models/{model_id}/status` | Inteligencia artificial | `modelos.administrar` | ✅ | — | — | — | — |
| POST | `/api/v1/ai/models/{model_id}/versions` | Inteligencia artificial | `versiones_modelo.administrar` | ✅ | — | — | — | — |
| GET | `/api/v1/ai/models/{model_id}/versions` | Inteligencia artificial | `versiones_modelo.leer` | ✅ | ✅ | ✅ | — | — |
| GET | `/api/v1/ai/models/code/{code}` | Inteligencia artificial | `modelos.leer` | ✅ | ✅ | ✅ | ✅ | — |
| GET | `/api/v1/ai/models/code/{code}/active-version` | Inteligencia artificial | `versiones_modelo.leer` | ✅ | ✅ | ✅ | — | — |
| GET | `/api/v1/ai/models/{model_id}` | Inteligencia artificial | `modelos.leer` | ✅ | ✅ | ✅ | ✅ | — |
| GET | `/api/v1/ai/models/{model_id}/active-version` | Inteligencia artificial | `versiones_modelo.leer` | ✅ | ✅ | ✅ | — | — |
| GET | `/api/v1/ai/versions/{version_id}` | Inteligencia artificial | `versiones_modelo.leer` | ✅ | ✅ | ✅ | — | — |
| POST | `/api/v1/ai/versions/{version_id}/activate` | Inteligencia artificial | `versiones_modelo.activar` | ✅ | — | — | — | — |
| POST | `/api/v1/ai/versions/{version_id}/deactivate` | Inteligencia artificial | `versiones_modelo.activar` | ✅ | — | — | — | — |
| GET | `/api/v1/ai/analysis-requests/{request_id}/result` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/ai/sentiment-analysis-requests` | Inteligencia artificial | `analisis.solicitar` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/ai/recommendation-requests` | Inteligencia artificial | `analisis.solicitar` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/recommendation-requests/{request_id}` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/recommendation-requests/{request_id}/result` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| POST | `/api/v1/ai/integral-analysis-requests` | Inteligencia artificial | `analisis.solicitar` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/integral-analysis-requests/{request_id}` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/ai/integral-analysis-requests/{request_id}/result` | Inteligencia artificial | `analisis.leer` | ✅ | ✅ | — | ✅ | — |
| GET | `/api/v1/news/assets/{asset_id}` | Noticias | `noticias.leer` | ✅ | ✅ | — | ✅ | ✅ |
| POST | `/api/v1/news/assets/{asset_id}/sync` | Noticias | `noticias.cargar` | ✅ | — | — | — | ✅ |
| GET | `/api/v1/notifications` | Notificaciones | `notificaciones.leer` | ✅ | — | — | ✅ | ✅ |
| GET | `/api/v1/notifications/unread-count` | Notificaciones | `notificaciones.leer` | ✅ | — | — | ✅ | ✅ |
| GET | `/api/v1/notifications/admin` | Notificaciones | `notificaciones.administrar` | ✅ | — | — | — | ✅ |
| GET | `/api/v1/notifications/admin/{notification_id}` | Notificaciones | `notificaciones.administrar` | ✅ | — | — | — | ✅ |
| PATCH | `/api/v1/notifications/admin/{notification_id}/cancel` | Notificaciones | `notificaciones.administrar` | ✅ | — | — | — | ✅ |
| GET | `/api/v1/notifications/{notification_id}` | Notificaciones | `notificaciones.leer` | ✅ | — | — | ✅ | ✅ |
| PATCH | `/api/v1/notifications/{notification_id}/read` | Notificaciones | `notificaciones.leer` | ✅ | — | — | ✅ | ✅ |
| GET | `/api/v1/reports/assets` | Reportes | `reportes.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/portfolios` | Reportes | `reportes.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/simulations` | Reportes | `reportes.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/recommendations` | Reportes | `reportes.leer` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/export/assets` | Reportes | `reportes.exportar` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/export/portfolios` | Reportes | `reportes.exportar` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/export/simulations` | Reportes | `reportes.exportar` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/export/recommendations` | Reportes | `reportes.exportar` | ✅ | ✅ | ✅ | ✅ | ✅ |
| GET | `/api/v1/reports/admin/users` | Reportes | `reportes.administrar` | ✅ | — | ✅ | — | ✅ |
| GET | `/api/v1/reports/admin/audit` | Reportes | `reportes.administrar` | ✅ | — | ✅ | — | ✅ |
| GET | `/api/v1/reports/admin/jobs` | Reportes | `reportes.administrar` | ✅ | — | ✅ | — | ✅ |
| GET | `/api/v1/reports/admin/export/users` | Reportes | `reportes.administrar + reportes.exportar` | ✅ | — | ✅ | — | ✅ |
| GET | `/api/v1/reports/admin/export/audit` | Reportes | `reportes.administrar + reportes.exportar` | ✅ | — | ✅ | — | ✅ |
| GET | `/api/v1/reports/admin/export/jobs` | Reportes | `reportes.administrar + reportes.exportar` | ✅ | — | ✅ | — | ✅ |

## Fuente de verdad

- Endpoints y métodos: `openapi_alphainvest.json`.
- Clasificación endpoint/permiso: `scripts/generate_api_documentation.py`.
- Asignaciones rol/permiso: `app_auth.roles`, `app_auth.permisos` y `app_auth.rol_permisos`.

La matriz debe regenerarse cuando cambien endpoints, permisos o asignaciones de roles.
