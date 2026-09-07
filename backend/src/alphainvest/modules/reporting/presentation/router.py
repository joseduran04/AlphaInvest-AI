from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Query,
    status,
)
from fastapi.responses import StreamingResponse

from alphainvest.modules.reporting.presentation.dependencies import (
    ReportAdminContext,
    ReportExportContext,
    ReportingExportServiceDependency,
    ReportingServiceDependency,
    ReportReadContext,
)
from alphainvest.modules.reporting.presentation.schemas import (
    AssetReportListResponse,
    AssetReportResponse,
    AuditDailyReportListResponse,
    AuditDailyReportResponse,
    OperationJobReportListResponse,
    OperationJobReportResponse,
    PortfolioReportListResponse,
    PortfolioReportResponse,
    RecommendationReportListResponse,
    RecommendationReportResponse,
    SimulationReportListResponse,
    SimulationReportResponse,
    UserReportListResponse,
    UserReportResponse,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reportes"],
)


ExportLimit = Annotated[
    int,
    Query(
        ge=1,
        le=5000,
    ),
]


def build_csv_response(
    *,
    content: str,
    filename: str,
) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )


# ============================================================
# CONSULTAS DE USUARIO
# ============================================================


@router.get(
    "/assets",
    response_model=AssetReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar reporte de activos",
)
async def list_asset_reports(
    _: ReportReadContext,
    service: ReportingServiceDependency,
    symbol: str | None = Query(default=None),
    market_code: str | None = Query(default=None),
    asset_type_code: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    asset_status: str | None = Query(
        default=None,
        alias="status",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AssetReportListResponse:
    return await service.list_assets(
        symbol=symbol,
        market_code=market_code,
        asset_type_code=asset_type_code,
        sector=sector,
        status=asset_status,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/portfolios",
    response_model=PortfolioReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar mis reportes de portafolios",
)
async def list_portfolio_reports(
    context: ReportReadContext,
    service: ReportingServiceDependency,
    portfolio_status: str | None = Query(
        default=None,
        alias="status",
    ),
    portfolio_type: str | None = Query(
        default=None,
        alias="type",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> PortfolioReportListResponse:
    return await service.list_portfolios(
        user_id=context.user.id,
        status=portfolio_status,
        portfolio_type=portfolio_type,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/simulations",
    response_model=SimulationReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar mis reportes de simulaciones",
)
async def list_simulation_reports(
    context: ReportReadContext,
    service: ReportingServiceDependency,
    simulation_status: str | None = Query(
        default=None,
        alias="status",
    ),
    simulation_type: str | None = Query(
        default=None,
        alias="type",
    ),
    date_from: date | None = Query(
        default=None,
    ),
    date_to: date | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> SimulationReportListResponse:
    return await service.list_simulations(
        user_id=context.user.id,
        status=simulation_status,
        simulation_type=simulation_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/recommendations",
    response_model=RecommendationReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar mis reportes de recomendaciones",
)
async def list_recommendation_reports(
    context: ReportReadContext,
    service: ReportingServiceDependency,
    recommendation_type: str | None = Query(
        default=None,
        alias="type",
    ),
    risk_level: str | None = Query(
        default=None,
    ),
    horizon: str | None = Query(
        default=None,
    ),
    recommendation_status: str | None = Query(
        default=None,
        alias="status",
    ),
    date_from: date | None = Query(
        default=None,
    ),
    date_to: date | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> RecommendationReportListResponse:
    return await service.list_recommendations(
        user_id=context.user.id,
        recommendation_type=recommendation_type,
        risk_level=risk_level,
        horizon=horizon,
        status=recommendation_status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


# ============================================================
# EXPORTACIONES DE USUARIO
# ============================================================


@router.get(
    "/export/assets",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar reporte de activos a CSV",
)
async def export_asset_reports(
    _: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    symbol: str | None = Query(default=None),
    market_code: str | None = Query(default=None),
    asset_type_code: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    asset_status: str | None = Query(
        default=None,
        alias="status",
    ),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_assets(
        symbol=symbol,
        market_code=market_code,
        asset_type_code=asset_type_code,
        sector=sector,
        status=asset_status,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=AssetReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="assets_report.csv",
    )


@router.get(
    "/export/portfolios",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar mis portafolios a CSV",
)
async def export_portfolio_reports(
    context: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    portfolio_status: str | None = Query(
        default=None,
        alias="status",
    ),
    portfolio_type: str | None = Query(
        default=None,
        alias="type",
    ),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_portfolios(
        user_id=context.user.id,
        status=portfolio_status,
        portfolio_type=portfolio_type,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=PortfolioReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="portfolios_report.csv",
    )


@router.get(
    "/export/simulations",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar mis simulaciones a CSV",
)
async def export_simulation_reports(
    context: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    simulation_status: str | None = Query(
        default=None,
        alias="status",
    ),
    simulation_type: str | None = Query(
        default=None,
        alias="type",
    ),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_simulations(
        user_id=context.user.id,
        status=simulation_status,
        simulation_type=simulation_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=SimulationReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="simulations_report.csv",
    )


@router.get(
    "/export/recommendations",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar mis recomendaciones a CSV",
)
async def export_recommendation_reports(
    context: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    recommendation_type: str | None = Query(
        default=None,
        alias="type",
    ),
    risk_level: str | None = Query(default=None),
    horizon: str | None = Query(default=None),
    recommendation_status: str | None = Query(
        default=None,
        alias="status",
    ),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_recommendations(
        user_id=context.user.id,
        recommendation_type=recommendation_type,
        risk_level=risk_level,
        horizon=horizon,
        status=recommendation_status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=RecommendationReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="recommendations_report.csv",
    )


# ============================================================
# REPORTES ADMINISTRATIVOS
# ============================================================


@router.get(
    "/admin/users",
    response_model=UserReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar reporte administrativo de usuarios",
)
async def list_user_reports(
    _: ReportAdminContext,
    service: ReportingServiceDependency,
    user_status: str | None = Query(
        default=None,
        alias="status",
    ),
    email_verified: bool | None = Query(
        default=None,
    ),
    blocked: bool | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> UserReportListResponse:
    return await service.list_users(
        status=user_status,
        email_verified=email_verified,
        blocked=blocked,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/admin/audit",
    response_model=AuditDailyReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar reporte administrativo de auditoría",
)
async def list_audit_reports(
    _: ReportAdminContext,
    service: ReportingServiceDependency,
    entity_schema: str | None = Query(
        default=None,
    ),
    entity_name: str | None = Query(
        default=None,
    ),
    action: str | None = Query(
        default=None,
    ),
    origin: str | None = Query(
        default=None,
    ),
    date_from: date | None = Query(
        default=None,
    ),
    date_to: date | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> AuditDailyReportListResponse:
    return await service.list_daily_audit(
        entity_schema=entity_schema,
        entity_name=entity_name,
        action=action,
        origin=origin,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/admin/jobs",
    response_model=OperationJobReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar reporte administrativo de trabajos",
)
async def list_operation_job_reports(
    _: ReportAdminContext,
    service: ReportingServiceDependency,
    active: bool | None = Query(
        default=None,
    ),
    job_type: str | None = Query(
        default=None,
        alias="type",
    ),
    last_status: str | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> OperationJobReportListResponse:
    return await service.list_operation_jobs(
        active=active,
        job_type=job_type,
        last_status=last_status,
        limit=limit,
        offset=offset,
    )


# ============================================================
# EXPORTACIONES ADMINISTRATIVAS
# ============================================================


@router.get(
    "/admin/export/users",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar usuarios a CSV",
)
async def export_user_reports(
    _: ReportAdminContext,
    __: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    user_status: str | None = Query(
        default=None,
        alias="status",
    ),
    email_verified: bool | None = Query(default=None),
    blocked: bool | None = Query(default=None),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_users(
        status=user_status,
        email_verified=email_verified,
        blocked=blocked,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=UserReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="users_report.csv",
    )


@router.get(
    "/admin/export/audit",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar auditoría a CSV",
)
async def export_audit_reports(
    _: ReportAdminContext,
    __: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    entity_schema: str | None = Query(default=None),
    entity_name: str | None = Query(default=None),
    action: str | None = Query(default=None),
    origin: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_daily_audit(
        entity_schema=entity_schema,
        entity_name=entity_name,
        action=action,
        origin=origin,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=AuditDailyReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="audit_report.csv",
    )


@router.get(
    "/admin/export/jobs",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Exportar trabajos programados a CSV",
)
async def export_operation_job_reports(
    _: ReportAdminContext,
    __: ReportExportContext,
    service: ReportingServiceDependency,
    export_service: ReportingExportServiceDependency,
    active: bool | None = Query(default=None),
    job_type: str | None = Query(
        default=None,
        alias="type",
    ),
    last_status: str | None = Query(default=None),
    limit: ExportLimit = 5000,
    offset: int = Query(
        default=0,
        ge=0,
    ),
) -> StreamingResponse:
    report = await service.list_operation_jobs(
        active=active,
        job_type=job_type,
        last_status=last_status,
        limit=limit,
        offset=offset,
    )

    content = export_service.build_csv(
        items=report.items,
        schema=OperationJobReportResponse,
    )

    return build_csv_response(
        content=content,
        filename="operation_jobs_report.csv",
    )