/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : 21_test_data.sql
Motor   : PostgreSQL
Objetivo: Cargar datos de prueba controlados, identificables, idempotentes y
          eliminables para validar autenticación, mercado, portafolios,
          simulaciones y operación.

IMPORTANTE:
- Ejecutar solamente en ambientes de desarrollo o pruebas.
- No ejecutar en producción.
- Todos los registros principales se identifican con el prefijo TEST_ o con
  correos bajo el dominio example.test.
- El script depende de las partes 03 a 20.
- La contraseña de los usuarios de prueba es únicamente para desarrollo:
      AlphaTest2026!
===============================================================================
*/

BEGIN;

/*
===============================================================================
0. PROTECCIÓN DE AMBIENTE
===============================================================================
Por seguridad, el script exige que la base no tenga un nombre claramente
productivo. Ajustar la lista si el proyecto utiliza otra convención.
*/
DO $$
DECLARE
    v_database TEXT := LOWER(CURRENT_DATABASE());
BEGIN
    IF v_database LIKE '%prod%'
       OR v_database LIKE '%production%'
       OR v_database LIKE '%produccion%'
    THEN
        RAISE EXCEPTION
            '21_test_data.sql no puede ejecutarse en una base identificada como producción: %',
            CURRENT_DATABASE();
    END IF;
END;
$$;

/*
===============================================================================
1. USUARIOS DE PRUEBA
===============================================================================
Se utiliza crypt/gen_salt de pgcrypto, habilitada en 01_extensions.sql.
La clave natural esperada es auth.usuarios.correo.
*/
INSERT INTO auth.usuarios
(
    nombres,
    apellidos,
    correo,
    password_hash,
    estado,
    correo_verificado,
    intentos_fallidos
)
VALUES
(
    'Usuario',
    'Conservador TEST',
    'test.conservador@example.test',
    crypt('AlphaTest2026!', gen_salt('bf', 10)),
    'ACTIVO',
    TRUE,
    0
),
(
    'Usuario',
    'Moderado TEST',
    'test.moderado@example.test',
    crypt('AlphaTest2026!', gen_salt('bf', 10)),
    'ACTIVO',
    TRUE,
    0
),
(
    'Usuario',
    'Agresivo TEST',
    'test.agresivo@example.test',
    crypt('AlphaTest2026!', gen_salt('bf', 10)),
    'ACTIVO',
    TRUE,
    0
)
ON CONFLICT (correo)
DO UPDATE SET
    nombres = EXCLUDED.nombres,
    apellidos = EXCLUDED.apellidos,
    estado = EXCLUDED.estado,
    correo_verificado = EXCLUDED.correo_verificado,
    intentos_fallidos = 0,
    fecha_actualizacion = CURRENT_TIMESTAMP;

/*
===============================================================================
2. ASIGNACIÓN DEL ROL INVERSIONISTA
===============================================================================
*/
INSERT INTO auth.usuario_roles
(
    usuario_id,
    rol_id
)
SELECT
    u.id,
    r.id
FROM auth.usuarios u
JOIN auth.roles r
    ON r.nombre = 'INVERSIONISTA'
WHERE u.correo IN
(
    'test.conservador@example.test',
    'test.moderado@example.test',
    'test.agresivo@example.test'
)
ON CONFLICT (usuario_id, rol_id)
DO NOTHING;

