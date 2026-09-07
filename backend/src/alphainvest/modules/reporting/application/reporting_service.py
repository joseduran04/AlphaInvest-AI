from datetime import date
from uuid import UUID

from alphainvest.modules.reporting.infrastructure.repository import (
    ReportingRepository,
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


class ReportingService:
    """Casos de uso de consulta para reportes."""

    def __init__(
        self,
        repository: ReportingRepository,
    ) -> None:
        self._repository = repository

    async def list_assets(
        self,
        *,
        symbol: str | None,
        market_code: str | None,
        asset_type_code: str | None,
        sector: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> AssetReportListResponse:
        items, total = await self._repository.list_assets(
            symbol=symbol,
            market_code=market_code,
            asset_type_code=asset_type_code,
            sector=sector,
            status=status,
            limit=limit,
            offset=offset,
        )

        return AssetReportListResponse(
            items=[
                AssetReportResponse.model_validate(item)
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_portfolios(
        self,
        *,
        user_id: UUID,
        status: str | None,
        portfolio_type: str | None,
        limit: int,
        offset: int,
    ) -> PortfolioReportListResponse:
        items, total = (
            await self._repository.list_portfolios_for_user(
                user_id=user_id,
                status=status,
                portfolio_type=portfolio_type,
                limit=limit,
                offset=offset,
            )
        )

        return PortfolioReportListResponse(
            items=[
                PortfolioReportResponse.model_validate(item)
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_simulations(
        self,
        *,
        user_id: UUID,
        status: str | None,
        simulation_type: str | None,
        date_from: date | None,
        date_to: date | None,
        limit: int,
        offset: int,
    ) -> SimulationReportListResponse:
        items, total = (
            await self._repository.list_simulations_for_user(
                user_id=user_id,
                status=status,
                simulation_type=simulation_type,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        )

        return SimulationReportListResponse(
            items=[
                SimulationReportResponse.model_validate(item)
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_recommendations(
        self,
        *,
        user_id: UUID,
        recommendation_type: str | None,
        risk_level: str | None,
        horizon: str | None,
        status: str | None,
        date_from: date | None,
        date_to: date | None,
        limit: int,
        offset: int,
    ) -> RecommendationReportListResponse:
        items, total = (
            await self._repository.list_recommendations_for_user(
                user_id=user_id,
                recommendation_type=recommendation_type,
                risk_level=risk_level,
                horizon=horizon,
                status=status,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        )

        return RecommendationReportListResponse(
            items=[
                RecommendationReportResponse.model_validate(
                    item
                )
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_users(
        self,
        *,
        status: str | None,
        email_verified: bool | None,
        blocked: bool | None,
        limit: int,
        offset: int,
    ) -> UserReportListResponse:
        items, total = await self._repository.list_users(
            status=status,
            email_verified=email_verified,
            blocked=blocked,
            limit=limit,
            offset=offset,
        )

        return UserReportListResponse(
            items=[
                UserReportResponse.model_validate(item)
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_daily_audit(
        self,
        *,
        entity_schema: str | None,
        entity_name: str | None,
        action: str | None,
        origin: str | None,
        date_from: date | None,
        date_to: date | None,
        limit: int,
        offset: int,
    ) -> AuditDailyReportListResponse:
        items, total = (
            await self._repository.list_daily_audit(
                entity_schema=entity_schema,
                entity_name=entity_name,
                action=action,
                origin=origin,
                date_from=date_from,
                date_to=date_to,
                limit=limit,
                offset=offset,
            )
        )

        return AuditDailyReportListResponse(
            items=[
                AuditDailyReportResponse.model_validate(item)
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def list_operation_jobs(
        self,
        *,
        active: bool | None,
        job_type: str | None,
        last_status: str | None,
        limit: int,
        offset: int,
    ) -> OperationJobReportListResponse:
        items, total = (
            await self._repository.list_operation_jobs(
                active=active,
                job_type=job_type,
                last_status=last_status,
                limit=limit,
                offset=offset,
            )
        )

        return OperationJobReportListResponse(
            items=[
                OperationJobReportResponse.model_validate(
                    item
                )
                for item in items
            ],
            total=total,
            limit=limit,
            offset=offset,
        )