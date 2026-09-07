/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : 22_documentation.sql
Motor   : PostgreSQL
Objetivo: Documentar, diagnosticar y verificar la instalación completa de la
          base de datos mediante consultas basadas en el catálogo del sistema.

Dependencias:
- Partes 00 a 21 ejecutadas.
- Permisos de lectura sobre information_schema y pg_catalog.
- Para algunos diagnósticos administrativos se recomienda ejecutar con el rol
  propietario de la base de datos.

IMPORTANTE:
- Este archivo no altera datos funcionales.
- Las vistas creadas pertenecen al esquema operation.
- Las consultas finales sirven como checklist técnico de instalación.
===============================================================================
*/

BEGIN;

/*
===============================================================================
1. TABLA DE VERSIONES DEL ESQUEMA
===============================================================================
Registra las versiones instaladas del modelo de base de datos.
*/
CREATE TABLE IF NOT EXISTS operation.versiones_esquema
(
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version             VARCHAR(30) NOT NULL,
    descripcion         TEXT NOT NULL,
    archivo_origen      VARCHAR(150) NOT NULL,
    checksum_referencia VARCHAR(128),
    aplicada_por        VARCHAR(150) NOT NULL DEFAULT CURRENT_USER,
    aplicada_en         TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadatos           JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT uq_versiones_esquema_version
        UNIQUE (version),

    CONSTRAINT ck_versiones_esquema_version_no_vacia
        CHECK (NULLIF(BTRIM(version), '') IS NOT NULL),

    CONSTRAINT ck_versiones_esquema_archivo_no_vacio
        CHECK (NULLIF(BTRIM(archivo_origen), '') IS NOT NULL),

    CONSTRAINT ck_versiones_esquema_metadatos_objeto
        CHECK (jsonb_typeof(metadatos) = 'object')
);

COMMENT ON TABLE operation.versiones_esquema IS
'Historial técnico de versiones instaladas del esquema AlphaInvest AI.';

COMMENT ON COLUMN operation.versiones_esquema.version IS
'Identificador lógico de la versión del modelo de datos.';

COMMENT ON COLUMN operation.versiones_esquema.archivo_origen IS
'Script responsable de registrar la versión.';

COMMENT ON COLUMN operation.versiones_esquema.checksum_referencia IS
'Checksum opcional calculado externamente para validar integridad del entregable.';

INSERT INTO operation.versiones_esquema
(
    version,
    descripcion,
    archivo_origen,
    metadatos
)
VALUES
(
    '1.0.0',
    'Instalación modular inicial de AlphaInvest AI, partes 00 a 22.',
    '22_documentation.sql',
    jsonb_build_object
    (
        'motor', 'PostgreSQL',
        'modulos',
        jsonb_build_array
        (
            'app_auth',
            'profile',
            'ai',
            'market',
            'portfolio',
            'simulation',
            'audit',
            'operation',
            'reporting'
        ),
        'ultima_parte', 22
    )
)
ON CONFLICT (version)
DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    archivo_origen = EXCLUDED.archivo_origen,
    aplicada_por = CURRENT_USER,
    aplicada_en = CURRENT_TIMESTAMP,
    metadatos = EXCLUDED.metadatos;

/*
===============================================================================
2. ÍNDICES DE DOCUMENTACIÓN
===============================================================================
*/
CREATE INDEX IF NOT EXISTS idx_versiones_esquema_aplicada_en
    ON operation.versiones_esquema (aplicada_en DESC);

CREATE INDEX IF NOT EXISTS idx_versiones_esquema_archivo
    ON operation.versiones_esquema (archivo_origen);

