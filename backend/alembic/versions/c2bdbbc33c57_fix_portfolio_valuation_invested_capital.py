"""Corrige capital_invertido en valoraciones históricas de portafolios.

Revision ID: c2bdbbc33c57
Revises: 130add9be5fa
"""

from collections.abc import Sequence

from alembic import op

revision: str = "c2bdbbc33c57"
down_revision: str | Sequence[str] | None = "130add9be5fa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Usa el costo de posiciones abiertas como capital invertido."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION portfolio.fn_registrar_valoracion
        (
            p_portafolio_id UUID,
            p_fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            p_detalle JSONB DEFAULT NULL
        )
        RETURNS BIGINT
        LANGUAGE plpgsql
        AS
        $$
        DECLARE
            v_portafolio        portfolio.portafolios%ROWTYPE;
            v_valor_posiciones  NUMERIC(24,8);
            v_capital_invertido NUMERIC(24,8);
            v_valor_total       NUMERIC(24,8);
            v_ganancia          NUMERIC(24,8);
            v_rendimiento       NUMERIC(16,8);
            v_valoracion_id     BIGINT;
            v_detalle           JSONB;
        BEGIN
            IF p_portafolio_id IS NULL THEN
                RAISE EXCEPTION
                    'El identificador de portafolio no puede ser nulo.'
                    USING ERRCODE = '22004';
            END IF;

            IF p_fecha_hora IS NULL THEN
                RAISE EXCEPTION
                    'La fecha de valoración no puede ser nula.'
                    USING ERRCODE = '22004';
            END IF;

            IF p_detalle IS NOT NULL
               AND jsonb_typeof(p_detalle) <> 'object' THEN
                RAISE EXCEPTION
                    'El detalle de la valoración debe ser un objeto JSON.'
                    USING ERRCODE = '22023';
            END IF;

            SELECT *
            INTO v_portafolio
            FROM portfolio.portafolios
            WHERE id = p_portafolio_id
            FOR UPDATE;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'No existe el portafolio %.',
                    p_portafolio_id
                    USING ERRCODE = 'P0002';
            END IF;

            PERFORM
                portfolio.fn_recalcular_portafolio
                (
                    p_portafolio_id
                );

            SELECT
                COALESCE
                (
                    SUM(valor_actual),
                    0
                ),
                COALESCE
                (
                    SUM(costo_total),
                    0
                )
            INTO
                v_valor_posiciones,
                v_capital_invertido
            FROM portfolio.posiciones
            WHERE portafolio_id = p_portafolio_id
              AND estado = 'ABIERTA'
              AND cantidad > 0;

            v_valor_total :=
                ROUND
                (
                    v_portafolio.saldo_efectivo
                    + v_valor_posiciones,
                    8
                );

            v_ganancia :=
                ROUND
                (
                    v_valor_total
                    - v_portafolio.capital_inicial,
                    8
                );

            IF v_portafolio.capital_inicial > 0 THEN
                v_rendimiento :=
                    ROUND
                    (
                        (
                            v_ganancia
                            / v_portafolio.capital_inicial
                        ) * 100,
                        8
                    );
            ELSE
                v_rendimiento := NULL;
            END IF;

            v_detalle :=
                COALESCE
                (
                    p_detalle,
                    '{}'::JSONB
                )
                ||
                jsonb_build_object
                (
                    'posiciones_abiertas',
                    (
                        SELECT COUNT(*)
                        FROM portfolio.posiciones
                        WHERE portafolio_id = p_portafolio_id
                          AND estado = 'ABIERTA'
                          AND cantidad > 0
                    ),
                    'origen',
                    COALESCE
                    (
                        p_detalle ->> 'origen',
                        'FUNCION_POSTGRESQL'
                    )
                );

            INSERT INTO portfolio.valoraciones_portafolio
            (
                portafolio_id,
                fecha_hora,
                saldo_efectivo,
                valor_posiciones,
                valor_total,
                capital_invertido,
                ganancia_perdida,
                rendimiento_porcentaje,
                moneda,
                detalle
            )
            VALUES
            (
                p_portafolio_id,
                p_fecha_hora,
                v_portafolio.saldo_efectivo,
                v_valor_posiciones,
                v_valor_total,
                v_capital_invertido,
                v_ganancia,
                v_rendimiento,
                v_portafolio.moneda_base,
                v_detalle
            )
            RETURNING id
            INTO v_valoracion_id;

            RETURN v_valoracion_id;
        END;
        $$;
        """
    )


def downgrade() -> None:
    """Restaura el comportamiento anterior basado en capital inicial."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION portfolio.fn_registrar_valoracion
        (
            p_portafolio_id UUID,
            p_fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            p_detalle JSONB DEFAULT NULL
        )
        RETURNS BIGINT
        LANGUAGE plpgsql
        AS
        $$
        DECLARE
            v_portafolio       portfolio.portafolios%ROWTYPE;
            v_valor_posiciones NUMERIC(24,8);
            v_valor_total      NUMERIC(24,8);
            v_ganancia         NUMERIC(24,8);
            v_rendimiento      NUMERIC(16,8);
            v_valoracion_id    BIGINT;
            v_detalle          JSONB;
        BEGIN
            IF p_portafolio_id IS NULL THEN
                RAISE EXCEPTION
                    'El identificador de portafolio no puede ser nulo.'
                    USING ERRCODE = '22004';
            END IF;

            IF p_fecha_hora IS NULL THEN
                RAISE EXCEPTION
                    'La fecha de valoración no puede ser nula.'
                    USING ERRCODE = '22004';
            END IF;

            IF p_detalle IS NOT NULL
               AND jsonb_typeof(p_detalle) <> 'object' THEN
                RAISE EXCEPTION
                    'El detalle de la valoración debe ser un objeto JSON.'
                    USING ERRCODE = '22023';
            END IF;

            SELECT *
            INTO v_portafolio
            FROM portfolio.portafolios
            WHERE id = p_portafolio_id
            FOR UPDATE;

            IF NOT FOUND THEN
                RAISE EXCEPTION
                    'No existe el portafolio %.',
                    p_portafolio_id
                    USING ERRCODE = 'P0002';
            END IF;

            PERFORM
                portfolio.fn_recalcular_portafolio
                (
                    p_portafolio_id
                );

            SELECT
                COALESCE
                (
                    SUM(valor_actual),
                    0
                )
            INTO v_valor_posiciones
            FROM portfolio.posiciones
            WHERE portafolio_id = p_portafolio_id
              AND estado = 'ABIERTA'
              AND cantidad > 0;

            v_valor_total :=
                ROUND
                (
                    v_portafolio.saldo_efectivo
                    + v_valor_posiciones,
                    8
                );

            v_ganancia :=
                ROUND
                (
                    v_valor_total
                    - v_portafolio.capital_inicial,
                    8
                );

            IF v_portafolio.capital_inicial > 0 THEN
                v_rendimiento :=
                    ROUND
                    (
                        (
                            v_ganancia
                            / v_portafolio.capital_inicial
                        ) * 100,
                        8
                    );
            ELSE
                v_rendimiento := NULL;
            END IF;

            v_detalle :=
                COALESCE
                (
                    p_detalle,
                    '{}'::JSONB
                )
                ||
                jsonb_build_object
                (
                    'posiciones_abiertas',
                    (
                        SELECT COUNT(*)
                        FROM portfolio.posiciones
                        WHERE portafolio_id = p_portafolio_id
                          AND estado = 'ABIERTA'
                          AND cantidad > 0
                    ),
                    'origen',
                    COALESCE
                    (
                        p_detalle ->> 'origen',
                        'FUNCION_POSTGRESQL'
                    )
                );

            INSERT INTO portfolio.valoraciones_portafolio
            (
                portafolio_id,
                fecha_hora,
                saldo_efectivo,
                valor_posiciones,
                valor_total,
                capital_invertido,
                ganancia_perdida,
                rendimiento_porcentaje,
                moneda,
                detalle
            )
            VALUES
            (
                p_portafolio_id,
                p_fecha_hora,
                v_portafolio.saldo_efectivo,
                v_valor_posiciones,
                v_valor_total,
                v_portafolio.capital_inicial,
                v_ganancia,
                v_rendimiento,
                v_portafolio.moneda_base,
                v_detalle
            )
            RETURNING id
            INTO v_valoracion_id;

            RETURN v_valoracion_id;
        END;
        $$;
        """
    )