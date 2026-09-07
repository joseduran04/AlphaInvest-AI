/*
============================================================
 AlphaInvest AI
 Script: 13_triggers.sql

 Propósito:
 Crear funciones de trigger y asociarlas con las tablas
 correspondientes para automatizar reglas de integridad,
 cálculos derivados, actualización de fechas, validación
 de estados y auditoría selectiva.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql
 - 05_profile_tables.sql
 - 06_market_tables.sql
 - 07_portfolio_tables.sql
 - 08_simulation_tables.sql
 - 09_ai_analysis_tables.sql
 - 10_audit_operation_tables.sql
 - 11_indexes.sql
 - 12_functions.sql

 Esquemas utilizados:
 - app_auth
 - profile
 - portfolio
 - simulation
 - ai
 - audit
 - operation

 Consideraciones:
 - Los triggers se eliminan antes de recrearse.
 - Las funciones se crean con CREATE OR REPLACE FUNCTION.
 - La auditoría se aplica únicamente a tablas seleccionadas.
 - No se auditan tablas masivas como precios históricos.
============================================================
*/

BEGIN;


/*
============================================================
 1. FUNCIÓN DE TRIGGER:
    portfolio.fn_trg_calcular_posicion
============================================================

 Propósito:
 Calcular automáticamente los campos derivados de una
 posición antes de insertar o actualizar el registro.

 Evita:
 - costo_total inconsistente
 - valor_actual incorrecto
 - ganancia_perdida incorrecta
 - rendimiento incorrecto
 - estado incompatible con cantidad
============================================================
*/

CREATE OR REPLACE FUNCTION portfolio.fn_trg_calcular_posicion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    /*
     El costo se calcula con la cantidad actual y el precio
     promedio de compra.
    */

    NEW.costo_total :=
        ROUND
        (
            NEW.cantidad
            * NEW.precio_promedio_compra,
            8
        );

    /*
     Cuando existe precio actual, se calculan el valor,
     la ganancia y el rendimiento.
    */

    IF NEW.precio_actual IS NOT NULL THEN
        NEW.valor_actual :=
            ROUND
            (
                NEW.cantidad
                * NEW.precio_actual,
                8
            );

        NEW.ganancia_perdida :=
            ROUND
            (
                NEW.valor_actual
                - NEW.costo_total,
                8
            );

        IF NEW.costo_total > 0 THEN
            NEW.rendimiento_porcentaje :=
                ROUND
                (
                    (
                        NEW.ganancia_perdida
                        / NEW.costo_total
                    ) * 100,
                    8
                );
        ELSE
            NEW.rendimiento_porcentaje := NULL;
        END IF;
    ELSE
        NEW.valor_actual := NULL;
        NEW.ganancia_perdida := NULL;
        NEW.rendimiento_porcentaje := NULL;
    END IF;

    /*
     Una posición con cantidad cero se considera cerrada.
    */

    IF NEW.cantidad = 0 THEN
        NEW.estado := 'CERRADA';

        NEW.fecha_cierre :=
            COALESCE
            (
                NEW.fecha_cierre,
                CURRENT_TIMESTAMP
            );
    ELSE
        NEW.estado := 'ABIERTA';
        NEW.fecha_cierre := NULL;
    END IF;

    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
portfolio.fn_trg_calcular_posicion() IS
'Calcula automáticamente costo, valor, ganancia, rendimiento, estado y fecha de cierre de una posición virtual.';


/*
============================================================
 2. TRIGGER:
    Cálculo automático de posiciones
============================================================
*/

DROP TRIGGER IF EXISTS
trg_posiciones_calcular
ON portfolio.posiciones;

CREATE TRIGGER trg_posiciones_calcular
BEFORE INSERT OR UPDATE OF
    cantidad,
    precio_promedio_compra,
    precio_actual
ON portfolio.posiciones
FOR EACH ROW
EXECUTE FUNCTION portfolio.fn_trg_calcular_posicion();

COMMENT ON TRIGGER
trg_posiciones_calcular
ON portfolio.posiciones IS
'Recalcula automáticamente los campos derivados cuando cambia la cantidad o alguno de los precios de una posición.';


/*
============================================================
 3. FUNCIÓN DE TRIGGER:
    simulation.fn_trg_validar_configuracion_lista
============================================================

 Propósito:
 Exigir una distribución válida cuando una configuración
 se cambia al estado LISTA.

 Una configuración en BORRADOR puede estar incompleta.
 Una configuración en LISTA debe:
 - Tener al menos un activo.
 - Sumar 100 por ciento.
 - No exceder el capital inicial con sus montos.
============================================================
*/