/*
===============================================================================
3. VISTA: INVENTARIO DE ESQUEMAS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_esquemas AS
SELECT
    n.nspname AS esquema,
    pg_get_userbyid(n.nspowner) AS propietario,
    COUNT(DISTINCT c.oid)
        FILTER (WHERE c.relkind IN ('r', 'p')) AS tablas,
    COUNT(DISTINCT c.oid)
        FILTER (WHERE c.relkind = 'v') AS vistas,
    COUNT(DISTINCT c.oid)
        FILTER (WHERE c.relkind = 'm') AS vistas_materializadas,
    COUNT(DISTINCT p.oid) AS funciones_procedimientos,
    obj_description(n.oid, 'pg_namespace') AS comentario
FROM pg_namespace n
LEFT JOIN pg_class c
    ON c.relnamespace = n.oid
LEFT JOIN pg_proc p
    ON p.pronamespace = n.oid
WHERE n.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
GROUP BY
    n.oid,
    n.nspname,
    n.nspowner;

/*
===============================================================================
4. VISTA: INVENTARIO DE TABLAS Y VISTAS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_objetos AS
SELECT
    n.nspname AS esquema,
    c.relname AS objeto,
    CASE c.relkind
        WHEN 'r' THEN 'TABLA'
        WHEN 'p' THEN 'TABLA PARTICIONADA'
        WHEN 'v' THEN 'VISTA'
        WHEN 'm' THEN 'VISTA MATERIALIZADA'
        WHEN 'S' THEN 'SECUENCIA'
        WHEN 'f' THEN 'TABLA EXTERNA'
        ELSE c.relkind::TEXT
    END AS tipo_objeto,
    pg_get_userbyid(c.relowner) AS propietario,
    CASE
        WHEN c.relkind IN ('r', 'p', 'm') THEN
            pg_size_pretty(pg_total_relation_size(c.oid))
        ELSE NULL
    END AS tamano_total,
    obj_description(c.oid, 'pg_class') AS comentario
FROM pg_class c
JOIN pg_namespace n
    ON n.oid = c.relnamespace
WHERE n.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
AND c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f');

/*
===============================================================================
5. VISTA: DICCIONARIO DE COLUMNAS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_diccionario_columnas AS
SELECT
    c.table_schema AS esquema,
    c.table_name AS tabla,
    c.ordinal_position AS posicion,
    c.column_name AS columna,
    c.data_type AS tipo_dato,
    c.udt_name AS tipo_interno,
    c.character_maximum_length AS longitud_maxima,
    c.numeric_precision AS precision_numerica,
    c.numeric_scale AS escala_numerica,
    c.is_nullable = 'YES' AS permite_nulos,
    c.column_default AS valor_predeterminado,
    pgd.description AS comentario
FROM information_schema.columns c
LEFT JOIN pg_catalog.pg_statio_all_tables st
    ON st.schemaname = c.table_schema
   AND st.relname = c.table_name
LEFT JOIN pg_catalog.pg_description pgd
    ON pgd.objoid = st.relid
   AND pgd.objsubid = c.ordinal_position
WHERE c.table_schema IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
6. VISTA: LLAVES PRIMARIAS, ÚNICAS Y FORÁNEAS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_restricciones AS
SELECT
    tc.constraint_schema AS esquema,
    tc.table_name AS tabla,
    tc.constraint_name AS restriccion,
    tc.constraint_type AS tipo,
    STRING_AGG(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columnas,
    ccu.table_schema AS esquema_referenciado,
    ccu.table_name AS tabla_referenciada,
    ccu.column_name AS columna_referenciada
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
    ON kcu.constraint_schema = tc.constraint_schema
   AND kcu.constraint_name = tc.constraint_name
   AND kcu.table_name = tc.table_name
LEFT JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_schema = tc.constraint_schema
   AND ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_schema IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
GROUP BY
    tc.constraint_schema,
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    ccu.table_schema,
    ccu.table_name,
    ccu.column_name;

/*
===============================================================================
7. VISTA: ÍNDICES
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_indices AS
SELECT
    schemaname AS esquema,
    tablename AS tabla,
    indexname AS indice,
    indexdef AS definicion
FROM pg_indexes
WHERE schemaname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
8. VISTA: FUNCIONES Y PROCEDIMIENTOS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_rutinas AS
SELECT
    n.nspname AS esquema,
    p.proname AS rutina,
    pg_get_function_identity_arguments(p.oid) AS argumentos,
    pg_get_function_result(p.oid) AS resultado,
    CASE p.prokind
        WHEN 'f' THEN 'FUNCION'
        WHEN 'p' THEN 'PROCEDIMIENTO'
        WHEN 'a' THEN 'AGREGADO'
        WHEN 'w' THEN 'VENTANA'
        ELSE p.prokind::TEXT
    END AS tipo,
    l.lanname AS lenguaje,
    p.prosecdef AS security_definer,
    p.provolatile AS volatilidad,
    obj_description(p.oid, 'pg_proc') AS comentario
FROM pg_proc p
JOIN pg_namespace n
    ON n.oid = p.pronamespace
JOIN pg_language l
    ON l.oid = p.prolang
WHERE n.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
9. VISTA: TRIGGERS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_triggers AS
SELECT
    n.nspname AS esquema,
    c.relname AS tabla,
    t.tgname AS trigger,
    p.proname AS funcion,
    t.tgenabled AS estado_interno,
    pg_get_triggerdef(t.oid, TRUE) AS definicion
FROM pg_trigger t
JOIN pg_class c
    ON c.oid = t.tgrelid
JOIN pg_namespace n
    ON n.oid = c.relnamespace
JOIN pg_proc p
    ON p.oid = t.tgfoid
WHERE NOT t.tgisinternal
AND n.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
10. VISTA: DEPENDENCIAS ENTRE OBJETOS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_dependencias AS
SELECT DISTINCT
    origen_ns.nspname AS esquema_origen,
    origen.relname AS objeto_origen,
    CASE origen.relkind
        WHEN 'v' THEN 'VISTA'
        WHEN 'm' THEN 'VISTA MATERIALIZADA'
        WHEN 'r' THEN 'TABLA'
        WHEN 'p' THEN 'TABLA PARTICIONADA'
        ELSE origen.relkind::TEXT
    END AS tipo_origen,
    destino_ns.nspname AS esquema_destino,
    destino.relname AS objeto_destino,
    CASE destino.relkind
        WHEN 'v' THEN 'VISTA'
        WHEN 'm' THEN 'VISTA MATERIALIZADA'
        WHEN 'r' THEN 'TABLA'
        WHEN 'p' THEN 'TABLA PARTICIONADA'
        ELSE destino.relkind::TEXT
    END AS tipo_destino
FROM pg_depend d
JOIN pg_rewrite rw
    ON rw.oid = d.objid
JOIN pg_class origen
    ON origen.oid = rw.ev_class
JOIN pg_namespace origen_ns
    ON origen_ns.oid = origen.relnamespace
JOIN pg_class destino
    ON destino.oid = d.refobjid
JOIN pg_namespace destino_ns
    ON destino_ns.oid = destino.relnamespace
WHERE origen_ns.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
AND destino_ns.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
AND origen.oid <> destino.oid;

/*
===============================================================================
11. VISTA: PERMISOS
===============================================================================
*/
CREATE OR REPLACE VIEW operation.v_documentacion_permisos AS
SELECT
    grantee AS rol,
    table_schema AS esquema,
    table_name AS objeto,
    privilege_type AS permiso,
    is_grantable = 'YES' AS puede_delegar
