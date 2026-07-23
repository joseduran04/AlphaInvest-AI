Biblioteca
/
AlphaInvest_AI
/
16_views.sql


/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : 16_views.sql
Motor   : PostgreSQL
Objetivo: Crear vistas de consulta para simplificar el acceso a la información
          consolidada de autenticación, mercado, portafolios, perfil de riesgo,
          simulaciones, modelos de IA y operación.

Características:
- Compatible con PostgreSQL.
- Transaccional.
- Idempotente mediante CREATE OR REPLACE VIEW.
- No inserta, actualiza ni elimina datos de negocio.
- Construido únicamente con tablas y columnas existentes en los scripts 03-10.
===============================================================================
*/

BEGIN;

/*
===============================================================================
1. USUARIOS CON ROLES
===============================================================================
Resume los datos básicos de cada usuario y todos sus roles activos.
La agregación evita devolver una fila duplicada por cada rol asignado.
*/
CREATE OR REPLACE VIEW auth.v_usuarios_roles AS
SELECT
    u.id AS usuario_id,
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
    COALESCE
    (
        ARRAY_AGG(DISTINCT r.nombre ORDER BY r.nombre)
            FILTER (WHERE r.id IS NOT NULL AND r.activo),
        ARRAY[]::VARCHAR[]
    ) AS roles
FROM auth.usuarios u
LEFT JOIN auth.usuario_roles ur
    ON ur.usuario_id = u.id
LEFT JOIN auth.roles r
    ON r.id = ur.rol_id
GROUP BY
    u.id,
    u.nombres,
    u.apellidos,
    u.correo,
    u.estado,
    u.correo_verificado,
    u.intentos_fallidos,
    u.bloqueado_hasta,
    u.ultimo_acceso,
    u.fecha_creacion,
    u.fecha_actualizacion;

COMMENT ON VIEW auth.v_usuarios_roles IS
'Usuarios del sistema con sus roles activos agregados en un arreglo.';

/*
===============================================================================
2. CATÁLOGO CONSOLIDADO DE ACTIVOS
===============================================================================
Expone cada activo junto con la información descriptiva de su mercado y tipo.
*/
CREATE OR REPLACE VIEW market.v_activos_catalogo AS
SELECT
    a.id AS activo_id,
    a.simbolo,
    a.nombre AS activo_nombre,
    a.descripcion,
    a.moneda,
    a.sector,
    a.industria,
    a.isin,
    a.estado AS activo_estado,
    a.fecha_alta,
    a.fecha_actualizacion,
    m.id AS mercado_id,
    m.codigo AS mercado_codigo,
    m.nombre AS mercado_nombre,
    m.pais AS mercado_pais,
    m.zona_horaria AS mercado_zona_horaria,
    m.moneda AS mercado_moneda,
    m.activo AS mercado_activo,
    ta.id AS tipo_activo_id,
    ta.codigo AS tipo_activo_codigo,
    ta.nombre AS tipo_activo_nombre,
    ta.activo AS tipo_activo_activo
FROM market.activos a
JOIN market.mercados m
    ON m.id = a.mercado_id
JOIN market.tipos_activo ta
    ON ta.id = a.tipo_activo_id;

COMMENT ON VIEW market.v_activos_catalogo IS
'Catálogo consolidado de activos con su mercado y tipo de activo.';

/*
===============================================================================
3. ÚLTIMO PRECIO DISPONIBLE POR ACTIVO
===============================================================================
DISTINCT ON selecciona el precio más reciente de cada activo. En caso de existir
más de un registro con la misma fecha, se prioriza el de registro más reciente.
*/
CREATE OR REPLACE VIEW market.v_ultimos_precios AS
SELECT DISTINCT ON (ph.activo_id)
    ph.activo_id,
    a.simbolo,
    a.nombre AS activo_nombre,
    m.codigo AS mercado_codigo,
    ta.codigo AS tipo_activo_codigo,
    ph.fecha AS fecha_precio,
    ph.apertura,
    ph.maximo,
    ph.minimo,
    ph.cierre,
    ph.cierre_ajustado,
    ph.volumen,
    ph.moneda,
    ph.fuente_id,
    ff.nombre AS fuente_nombre,
    ff.proveedor AS fuente_proveedor,
    ph.fecha_registro
FROM market.precios_historicos ph
JOIN market.activos a
    ON a.id = ph.activo_id
JOIN market.mercados m
    ON m.id = a.mercado_id
JOIN market.tipos_activo ta
    ON ta.id = a.tipo_activo_id
LEFT JOIN market.fuentes_financieras ff
    ON ff.id = ph.fuente_id
ORDER BY
    ph.activo_id,
    ph.fecha DESC,
    ph.fecha_registro DESC,
    ph.id DESC;

COMMENT ON VIEW market.v_ultimos_precios IS
'Último precio histórico disponible de cada activo financiero.';

