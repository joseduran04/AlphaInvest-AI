/*
============================================================
 AlphaInvest AI
 Script: 25_simulation_permissions.sql

 Propósito:
 Agregar permisos del módulo Simulation y asignarlos a los
 roles correspondientes de forma idempotente.

 Dependencias:
 - 03_auth_tables.sql
 - 14_seed_catalogs.sql
 - 24_portfolio_permissions.sql
============================================================
*/

BEGIN;


/*
============================================================
 1. PERMISOS DE SIMULACIÓN
============================================================
*/

INSERT INTO app_auth.permisos
(
    codigo,
    nombre,
    descripcion,
    modulo,
    activo
)
VALUES
    (
        'simulaciones.leer',
        'Consultar simulaciones',
        'Permite consultar configuraciones, ejecuciones y resultados de simulaciones propias.',
        'SIMULATION',
        TRUE
    ),
    (
        'simulaciones.crear',
        'Crear simulaciones',
        'Permite crear configuraciones de simulación propias.',
        'SIMULATION',
        TRUE
    ),
    (
        'simulaciones.actualizar',
        'Actualizar simulaciones',
        'Permite actualizar configuraciones de simulación propias.',
        'SIMULATION',
        TRUE
    ),
    (
        'simulaciones.archivar',
        'Archivar simulaciones',
        'Permite archivar configuraciones de simulación propias.',
        'SIMULATION',
        TRUE
    ),
    (
        'simulaciones.ejecutar',
        'Ejecutar simulaciones',
        'Permite solicitar ejecuciones de configuraciones de simulación propias.',
        'SIMULATION',
        TRUE
    )
ON CONFLICT (codigo)
DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    modulo = EXCLUDED.modulo,
    activo = EXCLUDED.activo;


/*
============================================================
 2. INVERSIONISTA
============================================================
*/

INSERT INTO app_auth.rol_permisos
(
    rol_id,
    permiso_id
)
SELECT
    r.id,
    p.id
FROM app_auth.roles AS r
CROSS JOIN app_auth.permisos AS p
WHERE r.nombre = 'INVERSIONISTA'
  AND p.codigo IN
  (
      'simulaciones.leer',
      'simulaciones.crear',
      'simulaciones.actualizar',
      'simulaciones.archivar',
      'simulaciones.ejecutar'
  )
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;


/*
============================================================
 3. ANALISTA
============================================================
*/

INSERT INTO app_auth.rol_permisos
(
    rol_id,
    permiso_id
)
SELECT
    r.id,
    p.id
FROM app_auth.roles AS r
CROSS JOIN app_auth.permisos AS p
WHERE r.nombre = 'ANALISTA'
  AND p.codigo = 'simulaciones.leer'
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;


/*
============================================================
 4. ADMINISTRADOR
============================================================
*/

INSERT INTO app_auth.rol_permisos
(
    rol_id,
    permiso_id
)
SELECT
    r.id,
    p.id
FROM app_auth.roles AS r
CROSS JOIN app_auth.permisos AS p
WHERE r.nombre = 'ADMINISTRADOR'
  AND p.modulo = 'SIMULATION'
  AND p.activo = TRUE
ON CONFLICT (rol_id, permiso_id)
DO NOTHING;


COMMIT;


/*
============================================================
 VALIDACIÓN
============================================================

SELECT
    r.nombre AS rol,
    p.codigo AS permiso,
    p.nombre,
    p.modulo,
    p.activo
FROM app_auth.rol_permisos AS rp
INNER JOIN app_auth.roles AS r
    ON r.id = rp.rol_id
INNER JOIN app_auth.permisos AS p
    ON p.id = rp.permiso_id
WHERE p.modulo = 'SIMULATION'
ORDER BY
    r.nombre,
    p.codigo;

============================================================
*/