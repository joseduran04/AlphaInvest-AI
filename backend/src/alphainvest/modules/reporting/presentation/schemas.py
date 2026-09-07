from datetime import date as Date
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssetReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID | None = Field(
        validation_alias="activo_id"
    )
    symbol: str | None = Field(
        validation_alias="simbolo"
    )
    asset_name: str | None = Field(
        validation_alias="activo_nombre"
    )
    description: str | None = Field(
        validation_alias="descripcion"
    )
    currency: str | None = Field(
        validation_alias="moneda"
    )
    sector: str | None = None
    industry: str | None = Field(
        default=None,
        validation_alias="industria",
    )
    isin: str | None = None
    asset_status: str | None = Field(
        validation_alias="activo_estado"
    )

    market_id: UUID | None = Field(
        validation_alias="mercado_id"
    )
    market_code: str | None = Field(
        validation_alias="mercado_codigo"
    )
    market_name: str | None = Field(
        validation_alias="mercado_nombre"
    )
    market_country: str | None = Field(
        validation_alias="mercado_pais"
    )
    market_timezone: str | None = Field(
        validation_alias="mercado_zona_horaria"
    )

    asset_type_id: UUID | None = Field(
        validation_alias="tipo_activo_id"
    )
    asset_type_code: str | None = Field(
        validation_alias="tipo_activo_codigo"
    )
    asset_type_name: str | None = Field(
        validation_alias="tipo_activo_nombre"
    )

    price_date: Date | None = Field(
        validation_alias="fecha_precio"
    )
    open_price: Decimal | None = Field(
        validation_alias="apertura"
    )
    high_price: Decimal | None = Field(
        validation_alias="maximo"
    )
    low_price: Decimal | None = Field(
        validation_alias="minimo"
    )
    close_price: Decimal | None = Field(
        validation_alias="cierre"
    )
    adjusted_close: Decimal | None = Field(
        validation_alias="cierre_ajustado"
    )
    volume: Decimal | None = Field(
        validation_alias="volumen"
    )

    source_id: UUID | None = Field(
        validation_alias="fuente_id"
    )
    source_name: str | None = Field(
        validation_alias="fuente_nombre"
    )
    source_provider: str | None = Field(
        validation_alias="fuente_proveedor"
    )

    price_registered_at: datetime | None = Field(
        validation_alias="precio_fecha_registro"
    )
    daily_change_percentage: Decimal | None = Field(
        validation_alias=(
            "variacion_diaria_porcentaje"
        )
    )
    price_age_days: int | None = Field(
        validation_alias="antiguedad_precio_dias"
    )


class AssetReportListResponse(BaseModel):
    items: list[AssetReportResponse]
    total: int
    limit: int
    offset: int


class PortfolioReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    portfolio_id: UUID | None = Field(
        validation_alias="portafolio_id"
    )
    user_id: UUID | None = Field(
        validation_alias="usuario_id"
    )
    first_names: str | None = Field(
        validation_alias="nombres"
    )
    last_names: str | None = Field(
        validation_alias="apellidos"
    )
    email: str | None = Field(
        validation_alias="correo"
    )

    portfolio_name: str | None = Field(
        validation_alias="portafolio_nombre"
    )
    description: str | None = Field(
        default=None,
        validation_alias="descripcion",
    )
    base_currency: str | None = Field(
        validation_alias="moneda_base"
    )

    initial_capital: Decimal | None = Field(
        validation_alias="capital_inicial"
    )
    cash_balance: Decimal | None = Field(
        validation_alias="saldo_efectivo"
    )
    type: str | None = Field(
        validation_alias="tipo"
    )
    status: str | None = Field(
        validation_alias="estado"
    )

    start_date: Date | None = Field(
        validation_alias="fecha_inicio"
    )
    close_date: Date | None = Field(
        validation_alias="fecha_cierre"
    )
    created_at: datetime | None = Field(
        validation_alias="fecha_creacion"
    )
    updated_at: datetime | None = Field(
        validation_alias="fecha_actualizacion"
    )

    open_positions: int | None = Field(
        validation_alias="posiciones_abiertas"
    )
    total_positions: int | None = Field(
        validation_alias="posiciones_totales"
    )

    invested_capital: Decimal | None = Field(
        validation_alias="capital_invertido"
    )
    positions_value: Decimal | None = Field(
        validation_alias="valor_posiciones"
    )
    estimated_total_value: Decimal | None = Field(
        validation_alias="valor_total_estimado"
    )
    positions_profit_loss: Decimal | None = Field(
        validation_alias=(
            "ganancia_perdida_posiciones"
        )
    )
    estimated_return_percentage: Decimal | None = (
        Field(
            validation_alias=(
                "rendimiento_estimado_porcentaje"
            )
        )
    )

    last_valuation_at: datetime | None = Field(
        validation_alias="ultima_valoracion_fecha"
    )
    last_total_value: Decimal | None = Field(
        validation_alias="ultimo_valor_total"
    )
    last_profit_loss: Decimal | None = Field(
        validation_alias="ultima_ganancia_perdida"
    )
    last_return_percentage: Decimal | None = Field(
        validation_alias=(
            "ultimo_rendimiento_porcentaje"
        )
    )


