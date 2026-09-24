"""Mide ganancia y rendimiento de portafolios sobre lo invertido.

Decisión (2026-09-24): el portafolio registra inversiones. La ganancia es
valor actual de las posiciones abiertas menos lo invertido en ellas, y el
rendimiento se calcula sobre lo invertido. El capital inicial y el efectivo
ya no participan en las métricas.

- portfolio.fn_registrar_valoracion: nuevas valoraciones con esa fórmula.
- Recalcula ganancia_perdida y rendimiento_porcentaje de las valoraciones
  existentes (campos derivados; los montos originales no cambian).
- reporting.v_reporte_portafolios: rendimiento sobre capital invertido.

El downgrade restaura la fórmula anterior (valor total − capital inicial).

Revision ID: 8c3f1e6a2d47
Revises: 5b7e2d9f4a10
"""

from collections.abc import Sequence

from alembic import op

revision: str = "8c3f1e6a2d47"
down_revision: str | Sequence[str] | None = "5b7e2d9f4a10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_VALUATION_FUNCTION = """
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

            -- Ganancia y rendimiento se miden sobre lo invertido en
            -- posiciones abiertas; el capital inicial no participa.
            v_ganancia :=
                ROUND
                (
                    v_valor_posiciones
                    - v_capital_invertido,
                    8
                );

            IF v_capital_invertido > 0 THEN
                v_rendimiento :=
                    ROUND
                    (
                        (
                            v_ganancia
                            / v_capital_invertido
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

PREVIOUS_VALUATION_FUNCTION = """
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

NEW_REPORT_VIEW = """
        CREATE OR REPLACE VIEW reporting.v_reporte_portafolios AS
        SELECT
            p.portafolio_id,
            p.usuario_id,
            p.nombres,
            p.apellidos,
            p.correo,
            p.portafolio_nombre,
            p.descripcion,
            p.moneda_base,
            p.capital_inicial,
            p.saldo_efectivo,
            p.tipo,
            p.estado,
            p.fecha_inicio,
            p.fecha_cierre,
            p.fecha_creacion,
            p.fecha_actualizacion,
            p.posiciones_abiertas,
            p.posiciones_totales,
            p.capital_invertido,
            p.valor_posiciones,
            p.valor_total_estimado,
            p.ganancia_perdida_posiciones,
            CASE
                WHEN p.capital_invertido = 0 THEN NULL
                ELSE ROUND(
                    (p.ganancia_perdida_posiciones / p.capital_invertido) * 100,
                    8
                )
            END AS rendimiento_estimado_porcentaje,
            uv.fecha_hora AS ultima_valoracion_fecha,
            uv.valor_total AS ultimo_valor_total,
            uv.ganancia_perdida AS ultima_ganancia_perdida,
            uv.rendimiento_porcentaje AS ultimo_rendimiento_porcentaje
        FROM portfolio.v_resumen_portafolios p
        LEFT JOIN portfolio.mv_ultima_valoracion_portafolio uv
            ON uv.portafolio_id = p.portafolio_id
        """

PREVIOUS_REPORT_VIEW = """
        CREATE OR REPLACE VIEW reporting.v_reporte_portafolios AS
        SELECT
            p.portafolio_id,
            p.usuario_id,
            p.nombres,
            p.apellidos,
            p.correo,
            p.portafolio_nombre,
            p.descripcion,
            p.moneda_base,
            p.capital_inicial,
            p.saldo_efectivo,
            p.tipo,
            p.estado,
            p.fecha_inicio,
            p.fecha_cierre,
            p.fecha_creacion,
            p.fecha_actualizacion,
            p.posiciones_abiertas,
            p.posiciones_totales,
            p.capital_invertido,
            p.valor_posiciones,
            p.valor_total_estimado,
            p.ganancia_perdida_posiciones,
            CASE
                WHEN p.capital_inicial = 0 THEN NULL
                ELSE ROUND(
                    ((p.valor_total_estimado - p.capital_inicial) / p.capital_inicial) * 100,
                    8
                )
            END AS rendimiento_estimado_porcentaje,
            uv.fecha_hora AS ultima_valoracion_fecha,
            uv.valor_total AS ultimo_valor_total,
            uv.ganancia_perdida AS ultima_ganancia_perdida,
            uv.rendimiento_porcentaje AS ultimo_rendimiento_porcentaje
        FROM portfolio.v_resumen_portafolios p
        LEFT JOIN portfolio.mv_ultima_valoracion_portafolio uv
            ON uv.portafolio_id = p.portafolio_id
        """


def _refresh_latest_valuation() -> None:
    op.execute(
        "REFRESH MATERIALIZED VIEW portfolio.mv_ultima_valoracion_portafolio"
    )


def upgrade() -> None:
    op.execute(NEW_VALUATION_FUNCTION)

    op.execute(
        """
        UPDATE portfolio.valoraciones_portafolio
        SET ganancia_perdida = ROUND(valor_posiciones - capital_invertido, 8),
            rendimiento_porcentaje = CASE
                WHEN capital_invertido > 0 THEN ROUND(
                    ((valor_posiciones - capital_invertido) / capital_invertido) * 100,
                    8
                )
                ELSE NULL
            END
        """
    )

    op.execute(NEW_REPORT_VIEW)
    _refresh_latest_valuation()


def downgrade() -> None:
    op.execute(PREVIOUS_VALUATION_FUNCTION)

    op.execute(
        """
        UPDATE portfolio.valoraciones_portafolio v
        SET ganancia_perdida = ROUND(v.valor_total - p.capital_inicial, 8),
            rendimiento_porcentaje = CASE
                WHEN p.capital_inicial > 0 THEN ROUND(
                    ((v.valor_total - p.capital_inicial) / p.capital_inicial) * 100,
                    8
                )
                ELSE NULL
            END
        FROM portfolio.portafolios p
        WHERE p.id = v.portafolio_id
        """
    )

    op.execute(PREVIOUS_REPORT_VIEW)
    _refresh_latest_valuation()
