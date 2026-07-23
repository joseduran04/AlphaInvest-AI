/*
===============================================================================
Proyecto: AlphaInvest AI
Archivo : 19_security.sql
Motor   : PostgreSQL
Objetivo: Configurar roles técnicos y privilegios mínimos para la aplicación,
          procesos internos, consultas/reportes y administración de objetos.

Dependencias:
- 02_schemas.sql
- 03_auth_tables.sql a 10_audit_operation_tables.sql
- 12_functions.sql
- 16_views.sql
- 17_materialized_views.sql
- 18_reporting.sql

IMPORTANTE:
- Ejecutar con un usuario que tenga privilegio CREATEROLE y permisos sobre
  todos los objetos del proyecto.
- Este archivo NO crea usuarios LOGIN ni contiene contraseñas.
- Las credenciales deben crearse fuera de Git mediante variables de entorno,
  un gestor de secretos o una tarea de despliegue segura.
===============================================================================
*/

BEGIN;

/*
===============================================================================
1. ROLES DE GRUPO SIN INICIO DE SESIÓN
===============================================================================
*/
DO $security$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_owner') THEN
        CREATE ROLE alphainvest_owner
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_app') THEN
        CREATE ROLE alphainvest_app
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_worker') THEN
        CREATE ROLE alphainvest_worker
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'alphainvest_readonly') THEN
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

COMMENT ON ROLE alphainvest_owner IS
'Rol propietario técnico de objetos de AlphaInvest AI; no inicia sesión directamente.';

COMMENT ON ROLE alphainvest_app IS
'Rol de la API principal con permisos de negocio y sin administración de estructura.';

COMMENT ON ROLE alphainvest_worker IS
'Rol de procesos internos, ingesta de mercado, IA, simulaciones y trabajos programados.';

COMMENT ON ROLE alphainvest_readonly IS
'Rol de consulta para reportes, soporte y herramientas de inteligencia de negocio.';

/*
===============================================================================
2. SEGURIDAD GENERAL DE LA BASE DE DATOS
===============================================================================
*/
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

DO $database_privileges$
BEGIN
    EXECUTE FORMAT('REVOKE ALL ON DATABASE %I FROM PUBLIC', CURRENT_DATABASE());
    EXECUTE FORMAT(
        'GRANT CONNECT ON DATABASE %I TO alphainvest_owner, alphainvest_app, alphainvest_worker, alphainvest_readonly',
        CURRENT_DATABASE()
    );
    EXECUTE FORMAT(
        'GRANT TEMPORARY ON DATABASE %I TO alphainvest_app, alphainvest_worker',
        CURRENT_DATABASE()
    );
END
$database_privileges$;

/*
===============================================================================
3. ACCESO A ESQUEMAS
===============================================================================
*/
REVOKE ALL ON SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
FROM PUBLIC;

GRANT USAGE ON SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    operation,
    reporting
TO alphainvest_app;

GRANT USAGE ON SCHEMA
    auth,
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
    auth,
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
    auth,
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
La API puede operar datos de negocio, pero no puede modificar auditoría,
configuración técnica de trabajos ni la estructura de la base.
===============================================================================
*/
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA
    auth,
    profile,
    portfolio,
    simulation
TO alphainvest_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ai
TO alphainvest_app;

GRANT SELECT ON ALL TABLES IN SCHEMA market, operation, reporting
TO alphainvest_app;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA
    auth,
    ai,
    profile,
    portfolio,
    simulation
TO alphainvest_app;

/*
===============================================================================
5. PRIVILEGIOS DEL ROL DE PROCESOS
===============================================================================
Los workers pueden ejecutar ingesta, cálculos, simulaciones, IA y tareas
programadas. Auditoría permanece de solo lectura salvo inserción controlada.
===============================================================================
*/
GRANT SELECT ON ALL TABLES IN SCHEMA auth, profile, reporting
TO alphainvest_worker;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    operation
TO alphainvest_worker;

GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA audit
TO alphainvest_worker;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA
    ai,
    market,
    portfolio,
    simulation,
    audit,
    operation