/*
===============================================================================
3. PRECIOS HISTÓRICOS DE PRUEBA
===============================================================================
Se cargan cinco días para AAPL, MSFT, NVDA, SPY y QQQ.
La fuente utilizada es Carga Manual.
===============================================================================
*/
WITH datos(simbolo, fecha, apertura, maximo, minimo, cierre, cierre_ajustado, volumen) AS
(
    VALUES
        ('AAPL', CURRENT_DATE - 4, 210.00, 214.00, 208.50, 213.20, 213.20, 55000000::BIGINT),
        ('AAPL', CURRENT_DATE - 3, 213.50, 216.00, 211.80, 215.10, 215.10, 52000000::BIGINT),
        ('AAPL', CURRENT_DATE - 2, 215.00, 217.40, 213.90, 216.70, 216.70, 50000000::BIGINT),
        ('AAPL', CURRENT_DATE - 1, 216.40, 219.00, 215.70, 218.60, 218.60, 48000000::BIGINT),
        ('AAPL', CURRENT_DATE,     218.80, 221.00, 217.90, 220.40, 220.40, 51000000::BIGINT),

        ('MSFT', CURRENT_DATE - 4, 498.00, 503.00, 496.00, 501.50, 501.50, 24000000::BIGINT),
        ('MSFT', CURRENT_DATE - 3, 501.00, 505.50, 499.50, 504.20, 504.20, 23000000::BIGINT),
        ('MSFT', CURRENT_DATE - 2, 504.00, 508.00, 502.00, 506.70, 506.70, 22500000::BIGINT),
        ('MSFT', CURRENT_DATE - 1, 506.50, 510.00, 505.00, 509.10, 509.10, 22000000::BIGINT),
        ('MSFT', CURRENT_DATE,     509.00, 513.00, 507.50, 512.30, 512.30, 23500000::BIGINT),

        ('NVDA', CURRENT_DATE - 4, 176.00, 181.00, 174.00, 179.50, 179.50, 185000000::BIGINT),
        ('NVDA', CURRENT_DATE - 3, 179.00, 183.50, 177.50, 182.20, 182.20, 178000000::BIGINT),
        ('NVDA', CURRENT_DATE - 2, 182.00, 186.00, 180.00, 184.80, 184.80, 172000000::BIGINT),
        ('NVDA', CURRENT_DATE - 1, 184.50, 188.00, 183.00, 187.10, 187.10, 169000000::BIGINT),
        ('NVDA', CURRENT_DATE,     187.00, 190.50, 185.50, 189.60, 189.60, 175000000::BIGINT),

        ('SPY', CURRENT_DATE - 4, 625.00, 629.00, 623.50, 628.00, 628.00, 68000000::BIGINT),
        ('SPY', CURRENT_DATE - 3, 628.00, 631.00, 626.50, 630.20, 630.20, 65000000::BIGINT),
        ('SPY', CURRENT_DATE - 2, 630.00, 633.50, 628.50, 632.70, 632.70, 64000000::BIGINT),
        ('SPY', CURRENT_DATE - 1, 632.50, 635.00, 631.00, 634.40, 634.40, 62000000::BIGINT),
        ('SPY', CURRENT_DATE,     634.00, 637.00, 632.50, 636.20, 636.20, 66000000::BIGINT),

        ('QQQ', CURRENT_DATE - 4, 558.00, 563.00, 556.00, 561.50, 561.50, 47000000::BIGINT),
        ('QQQ', CURRENT_DATE - 3, 561.00, 565.00, 559.00, 564.10, 564.10, 45000000::BIGINT),
        ('QQQ', CURRENT_DATE - 2, 564.00, 568.00, 562.00, 567.20, 567.20, 44000000::BIGINT),
        ('QQQ', CURRENT_DATE - 1, 567.00, 571.00, 565.50, 570.10, 570.10, 43000000::BIGINT),
        ('QQQ', CURRENT_DATE,     570.00, 574.00, 568.50, 573.20, 573.20, 46000000::BIGINT)
)
INSERT INTO market.precios_historicos
(
    activo_id,
    fuente_id,
    fecha,
    apertura,
    maximo,
    minimo,
    cierre,
    cierre_ajustado,
    volumen,
    moneda
)
SELECT
    a.id,
    f.id,
    d.fecha,
    d.apertura,
    d.maximo,
    d.minimo,
    d.cierre,
    d.cierre_ajustado,
    d.volumen,
    a.moneda
FROM datos d
JOIN market.activos a
    ON a.simbolo = d.simbolo
