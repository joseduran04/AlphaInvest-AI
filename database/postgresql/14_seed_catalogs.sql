/*
============================================================
 AlphaInvest AI
 Script: 14_seed_catalogs.sql

 Propósito:
 Cargar los catálogos y configuraciones base del sistema de
 forma transaccional, idempotente y compatible con PostgreSQL.

 Reconstruido exclusivamente a partir de:
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql
 - 06_market_tables.sql
 - 10_audit_operation_tables.sql

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql
 - 06_market_tables.sql
 - 10_audit_operation_tables.sql

 Notas:
 - No se insertan usuarios, sesiones ni aceptaciones de términos.
 - No se insertan versiones de modelos, activos, precios, indicadores
   ni noticias.
 - No se insertan registros de auditoría, errores, notificaciones,
   ejecuciones de trabajos ni bloqueos de procesos.
 - La idempotencia se apoya exclusivamente en restricciones UNIQUE
   existentes en las tablas reales.
============================================================
*/

BEGIN;

/*
============================================================
 1. ROLES
 Clave natural real: auth.roles.nombre
============================================================
*/

INSERT INTO auth.roles
(
    nombre,
    descripcion,
    activo
)
VALUES
    (
        'ADMINISTRADOR',
        'Acceso administrativo completo a la configuración, seguridad, operación y supervisión del sistema.',
        TRUE
    ),
    (
        'ANALISTA',
        'Consulta información financiera, ejecuta análisis y revisa resultados generados por modelos de IA.',
        TRUE
    ),
    (
        'INVERSIONISTA',
        'Usuario final que consulta mercados, activos, análisis, predicciones y notificaciones propias.',
        TRUE
    ),
    (
        'OPERADOR',
        'Supervisa procesos automáticos, fuentes financieras, trabajos programados y eventos operativos.',
        TRUE
    ),
    (
        'AUDITOR',
        'Consulta registros de auditoría, eventos de seguridad y errores sin modificar la operación.',
        TRUE
    )
ON CONFLICT (nombre)
DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    activo = EXCLUDED.activo;


/*
============================================================
 2. PERMISOS
 Clave natural real: auth.permisos.codigo
============================================================
*/

