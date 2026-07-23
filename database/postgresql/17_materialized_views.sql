/*
============================================================
 AlphaInvest AI
 Script: 17_materialized_views.sql

 Propósito:
 Crear vistas materializadas para consultas analíticas y operativas
 de mayor costo, junto con índices únicos que permitan ejecutar
 REFRESH MATERIALIZED VIEW CONCURRENTLY después de la carga inicial.

 Dependencias:
 - 03_auth_tables.sql
 - 06_market_tables.sql
 - 07_portfolio_tables.sql
 - 08_simulation_tables.sql
 - 10_audit_operation_tables.sql
 - 16_views.sql
============================================================
*/

BEGIN;

/*
============================================================
 1. RESUMEN DIARIO DE PRECIOS POR ACTIVO
============================================================
*/

DROP MATERIALIZED VIEW IF EXISTS market.mv_resumen_diario_activos;

CREATE MATERIALIZED VIEW market.mv_resumen_diario_activos AS
SELECT
    ph.activo_id,
    a.simbolo,
    a.nombre AS activo_nombre,
    m.codigo AS mercado_codigo,
    ta.codigo AS tipo_activo_codigo,
    ph.fecha,
    COUNT(DISTINCT ph.fuente_id)::BIGINT AS numero_fuentes,
    MIN(ph.minimo) AS minimo_reportado,
    MAX(ph.maximo) AS maximo_reportado,
    AVG(ph.apertura) AS apertura_promedio,
    AVG(ph.cierre) AS cierre_promedio,
    AVG(COALESCE(ph.cierre_ajustado, ph.cierre)) AS cierre_ajustado_promedio,
    SUM(COALESCE(ph.volumen, 0)) AS volumen_total,
    ph.moneda,
    MAX(ph.fecha_registro) AS ultima_actualizacion
FROM market.precios_historicos ph
JOIN market.activos a
    ON a.id = ph.activo_id
JOIN market.mercados m
    ON m.id = a.mercado_id
JOIN market.tipos_activo ta
    ON ta.id = a.tipo_activo_id
GROUP BY
    ph.activo_id,
    a.simbolo,
    a.nombre,
    m.codigo,
    ta.codigo,
    ph.fecha,
    ph.moneda
WITH DATA;

CREATE UNIQUE INDEX ux_mv_resumen_diario_activos
    ON market.mv_resumen_diario_activos (activo_id, fecha, moneda);

CREATE INDEX ix_mv_resumen_diario_activos_fecha
    ON market.mv_resumen_diario_activos (fecha DESC);

COMMENT ON MATERIALIZED VIEW market.mv_resumen_diario_activos IS
'Resumen diario consolidado de precios históricos por activo, fecha y moneda.';

/*
============================================================
 2. ÚLTIMA VALORACIÓN DE CADA PORTAFOLIO
============================================================
*/

DROP MATERIALIZED VIEW IF EXISTS portfolio.mv_ultima_valoracion_portafolio;

CREATE MATERIALIZED VIEW portfolio.mv_ultima_valoracion_portafolio AS
SELECT DISTINCT ON (vp.portafolio_id)
    vp.portafolio_id,
    p.usuario_id,
    p.nombre AS portafolio_nombre,
    p.tipo AS portafolio_tipo,
    p.estado AS portafolio_estado,
    vp.fecha_hora,
    vp.saldo_efectivo,
    vp.valor_posiciones,
    vp.valor_total,
    vp.capital_invertido,
    vp.ganancia_perdida,
    vp.rendimiento_porcentaje,
    vp.moneda,
    vp.fecha_registro
FROM portfolio.valoraciones_portafolio vp
JOIN portfolio.portafolios p
    ON p.id = vp.portafolio_id
ORDER BY
    vp.portafolio_id,
    vp.fecha_hora DESC,
    vp.id DESC
WITH DATA;

CREATE UNIQUE INDEX ux_mv_ultima_valoracion_portafolio
    ON portfolio.mv_ultima_valoracion_portafolio (portafolio_id);

CREATE INDEX ix_mv_ultima_valoracion_usuario
    ON portfolio.mv_ultima_valoracion_portafolio (usuario_id, fecha_hora DESC);

COMMENT ON MATERIALIZED VIEW portfolio.mv_ultima_valoracion_portafolio IS
'Última valoración registrada para cada portafolio virtual o simulado.';

/*
============================================================
 3. ESTADÍSTICAS DE RESULTADOS DE SIMULACIÓN
============================================================
*/

DROP MATERIALIZED VIEW IF EXISTS simulation.mv_estadisticas_simulacion;

