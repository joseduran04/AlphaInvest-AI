/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : 18_reporting.sql
Motor   : PostgreSQL
Objetivo: Crear una capa de reportes reutilizable para usuarios, mercado,
          portafolios, simulaciones, recomendaciones, auditoría y operación.

Dependencias:
- 03_auth_tables.sql
- 06_market_tables.sql
- 07_portfolio_tables.sql
- 08_simulation_tables.sql
- 09_ai_analysis_tables.sql
- 10_audit_operation_tables.sql
- 16_views.sql
- 17_materialized_views.sql

Características:
- No modifica datos de negocio.
- Idempotente mediante CREATE OR REPLACE VIEW.
- Centraliza columnas y cálculos usados por exportaciones y paneles.
- Permite aplicar filtros directamente con WHERE desde backend, DBeaver o BI.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS reporting;

COMMENT ON SCHEMA reporting IS
'Capa de consulta consolidada para reportes, exportaciones y paneles de AlphaInvest AI.';

/*
===============================================================================
1. REPORTE DE USUARIOS
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_usuarios AS
SELECT
    u.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    u.estado,
    u.correo_verificado,
    u.intentos_fallidos,
    u.bloqueado_hasta,
    u.ultimo_acceso,
    u.fecha_creacion,
    u.fecha_actualizacion,
    u.roles,
    CARDINALITY(u.roles) AS total_roles,
    CASE
        WHEN u.bloqueado_hasta IS NOT NULL
         AND u.bloqueado_hasta > CURRENT_TIMESTAMP
            THEN TRUE
        ELSE FALSE
    END AS bloqueado_actualmente
FROM auth.v_usuarios_roles u;

COMMENT ON VIEW reporting.v_reporte_usuarios IS
'Reporte consolidado de usuarios, roles y estado actual de bloqueo.';

/*
===============================================================================
2. REPORTE DE ACTIVOS Y ÚLTIMO PRECIO
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_activos_precios AS
SELECT
    a.activo_id,
    a.simbolo,
    a.activo_nombre,
    a.descripcion,
    a.moneda,
    a.sector,
    a.industria,
    a.isin,
    a.activo_estado,
    a.mercado_id,
    a.mercado_codigo,
    a.mercado_nombre,
    a.mercado_pais,
    a.mercado_zona_horaria,
    a.tipo_activo_id,
    a.tipo_activo_codigo,
    a.tipo_activo_nombre,
    p.fecha_precio,
    p.apertura,
    p.maximo,
    p.minimo,
    p.cierre,
    p.cierre_ajustado,
    p.volumen,
    p.fuente_id,
    p.fuente_nombre,
    p.fuente_proveedor,
    p.fecha_registro AS precio_fecha_registro,
    CASE
        WHEN p.fecha_precio IS NULL THEN NULL
        WHEN p.apertura IS NULL OR p.apertura = 0 THEN NULL
        ELSE ROUND(((p.cierre - p.apertura) / p.apertura) * 100, 8)
    END AS variacion_diaria_porcentaje,
    CASE
        WHEN p.fecha_precio IS NULL THEN NULL
        ELSE CURRENT_DATE - p.fecha_precio
    END AS antiguedad_precio_dias
FROM market.v_activos_catalogo a
LEFT JOIN market.v_ultimos_precios p
    ON p.activo_id = a.activo_id;

COMMENT ON VIEW reporting.v_reporte_activos_precios IS
'Reporte maestro de activos con su último precio y variación diaria calculada.';

/*
===============================================================================
3. REPORTE DE PORTAFOLIOS
===============================================================================
*/
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
    ON uv.portafolio_id = p.portafolio_id;

COMMENT ON VIEW reporting.v_reporte_portafolios IS
'Reporte consolidado de portafolios con valoración estimada y última valoración registrada.';