INSERT INTO auth.permisos
(
    codigo,
    nombre,
    descripcion,
    modulo,
    activo
)
VALUES
    -- Usuarios y autorización
    ('usuarios.leer', 'Consultar usuarios', 'Permite consultar usuarios registrados y su estado.', 'AUTH', TRUE),
    ('usuarios.crear', 'Crear usuarios', 'Permite registrar usuarios desde funciones administrativas.', 'AUTH', TRUE),
    ('usuarios.actualizar', 'Actualizar usuarios', 'Permite modificar información y estado de usuarios.', 'AUTH', TRUE),
    ('usuarios.bloquear', 'Bloquear usuarios', 'Permite bloquear o desbloquear cuentas de usuario.', 'AUTH', TRUE),
    ('roles.leer', 'Consultar roles', 'Permite consultar el catálogo de roles.', 'AUTH', TRUE),
    ('roles.administrar', 'Administrar roles', 'Permite crear, actualizar y activar o desactivar roles.', 'AUTH', TRUE),
    ('permisos.leer', 'Consultar permisos', 'Permite consultar el catálogo de permisos.', 'AUTH', TRUE),
    ('permisos.administrar', 'Administrar permisos', 'Permite crear, actualizar y activar o desactivar permisos.', 'AUTH', TRUE),
    ('roles.asignar', 'Asignar roles', 'Permite asignar o retirar roles a usuarios.', 'AUTH', TRUE),
    ('permisos.asignar', 'Asignar permisos', 'Permite asociar o retirar permisos de los roles.', 'AUTH', TRUE),
    ('sesiones.leer', 'Consultar sesiones', 'Permite consultar sesiones activas de usuarios.', 'AUTH', TRUE),
    ('sesiones.revocar', 'Revocar sesiones', 'Permite invalidar sesiones activas.', 'AUTH', TRUE),

    -- Inteligencia artificial
    ('modelos.leer', 'Consultar modelos de IA', 'Permite consultar modelos y sus datos generales.', 'AI', TRUE),
    ('modelos.administrar', 'Administrar modelos de IA', 'Permite registrar, actualizar y cambiar el estado de modelos.', 'AI', TRUE),
    ('versiones_modelo.leer', 'Consultar versiones de modelos', 'Permite consultar versiones, métricas y artefactos registrados.', 'AI', TRUE),
    ('versiones_modelo.administrar', 'Administrar versiones de modelos', 'Permite registrar y actualizar versiones de modelos.', 'AI', TRUE),
    ('versiones_modelo.activar', 'Activar versiones de modelos', 'Permite activar o desactivar versiones de modelos de IA.', 'AI', TRUE),

    -- Mercado
    ('mercados.leer', 'Consultar mercados', 'Permite consultar el catálogo de mercados.', 'MARKET', TRUE),
    ('mercados.administrar', 'Administrar mercados', 'Permite crear y actualizar mercados.', 'MARKET', TRUE),
    ('tipos_activo.leer', 'Consultar tipos de activo', 'Permite consultar las clases de instrumentos financieros.', 'MARKET', TRUE),
    ('tipos_activo.administrar', 'Administrar tipos de activo', 'Permite crear y actualizar tipos de activo.', 'MARKET', TRUE),
    ('activos.leer', 'Consultar activos', 'Permite consultar instrumentos financieros.', 'MARKET', TRUE),
    ('activos.administrar', 'Administrar activos', 'Permite registrar y actualizar activos financieros.', 'MARKET', TRUE),
    ('precios.leer', 'Consultar precios históricos', 'Permite consultar series históricas de precios.', 'MARKET', TRUE),
    ('precios.cargar', 'Cargar precios históricos', 'Permite insertar o actualizar datos históricos de mercado.', 'MARKET', TRUE),
    ('indicadores.leer', 'Consultar indicadores financieros', 'Permite consultar indicadores calculados.', 'MARKET', TRUE),
    ('indicadores.calcular', 'Calcular indicadores financieros', 'Permite ejecutar el cálculo y registro de indicadores.', 'MARKET', TRUE),
    ('noticias.leer', 'Consultar noticias financieras', 'Permite consultar referencias de noticias asociadas a activos.', 'MARKET', TRUE),
    ('noticias.cargar', 'Cargar noticias financieras', 'Permite registrar referencias de noticias financieras.', 'MARKET', TRUE),
    ('fuentes.leer', 'Consultar fuentes financieras', 'Permite consultar proveedores de datos financieros.', 'MARKET', TRUE),
    ('fuentes.administrar', 'Administrar fuentes financieras', 'Permite configurar proveedores y prioridades de consulta.', 'MARKET', TRUE),

    -- Auditoría y seguridad
    ('auditoria.leer', 'Consultar auditoría', 'Permite consultar registros de auditoría.', 'AUDIT', TRUE),
    ('seguridad.leer', 'Consultar eventos de seguridad', 'Permite consultar eventos de seguridad.', 'AUDIT', TRUE),
    ('seguridad.revisar', 'Revisar eventos de seguridad', 'Permite marcar eventos de seguridad como revisados.', 'AUDIT', TRUE),
    ('errores.leer', 'Consultar errores de aplicación', 'Permite consultar errores registrados por los servicios.', 'AUDIT', TRUE),
    ('errores.resolver', 'Resolver errores de aplicación', 'Permite marcar errores como resueltos y documentar su solución.', 'AUDIT', TRUE),

    -- Operación
    ('notificaciones.leer', 'Consultar notificaciones', 'Permite consultar notificaciones propias o administrativas.', 'OPERATION', TRUE),
    ('notificaciones.administrar', 'Administrar notificaciones', 'Permite crear, programar y actualizar notificaciones.', 'OPERATION', TRUE),
    ('trabajos.leer', 'Consultar trabajos programados', 'Permite consultar la configuración de trabajos.', 'OPERATION', TRUE),
    ('trabajos.administrar', 'Administrar trabajos programados', 'Permite crear y modificar trabajos programados.', 'OPERATION', TRUE),
    ('trabajos.ejecutar', 'Ejecutar trabajos', 'Permite solicitar ejecuciones manuales de trabajos.', 'OPERATION', TRUE),
    ('ejecuciones.leer', 'Consultar ejecuciones', 'Permite consultar ejecuciones y sus resultados.', 'OPERATION', TRUE),
    ('procesos.leer', 'Consultar control de procesos', 'Permite consultar bloqueos y procesos en ejecución.', 'OPERATION', TRUE),
    ('procesos.administrar', 'Administrar control de procesos', 'Permite liberar o gestionar controles operativos de procesos.', 'OPERATION', TRUE)
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    modulo = EXCLUDED.modulo,
    activo = EXCLUDED.activo;


