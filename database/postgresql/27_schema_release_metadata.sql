/*
===============================================================================
ALPHAINVEST AI
27_schema_release_metadata.sql

PROPÓSITO
-------------------------------------------------------------------------------
Registrar la versión estable posterior a la instalación modular inicial del
esquema AlphaInvest AI.

Este script NO crea tablas funcionales ni modifica estructuras del dominio.
Su responsabilidad es exclusivamente registrar la metadata de liberación del
esquema una vez completados los scripts que forman el baseline estable.

BASELINE ESTABLE
-------------------------------------------------------------------------------
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
22_documentation.sql
23_seed_risk_questionnaire.sql
24_portfolio_permissions.sql
25_simulation_permissions.sql

EXCLUSIONES DEL BASELINE
-------------------------------------------------------------------------------
00_create_database.sql
    Bootstrap exclusivo para instalaciones PostgreSQL locales.

21_test_data.sql
    Datos exclusivos para desarrollo y pruebas.

26_ai_analysis_retry.sql
    Migración incremental de compatibilidad histórica. No es necesaria cuando
    09_ai_analysis_tables.sql ya contiene la estructura definitiva.

En Supabase, 19_security.sql debe sustituirse por:
supabase/19_security_supabase.sql

VERSIÓN DEL ESQUEMA
-------------------------------------------------------------------------------
Versión final registrada por este script: 1.1.0
===============================================================================
*/

BEGIN;

/*
===============================================================================
1. VALIDACIÓN DE INFRAESTRUCTURA DE VERSIONADO
===============================================================================
*/
DO
$$
BEGIN
    IF to_regclass('operation.versiones_esquema') IS NULL THEN
        RAISE EXCEPTION
            'No existe operation.versiones_esquema. Ejecute primero 22_documentation.sql.';
    END IF;
END;
$$;

/*
===============================================================================
2. REGISTRO DE VERSIÓN ESTABLE
===============================================================================
*/
INSERT INTO operation.versiones_esquema
(
    version,
    descripcion,
    archivo_origen,
    metadatos
)
VALUES
(
    '1.1.0',
    'Baseline estable de AlphaInvest AI posterior a las partes funcionales 23, 24 y 25.',
    '27_schema_release_metadata.sql',
    jsonb_build_object
    (
        'motor',
        'PostgreSQL',

        'estado',
        'ESTABLE',

        'baseline',
        jsonb_build_array
        (
            1, 2, 3, 4, 5,
            6, 7, 8, 9, 10,
            11, 12, 13, 14, 15,
            16, 17, 18, 19, 20,
            22, 23, 24, 25
        ),

        'ultima_parte_baseline',
        25,

        'scripts_excluidos',
        jsonb_build_array
        (
            jsonb_build_object
            (
                'parte', 0,
                'archivo', '00_create_database.sql',
                'motivo', 'Bootstrap exclusivo para PostgreSQL local'
            ),
            jsonb_build_object
            (
                'parte', 21,
                'archivo', '21_test_data.sql',
                'motivo', 'Datos exclusivos para desarrollo y pruebas'
            ),
            jsonb_build_object
            (
                'parte', 26,
                'archivo', '26_ai_analysis_retry.sql',
                'motivo', 'Migración incremental de compatibilidad histórica'
            )
        ),

        'supabase',
        jsonb_build_object
        (
            'seguridad',
            'supabase/19_security_supabase.sql',
            'schema_auth_aplicacion',
            'app_auth'
        ),

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
        )
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
3. VALIDACIÓN DEL REGISTRO
===============================================================================
*/
DO
$$
DECLARE
    v_version VARCHAR(30);
BEGIN
    SELECT version
    INTO v_version
    FROM operation.versiones_esquema
    WHERE version = '1.1.0';

    IF v_version IS NULL THEN
        RAISE EXCEPTION
            'No fue posible registrar la versión 1.1.0 del esquema.';
    END IF;
END;
$$;

COMMIT;