/*
===============================================================================
4. REPORTE DE SIMULACIONES
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_simulaciones AS
SELECT
    s.ejecucion_id,
    s.configuracion_id,
    s.configuracion_nombre,
    s.tipo_simulacion,
    s.capital_configurado,
    s.moneda_base,
    s.periodo_inicio,
    s.periodo_fin,
    s.usuario_id,
    s.nombres,
    s.apellidos,
    s.correo,
    s.version_modelo_id,
    s.version_modelo,
    s.modelo_codigo,
    s.modelo_nombre,
    s.estado,
    s.porcentaje_progreso,
    s.fecha_solicitud,
    s.fecha_inicio,
    s.fecha_fin,
    s.mensaje_error,
    s.identificador_proceso,
    s.resultado_id,
    s.capital_final,
    s.ganancia_perdida,
    s.rendimiento_total_porcentaje,
    s.rendimiento_anualizado_porcentaje,
    s.volatilidad_anualizada,
    s.indice_sharpe,
    s.maximo_drawdown_porcentaje,
    s.valor_en_riesgo,
    s.probabilidad_ganancia,
    s.fecha_resultado,
    CASE
        WHEN s.fecha_inicio IS NULL OR s.fecha_fin IS NULL THEN NULL
        ELSE EXTRACT(EPOCH FROM (s.fecha_fin - s.fecha_inicio))
    END AS duracion_segundos,
    CASE
        WHEN s.estado = 'COMPLETADA' AND s.resultado_id IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS resultado_disponible
FROM simulation.v_resumen_ejecuciones s;

COMMENT ON VIEW reporting.v_reporte_simulaciones IS
'Reporte detallado de ejecuciones de simulación, tiempos, modelo y resultados.';

/*
===============================================================================
5. REPORTE DE RECOMENDACIONES DE IA
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_recomendaciones AS
SELECT
    r.id AS recomendacion_id,
    r.solicitud_id,
    r.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    r.perfil_riesgo_id,
    r.portafolio_id,
    p.nombre AS portafolio_nombre,
    r.version_modelo_id,
    vm.version AS version_modelo,
    mi.codigo AS modelo_codigo,
    mi.nombre AS modelo_nombre,
    r.tipo,
    r.titulo,
    r.resumen,
    r.justificacion,
    r.nivel_riesgo,
    r.horizonte,
    r.confianza,
    r.prioridad,
    r.estado,
    r.advertencia,
    r.fecha_generacion,
    r.fecha_expiracion,
    r.fecha_aceptacion,
    r.fecha_rechazo,
    COUNT(ra.activo_id)::BIGINT AS total_activos_relacionados,
    COALESCE(
        ARRAY_AGG(DISTINCT a.simbolo ORDER BY a.simbolo)
            FILTER (WHERE a.id IS NOT NULL),
        ARRAY[]::VARCHAR[]
    ) AS simbolos_activos,
    CASE
        WHEN r.fecha_expiracion IS NOT NULL
         AND r.fecha_expiracion <= CURRENT_TIMESTAMP
         AND r.estado NOT IN ('ACEPTADA', 'RECHAZADA', 'RETIRADA')
            THEN TRUE
        ELSE FALSE
    END AS expirada_por_fecha
FROM ai.recomendaciones r
JOIN auth.usuarios u
    ON u.id = r.usuario_id
JOIN ai.versiones_modelo vm
    ON vm.id = r.version_modelo_id
JOIN ai.modelos_ia mi
    ON mi.id = vm.modelo_id
LEFT JOIN portfolio.portafolios p
    ON p.id = r.portafolio_id
LEFT JOIN ai.recomendacion_activos ra
    ON ra.recomendacion_id = r.id
LEFT JOIN market.activos a
    ON a.id = ra.activo_id
GROUP BY
    r.id,
    r.solicitud_id,
    r.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    r.perfil_riesgo_id,
    r.portafolio_id,
    p.nombre,
    r.version_modelo_id,
    vm.version,
    mi.codigo,
    mi.nombre,
    r.tipo,
    r.titulo,
    r.resumen,
    r.justificacion,
    r.nivel_riesgo,
    r.horizonte,
    r.confianza,
    r.prioridad,
    r.estado,
    r.advertencia,
    r.fecha_generacion,
    r.fecha_expiracion,
    r.fecha_aceptacion,
    r.fecha_rechazo;

COMMENT ON VIEW reporting.v_reporte_recomendaciones IS
'Reporte de recomendaciones generadas por IA con modelo, usuario, portafolio y activos relacionados.';

/*
===============================================================================
6. REPORTE DIARIO DE AUDITORÍA
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_auditoria_diaria AS
SELECT
    DATE_TRUNC('day', ra.fecha_evento)::DATE AS fecha,
    ra.esquema_entidad,
    ra.nombre_entidad,
    ra.accion,
    ra.origen,
    COUNT(*)::BIGINT AS total_eventos,
    COUNT(DISTINCT ra.usuario_id)::BIGINT AS usuarios_involucrados,
    COUNT(*) FILTER (WHERE ra.usuario_id IS NULL)::BIGINT AS eventos_sin_usuario,
    MIN(ra.fecha_evento) AS primer_evento,
    MAX(ra.fecha_evento) AS ultimo_evento
FROM audit.registros_auditoria ra
GROUP BY
    DATE_TRUNC('day', ra.fecha_evento)::DATE,
    ra.esquema_entidad,
    ra.nombre_entidad,
    ra.accion,
    ra.origen;

COMMENT ON VIEW reporting.v_reporte_auditoria_diaria IS
'Resumen diario de acciones de auditoría por entidad, acción y origen.';

/*
===============================================================================
7. REPORTE OPERATIVO DE TRABAJOS
===============================================================================
*/
CREATE OR REPLACE VIEW reporting.v_reporte_operacion_trabajos AS
SELECT
    e.trabajo_id,
    e.codigo,
    e.nombre,
    e.descripcion,
    e.tipo,
    e.activo,
    e.expresion_cron,
    e.intervalo_segundos,
    e.zona_horaria,
    e.permite_concurrencia,
    e.tiempo_maximo_segundos,
    e.maximo_reintentos,
    e.siguiente_ejecucion,
    e.ultima_ejecucion,
    e.ultima_ejecucion_id,
    e.ultima_ejecucion_estado,
    e.ultima_ejecucion_intento,
    e.ultima_ejecucion_disparador,
    e.ultima_ejecucion_fecha_solicitud,
    e.ultima_ejecucion_fecha_inicio,
    e.ultima_ejecucion_fecha_fin,
    e.ultima_ejecucion_progreso,
    e.registros_procesados,
    e.registros_exitosos,
    e.registros_fallidos,
    e.ultima_ejecucion_error,
    m.total_ejecuciones,
    m.ejecuciones_completadas,
    m.ejecuciones_fallidas,
    m.ejecuciones_canceladas,
    m.ejecuciones_en_curso,
    m.duracion_promedio_segundos,
    m.ultima_solicitud,
    m.ultima_finalizacion,
    CASE
        WHEN m.total_ejecuciones = 0 THEN NULL
        ELSE ROUND(
            (m.ejecuciones_completadas::NUMERIC / m.total_ejecuciones::NUMERIC) * 100,
            4
        )
    END AS tasa_exito_porcentaje
FROM operation.v_estado_trabajos_programados e
LEFT JOIN operation.mv_metricas_trabajos m
    ON m.trabajo_id = e.trabajo_id;

COMMENT ON VIEW reporting.v_reporte_operacion_trabajos IS
'Reporte operativo de trabajos programados con última ejecución y métricas acumuladas.';

COMMIT;

/*
===============================================================================
CONSULTAS DE VALIDACIÓN SUGERIDAS
===============================================================================

SELECT * FROM reporting.v_reporte_usuarios
ORDER BY fecha_creacion DESC;

SELECT * FROM reporting.v_reporte_activos_precios
ORDER BY mercado_codigo, simbolo;

SELECT * FROM reporting.v_reporte_portafolios
ORDER BY fecha_creacion DESC;

SELECT * FROM reporting.v_reporte_simulaciones
ORDER BY fecha_solicitud DESC;

SELECT * FROM reporting.v_reporte_recomendaciones
ORDER BY fecha_generacion DESC;

SELECT * FROM reporting.v_reporte_auditoria_diaria
ORDER BY fecha DESC, esquema_entidad, nombre_entidad;

SELECT * FROM reporting.v_reporte_operacion_trabajos
ORDER BY codigo;

===============================================================================
*/