CREATE OR REPLACE FUNCTION
simulation.fn_trg_validar_configuracion_lista()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'LISTA'
       AND
       (
           TG_OP = 'INSERT'
           OR OLD.estado IS DISTINCT FROM NEW.estado
           OR OLD.capital_inicial
              IS DISTINCT FROM NEW.capital_inicial
       ) THEN

        PERFORM
            simulation.fn_exigir_distribucion_valida
            (
                NEW.id
            );
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_trg_validar_configuracion_lista() IS
'Impide marcar una configuración como LISTA cuando su distribución de activos no es válida.';


/*
============================================================
 4. TRIGGER:
    Validar configuración al marcarla LISTA
============================================================

 Se utiliza AFTER porque los activos relacionados ya deben
 existir en simulation.configuracion_activos.

 Para una configuración nueva se recomienda:
 1. Crear en BORRADOR.
 2. Insertar activos.
 3. Cambiar a LISTA.
============================================================
*/

DROP TRIGGER IF EXISTS
trg_configuraciones_validar_lista
ON simulation.configuraciones;

CREATE TRIGGER trg_configuraciones_validar_lista
AFTER UPDATE OF
    estado,
    capital_inicial
ON simulation.configuraciones
FOR EACH ROW
WHEN
(
    NEW.estado = 'LISTA'
)
EXECUTE FUNCTION
simulation.fn_trg_validar_configuracion_lista();

COMMENT ON TRIGGER
trg_configuraciones_validar_lista
ON simulation.configuraciones IS
'Valida la distribución de activos cuando una configuración de simulación se marca como LISTA.';


/*
============================================================
 5. FUNCIÓN DE TRIGGER:
    simulation.fn_trg_validar_ejecucion
============================================================

 Propósito:
 Validar que una ejecución:
 - Use una configuración existente.
 - Sea solicitada por el propietario de la configuración.
 - Se base en una configuración LISTA.
 - Tenga una distribución válida.
============================================================
*/

CREATE OR REPLACE FUNCTION
simulation.fn_trg_validar_ejecucion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_usuario_id UUID;
    v_estado     VARCHAR(30);
BEGIN
    SELECT
        usuario_id,
        estado
    INTO
        v_usuario_id,
        v_estado
    FROM simulation.configuraciones
    WHERE id = NEW.configuracion_id
    FOR SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe la configuración de simulación %.',
            NEW.configuracion_id
            USING ERRCODE = '23503';
    END IF;

    IF NEW.usuario_id <> v_usuario_id THEN
        RAISE EXCEPTION
            'El usuario de la ejecución no coincide con el propietario de la configuración.'
            USING
                ERRCODE = '23514',
                HINT = 'Utilice el usuario_id registrado en la configuración.';
    END IF;

    IF v_estado <> 'LISTA' THEN
        RAISE EXCEPTION
            'La configuración % no está LISTA para ejecutarse. Estado actual: %.',
            NEW.configuracion_id,
            v_estado
            USING ERRCODE = '23514';
    END IF;

    PERFORM
        simulation.fn_exigir_distribucion_valida
        (
            NEW.configuracion_id
        );

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_trg_validar_ejecucion() IS
'Valida propiedad, estado y distribución antes de crear una ejecución de simulación.';


/*
============================================================
 6. TRIGGER:
    Validación antes de crear una ejecución
============================================================
*/

DROP TRIGGER IF EXISTS
trg_ejecuciones_simulacion_validar
ON simulation.ejecuciones;

CREATE TRIGGER trg_ejecuciones_simulacion_validar
BEFORE INSERT
ON simulation.ejecuciones
FOR EACH ROW
EXECUTE FUNCTION simulation.fn_trg_validar_ejecucion();

COMMENT ON TRIGGER
trg_ejecuciones_simulacion_validar
ON simulation.ejecuciones IS
'Impide crear ejecuciones para configuraciones incompletas, no listas o pertenecientes a otro usuario.';


/*
============================================================
 7. FUNCIÓN DE TRIGGER:
    simulation.fn_trg_gestionar_estado_ejecucion
============================================================

 Propósito:
 Completar automáticamente fechas y progreso según el
 estado de una ejecución de simulación.
============================================================
*/

CREATE OR REPLACE FUNCTION
simulation.fn_trg_gestionar_estado_ejecucion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'PENDIENTE' THEN
        NEW.porcentaje_progreso :=
            COALESCE
            (
                NEW.porcentaje_progreso,
                0
            );
    END IF;

    IF NEW.estado = 'EJECUTANDO' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin := NULL;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado = 'COMPLETADA' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );

        NEW.porcentaje_progreso := 100;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado IN ('FALLIDA', 'CANCELADA') THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_trg_gestionar_estado_ejecucion() IS
'Completa automáticamente fechas, progreso y datos relacionados con los estados de una ejecución de simulación.';


/*
============================================================
 8. TRIGGER:
    Gestión de estados de simulaciones
============================================================
*/

DROP TRIGGER IF EXISTS
trg_ejecuciones_simulacion_estado
ON simulation.ejecuciones;

