/*
============================================================
 AlphaInvest AI
 Script: 00_create_database.sql
 Propósito: Crear la base de datos principal.
 Ejecutar conectado a la base postgres.
============================================================
*/

CREATE DATABASE alphainvest_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TEMPLATE = template0;