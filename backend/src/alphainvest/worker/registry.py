from collections.abc import Awaitable, Callable

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.ai_analysis_requests import (
    process_pending_asset_analysis_requests,
)
from alphainvest.worker.jobs.integral_analysis_requests import (
    process_pending_integral_analysis_requests,
)
from alphainvest.worker.jobs.market_indicators import (
    calculate_configured_market_indicators,
)
from alphainvest.worker.jobs.market_prices import (
    synchronize_configured_market_prices,
)
from alphainvest.worker.jobs.news import (
    synchronize_configured_news,
)
from alphainvest.worker.jobs.recommendation_requests import (
    process_pending_recommendation_requests,
)
from alphainvest.worker.jobs.sentiment_analysis_requests import (
    process_pending_sentiment_analysis_requests,
)
from alphainvest.worker.jobs.simulation_executions import (
    process_pending_simulation_executions,
)

WorkerJob = Callable[[Settings], Awaitable[None]]

WORKER_JOB_REGISTRY: dict[str, WorkerJob] = {
    "ACTUALIZAR_PRECIOS_DIARIOS": (
        synchronize_configured_market_prices
    ),
    "CALCULAR_INDICADORES_DIARIOS": (
        calculate_configured_market_indicators
    ),
    "PROCESAR_SIMULACIONES_PENDIENTES": (
        process_pending_simulation_executions
    ),
    "PROCESAR_ANALISIS_ACTIVOS_PENDIENTES": (
        process_pending_asset_analysis_requests
    ),
    "SINCRONIZAR_NOTICIAS": (
        synchronize_configured_news
    ),
    "PROCESAR_ANALISIS_SENTIMIENTO_PENDIENTES": (
        process_pending_sentiment_analysis_requests
    ),
    "PROCESAR_RECOMENDACIONES_PENDIENTES": (
        process_pending_recommendation_requests
    ),
    "PROCESAR_ANALISIS_INTEGRALES_PENDIENTES": (
        process_pending_integral_analysis_requests
    ),
}