JOIN market.fuentes_financieras f
    ON f.nombre = 'Carga Manual'
ON CONFLICT (activo_id, fuente_id, fecha)
DO UPDATE SET
    apertura = EXCLUDED.apertura,
    maximo = EXCLUDED.maximo,
    minimo = EXCLUDED.minimo,
    cierre = EXCLUDED.cierre,
    cierre_ajustado = EXCLUDED.cierre_ajustado,
    volumen = EXCLUDED.volumen,
    moneda = EXCLUDED.moneda,
    fecha_registro = CURRENT_TIMESTAMP;

/*
===============================================================================
4. PORTAFOLIOS DE PRUEBA
===============================================================================
*/
INSERT INTO portfolio.portafolios
(
    usuario_id,
    nombre,
    descripcion,
    moneda_base,
    capital_inicial,
    saldo_efectivo,
    tipo,
    estado,
    fecha_inicio
)
SELECT
    u.id,
    v.nombre,
    v.descripcion,
    'USD',
    v.capital_inicial,
    v.saldo_efectivo,
    'VIRTUAL',
    'ACTIVO',
    CURRENT_DATE - 30
FROM
(
    VALUES
        ('test.conservador@example.test', 'TEST_Portafolio_Conservador',
         'Portafolio de prueba con mayor ponderación en ETF.', 10000.00, 4000.00),
        ('test.moderado@example.test', 'TEST_Portafolio_Moderado',
         'Portafolio de prueba diversificado entre ETF y tecnología.', 15000.00, 4500.00),
        ('test.agresivo@example.test', 'TEST_Portafolio_Agresivo',
         'Portafolio de prueba concentrado en acciones de crecimiento.', 20000.00, 5000.00)
) AS v(correo, nombre, descripcion, capital_inicial, saldo_efectivo)
JOIN auth.usuarios u
    ON u.correo = v.correo
ON CONFLICT (usuario_id, nombre)
DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    moneda_base = EXCLUDED.moneda_base,
    capital_inicial = EXCLUDED.capital_inicial,
    saldo_efectivo = EXCLUDED.saldo_efectivo,
    tipo = EXCLUDED.tipo,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;

/*
===============================================================================
5. POSICIONES DE PRUEBA
===============================================================================
Los importes se calculan explícitamente para que el script no dependa de que
los triggers estén habilitados durante la carga.
===============================================================================
*/
WITH datos(portafolio_nombre, simbolo, cantidad, precio_compra, precio_actual) AS
(
    VALUES
        ('TEST_Portafolio_Conservador', 'SPY',  6.00000000, 620.00, 636.20),
        ('TEST_Portafolio_Conservador', 'QQQ',  4.00000000, 550.00, 573.20),

        ('TEST_Portafolio_Moderado', 'SPY',   5.00000000, 620.00, 636.20),
        ('TEST_Portafolio_Moderado', 'AAPL', 15.00000000, 205.00, 220.40),
        ('TEST_Portafolio_Moderado', 'MSFT',  8.00000000, 490.00, 512.30),

        ('TEST_Portafolio_Agresivo', 'NVDA', 40.00000000, 165.00, 189.60),
        ('TEST_Portafolio_Agresivo', 'AAPL', 20.00000000, 205.00, 220.40),
        ('TEST_Portafolio_Agresivo', 'MSFT',  8.00000000, 490.00, 512.30)
)
INSERT INTO portfolio.posiciones
(
    portafolio_id,
    activo_id,
    cantidad,
    precio_promedio_compra,
    costo_total,
    precio_actual,
    valor_actual,
    ganancia_perdida,
    rendimiento_porcentaje,
    moneda,
    estado,
    fecha_apertura,
    fecha_actualizacion
)
SELECT
    p.id,
    a.id,
    d.cantidad,
    d.precio_compra,
    ROUND(d.cantidad * d.precio_compra, 8),
    d.precio_actual,
    ROUND(d.cantidad * d.precio_actual, 8),
    ROUND(d.cantidad * (d.precio_actual - d.precio_compra), 8),
    ROUND(((d.precio_actual - d.precio_compra) / NULLIF(d.precio_compra, 0)) * 100, 8),
    a.moneda,
    'ABIERTA',
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP
FROM datos d
JOIN portfolio.portafolios p
    ON p.nombre = d.portafolio_nombre
