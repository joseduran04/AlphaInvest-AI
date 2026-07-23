-- ============================================================================
-- AlphaInvest AI
-- Parte 20: Respaldo y restauración de PostgreSQL
-- Archivo: 20_backup_restore.sql
--
-- OBJETIVO
--   1. Crear un registro interno de respaldos y restauraciones.
--   2. Proporcionar funciones para registrar ejecuciones.
--   3. Exponer una vista de seguimiento.
--   4. Documentar comandos seguros de pg_dump, pg_restore y psql.
--
-- IMPORTANTE
--   pg_dump y pg_restore son herramientas externas de PostgreSQL.
--   No pueden ejecutarse directamente como sentencias SQL dentro de DBeaver.
--   Los comandos incluidos al final de este archivo deben ejecutarse desde:
--      - PowerShell
--      - CMD
--      - Bash
--      - Una tarea automatizada o pipeline
--
-- REQUISITOS
--   - PostgreSQL Client Tools instaladas.
--   - Acceso a pg_dump, pg_restore y psql desde PATH.
--   - El esquema operation debe existir.
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TABLA DE REGISTRO DE RESPALDOS Y RESTAURACIONES
-- ============================================================================

CREATE TABLE IF NOT EXISTS operation.registros_respaldo
(
    id                    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_operacion        VARCHAR(20) NOT NULL,
    tipo_respaldo         VARCHAR(30) NOT NULL,
    formato               VARCHAR(20) NOT NULL,
    base_datos            VARCHAR(100) NOT NULL,
    nombre_archivo        VARCHAR(500) NOT NULL,
    ruta_archivo          VARCHAR(1000),
    tamanio_bytes         BIGINT,
    checksum_sha256       VARCHAR(64),
    estado                VARCHAR(20) NOT NULL DEFAULT 'INICIADO',
    fecha_inicio          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin             TIMESTAMPTZ,
    duracion_segundos     NUMERIC(14,3),
    ejecutado_por         VARCHAR(150),
    servidor_origen       VARCHAR(255),
    servidor_destino      VARCHAR(255),
    version_postgresql    VARCHAR(100),
    mensaje_error         TEXT,
    observaciones         TEXT,
    metadata              JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT ck_registros_respaldo_tipo_operacion
        CHECK (tipo_operacion IN ('RESPALDO', 'RESTAURACION', 'VALIDACION')),

    CONSTRAINT ck_registros_respaldo_tipo_respaldo
        CHECK
        (
            tipo_respaldo IN
            (
                'COMPLETO',
                'SOLO_ESQUEMA',
                'SOLO_DATOS',
                'POR_ESQUEMA',
                'TABLAS_ESPECIFICAS'
            )
        ),

    CONSTRAINT ck_registros_respaldo_formato
        CHECK (formato IN ('CUSTOM', 'PLAIN', 'DIRECTORY', 'TAR')),

    CONSTRAINT ck_registros_respaldo_estado
        CHECK
        (
            estado IN
            (
                'INICIADO',
                'COMPLETADO',
                'FALLIDO',
                'VALIDADO',
                'CANCELADO'
            )
        ),

    CONSTRAINT ck_registros_respaldo_tamanio
        CHECK (tamanio_bytes IS NULL OR tamanio_bytes >= 0),

    CONSTRAINT ck_registros_respaldo_duracion
        CHECK (duracion_segundos IS NULL OR duracion_segundos >= 0),

    CONSTRAINT ck_registros_respaldo_checksum
        CHECK
        (
            checksum_sha256 IS NULL
            OR checksum_sha256 ~ '^[A-Fa-f0-9]{64}$'
        ),

    CONSTRAINT ck_registros_respaldo_fechas
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

COMMENT ON TABLE operation.registros_respaldo IS
'Bitácora técnica de respaldos, restauraciones y validaciones de AlphaInvest AI.';

COMMENT ON COLUMN operation.registros_respaldo.checksum_sha256 IS
'Checksum SHA-256 calculado fuera de PostgreSQL para validar integridad del archivo.';

COMMENT ON COLUMN operation.registros_respaldo.metadata IS
'Información adicional del proceso en formato JSONB, sin almacenar contraseñas.';

-- ============================================================================
-- 2. ÍNDICES
-- ============================================================================

CREATE INDEX IF NOT EXISTS ix_registros_respaldo_fecha_inicio
    ON operation.registros_respaldo (fecha_inicio DESC);

CREATE INDEX IF NOT EXISTS ix_registros_respaldo_tipo_estado
    ON operation.registros_respaldo (tipo_operacion, estado);

CREATE INDEX IF NOT EXISTS ix_registros_respaldo_base_datos
    ON operation.registros_respaldo (base_datos, fecha_inicio DESC);

CREATE INDEX IF NOT EXISTS ix_registros_respaldo_metadata_gin
    ON operation.registros_respaldo
    USING GIN (metadata);

-- ============================================================================
-- 3. FUNCIÓN PARA REGISTRAR EL INICIO DE UNA OPERACIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION operation.fn_iniciar_registro_respaldo
(
    p_tipo_operacion      VARCHAR,
    p_tipo_respaldo       VARCHAR,
    p_formato             VARCHAR,
    p_base_datos          VARCHAR,
    p_nombre_archivo      VARCHAR,
    p_ruta_archivo        VARCHAR DEFAULT NULL,
    p_ejecutado_por       VARCHAR DEFAULT NULL,
    p_servidor_origen     VARCHAR DEFAULT NULL,
    p_servidor_destino    VARCHAR DEFAULT NULL,
    p_observaciones       TEXT DEFAULT NULL,
    p_metadata            JSONB DEFAULT '{}'::JSONB
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = operation, pg_temp
AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO operation.registros_respaldo
    (
        tipo_operacion,
        tipo_respaldo,
        formato,
        base_datos,
        nombre_archivo,
        ruta_archivo,
        estado,
        ejecutado_por,
        servidor_origen,
        servidor_destino,
        version_postgresql,
        observaciones,
        metadata
    )
    VALUES
    (
        UPPER(TRIM(p_tipo_operacion)),
        UPPER(TRIM(p_tipo_respaldo)),
        UPPER(TRIM(p_formato)),
        TRIM(p_base_datos),
        TRIM(p_nombre_archivo),
        NULLIF(TRIM(p_ruta_archivo), ''),
        'INICIADO',
        NULLIF(TRIM(p_ejecutado_por), ''),
        NULLIF(TRIM(p_servidor_origen), ''),
        NULLIF(TRIM(p_servidor_destino), ''),
        current_setting('server_version'),
        p_observaciones,
        COALESCE(p_metadata, '{}'::JSONB)
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

COMMENT ON FUNCTION operation.fn_iniciar_registro_respaldo
(
    VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
    VARCHAR, VARCHAR, VARCHAR, VARCHAR, TEXT, JSONB
) IS
'Registra el inicio de un respaldo, restauración o validación y devuelve su identificador.';

-- ============================================================================
-- 4. FUNCIÓN PARA FINALIZAR UNA OPERACIÓN
-- ============================================================================

CREATE OR REPLACE FUNCTION operation.fn_finalizar_registro_respaldo
(
    p_id                  BIGINT,
    p_estado              VARCHAR,
    p_tamanio_bytes       BIGINT DEFAULT NULL,
    p_checksum_sha256     VARCHAR DEFAULT NULL,
    p_mensaje_error       TEXT DEFAULT NULL,
    p_observaciones       TEXT DEFAULT NULL,
    p_metadata_adicional  JSONB DEFAULT '{}'::JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = operation, pg_temp
AS $$
DECLARE
    v_actualizados INTEGER;
BEGIN
    UPDATE operation.registros_respaldo
    SET
        estado = UPPER(TRIM(p_estado)),
        fecha_fin = CURRENT_TIMESTAMP,
        duracion_segundos =
            ROUND(
                EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - fecha_inicio))::NUMERIC,
                3
            ),
        tamanio_bytes = COALESCE(p_tamanio_bytes, tamanio_bytes),
        checksum_sha256 =
            COALESCE(NULLIF(LOWER(TRIM(p_checksum_sha256)), ''), checksum_sha256),
        mensaje_error = p_mensaje_error,
        observaciones = COALESCE(p_observaciones, observaciones),
        metadata =
            COALESCE(metadata, '{}'::JSONB)
            || COALESCE(p_metadata_adicional, '{}'::JSONB)
    WHERE id = p_id
      AND estado = 'INICIADO';

    GET DIAGNOSTICS v_actualizados = ROW_COUNT;

    RETURN v_actualizados = 1;
END;
$$;

COMMENT ON FUNCTION operation.fn_finalizar_registro_respaldo
(
    BIGINT, VARCHAR, BIGINT, VARCHAR, TEXT, TEXT, JSONB
) IS
'Finaliza un registro iniciado, calcula su duración y almacena integridad, tamaño y resultado.';

-- ============================================================================
-- 5. VISTA DE ESTADO DE RESPALDOS
-- ============================================================================

CREATE OR REPLACE VIEW operation.v_estado_respaldos AS
SELECT
    rr.id,
    rr.tipo_operacion,
    rr.tipo_respaldo,
    rr.formato,
    rr.base_datos,
    rr.nombre_archivo,
    rr.ruta_archivo,
    rr.estado,
    rr.fecha_inicio,
    rr.fecha_fin,
    rr.duracion_segundos,
    rr.tamanio_bytes,
    CASE
        WHEN rr.tamanio_bytes IS NULL THEN NULL
        ELSE ROUND(rr.tamanio_bytes / 1024.0 / 1024.0, 2)
    END AS tamanio_mb,
    rr.checksum_sha256,
    rr.ejecutado_por,
    rr.servidor_origen,
    rr.servidor_destino,
    rr.version_postgresql,
    rr.mensaje_error,
    rr.observaciones,
    rr.metadata,
    CASE
        WHEN rr.estado = 'INICIADO'
             AND rr.fecha_inicio < CURRENT_TIMESTAMP - INTERVAL '6 hours'
            THEN TRUE
        ELSE FALSE
    END AS posiblemente_interrumpido,
    CASE
        WHEN rr.estado IN ('COMPLETADO', 'VALIDADO')
             AND rr.checksum_sha256 IS NOT NULL
             AND rr.tamanio_bytes > 0
            THEN TRUE
        ELSE FALSE
    END AS integridad_registrada
FROM operation.registros_respaldo rr;

COMMENT ON VIEW operation.v_estado_respaldos IS
'Vista consolidada para supervisar respaldos, restauraciones y validaciones.';

-- ============================================================================
-- 6. PERMISOS CONDICIONALES PARA LOS ROLES DE LA PARTE 19
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_owner') THEN
        GRANT ALL PRIVILEGES
            ON TABLE operation.registros_respaldo
            TO alphainvest_owner;

        GRANT ALL PRIVILEGES
            ON ALL SEQUENCES IN SCHEMA operation
            TO alphainvest_owner;

        GRANT EXECUTE
            ON FUNCTION operation.fn_iniciar_registro_respaldo
            (
                VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
                VARCHAR, VARCHAR, VARCHAR, VARCHAR, TEXT, JSONB
            )
            TO alphainvest_owner;

        GRANT EXECUTE
            ON FUNCTION operation.fn_finalizar_registro_respaldo
            (
                BIGINT, VARCHAR, BIGINT, VARCHAR, TEXT, TEXT, JSONB
            )
            TO alphainvest_owner;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_worker') THEN
        GRANT SELECT, INSERT, UPDATE
            ON TABLE operation.registros_respaldo
            TO alphainvest_worker;

        GRANT USAGE, SELECT
            ON ALL SEQUENCES IN SCHEMA operation
            TO alphainvest_worker;

        GRANT EXECUTE
            ON FUNCTION operation.fn_iniciar_registro_respaldo
            (
                VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR,
                VARCHAR, VARCHAR, VARCHAR, VARCHAR, TEXT, JSONB
            )
            TO alphainvest_worker;

        GRANT EXECUTE
            ON FUNCTION operation.fn_finalizar_registro_respaldo
            (
                BIGINT, VARCHAR, BIGINT, VARCHAR, TEXT, TEXT, JSONB
            )
            TO alphainvest_worker;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_app') THEN
        GRANT SELECT
            ON TABLE operation.registros_respaldo
            TO alphainvest_app;

        GRANT SELECT
            ON operation.v_estado_respaldos
            TO alphainvest_app;
    END IF;

    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_readonly') THEN
        GRANT SELECT
            ON TABLE operation.registros_respaldo
            TO alphainvest_readonly;

        GRANT SELECT
            ON operation.v_estado_respaldos
            TO alphainvest_readonly;
    END IF;
END;
$$;

COMMIT;

-- ============================================================================
-- 7. EJEMPLOS SQL DE REGISTRO
-- ============================================================================

-- Registrar el inicio de un respaldo:
--
-- SELECT operation.fn_iniciar_registro_respaldo
-- (
--     'RESPALDO',
--     'COMPLETO',
--     'CUSTOM',
--     CURRENT_DATABASE(),
--     'alphainvest_2026-07-23_020000.backup',
--     'C:\backups\alphainvest',
--     CURRENT_USER,
--     INET_SERVER_ADDR()::TEXT,
--     NULL,
--     'Respaldo manual previo a despliegue',
--     '{"ambiente":"desarrollo"}'::JSONB
-- ) AS respaldo_id;
--
-- Finalizar correctamente:
--
-- SELECT operation.fn_finalizar_registro_respaldo
-- (
--     1,
--     'COMPLETADO',
--     15728640,
--     '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
--     NULL,
--     'Respaldo verificado',
--     '{"verificado_con":"pg_restore --list"}'::JSONB
-- );
--
-- Finalizar con error:
--
-- SELECT operation.fn_finalizar_registro_respaldo
-- (
--     1,
--     'FALLIDO',
--     NULL,
--     NULL,
--     'pg_dump terminó con código distinto de cero',
--     NULL,
--     '{"exit_code":1}'::JSONB
-- );

-- ============================================================================
-- 8. COMANDOS POWERSHELL PARA RESPALDO
-- ============================================================================
--
-- No guardar contraseñas dentro de este archivo.
-- Se recomienda usar temporalmente la variable PGPASSWORD o un archivo pgpass.
--
-- Ejemplo de variables:
--
-- $env:PGHOST = "localhost"
-- $env:PGPORT = "5432"
-- $env:PGUSER = "postgres"
-- $env:PGDATABASE = "alphainvest_ai"
-- $env:PGPASSWORD = "<PASSWORD_LOCAL>"
--
-- $Fecha = Get-Date -Format "yyyy-MM-dd_HHmmss"
-- $Carpeta = "C:\backups\alphainvest"
-- New-Item -ItemType Directory -Force -Path $Carpeta | Out-Null
--
-- ---------------------------------------------------------------------------
-- Respaldo completo en formato CUSTOM (recomendado)
-- ---------------------------------------------------------------------------
--
-- pg_dump `
--   --format=custom `
--   --compress=9 `
--   --verbose `
--   --no-owner `
--   --no-privileges `
--   --file="$Carpeta\alphainvest_$Fecha.backup" `
--   $env:PGDATABASE
--
-- ---------------------------------------------------------------------------
-- Respaldo únicamente de estructura
-- ---------------------------------------------------------------------------
--
-- pg_dump `
--   --schema-only `
--   --format=plain `
--   --no-owner `
--   --no-privileges `
--   --file="$Carpeta\alphainvest_schema_$Fecha.sql" `
--   $env:PGDATABASE
--
-- ---------------------------------------------------------------------------
-- Respaldo únicamente de datos
-- ---------------------------------------------------------------------------
--
-- pg_dump `
--   --data-only `
--   --format=custom `
--   --compress=9 `
--   --no-owner `
--   --no-privileges `
--   --file="$Carpeta\alphainvest_data_$Fecha.backup" `
--   $env:PGDATABASE
--
-- ---------------------------------------------------------------------------
-- Respaldo de esquemas funcionales seleccionados
-- ---------------------------------------------------------------------------
--
-- pg_dump `
--   --format=custom `
--   --compress=9 `
--   --no-owner `
--   --no-privileges `
--   --schema=auth `
--   --schema=ai `
--   --schema=profile `
--   --schema=market `
--   --schema=portfolio `
--   --schema=simulation `
--   --schema=audit `
--   --schema=operation `
--   --schema=reporting `
--   --file="$Carpeta\alphainvest_schemas_$Fecha.backup" `
--   $env:PGDATABASE
--
-- ---------------------------------------------------------------------------
-- Calcular checksum SHA-256
-- ---------------------------------------------------------------------------
--
-- Get-FileHash `
--   "$Carpeta\alphainvest_$Fecha.backup" `
--   -Algorithm SHA256
--
-- ---------------------------------------------------------------------------
-- Validar que el archivo CUSTOM puede ser leído
-- ---------------------------------------------------------------------------
--
-- pg_restore `
--   --list `
--   "$Carpeta\alphainvest_$Fecha.backup" `
--   | Out-File "$Carpeta\alphainvest_$Fecha.contents.txt"
--
-- ============================================================================
-- 9. COMANDOS POWERSHELL PARA RESTAURACIÓN
-- ============================================================================
--
-- Restaurar sobre una base nueva es la opción recomendada.
--
-- createdb `
--   --host=$env:PGHOST `
--   --port=$env:PGPORT `
--   --username=$env:PGUSER `
--   "alphainvest_restore_test"
--
-- pg_restore `
--   --host=$env:PGHOST `
--   --port=$env:PGPORT `
--   --username=$env:PGUSER `
--   --dbname="alphainvest_restore_test" `
--   --clean `
--   --if-exists `
--   --no-owner `
--   --no-privileges `
--   --verbose `
--   "$Carpeta\alphainvest_$Fecha.backup"
--
-- Para restaurar un archivo SQL plano:
--
-- psql `
--   --host=$env:PGHOST `
--   --port=$env:PGPORT `
--   --username=$env:PGUSER `
--   --dbname="alphainvest_restore_test" `
--   --file="$Carpeta\alphainvest_schema_$Fecha.sql"
--
-- ============================================================================
-- 10. COMANDOS BASH
-- ============================================================================
--
-- export PGHOST="localhost"
-- export PGPORT="5432"
-- export PGUSER="postgres"
-- export PGDATABASE="alphainvest_ai"
-- export PGPASSWORD="<PASSWORD_LOCAL>"
--
-- FECHA=$(date +"%Y-%m-%d_%H%M%S")
-- CARPETA="$HOME/backups/alphainvest"
-- mkdir -p "$CARPETA"
--
-- pg_dump \
--   --format=custom \
--   --compress=9 \
--   --verbose \
--   --no-owner \
--   --no-privileges \
--   --file="$CARPETA/alphainvest_$FECHA.backup" \
--   "$PGDATABASE"
--
-- sha256sum "$CARPETA/alphainvest_$FECHA.backup"
--
-- pg_restore \
--   --list \
--   "$CARPETA/alphainvest_$FECHA.backup" \
--   > "$CARPETA/alphainvest_$FECHA.contents.txt"
--
-- ============================================================================
-- 11. VALIDACIÓN POSTERIOR A UNA RESTAURACIÓN
-- ============================================================================
--
-- Ejecutar estas consultas en la base restaurada:
--
-- SELECT CURRENT_DATABASE() AS base_datos_restaurada;
--
-- SELECT
--     n.nspname AS esquema,
--     COUNT(*) AS total_objetos
-- FROM pg_class c
-- JOIN pg_namespace n
--     ON n.oid = c.relnamespace
-- WHERE n.nspname IN
-- (
--     'auth',
--     'ai',
--     'profile',
--     'market',
--     'portfolio',
--     'simulation',
--     'audit',
--     'operation',
--     'reporting'
-- )
-- AND c.relkind IN ('r', 'p', 'v', 'm', 'S')
-- GROUP BY n.nspname
-- ORDER BY n.nspname;
--
-- SELECT COUNT(*) AS total_activos
-- FROM market.activos;
--
-- SELECT COUNT(*) AS total_roles
-- FROM auth.roles;
--
-- SELECT COUNT(*) AS total_permisos
-- FROM auth.permisos;
--
-- SELECT
--     schemaname,
--     viewname
-- FROM pg_catalog.pg_views
-- WHERE schemaname IN
-- (
--     'auth',
--     'ai',
--     'profile',
--     'market',
--     'portfolio',
--     'simulation',
--     'operation',
--     'reporting'
-- )
-- ORDER BY schemaname, viewname;
--
-- SELECT
--     schemaname,
--     matviewname,
--     ispopulated
-- FROM pg_catalog.pg_matviews
-- ORDER BY schemaname, matviewname;
--
-- ============================================================================
-- 12. POLÍTICA RECOMENDADA DE RETENCIÓN
-- ============================================================================
--
-- Desarrollo:
--   - 7 respaldos diarios.
--   - 4 respaldos semanales.
--
-- Pruebas:
--   - Respaldo previo a cada despliegue.
--   - Retención mínima de 30 días.
--
-- Producción:
--   - Diario: 14 días.
--   - Semanal: 8 semanas.
--   - Mensual: 12 meses.
--   - Anual: según la política legal y operativa aplicable.
--
-- Todo respaldo debe almacenarse fuera del servidor principal y, cuando sea
-- posible, cifrado en reposo.
--
-- Nunca se deben versionar:
--   - Contraseñas.
--   - Archivos .backup.
--   - Archivos .dump.
--   - Archivos SQL con datos reales.
--   - Archivos .pgpass.
--
-- Recomendación para .gitignore:
--
-- backups/
-- *.backup
-- *.dump
-- *.tar
-- *.pgpass
-- .pgpass
-- ============================================================================