FROM information_schema.role_table_grants
WHERE table_schema IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
12. VISTA: RESUMEN DE FILAS ESTIMADAS
===============================================================================
Las cantidades son estimaciones del planificador. Para actualizarlas:
ANALYZE;
*/
CREATE OR REPLACE VIEW operation.v_documentacion_filas_estimadas AS
SELECT
    n.nspname AS esquema,
    c.relname AS tabla,
    c.reltuples::BIGINT AS filas_estimadas,
    pg_size_pretty(pg_relation_size(c.oid)) AS tamano_datos,
    pg_size_pretty(pg_indexes_size(c.oid)) AS tamano_indices,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS tamano_total
FROM pg_class c
JOIN pg_namespace n
    ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'p')
AND n.nspname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
);

/*
===============================================================================
13. FUNCIÓN: VERIFICACIÓN GENERAL DE INSTALACIÓN
===============================================================================
Devuelve una fila por comprobación y no detiene la ejecución.
*/
CREATE OR REPLACE FUNCTION operation.fn_verificar_instalacion()
RETURNS TABLE
(
    categoria       TEXT,
    comprobacion    TEXT,
    estado          TEXT,
    detalle         TEXT
)
LANGUAGE plpgsql
STABLE
AS
$$
DECLARE
    v_esquemas_esperados INTEGER := 9;
    v_esquemas_actuales INTEGER;
    v_tablas INTEGER;
    v_vistas INTEGER;
    v_materializadas INTEGER;
    v_funciones INTEGER;
    v_triggers INTEGER;
    v_version TEXT;