TO alphainvest_worker;

/*
===============================================================================
6. PRIVILEGIOS DEL ROL DE SOLO LECTURA
===============================================================================
*/
GRANT SELECT ON ALL TABLES IN SCHEMA
    auth,
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
7. PRIVILEGIOS SOBRE FUNCIONES Y PROCEDIMIENTOS
===============================================================================
Primero se revoca la ejecución pública y después se concede únicamente a los
roles que necesitan invocar lógica almacenada.
===============================================================================
*/
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
FROM PUBLIC;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    operation,
    reporting
TO alphainvest_app;

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA
    auth,
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
8. PRIVILEGIOS DEL PROPIETARIO TÉCNICO
===============================================================================
Este rol recibe control completo, aunque la transferencia de propiedad de cada
objeto se deja para el despliegue porque requiere conocer al propietario actual.
===============================================================================
*/
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA
    auth,
    ai,
    profile,
    market,
    portfolio,
    simulation,
    audit,
    operation,
    reporting
TO alphainvest_owner;

GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA
    auth,
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
9. PRIVILEGIOS PREDETERMINADOS PARA OBJETOS FUTUROS
===============================================================================
Estas reglas aplican a objetos que cree el usuario que ejecuta este archivo.
En despliegues donde otro rol cree objetos, repetir ALTER DEFAULT PRIVILEGES
usando: ALTER DEFAULT PRIVILEGES FOR ROLE <rol_creador> ...
===============================================================================
*/

-- Eliminar accesos públicos automáticos.
ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
REVOKE ALL ON TABLES FROM PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
REVOKE ALL ON SEQUENCES FROM PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Propietario técnico.
ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
GRANT ALL PRIVILEGES ON TABLES TO alphainvest_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
GRANT ALL PRIVILEGES ON SEQUENCES TO alphainvest_owner;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
GRANT ALL PRIVILEGES ON FUNCTIONS TO alphainvest_owner;

-- Aplicación principal.
ALTER DEFAULT PRIVILEGES IN SCHEMA auth, profile, portfolio, simulation, ai
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA market, operation, reporting
GRANT SELECT ON TABLES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth, profile, portfolio, simulation, ai
GRANT USAGE, SELECT ON SEQUENCES TO alphainvest_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, operation, reporting
GRANT EXECUTE ON FUNCTIONS TO alphainvest_app;

-- Procesos internos.
ALTER DEFAULT PRIVILEGES IN SCHEMA auth, profile, reporting
GRANT SELECT ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA ai, market, portfolio, simulation, operation
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA audit
GRANT SELECT, INSERT ON TABLES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA ai, market, portfolio, simulation, audit, operation
GRANT USAGE, SELECT ON SEQUENCES TO alphainvest_worker;

ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
GRANT EXECUTE ON FUNCTIONS TO alphainvest_worker;

-- Consulta y reportes.
ALTER DEFAULT PRIVILEGES IN SCHEMA
    auth, ai, profile, market, portfolio, simulation, audit, operation, reporting
GRANT SELECT ON TABLES TO alphainvest_readonly;

COMMIT;

/*
===============================================================================
EJEMPLO DE CREACIÓN DE USUARIOS LOGIN - NO EJECUTAR NI VERSIONAR CONTRASEÑAS
===============================================================================
Ejecutar desde una herramienta de despliegue usando secretos reales:

CREATE ROLE alphainvest_api_user
    LOGIN
    PASSWORD '<PASSWORD_DESDE_GESTOR_DE_SECRETOS>'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT alphainvest_app TO alphainvest_api_user;

CREATE ROLE alphainvest_worker_user
    LOGIN
    PASSWORD '<PASSWORD_DESDE_GESTOR_DE_SECRETOS>'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT alphainvest_worker TO alphainvest_worker_user;

CREATE ROLE alphainvest_report_user
    LOGIN
    PASSWORD '<PASSWORD_DESDE_GESTOR_DE_SECRETOS>'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT alphainvest_readonly TO alphainvest_report_user;
===============================================================================
*/