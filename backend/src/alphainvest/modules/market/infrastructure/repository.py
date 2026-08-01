from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)
from alphainvest.modules.market.infrastructure.models import (
    AssetModel,
    AssetTypeModel,
    FinancialSourceModel,
    HistoricalPriceModel,
    MarketModel,
)


class MarketRepository:
    """Acceso a datos del módulo de mercado."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_markets(
        self,
        *,
        active_only: bool = True,
    ) -> list[MarketModel]:
        statement = select(MarketModel)

        if active_only:
            statement = statement.where(
                MarketModel.activo.is_(True)
            )

        statement = statement.order_by(
            MarketModel.codigo.asc()
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def list_asset_types(
        self,
        *,
        active_only: bool = True,
    ) -> list[AssetTypeModel]:
        statement = select(AssetTypeModel)

        if active_only:
            statement = statement.where(
                AssetTypeModel.activo.is_(True)
            )

        statement = statement.order_by(
            AssetTypeModel.nombre.asc()
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def list_assets(
        self,
        *,
        search: str | None,
        market_code: str | None,
        asset_type_code: str | None,
        sector: str | None,
        currency: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AssetModel], int]:
        filters = []

        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    AssetModel.simbolo.ilike(pattern),
                    AssetModel.nombre.ilike(pattern),
                )
            )

        if market_code:
            filters.append(
                MarketModel.codigo
                == market_code.strip().upper()
            )

        if asset_type_code:
            filters.append(
                AssetTypeModel.codigo
                == asset_type_code.strip().upper()
            )

        if sector:
            filters.append(
                AssetModel.sector.ilike(
                    f"%{sector.strip()}%"
                )
            )

        if currency:
            filters.append(
                AssetModel.moneda
                == currency.strip().upper()
            )

        if status:
            filters.append(
                AssetModel.estado == status
            )

        base_statement = (
            select(AssetModel)
            .join(AssetModel.mercado)
            .join(AssetModel.tipo_activo)
            .where(*filters)
        )

        count_statement = (
            select(func.count(AssetModel.id))
            .join(AssetModel.mercado)
            .join(AssetModel.tipo_activo)
            .where(*filters)
        )

        result = await self._session.execute(
            base_statement
            .options(
                selectinload(AssetModel.mercado),
                selectinload(AssetModel.tipo_activo),
            )
            .order_by(
                MarketModel.codigo.asc(),
                AssetModel.simbolo.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def get_asset(
        self,
        asset_id: UUID,
    ) -> AssetModel | None:
        statement = (
            select(AssetModel)
            .where(AssetModel.id == asset_id)
            .options(
                selectinload(AssetModel.mercado),
                selectinload(AssetModel.tipo_activo),
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_asset_by_symbol(
        self,
        symbol: str,
    ) -> AssetModel | None:
        statement = (
            select(AssetModel)
            .where(
                AssetModel.simbolo == symbol.strip().upper(),
                AssetModel.estado == "ACTIVO",
            )
            .options(
                selectinload(AssetModel.mercado),
                selectinload(AssetModel.tipo_activo),
            )
            .order_by(AssetModel.fecha_alta.asc())
            .limit(1)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_financial_sources(
        self,
        *,
        active_only: bool = True,
    ) -> list[FinancialSourceModel]:
        statement = select(FinancialSourceModel)

        if active_only:
            statement = statement.where(
                FinancialSourceModel.activa.is_(True)
            )

        statement = statement.order_by(
            FinancialSourceModel.prioridad.asc(),
            FinancialSourceModel.nombre.asc(),
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_financial_source(
        self,
        source_id: UUID,
    ) -> FinancialSourceModel | None:
        return await self._session.get(
            FinancialSourceModel,
            source_id,
        )

    async def list_asset_prices(
        self,
        *,
        asset_id: UUID,
        start_date: date | None,
        end_date: date | None,
        source_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[HistoricalPriceModel], int]:
        filters = [
            HistoricalPriceModel.activo_id == asset_id
        ]

        if start_date is not None:
            filters.append(
                HistoricalPriceModel.fecha >= start_date
            )

        if end_date is not None:
            filters.append(
                HistoricalPriceModel.fecha <= end_date
            )

        if source_id is not None:
            filters.append(
                HistoricalPriceModel.fuente_id == source_id
            )

        statement = (
            select(HistoricalPriceModel)
            .where(*filters)
            .options(
                selectinload(HistoricalPriceModel.fuente)
            )
            .order_by(
                HistoricalPriceModel.fecha.desc(),
                HistoricalPriceModel.fecha_registro.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(func.count(HistoricalPriceModel.id))
            .where(*filters)
        )

        result = await self._session.execute(statement)
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def get_latest_asset_price(
        self,
        *,
        asset_id: UUID,
        source_id: UUID | None = None,
    ) -> HistoricalPriceModel | None:
        filters = [
            HistoricalPriceModel.activo_id == asset_id
        ]

        if source_id is not None:
            filters.append(
                HistoricalPriceModel.fuente_id == source_id
            )

        statement = (
            select(HistoricalPriceModel)
            .where(*filters)
            .options(
                selectinload(HistoricalPriceModel.fuente)
            )
            .order_by(
                HistoricalPriceModel.fecha.desc(),
                HistoricalPriceModel.fecha_registro.desc(),
                HistoricalPriceModel.id.desc(),
            )
            .limit(1)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_financial_source_by_name(
        self,
        *,
        name: str,
        active_only: bool = True,
    ) -> FinancialSourceModel | None:
        statement = select(FinancialSourceModel).where(
            FinancialSourceModel.nombre == name
        )

        if active_only:
            statement = statement.where(
                FinancialSourceModel.activa.is_(True)
            )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_existing_price_dates(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
        dates: list[date],
    ) -> set[date]:
        if not dates:
            return set()

        statement = select(
            HistoricalPriceModel.fecha
        ).where(
            HistoricalPriceModel.activo_id == asset_id,
            HistoricalPriceModel.fuente_id == source_id,
            HistoricalPriceModel.fecha.in_(dates),
        )

        result = await self._session.execute(statement)

        return set(result.scalars().all())

    async def upsert_daily_prices(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
        prices: list[DailyPricePoint],
    ) -> None:
        if not prices:
            return

        values = [
            {
                "activo_id": asset_id,
                "fuente_id": source_id,
                "fecha": price.date,
                "apertura": price.open,
                "maximo": price.high,
                "minimo": price.low,
                "cierre": price.close,
                "cierre_ajustado": price.adjusted_close,
                "volumen": price.volume,
                "moneda": price.currency,
            }
            for price in prices
        ]

        statement = insert(
            HistoricalPriceModel
        ).values(values)

        statement = statement.on_conflict_do_update(
            index_elements=[
                HistoricalPriceModel.activo_id,
                HistoricalPriceModel.fuente_id,
                HistoricalPriceModel.fecha,
            ],
            set_={
                "apertura": statement.excluded.apertura,
                "maximo": statement.excluded.maximo,
                "minimo": statement.excluded.minimo,
                "cierre": statement.excluded.cierre,
                "cierre_ajustado": (
                    statement.excluded.cierre_ajustado
                ),
                "volumen": statement.excluded.volumen,
                "moneda": statement.excluded.moneda,
                "fecha_registro": func.now(),
            },
        )

        await self._session.execute(statement)

    async def mark_source_requested(
        self,
        source: FinancialSourceModel,
    ) -> datetime:
        synchronized_at = datetime.now(UTC)
        source.ultima_consulta = synchronized_at

        await self._session.flush()

        return synchronized_at

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()