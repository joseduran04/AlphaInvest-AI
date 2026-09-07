from datetime import date
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class ReportingRepository:
    """Acceso read-only a la capa reporting de PostgreSQL."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

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
    ) -> tuple[list[dict[str, object]], int]:
        conditions: list[str] = []
        parameters: dict[str, object] = {
            "limit": limit,
            "offset": offset,
        }

        if symbol is not None:
            conditions.append(
                "UPPER(simbolo) = UPPER(:symbol)"
            )
            parameters["symbol"] = symbol.strip()

        if market_code is not None:
            conditions.append(
                "UPPER(mercado_codigo) = UPPER(:market_code)"
            )
            parameters["market_code"] = market_code.strip()

        if asset_type_code is not None:
            conditions.append(
                "UPPER(tipo_activo_codigo) = "
                "UPPER(:asset_type_code)"
            )
            parameters["asset_type_code"] = (
                asset_type_code.strip()
            )

        if sector is not None:
            conditions.append(
                "UPPER(sector) = UPPER(:sector)"
            )
            parameters["sector"] = sector.strip()

        if status is not None:
            conditions.append(
                "UPPER(activo_estado) = UPPER(:status)"
            )
            parameters["status"] = status.strip()

        where_clause = ""

        if conditions:
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_activos_precios
            {where_clause}
            ORDER BY
                mercado_codigo ASC NULLS LAST,
                simbolo ASC NULLS LAST
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_activos_precios
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        items = [
            dict(row)
            for row in result.mappings().all()
        ]

        return (
            items,
            int(count_result.scalar_one()),
        )

    async def list_portfolios_for_user(
        self,
        *,
        user_id: UUID,
        status: str | None,
        portfolio_type: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        conditions = [
            "usuario_id = :user_id",
        ]

        parameters: dict[str, object] = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
        }

        if status is not None:
            conditions.append(
                "UPPER(estado) = UPPER(:status)"
            )
            parameters["status"] = status.strip()

        if portfolio_type is not None:
            conditions.append(
                "UPPER(tipo) = UPPER(:portfolio_type)"
            )
            parameters["portfolio_type"] = (
                portfolio_type.strip()
            )

        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_portafolios
            {where_clause}
            ORDER BY
                fecha_creacion DESC NULLS LAST,
                portafolio_id DESC
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_portafolios
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        items = [
            dict(row)
            for row in result.mappings().all()
        ]

        return (
            items,
            int(count_result.scalar_one()),
        )

    async def list_simulations_for_user(
        self,
        *,
        user_id: UUID,
        status: str | None,
        simulation_type: str | None,
        date_from: date | None,
        date_to: date | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        conditions = [
            "usuario_id = :user_id",
        ]

        parameters: dict[str, object] = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
        }

        if status is not None:
            conditions.append(
                "UPPER(estado) = UPPER(:status)"
            )
            parameters["status"] = status.strip()

        if simulation_type is not None:
            conditions.append(
                "UPPER(tipo_simulacion) = "
                "UPPER(:simulation_type)"
            )
            parameters["simulation_type"] = (
                simulation_type.strip()
            )

        if date_from is not None:
            conditions.append(
                "fecha_solicitud::date >= :date_from"
            )
            parameters["date_from"] = date_from

        if date_to is not None:
            conditions.append(
                "fecha_solicitud::date <= :date_to"
            )
            parameters["date_to"] = date_to

        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_simulaciones
            {where_clause}
            ORDER BY
                fecha_solicitud DESC NULLS LAST,
                ejecucion_id DESC
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_simulaciones
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        items = [
            dict(row)
            for row in result.mappings().all()
        ]

        return (
            items,
            int(count_result.scalar_one()),
        )

    async def list_recommendations_for_user(
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
    ) -> tuple[list[dict[str, object]], int]:
        conditions = [
            "usuario_id = :user_id",
        ]

        parameters: dict[str, object] = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
        }

        if recommendation_type is not None:
            conditions.append(
                "UPPER(tipo) = "
                "UPPER(:recommendation_type)"
            )
            parameters["recommendation_type"] = (
                recommendation_type.strip()
            )

        if risk_level is not None:
            conditions.append(
                "UPPER(nivel_riesgo) = "
                "UPPER(:risk_level)"
            )
            parameters["risk_level"] = (
                risk_level.strip()
            )

        if horizon is not None:
            conditions.append(
                "UPPER(horizonte) = UPPER(:horizon)"
            )
            parameters["horizon"] = horizon.strip()

        if status is not None:
            conditions.append(
                "UPPER(estado) = UPPER(:status)"
            )
            parameters["status"] = status.strip()

        if date_from is not None:
            conditions.append(
                "fecha_generacion::date >= :date_from"
            )
            parameters["date_from"] = date_from

        if date_to is not None:
            conditions.append(
                "fecha_generacion::date <= :date_to"
            )
            parameters["date_to"] = date_to

        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_recomendaciones
            {where_clause}
            ORDER BY
                fecha_generacion DESC NULLS LAST,
                recomendacion_id DESC
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_recomendaciones
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        items = [
            dict(row)
            for row in result.mappings().all()
        ]

        return (
            items,
            int(count_result.scalar_one()),
        )

    async def list_users(
        self,
        *,
        status: str | None,
        email_verified: bool | None,
        blocked: bool | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        conditions: list[str] = []

        parameters: dict[str, object] = {
            "limit": limit,
            "offset": offset,
        }

        if status is not None:
            conditions.append(
                "UPPER(estado) = UPPER(:status)"
            )
            parameters["status"] = status.strip()

        if email_verified is not None:
            conditions.append(
                "correo_verificado = :email_verified"
            )
            parameters["email_verified"] = (
                email_verified
            )

        if blocked is not None:
            conditions.append(
                "bloqueado_actualmente = :blocked"
            )
            parameters["blocked"] = blocked

        where_clause = ""

        if conditions:
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_usuarios
            {where_clause}
            ORDER BY
                fecha_creacion DESC NULLS LAST,
                usuario_id DESC
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_usuarios
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        return (
            [
                dict(row)
                for row in result.mappings().all()
            ],
            int(count_result.scalar_one()),
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
    ) -> tuple[list[dict[str, object]], int]:
        conditions: list[str] = []

        parameters: dict[str, object] = {
            "limit": limit,
            "offset": offset,
        }

        if entity_schema is not None:
            conditions.append(
                "UPPER(esquema_entidad) = "
                "UPPER(:entity_schema)"
            )
            parameters["entity_schema"] = (
                entity_schema.strip()
            )

        if entity_name is not None:
            conditions.append(
                "UPPER(nombre_entidad) = "
                "UPPER(:entity_name)"
            )
            parameters["entity_name"] = (
                entity_name.strip()
            )

        if action is not None:
            conditions.append(
                "UPPER(accion) = UPPER(:action)"
            )
            parameters["action"] = action.strip()

        if origin is not None:
            conditions.append(
                "UPPER(origen) = UPPER(:origin)"
            )
            parameters["origin"] = origin.strip()

        if date_from is not None:
            conditions.append(
                "fecha >= :date_from"
            )
            parameters["date_from"] = date_from

        if date_to is not None:
            conditions.append(
                "fecha <= :date_to"
            )
            parameters["date_to"] = date_to

        where_clause = ""

        if conditions:
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_auditoria_diaria
            {where_clause}
            ORDER BY
                fecha DESC NULLS LAST,
                esquema_entidad ASC NULLS LAST,
                nombre_entidad ASC NULLS LAST,
                accion ASC NULLS LAST
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_auditoria_diaria
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        return (
            [
                dict(row)
                for row in result.mappings().all()
            ],
            int(count_result.scalar_one()),
        )

    async def list_operation_jobs(
        self,
        *,
        active: bool | None,
        job_type: str | None,
        last_status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, object]], int]:
        conditions: list[str] = []

        parameters: dict[str, object] = {
            "limit": limit,
            "offset": offset,
        }

        if active is not None:
            conditions.append(
                "activo = :active"
            )
            parameters["active"] = active

        if job_type is not None:
            conditions.append(
                "UPPER(tipo) = UPPER(:job_type)"
            )
            parameters["job_type"] = (
                job_type.strip()
            )

        if last_status is not None:
            conditions.append(
                "UPPER(ultima_ejecucion_estado) = "
                "UPPER(:last_status)"
            )
            parameters["last_status"] = (
                last_status.strip()
            )

        where_clause = ""

        if conditions:
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

        statement = text(
            f"""
            SELECT *
            FROM reporting.v_reporte_operacion_trabajos
            {where_clause}
            ORDER BY
                codigo ASC NULLS LAST,
                trabajo_id ASC
            LIMIT :limit
            OFFSET :offset
            """
        )

        count_statement = text(
            f"""
            SELECT COUNT(*)
            FROM reporting.v_reporte_operacion_trabajos
            {where_clause}
            """
        )

        result = await self._session.execute(
            statement,
            parameters,
        )

        count_result = await self._session.execute(
            count_statement,
            {
                key: value
                for key, value in parameters.items()
                if key not in {"limit", "offset"}
            },
        )

        return (
            [
                dict(row)
                for row in result.mappings().all()
            ],
            int(count_result.scalar_one()),
        )