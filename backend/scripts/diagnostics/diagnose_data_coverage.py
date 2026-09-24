"""Diagnóstico de cobertura de datos (SOLO LECTURA).

Uso (desde backend/ con el entorno virtual activo):

    python scripts/diagnostics/diagnose_data_coverage.py
    python scripts/diagnostics/diagnose_data_coverage.py --symbols META AMZN AAPL
    python scripts/diagnostics/diagnose_data_coverage.py --yahoo

La conexión se abre en modo READ ONLY: PostgreSQL rechaza
cualquier INSERT/UPDATE/DELETE dentro de esta sesión.
No imprime correos, nombres ni credenciales.
"""

import argparse
import asyncio
from collections.abc import Sequence
from typing import Any

from sqlalchemy import text

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)

DEFAULT_SYMBOLS = ("AAPL", "META", "AMZN")


def _print_rows(title: str, rows: Sequence[Any]) -> None:
    print(f"\n=== {title} ===")

    if not rows:
        print("(sin filas)")
        return

    keys = list(rows[0].keys())
    print(" | ".join(keys))

    for row in rows:
        print(" | ".join(str(row[key]) for key in keys))


async def run_queries(symbols: list[str]) -> None:
    async with AsyncSessionFactory() as session:
        await session.execute(
            text("SET TRANSACTION READ ONLY")
        )

        async def query(
            sql: str,
            params: dict[str, Any] | None = None,
        ) -> Sequence[Any]:
            result = await session.execute(
                text(sql),
                params or {},
            )
            return result.mappings().all()

        _print_rows(
            "Worker / configuración relevante",
            [
                {
                    "nota": (
                        "Ver APP_WORKER_PRICE_SYNC_SYMBOLS "
                        "en backend/.env"
                    )
                }
            ],
        )

        _print_rows(
            "Fuentes financieras",
            await query(
                """
                SELECT nombre, proveedor, prioridad, activa,
                       requiere_api_key, limite_consultas_minuto,
                       ultima_consulta
                FROM market.fuentes_financieras
                ORDER BY prioridad, nombre
                """
            ),
        )

        _print_rows(
            "Cobertura de precios por activo y fuente",
            await query(
                """
                SELECT a.simbolo, a.estado, f.nombre AS fuente,
                       COUNT(p.id) AS filas,
                       MIN(p.fecha) AS desde,
                       MAX(p.fecha) AS hasta,
                       MAX(p.fecha_registro) AS ultima_carga,
                       COUNT(p.cierre_ajustado) AS con_ajustado
                FROM market.activos a
                LEFT JOIN market.precios_historicos p
                       ON p.activo_id = a.id
                LEFT JOIN market.fuentes_financieras f
                       ON f.id = p.fuente_id
                GROUP BY a.simbolo, a.estado, f.nombre
                ORDER BY a.simbolo, f.nombre
                """
            ),
        )

        _print_rows(
            "Precios desde 2026-08-25 de los símbolos pedidos",
            await query(
                """
                SELECT a.simbolo, f.nombre AS fuente, p.fecha,
                       p.apertura, p.cierre, p.cierre_ajustado,
                       p.volumen, p.moneda, p.fecha_registro
                FROM market.precios_historicos p
                JOIN market.activos a ON a.id = p.activo_id
                JOIN market.fuentes_financieras f
                  ON f.id = p.fuente_id
                WHERE a.simbolo = ANY(:symbols)
                  AND p.fecha >= DATE '2026-08-25'
                ORDER BY a.simbolo, f.nombre, p.fecha
                """,
                {"symbols": symbols},
            ),
        )

        _print_rows(
            "Últimas 25 ejecuciones de trabajos",
            await query(
                """
                SELECT t.codigo, e.estado, e.disparador,
                       e.fecha_solicitud, e.fecha_fin,
                       e.registros_procesados,
                       e.resultado ->> 'symbol' AS simbolo,
                       e.resultado ->> 'source_name' AS fuente,
                       e.resultado ->> 'last_date' AS ultima_fecha,
                       LEFT(e.mensaje_error, 160) AS error
                FROM operation.ejecuciones_trabajo e
                JOIN operation.trabajos_programados t
                  ON t.id = e.trabajo_id
                ORDER BY e.fecha_solicitud DESC
                LIMIT 25
                """
            ),
        )

        _print_rows(
            "Noticias por activo",
            await query(
                """
                SELECT a.simbolo,
                       COUNT(n.id) AS noticias,
                       MIN(n.fecha_publicacion) AS primera,
                       MAX(n.fecha_publicacion) AS ultima,
                       ROUND(AVG(n.relevancia)::numeric, 4)
                           AS relevancia_promedio,
                       COUNT(*) FILTER (
                           WHERE n.relevancia < 0.3
                       ) AS relevancia_menor_0_3
                FROM market.activos a
                LEFT JOIN market.noticias_referencia n
                       ON n.activo_id = a.id
                GROUP BY a.simbolo
                ORDER BY a.simbolo
                """
            ),
        )

        _print_rows(
            "Distribución de relevancia de noticias AAPL",
            await query(
                """
                SELECT width_bucket(n.relevancia, 0, 1, 10)
                           AS bucket_0_1,
                       COUNT(*) AS noticias
                FROM market.noticias_referencia n
                JOIN market.activos a ON a.id = n.activo_id
                WHERE a.simbolo = 'AAPL'
                GROUP BY 1
                ORDER BY 1
                """
            ),
        )

        _print_rows(
            "Portafolios (anonimizados): efectivo vs posiciones",
            await query(
                """
                SELECT LEFT(p.id::text, 8) AS portafolio,
                       p.tipo, p.estado,
                       p.capital_inicial, p.saldo_efectivo,
                       COUNT(pos.id) FILTER (
                           WHERE pos.estado = 'ABIERTA'
                       ) AS posiciones_abiertas,
                       COALESCE(SUM(pos.costo_total) FILTER (
                           WHERE pos.estado = 'ABIERTA'
                       ), 0) AS costo_posiciones
                FROM portfolio.portafolios p
                LEFT JOIN portfolio.posiciones pos
                       ON pos.portafolio_id = p.id
                GROUP BY p.id
                ORDER BY p.fecha_creacion
                """
            ),
        )

        await session.rollback()


def compare_with_yahoo(symbols: list[str]) -> None:
    import yfinance as yf

    for symbol in symbols:
        print(f"\n=== Yahoo Finance en vivo: {symbol} (últimos 20 días) ===")

        history = yf.Ticker(symbol).history(
            period="1mo",
            interval="1d",
            actions=True,
            auto_adjust=False,
        )

        print(f"zona horaria índice: {history.index.tz}")
        print(
            history.tail(20)[
                [
                    "Open",
                    "Close",
                    "Adj Close",
                    "Volume",
                    "Dividends",
                    "Stock Splits",
                ]
            ].to_string()
        )


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=list(DEFAULT_SYMBOLS),
    )
    parser.add_argument(
        "--yahoo",
        action="store_true",
        help="Consulta Yahoo Finance en vivo (no escribe en BD).",
    )
    args = parser.parse_args()
    symbols = [symbol.strip().upper() for symbol in args.symbols]

    try:
        await run_queries(symbols)
    finally:
        await dispose_engine()

    if args.yahoo:
        compare_with_yahoo(symbols)


if __name__ == "__main__":
    asyncio.run(main())