JOIN market.activos a
    ON a.simbolo = d.simbolo
ON CONFLICT (portafolio_id, activo_id)
DO UPDATE SET
    cantidad = EXCLUDED.cantidad,
    precio_promedio_compra = EXCLUDED.precio_promedio_compra,
    costo_total = EXCLUDED.costo_total,
    precio_actual = EXCLUDED.precio_actual,
    valor_actual = EXCLUDED.valor_actual,
    ganancia_perdida = EXCLUDED.ganancia_perdida,
    rendimiento_porcentaje = EXCLUDED.rendimiento_porcentaje,
    moneda = EXCLUDED.moneda,
    estado = 'ABIERTA',
    fecha_actualizacion = CURRENT_TIMESTAMP,
    fecha_cierre = NULL;

/*
===============================================================================
6. VALORACIONES DE PORTAFOLIO
===============================================================================
*/
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
    moneda
)
SELECT
    p.id,
    CURRENT_TIMESTAMP,
    p.saldo_efectivo,
    COALESCE(SUM(pos.valor_actual) FILTER (WHERE pos.estado = 'ABIERTA'), 0),
    p.saldo_efectivo
        + COALESCE(SUM(pos.valor_actual) FILTER (WHERE pos.estado = 'ABIERTA'), 0),
    COALESCE(SUM(pos.costo_total) FILTER (WHERE pos.estado = 'ABIERTA'), 0),
    p.saldo_efectivo
        + COALESCE(SUM(pos.valor_actual) FILTER (WHERE pos.estado = 'ABIERTA'), 0)
        - p.capital_inicial,
    CASE
        WHEN p.capital_inicial = 0 THEN 0
        ELSE ROUND(
            (
                (
                    p.saldo_efectivo
                    + COALESCE(SUM(pos.valor_actual)
                        FILTER (WHERE pos.estado = 'ABIERTA'), 0)
                    - p.capital_inicial
                ) / p.capital_inicial
            ) * 100,
            8
        )
    END,
    p.moneda_base
FROM portfolio.portafolios p
LEFT JOIN portfolio.posiciones pos
    ON pos.portafolio_id = p.id
WHERE p.nombre LIKE 'TEST\_%' ESCAPE '\'
GROUP BY
    p.id,
    p.saldo_efectivo,
    p.capital_inicial,
    p.moneda_base;

/*
===============================================================================
7. CONFIGURACIONES DE SIMULACIÓN
===============================================================================
*/
INSERT INTO simulation.configuraciones
(
    usuario_id,
    nombre,
    descripcion,
    tipo_simulacion,
    capital_inicial,
    moneda_base,
    fecha_inicio,
    fecha_fin,
    aportacion_periodica,
    frecuencia_aportacion,
    comision_porcentaje,
    inflacion_anual,
    tasa_libre_riesgo,
    numero_escenarios,
    semilla_aleatoria,
    parametros,
    estado
)
SELECT
    u.id,
    'TEST_Backtest_SPY_1A',
    'Configuración de prueba para validar simulación histórica.',
    'HISTORICA',
    10000.00,
    'USD',
    (CURRENT_DATE - INTERVAL '1 year')::DATE,
    CURRENT_DATE,
    0.00,
    NULL,
    0.10,
    3.50,
    4.00,
    1,
    20260723,
    '{"activo":"SPY","estrategia":"comprar_y_mantener","entorno":"TEST"}'::JSONB,
    'LISTA'