CREATE TRIGGER trg_ejecuciones_simulacion_estado
BEFORE INSERT OR UPDATE OF estado
ON simulation.ejecuciones
FOR EACH ROW
EXECUTE FUNCTION
simulation.fn_trg_gestionar_estado_ejecucion();

COMMENT ON TRIGGER
trg_ejecuciones_simulacion_estado
ON simulation.ejecuciones IS
'Gestiona automáticamente fechas y progreso al cambiar el estado de una ejecución de simulación.';


/*
============================================================
 9. FUNCIÓN DE TRIGGER:
    ai.fn_trg_validar_solicitud_recursos
============================================================

 Propósito:
 Comprobar que el portafolio y perfil utilizados por una
 solicitud de análisis pertenezcan al mismo usuario.
============================================================
*/

CREATE OR REPLACE FUNCTION
ai.fn_trg_validar_solicitud_recursos()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_propietario UUID;
BEGIN
    IF NEW.portafolio_id IS NOT NULL THEN
        SELECT usuario_id
        INTO v_propietario
        FROM portfolio.portafolios
        WHERE id = NEW.portafolio_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe el portafolio %.',
                NEW.portafolio_id
                USING ERRCODE = '23503';
        END IF;

        IF v_propietario <> NEW.usuario_id THEN
            RAISE EXCEPTION
                'El portafolio no pertenece al usuario de la solicitud.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.perfil_riesgo_id IS NOT NULL THEN
        SELECT usuario_id
        INTO v_propietario
        FROM profile.perfiles_riesgo
        WHERE id = NEW.perfil_riesgo_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe el perfil de riesgo %.',
                NEW.perfil_riesgo_id
                USING ERRCODE = '23503';
        END IF;

        IF v_propietario <> NEW.usuario_id THEN
            RAISE EXCEPTION
                'El perfil de riesgo no pertenece al usuario de la solicitud.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.ejecucion_simulacion_id IS NOT NULL THEN
        SELECT usuario_id
        INTO v_propietario
        FROM simulation.ejecuciones
        WHERE id = NEW.ejecucion_simulacion_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe la ejecución de simulación %.',
                NEW.ejecucion_simulacion_id
                USING ERRCODE = '23503';
        END IF;

        IF v_propietario <> NEW.usuario_id THEN
            RAISE EXCEPTION
                'La ejecución de simulación no pertenece al usuario de la solicitud.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
ai.fn_trg_validar_solicitud_recursos() IS
'Comprueba que el portafolio, perfil de riesgo y simulación de una solicitud pertenezcan al mismo usuario.';


/*
============================================================
 10. TRIGGER:
     Validación de recursos de solicitudes de IA
============================================================
*/

DROP TRIGGER IF EXISTS
trg_solicitudes_analisis_validar_recursos
ON ai.solicitudes_analisis;

CREATE TRIGGER trg_solicitudes_analisis_validar_recursos
BEFORE INSERT OR UPDATE OF
    usuario_id,
    portafolio_id,
    perfil_riesgo_id,
    ejecucion_simulacion_id
ON ai.solicitudes_analisis
FOR EACH ROW
EXECUTE FUNCTION ai.fn_trg_validar_solicitud_recursos();

COMMENT ON TRIGGER
trg_solicitudes_analisis_validar_recursos
ON ai.solicitudes_analisis IS
'Evita que una solicitud utilice recursos pertenecientes a otro usuario.';


/*
============================================================
 11. FUNCIÓN DE TRIGGER:
     ai.fn_trg_gestionar_estado_solicitud
============================================================
*/

CREATE OR REPLACE FUNCTION
ai.fn_trg_gestionar_estado_solicitud()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'PENDIENTE' THEN
        NEW.porcentaje_progreso :=
            COALESCE
            (
                NEW.porcentaje_progreso,
                0
            );
    END IF;

    IF NEW.estado = 'EJECUTANDO' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin := NULL;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado = 'COMPLETADA' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );

        NEW.porcentaje_progreso := 100;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado IN ('FALLIDA', 'CANCELADA') THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
ai.fn_trg_gestionar_estado_solicitud() IS
'Gestiona automáticamente fechas, progreso y errores de una solicitud de análisis de IA.';


/*
============================================================
 12. TRIGGER:
     Gestión de estados de solicitudes de IA
============================================================
*/

DROP TRIGGER IF EXISTS
trg_solicitudes_analisis_estado
ON ai.solicitudes_analisis;

CREATE TRIGGER trg_solicitudes_analisis_estado
BEFORE INSERT OR UPDATE OF estado
ON ai.solicitudes_analisis
FOR EACH ROW
EXECUTE FUNCTION ai.fn_trg_gestionar_estado_solicitud();

