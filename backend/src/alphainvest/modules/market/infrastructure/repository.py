from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.market.domain.enums import MoversPeriod
from alphainvest.modules.market.domain.indicator_values import (
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
        period: MoversPeriod = MoversPeriod.DAY,
        lookback_days: int = 30,
    ) -> list[dict[str, object]]:
        """Último cierre de cada activo ACTIVO y su cierre de referencia.

        Por activo se usa la fuente con el dato más reciente; en empate,
        la fuente preferida. Se usa el cierre ajustado cuando existe.

        La referencia es el último cierre en o antes de la fecha ancla:
        el día anterior (DIA), 7 días antes (SEMANA), un mes antes (MES)
        o el 31 de diciembre del año anterior (ANIO). Si el activo no
        tiene cierres en los 14 días previos al ancla, se omite.
        """

        statement = text(
            """
            WITH latest AS (
                SELECT DISTINCT ON (p.activo_id, p.fuente_id)
                    p.activo_id,
                    p.fuente_id,
                    p.fecha AS last_date,
                    COALESCE(p.cierre_ajustado, p.cierre) AS last_close
                FROM market.precios_historicos p
                JOIN market.activos a
                  ON a.id = p.activo_id
                 AND a.estado = 'ACTIVO'
                WHERE p.fecha >= CURRENT_DATE - CAST(:lookback_days AS INTEGER)
                ORDER BY p.activo_id, p.fuente_id, p.fecha DESC
            ),
            chosen AS (
                SELECT DISTINCT ON (l.activo_id)
                    l.activo_id,
                    l.fuente_id,
                    l.last_date,
                    l.last_close
                FROM latest l
                JOIN market.fuentes_financieras f ON f.id = l.fuente_id
                ORDER BY
                    l.activo_id,
                    l.last_date DESC,
                    (f.nombre = :preferred_source_name) DESC
            ),
            anchored AS (
                SELECT
                    c.*,
                    CASE CAST(:period AS TEXT)
                        WHEN 'SEMANA' THEN c.last_date - 7
                        WHEN 'MES' THEN CAST(
                            c.last_date - INTERVAL '1 month' AS DATE
                        )
                        WHEN 'ANIO' THEN MAKE_DATE(
                            CAST(EXTRACT(YEAR FROM c.last_date) AS INTEGER) - 1,
                            12,
                            31
                        )
                        ELSE c.last_date - 1
                    END AS anchor_date
                FROM chosen c
            )
            SELECT
                a.id AS asset_id,
                a.simbolo AS symbol,
                a.nombre AS name,
                a.moneda AS currency,
                f.nombre AS source_name,
                an.last_date,
                an.last_close,
                ref.fecha AS previous_date,
                ref.precio AS previous_close
            FROM anchored an
            JOIN market.activos a ON a.id = an.activo_id
            JOIN market.fuentes_financieras f ON f.id = an.fuente_id
            JOIN LATERAL (
                SELECT
                    p.fecha,
                    COALESCE(p.cierre_ajustado, p.cierre) AS precio
                FROM market.precios_historicos p
                WHERE p.activo_id = an.activo_id
                  AND p.fuente_id = an.fuente_id
                  AND p.fecha <= an.anchor_date
                  AND p.fecha >= an.anchor_date - 14
                ORDER BY p.fecha DESC
                LIMIT 1
            ) ref ON TRUE
            WHERE ref.precio > 0
            ORDER BY a.id
            """
        )

        result = await self._session.execute(
            statement,
            {
                "lookback_days": lookback_days,
                "preferred_source_name": preferred_source_name,
                "period": period.value,
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

    async def list_daily_closes(
        self,
        *,
        asset_id: UUID,
        start_date: date | None,
        preferred_source_name: str,
    ) -> list[tuple[date, Decimal]]:
        """Un cierre por fecha: la fuente preferida primero.

        Se usa el cierre (no el ajustado por dividendos), como en las
        gráficas de precio de los portales financieros.
        """

        date_filter = (
            "AND p.fecha >= :start_date"
            if start_date is not None
            else ""
        )

        statement = text(
            f"""
            SELECT DISTINCT ON (p.fecha)
                p.fecha,
                p.cierre
            FROM market.precios_historicos p
            JOIN market.fuentes_financieras f
              ON f.id = p.fuente_id
            WHERE p.activo_id = :asset_id
              {date_filter}
            ORDER BY
                p.fecha,
                (f.nombre = :preferred_source_name) DESC,
                p.fecha_registro DESC
            """
        )

        parameters: dict[str, object] = {
            "asset_id": asset_id,
            "preferred_source_name": preferred_source_name,
        }

        if start_date is not None:
            parameters["start_date"] = start_date

        result = await self._session.execute(
            statement,
            parameters,
        )

        return [
            (row[0], Decimal(row[1]))
            for row in result.all()
        ]

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

    async def get_last_price_date(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
    ) -> date | None:
        """Última fecha con precio guardado para el activo y la fuente."""

        statement = select(
            func.max(HistoricalPriceModel.fecha)
        ).where(
            HistoricalPriceModel.activo_id == asset_id,
            HistoricalPriceModel.fuente_id == source_id,
        )

        result = await self._session.execute(statement)
        value = result.scalar_one_or_none()

        return value if isinstance(value, date) else None

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
                    # Solo reescribe filas que cambiaron: re-sincronizar un
                    # histórico igual no genera escrituras (ahorra E/S).
                    where=or_(
                        HistoricalPriceModel.apertura.is_distinct_from(
                            statement.excluded.apertura
                        ),
                        HistoricalPriceModel.maximo.is_distinct_from(
                            statement.excluded.maximo
                        ),
                        HistoricalPriceModel.minimo.is_distinct_from(
                            statement.excluded.minimo
                        ),
                        HistoricalPriceModel.cierre.is_distinct_from(
                            statement.excluded.cierre
                        ),
                        HistoricalPriceModel.cierre_ajustado.is_distinct_from(
                            statement.excluded.cierre_ajustado
                        ),
                        HistoricalPriceModel.volumen.is_distinct_from(
                            statement.excluded.volumen
                        ),
                    ),
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

    async def get_indicator_price_source(
        self,
        *,
        asset_id: UUID,
        preferred_source_name: str,
    ) -> tuple[UUID, str] | None:
        """Fuente con el precio más reciente del activo.

        En empate se usa la fuente preferida, igual que en las gráficas.
        """

        statement = text(
            """
            SELECT p.fuente_id, f.nombre
            FROM market.precios_historicos p
            JOIN market.fuentes_financieras f ON f.id = p.fuente_id
            WHERE p.activo_id = :asset_id
            GROUP BY p.fuente_id, f.nombre
            ORDER BY
                MAX(p.fecha) DESC,
                (f.nombre = :preferred_source_name) DESC
            LIMIT 1
            """
        )

        result = await self._session.execute(
            statement,
            {
                "asset_id": asset_id,
                "preferred_source_name": preferred_source_name,
            },
        )
        row = result.first()

        if row is None:
            return None

        return row.fuente_id, str(row.nombre)

    async def list_closing_prices_for_indicators(
        self,
        *,
        asset_id: UUID,
        source_id: UUID,
        since: date | None = None,
        until: date | None = None,
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

        if since is not None:
            statement = statement.where(
                HistoricalPriceModel.fecha >= since
            )

        if until is not None:
            statement = statement.where(
                HistoricalPriceModel.fecha <= until
            )

        result = await self._session.execute(statement)

        return [
            ClosingPricePoint(
                date=row.fecha,
                close=row.close,
            )
            for row in result.all()
        ]

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