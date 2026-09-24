"""Sincroniza noticias una vez al día para cuidar la cuota de Alpha Vantage.

Antes: INTERVALO cada 1800 s (≈48 llamadas/día por símbolo), lo que
agotaba la cuota gratuita de Alpha Vantage y producía ejecuciones
FALLIDA ("límite de consultas").

Ahora: CRON diario a las 23:20 (America/Mexico_City), después de la
actualización de precios (23:00). Cada símbolo sincronizado consume una
llamada por día.

Revision ID: 5b7e2d9f4a10
Revises: c2bdbbc33c57
"""

from collections.abc import Sequence

from alembic import op

revision: str = "5b7e2d9f4a10"
down_revision: str | Sequence[str] | None = "c2bdbbc33c57"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE operation.trabajos_programados
        SET tipo = 'CRON',
            expresion_cron = '20 23 * * *',
            intervalo_segundos = NULL,
            zona_horaria = 'America/Mexico_City',
            parametros = '{"frecuencia":"diaria","alcance":"activos_en_uso"}'::JSONB,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo = 'SINCRONIZAR_NOTICIAS'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE operation.trabajos_programados
        SET tipo = 'INTERVALO',
            expresion_cron = NULL,
            intervalo_segundos = 1800,
            zona_horaria = 'UTC',
            parametros = '{"ventana_minutos":30}'::JSONB,
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE codigo = 'SINCRONIZAR_NOTICIAS'
        """
    )