class PortfolioReportListResponse(BaseModel):
    items: list[PortfolioReportResponse]
    total: int
    limit: int
    offset: int


class SimulationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    execution_id: UUID | None = Field(
        validation_alias="ejecucion_id"
    )
    configuration_id: UUID | None = Field(
        validation_alias="configuracion_id"
    )
    configuration_name: str | None = Field(
        validation_alias="configuracion_nombre"
    )
    simulation_type: str | None = Field(
        validation_alias="tipo_simulacion"
    )
    configured_capital: Decimal | None = Field(
        validation_alias="capital_configurado"
    )
    base_currency: str | None = Field(
        validation_alias="moneda_base"
    )

    period_start: Date | None = Field(
        validation_alias="periodo_inicio"
    )
    period_end: Date | None = Field(
        validation_alias="periodo_fin"
    )

    user_id: UUID | None = Field(
        validation_alias="usuario_id"
    )
    first_names: str | None = Field(
        validation_alias="nombres"
    )
    last_names: str | None = Field(
        validation_alias="apellidos"
    )
    email: str | None = Field(
        validation_alias="correo"
    )

    model_version_id: UUID | None = Field(
        validation_alias="version_modelo_id"
    )
    model_version: str | None = Field(
        validation_alias="version_modelo"
    )
    model_code: str | None = Field(
        validation_alias="modelo_codigo"
    )
    model_name: str | None = Field(
        validation_alias="modelo_nombre"
    )

    status: str | None = Field(
        validation_alias="estado"
    )
    progress_percentage: Decimal | None = Field(
        validation_alias="porcentaje_progreso"
    )

    requested_at: datetime | None = Field(
        validation_alias="fecha_solicitud"
    )
    started_at: datetime | None = Field(
        validation_alias="fecha_inicio"
    )
    finished_at: datetime | None = Field(
        validation_alias="fecha_fin"
    )

    error_message: str | None = Field(
        validation_alias="mensaje_error"
    )
    process_id: str | None = Field(
        validation_alias="identificador_proceso"
    )

    result_id: UUID | None = Field(
        validation_alias="resultado_id"
    )
    final_capital: Decimal | None = Field(
        validation_alias="capital_final"
    )
    profit_loss: Decimal | None = Field(
        validation_alias="ganancia_perdida"
    )
    total_return_percentage: Decimal | None = Field(
        validation_alias=(
            "rendimiento_total_porcentaje"
        )
    )
    annualized_return_percentage: Decimal | None = (
        Field(
            validation_alias=(
                "rendimiento_anualizado_porcentaje"
            )
        )
    )
    annualized_volatility: Decimal | None = Field(
        validation_alias="volatilidad_anualizada"
    )
    sharpe_ratio: Decimal | None = Field(
        validation_alias="indice_sharpe"
    )
    max_drawdown_percentage: Decimal | None = Field(
        validation_alias=(
            "maximo_drawdown_porcentaje"
        )
    )
    value_at_risk: Decimal | None = Field(
        validation_alias="valor_en_riesgo"
    )
    gain_probability: Decimal | None = Field(
        validation_alias="probabilidad_ganancia"
    )

    result_at: datetime | None = Field(
        validation_alias="fecha_resultado"
    )
    duration_seconds: Decimal | None = Field(
        validation_alias="duracion_segundos"
    )
    result_available: bool | None = Field(
        validation_alias="resultado_disponible"
    )