COMMENT ON TRIGGER
trg_solicitudes_analisis_estado
ON ai.solicitudes_analisis IS
'Completa automáticamente fechas y progreso al cambiar el estado de una solicitud de análisis.';


/*
============================================================
 13. FUNCIÓN DE TRIGGER:
     ai.fn_trg_validar_recomendacion
============================================================

 Propósito:
 Comprobar consistencia entre:
 - solicitud
 - usuario
 - perfil de riesgo
 - portafolio
============================================================
*/

CREATE OR REPLACE FUNCTION
ai.fn_trg_validar_recomendacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_usuario_solicitud UUID;
    v_usuario_recurso   UUID;
BEGIN
    SELECT usuario_id
    INTO v_usuario_solicitud
    FROM ai.solicitudes_analisis
    WHERE id = NEW.solicitud_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe la solicitud de análisis %.',
            NEW.solicitud_id
            USING ERRCODE = '23503';
    END IF;

    IF NEW.usuario_id <> v_usuario_solicitud THEN
        RAISE EXCEPTION
            'El usuario de la recomendación no coincide con el usuario de la solicitud.'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.perfil_riesgo_id IS NOT NULL THEN
        SELECT usuario_id
        INTO v_usuario_recurso
        FROM profile.perfiles_riesgo
        WHERE id = NEW.perfil_riesgo_id;

        IF v_usuario_recurso IS DISTINCT FROM NEW.usuario_id THEN
            RAISE EXCEPTION
                'El perfil de riesgo de la recomendación no pertenece al usuario.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    IF NEW.portafolio_id IS NOT NULL THEN
        SELECT usuario_id
        INTO v_usuario_recurso
        FROM portfolio.portafolios
        WHERE id = NEW.portafolio_id;

        IF v_usuario_recurso IS DISTINCT FROM NEW.usuario_id THEN
            RAISE EXCEPTION
                'El portafolio de la recomendación no pertenece al usuario.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
ai.fn_trg_validar_recomendacion() IS
'Valida que la recomendación, solicitud, perfil y portafolio pertenezcan al mismo usuario.';


/*
============================================================
 14. TRIGGER:
     Validación de recomendaciones
============================================================
*/

DROP TRIGGER IF EXISTS
trg_recomendaciones_validar
ON ai.recomendaciones;

CREATE TRIGGER trg_recomendaciones_validar
BEFORE INSERT OR UPDATE OF
    solicitud_id,
    usuario_id,
    perfil_riesgo_id,
    portafolio_id
ON ai.recomendaciones
FOR EACH ROW
EXECUTE FUNCTION ai.fn_trg_validar_recomendacion();

COMMENT ON TRIGGER
trg_recomendaciones_validar
ON ai.recomendaciones IS
'Impide crear recomendaciones con recursos pertenecientes a usuarios diferentes.';


/*
============================================================
 15. FUNCIÓN DE TRIGGER:
     ai.fn_trg_gestionar_estado_recomendacion
============================================================
*/

