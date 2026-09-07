# AlphaInvest AI — Referencia de API

Documento generado automáticamente a partir de OpenAPI.

## Información general

- **Nombre:** AlphaInvest AI API
- **Versión:** 1.0.0
- **Base path:** `/api/v1`
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI:** `/openapi.json`
- **Paths OpenAPI:** 87
- **Schemas:** 141

## Autenticación

AlphaInvest AI utiliza tokens de acceso Bearer.

```http
Authorization: Bearer <access_token>
```

Esquemas OpenAPI registrados:

```json
{
  "HTTPBearer": {
    "type": "http",
    "scheme": "bearer"
  }
}
```

## Convenciones

- `Público`: no requiere access token.
- `Autenticado`: requiere sesión válida.
- Cualquier código como `activos.leer` corresponde a un permiso RBAC.
- Los endpoints administrativos pueden requerir más de un permiso.
- Los recursos personales aplican control de propiedad por usuario.

## Endpoints

| Método | Ruta | Tag | Resumen | Acceso | Request | Response | Parámetros | Códigos |
|---|---|---|---|---|---|---|---|---|
| GET | `/api/v1/health/live` | Health | Liveness | Público | - | object | - | 200 |
| GET | `/api/v1/health/ready` | Health | Readiness | Público | - | - | - | 200 |
| GET | `/api/v1/health` | Health | Health Alias | Público | - | - | - | 200 |
| POST | `/api/v1/auth/register` | Autenticación | Register | Público | RegisterRequest | UserResponse | - | 201, 422 |
| POST | `/api/v1/auth/login` | Autenticación | Login | Público | LoginRequest | TokenResponse | - | 200, 422 |
| POST | `/api/v1/auth/refresh` | Autenticación | Refresh | Público | RefreshRequest | TokenResponse | - | 200, 422 |
| POST | `/api/v1/auth/logout` | Autenticación | Logout | Público | LogoutRequest | - | - | 204, 422 |
| GET | `/api/v1/auth/me` | Autenticación | Me | Autenticado | - | UserResponse | - | 200 |
| GET | `/api/v1/profile/questionnaire` | Perfil de riesgo | Obtener cuestionario de perfil de riesgo | Público | - | QuestionnaireResponse | - | 200 |
| GET | `/api/v1/profile/current` | Perfil de riesgo | Obtener perfil de riesgo vigente | Autenticado | - | CurrentRiskProfileResponse | - | 200 |
| GET | `/api/v1/profile/history` | Perfil de riesgo | Obtener historial de perfiles de riesgo | Autenticado | - | RiskProfileHistoryResponse | - | 200 |
| POST | `/api/v1/profile/evaluations` | Perfil de riesgo | Crear evaluación de perfil de riesgo | Autenticado | CreateRiskEvaluationRequest | RiskEvaluationResponse | - | 201, 422 |
| GET | `/api/v1/market/markets` | Mercado | Listar mercados | activos.leer | - | MarketListResponse | active_only (query, opt) | 200, 422 |
| GET | `/api/v1/market/asset-types` | Mercado | Listar tipos de activo | activos.leer | - | AssetTypeListResponse | active_only (query, opt) | 200, 422 |
| GET | `/api/v1/market/sources` | Mercado | Listar fuentes financieras | fuentes.leer | - | FinancialSourceListResponse | active_only (query, opt) | 200, 422 |
| GET | `/api/v1/market/assets` | Mercado | Listar activos financieros | activos.leer | - | AssetListResponse | search (query, opt); market_code (query, opt); asset_type_code (query, opt); sector (query, opt); currency (query, opt); status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/market/assets/{asset_id}` | Mercado | Obtener detalle de activo | activos.leer | - | AssetResponse | asset_id (path, req) | 200, 422 |
| GET | `/api/v1/market/assets/{asset_id}/prices` | Mercado | Consultar precios históricos | precios.leer | - | HistoricalPriceListResponse | asset_id (path, req); start_date (query, opt); end_date (query, opt); source_id (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/market/assets/{asset_id}/latest-price` | Mercado | Consultar último precio disponible | precios.leer | - | LatestPriceResponse | asset_id (path, req); source_id (query, opt) | 200, 422 |
| POST | `/api/v1/market/assets/{asset_id}/prices/sync` | Mercado | Sincronizar precios diarios | precios.cargar | - | PriceSynchronizationResponse | asset_id (path, req) | 200, 422 |
| POST | `/api/v1/market/assets/{asset_id}/indicators/calculate` | Mercado | Calcular indicadores financieros | indicadores.calcular | IndicatorCalculationRequest | IndicatorCalculationResponse | asset_id (path, req) | 200, 422 |
| GET | `/api/v1/market/assets/{asset_id}/indicators` | Mercado | Consultar indicadores financieros | indicadores.leer | - | FinancialIndicatorListResponse | asset_id (path, req); indicator_type (query, opt); period (query, opt); start_date (query, opt); end_date (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/market/synchronizations` | Mercado | Listar sincronizaciones de mercado | trabajos.leer | - | JobExecutionListResponse | status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/market/synchronizations/{execution_id}` | Mercado | Consultar sincronización de mercado | trabajos.leer | - | JobExecutionResponse | execution_id (path, req) | 200, 422 |
| POST | `/api/v1/portfolios` | Portafolios | Crear portafolio | portafolios.crear | PortfolioCreateRequest | PortfolioResponse | - | 201, 422 |
| GET | `/api/v1/portfolios` | Portafolios | Consultar portafolios propios | portafolios.leer | - | PortfolioListResponse | estado (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}` | Portafolios | Consultar portafolio | portafolios.leer | - | PortfolioResponse | portfolio_id (path, req) | 200, 422 |
| PATCH | `/api/v1/portfolios/{portfolio_id}` | Portafolios | Actualizar portafolio | portafolios.actualizar | PortfolioUpdateRequest | PortfolioResponse | portfolio_id (path, req) | 200, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}/summary` | Portafolios | Consultar resumen del portafolio | portafolios.leer | - | PortfolioOverviewResponse | portfolio_id (path, req) | 200, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}/allocation/assets` | Portafolios | Consultar distribución por activo | portafolios.leer | - | AssetAllocationResponse | portfolio_id (path, req) | 200, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}/allocation/sectors` | Portafolios | Consultar distribución por sector | portafolios.leer | - | SectorAllocationResponse | portfolio_id (path, req) | 200, 422 |
| POST | `/api/v1/portfolios/{portfolio_id}/valuations` | Portafolios | Registrar valoración histórica | portafolios.actualizar | PortfolioValuationCreateRequest | PortfolioValuationResponse | portfolio_id (path, req) | 201, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}/valuations` | Portafolios | Consultar historial de valoraciones | portafolios.leer | - | PortfolioValuationListResponse | portfolio_id (path, req); limit (query, opt); offset (query, opt) | 200, 422 |
| POST | `/api/v1/portfolios/{portfolio_id}/close` | Portafolios | Cerrar portafolio | portafolios.cerrar | - | PortfolioCloseResponse | portfolio_id (path, req) | 200, 422 |
| POST | `/api/v1/portfolios/{portfolio_id}/positions` | Portafolios | Agregar posición virtual | portafolios.actualizar | PositionCreateRequest | PositionResponse | portfolio_id (path, req) | 201, 422 |
| GET | `/api/v1/portfolios/{portfolio_id}/positions` | Portafolios | Consultar posiciones virtuales | portafolios.leer | - | PositionListResponse | portfolio_id (path, req); limit (query, opt); offset (query, opt) | 200, 422 |
| PATCH | `/api/v1/portfolios/{portfolio_id}/positions/{position_id}` | Portafolios | Actualizar posición virtual | portafolios.actualizar | PositionUpdateRequest | PositionResponse | portfolio_id (path, req); position_id (path, req) | 200, 422 |
| DELETE | `/api/v1/portfolios/{portfolio_id}/positions/{position_id}` | Portafolios | Eliminar posición virtual | portafolios.actualizar | - | - | portfolio_id (path, req); position_id (path, req) | 204, 422 |
| POST | `/api/v1/simulations/configurations` | Simulaciones | Crear configuración de simulación | simulaciones.crear | SimulationConfigurationCreateRequest | SimulationConfigurationResponse | - | 201, 422 |
| GET | `/api/v1/simulations/configurations` | Simulaciones | Listar configuraciones de simulación | simulaciones.leer | - | SimulationConfigurationListResponse | estado (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/simulations/configurations/{configuration_id}` | Simulaciones | Consultar configuración de simulación | simulaciones.leer | - | SimulationConfigurationResponse | configuration_id (path, req) | 200, 422 |
| PATCH | `/api/v1/simulations/configurations/{configuration_id}` | Simulaciones | Actualizar configuración de simulación | simulaciones.actualizar | SimulationConfigurationUpdateRequest | SimulationConfigurationResponse | configuration_id (path, req) | 200, 422 |
| POST | `/api/v1/simulations/configurations/{configuration_id}/archive` | Simulaciones | Archivar configuración de simulación | simulaciones.archivar | - | SimulationConfigurationArchiveResponse | configuration_id (path, req) | 200, 422 |
| POST | `/api/v1/simulations/configurations/{configuration_id}/assets` | Simulaciones | Agregar activo a configuración | simulaciones.actualizar | SimulationConfigurationAssetCreateRequest | SimulationConfigurationAssetResponse | configuration_id (path, req) | 201, 422 |
| GET | `/api/v1/simulations/configurations/{configuration_id}/assets` | Simulaciones | Listar activos de configuración | simulaciones.leer | - | SimulationConfigurationAssetListResponse | configuration_id (path, req) | 200, 422 |
| PATCH | `/api/v1/simulations/configurations/{configuration_id}/assets/{asset_id}` | Simulaciones | Actualizar activo de configuración | simulaciones.actualizar | SimulationConfigurationAssetUpdateRequest | SimulationConfigurationAssetResponse | configuration_id (path, req); asset_id (path, req) | 200, 422 |
| DELETE | `/api/v1/simulations/configurations/{configuration_id}/assets/{asset_id}` | Simulaciones | Eliminar activo de configuración | simulaciones.actualizar | - | - | configuration_id (path, req); asset_id (path, req) | 204, 422 |
| GET | `/api/v1/simulations/configurations/{configuration_id}/distribution` | Simulaciones | Consultar estado de distribución | simulaciones.leer | - | SimulationDistributionStatusResponse | configuration_id (path, req) | 200, 422 |
| POST | `/api/v1/simulations/configurations/{configuration_id}/ready` | Simulaciones | Marcar configuración como lista | simulaciones.actualizar | - | SimulationConfigurationReadyResponse | configuration_id (path, req) | 200, 422 |
| POST | `/api/v1/simulations/executions` | Simulaciones | Solicitar ejecución de simulación | simulaciones.ejecutar | SimulationExecutionCreateRequest | SimulationExecutionResponse | - | 201, 422 |
| GET | `/api/v1/simulations/executions` | Simulaciones | Listar ejecuciones de simulación | simulaciones.leer | - | SimulationExecutionListResponse | estado (query, opt); configuracion_id (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/simulations/executions/{execution_id}` | Simulaciones | Consultar ejecución de simulación | simulaciones.leer | - | SimulationExecutionResponse | execution_id (path, req) | 200, 422 |
| GET | `/api/v1/simulations/executions/{execution_id}/result` | Simulaciones | Consultar resultado de simulación | simulaciones.leer | - | SimulationResultResponse | execution_id (path, req) | 200, 422 |
| POST | `/api/v1/simulations/executions/{execution_id}/cancel` | Simulaciones | Cancelar ejecución de simulación | simulaciones.ejecutar | - | SimulationExecutionCancelResponse | execution_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/analysis-requests` | Inteligencia artificial | Solicitar análisis de un activo | analisis.solicitar | AssetAnalysisRequestCreate | AnalysisRequestResponse | - | 201, 422 |
| GET | `/api/v1/ai/analysis-requests/{request_id}` | Inteligencia artificial | Consultar solicitud de análisis | analisis.leer | - | AnalysisRequestResponse | request_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/models` | Inteligencia artificial | Listar modelos de inteligencia artificial | modelos.leer | - | AIModelListResponse | search (query, opt); type (query, opt); status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| PATCH | `/api/v1/ai/models/{model_id}/status` | Inteligencia artificial | Cambiar estado de un modelo de IA | modelos.administrar | AIModelStatusUpdateRequest | AIModelResponse | model_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/models/{model_id}/versions` | Inteligencia artificial | Registrar versión de modelo de IA | versiones_modelo.administrar | ModelVersionCreateRequest | ModelVersionResponse | model_id (path, req) | 201, 422 |
| GET | `/api/v1/ai/models/{model_id}/versions` | Inteligencia artificial | Listar versiones de un modelo de IA | versiones_modelo.leer | - | ModelVersionListResponse | model_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/models/code/{code}` | Inteligencia artificial | Consultar modelo de IA por código | modelos.leer | - | AIModelResponse | code (path, req) | 200, 422 |
| GET | `/api/v1/ai/models/code/{code}/active-version` | Inteligencia artificial | Consultar versión activa por código de modelo | versiones_modelo.leer | - | ActiveModelVersionResponse | code (path, req) | 200, 422 |
| GET | `/api/v1/ai/models/{model_id}` | Inteligencia artificial | Consultar modelo de inteligencia artificial | modelos.leer | - | AIModelResponse | model_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/models/{model_id}/active-version` | Inteligencia artificial | Consultar versión activa de un modelo de IA | versiones_modelo.leer | - | ActiveModelVersionResponse | model_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/versions/{version_id}` | Inteligencia artificial | Consultar versión de modelo de IA | versiones_modelo.leer | - | ModelVersionResponse | version_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/versions/{version_id}/activate` | Inteligencia artificial | Activar versión de modelo de IA | versiones_modelo.activar | - | ModelVersionResponse | version_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/versions/{version_id}/deactivate` | Inteligencia artificial | Desactivar versión de modelo de IA | versiones_modelo.activar | - | ModelVersionResponse | version_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/analysis-requests/{request_id}/result` | Inteligencia artificial | Consultar resultado de análisis | analisis.leer | - | AssetAnalysisResultResponse | request_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/sentiment-analysis-requests` | Inteligencia artificial | Solicitar análisis de sentimiento | analisis.solicitar | SentimentAnalysisRequestCreate | AnalysisRequestResponse | - | 201, 422 |
| POST | `/api/v1/ai/recommendation-requests` | Inteligencia artificial | Solicitar recomendación inteligente | analisis.solicitar | RecommendationRequestCreate | AnalysisRequestResponse | - | 201, 422 |
| GET | `/api/v1/ai/recommendation-requests/{request_id}` | Inteligencia artificial | Consultar solicitud de recomendación | analisis.leer | - | AnalysisRequestResponse | request_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/recommendation-requests/{request_id}/result` | Inteligencia artificial | Consultar resultado de recomendación | analisis.leer | - | RecommendationResultResponse | request_id (path, req) | 200, 422 |
| POST | `/api/v1/ai/integral-analysis-requests` | Inteligencia artificial | Solicitar análisis integral | analisis.solicitar | IntegralAnalysisRequestCreate | AnalysisRequestResponse | - | 201, 422 |
| GET | `/api/v1/ai/integral-analysis-requests/{request_id}` | Inteligencia artificial | Consultar solicitud de análisis integral | analisis.leer | - | AnalysisRequestResponse | request_id (path, req) | 200, 422 |
| GET | `/api/v1/ai/integral-analysis-requests/{request_id}/result` | Inteligencia artificial | Consultar resultado de análisis integral | analisis.leer | - | RecommendationResultResponse | request_id (path, req) | 200, 422 |
| GET | `/api/v1/news/assets/{asset_id}` | Noticias | Consultar noticias de un activo | noticias.leer | - | NewsListResponse | asset_id (path, req); start_at (query, opt); end_at (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| POST | `/api/v1/news/assets/{asset_id}/sync` | Noticias | Sincronizar noticias de un activo | noticias.cargar | - | NewsSynchronizationResponse | asset_id (path, req); start_at (query, opt); end_at (query, opt); limit (query, opt) | 200, 422 |
| GET | `/api/v1/notifications` | Notificaciones | Consultar mis notificaciones | notificaciones.leer | - | NotificationListResponse | unread_only (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/notifications/unread-count` | Notificaciones | Contar notificaciones no leídas | notificaciones.leer | - | UnreadNotificationCountResponse | - | 200 |
| GET | `/api/v1/notifications/admin` | Notificaciones | Listar notificaciones administrativamente | notificaciones.administrar | - | AdminNotificationListResponse | user_id (query, opt); status (query, opt); type (query, opt); channel (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/notifications/admin/{notification_id}` | Notificaciones | Consultar notificación administrativamente | notificaciones.administrar | - | NotificationResponse | notification_id (path, req) | 200, 422 |
| PATCH | `/api/v1/notifications/admin/{notification_id}/cancel` | Notificaciones | Cancelar una notificación | notificaciones.administrar | - | NotificationResponse | notification_id (path, req) | 200, 422 |
| GET | `/api/v1/notifications/{notification_id}` | Notificaciones | Consultar una notificación | notificaciones.leer | - | NotificationResponse | notification_id (path, req) | 200, 422 |
| PATCH | `/api/v1/notifications/{notification_id}/read` | Notificaciones | Marcar notificación como leída | notificaciones.leer | - | NotificationResponse | notification_id (path, req) | 200, 422 |
| GET | `/api/v1/reports/assets` | Reportes | Consultar reporte de activos | reportes.leer | - | AssetReportListResponse | symbol (query, opt); market_code (query, opt); asset_type_code (query, opt); sector (query, opt); status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/portfolios` | Reportes | Consultar mis reportes de portafolios | reportes.leer | - | PortfolioReportListResponse | status (query, opt); type (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/simulations` | Reportes | Consultar mis reportes de simulaciones | reportes.leer | - | SimulationReportListResponse | status (query, opt); type (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/recommendations` | Reportes | Consultar mis reportes de recomendaciones | reportes.leer | - | RecommendationReportListResponse | type (query, opt); risk_level (query, opt); horizon (query, opt); status (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/export/assets` | Reportes | Exportar reporte de activos a CSV | reportes.exportar | - | - | symbol (query, opt); market_code (query, opt); asset_type_code (query, opt); sector (query, opt); status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/export/portfolios` | Reportes | Exportar mis portafolios a CSV | reportes.exportar | - | - | status (query, opt); type (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/export/simulations` | Reportes | Exportar mis simulaciones a CSV | reportes.exportar | - | - | status (query, opt); type (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/export/recommendations` | Reportes | Exportar mis recomendaciones a CSV | reportes.exportar | - | - | type (query, opt); risk_level (query, opt); horizon (query, opt); status (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/users` | Reportes | Consultar reporte administrativo de usuarios | reportes.administrar | - | UserReportListResponse | status (query, opt); email_verified (query, opt); blocked (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/audit` | Reportes | Consultar reporte administrativo de auditoría | reportes.administrar | - | AuditDailyReportListResponse | entity_schema (query, opt); entity_name (query, opt); action (query, opt); origin (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/jobs` | Reportes | Consultar reporte administrativo de trabajos | reportes.administrar | - | OperationJobReportListResponse | active (query, opt); type (query, opt); last_status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/export/users` | Reportes | Exportar usuarios a CSV | reportes.administrar + reportes.exportar | - | - | status (query, opt); email_verified (query, opt); blocked (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/export/audit` | Reportes | Exportar auditoría a CSV | reportes.administrar + reportes.exportar | - | - | entity_schema (query, opt); entity_name (query, opt); action (query, opt); origin (query, opt); date_from (query, opt); date_to (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |
| GET | `/api/v1/reports/admin/export/jobs` | Reportes | Exportar trabajos programados a CSV | reportes.administrar + reportes.exportar | - | - | active (query, opt); type (query, opt); last_status (query, opt); limit (query, opt); offset (query, opt) | 200, 422 |

## Schemas registrados

- `AIModelListResponse`
- `AIModelResponse`
- `AIModelStatus`
- `AIModelStatusUpdateRequest`
- `AIModelSummaryResponse`
- `ActiveModelVersionResponse`
- `AdminNotificationListResponse`
- `AnalysisHorizon`
- `AnalysisRequestResponse`
- `AnalysisRequestStatus`
- `AnalysisType`
- `AnswerOptionResponse`
- `AssetAllocationItemResponse`
- `AssetAllocationResponse`
- `AssetAnalysisRequestCreate`
- `AssetAnalysisResultResponse`
- `AssetListResponse`
- `AssetMarketResponse`
- `AssetPredictionProbabilitiesResponse`
- `AssetReportListResponse`
- `AssetReportResponse`
- `AssetResponse`
- `AssetStatus`
- `AssetTypeListResponse`
- `AssetTypeResponse`
- `AssetTypeSummaryResponse`
- `AuditDailyReportListResponse`
- `AuditDailyReportResponse`
- `ClassificationMethod`
- `ContributionFrequency`
- `CreateRiskEvaluationRequest`
- `CurrentRiskProfileResponse`
- `EvaluationAnswerRequest`
- `EvaluationStatus`
- `FinancialIndicatorListResponse`
- `FinancialIndicatorResponse`
- `FinancialIndicatorType`
- `FinancialSourceListResponse`
- `FinancialSourceResponse`
- `HTTPValidationError`
- `HistoricalPriceListResponse`
- `HistoricalPriceResponse`
- `IndicatorCalculationItemResponse`
- `IndicatorCalculationRequest`
- `IndicatorCalculationResponse`
- `IndicatorCalculationSpec`
- `IntegralAnalysisRequestCreate`
- `JobExecutionListResponse`
- `JobExecutionResponse`
- `JobExecutionStatus`
- `JobSummaryResponse`
- `JobTrigger`
- `LatestPriceResponse`
- `LoginRequest`
- `LogoutRequest`
- `MarketListResponse`
- `MarketResponse`
- `ModelVersionCreateRequest`
- `ModelVersionListResponse`
- `ModelVersionResponse`
- `NewsListResponse`
- `NewsProviderSentimentResponse`
- `NewsResponse`
- `NewsSynchronizationResponse`
- `NewsTickerSentimentResponse`
- `NewsTopicResponse`
- `NotificationChannel`
- `NotificationListResponse`
- `NotificationPriority`
- `NotificationResponse`
- `NotificationStatus`
- `NotificationType`
- `OperationJobReportListResponse`
- `OperationJobReportResponse`
- `PortfolioCloseResponse`
- `PortfolioCreateRequest`
- `PortfolioLatestValuationResponse`
- `PortfolioListResponse`
- `PortfolioOverviewResponse`
- `PortfolioReportListResponse`
- `PortfolioReportResponse`
- `PortfolioResponse`
- `PortfolioStatus`
- `PortfolioSummaryResponse`
- `PortfolioType`
- `PortfolioUpdateRequest`
- `PortfolioValuationCreateRequest`
- `PortfolioValuationListResponse`
- `PortfolioValuationResponse`
- `PositionCreateRequest`
- `PositionListResponse`
- `PositionResponse`
- `PositionStatus`
- `PositionUpdateRequest`
- `PriceSourceSummaryResponse`
- `PriceSynchronizationResponse`
- `QuestionResponse`
- `QuestionnaireResponse`
- `RecommendationAssetResponse`
- `RecommendationEvidenceResponse`
- `RecommendationReportListResponse`
- `RecommendationReportResponse`
- `RecommendationRequestCreate`
- `RecommendationResultResponse`
- `RefreshRequest`
- `RegisterRequest`
- `RiskClassification`
- `RiskEvaluationResponse`
- `RiskProfileHistoryItemResponse`
- `RiskProfileHistoryResponse`
- `SectorAllocationItemResponse`
- `SectorAllocationResponse`
- `SentimentAnalysisRequestCreate`
- `SimulationAssetResultResponse`
- `SimulationConfigurationArchiveResponse`
- `SimulationConfigurationAssetCreateRequest`
- `SimulationConfigurationAssetListResponse`
- `SimulationConfigurationAssetResponse`
- `SimulationConfigurationAssetUpdateRequest`
- `SimulationConfigurationCreateRequest`
- `SimulationConfigurationListResponse`
- `SimulationConfigurationReadyResponse`
- `SimulationConfigurationResponse`
- `SimulationConfigurationStatus`
- `SimulationConfigurationUpdateRequest`
- `SimulationDistributionStatusResponse`
- `SimulationExecutionCancelResponse`
- `SimulationExecutionCreateRequest`
- `SimulationExecutionListResponse`
- `SimulationExecutionResponse`
- `SimulationExecutionStatus`
- `SimulationReportListResponse`
- `SimulationReportResponse`
- `SimulationResultResponse`
- `SimulationType`
- `TokenResponse`
- `UnreadNotificationCountResponse`
- `UserReportListResponse`
- `UserReportResponse`
- `UserResponse`
- `ValidationError`

## Fuente

Este documento se genera a partir de `openapi_alphainvest.json`, obtenido de `GET /openapi.json` en una instancia real del backend.

Los permisos RBAC se complementan con las dependencias reales de los módulos de AlphaInvest AI.
