import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.portfolio.infrastructure.models import (
    PortfolioModel,
    PortfolioValuationModel,
    PositionModel,
)


class PortfolioRepository:
    """Acceso a datos de portafolios."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_id_for_user(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioModel | None:
        statement = (
            select(PortfolioModel)
            .where(
                PortfolioModel.id == portfolio_id,
                PortfolioModel.usuario_id == user_id,
            )
            .options(
                selectinload(
                    PortfolioModel.posiciones
                ),
                selectinload(
                    PortfolioModel.valoraciones
                ),
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_by_name_for_user(
        self,
        *,
        user_id: UUID,
        name: str,
    ) -> PortfolioModel | None:
        statement = select(
            PortfolioModel
        ).where(
            PortfolioModel.usuario_id == user_id,
            func.lower(PortfolioModel.nombre)
            == name.strip().lower(),
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        *,
        user_id: UUID,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[PortfolioModel], int]:
        filters = [
            PortfolioModel.usuario_id == user_id
        ]

        if status is not None:
            filters.append(
                PortfolioModel.estado == status
            )

        statement = (
            select(PortfolioModel)
            .where(*filters)
            .order_by(
                PortfolioModel.fecha_creacion.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(PortfolioModel.id)
            )
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def create(
        self,
        *,
        user_id: UUID,
        name: str,
        description: str | None,
        base_currency: str,
        initial_capital: Decimal,
        portfolio_type: str,
        start_date: date | None,
    ) -> PortfolioModel:
        portfolio = PortfolioModel(
            usuario_id=user_id,
            nombre=name,
            descripcion=description,
            moneda_base=base_currency,
            capital_inicial=initial_capital,
            saldo_efectivo=initial_capital,
            tipo=portfolio_type,
        )

        if start_date is not None:
            portfolio.fecha_inicio = start_date

        self._session.add(portfolio)
        await self._session.flush()
        await self._session.refresh(portfolio)

        return portfolio

    async def update(
        self,
        portfolio: PortfolioModel,
        *,
        name: str | None,
        description: str | None,
        description_was_sent: bool,
    ) -> PortfolioModel:
        if name is not None:
            portfolio.nombre = name

        if description_was_sent:
            portfolio.descripcion = description

        await self._session.flush()
        await self._session.refresh(portfolio)

        return portfolio

    async def close(
        self,
        portfolio: PortfolioModel,
        *,
        closing_date: date,
    ) -> PortfolioModel:
        portfolio.estado = "CERRADO"
        portfolio.fecha_cierre = closing_date

        await self._session.flush()
        await self._session.refresh(portfolio)

        return portfolio

    async def get_position_by_id(
        self,
        *,
        portfolio_id: UUID,
        position_id: UUID,
    ) -> PositionModel | None:
        statement = select(
            PositionModel
        ).where(
            PositionModel.id == position_id,
            PositionModel.portafolio_id
            == portfolio_id,
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_position_by_asset(
        self,
        *,
        portfolio_id: UUID,
        asset_id: UUID,
    ) -> PositionModel | None:
        statement = select(
            PositionModel
        ).where(
            PositionModel.portafolio_id
            == portfolio_id,
            PositionModel.activo_id == asset_id,
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_positions(
        self,
        *,
        portfolio_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[PositionModel], int]:
        filters = [
            PositionModel.portafolio_id
            == portfolio_id
        ]

        statement = (
            select(PositionModel)
            .where(*filters)
            .order_by(
                PositionModel.fecha_apertura.desc(),
                PositionModel.id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(func.count(PositionModel.id))
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def create_position(
        self,
        *,
        portfolio_id: UUID,
        asset_id: UUID,
        quantity: Decimal,
        average_purchase_price: Decimal,
        currency: str,
        current_price: Decimal | None,
        opening_date: datetime | None,
    ) -> PositionModel:
        position = PositionModel(
            portafolio_id=portfolio_id,
            activo_id=asset_id,
            cantidad=quantity,
            precio_promedio_compra=(
                average_purchase_price
            ),
            moneda=currency,
            precio_actual=current_price,
        )

        if opening_date is not None:
            position.fecha_apertura = opening_date

        self._session.add(position)
        await self._session.flush()
        await self._session.refresh(position)

        return position

    async def update_position(
        self,
        position: PositionModel,
        *,
        quantity: Decimal | None,
        average_purchase_price: Decimal | None,
        opening_date: datetime | None,
        opening_date_was_sent: bool,
        current_price: Decimal | None,
    ) -> PositionModel:
        if quantity is not None:
            position.cantidad = quantity

        if average_purchase_price is not None:
            position.precio_promedio_compra = (
                average_purchase_price
            )

        if opening_date_was_sent:
            if opening_date is None:
                raise ValueError(
                    "La fecha de apertura "
                    "no puede ser nula"
                )

            position.fecha_apertura = opening_date

        position.precio_actual = current_price

        await self._session.flush()
        await self._session.refresh(position)

        return position

    async def delete_position(
        self,
        position: PositionModel,
    ) -> None:
        await self._session.delete(position)
        await self._session.flush()

    async def get_portfolio_summary(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> dict[str, object] | None:
        statement = text(
            """
            SELECT
                portafolio_id,
                usuario_id,
                portafolio_nombre,
                descripcion,
                moneda_base,
                capital_inicial,
                saldo_efectivo,
                tipo,
                estado,
                fecha_inicio,
                fecha_cierre,
                fecha_creacion,
                fecha_actualizacion,
                posiciones_abiertas,
                posiciones_totales,
                capital_invertido,
                valor_posiciones,
                valor_total_estimado,
                ganancia_perdida_posiciones
            FROM portfolio.v_resumen_portafolios
            WHERE portafolio_id = :portfolio_id
              AND usuario_id = :user_id
            """
        )

        result = await self._session.execute(
            statement,
            {
                "portfolio_id": portfolio_id,
                "user_id": user_id,
            },
        )

        row = result.mappings().one_or_none()

        if row is None:
            return None

        return dict(row)

    async def get_latest_valuation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> dict[str, object] | None:
        statement = text(
            """
            SELECT
                vp.portafolio_id,
                vp.fecha_hora,
                vp.saldo_efectivo,
                vp.valor_posiciones,
                vp.valor_total,
                vp.capital_invertido,
                vp.ganancia_perdida,
                vp.rendimiento_porcentaje,
                vp.moneda,
                vp.fecha_registro
            FROM portfolio.valoraciones_portafolio AS vp
            INNER JOIN portfolio.portafolios AS pf
                ON pf.id = vp.portafolio_id
            WHERE vp.portafolio_id = :portfolio_id
              AND pf.usuario_id = :user_id
            ORDER BY
                vp.fecha_hora DESC,
                vp.id DESC
            LIMIT 1
            """
        )

        result = await self._session.execute(
            statement,
            {
                "portfolio_id": portfolio_id,
                "user_id": user_id,
            },
        )

        row = result.mappings().one_or_none()

        if row is None:
            return None

        return dict(row)

    async def get_asset_allocation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> list[dict[str, object]]:
        statement = text(
            """
            WITH posiciones_valoradas AS (
                SELECT
                    p.activo_id,
                    a.simbolo,
                    a.nombre,
                    a.sector,
                    a.industria,
                    p.cantidad,
                    COALESCE(
                        p.valor_actual,
                        p.costo_total,
                        0
                    ) AS valor_referencia
                FROM portfolio.posiciones AS p
                INNER JOIN portfolio.portafolios AS pf
                    ON pf.id = p.portafolio_id
                INNER JOIN market.activos AS a
                    ON a.id = p.activo_id
                WHERE p.portafolio_id = :portfolio_id
                  AND pf.usuario_id = :user_id
                  AND p.estado = 'ABIERTA'
                  AND p.cantidad > 0
            )
            SELECT
                activo_id,
                simbolo,
                nombre,
                sector,
                industria,
                cantidad,
                valor_referencia,
                CASE
                    WHEN SUM(valor_referencia) OVER () = 0
                    THEN 0
                    ELSE (
                        valor_referencia
                        / SUM(valor_referencia) OVER ()
                    ) * 100
                END AS porcentaje
            FROM posiciones_valoradas
            ORDER BY
                valor_referencia DESC,
                simbolo ASC
            """
        )

        result = await self._session.execute(
            statement,
            {
                "portfolio_id": portfolio_id,
                "user_id": user_id,
            },
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]

    async def get_sector_allocation(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> list[dict[str, object]]:
        statement = text(
            """
            WITH posiciones_valoradas AS (
                SELECT
                    COALESCE(
                        NULLIF(BTRIM(a.sector), ''),
                        'SIN_SECTOR'
                    ) AS sector,
                    COALESCE(
                        p.valor_actual,
                        p.costo_total,
                        0
                    ) AS valor_referencia
                FROM portfolio.posiciones AS p
                INNER JOIN portfolio.portafolios AS pf
                    ON pf.id = p.portafolio_id
                INNER JOIN market.activos AS a
                    ON a.id = p.activo_id
                WHERE p.portafolio_id = :portfolio_id
                  AND pf.usuario_id = :user_id
                  AND p.estado = 'ABIERTA'
                  AND p.cantidad > 0
            ),
            sectores AS (
                SELECT
                    sector,
                    COUNT(*) AS posiciones,
                    SUM(valor_referencia)
                        AS valor_referencia
                FROM posiciones_valoradas
                GROUP BY sector
            )
            SELECT
                sector,
                posiciones,
                valor_referencia,
                CASE
                    WHEN SUM(valor_referencia) OVER () = 0
                    THEN 0
                    ELSE (
                        valor_referencia
                        / SUM(valor_referencia) OVER ()
                    ) * 100
                END AS porcentaje
            FROM sectores
            ORDER BY
                valor_referencia DESC,
                sector ASC
            """
        )

        result = await self._session.execute(
            statement,
            {
                "portfolio_id": portfolio_id,
                "user_id": user_id,
            },
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]

    async def register_valuation(
        self,
        *,
        portfolio_id: UUID,
        valuation_date: datetime | None,
        details: dict[str, object] | None,
    ) -> int:
        statement = text(
            """
            SELECT portfolio.fn_registrar_valoracion(
                :portfolio_id,
                COALESCE(
                    :valuation_date,
                    CURRENT_TIMESTAMP
                ),
                CAST(:details AS JSONB)
            ) AS valuation_id
            """
        )

        serialized_details = (
            json.dumps(
                details,
                ensure_ascii=False,
            )
            if details is not None
            else None
        )

        result = await self._session.execute(
            statement,
            {
                "portfolio_id": portfolio_id,
                "valuation_date": valuation_date,
                "details": serialized_details,
            },
        )

        return int(result.scalar_one())

    async def get_valuation_by_id(
        self,
        *,
        valuation_id: int,
        portfolio_id: UUID,
        user_id: UUID,
    ) -> PortfolioValuationModel | None:
        statement = (
            select(PortfolioValuationModel)
            .join(
                PortfolioModel,
                PortfolioModel.id
                == PortfolioValuationModel.portafolio_id,
            )
            .where(
                PortfolioValuationModel.id
                == valuation_id,
                PortfolioValuationModel.portafolio_id
                == portfolio_id,
                PortfolioModel.usuario_id == user_id,
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_valuations(
        self,
        *,
        portfolio_id: UUID,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> tuple[
        list[PortfolioValuationModel],
        int,
    ]:
        filters = [
            PortfolioValuationModel.portafolio_id
            == portfolio_id,
            PortfolioModel.usuario_id == user_id,
        ]

        statement = (
            select(PortfolioValuationModel)
            .join(
                PortfolioModel,
                PortfolioModel.id
                == PortfolioValuationModel.portafolio_id,
            )
            .where(*filters)
            .order_by(
                PortfolioValuationModel.fecha_hora.desc(),
                PortfolioValuationModel.id.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(
                    PortfolioValuationModel.id
                )
            )
            .join(
                PortfolioModel,
                PortfolioModel.id
                == PortfolioValuationModel.portafolio_id,
            )
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