class SimulationReportListResponse(BaseModel):
    items: list[SimulationReportResponse]
    total: int
    limit: int
    offset: int


class RecommendationReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: UUID | None = Field(
        validation_alias="recomendacion_id"
    )
    request_id: UUID | None = Field(
        validation_alias="solicitud_id"
    )
    user_id: UUID | None = Field(
        validation_alias="usuario_id"
    )
    first_names: str | None = Field(
        validation_alias="nombres"
    )
    last_names: str | None = Field(
        validation_alias="apellidos"
    )
    email: str | None = Field(
        validation_alias="correo"
    )

    risk_profile_id: UUID | None = Field(
        validation_alias="perfil_riesgo_id"
    )
    portfolio_id: UUID | None = Field(
        validation_alias="portafolio_id"
    )
    portfolio_name: str | None = Field(
        validation_alias="portafolio_nombre"
    )

    model_version_id: UUID | None = Field(
        validation_alias="version_modelo_id"
    )
    model_version: str | None = Field(
        validation_alias="version_modelo"
    )
    model_code: str | None = Field(
        validation_alias="modelo_codigo"
    )
    model_name: str | None = Field(
        validation_alias="modelo_nombre"
    )

    type: str | None = Field(
        validation_alias="tipo"
    )
    title: str | None = Field(
        validation_alias="titulo"
    )
    summary: str | None = Field(
        validation_alias="resumen"
    )
    justification: str | None = Field(
        validation_alias="justificacion"
    )
    risk_level: str | None = Field(
        validation_alias="nivel_riesgo"
    )
    horizon: str | None = Field(
        validation_alias="horizonte"
    )
    confidence: Decimal | None = Field(
        validation_alias="confianza"
    )
    priority: int | None = Field(
        validation_alias="prioridad"
    )
    status: str | None = Field(
        validation_alias="estado"
    )
    warning: str | None = Field(
        validation_alias="advertencia"
    )

    generated_at: datetime | None = Field(
        validation_alias="fecha_generacion"
    )
    expires_at: datetime | None = Field(
        validation_alias="fecha_expiracion"
    )
    accepted_at: datetime | None = Field(
        validation_alias="fecha_aceptacion"
    )
    rejected_at: datetime | None = Field(
        validation_alias="fecha_rechazo"
    )

    related_asset_count: int | None = Field(
        validation_alias="total_activos_relacionados"
    )
    asset_symbols: list[str] | None = Field(
        validation_alias="simbolos_activos"
    )
    expired_by_date: bool | None = Field(
        validation_alias="expirada_por_fecha"
    )


class RecommendationReportListResponse(BaseModel):
    items: list[RecommendationReportResponse]
    total: int
    limit: int
    offset: int


class UserReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID | None = Field(
        validation_alias="usuario_id"
    )
    first_names: str | None = Field(
        validation_alias="nombres"
    )
    last_names: str | None = Field(
        validation_alias="apellidos"
    )
    email: str | None = Field(
        validation_alias="correo"
    )
    status: str | None = Field(
        validation_alias="estado"
    )
    email_verified: bool | None = Field(
        validation_alias="correo_verificado"
    )
    failed_attempts: int | None = Field(
        validation_alias="intentos_fallidos"
    )
    blocked_until: datetime | None = Field(
        validation_alias="bloqueado_hasta"
    )
    last_access_at: datetime | None = Field(
        validation_alias="ultimo_acceso"
    )
    created_at: datetime | None = Field(
        validation_alias="fecha_creacion"
    )
    updated_at: datetime | None = Field(
        validation_alias="fecha_actualizacion"
    )
    roles: list[str] | None = None
    total_roles: int | None = None
    currently_blocked: bool | None = Field(
        validation_alias="bloqueado_actualmente"
    )


class UserReportListResponse(BaseModel):
    items: list[UserReportResponse]
    total: int
    limit: int
    offset: int


class AuditDailyReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: Date | None = Field(
        validation_alias="fecha"
    )
    entity_schema: str | None = Field(
        validation_alias="esquema_entidad"
    )
    entity_name: str | None = Field(
        validation_alias="nombre_entidad"
    )
    action: str | None = Field(
        validation_alias="accion"
    )
    origin: str | None = Field(
        validation_alias="origen"
    )
    total_events: int | None = Field(
        validation_alias="total_eventos"
    )
    involved_users: int | None = Field(
        validation_alias="usuarios_involucrados"
    )
    events_without_user: int | None = Field(
        validation_alias="eventos_sin_usuario"
    )
    first_event_at: datetime | None = Field(
        validation_alias="primer_evento"
    )
    last_event_at: datetime | None = Field(
        validation_alias="ultimo_evento"
    )


class AuditDailyReportListResponse(BaseModel):
    items: list[AuditDailyReportResponse]
    total: int
    limit: int
    offset: int


class OperationJobReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID | None = Field(
        validation_alias="trabajo_id"
    )
    code: str | None = Field(
        validation_alias="codigo"
    )
    name: str | None = Field(
        validation_alias="nombre"
    )
    description: str | None = Field(
        validation_alias="descripcion"
    )
    type: str | None = Field(
        validation_alias="tipo"
    )
    active: bool | None = Field(
        validation_alias="activo"
    )

    cron_expression: str | None = Field(
        validation_alias="expresion_cron"
    )
    interval_seconds: int | None = Field(
        validation_alias="intervalo_segundos"
    )
    timezone: str | None = Field(
        validation_alias="zona_horaria"
    )
    allows_concurrency: bool | None = Field(
        validation_alias="permite_concurrencia"
    )
    timeout_seconds: int | None = Field(
        validation_alias="tiempo_maximo_segundos"
    )
    max_retries: int | None = Field(
        validation_alias="maximo_reintentos"
    )

    next_execution_at: datetime | None = Field(
        validation_alias="siguiente_ejecucion"
    )
    last_execution_at: datetime | None = Field(
        validation_alias="ultima_ejecucion"
    )
    last_execution_id: UUID | None = Field(
        validation_alias="ultima_ejecucion_id"
    )
    last_execution_status: str | None = Field(
        validation_alias="ultima_ejecucion_estado"
    )
    last_execution_attempt: int | None = Field(
        validation_alias="ultima_ejecucion_intento"
    )
    last_execution_trigger: str | None = Field(
        validation_alias=(
            "ultima_ejecucion_disparador"
        )
    )

    last_execution_requested_at: datetime | None = (
        Field(
            validation_alias=(
                "ultima_ejecucion_fecha_solicitud"
            )
        )
    )
    last_execution_started_at: datetime | None = Field(
        validation_alias=(
            "ultima_ejecucion_fecha_inicio"
        )
    )
    last_execution_finished_at: datetime | None = (
        Field(
            validation_alias=(
                "ultima_ejecucion_fecha_fin"
            )
        )
    )
    last_execution_progress: Decimal | None = Field(
        validation_alias="ultima_ejecucion_progreso"
    )

    processed_records: int | None = Field(
        validation_alias="registros_procesados"
    )
    successful_records: int | None = Field(
        validation_alias="registros_exitosos"
    )
    failed_records: int | None = Field(
        validation_alias="registros_fallidos"
    )
    last_execution_error: str | None = Field(
        validation_alias="ultima_ejecucion_error"
    )

    total_executions: int | None = Field(
        validation_alias="total_ejecuciones"
    )
    completed_executions: int | None = Field(
        validation_alias="ejecuciones_completadas"
    )
    failed_executions: int | None = Field(
        validation_alias="ejecuciones_fallidas"
    )
    cancelled_executions: int | None = Field(
        validation_alias="ejecuciones_canceladas"
    )
    running_executions: int | None = Field(
        validation_alias="ejecuciones_en_curso"
    )

    average_duration_seconds: Decimal | None = Field(
        validation_alias="duracion_promedio_segundos"
    )
    last_request_at: datetime | None = Field(
        validation_alias="ultima_solicitud"
    )
    last_completion_at: datetime | None = Field(
        validation_alias="ultima_finalizacion"
    )
    success_rate_percentage: Decimal | None = Field(
        validation_alias="tasa_exito_porcentaje"
    )


class OperationJobReportListResponse(BaseModel):
    items: list[OperationJobReportResponse]
    total: int
    limit: int
    offset: int