FROM auth.usuarios u
WHERE u.correo = 'test.moderado@example.test'
ON CONFLICT (usuario_id, nombre)
DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    tipo_simulacion = EXCLUDED.tipo_simulacion,
    capital_inicial = EXCLUDED.capital_inicial,
    moneda_base = EXCLUDED.moneda_base,
    fecha_inicio = EXCLUDED.fecha_inicio,
    fecha_fin = EXCLUDED.fecha_fin,
    aportacion_periodica = EXCLUDED.aportacion_periodica,
    frecuencia_aportacion = EXCLUDED.frecuencia_aportacion,
    comision_porcentaje = EXCLUDED.comision_porcentaje,
    inflacion_anual = EXCLUDED.inflacion_anual,
    tasa_libre_riesgo = EXCLUDED.tasa_libre_riesgo,
    numero_escenarios = EXCLUDED.numero_escenarios,
    semilla_aleatoria = EXCLUDED.semilla_aleatoria,
    parametros = EXCLUDED.parametros,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;

/*
===============================================================================
8. DISTRIBUCIÓN DE ACTIVOS DE LA CONFIGURACIÓN
===============================================================================
El trigger de simulation.ejecuciones exige que la configuración incluya al
menos un activo y que la suma de porcentaje_asignado sea exactamente 100.
*/
INSERT INTO simulation.configuracion_activos
(
    configuracion_id,
    activo_id,
    porcentaje_asignado,
    monto_inicial,
    precio_inicial,
    orden,
    parametros
)
SELECT
    c.id,
    a.id,
    100.00000000,
    c.capital_inicial,
    620.00000000,
    1,
    '{"entorno":"TEST","estrategia":"comprar_y_mantener"}'::JSONB
FROM simulation.configuraciones c
JOIN market.activos a
    ON a.simbolo = 'SPY'
WHERE c.nombre = 'TEST_Backtest_SPY_1A'
ON CONFLICT (configuracion_id, activo_id)
DO UPDATE SET
    porcentaje_asignado = EXCLUDED.porcentaje_asignado,
    monto_inicial = EXCLUDED.monto_inicial,
    precio_inicial = EXCLUDED.precio_inicial,
    orden = EXCLUDED.orden,
    parametros = EXCLUDED.parametros;

/*
===============================================================================
9. EJECUCIÓN Y RESULTADO DE SIMULACIÓN
===============================================================================
*/
INSERT INTO simulation.ejecuciones
(
    configuracion_id,
    usuario_id,
    version_modelo_id,
    estado,
    porcentaje_progreso,
    fecha_solicitud,
    fecha_inicio,
    fecha_fin,
    identificador_proceso
)
SELECT
    c.id,
    c.usuario_id,
    NULL,
    'COMPLETADA',
    100.00,
    CURRENT_TIMESTAMP - INTERVAL '2 minutes',
    CURRENT_TIMESTAMP - INTERVAL '110 seconds',
    CURRENT_TIMESTAMP - INTERVAL '10 seconds',
    'TEST_SIM_SPY_001'
FROM simulation.configuraciones c
WHERE c.nombre = 'TEST_Backtest_SPY_1A'
ON CONFLICT (identificador_proceso)
DO UPDATE SET
    estado = EXCLUDED.estado,
    porcentaje_progreso = EXCLUDED.porcentaje_progreso,
    fecha_inicio = EXCLUDED.fecha_inicio,
    fecha_fin = EXCLUDED.fecha_fin,
    mensaje_error = NULL;

INSERT INTO simulation.resultados
(
    ejecucion_id,
    capital_inicial,
    aportaciones_totales,
    capital_final,
    ganancia_perdida,
    rendimiento_total_porcentaje,
    rendimiento_anualizado_porcentaje,
    volatilidad_anualizada,
    indice_sharpe,
    maximo_drawdown_porcentaje,
    valor_en_riesgo,
    nivel_confianza_var,
    mejor_escenario,
    peor_escenario,
    mediana_escenarios,
    probabilidad_ganancia,
    moneda,
    resumen
)
SELECT
    e.id,
    10000.00,
    0.00,
    11280.00,
    1280.00,
    12.80000000,
    12.80000000,
    15.40000000,
    0.83000000,
    8.20000000,
    420.00,
    0.95000000,
    11850.00,
    9100.00,
    10950.00,
    0.64000000,
    'USD',
    '{"entorno":"TEST","operaciones":12,"dias_positivos":148}'::JSONB
