from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select, text, tuple_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.market.domain.indicator_values import (
    CalculatedIndicatorPoint,
    ClosingPricePoint,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)
from alphainvest.modules.market.infrastructure.models import (
    AssetModel,
    AssetTypeModel,
    FinancialIndicatorModel,
    FinancialSourceModel,
    HistoricalPriceModel,
    MarketModel,
    NewsReferenceModel,
)


class MarketRepository:
    """Acceso a datos del módulo de mercado."""

    PRICE_WRITE_BATCH_SIZE = 500
    INDICATOR_WRITE_BATCH_SIZE = 1000
    LOOKUP_BATCH_SIZE = 1000

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

    async def list_latest_price_changes(
        self,
        *,
        preferred_source_name: str,
        lookback_days: int = 30,
    ) -> list[dict[str, object]]:
        """Últimos dos cierres de cada activo ACTIVO.

        Por activo se usa la fuente con el dato más reciente; en empate,
        la fuente preferida. Se usa el cierre ajustado cuando existe.
        """

        statement = text(
            """
            WITH ranked AS (
                SELECT
                    p.activo_id,
                    p.fuente_id,
                    p.fecha,
                    COALESCE(p.cierre_ajustado, p.cierre) AS precio,
                    ROW_NUMBER() OVER (
                        PARTITION BY p.activo_id, p.fuente_id
                        ORDER BY p.fecha DESC
                    ) AS rn
                FROM market.precios_historicos p
                JOIN market.activos a
                  ON a.id = p.activo_id
                 AND a.estado = 'ACTIVO'
                WHERE p.fecha >= CURRENT_DATE - CAST(:lookback_days AS INTEGER)
            ),
            pairs AS (
                SELECT
                    activo_id,
                    fuente_id,
                    MAX(fecha) FILTER (WHERE rn = 1) AS last_date,
                    MAX(precio) FILTER (WHERE rn = 1) AS last_close,
                    MAX(fecha) FILTER (WHERE rn = 2) AS previous_date,
                    MAX(precio) FILTER (WHERE rn = 2) AS previous_close
                FROM ranked
                WHERE rn <= 2
                GROUP BY activo_id, fuente_id
            )
            SELECT DISTINCT ON (pr.activo_id)
                a.id AS asset_id,
                a.simbolo AS symbol,
                a.nombre AS name,
                a.moneda AS currency,
                f.nombre AS source_name,
                pr.last_date,
                pr.last_close,
                pr.previous_date,
                pr.previous_close
            FROM pairs pr
            JOIN market.activos a ON a.id = pr.activo_id
            JOIN market.fuentes_financieras f ON f.id = pr.fuente_id
            WHERE pr.previous_close IS NOT NULL
              AND pr.previous_close > 0
            ORDER BY
                pr.activo_id,
                pr.last_date DESC,
                (f.nombre = :preferred_source_name) DESC
            """
        )

        result = await self._session.execute(
            statement,
            {
                "lookback_days": lookback_days,
                "preferred_source_name": preferred_source_name,
            },
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]

    async def refresh_open_position_prices(
        self,
        *,
        asset_id: UUID,
    ) -> int:
        """Actualiza el precio actual de las posiciones abiertas del activo.

        Usa el último precio guardado (cualquier fuente, ajustado si existe),
        igual que al crear una posición. El trigger de posiciones recalcula
        valor, ganancia y rendimiento.
        """

        statement = text(
            """
            UPDATE portfolio.posiciones pos
            SET precio_actual = latest.precio,
                fecha_actualizacion = CURRENT_TIMESTAMP
            FROM (
                SELECT DISTINCT ON (p.activo_id)
                    p.activo_id,
                    COALESCE(p.cierre_ajustado, p.cierre) AS precio
                FROM market.precios_historicos p
                WHERE p.activo_id = :asset_id
                ORDER BY
                    p.activo_id,
                    p.fecha DESC,
                    p.fecha_registro DESC,
                    p.id DESC
            ) latest
            WHERE pos.activo_id = latest.activo_id
              AND pos.estado = 'ABIERTA'
              AND pos.activo_id = :asset_id
              AND pos.precio_actual IS DISTINCT FROM latest.precio
            """
        )

        result = await self._session.execute(
            statement,
            {"asset_id": asset_id},
        )

        return int(getattr(result, "rowcount", 0) or 0)

    async def list_active_symbols(self) -> list[str]:
        """Símbolos de todos los activos en estado ACTIVO."""

        statement = (
            select(AssetModel.simbolo)
            .where(AssetModel.estado == "ACTIVO")
            .order_by(AssetModel.simbolo)
        )

        result = await self._session.execute(statement)

        return [
            str(symbol)
            for symbol in result.scalars().all()
        ]

    async def list_symbols_in_use(self) -> list[str]:
        """Símbolos de activos activos que el usuario está utilizando.

        Incluye posiciones abiertas de portafolios activos, activos de
        configuraciones de simulación no archivadas y listas de seguimiento.
        """

        statement = text(
            """
            SELECT DISTINCT a.simbolo
            FROM market.activos a
            WHERE a.estado = 'ACTIVO'
              AND (
                  EXISTS (
                      SELECT 1
                      FROM portfolio.posiciones pos
                      JOIN portfolio.portafolios p
                        ON p.id = pos.portafolio_id
                      WHERE pos.activo_id = a.id
                        AND pos.estado = 'ABIERTA'
                        AND p.estado = 'ACTIVO'
                  )
                  OR EXISTS (
                      SELECT 1
                      FROM simulation.configuracion_activos ca
                      JOIN simulation.configuraciones c
                        ON c.id = ca.configuracion_id
                      WHERE ca.activo_id = a.id
                        AND c.estado <> 'ARCHIVADA'
                  )
                  OR EXISTS (
                      SELECT 1
                      FROM portfolio.lista_activos la
                      WHERE la.activo_id = a.id
                  )
              )
            ORDER BY a.simbolo
            """
        )

        result = await self._session.execute(statement)

        return [
            str(symbol)
            for symbol in result.scalars().all()
        ]

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

    async def upsert_news_reference(
        self,
        *,
        asset_id: UUID,
        mongo_document_id: str,
        title: str,
        source: str,
        url: str | None,
        published_at: datetime,
        language: str | None,
        relevance: Decimal | None,
    ) -> UUID:
        insert_statement = insert(
            NewsReferenceModel
        ).values(
            activo_id=asset_id,
            mongo_document_id=(
                mongo_document_id
            ),
            titulo=title,
            fuente=source,
            url=url,
            fecha_publicacion=published_at,
            idioma=language,
            relevancia=relevance,
        )

        returning_statement = (
            insert_statement
            .on_conflict_do_update(
                index_elements=[
                    NewsReferenceModel.activo_id,
                    (
                        NewsReferenceModel
                        .mongo_document_id
                    ),
                ],
                set_={
                    "titulo": (
                        insert_statement
                        .excluded
                        .titulo
                    ),
                    "fuente": (
                        insert_statement
                        .excluded
                        .fuente
                    ),
                    "url": (
                        insert_statement
                        .excluded
                        .url
                    ),
                    "fecha_publicacion": (
                        insert_statement
                        .excluded
                        .fecha_publicacion
                    ),
                    "idioma": (
                        insert_statement
                        .excluded
                        .idioma
                    ),
                    "relevancia": (
                        insert_statement
                        .excluded
                        .relevancia
                    ),
                },
            )
            .returning(
                NewsReferenceModel.id
            )
        )

        result = await self._session.execute(
            returning_statement
        )

        reference_id = result.scalar_one()

        if not isinstance(
            reference_id,
            UUID,
        ):
            raise RuntimeError(
                "PostgreSQL devolvió un "
                "identificador de noticia inválido"
            )

        return reference_id

    async def list_news_references(
        self,
        *,
        asset_id: UUID,
        start_at: datetime | None,
        end_at: datetime | None,
        limit: int,
        offset: int,
        order_by: str = "fecha",
    ) -> tuple[
        list[NewsReferenceModel],
        int,
    ]:
        filters = [
            NewsReferenceModel.activo_id
            == asset_id
        ]

        if start_at is not None:
            filters.append(
                NewsReferenceModel
                .fecha_publicacion
                >= start_at
            )

        if end_at is not None:
            filters.append(
                NewsReferenceModel
                .fecha_publicacion
                <= end_at
            )

        statement = (
            select(NewsReferenceModel)
            .where(*filters)
            .order_by(
                *(
                    (
                        NewsReferenceModel
                        .relevancia
                        .desc()
                        .nulls_last(),
                    )
                    if order_by == "relevancia"
                    else ()
                ),
                NewsReferenceModel
                .fecha_publicacion
                .desc(),
                NewsReferenceModel
                .fecha_registro
                .desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(
                    NewsReferenceModel.id
                )
            )
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )

        count_result = (
            await self._session.execute(
                count_statement
            )
        )

        return (
            list(
                result.scalars().all()
            ),
            int(
                count_result.scalar_one()
            ),
        )

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

    async def list_asset_prices_for_simulation(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPriceModel]:
        statement = (
            select(HistoricalPriceModel)
            .where(
                HistoricalPriceModel.activo_id == asset_id,
                HistoricalPriceModel.fuente_id == source_id,
                HistoricalPriceModel.fecha >= start_date,
                HistoricalPriceModel.fecha <= end_date,
            )
            .order_by(
                HistoricalPriceModel.fecha.asc()
            )
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

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

        existing_dates: set[date] = set()

        for start in range(
            0,
            len(dates),
            self.LOOKUP_BATCH_SIZE,
        ):
            batch = dates[
                start:start + self.LOOKUP_BATCH_SIZE
            ]

            statement = select(
                HistoricalPriceModel.fecha
            ).where(
                HistoricalPriceModel.activo_id
                == asset_id,
                HistoricalPriceModel.fuente_id
                == source_id,
                HistoricalPriceModel.fecha.in_(
                    batch
                ),
            )

            result = await self._session.execute(
                statement
            )

            existing_dates.update(
                result.scalars().all()
            )

        return existing_dates

    async def upsert_daily_prices(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
        prices: list[DailyPricePoint],
    ) -> None:
        if not prices:
            return

        for start in range(
            0,
            len(prices),
            self.PRICE_WRITE_BATCH_SIZE,
        ):
            batch = prices[
                start:start
                + self.PRICE_WRITE_BATCH_SIZE
            ]

            values = [
                {
                    "activo_id": asset_id,
                    "fuente_id": source_id,
                    "fecha": price.date,
                    "apertura": price.open,
                    "maximo": price.high,
                    "minimo": price.low,
                    "cierre": price.close,
                    "cierre_ajustado": (
                        price.adjusted_close
                    ),
                    "volumen": price.volume,
                    "moneda": price.currency,
                }
                for price in batch
            ]

            statement = insert(
                HistoricalPriceModel
            ).values(values)

            statement = (
                statement.on_conflict_do_update(
                    index_elements=[
                        HistoricalPriceModel.activo_id,
                        HistoricalPriceModel.fuente_id,
                        HistoricalPriceModel.fecha,
                    ],
                    set_={
                        "apertura": (
                            statement.excluded.apertura
                        ),
                        "maximo": (
                            statement.excluded.maximo
                        ),
                        "minimo": (
                            statement.excluded.minimo
                        ),
                        "cierre": (
                            statement.excluded.cierre
                        ),
                        "cierre_ajustado": (
                            statement.excluded
                            .cierre_ajustado
                        ),
                        "volumen": (
                            statement.excluded.volumen
                        ),
                        "moneda": (
                            statement.excluded.moneda
                        ),
                        "fecha_registro": func.now(),
                    },
                )
            )

            await self._session.execute(
                statement
            )

    async def mark_source_requested(
        self,
        source: FinancialSourceModel,
    ) -> datetime:
        synchronized_at = datetime.now(UTC)
        source.ultima_consulta = synchronized_at

        await self._session.flush()

        return synchronized_at

    async def list_closing_prices_for_indicators(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
    ) -> list[ClosingPricePoint]:
        statement = (
            select(
                HistoricalPriceModel.fecha,
                func.coalesce(
                    HistoricalPriceModel.cierre_ajustado,
                    HistoricalPriceModel.cierre,
                ).label("close"),
            )
            .where(
                HistoricalPriceModel.activo_id == asset_id,
                HistoricalPriceModel.fuente_id == source_id,
            )
            .order_by(
                HistoricalPriceModel.fecha.asc()
            )
        )

        result = await self._session.execute(statement)

        return [
            ClosingPricePoint(
                date=row.fecha,
                close=row.close,
            )
            for row in result.all()
        ]

    async def upsert_financial_indicators(
        self,
        *,
        asset_id: UUID,
        indicators: list[
            CalculatedIndicatorPoint
        ],
    ) -> None:
        if not indicators:
            return

        for start in range(
            0,
            len(indicators),
            self.INDICATOR_WRITE_BATCH_SIZE,
        ):
            batch = indicators[
                start:start
                + self.INDICATOR_WRITE_BATCH_SIZE
            ]

            values = [
                {
                    "activo_id": asset_id,
                    "tipo_indicador": (
                        indicator.indicator_type
                    ),
                    "fecha": indicator.date,
                    "valor": indicator.value,
                    "periodo": indicator.period,
                    "parametros": (
                        indicator.parameters
                    ),
                    "fuente_calculo": (
                        indicator.calculation_source
                    ),
                }
                for indicator in batch
            ]

            statement = insert(
                FinancialIndicatorModel
            ).values(values)

            statement = (
                statement.on_conflict_do_update(
                    index_elements=[
                        FinancialIndicatorModel
                        .activo_id,
                        FinancialIndicatorModel
                        .tipo_indicador,
                        FinancialIndicatorModel
                        .fecha,
                        FinancialIndicatorModel
                        .periodo,
                    ],
                    set_={
                        "valor": (
                            statement.excluded.valor
                        ),
                        "parametros": (
                            statement.excluded
                            .parametros
                        ),
                        "fuente_calculo": (
                            statement.excluded
                            .fuente_calculo
                        ),
                        "fecha_calculo": func.now(),
                    },
                )
            )

            await self._session.execute(
                statement
            )

    async def get_existing_indicator_keys(
        self,
        *,
        asset_id: UUID,
        keys: list[tuple[str, date, str]],
    ) -> set[tuple[str, date, str]]:
        if not keys:
            return set()

        existing_keys: set[
            tuple[str, date, str]
        ] = set()

        for start in range(
            0,
            len(keys),
            self.LOOKUP_BATCH_SIZE,
        ):
            batch = keys[
                start:start + self.LOOKUP_BATCH_SIZE
            ]

            statement = select(
                FinancialIndicatorModel.tipo_indicador,
                FinancialIndicatorModel.fecha,
                FinancialIndicatorModel.periodo,
            ).where(
                FinancialIndicatorModel.activo_id
                == asset_id,
                tuple_(
                    FinancialIndicatorModel
                    .tipo_indicador,
                    FinancialIndicatorModel.fecha,
                    FinancialIndicatorModel.periodo,
                ).in_(batch),
            )

            result = await self._session.execute(
                statement
            )

            existing_keys.update(
                (
                    row.tipo_indicador,
                    row.fecha,
                    row.periodo,
                )
                for row in result.all()
            )

        return existing_keys

    async def list_financial_indicators(
        self,
        *,
        asset_id: UUID,
        indicator_type: str | None,
        period: str | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        offset: int,
    ) -> tuple[list[FinancialIndicatorModel], int]:
        filters = [
            FinancialIndicatorModel.activo_id == asset_id
        ]

        if indicator_type is not None:
            filters.append(
                FinancialIndicatorModel.tipo_indicador
                == indicator_type
            )

        if period is not None:
            filters.append(
                FinancialIndicatorModel.periodo
                == period.strip().upper()
            )

        if start_date is not None:
            filters.append(
                FinancialIndicatorModel.fecha
                >= start_date
            )

        if end_date is not None:
            filters.append(
                FinancialIndicatorModel.fecha
                <= end_date
            )

        statement = (
            select(FinancialIndicatorModel)
            .where(*filters)
            .order_by(
                FinancialIndicatorModel.fecha.desc(),
                FinancialIndicatorModel.tipo_indicador.asc(),
                FinancialIndicatorModel.periodo.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(
                    FinancialIndicatorModel.id
                )
            )
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

    async def list_financial_indicators_for_ai(
        self,
        *,
        asset_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[FinancialIndicatorModel]:
        statement = (
            select(FinancialIndicatorModel)
            .where(
                FinancialIndicatorModel.activo_id
                == asset_id,
                FinancialIndicatorModel.fecha
                >= start_date,
                FinancialIndicatorModel.fecha
                <= end_date,
            )
            .order_by(
                FinancialIndicatorModel.fecha.asc(),
                FinancialIndicatorModel.tipo_indicador.asc(),
                FinancialIndicatorModel.periodo.asc(),
            )
        )

        result = await self._session.execute(
            statement
        )

        return list(result.scalars().all())

    async def get_news_reference(
        self,
        news_reference_id: UUID,
    ) -> NewsReferenceModel | None:
        return await self._session.get(
            NewsReferenceModel,
            news_reference_id,
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()