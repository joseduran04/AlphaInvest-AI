"""Reconcilia saldo_efectivo de portafolios virtuales activos (AI-PORT-001).

Antes de post-v1.1.0, agregar una posición no descontaba efectivo.
Este script recalcula:

    saldo_esperado = capital_inicial - suma(costo_total de posiciones abiertas)

Por defecto es un SIMULACRO (solo lectura). Para aplicar los cambios:

    PYTHONPATH=src python scripts/portfolio/reconcile_cash_balances.py --apply

No modifica posiciones, valoraciones históricas ni portafolios cerrados.
Omite portafolios cuyo saldo esperado sería negativo o que tengan
posiciones en una moneda distinta a la base.
"""

import argparse
import asyncio
from decimal import Decimal

from sqlalchemy import text

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)

SELECT_CANDIDATES_SQL = (
    """
    SELECT p.id,
           p.moneda_base,
           p.capital_inicial,
           p.saldo_efectivo,
           COALESCE(
               SUM(pos.costo_total) FILTER (WHERE pos.estado = 'ABIERTA'),
               0
           ) AS costo_abierto,
           COUNT(pos.id) FILTER (
               WHERE pos.estado = 'ABIERTA'
                 AND pos.moneda <> p.moneda_base
           ) AS posiciones_otra_moneda
    FROM portfolio.portafolios p
    LEFT JOIN portfolio.posiciones pos
           ON pos.portafolio_id = p.id
    WHERE p.tipo = 'VIRTUAL'
      AND p.estado = 'ACTIVO'
    GROUP BY p.id
    ORDER BY p.fecha_creacion
    """
)

LOCK_PORTFOLIOS = text(
    """
    SELECT id
    FROM portfolio.portafolios
    WHERE tipo = 'VIRTUAL'
      AND estado = 'ACTIVO'
    FOR UPDATE
    """
)

UPDATE_BALANCE = text(
    """
    UPDATE portfolio.portafolios
    SET saldo_efectivo = :expected
    WHERE id = :portfolio_id
      AND saldo_efectivo = :current
    """
)


async def reconcile(*, apply: bool) -> None:
    mode = "APLICAR" if apply else "SIMULACRO (sin cambios)"
    print(f"Modo: {mode}\n")

    async with AsyncSessionFactory() as session:
        if not apply:
            await session.execute(text("SET TRANSACTION READ ONLY"))

        if apply:
            # Bloquea los portafolios antes de calcular. PostgreSQL no permite
            # FOR UPDATE junto con GROUP BY, por eso se hace en una consulta aparte.
            await session.execute(LOCK_PORTFOLIOS)

        rows = (await session.execute(text(SELECT_CANDIDATES_SQL))).mappings().all()
        changes = 0

        for row in rows:
            short_id = str(row["id"])[:8]
            current = Decimal(row["saldo_efectivo"])
            expected = Decimal(row["capital_inicial"]) - Decimal(row["costo_abierto"])

            if row["posiciones_otra_moneda"]:
                print(f"{short_id}: OMITIDO, tiene posiciones en otra moneda")
                continue

            if expected < 0:
                print(f"{short_id}: OMITIDO, saldo esperado negativo ({expected})")
                continue

            if expected == current:
                continue

            changes += 1
            print(
                f"{short_id}: saldo {current} -> {expected} "
                f"({row['moneda_base']}, costo abierto {row['costo_abierto']})"
            )

            if apply:
                await session.execute(
                    UPDATE_BALANCE,
                    {
                        "expected": expected,
                        "portfolio_id": row["id"],
                        "current": current,
                    },
                )

        if apply:
            await session.commit()
        else:
            await session.rollback()

    print(f"\nPortafolios {'corregidos' if apply else 'por corregir'}: {changes}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica la corrección. Sin esta opción solo muestra el simulacro.",
    )
    args = parser.parse_args()

    try:
        await reconcile(apply=args.apply)
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())
