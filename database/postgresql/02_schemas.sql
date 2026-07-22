/*
============================================================
 AlphaInvest AI
 Script: 02_schemas.sql
 Propósito: Crear los esquemas por dominio.
============================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS profile;
CREATE SCHEMA IF NOT EXISTS market;
CREATE SCHEMA IF NOT EXISTS portfolio;
CREATE SCHEMA IF NOT EXISTS simulation;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS operation;

COMMENT ON SCHEMA auth IS
'Usuarios, autenticacion, roles, permisos y sesiones.';

COMMENT ON SCHEMA profile IS
'Cuestionarios, evaluaciones y perfiles de riesgo.';

COMMENT ON SCHEMA market IS
'Activos, mercados, precios e indicadores financieros.';

COMMENT ON SCHEMA portfolio IS
'Listas de seguimiento y portafolios virtuales.';

COMMENT ON SCHEMA simulation IS
'Configuraciones y resultados de simulaciones historicas.';

COMMENT ON SCHEMA ai IS
'Modelos, analisis, predicciones y recomendaciones.';

COMMENT ON SCHEMA audit IS
'Eventos de auditoria y errores del sistema.';

COMMENT ON SCHEMA operation IS
'Tareas programadas y ejecuciones de procesos.';

COMMIT;