/*
============================================================
 3. ASIGNACIÓN DE PERMISOS A ROLES
 Clave real: (rol_id, permiso_id)
============================================================
*/

-- ADMINISTRADOR: todos los permisos activos.
INSERT INTO auth.rol_permisos
(
    rol_id,
    permiso_id
)
SELECT
    r.id,
    p.id
FROM auth.roles AS r
CROSS JOIN auth.permisos AS p
WHERE r.nombre = 'ADMINISTRADOR'
  AND r.activo = TRUE
  AND p.activo = TRUE
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;

-- ANALISTA: consulta y análisis de información financiera y de IA.
INSERT INTO auth.rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM auth.roles AS r
JOIN auth.permisos AS p
  ON p.codigo IN
  (
      'modelos.leer',
      'versiones_modelo.leer',
      'mercados.leer',
      'tipos_activo.leer',
      'activos.leer',
      'precios.leer',
      'indicadores.leer',
      'indicadores.calcular',
      'noticias.leer',
      'fuentes.leer',
      'trabajos.leer',
      'trabajos.ejecutar',
      'ejecuciones.leer'
  )
WHERE r.nombre = 'ANALISTA'
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;

-- INVERSIONISTA: acceso de consulta a información funcional.
INSERT INTO auth.rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM auth.roles AS r
JOIN auth.permisos AS p
  ON p.codigo IN
  (
      'modelos.leer',
      'mercados.leer',
      'tipos_activo.leer',
      'activos.leer',
      'precios.leer',
      'indicadores.leer',
      'noticias.leer',
      'notificaciones.leer'
  )
WHERE r.nombre = 'INVERSIONISTA'
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;

-- OPERADOR: administración de fuentes, cargas y procesos automáticos.
INSERT INTO auth.rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM auth.roles AS r
JOIN auth.permisos AS p
  ON p.codigo IN
  (
      'mercados.leer',
      'tipos_activo.leer',
      'activos.leer',
      'activos.administrar',
      'precios.leer',
      'precios.cargar',
      'indicadores.leer',
      'indicadores.calcular',
      'noticias.leer',
      'noticias.cargar',
      'fuentes.leer',
      'fuentes.administrar',
      'errores.leer',
      'notificaciones.leer',
      'notificaciones.administrar',
      'trabajos.leer',
      'trabajos.administrar',
      'trabajos.ejecutar',
      'ejecuciones.leer',
      'procesos.leer',
      'procesos.administrar'
  )
WHERE r.nombre = 'OPERADOR'
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;

-- AUDITOR: acceso de lectura a seguridad, errores, procesos y configuración.
INSERT INTO auth.rol_permisos (rol_id, permiso_id)
SELECT r.id, p.id
FROM auth.roles AS r
JOIN auth.permisos AS p
  ON p.codigo IN
  (
      'usuarios.leer',
      'roles.leer',
      'permisos.leer',
      'sesiones.leer',
      'modelos.leer',
      'versiones_modelo.leer',
      'mercados.leer',
      'tipos_activo.leer',
      'activos.leer',
      'fuentes.leer',
      'auditoria.leer',
      'seguridad.leer',
      'seguridad.revisar',
      'errores.leer',
      'trabajos.leer',
      'ejecuciones.leer',
      'procesos.leer'
  )
WHERE r.nombre = 'AUDITOR'
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;


/*
============================================================
 4. MODELOS DE INTELIGENCIA ARTIFICIAL
 Clave natural real: ai.modelos_ia.codigo
============================================================
*/

