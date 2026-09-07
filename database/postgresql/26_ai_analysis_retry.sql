/*
============================================================
 26. RECUPERACIÓN DE SOLICITUDES DE ANÁLISIS IA
============================================================

 Agrega un contador persistente de intentos de procesamiento
 a ai.solicitudes_analisis.

 El límite máximo de reintentos continúa definido en:
 operation.trabajos_programados.maximo_reintentos
============================================================
*/

BEGIN;


/*
============================================================
 1. CONTADOR DE INTENTOS
============================================================
*/

ALTER TABLE ai.solicitudes_analisis
ADD COLUMN IF NOT EXISTS intentos_procesamiento INTEGER;


UPDATE ai.solicitudes_analisis
SET intentos_procesamiento = 0
WHERE intentos_procesamiento IS NULL;


ALTER TABLE ai.solicitudes_analisis
ALTER COLUMN intentos_procesamiento
SET DEFAULT 0;


ALTER TABLE ai.solicitudes_analisis
ALTER COLUMN intentos_procesamiento
SET NOT NULL;


/*
============================================================
 2. CHECK
============================================================
*/

DO
$$
BEGIN
    IF NOT EXISTS
    (
        SELECT 1
        FROM pg_constraint
        WHERE conname =
            'ck_solicitudes_analisis_intentos'
          AND conrelid =
            'ai.solicitudes_analisis'::regclass
    ) THEN
        ALTER TABLE ai.solicitudes_analisis
        ADD CONSTRAINT
            ck_solicitudes_analisis_intentos
        CHECK
        (
            intentos_procesamiento >= 0
        );
    END IF;
END;
$$;


COMMENT ON COLUMN
ai.solicitudes_analisis.intentos_procesamiento IS
'Cantidad de intentos de procesamiento iniciados para la solicitud.';


COMMIT;