FROM simulation.ejecuciones e
WHERE e.identificador_proceso = 'TEST_SIM_SPY_001'
ON CONFLICT (ejecucion_id)
DO UPDATE SET
    capital_inicial = EXCLUDED.capital_inicial,
    aportaciones_totales = EXCLUDED.aportaciones_totales,
    capital_final = EXCLUDED.capital_final,
    ganancia_perdida = EXCLUDED.ganancia_perdida,
    rendimiento_total_porcentaje = EXCLUDED.rendimiento_total_porcentaje,
    rendimiento_anualizado_porcentaje = EXCLUDED.rendimiento_anualizado_porcentaje,
    volatilidad_anualizada = EXCLUDED.volatilidad_anualizada,
    indice_sharpe = EXCLUDED.indice_sharpe,
    maximo_drawdown_porcentaje = EXCLUDED.maximo_drawdown_porcentaje,
    valor_en_riesgo = EXCLUDED.valor_en_riesgo,
    nivel_confianza_var = EXCLUDED.nivel_confianza_var,
    mejor_escenario = EXCLUDED.mejor_escenario,
    peor_escenario = EXCLUDED.peor_escenario,
    mediana_escenarios = EXCLUDED.mediana_escenarios,
    probabilidad_ganancia = EXCLUDED.probabilidad_ganancia,
    moneda = EXCLUDED.moneda,
    resumen = EXCLUDED.resumen,
    fecha_registro = CURRENT_TIMESTAMP;

/*
===============================================================================
10. EJECUCIÓN DE TRABAJO PROGRAMADO
===============================================================================
*/
INSERT INTO operation.ejecuciones_trabajo
(
    trabajo_id,
    estado,
    numero_intento,
    disparador,
    identificador_proceso,
    fecha_solicitud,
    fecha_inicio,
    fecha_fin,
    progreso,
    registros_procesados,
    registros_exitosos,
    registros_fallidos,
    resultado
)
SELECT
    tp.id,
    'COMPLETADA',
    1,
    'MANUAL',
    'TEST_JOB_PRECIOS_001',
    CURRENT_TIMESTAMP - INTERVAL '90 seconds',
    CURRENT_TIMESTAMP - INTERVAL '80 seconds',
    CURRENT_TIMESTAMP - INTERVAL '5 seconds',
    100.0000,
    25,
    25,
    0,
    '{"entorno":"TEST","origen":"21_test_data.sql","mensaje":"Carga de precios de prueba completada"}'::JSONB
FROM operation.trabajos_programados tp
WHERE tp.codigo = 'ACTUALIZAR_PRECIOS_DIARIOS'
ON CONFLICT (identificador_proceso)
DO UPDATE SET
    trabajo_id = EXCLUDED.trabajo_id,
    estado = EXCLUDED.estado,
    numero_intento = EXCLUDED.numero_intento,
    disparador = EXCLUDED.disparador,
    fecha_solicitud = EXCLUDED.fecha_solicitud,
    fecha_inicio = EXCLUDED.fecha_inicio,
    fecha_fin = EXCLUDED.fecha_fin,
    progreso = EXCLUDED.progreso,
    registros_procesados = EXCLUDED.registros_procesados,
    registros_exitosos = EXCLUDED.registros_exitosos,
    registros_fallidos = EXCLUDED.registros_fallidos,
    resultado = EXCLUDED.resultado,
    mensaje_error = NULL;