INSERT INTO ai.modelos_ia
(
    codigo,
    nombre,
    tipo,
    objetivo,
    descripcion,
    estado
)
VALUES
    (
        'PREDICCION_TENDENCIA',
        'Predicción de tendencia de mercado',
        'CLASIFICACION',
        'Clasificar la tendencia esperada de un activo',
        'Modelo orientado a estimar si la tendencia esperada de un activo es alcista, bajista o lateral.',
        'DESARROLLO'
    ),
    (
        'PRONOSTICO_PRECIO',
        'Pronóstico de precio',
        'REGRESION',
        'Estimar valores futuros de precios financieros',
        'Modelo de regresión para estimar precios o rendimientos esperados a partir de datos históricos.',
        'DESARROLLO'
    ),
    (
        'ANALISIS_SENTIMIENTO',
        'Análisis de sentimiento financiero',
        'NLP',
        'Clasificar sentimiento en noticias financieras',
        'Modelo de procesamiento de lenguaje natural para clasificar sentimiento positivo, neutral o negativo.',
        'DESARROLLO'
    ),
    (
        'CLASIFICACION_RIESGO',
        'Clasificación de riesgo',
        'CLASIFICACION',
        'Clasificar el nivel de riesgo de un activo',
        'Modelo destinado a clasificar activos en niveles de riesgo con base en variables de mercado.',
        'DESARROLLO'
    ),
    (
        'DETECCION_ANOMALIAS',
        'Detección de anomalías de mercado',
        'ANOMALIAS',
        'Detectar comportamientos atípicos en series financieras',
        'Modelo para identificar movimientos, volúmenes o patrones inusuales en datos financieros.',
        'DESARROLLO'
    )
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    tipo = EXCLUDED.tipo,
    objetivo = EXCLUDED.objetivo,
    descripcion = EXCLUDED.descripcion,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 5. MERCADOS
 Clave natural real: market.mercados.codigo
============================================================
*/

INSERT INTO market.mercados
(
    codigo,
    nombre,
    pais,
    zona_horaria,
    moneda,
    activo
)
VALUES
    ('NASDAQ', 'Nasdaq Stock Market', 'Estados Unidos', 'America/New_York', 'USD', TRUE),
    ('NYSE', 'New York Stock Exchange', 'Estados Unidos', 'America/New_York', 'USD', TRUE),
    ('BMV', 'Bolsa Mexicana de Valores', 'México', 'America/Mexico_City', 'MXN', TRUE),
    ('BIVA', 'Bolsa Institucional de Valores', 'México', 'America/Mexico_City', 'MXN', TRUE),
    ('CRYPTO', 'Mercado global de criptoactivos', 'Global', 'UTC', 'USD', TRUE),
    ('FOREX', 'Mercado global de divisas', 'Global', 'UTC', 'USD', TRUE)
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    pais = EXCLUDED.pais,
    zona_horaria = EXCLUDED.zona_horaria,
    moneda = EXCLUDED.moneda,
    activo = EXCLUDED.activo,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 6. TIPOS DE ACTIVO
 Claves naturales reales:
 - market.tipos_activo.codigo
 - market.tipos_activo.nombre
============================================================
*/

INSERT INTO market.tipos_activo
(
    codigo,
    nombre,
    descripcion,
    activo
)
VALUES
    ('ACCION', 'Acción', 'Título representativo de una participación en una empresa.', TRUE),
    ('ETF', 'Fondo cotizado', 'Fondo de inversión negociado en un mercado bursátil.', TRUE),
    ('CRIPTO', 'Criptoactivo', 'Activo digital negociado mediante redes de registro distribuido.', TRUE),
    ('DIVISA', 'Divisa', 'Moneda negociada en el mercado internacional de cambios.', TRUE),
    ('INDICE', 'Índice bursátil', 'Indicador compuesto que representa el comportamiento de un conjunto de activos.', TRUE),
    ('BONO', 'Bono', 'Instrumento financiero de deuda emitido por una entidad pública o privada.', TRUE),
    ('FONDO', 'Fondo de inversión', 'Vehículo colectivo de inversión no necesariamente cotizado como ETF.', TRUE),
    ('MATERIA_PRIMA', 'Materia prima', 'Activo asociado a productos básicos o commodities.', TRUE)
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    activo = EXCLUDED.activo;


/*
============================================================
 7. FUENTES FINANCIERAS
 Clave natural real: market.fuentes_financieras.nombre
============================================================
*/

