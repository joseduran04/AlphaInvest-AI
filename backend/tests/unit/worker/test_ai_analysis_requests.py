from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)


def test_ai_analysis_job_is_registered() -> None:
    assert (
        "PROCESAR_ANALISIS_ACTIVOS_PENDIENTES"
        in WORKER_JOB_REGISTRY
    )