BEGIN
    SELECT COUNT(*)
    INTO v_esquemas_actuales
    FROM pg_namespace
    WHERE nspname IN
    (
        'app_auth',
        'profile',
        'ai',
        'market',
        'portfolio',
        'simulation',
        'audit',
        'operation',
        'reporting'
    );

    RETURN QUERY
    SELECT
        'ESTRUCTURA',
        'Esquemas funcionales',
        CASE
            WHEN v_esquemas_actuales = v_esquemas_esperados
                THEN 'OK'
            ELSE 'REVISAR'
        END,
        FORMAT(
            'Esperados: %s. Encontrados: %s.',
            v_esquemas_esperados,
            v_esquemas_actuales
        );

    SELECT COUNT(*)
    INTO v_tablas
    FROM pg_class c
    JOIN pg_namespace n
        ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r', 'p')
      AND n.nspname IN
      (
          'app_auth',
          'profile',
          'ai',
          'market',
          'portfolio',
          'simulation',
          'audit',
          'operation',
          'reporting'
      );

    RETURN QUERY
    SELECT
        'ESTRUCTURA',
        'Tablas instaladas',
        CASE WHEN v_tablas > 0 THEN 'OK' ELSE 'ERROR' END,
        FORMAT('Total encontrado: %s.', v_tablas);

    SELECT COUNT(*)
    INTO v_vistas
    FROM pg_class c
    JOIN pg_namespace n
        ON n.oid = c.relnamespace
    WHERE c.relkind = 'v'
      AND n.nspname IN
      (
          'app_auth',
          'profile',
          'ai',
          'market',
          'portfolio',
          'simulation',
          'audit',
          'operation',
          'reporting'
      );

    RETURN QUERY
    SELECT
        'CONSULTA',
        'Vistas instaladas',
        CASE WHEN v_vistas > 0 THEN 'OK' ELSE 'REVISAR' END,
        FORMAT('Total encontrado: %s.', v_vistas);

    SELECT COUNT(*)
    INTO v_materializadas
    FROM pg_class c
    JOIN pg_namespace n
        ON n.oid = c.relnamespace
    WHERE c.relkind = 'm'
      AND n.nspname IN
      (
          'app_auth',
          'profile',
          'ai',
          'market',
          'portfolio',
          'simulation',
          'audit',
          'operation',
          'reporting'
      );

    RETURN QUERY
    SELECT
        'RENDIMIENTO',
        'Vistas materializadas',
        CASE WHEN v_materializadas > 0 THEN 'OK' ELSE 'REVISAR' END,
        FORMAT('Total encontrado: %s.', v_materializadas);

    SELECT COUNT(*)
    INTO v_funciones
    FROM pg_proc p
    JOIN pg_namespace n
        ON n.oid = p.pronamespace
    WHERE n.nspname IN
    (
        'app_auth',
        'profile',
        'ai',
        'market',
        'portfolio',
        'simulation',
        'audit',
        'operation',
        'reporting'
    );

    RETURN QUERY
    SELECT
        'LOGICA',
        'Funciones y procedimientos',
        CASE WHEN v_funciones > 0 THEN 'OK' ELSE 'REVISAR' END,
        FORMAT('Total encontrado: %s.', v_funciones);

    SELECT COUNT(*)
    INTO v_triggers
    FROM pg_trigger t
    JOIN pg_class c
        ON c.oid = t.tgrelid
    JOIN pg_namespace n
        ON n.oid = c.relnamespace
    WHERE NOT t.tgisinternal
      AND n.nspname IN
      (
          'app_auth',
          'profile',
          'ai',
          'market',
          'portfolio',
          'simulation',
          'audit',
          'operation',
          'reporting'
      );

    RETURN QUERY
    SELECT
        'LOGICA',
        'Triggers funcionales',
        CASE WHEN v_triggers > 0 THEN 'OK' ELSE 'REVISAR' END,
        FORMAT('Total encontrado: %s.', v_triggers);

    SELECT MAX(version)
    INTO v_version
    FROM operation.versiones_esquema;

    RETURN QUERY
    SELECT
        'VERSION',
        'Versión del esquema',
        CASE WHEN v_version IS NOT NULL THEN 'OK' ELSE 'ERROR' END,
        COALESCE(
            FORMAT('Versión registrada: %s.', v_version),
            'No existe una versión registrada.'
        );

    RETURN QUERY
    SELECT
        'EXTENSION',
        'pgcrypto',
        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM pg_extension
                WHERE extname = 'pgcrypto'
            )
            THEN 'OK'
            ELSE 'ERROR'
        END,
        CASE
            WHEN EXISTS
            (
                SELECT 1
                FROM pg_extension
                WHERE extname = 'pgcrypto'
            )
            THEN 'La extensión pgcrypto está instalada.'
            ELSE 'Falta pgcrypto; UUID y hashing pueden fallar.'
        END;
