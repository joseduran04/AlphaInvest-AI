from datetime import date
from decimal import Decimal
from typing import cast
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.portfolio.domain.enums import (
    PortfolioStatus,
)
from alphainvest.modules.portfolio.domain.exceptions import (
    PortfolioAssetNotFoundError,
    PortfolioAssetUnavailableError,
    PortfolioNameAlreadyExistsError,
    PortfolioNotFoundError,
    PortfolioUnavailableError,
    PositionAlreadyExistsError,
    PositionNotFoundError,
)
from alphainvest.modules.portfolio.infrastructure.models import (
    PortfolioModel,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)
from alphainvest.modules.portfolio.presentation.schemas import (
    AssetAllocationItemResponse,
    AssetAllocationResponse,
    PortfolioCloseResponse,
    PortfolioCreateRequest,
    PortfolioLatestValuationResponse,
    PortfolioListResponse,
    PortfolioOverviewResponse,
    PortfolioResponse,
    PortfolioSummaryResponse,
    PortfolioUpdateRequest,
    PortfolioValuationCreateRequest,
    PortfolioValuationListResponse,
    PortfolioValuationResponse,
    PositionCreateRequest,
    PositionListResponse,
    PositionResponse,
    PositionUpdateRequest,
    SectorAllocationItemResponse,
    SectorAllocationResponse,
)