CREATE OR REPLACE FUNCTION
ai.fn_trg_gestionar_estado_recomendacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'ACEPTADA' THEN
        NEW.fecha_aceptacion :=
            COALESCE
            (
                NEW.fecha_aceptacion,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_rechazo := NULL;
    ELSIF NEW.estado = 'RECHAZADA' THEN
        NEW.fecha_rechazo :=
            COALESCE
            (
                NEW.fecha_rechazo,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_aceptacion := NULL;
    ELSIF NEW.estado IN
    (
        'GENERADA',
        'MOSTRADA',
        'EXPIRADA',
        'RETIRADA'
    ) THEN
        IF NEW.estado IN ('GENERADA', 'MOSTRADA') THEN
            NEW.fecha_aceptacion := NULL;
            NEW.fecha_rechazo := NULL;
        END IF;
    END IF;

    /*
     Una recomendación vencida no puede aceptarse.
    */

    IF NEW.estado = 'ACEPTADA'
       AND NEW.fecha_expiracion IS NOT NULL
       AND NEW.fecha_expiracion <= CURRENT_TIMESTAMP THEN
        RAISE EXCEPTION
            'No se puede aceptar una recomendación expirada.'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
ai.fn_trg_gestionar_estado_recomendacion() IS
'Gestiona fechas de aceptación y rechazo e impide aceptar recomendaciones expiradas.';


/*
============================================================
 16. TRIGGER:
     Estados de recomendaciones
============================================================
*/

DROP TRIGGER IF EXISTS
trg_recomendaciones_estado
ON ai.recomendaciones;

CREATE TRIGGER trg_recomendaciones_estado
BEFORE INSERT OR UPDATE OF
    estado,
    fecha_expiracion
ON ai.recomendaciones
FOR EACH ROW
EXECUTE FUNCTION ai.fn_trg_gestionar_estado_recomendacion();

COMMENT ON TRIGGER
trg_recomendaciones_estado
ON ai.recomendaciones IS
'Gestiona automáticamente las fechas de decisión de una recomendación y valida su vigencia.';


/*
============================================================
 17. FUNCIÓN DE TRIGGER:
     ai.fn_trg_validar_evidencia
============================================================

 Propósito:
 Garantizar que una evidencia, su predicción y su
 recomendación pertenezcan a la misma solicitud.
============================================================
*/

CREATE OR REPLACE FUNCTION
ai.fn_trg_validar_evidencia()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_solicitud_prediccion UUID;
    v_solicitud_recomendacion UUID;
    v_solicitud_prediccion_origen TEXT;
BEGIN
    /*
    ============================================================
    1. VALIDAR RECOMENDACIÓN
    ============================================================
    La recomendación sí debe pertenecer siempre a la misma
    solicitud que la evidencia.
    */

    IF NEW.recomendacion_id IS NOT NULL THEN
        SELECT solicitud_id
        INTO v_solicitud_recomendacion
        FROM ai.recomendaciones
        WHERE id = NEW.recomendacion_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe la recomendación %.',
                NEW.recomendacion_id
                USING ERRCODE = '23503';
        END IF;

        IF v_solicitud_recomendacion <> NEW.solicitud_id THEN
            RAISE EXCEPTION
                'La recomendación de la evidencia pertenece a otra solicitud.'
                USING ERRCODE = '23514';
        END IF;
    END IF;

    /*
    ============================================================
    2. VALIDAR PREDICCIÓN
    ============================================================

    Una predicción puede pertenecer:

    A) A la misma solicitud de la evidencia.

    B) A una solicitud ACTIVO utilizada como origen de una
       solicitud RECOMENDACION.

       En este segundo caso, la solicitud de recomendación debe
       declarar explícitamente prediction_request_id dentro de
       parametros.
    */

    IF NEW.prediccion_id IS NOT NULL THEN
        SELECT solicitud_id
        INTO v_solicitud_prediccion
        FROM ai.predicciones_activo
        WHERE id = NEW.prediccion_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe la predicción %.',
                NEW.prediccion_id
                USING ERRCODE = '23503';
        END IF;

        IF v_solicitud_prediccion <> NEW.solicitud_id THEN

            /*
             La referencia cruzada solamente es válida cuando
             la evidencia pertenece a una recomendación.
            */

            IF NEW.recomendacion_id IS NULL THEN
                RAISE EXCEPTION
                    'La predicción de la evidencia pertenece a otra solicitud.'
                    USING ERRCODE = '23514';
            END IF;

            SELECT
                parametros ->> 'prediction_request_id'
            INTO v_solicitud_prediccion_origen
            FROM ai.solicitudes_analisis
            WHERE id = NEW.solicitud_id;

            IF
                v_solicitud_prediccion_origen IS NULL
                OR v_solicitud_prediccion_origen
                    <> v_solicitud_prediccion::TEXT
            THEN
                RAISE EXCEPTION
                    'La predicción de la evidencia no corresponde a la solicitud ACTIVO declarada como origen.'
                    USING ERRCODE = '23514';
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
ai.fn_trg_validar_evidencia() IS
'Garantiza la consistencia entre evidencias, recomendaciones y predicciones, permitiendo predicciones de una solicitud ACTIVO origen cuando una solicitud RECOMENDACION la referencia explícitamente mediante prediction_request_id.';


/*
============================================================
 18. TRIGGER:
     Validación de evidencias
============================================================
*/

DROP TRIGGER IF EXISTS
trg_evidencias_analisis_validar
ON ai.evidencias_analisis;

CREATE TRIGGER trg_evidencias_analisis_validar
BEFORE INSERT OR UPDATE OF
    solicitud_id,
    recomendacion_id,
    prediccion_id
ON ai.evidencias_analisis
FOR EACH ROW
EXECUTE FUNCTION ai.fn_trg_validar_evidencia();

COMMENT ON TRIGGER
trg_evidencias_analisis_validar
ON ai.evidencias_analisis IS
'Valida la trazabilidad de evidencias con su recomendación y permite predicciones externas únicamente cuando corresponden a la solicitud ACTIVO declarada como origen.';


/*
============================================================
 19. FUNCIÓN DE TRIGGER:
     operation.fn_trg_gestionar_notificacion
============================================================
*/

CREATE OR REPLACE FUNCTION
operation.fn_trg_gestionar_notificacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'PROGRAMADA'
       AND NEW.fecha_programada IS NULL THEN
        RAISE EXCEPTION
            'Una notificación PROGRAMADA requiere fecha_programada.'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.estado = 'ENVIANDO' THEN
        NEW.intentos_envio :=
            CASE
                WHEN TG_OP = 'INSERT'
                    THEN COALESCE(NEW.intentos_envio, 0) + 1
                WHEN OLD.estado IS DISTINCT FROM 'ENVIANDO'
                    THEN COALESCE(OLD.intentos_envio, 0) + 1
                ELSE NEW.intentos_envio
            END;
    END IF;

    IF NEW.estado = 'ENVIADA' THEN
        NEW.fecha_envio :=
            COALESCE
            (
                NEW.fecha_envio,
                CURRENT_TIMESTAMP
            );

        NEW.ultimo_error := NULL;
    END IF;

    IF NEW.estado = 'FALLIDA'
       AND NULLIF(TRIM(NEW.ultimo_error), '') IS NULL THEN
        RAISE EXCEPTION
            'Una notificación FALLIDA requiere ultimo_error.'
            USING ERRCODE = '23514';
    END IF;

    IF NEW.fecha_lectura IS NOT NULL
       AND NEW.fecha_envio IS NULL THEN
        RAISE EXCEPTION
            'Una notificación no puede marcarse como leída antes de ser enviada.'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
operation.fn_trg_gestionar_notificacion() IS
'Gestiona intentos, fechas de envío, lectura y errores del ciclo de vida de una notificación.';


/*
============================================================
 20. TRIGGER:
     Gestión de notificaciones
============================================================
*/

DROP TRIGGER IF EXISTS
trg_notificaciones_estado
ON operation.notificaciones;

CREATE TRIGGER trg_notificaciones_estado
BEFORE INSERT OR UPDATE OF
    estado,
    fecha_programada,
    fecha_envio,
    fecha_lectura
ON operation.notificaciones
FOR EACH ROW
EXECUTE FUNCTION operation.fn_trg_gestionar_notificacion();

COMMENT ON TRIGGER
trg_notificaciones_estado
ON operation.notificaciones IS
'Gestiona automáticamente el ciclo de vida de las notificaciones.';


/*
============================================================
 21. FUNCIÓN DE TRIGGER:
     operation.fn_trg_gestionar_ejecucion_trabajo
============================================================
*/

CREATE OR REPLACE FUNCTION
operation.fn_trg_gestionar_ejecucion_trabajo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    IF NEW.estado = 'EJECUTANDO' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin := NULL;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado = 'COMPLETADA' THEN
        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );

        NEW.progreso := 100;
        NEW.mensaje_error := NULL;
    END IF;

    IF NEW.estado IN
    (
        'FALLIDA',
        'CANCELADA',
        'OMITIDA'
    ) THEN
        /*
         Un trabajo omitido puede no haber iniciado realmente,
         pero la estructura actual exige fecha_fin.
        */

        NEW.fecha_inicio :=
            COALESCE
            (
                NEW.fecha_inicio,
                NEW.fecha_solicitud,
                CURRENT_TIMESTAMP
            );

        NEW.fecha_fin :=
            COALESCE
            (
                NEW.fecha_fin,
                CURRENT_TIMESTAMP
            );
    END IF;

    IF NEW.estado = 'FALLIDA'
       AND NULLIF(TRIM(NEW.mensaje_error), '') IS NULL THEN
        RAISE EXCEPTION
            'Una ejecución FALLIDA requiere mensaje_error.'
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
operation.fn_trg_gestionar_ejecucion_trabajo() IS
'Gestiona automáticamente fechas, progreso y errores de las ejecuciones de trabajos programados.';


/*
============================================================
 22. TRIGGER:
     Gestión de ejecuciones de trabajos
============================================================
*/

DROP TRIGGER IF EXISTS
trg_ejecuciones_trabajo_estado
ON operation.ejecuciones_trabajo;

CREATE TRIGGER trg_ejecuciones_trabajo_estado
BEFORE INSERT OR UPDATE OF estado
ON operation.ejecuciones_trabajo
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_trg_gestionar_ejecucion_trabajo();

COMMENT ON TRIGGER
trg_ejecuciones_trabajo_estado
ON operation.ejecuciones_trabajo IS
'Completa fechas, progreso y errores según el estado de una ejecución de trabajo.';


/*
============================================================
 23. FUNCIÓN DE TRIGGER:
     audit.fn_trg_auditoria_generica
============================================================

 Propósito:
 Registrar automáticamente INSERT, UPDATE y DELETE para
 tablas seleccionadas.

 Configuración opcional mediante variables de sesión:

 SET LOCAL app.usuario_id = 'UUID';
 SET LOCAL app.direccion_ip = '127.0.0.1';
 SET LOCAL app.agente_usuario = 'FastAPI';
 SET LOCAL app.identificador_solicitud = 'request-id';

 Cuando no existen, los datos permanecen NULL.

 Protección:
 Se eliminan campos sensibles del JSON antes de guardar.
============================================================
*/

CREATE OR REPLACE FUNCTION audit.fn_trg_auditoria_generica()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_usuario_id              UUID;
    v_direccion_ip            INET;
    v_agente_usuario          TEXT;
    v_identificador_solicitud VARCHAR(150);

    v_anterior                JSONB;
    v_nuevo                   JSONB;
    v_campos                  JSONB;

    v_registro_id             TEXT;
BEGIN
    /*
     Las configuraciones app.* son opcionales y se obtienen
     con missing_ok = TRUE.
    */

    BEGIN
        v_usuario_id :=
            NULLIF
            (
                current_setting
                (
                    'app.usuario_id',
                    TRUE
                ),
                ''
            )::UUID;
    EXCEPTION
        WHEN invalid_text_representation THEN
            v_usuario_id := NULL;
    END;

    BEGIN
        v_direccion_ip :=
            NULLIF
            (
                current_setting
                (
                    'app.direccion_ip',
                    TRUE
                ),
                ''
            )::INET;
    EXCEPTION
        WHEN invalid_text_representation THEN
            v_direccion_ip := NULL;
    END;

    v_agente_usuario :=
        NULLIF
        (
            current_setting
            (
                'app.agente_usuario',
                TRUE
            ),
            ''
        );

    v_identificador_solicitud :=
        NULLIF
        (
            current_setting
            (
                'app.identificador_solicitud',
                TRUE
            ),
            ''
        );

    /*
     Convertir registros a JSON y eliminar información
     sensible.
    */

    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        v_anterior :=
            to_jsonb(OLD)
            - 'password_hash'
            - 'refresh_token_hash'
            - 'token'
            - 'access_token'
            - 'refresh_token'
            - 'secret'
            - 'api_key';
    END IF;

    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        v_nuevo :=
            to_jsonb(NEW)
            - 'password_hash'
            - 'refresh_token_hash'
            - 'token'
            - 'access_token'
            - 'refresh_token'
            - 'secret'
            - 'api_key';
    END IF;

    /*
     Obtener el identificador principal.

     Las tablas auditadas en este script utilizan id.
    */

    IF TG_OP = 'DELETE' THEN
        v_registro_id := to_jsonb(OLD) ->> 'id';
    ELSE
        v_registro_id := to_jsonb(NEW) ->> 'id';
    END IF;

    /*
     En UPDATE se registran únicamente los nombres de campos
     cuyo valor cambió.
    */

    IF TG_OP = 'UPDATE' THEN
        SELECT
            COALESCE
            (
                jsonb_agg(clave ORDER BY clave),
                '[]'::JSONB
            )
        INTO v_campos
        FROM
        (
            SELECT n.key AS clave
            FROM jsonb_each(v_nuevo) AS n
            JOIN jsonb_each(v_anterior) AS a
                ON a.key = n.key
            WHERE n.value IS DISTINCT FROM a.value
        ) AS cambios;

        /*
         Evitar generar auditoría cuando solamente cambió
         fecha_actualizacion.
        */

        IF v_campos = '["fecha_actualizacion"]'::JSONB
           OR v_campos = '[]'::JSONB THEN
            RETURN NEW;
        END IF;
    END IF;

    INSERT INTO audit.registros_auditoria
    (
        usuario_id,
        esquema_entidad,
        nombre_entidad,
        registro_id,
        accion,
        valores_anteriores,
        valores_nuevos,
        campos_modificados,
        direccion_ip,
        agente_usuario,
        origen,
        identificador_solicitud
    )
    VALUES
    (
        v_usuario_id,
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        v_registro_id,
        TG_OP,
        v_anterior,
        v_nuevo,
        v_campos,
        v_direccion_ip,
        v_agente_usuario,
        'BASE_DATOS',
        v_identificador_solicitud
    );

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
audit.fn_trg_auditoria_generica() IS
'Registra automáticamente operaciones INSERT, UPDATE y DELETE, eliminando campos sensibles antes de almacenar los valores.';


/*
============================================================
 24. TRIGGERS DE fecha_actualizacion
============================================================

 Se utiliza la función genérica creada en 12_functions.sql.
============================================================
*/

/*
------------------------------------------------------------
 app_auth.usuarios
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_usuarios_fecha_actualizacion
ON app_auth.usuarios;

CREATE TRIGGER trg_usuarios_fecha_actualizacion
BEFORE UPDATE
ON app_auth.usuarios
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 ai.modelos_ia
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_modelos_ia_fecha_actualizacion
ON ai.modelos_ia;

CREATE TRIGGER trg_modelos_ia_fecha_actualizacion
BEFORE UPDATE
ON ai.modelos_ia
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 profile.cuestionarios
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_cuestionarios_fecha_actualizacion
ON profile.cuestionarios;

CREATE TRIGGER trg_cuestionarios_fecha_actualizacion
BEFORE UPDATE
ON profile.cuestionarios
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 portfolio.listas_seguimiento
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_listas_seguimiento_fecha_actualizacion
ON portfolio.listas_seguimiento;

CREATE TRIGGER trg_listas_seguimiento_fecha_actualizacion
BEFORE UPDATE
ON portfolio.listas_seguimiento
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 portfolio.portafolios
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_portafolios_fecha_actualizacion
ON portfolio.portafolios;

CREATE TRIGGER trg_portafolios_fecha_actualizacion
BEFORE UPDATE
ON portfolio.portafolios
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 simulation.configuraciones
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_configuraciones_fecha_actualizacion
ON simulation.configuraciones;

CREATE TRIGGER trg_configuraciones_fecha_actualizacion
BEFORE UPDATE
ON simulation.configuraciones
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
------------------------------------------------------------
 operation.trabajos_programados
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_trabajos_programados_fecha_actualizacion
ON operation.trabajos_programados;

CREATE TRIGGER trg_trabajos_programados_fecha_actualizacion
BEFORE UPDATE
ON operation.trabajos_programados
FOR EACH ROW
EXECUTE FUNCTION
operation.fn_actualizar_fecha_actualizacion();


/*
============================================================
 25. TRIGGERS DE AUDITORÍA AUTOMÁTICA
============================================================

 Se auditan tablas de alto valor funcional.

 No se incluyen:
 - market.precios_historicos
 - market.indicadores_financieros
 - portfolio.valoraciones_portafolio
 - operation.control_procesos
 - audit.*
============================================================
*/

/*
------------------------------------------------------------
 app_auth.usuarios
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_usuarios
ON app_auth.usuarios;

CREATE TRIGGER trg_auditoria_usuarios
AFTER INSERT OR UPDATE OR DELETE
ON app_auth.usuarios
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 app_auth.roles
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_roles
ON app_auth.roles;

CREATE TRIGGER trg_auditoria_roles
AFTER INSERT OR UPDATE OR DELETE
ON app_auth.roles
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 profile.perfiles_riesgo
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_perfiles_riesgo
ON profile.perfiles_riesgo;

CREATE TRIGGER trg_auditoria_perfiles_riesgo
AFTER INSERT OR UPDATE OR DELETE
ON profile.perfiles_riesgo
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 portfolio.listas_seguimiento
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_listas_seguimiento
ON portfolio.listas_seguimiento;

CREATE TRIGGER trg_auditoria_listas_seguimiento
AFTER INSERT OR UPDATE OR DELETE
ON portfolio.listas_seguimiento
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 portfolio.portafolios
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_portafolios
ON portfolio.portafolios;

CREATE TRIGGER trg_auditoria_portafolios
AFTER INSERT OR UPDATE OR DELETE
ON portfolio.portafolios
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 simulation.configuraciones
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_configuraciones
ON simulation.configuraciones;

CREATE TRIGGER trg_auditoria_configuraciones
AFTER INSERT OR UPDATE OR DELETE
ON simulation.configuraciones
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 ai.recomendaciones
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_recomendaciones
ON ai.recomendaciones;

CREATE TRIGGER trg_auditoria_recomendaciones
AFTER INSERT OR UPDATE OR DELETE
ON ai.recomendaciones
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
------------------------------------------------------------
 operation.trabajos_programados
------------------------------------------------------------
*/

DROP TRIGGER IF EXISTS
trg_auditoria_trabajos_programados
ON operation.trabajos_programados;

CREATE TRIGGER trg_auditoria_trabajos_programados
AFTER INSERT OR UPDATE OR DELETE
ON operation.trabajos_programados
FOR EACH ROW
EXECUTE FUNCTION audit.fn_trg_auditoria_generica();


/*
============================================================
 26. COMENTARIOS DE TRIGGERS DE TIMESTAMP
============================================================
*/

COMMENT ON TRIGGER
trg_usuarios_fecha_actualizacion
ON app_auth.usuarios IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica un usuario.';

COMMENT ON TRIGGER
trg_modelos_ia_fecha_actualizacion
ON ai.modelos_ia IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica un modelo de IA.';

COMMENT ON TRIGGER
trg_cuestionarios_fecha_actualizacion
ON profile.cuestionarios IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica un cuestionario.';

COMMENT ON TRIGGER
trg_listas_seguimiento_fecha_actualizacion
ON portfolio.listas_seguimiento IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica una lista de seguimiento.';

COMMENT ON TRIGGER
trg_portafolios_fecha_actualizacion
ON portfolio.portafolios IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica un portafolio.';

COMMENT ON TRIGGER
trg_configuraciones_fecha_actualizacion
ON simulation.configuraciones IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica una configuración.';

COMMENT ON TRIGGER
trg_trabajos_programados_fecha_actualizacion
ON operation.trabajos_programados IS
'Actualiza automáticamente fecha_actualizacion cuando se modifica un trabajo programado.';


/*
============================================================
 27. CONFIRMACIÓN
============================================================
*/

COMMIT;