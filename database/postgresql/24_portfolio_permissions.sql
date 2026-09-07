/*
============================================================
 AlphaInvest AI
 Script: 24_portfolio_permissions.sql

 Propósito:
 Agregar permisos del módulo Portfolio y asignarlos a los
 roles correspondientes de forma idempotente.
============================================================
*/

BEGIN;


/*
============================================================
 1. PERMISOS DE PORTAFOLIOS
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
        'portafolios.leer',
        'Consultar portafolios',
        'Permite consultar los portafolios propios.',
        'PORTFOLIO',
        TRUE
    ),
    (
        'portafolios.crear',
        'Crear portafolios',
        'Permite crear portafolios virtuales o simulados.',
        'PORTFOLIO',
        TRUE
    ),
    (
        'portafolios.actualizar',
        'Actualizar portafolios',
        'Permite actualizar la información de portafolios propios.',
        'PORTFOLIO',
        TRUE
    ),
    (
        'portafolios.cerrar',
        'Cerrar portafolios',
        'Permite cerrar portafolios propios.',
        'PORTFOLIO',
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
      'portafolios.leer',
      'portafolios.crear',
      'portafolios.actualizar',
      'portafolios.cerrar'
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
  AND p.codigo = 'portafolios.leer'
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
  AND p.modulo = 'PORTFOLIO'
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
    p.codigo AS permiso
FROM app_auth.rol_permisos AS rp
INNER JOIN app_auth.roles AS r
    ON r.id = rp.rol_id
INNER JOIN app_auth.permisos AS p
    ON p.id = rp.permiso_id
WHERE p.modulo = 'PORTFOLIO'
ORDER BY
    r.nombre,
    p.codigo;

============================================================
*/