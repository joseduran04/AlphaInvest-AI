/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : supabase/19_security_supabase.sql
Motor   : PostgreSQL / Supabase
Objetivo:
    Configurar únicamente los roles y privilegios propios de AlphaInvest AI
    sin modificar los roles internos administrados por Supabase.

IMPORTANTE:
- Este archivo es la variante de 19_security.sql para Supabase.
- NO reemplaza 19_security.sql en instalaciones PostgreSQL locales.
- NO revoca permisos globales de PUBLIC sobre la base.
- NO modifica roles internos de Supabase.
- NO utiliza Supabase Auth.
- NO crea usuarios LOGIN ni almacena contraseñas.
===============================================================================
*/

BEGIN;

/*
===============================================================================
1. ROLES DE GRUPO DE ALPHAINVEST
===============================================================================
Estos roles representan responsabilidades internas de AlphaInvest.

No se modifican:
- postgres
- anon
- authenticated
- authenticator
- service_role
- supabase_* u otros roles administrados por Supabase
===============================================================================
*/

DO $security$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'alphainvest_owner'
    ) THEN
        CREATE ROLE alphainvest_owner
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'alphainvest_app'
    ) THEN
        CREATE ROLE alphainvest_app
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'alphainvest_worker'
    ) THEN
        CREATE ROLE alphainvest_worker
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'alphainvest_readonly'
    ) THEN
        CREATE ROLE alphainvest_readonly
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;
END
$security$;


/*
===============================================================================
2. COMENTARIOS
===============================================================================
*/

COMMENT ON ROLE alphainvest_owner IS
'Rol propietario técnico de objetos de AlphaInvest AI.';

COMMENT ON ROLE alphainvest_app IS
'Rol lógico de la API AlphaInvest AI.';

COMMENT ON ROLE alphainvest_worker IS
'Rol lógico de procesos internos y workers de AlphaInvest AI.';

COMMENT ON ROLE alphainvest_readonly IS
'Rol lógico de consulta y reportes de AlphaInvest AI.';


/*
===============================================================================
3. ACCESO A ESQUEMAS DE ALPHAINVEST
===============================================================================

A diferencia del script PostgreSQL local:
- no se revocan permisos globales de PUBLIC;
- no se modifica el esquema public;
- no se alteran esquemas internos de Supabase.
===============================================================================
*/

GRANT USAGE ON SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    operation,
    reporting
TO alphainvest_app;

GRANT USAGE ON SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_worker;

GRANT USAGE ON SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_readonly;

GRANT USAGE, CREATE ON SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;


/*
===============================================================================
4. PRIVILEGIOS DEL ROL DE APLICACIÓN
===============================================================================
*/

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA
    app_auth,
    profile,
    portfolio,
    simulation
TO alphainvest_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA ai
TO alphainvest_app;

GRANT SELECT
ON ALL TABLES IN SCHEMA
    market,
    operation,
    reporting
TO alphainvest_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA
    app_auth,
    ai,
    profile,
    portfolio,
    simulation
TO alphainvest_app;


/*
===============================================================================
5. PRIVILEGIOS DEL WORKER
===============================================================================
*/

GRANT SELECT
ON ALL TABLES IN SCHEMA
    app_auth,
    profile,
    reporting
TO alphainvest_worker;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    operation
TO alphainvest_worker;

GRANT SELECT, INSERT
ON ALL TABLES IN SCHEMA audit
TO alphainvest_worker;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    audit,
    operation
TO alphainvest_worker;


/*
===============================================================================
6. PRIVILEGIOS DE SOLO LECTURA
===============================================================================
*/

GRANT SELECT
ON ALL TABLES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_readonly;


/*
===============================================================================
7. FUNCIONES Y PROCEDIMIENTOS
===============================================================================

No se revoca EXECUTE globalmente a PUBLIC para evitar interferir con objetos
ajenos a AlphaInvest dentro del proyecto Supabase.

Solo se conceden permisos explícitos a nuestros roles.
===============================================================================
*/

GRANT EXECUTE
ON ALL FUNCTIONS IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    operation,
    reporting
TO alphainvest_app;

GRANT EXECUTE
ON ALL FUNCTIONS IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_worker;


/*
===============================================================================
8. PROPIETARIO TÉCNICO LÓGICO
===============================================================================
*/

GRANT ALL PRIVILEGES
ON ALL TABLES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;

GRANT ALL PRIVILEGES
ON ALL SEQUENCES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;

GRANT ALL PRIVILEGES
ON ALL FUNCTIONS IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;


/*
===============================================================================
9. PRIVILEGIOS PREDETERMINADOS
===============================================================================

Estos privilegios aplican únicamente a objetos futuros creados por el usuario
que ejecute este script.

No se revocan privilegios predeterminados de PUBLIC porque en Supabase pueden
existir objetos administrados por la plataforma fuera del dominio AlphaInvest.
===============================================================================
*/

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    profile,
    portfolio,
    simulation,
    ai
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    market,
    operation,
    reporting
GRANT SELECT
ON TABLES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    profile,
    portfolio,
    simulation,
    ai
GRANT USAGE, SELECT
ON SEQUENCES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    operation,
    reporting
GRANT EXECUTE
ON FUNCTIONS TO alphainvest_app;


ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    profile,
    reporting
GRANT SELECT
ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    operation
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    audit
GRANT SELECT, INSERT
ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    audit,
    operation
GRANT USAGE, SELECT
ON SEQUENCES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
GRANT EXECUTE
ON FUNCTIONS TO alphainvest_worker;


ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
GRANT SELECT
ON TABLES TO alphainvest_readonly;


ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
GRANT ALL PRIVILEGES
ON TABLES TO alphainvest_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
GRANT ALL PRIVILEGES
ON SEQUENCES TO alphainvest_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    app_auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
GRANT ALL PRIVILEGES
ON FUNCTIONS TO alphainvest_owner;


COMMIT;

/*
===============================================================================
NOTA DE DESPLIEGUE
===============================================================================

Los roles anteriores son roles lógicos NOLOGIN.

No se crean usuarios LOGIN en este script.

Las conexiones reales de FastAPI y del worker se configurarán durante el
despliegue usando credenciales seguras proporcionadas por el entorno de
producción.

No versionar:
- contraseñas;
- connection strings reales;
- certificados privados;
- service_role keys;
- JWT secrets.

===============================================================================
*/