/*
===============================================================================
ALPHAINVEST AI
28_on_demand_indicators_and_job_audit.sql

PROPÓSITO
-------------------------------------------------------------------------------
Reducir el tamaño de la base y el tráfico de salida:

1. Los indicadores técnicos (SMA, EMA, RSI, volatilidad y MACD) ya no se
   guardan: la API los calcula al consultarlos con los precios guardados.
   Se desactiva el trabajo nocturno que los recalculaba y se vacía la
   tabla market.indicadores_financieros.

2. El worker actualiza siguiente_ejecucion y ultima_ejecucion de cada
   trabajo en cada corrida. La auditoría de operation.trabajos_programados
   deja de registrar esos cambios; los demás cambios se siguen auditando.

EJECUCIÓN
-------------------------------------------------------------------------------
Supabase -> SQL Editor. Se puede ejecutar más de una vez.
El paso 4 (VACUUM) se ejecuta aparte, una sentencia a la vez.
===============================================================================
*/

BEGIN;

-- 1. Desactivar el cálculo nocturno de indicadores.
UPDATE operation.trabajos_programados
SET activo = FALSE,
    descripcion = 'Obsoleto: los indicadores se calculan al consultarlos y no se guardan.'
WHERE codigo = 'CALCULAR_INDICADORES_DIARIOS';

-- 2. Vaciar los indicadores guardados (se recalculan al consultarlos).
TRUNCATE TABLE market.indicadores_financieros;

-- 3. Auditar los trabajos sin el ruido de la programación del worker.
DROP TRIGGER IF EXISTS
trg_auditoria_trabajos_programados
ON operation.trabajos_programados;

CREATE TRIGGER trg_auditoria_trabajos_programados
AFTER INSERT OR DELETE
ON operation.trabajos_programados
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();

DROP TRIGGER IF EXISTS
trg_auditoria_trabajos_programados_cambios
ON operation.trabajos_programados;

CREATE TRIGGER trg_auditoria_trabajos_programados_cambios
AFTER UPDATE
ON operation.trabajos_programados
FOR EACH ROW
WHEN (
    (
        to_jsonb(OLD)
        - ARRAY['siguiente_ejecucion', 'ultima_ejecucion', 'fecha_actualizacion']
    )
    IS DISTINCT FROM
    (
        to_jsonb(NEW)
        - ARRAY['siguiente_ejecucion', 'ultima_ejecucion', 'fecha_actualizacion']
    )
)
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();

-- Quitar el ruido que ya se acumuló.
DELETE FROM audit.registros_auditoria
WHERE nombre_entidad = 'trabajos_programados'
  AND accion = 'UPDATE'
  AND (
        (valores_anteriores
            - ARRAY['siguiente_ejecucion', 'ultima_ejecucion', 'fecha_actualizacion'])
        IS NOT DISTINCT FROM
        (valores_nuevos
            - ARRAY['siguiente_ejecucion', 'ultima_ejecucion', 'fecha_actualizacion'])
      );

COMMIT;

/*
4. Liberar el espacio (ejecutar aparte, fuera de la transacción):

VACUUM FULL audit.registros_auditoria;
*/