class PortfolioService:
    """Casos de uso básicos de portafolios."""

    def __init__(
        self,
        repository: PortfolioRepository,
        market_repository: MarketRepository | None = None,
    ) -> None:
        self._repository = repository
        self._market_repository = market_repository

    def _get_market_repository(
        self,
    ) -> MarketRepository:
        if self._market_repository is None:
            raise RuntimeError(
                "El repositorio de mercado "
                "no está configurado"
            )

        return self._market_repository

    async def _get_active_portfolio(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioModel:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        if portfolio.estado != PortfolioStatus.ACTIVE.value:
            raise PortfolioUnavailableError(
                "Solo pueden administrarse "
                "posiciones de portafolios activos"
            )

        return portfolio

    async def create_portfolio(
        self,
        *,
        user_id: UUID,
        request: PortfolioCreateRequest,
    ) -> PortfolioResponse:
        existing = (
            await self._repository
            .get_by_name_for_user(
                user_id=user_id,
                name=request.nombre,
            )
        )

        if existing is not None:
            raise PortfolioNameAlreadyExistsError(
                "Ya existe un portafolio con ese nombre"
            )

        try:
            portfolio = await self._repository.create(
                user_id=user_id,
                name=request.nombre,
                description=request.descripcion,
                base_currency=request.moneda_base,
                initial_capital=request.capital_inicial,
                portfolio_type=request.tipo.value,
                start_date=request.fecha_inicio,
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise PortfolioNameAlreadyExistsError(
                "Ya existe un portafolio con ese nombre"
            ) from error

        return PortfolioResponse.model_validate(
            portfolio
        )

    async def list_portfolios(
        self,
        *,
        user_id: UUID,
        status: PortfolioStatus | None,
        limit: int,
        offset: int,
    ) -> PortfolioListResponse:
        portfolios, total = (
            await self._repository.list_for_user(
                user_id=user_id,
                status=(
                    status.value
                    if status is not None
                    else None
                ),
                limit=limit,
                offset=offset,
            )
        )

        return PortfolioListResponse(
            items=[
                PortfolioResponse.model_validate(
                    portfolio
                )
                for portfolio in portfolios
            ],
            total=total,
            limit=limit,
            offset=offset,
            estado=status,
        )

    async def get_portfolio(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        return PortfolioResponse.model_validate(
            portfolio
        )

    async def get_portfolio_summary(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioOverviewResponse:
        summary_data = (
            await self._repository
            .get_portfolio_summary(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if summary_data is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        initial_capital = cast(
            Decimal,
            summary_data["capital_inicial"],
        )
        estimated_total = cast(
            Decimal,
            summary_data["valor_total_estimado"],
        )

        total_profit_loss = (
            estimated_total - initial_capital
        )

        estimated_return = (
            None
            if initial_capital == 0
            else (
                total_profit_loss
                / initial_capital
                * Decimal("100")
            )
        )

        summary = (
            PortfolioSummaryResponse.model_validate(
                {
                    **summary_data,
                    "ganancia_perdida_total": (
                        total_profit_loss
                    ),
                    (
                        "rendimiento_estimado_"
                        "porcentaje"
                    ): estimated_return,
                }
            )
        )

        valuation_data = (
            await self._repository
            .get_latest_valuation(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        latest_valuation = (
            PortfolioLatestValuationResponse
            .model_validate(valuation_data)
            if valuation_data is not None
            else None
        )

        return PortfolioOverviewResponse(
            resumen=summary,
            ultima_valoracion=latest_valuation,
        )

    async def get_asset_allocation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> AssetAllocationResponse:
        summary_data = (
            await self._repository
            .get_portfolio_summary(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if summary_data is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        allocation_data = (
            await self._repository
            .get_asset_allocation(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        items = [
            AssetAllocationItemResponse
            .model_validate(item)
            for item in allocation_data
        ]

        total_value = sum(
            (
                item.valor_referencia
                for item in items
            ),
            start=Decimal("0"),
        )

        return AssetAllocationResponse(
            portafolio_id=portfolio_id,
            moneda_base=cast(
                str,
                summary_data["moneda_base"],
            ),
            valor_total_distribuido=total_value,
            items=items,
        )

    async def get_sector_allocation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> SectorAllocationResponse:
        summary_data = (
            await self._repository
            .get_portfolio_summary(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if summary_data is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        allocation_data = (
            await self._repository
            .get_sector_allocation(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        items = [
            SectorAllocationItemResponse
            .model_validate(item)
            for item in allocation_data
        ]

        total_value = sum(
            (
                item.valor_referencia
                for item in items
            ),
            start=Decimal("0"),
        )

        return SectorAllocationResponse(
            portafolio_id=portfolio_id,
            moneda_base=cast(
                str,
                summary_data["moneda_base"],
            ),
            valor_total_distribuido=total_value,
            items=items,
        )

    async def register_portfolio_valuation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        request: PortfolioValuationCreateRequest,
    ) -> PortfolioValuationResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        valuation_id = (
            await self._repository
            .register_valuation(
                portfolio_id=portfolio_id,
                valuation_date=request.fecha_hora,
                details=request.detalle,
            )
        )

        valuation = (
            await self._repository
            .get_valuation_by_id(
                valuation_id=valuation_id,
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if valuation is None:
            await self._repository.rollback()

            raise RuntimeError(
                "No fue posible recuperar "
                "la valoración registrada"
            )

        await self._repository.commit()

        return PortfolioValuationResponse.model_validate(
            valuation
        )

    async def list_portfolio_valuations(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> PortfolioValuationListResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        valuations, total = (
            await self._repository.list_valuations(
                portfolio_id=portfolio_id,
                user_id=user_id,
                limit=limit,
                offset=offset,
            )
        )

        return PortfolioValuationListResponse(
            items=[
                PortfolioValuationResponse
                .model_validate(valuation)
                for valuation in valuations
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_portfolio(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        request: PortfolioUpdateRequest,
    ) -> PortfolioResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        if portfolio.estado != PortfolioStatus.ACTIVE.value:
            raise PortfolioUnavailableError(
                "Solo pueden actualizarse "
                "portafolios activos"
            )

        if (
            request.nombre is not None
            and request.nombre.lower()
            != portfolio.nombre.lower()
        ):
            existing = (
                await self._repository
                .get_by_name_for_user(
                    user_id=user_id,
                    name=request.nombre,
                )
            )

            if existing is not None:
                raise PortfolioNameAlreadyExistsError(
                    "Ya existe un portafolio "
                    "con ese nombre"
                )

        try:
            updated = await self._repository.update(
                portfolio,
                name=request.nombre,
                description=request.descripcion,
                description_was_sent=(
                    "descripcion"
                    in request.model_fields_set
                ),
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise PortfolioNameAlreadyExistsError(
                "Ya existe un portafolio "
                "con ese nombre"
            ) from error

        return PortfolioResponse.model_validate(
            updated
        )

    async def close_portfolio(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioCloseResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        if portfolio.estado != PortfolioStatus.ACTIVE.value:
            raise PortfolioUnavailableError(
                "El portafolio no está activo"
            )

        open_positions = [
            position
            for position in portfolio.posiciones
            if position.estado == "ABIERTA"
            and position.cantidad > 0
        ]

        if open_positions:
            raise PortfolioUnavailableError(
                "No puede cerrarse un portafolio "
                "con posiciones abiertas"
            )

        closing_date = date.today()

        closed = await self._repository.close(
            portfolio,
            closing_date=closing_date,
        )

        await self._repository.commit()

        return PortfolioCloseResponse(
            id=closed.id,
            estado=PortfolioStatus.CLOSED,
            fecha_cierre=closing_date,
        )

    async def create_position(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        request: PositionCreateRequest,
    ) -> PositionResponse:
        await self._get_active_portfolio(
            portfolio_id=portfolio_id,
            user_id=user_id,
        )

        market_repository = (
            self._get_market_repository()
        )

        asset = await market_repository.get_asset(
            request.activo_id
        )

        if asset is None:
            raise PortfolioAssetNotFoundError(
                "El activo solicitado no existe"
            )

        if asset.estado != "ACTIVO":
            raise PortfolioAssetUnavailableError(
                "El activo solicitado no está activo"
            )

        existing_position = (
            await self._repository
            .get_position_by_asset(
                portfolio_id=portfolio_id,
                asset_id=request.activo_id,
            )
        )

        if existing_position is not None:
            raise PositionAlreadyExistsError(
                "El activo ya existe en el portafolio"
            )

        latest_price = (
            await market_repository
            .get_latest_asset_price(
                asset_id=asset.id,
            )
        )

        current_price = (
            latest_price.cierre_ajustado
            if (
                latest_price is not None
                and latest_price.cierre_ajustado
                is not None
            )
            else (
                latest_price.cierre
                if latest_price is not None
                else None
            )
        )

        try:
            position = (
                await self._repository
                .create_position(
                    portfolio_id=portfolio_id,
                    asset_id=asset.id,
                    quantity=request.cantidad,
                    average_purchase_price=(
                        request.precio_promedio_compra
                    ),
                    currency=asset.moneda,
                    current_price=current_price,
                    opening_date=(
                        request.fecha_apertura
                    ),
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise PositionAlreadyExistsError(
                "El activo ya existe en el portafolio"
            ) from error

        return PositionResponse.model_validate(
            position
        )

    async def list_positions(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> PositionListResponse:
        portfolio = (
            await self._repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise PortfolioNotFoundError(
                "El portafolio solicitado no existe"
            )

        positions, total = (
            await self._repository.list_positions(
                portfolio_id=portfolio_id,
                limit=limit,
                offset=offset,
            )
        )

        return PositionListResponse(
            items=[
                PositionResponse.model_validate(
                    position
                )
                for position in positions
            ],
            total=total,
        )

    async def update_position(
        self,
        *,
        portfolio_id: UUID,
        position_id: UUID,
        user_id: UUID,
        request: PositionUpdateRequest,
    ) -> PositionResponse:
        await self._get_active_portfolio(
            portfolio_id=portfolio_id,
            user_id=user_id,
        )

        position = (
            await self._repository
            .get_position_by_id(
                portfolio_id=portfolio_id,
                position_id=position_id,
            )
        )

        if position is None:
            raise PositionNotFoundError(
                "La posición solicitada no existe"
            )

        market_repository = (
            self._get_market_repository()
        )

        latest_price = (
            await market_repository
            .get_latest_asset_price(
                asset_id=position.activo_id,
            )
        )

        current_price = (
            latest_price.cierre_ajustado
            if (
                latest_price is not None
                and latest_price.cierre_ajustado
                is not None
            )
            else (
                latest_price.cierre
                if latest_price is not None
                else None
            )
        )

        updated = (
            await self._repository
            .update_position(
                position,
                quantity=request.cantidad,
                average_purchase_price=(
                    request.precio_promedio_compra
                ),
                opening_date=(
                    request.fecha_apertura
                ),
                opening_date_was_sent=(
                    "fecha_apertura"
                    in request.model_fields_set
                ),
                current_price=current_price,
            )
        )

        await self._repository.commit()

        return PositionResponse.model_validate(
            updated
        )

    async def delete_position(
        self,
        *,
        portfolio_id: UUID,
        position_id: UUID,
        user_id: UUID,
    ) -> None:
        await self._get_active_portfolio(
            portfolio_id=portfolio_id,
            user_id=user_id,
        )

        position = (
            await self._repository
            .get_position_by_id(
                portfolio_id=portfolio_id,
                position_id=position_id,
            )
        )

        if position is None:
            raise PositionNotFoundError(
                "La posición solicitada no existe"
            )

        await self._repository.delete_position(
            position
        )

        await self._repository.commit()