INSERT INTO market.fuentes_financieras
(
    nombre,
    proveedor,
    url_base,
    prioridad,
    activa,
    requiere_api_key,
    limite_consultas_minuto
)
VALUES
    ('Alpha Vantage', 'Alpha Vantage Inc.', 'https://www.alphavantage.co', 1, TRUE, TRUE, 5),
    ('Finnhub', 'Finnhub Stock API', 'https://finnhub.io', 2, TRUE, TRUE, 60),
    ('Twelve Data', 'Twelve Data Pte. Ltd.', 'https://twelvedata.com', 3, TRUE, TRUE, 8),
    ('CoinGecko', 'CoinGecko', 'https://www.coingecko.com', 4, TRUE, FALSE, 30),
    ('Yahoo Finance', 'Yahoo', 'https://finance.yahoo.com', 5, TRUE, FALSE, NULL),
    ('Carga Manual', 'AlphaInvest AI', NULL, 100, TRUE, FALSE, NULL)
ON CONFLICT (nombre)
DO UPDATE SET
    proveedor = EXCLUDED.proveedor,
    url_base = EXCLUDED.url_base,
    prioridad = EXCLUDED.prioridad,
    activa = EXCLUDED.activa,
    requiere_api_key = EXCLUDED.requiere_api_key,
    limite_consultas_minuto = EXCLUDED.limite_consultas_minuto,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 8. TRABAJOS PROGRAMADOS
 Clave natural real: operation.trabajos_programados.codigo
============================================================
*/

INSERT INTO operation.trabajos_programados
(
    codigo,
    nombre,
    descripcion,
    tipo,
    expresion_cron,
    intervalo_segundos,
    zona_horaria,
    parametros,
    activo,
    permite_concurrencia,
    tiempo_maximo_segundos,
    maximo_reintentos
)
VALUES
    (
        'ACTUALIZAR_PRECIOS_DIARIOS',
        'Actualizar precios diarios',
        'Obtiene y registra precios diarios de los activos configurados.',
        'CRON',
        '0 23 * * 1-5',
        NULL,
        'America/Mexico_City',
        '{"alcance":"activos_activos","frecuencia":"diaria"}'::JSONB,
        TRUE,
        FALSE,
        3600,
        3
    ),
    (
        'CALCULAR_INDICADORES_DIARIOS',
        'Calcular indicadores diarios',
        'Calcula indicadores financieros después de la actualización de precios.',
        'CRON',
        '30 23 * * 1-5',
        NULL,
        'America/Mexico_City',
        '{"frecuencia":"diaria"}'::JSONB,
        TRUE,
        FALSE,
        3600,
        3
    ),
    (
        'SINCRONIZAR_NOTICIAS',
        'Sincronizar noticias financieras',
        'Registra referencias de noticias financieras obtenidas por los servicios de integración.',
        'INTERVALO',
        NULL,
        1800,
        'UTC',
        '{"ventana_minutos":30}'::JSONB,
        TRUE,
        FALSE,
        1200,
        3
    ),
    (
        'LIMPIAR_SESIONES_EXPIRADAS',
        'Limpiar sesiones expiradas',
        'Revoca o depura sesiones que han superado su fecha de expiración.',
        'CRON',
        '0 * * * *',
        NULL,
        'UTC',
        '{}'::JSONB,
        TRUE,
        FALSE,
        600,
        2
    ),
    (
        'DEPURAR_CONTROL_PROCESOS',
        'Depurar controles de procesos',
        'Libera controles operativos vencidos y conserva la consistencia de los bloqueos.',
        'INTERVALO',
        NULL,
        300,
        'UTC',
        '{"solo_vencidos":true}'::JSONB,
        TRUE,
        FALSE,
        300,
        2
    ),
    (
        'REENTRENAR_MODELOS',
        'Reentrenar modelos de IA',
        'Trabajo manual para solicitar el reentrenamiento controlado de modelos.',
        'MANUAL',
        NULL,
        NULL,
        'UTC',
        '{}'::JSONB,
        TRUE,
        FALSE,
        14400,
        1
    )
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    tipo = EXCLUDED.tipo,
    expresion_cron = EXCLUDED.expresion_cron,
    intervalo_segundos = EXCLUDED.intervalo_segundos,
    zona_horaria = EXCLUDED.zona_horaria,
    parametros = EXCLUDED.parametros,
    activo = EXCLUDED.activo,
    permite_concurrencia = EXCLUDED.permite_concurrencia,
    tiempo_maximo_segundos = EXCLUDED.tiempo_maximo_segundos,
    maximo_reintentos = EXCLUDED.maximo_reintentos,
    fecha_actualizacion = CURRENT_TIMESTAMP;

COMMIT;