END;
$$;

COMMENT ON FUNCTION operation.fn_verificar_instalacion() IS
'Ejecuta comprobaciones generales de instalación sin modificar información.';

/*
===============================================================================
14. FUNCIÓN: DETECTAR LLAVES FORÁNEAS SIN ÍNDICE INICIAL
===============================================================================
La función identifica FK cuyo primer conjunto de columnas no coincide con el
inicio de algún índice. Es una ayuda diagnóstica, no una regla absoluta.
*/
CREATE OR REPLACE FUNCTION operation.fn_fk_sin_indice()
RETURNS TABLE
(
    esquema            TEXT,
    tabla              TEXT,
    restriccion        TEXT,
    columnas_fk        TEXT,
    recomendacion      TEXT
)
LANGUAGE sql
STABLE
AS
$$
WITH foreign_keys AS
(
    SELECT
        con.oid AS constraint_oid,
        ns.nspname AS esquema,
        tbl.relname AS tabla,
        con.conname AS restriccion,
        con.conrelid,
        con.conkey,
        ARRAY_AGG(att.attname ORDER BY u.ordinality) AS columnas
    FROM pg_constraint con
    JOIN pg_class tbl
        ON tbl.oid = con.conrelid
    JOIN pg_namespace ns
        ON ns.oid = tbl.relnamespace
    JOIN UNNEST(con.conkey) WITH ORDINALITY AS u(attnum, ordinality)
        ON TRUE
    JOIN pg_attribute att
        ON att.attrelid = con.conrelid
       AND att.attnum = u.attnum
    WHERE con.contype = 'f'
      AND ns.nspname IN
      (
          'app_auth',
          'profile',
          'ai',
          'market',
          'portfolio',
          'simulation',
          'audit',
          'operation',
          'reporting'
      )
    GROUP BY
        con.oid,
        ns.nspname,
        tbl.relname,
        con.conname,
        con.conrelid,
        con.conkey
)
SELECT
    fk.esquema,
    fk.tabla,
    fk.restriccion,
    ARRAY_TO_STRING(fk.columnas, ', ') AS columnas_fk,
    FORMAT(
        'Evaluar índice sobre %I.%I (%s).',
        fk.esquema,
        fk.tabla,
        ARRAY_TO_STRING(fk.columnas, ', ')
    ) AS recomendacion
FROM foreign_keys fk
WHERE NOT EXISTS
(
    SELECT 1
    FROM pg_index idx
    WHERE idx.indrelid = fk.conrelid
      AND idx.indisvalid
      AND idx.indisready
      AND (idx.indkey::SMALLINT[])[1:CARDINALITY(fk.conkey)]
          = fk.conkey
);
$$;