/*
===============================================================================
11. ACTUALIZACIÓN DE VISTAS MATERIALIZADAS
===============================================================================
No se utiliza CONCURRENTLY dentro de la transacción.
*/
REFRESH MATERIALIZED VIEW market.mv_resumen_diario_activos;
REFRESH MATERIALIZED VIEW portfolio.mv_ultima_valoracion_portafolio;
REFRESH MATERIALIZED VIEW simulation.mv_estadisticas_simulacion;
REFRESH MATERIALIZED VIEW operation.mv_metricas_trabajos;

COMMIT;

/*
===============================================================================
VALIDACIÓN
===============================================================================

SELECT correo, estado, roles
FROM auth.v_usuarios_roles
WHERE correo LIKE '%@example.test'
ORDER BY correo;

SELECT simbolo, fecha_precio, cierre
FROM market.v_ultimos_precios
WHERE simbolo IN ('AAPL', 'MSFT', 'NVDA', 'SPY', 'QQQ')
ORDER BY simbolo;

SELECT *
FROM portfolio.v_resumen_portafolios
WHERE portafolio_nombre LIKE 'TEST_%'
ORDER BY portafolio_nombre;

SELECT *
FROM simulation.v_resumen_ejecuciones
WHERE identificador_proceso = 'TEST_SIM_SPY_001';

SELECT *
FROM operation.v_estado_trabajos_programados
WHERE codigo = 'ACTUALIZAR_PRECIOS_DIARIOS';

===============================================================================
LIMPIEZA DE DATOS DE PRUEBA
===============================================================================
Ejecutar solamente cuando se deseen eliminar los datos creados por este archivo.
El orden respeta las relaciones de llave foránea.

BEGIN;

DELETE FROM simulation.resultados
WHERE ejecucion_id IN
(
    SELECT id
    FROM simulation.ejecuciones
    WHERE identificador_proceso = 'TEST_SIM_SPY_001'
);

DELETE FROM simulation.ejecuciones
WHERE identificador_proceso = 'TEST_SIM_SPY_001';

DELETE FROM simulation.configuracion_activos
WHERE configuracion_id IN
(
    SELECT id
    FROM simulation.configuraciones
    WHERE nombre = 'TEST_Backtest_SPY_1A'
);

DELETE FROM simulation.configuraciones
WHERE nombre = 'TEST_Backtest_SPY_1A';

DELETE FROM operation.ejecuciones_trabajo
WHERE identificador_proceso = 'TEST_JOB_PRECIOS_001';

DELETE FROM portfolio.valoraciones_portafolio
WHERE portafolio_id IN
(
    SELECT id
    FROM portfolio.portafolios
    WHERE nombre LIKE 'TEST\_%' ESCAPE '\'
);

DELETE FROM portfolio.posiciones
WHERE portafolio_id IN
(
    SELECT id
    FROM portfolio.portafolios
    WHERE nombre LIKE 'TEST\_%' ESCAPE '\'
);

DELETE FROM portfolio.portafolios
WHERE nombre LIKE 'TEST\_%' ESCAPE '\';

DELETE FROM market.precios_historicos
WHERE fuente_id =
(
    SELECT id
    FROM market.fuentes_financieras
    WHERE nombre = 'Carga Manual'
)
AND activo_id IN
(
    SELECT id
    FROM market.activos
    WHERE simbolo IN ('AAPL', 'MSFT', 'NVDA', 'SPY', 'QQQ')
)
AND fecha BETWEEN CURRENT_DATE - 4 AND CURRENT_DATE;

DELETE FROM auth.usuario_roles
WHERE usuario_id IN
(
    SELECT id
    FROM auth.usuarios
    WHERE correo LIKE '%@example.test'
);

DELETE FROM auth.usuarios
WHERE correo LIKE '%@example.test';

REFRESH MATERIALIZED VIEW market.mv_resumen_diario_activos;
REFRESH MATERIALIZED VIEW portfolio.mv_ultima_valoracion_portafolio;
REFRESH MATERIALIZED VIEW simulation.mv_estadisticas_simulacion;
REFRESH MATERIALIZED VIEW operation.mv_metricas_trabajos;

COMMIT;

===============================================================================
*/