/*
===============================================================================
4. RESUMEN DE PORTAFOLIOS
===============================================================================
Consolida el estado del portafolio y sus posiciones sin depender de que exista
una valoración histórica. Los importes se calculan con las columnas mantenidas
por las funciones y triggers del módulo portfolio.
*/
CREATE OR REPLACE VIEW portfolio.v_resumen_portafolios AS
SELECT
    p.id AS portafolio_id,
    p.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    p.nombre AS portafolio_nombre,
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
    COUNT(pos.id) FILTER (WHERE pos.estado = 'ABIERTA') AS posiciones_abiertas,
    COUNT(pos.id) AS posiciones_totales,
    COALESCE
    (
        SUM(pos.costo_total) FILTER (WHERE pos.estado = 'ABIERTA'),
        0
    ) AS capital_invertido,
    COALESCE
    (
        SUM(pos.valor_actual) FILTER (WHERE pos.estado = 'ABIERTA'),
        0
    ) AS valor_posiciones,
    p.saldo_efectivo
        + COALESCE
          (
              SUM(pos.valor_actual) FILTER (WHERE pos.estado = 'ABIERTA'),
              0
          ) AS valor_total_estimado,
    COALESCE
    (
        SUM(pos.ganancia_perdida) FILTER (WHERE pos.estado = 'ABIERTA'),
        0
    ) AS ganancia_perdida_posiciones
FROM portfolio.portafolios p
JOIN auth.usuarios u
    ON u.id = p.usuario_id
LEFT JOIN portfolio.posiciones pos
    ON pos.portafolio_id = p.id
GROUP BY
    p.id,
    p.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    p.nombre,
    p.descripcion,
    p.moneda_base,
    p.capital_inicial,
    p.saldo_efectivo,
    p.tipo,
    p.estado,
    p.fecha_inicio,
    p.fecha_cierre,
    p.fecha_creacion,
    p.fecha_actualizacion;

COMMENT ON VIEW portfolio.v_resumen_portafolios IS
'Resumen de portafolios con conteo y valuación estimada de posiciones.';

/*
===============================================================================
5. PERFILES DE RIESGO VIGENTES
===============================================================================
Muestra únicamente el perfil marcado como vigente y conserva la referencia a
la evaluación que le dio origen.
*/
CREATE OR REPLACE VIEW profile.v_perfiles_riesgo_vigentes AS
SELECT
    pr.id AS perfil_riesgo_id,
    pr.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    pr.evaluacion_id,
    er.cuestionario_id,
    c.nombre AS cuestionario_nombre,
    er.version_cuestionario,
    pr.clasificacion,
    pr.puntuacion,
    pr.confianza,
    pr.descripcion,
    pr.vigente,
    pr.fecha_inicio,
    pr.fecha_fin,
    pr.fecha_creacion,
    er.metodo_clasificacion,
    er.version_modelo_id,
    er.fecha_evaluacion,
    er.estado AS evaluacion_estado
FROM profile.perfiles_riesgo pr
JOIN auth.usuarios u
    ON u.id = pr.usuario_id
JOIN profile.evaluaciones_riesgo er
    ON er.id = pr.evaluacion_id
JOIN profile.cuestionarios c
    ON c.id = er.cuestionario_id
WHERE pr.vigente = TRUE;

COMMENT ON VIEW profile.v_perfiles_riesgo_vigentes IS
'Perfil de riesgo vigente de cada usuario con su evaluación de origen.';

/*
===============================================================================
6. RESUMEN DE EJECUCIONES DE SIMULACIÓN
===============================================================================
Une la ejecución con su configuración, usuario, modelo y resultado agregado.
Una ejecución pendiente o fallida puede no tener aún un resultado asociado.
*/
CREATE OR REPLACE VIEW simulation.v_resumen_ejecuciones AS
SELECT
    e.id AS ejecucion_id,
    e.configuracion_id,
    c.nombre AS configuracion_nombre,
    c.tipo_simulacion,
    c.capital_inicial AS capital_configurado,
    c.moneda_base,
    c.fecha_inicio AS periodo_inicio,
    c.fecha_fin AS periodo_fin,
    e.usuario_id,
    u.nombres,
    u.apellidos,
    u.correo,
    e.version_modelo_id,
    vm.version AS version_modelo,
    mi.codigo AS modelo_codigo,
    mi.nombre AS modelo_nombre,
    e.estado,
    e.porcentaje_progreso,
    e.fecha_solicitud,
    e.fecha_inicio,
    e.fecha_fin,
    e.mensaje_error,
    e.identificador_proceso,
    r.id AS resultado_id,
    r.capital_final,
    r.ganancia_perdida,
    r.rendimiento_total_porcentaje,
    r.rendimiento_anualizado_porcentaje,
    r.volatilidad_anualizada,
    r.indice_sharpe,
    r.maximo_drawdown_porcentaje,
    r.valor_en_riesgo,
    r.probabilidad_ganancia,
    r.fecha_registro AS fecha_resultado