/*
===============================================================================
15. PERMISOS CONDICIONALES
===============================================================================
*/
DO
$$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_owner') THEN
        GRANT SELECT, INSERT, UPDATE
            ON operation.versiones_esquema
            TO alphainvest_owner;

        GRANT SELECT
            ON operation.v_documentacion_esquemas,
               operation.v_documentacion_objetos,
               operation.v_diccionario_columnas,
               operation.v_documentacion_restricciones,
               operation.v_documentacion_indices,
               operation.v_documentacion_rutinas,
               operation.v_documentacion_triggers,
               operation.v_documentacion_dependencias,
               operation.v_documentacion_permisos,
               operation.v_documentacion_filas_estimadas
            TO alphainvest_owner;

        GRANT EXECUTE
            ON FUNCTION operation.fn_verificar_instalacion(),
                        operation.fn_fk_sin_indice()
            TO alphainvest_owner;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_readonly') THEN
        GRANT SELECT
            ON operation.versiones_esquema,
               operation.v_documentacion_esquemas,
               operation.v_documentacion_objetos,
               operation.v_diccionario_columnas,
               operation.v_documentacion_restricciones,
               operation.v_documentacion_indices,
               operation.v_documentacion_rutinas,
               operation.v_documentacion_triggers,
               operation.v_documentacion_dependencias,
               operation.v_documentacion_permisos,
               operation.v_documentacion_filas_estimadas
            TO alphainvest_readonly;

        GRANT EXECUTE
            ON FUNCTION operation.fn_verificar_instalacion(),
                        operation.fn_fk_sin_indice()
            TO alphainvest_readonly;
    END IF;
END;
$$;

COMMIT;

