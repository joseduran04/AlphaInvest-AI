/*
============================================================
 AlphaInvest AI
 Script: 01_extensions.sql
 Propósito: Habilitar extensiones requeridas.
 Ejecutar conectado a alphainvest_db.
============================================================
*/

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

COMMIT;