FROM simulation.ejecuciones e
JOIN simulation.configuraciones c
    ON c.id = e.configuracion_id
JOIN auth.usuarios u
    ON u.id = e.usuario_id
LEFT JOIN ai.versiones_modelo vm
    ON vm.id = e.version_modelo_id
LEFT JOIN ai.modelos_ia mi
    ON mi.id = vm.modelo_id
LEFT JOIN simulation.resultados r
    ON r.ejecucion_id = e.id;

COMMENT ON VIEW simulation.v_resumen_ejecuciones IS
'Resumen de ejecuciones de simulación con configuración, modelo y resultado.';

/*
===============================================================================
7. MODELOS DE IA Y VERSIÓN ACTIVA
===============================================================================
Expone todos los modelos registrados y, cuando exista, su única versión activa.
El índice único parcial uq_version_activa_modelo garantiza una versión activa
como máximo por modelo.
*/
CREATE OR REPLACE VIEW ai.v_modelos_versiones_activas AS
SELECT
    m.id AS modelo_id,
    m.codigo,
    m.nombre,
    m.tipo,
    m.objetivo,
    m.descripcion,
    m.estado AS modelo_estado,
    m.fecha_creacion,
    m.fecha_actualizacion,
    vm.id AS version_modelo_id,
    vm.version,
    vm.ruta_artefacto,
    vm.checksum,
    vm.algoritmo,
    vm.framework,
    vm.hiperparametros,
    vm.metricas,
    vm.conjunto_entrenamiento,
    vm.fecha_entrenamiento,
    vm.fecha_activacion,
    vm.creada_por,
    vm.fecha_registro
FROM ai.modelos_ia m
LEFT JOIN ai.versiones_modelo vm
    ON vm.modelo_id = m.id
   AND vm.activa = TRUE;

COMMENT ON VIEW ai.v_modelos_versiones_activas IS
'Modelos de inteligencia artificial con la versión activa, cuando exista.';

/*
===============================================================================
8. ESTADO DE TRABAJOS PROGRAMADOS
===============================================================================
Muestra cada trabajo junto con su ejecución más reciente, obtenida mediante un
JOIN LATERAL ordenado por fecha de solicitud.
*/
CREATE OR REPLACE VIEW operation.v_estado_trabajos_programados AS
SELECT
    tp.id AS trabajo_id,
    tp.codigo,
    tp.nombre,
    tp.descripcion,
    tp.tipo,
    tp.expresion_cron,
    tp.intervalo_segundos,
    tp.zona_horaria,
    tp.parametros,
    tp.activo,
    tp.permite_concurrencia,
    tp.tiempo_maximo_segundos,
    tp.maximo_reintentos,
    tp.siguiente_ejecucion,
    tp.ultima_ejecucion,
    tp.creado_por,
    tp.fecha_creacion,
    tp.fecha_actualizacion,
    et.id AS ultima_ejecucion_id,
    et.estado AS ultima_ejecucion_estado,
    et.numero_intento AS ultima_ejecucion_intento,
    et.disparador AS ultima_ejecucion_disparador,
    et.fecha_solicitud AS ultima_ejecucion_fecha_solicitud,
    et.fecha_inicio AS ultima_ejecucion_fecha_inicio,
    et.fecha_fin AS ultima_ejecucion_fecha_fin,
    et.progreso AS ultima_ejecucion_progreso,
    et.registros_procesados,
    et.registros_exitosos,
    et.registros_fallidos,
    et.mensaje_error AS ultima_ejecucion_error
FROM operation.trabajos_programados tp
LEFT JOIN LATERAL
(
    SELECT e.*
    FROM operation.ejecuciones_trabajo e
    WHERE e.trabajo_id = tp.id
    ORDER BY
        e.fecha_solicitud DESC,
        e.id DESC
    LIMIT 1
) et ON TRUE;

COMMENT ON VIEW operation.v_estado_trabajos_programados IS
'Trabajos programados con el estado y métricas de su ejecución más reciente.';

COMMIT;

/*
===============================================================================
CONSULTAS DE VALIDACIÓN SUGERIDAS
===============================================================================

SELECT * FROM auth.v_usuarios_roles LIMIT 10;
SELECT * FROM market.v_activos_catalogo ORDER BY mercado_codigo, simbolo;
SELECT * FROM market.v_ultimos_precios ORDER BY mercado_codigo, simbolo;
SELECT * FROM portfolio.v_resumen_portafolios LIMIT 10;
SELECT * FROM profile.v_perfiles_riesgo_vigentes LIMIT 10;
SELECT * FROM simulation.v_resumen_ejecuciones ORDER BY fecha_solicitud DESC;
SELECT * FROM ai.v_modelos_versiones_activas ORDER BY codigo;
SELECT * FROM operation.v_estado_trabajos_programados ORDER BY codigo;

===============================================================================
*/