/*
===============================================================================
16. ORDEN OFICIAL DE EJECUCIÓN
===============================================================================

00_create_database.sql
01_extensions.sql
02_schemas.sql
03_auth_tables.sql
04_ai_base_tables.sql
05_profile_tables.sql
06_market_tables.sql
07_portfolio_tables.sql
08_simulation_tables.sql
09_ai_analysis_tables.sql
10_audit_operation_tables.sql
11_indexes.sql
12_functions.sql
13_triggers.sql
14_seed_catalogs.sql
15_initial_data.sql
16_views.sql
17_materialized_views.sql
18_reporting.sql
19_security.sql
20_backup_restore.sql
21_test_data.sql
22_documentation.sql

Notas:
- 00_create_database.sql se ejecuta conectado a una base administrativa.
- A partir de 01_extensions.sql se debe utilizar la base AlphaInvest AI.
- 21_test_data.sql se ejecuta únicamente en desarrollo o pruebas.
- 19_security.sql debe ejecutarse con privilegios para administrar roles.
- Los respaldos físicos se realizan mediante pg_dump/pg_restore fuera de SQL.

===============================================================================
17. CONSULTAS DE VALIDACIÓN
===============================================================================

-- 17.1 Versión instalada
SELECT *
FROM operation.versiones_esquema
ORDER BY aplicada_en DESC;

-- 17.2 Resumen de esquemas
SELECT *
FROM operation.v_documentacion_esquemas
ORDER BY esquema;

-- 17.3 Inventario completo
SELECT *
FROM operation.v_documentacion_objetos
ORDER BY esquema, tipo_objeto, objeto;

-- 17.4 Diccionario de datos
SELECT *
FROM operation.v_diccionario_columnas
ORDER BY esquema, tabla, posicion;

-- 17.5 Restricciones
SELECT *
FROM operation.v_documentacion_restricciones
ORDER BY esquema, tabla, tipo, restriccion;

-- 17.6 Índices
SELECT *
FROM operation.v_documentacion_indices
ORDER BY esquema, tabla, indice;

-- 17.7 Funciones
SELECT *
FROM operation.v_documentacion_rutinas
ORDER BY esquema, rutina, argumentos;

-- 17.8 Triggers
SELECT *
FROM operation.v_documentacion_triggers
ORDER BY esquema, tabla, trigger;

-- 17.9 Dependencias de vistas
SELECT *
FROM operation.v_documentacion_dependencias
ORDER BY esquema_origen, objeto_origen, esquema_destino, objeto_destino;

-- 17.10 Permisos
SELECT *
FROM operation.v_documentacion_permisos
ORDER BY rol, esquema, objeto, permiso;

-- 17.11 Tamaño y filas estimadas
ANALYZE;

SELECT *
FROM operation.v_documentacion_filas_estimadas
ORDER BY esquema, tabla;

-- 17.12 Verificación general
SELECT *
FROM operation.fn_verificar_instalacion()
ORDER BY categoria, comprobacion;

-- 17.13 Llaves foráneas posiblemente no indexadas
SELECT *
FROM operation.fn_fk_sin_indice()
ORDER BY esquema, tabla, restriccion;

===============================================================================
18. CONSULTAS DE DIAGNÓSTICO
===============================================================================

-- Conexiones actuales
SELECT
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    LEFT(query, 250) AS consulta
FROM pg_stat_activity
WHERE datname = CURRENT_DATABASE()
ORDER BY query_start;

-- Bloqueos no concedidos
SELECT
    a.pid,
    a.usename,
    a.application_name,
    l.locktype,
    l.mode,
    l.granted,
    a.state,
    a.query_start,
    LEFT(a.query, 250) AS consulta
FROM pg_locks l
JOIN pg_stat_activity a
    ON a.pid = l.pid
WHERE a.datname = CURRENT_DATABASE()
  AND NOT l.granted
ORDER BY a.query_start;

-- Transacciones abiertas durante demasiado tiempo
SELECT
    pid,
    usename,
    application_name,
    state,
    xact_start,
    CURRENT_TIMESTAMP - xact_start AS duracion,
    LEFT(query, 250) AS consulta
FROM pg_stat_activity
WHERE datname = CURRENT_DATABASE()
  AND xact_start IS NOT NULL
  AND CURRENT_TIMESTAMP - xact_start > INTERVAL '5 minutes'
ORDER BY xact_start;

-- Tablas con más modificaciones pendientes de análisis
SELECT
    schemaname,
    relname AS tabla,
    n_live_tup,
    n_dead_tup,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
ORDER BY n_dead_tup DESC, n_live_tup DESC;

-- Estado de vistas materializadas
SELECT
    schemaname AS esquema,
    matviewname AS vista_materializada,
    matviewowner AS propietario,
    ispopulated AS tiene_datos
FROM pg_matviews
WHERE schemaname IN
(
    'app_auth',
    'profile',
    'ai',
    'market',
    'portfolio',
    'simulation',
    'audit',
    'operation',
    'reporting'
)
ORDER BY esquema, vista_materializada;

===============================================================================
19. CHECKLIST FINAL
===============================================================================

[ ] La base fue creada con el nombre esperado.
[ ] pgcrypto y las demás extensiones necesarias están instaladas.
[ ] Existen los nueve esquemas funcionales.
[ ] Todos los scripts 00 a 22 fueron ejecutados en orden.
[ ] Las semillas se cargaron sin duplicados.
[ ] Las vistas consultan sin errores.
[ ] Las vistas materializadas están pobladas.
[ ] Los triggers utilizan columnas existentes.
[ ] La función operation.fn_verificar_instalacion() devuelve estado OK.
[ ] Las FK críticas tienen índices apropiados.
[ ] Los roles de aplicación existen y tienen permisos mínimos.
[ ] Se realizó una prueba de pg_dump.
[ ] Se realizó una prueba de restauración en otra base.
[ ] Los datos de 21_test_data.sql se ejecutaron solo en pruebas.
[ ] El repositorio contiene los 23 scripts y la documentación.

===============================================================================
20. COMANDOS GIT
===============================================================================

git checkout feature/database-implementation
git add database/postgresql/22_documentation.sql
git commit -m "docs: agregar inventario y verificacion final de base de datos"
git push

===============================================================================
*/