CREATE MATERIALIZED VIEW simulation.mv_estadisticas_simulacion AS
SELECT
    c.usuario_id,
    c.tipo_simulacion,
    r.moneda,
    COUNT(*)::BIGINT AS ejecuciones_con_resultado,
    AVG(r.capital_inicial) AS capital_inicial_promedio,
    AVG(r.capital_final) AS capital_final_promedio,
    AVG(r.ganancia_perdida) AS ganancia_perdida_promedio,
    AVG(r.rendimiento_total_porcentaje) AS rendimiento_total_promedio,
    AVG(r.rendimiento_anualizado_porcentaje) AS rendimiento_anualizado_promedio,
    AVG(r.volatilidad_anualizada) AS volatilidad_promedio,
    AVG(r.indice_sharpe) AS indice_sharpe_promedio,
    AVG(r.maximo_drawdown_porcentaje) AS drawdown_promedio,
    AVG(r.probabilidad_ganancia) AS probabilidad_ganancia_promedio,
    MIN(r.fecha_registro) AS primer_resultado,
    MAX(r.fecha_registro) AS ultimo_resultado
FROM simulation.resultados r
JOIN simulation.ejecuciones e
    ON e.id = r.ejecucion_id
JOIN simulation.configuraciones c
    ON c.id = e.configuracion_id
GROUP BY
    c.usuario_id,
    c.tipo_simulacion,
    r.moneda
WITH DATA;

CREATE UNIQUE INDEX ux_mv_estadisticas_simulacion
    ON simulation.mv_estadisticas_simulacion
    (usuario_id, tipo_simulacion, moneda);

CREATE INDEX ix_mv_estadisticas_simulacion_tipo
    ON simulation.mv_estadisticas_simulacion
    (tipo_simulacion, ultimo_resultado DESC);

COMMENT ON MATERIALIZED VIEW simulation.mv_estadisticas_simulacion IS
'Estadísticas agregadas de resultados de simulación por usuario, tipo y moneda.';

/*
============================================================
 4. MÉTRICAS OPERATIVAS DE TRABAJOS PROGRAMADOS
============================================================
*/

DROP MATERIALIZED VIEW IF EXISTS operation.mv_metricas_trabajos;

CREATE MATERIALIZED VIEW operation.mv_metricas_trabajos AS
SELECT
    tp.id AS trabajo_id,
    tp.codigo,
    tp.nombre,
    tp.tipo,
    tp.activo,
    COUNT(et.id)::BIGINT AS total_ejecuciones,
    COUNT(et.id) FILTER (WHERE et.estado = 'COMPLETADA')::BIGINT AS ejecuciones_completadas,
    COUNT(et.id) FILTER (WHERE et.estado = 'FALLIDA')::BIGINT AS ejecuciones_fallidas,
    COUNT(et.id) FILTER (WHERE et.estado = 'CANCELADA')::BIGINT AS ejecuciones_canceladas,
    COUNT(et.id) FILTER (WHERE et.estado = 'EJECUTANDO')::BIGINT AS ejecuciones_en_curso,
    COALESCE(SUM(et.registros_procesados), 0)::BIGINT AS registros_procesados,
    COALESCE(SUM(et.registros_exitosos), 0)::BIGINT AS registros_exitosos,
    COALESCE(SUM(et.registros_fallidos), 0)::BIGINT AS registros_fallidos,
    AVG(EXTRACT(EPOCH FROM (et.fecha_fin - et.fecha_inicio)))
        FILTER (WHERE et.fecha_inicio IS NOT NULL AND et.fecha_fin IS NOT NULL)
        AS duracion_promedio_segundos,
    MAX(et.fecha_solicitud) AS ultima_solicitud,
    MAX(et.fecha_fin) AS ultima_finalizacion,
    tp.siguiente_ejecucion
FROM operation.trabajos_programados tp
LEFT JOIN operation.ejecuciones_trabajo et
    ON et.trabajo_id = tp.id
GROUP BY
    tp.id,
    tp.codigo,
    tp.nombre,
    tp.tipo,
    tp.activo,
    tp.siguiente_ejecucion
WITH DATA;

CREATE UNIQUE INDEX ux_mv_metricas_trabajos
    ON operation.mv_metricas_trabajos (trabajo_id);

CREATE INDEX ix_mv_metricas_trabajos_codigo
    ON operation.mv_metricas_trabajos (codigo);

COMMENT ON MATERIALIZED VIEW operation.mv_metricas_trabajos IS
'Métricas históricas acumuladas de cada trabajo programado.';

COMMIT;

/*
============================================================
 ACTUALIZACIÓN POSTERIOR

 Después de la creación inicial, estas vistas pueden actualizarse
 sin bloquear lecturas mediante los siguientes comandos, ejecutados
 fuera de una transacción explícita:

 REFRESH MATERIALIZED VIEW CONCURRENTLY market.mv_resumen_diario_activos;
 REFRESH MATERIALIZED VIEW CONCURRENTLY portfolio.mv_ultima_valoracion_portafolio;
 REFRESH MATERIALIZED VIEW CONCURRENTLY simulation.mv_estadisticas_simulacion;
 REFRESH MATERIALIZED VIEW CONCURRENTLY operation.mv_metricas_trabajos;
============================================================
*/