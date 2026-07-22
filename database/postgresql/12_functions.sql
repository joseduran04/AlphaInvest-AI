/*
============================================================
 AlphaInvest AI
 Script: 12_functions.sql

 Propósito:
 Crear funciones reutilizables para automatizar reglas
 de negocio, validaciones, cálculos financieros básicos,
 auditoría y control de procesos.

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

 Esquemas utilizados:
 - audit
 - operation
 - portfolio
 - simulation

 Nota:
 Las funciones de tipo trigger se asociarán a las tablas
 correspondientes en 13_triggers.sql.
============================================================
*/

BEGIN;


/*
============================================================
 1. FUNCIÓN GENÉRICA:
    operation.fn_actualizar_fecha_actualizacion
============================================================

 Propósito:
 Asignar CURRENT_TIMESTAMP al campo fecha_actualizacion
 antes de actualizar un registro.

 Uso:
 Se utilizará mediante triggers BEFORE UPDATE.

 Requisito:
 La tabla que utilice esta función debe contener una
 columna llamada fecha_actualizacion.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_actualizar_fecha_actualizacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS
$$
BEGIN
    NEW.fecha_actualizacion := CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION
operation.fn_actualizar_fecha_actualizacion() IS
'Función genérica de trigger que actualiza automáticamente la columna fecha_actualizacion antes de modificar un registro.';


/*
============================================================
 2. FUNCIÓN:
    simulation.fn_total_distribucion
============================================================

 Propósito:
 Calcular la suma de los porcentajes asignados a los
 activos de una configuración de simulación.

 Retorno:
 NUMERIC con el porcentaje total.

 Ejemplo:
 SELECT simulation.fn_total_distribucion(:configuracion_id);
============================================================
*/

CREATE OR REPLACE FUNCTION simulation.fn_total_distribucion
(
    p_configuracion_id UUID
)
RETURNS NUMERIC(14,8)
LANGUAGE plpgsql
STABLE
AS
$$
DECLARE
    v_total NUMERIC(14,8);
BEGIN
    IF p_configuracion_id IS NULL THEN
        RAISE EXCEPTION
            'El identificador de configuración no puede ser nulo.'
            USING ERRCODE = '22004';
    END IF;

    IF NOT EXISTS
    (
        SELECT 1
        FROM simulation.configuraciones
        WHERE id = p_configuracion_id
    ) THEN
        RAISE EXCEPTION
            'No existe la configuración de simulación %.',
            p_configuracion_id
            USING ERRCODE = 'P0002';
    END IF;

    SELECT
        COALESCE
        (
            SUM(porcentaje_asignado),
            0
        )
    INTO v_total
    FROM simulation.configuracion_activos
    WHERE configuracion_id = p_configuracion_id;

    RETURN v_total;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_total_distribucion(UUID) IS
'Calcula el porcentaje total asignado a los activos de una configuración de simulación.';


/*
============================================================
 3. FUNCIÓN:
    simulation.fn_validar_distribucion
============================================================

 Propósito:
 Validar que una configuración tenga al menos un activo
 y que la suma de porcentajes sea igual a 100.

 Tolerancia:
 Se permite una diferencia máxima de 0.0001 para cubrir
 efectos de redondeo decimal.

 Retorno:
 TRUE  = distribución válida.
 FALSE = distribución inválida.
============================================================
*/

CREATE OR REPLACE FUNCTION simulation.fn_validar_distribucion
(
    p_configuracion_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS
$$
DECLARE
    v_total         NUMERIC(14,8);
    v_cantidad      INTEGER;
    v_capital       NUMERIC(24,8);
    v_total_montos  NUMERIC(24,8);
BEGIN
    IF p_configuracion_id IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT capital_inicial
    INTO v_capital
    FROM simulation.configuraciones
    WHERE id = p_configuracion_id;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    SELECT
        COUNT(*)::INTEGER,
        COALESCE(SUM(porcentaje_asignado), 0),
        COALESCE(SUM(monto_inicial), 0)
    INTO
        v_cantidad,
        v_total,
        v_total_montos
    FROM simulation.configuracion_activos
    WHERE configuracion_id = p_configuracion_id;

    IF v_cantidad = 0 THEN
        RETURN FALSE;
    END IF;

    IF ABS(v_total - 100) > 0.0001 THEN
        RETURN FALSE;
    END IF;

    /*
     Si se capturaron montos iniciales, la suma no deberá
     superar el capital inicial.

     No se exige igualdad porque los montos pueden calcularse
     posteriormente desde los porcentajes.
    */

    IF v_total_montos > 0
       AND v_total_montos > v_capital + 0.01 THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_validar_distribucion(UUID) IS
'Valida que una configuración tenga activos, que sus porcentajes sumen 100 y que los montos iniciales no superen el capital disponible.';


/*
============================================================
 4. FUNCIÓN:
    simulation.fn_exigir_distribucion_valida
============================================================

 Propósito:
 Interrumpir una operación cuando la distribución de una
 configuración no sea válida.

 Esta función será útil antes de:
 - Cambiar una configuración a estado LISTA.
 - Crear una ejecución.
 - Ejecutar una simulación.
============================================================
*/

CREATE OR REPLACE FUNCTION simulation.fn_exigir_distribucion_valida
(
    p_configuracion_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
STABLE
AS
$$
DECLARE
    v_total NUMERIC(14,8);
BEGIN
    IF NOT simulation.fn_validar_distribucion
    (
        p_configuracion_id
    ) THEN
        v_total :=
            simulation.fn_total_distribucion
            (
                p_configuracion_id
            );

        RAISE EXCEPTION
            'La configuración % tiene una distribución inválida. Porcentaje actual: %.',
            p_configuracion_id,
            v_total
            USING
                ERRCODE = '23514',
                HINT = 'La configuración debe incluir al menos un activo y los porcentajes deben sumar 100.';
    END IF;
END;
$$;

COMMENT ON FUNCTION
simulation.fn_exigir_distribucion_valida(UUID) IS
'Genera una excepción cuando la distribución de activos de una configuración de simulación no es válida.';


/*
============================================================
 5. FUNCIÓN:
    portfolio.fn_recalcular_posicion
============================================================

 Propósito:
 Recalcular los campos derivados de una posición virtual.

 Fórmulas:
 costo_total =
     cantidad * precio_promedio_compra

 valor_actual =
     cantidad * precio_actual

 ganancia_perdida =
     valor_actual - costo_total

 rendimiento_porcentaje =
     ganancia_perdida / costo_total * 100

 Comportamiento:
 - Si cantidad = 0, la posición se marca CERRADA.
 - Si cantidad > 0, la posición se mantiene ABIERTA.
 - Si no existe precio actual, valor, ganancia y rendimiento
   permanecen en NULL.
============================================================
*/

CREATE OR REPLACE FUNCTION portfolio.fn_recalcular_posicion
(
    p_posicion_id UUID
)
RETURNS portfolio.posiciones
LANGUAGE plpgsql
AS
$$
DECLARE
    v_posicion portfolio.posiciones%ROWTYPE;
BEGIN
    IF p_posicion_id IS NULL THEN
        RAISE EXCEPTION
            'El identificador de posición no puede ser nulo.'
            USING ERRCODE = '22004';
    END IF;

    SELECT *
    INTO v_posicion
    FROM portfolio.posiciones
    WHERE id = p_posicion_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe la posición %.',
            p_posicion_id
            USING ERRCODE = 'P0002';
    END IF;

    v_posicion.costo_total :=
        ROUND
        (
            v_posicion.cantidad
            * v_posicion.precio_promedio_compra,
            8
        );

    IF v_posicion.precio_actual IS NOT NULL THEN
        v_posicion.valor_actual :=
            ROUND
            (
                v_posicion.cantidad
                * v_posicion.precio_actual,
                8
            );

        v_posicion.ganancia_perdida :=
            ROUND
            (
                v_posicion.valor_actual
                - v_posicion.costo_total,
                8
            );

        IF v_posicion.costo_total > 0 THEN
            v_posicion.rendimiento_porcentaje :=
                ROUND
                (
                    (
                        v_posicion.ganancia_perdida
                        / v_posicion.costo_total
                    ) * 100,
                    8
                );
        ELSE
            v_posicion.rendimiento_porcentaje := NULL;
        END IF;
    ELSE
        v_posicion.valor_actual := NULL;
        v_posicion.ganancia_perdida := NULL;
        v_posicion.rendimiento_porcentaje := NULL;
    END IF;

    IF v_posicion.cantidad = 0 THEN
        v_posicion.estado := 'CERRADA';

        v_posicion.fecha_cierre :=
            COALESCE
            (
                v_posicion.fecha_cierre,
                CURRENT_TIMESTAMP
            );
    ELSE
        v_posicion.estado := 'ABIERTA';
        v_posicion.fecha_cierre := NULL;
    END IF;

    UPDATE portfolio.posiciones
    SET
        costo_total = v_posicion.costo_total,
        valor_actual = v_posicion.valor_actual,
        ganancia_perdida = v_posicion.ganancia_perdida,
        rendimiento_porcentaje =
            v_posicion.rendimiento_porcentaje,
        estado = v_posicion.estado,
        fecha_cierre = v_posicion.fecha_cierre,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = p_posicion_id
    RETURNING *
    INTO v_posicion;

    RETURN v_posicion;
END;
$$;

COMMENT ON FUNCTION
portfolio.fn_recalcular_posicion(UUID) IS
'Recalcula costo, valor, ganancia, rendimiento y estado de una posición virtual.';


/*
============================================================
 6. FUNCIÓN:
    portfolio.fn_actualizar_precio_posicion
============================================================

 Propósito:
 Asignar un nuevo precio de mercado y recalcular
 inmediatamente la posición.

 Retorno:
 Registro actualizado de portfolio.posiciones.
============================================================
*/

CREATE OR REPLACE FUNCTION portfolio.fn_actualizar_precio_posicion
(
    p_posicion_id UUID,
    p_precio_actual NUMERIC(20,8)
)
RETURNS portfolio.posiciones
LANGUAGE plpgsql
AS
$$
DECLARE
    v_posicion portfolio.posiciones%ROWTYPE;
BEGIN
    IF p_posicion_id IS NULL THEN
        RAISE EXCEPTION
            'El identificador de posición no puede ser nulo.'
            USING ERRCODE = '22004';
    END IF;

    IF p_precio_actual IS NULL OR p_precio_actual < 0 THEN
        RAISE EXCEPTION
            'El precio actual debe ser mayor o igual a cero.'
            USING ERRCODE = '22003';
    END IF;

    UPDATE portfolio.posiciones
    SET
        precio_actual = p_precio_actual,
        fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = p_posicion_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe la posición %.',
            p_posicion_id
            USING ERRCODE = 'P0002';
    END IF;

    v_posicion :=
        portfolio.fn_recalcular_posicion
        (
            p_posicion_id
        );

    RETURN v_posicion;
END;
$$;

COMMENT ON FUNCTION
portfolio.fn_actualizar_precio_posicion(UUID, NUMERIC) IS
'Actualiza el precio de mercado de una posición y recalcula sus métricas financieras.';


/*
============================================================
 7. FUNCIÓN:
    portfolio.fn_recalcular_portafolio
============================================================

 Propósito:
 Recalcular todas las posiciones de un portafolio.

 Retorno:
 Cantidad de posiciones procesadas.
============================================================
*/

CREATE OR REPLACE FUNCTION portfolio.fn_recalcular_portafolio
(
    p_portafolio_id UUID
)
RETURNS INTEGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_posicion_id UUID;
    v_procesadas  INTEGER := 0;
BEGIN
    IF p_portafolio_id IS NULL THEN
        RAISE EXCEPTION
            'El identificador de portafolio no puede ser nulo.'
            USING ERRCODE = '22004';
    END IF;

    IF NOT EXISTS
    (
        SELECT 1
        FROM portfolio.portafolios
        WHERE id = p_portafolio_id
    ) THEN
        RAISE EXCEPTION
            'No existe el portafolio %.',
            p_portafolio_id
            USING ERRCODE = 'P0002';
    END IF;

    FOR v_posicion_id IN
        SELECT id
        FROM portfolio.posiciones
        WHERE portafolio_id = p_portafolio_id
        ORDER BY fecha_apertura
    LOOP
        PERFORM
            portfolio.fn_recalcular_posicion
            (
                v_posicion_id
            );

        v_procesadas := v_procesadas + 1;
    END LOOP;

    RETURN v_procesadas;
END;
$$;

COMMENT ON FUNCTION
portfolio.fn_recalcular_portafolio(UUID) IS
'Recalcula todas las posiciones pertenecientes a un portafolio y devuelve la cantidad procesada.';


/*
============================================================
 8. FUNCIÓN:
    portfolio.fn_registrar_valoracion
============================================================

 Propósito:
 Calcular y registrar una valoración histórica de un
 portafolio virtual.

 Cálculos:
 valor_posiciones =
     suma de valor_actual de posiciones abiertas

 valor_total =
     saldo_efectivo + valor_posiciones

 ganancia_perdida =
     valor_total - capital_inicial

 rendimiento =
     ganancia_perdida / capital_inicial * 100

 Retorno:
 ID BIGINT de la valoración creada.
============================================================
*/

CREATE OR REPLACE FUNCTION portfolio.fn_registrar_valoracion
(
    p_portafolio_id UUID,
    p_fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    p_detalle JSONB DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS
$$
DECLARE
    v_portafolio       portfolio.portafolios%ROWTYPE;
    v_valor_posiciones NUMERIC(24,8);
    v_valor_total      NUMERIC(24,8);
    v_ganancia         NUMERIC(24,8);
    v_rendimiento      NUMERIC(16,8);
    v_valoracion_id    BIGINT;
    v_detalle          JSONB;
BEGIN
    IF p_portafolio_id IS NULL THEN
        RAISE EXCEPTION
            'El identificador de portafolio no puede ser nulo.'
            USING ERRCODE = '22004';
    END IF;

    IF p_fecha_hora IS NULL THEN
        RAISE EXCEPTION
            'La fecha de valoración no puede ser nula.'
            USING ERRCODE = '22004';
    END IF;

    IF p_detalle IS NOT NULL
       AND jsonb_typeof(p_detalle) <> 'object' THEN
        RAISE EXCEPTION
            'El detalle de la valoración debe ser un objeto JSON.'
            USING ERRCODE = '22023';
    END IF;

    SELECT *
    INTO v_portafolio
    FROM portfolio.portafolios
    WHERE id = p_portafolio_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION
            'No existe el portafolio %.',
            p_portafolio_id
            USING ERRCODE = 'P0002';
    END IF;

    PERFORM
        portfolio.fn_recalcular_portafolio
        (
            p_portafolio_id
        );

    SELECT
        COALESCE
        (
            SUM(valor_actual),
            0
        )
    INTO v_valor_posiciones
    FROM portfolio.posiciones
    WHERE portafolio_id = p_portafolio_id
      AND estado = 'ABIERTA'
      AND cantidad > 0;

    v_valor_total :=
        ROUND
        (
            v_portafolio.saldo_efectivo
            + v_valor_posiciones,
            8
        );

    v_ganancia :=
        ROUND
        (
            v_valor_total
            - v_portafolio.capital_inicial,
            8
        );

    IF v_portafolio.capital_inicial > 0 THEN
        v_rendimiento :=
            ROUND
            (
                (
                    v_ganancia
                    / v_portafolio.capital_inicial
                ) * 100,
                8
            );
    ELSE
        v_rendimiento := NULL;
    END IF;

    v_detalle :=
        COALESCE
        (
            p_detalle,
            '{}'::JSONB
        )
        ||
        jsonb_build_object
        (
            'posiciones_abiertas',
            (
                SELECT COUNT(*)
                FROM portfolio.posiciones
                WHERE portafolio_id = p_portafolio_id
                  AND estado = 'ABIERTA'
                  AND cantidad > 0
            ),
            'origen',
            COALESCE
            (
                p_detalle ->> 'origen',
                'FUNCION_POSTGRESQL'
            )
        );

    INSERT INTO portfolio.valoraciones_portafolio
    (
        portafolio_id,
        fecha_hora,
        saldo_efectivo,
        valor_posiciones,
        valor_total,
        capital_invertido,
        ganancia_perdida,
        rendimiento_porcentaje,
        moneda,
        detalle
    )
    VALUES
    (
        p_portafolio_id,
        p_fecha_hora,
        v_portafolio.saldo_efectivo,
        v_valor_posiciones,
        v_valor_total,
        v_portafolio.capital_inicial,
        v_ganancia,
        v_rendimiento,
        v_portafolio.moneda_base,
        v_detalle
    )
    RETURNING id
    INTO v_valoracion_id;

    RETURN v_valoracion_id;
END;
$$;

COMMENT ON FUNCTION
portfolio.fn_registrar_valoracion(UUID, TIMESTAMPTZ, JSONB) IS
'Recalcula las posiciones y registra una valoración histórica consolidada de un portafolio virtual.';


/*
============================================================
 9. FUNCIÓN:
    audit.fn_registrar_auditoria
============================================================

 Propósito:
 Insertar manualmente un evento en el historial de auditoría.

 Retorno:
 ID BIGINT del registro creado.

 Seguridad:
 El llamador no debe enviar contraseñas, tokens, secretos,
 cookies ni credenciales dentro de los objetos JSON.
============================================================
*/

CREATE OR REPLACE FUNCTION audit.fn_registrar_auditoria
(
    p_usuario_id UUID,
    p_esquema_entidad VARCHAR,
    p_nombre_entidad VARCHAR,
    p_registro_id VARCHAR,
    p_accion VARCHAR,
    p_valores_anteriores JSONB DEFAULT NULL,
    p_valores_nuevos JSONB DEFAULT NULL,
    p_campos_modificados JSONB DEFAULT NULL,
    p_direccion_ip INET DEFAULT NULL,
    p_agente_usuario TEXT DEFAULT NULL,
    p_origen VARCHAR DEFAULT 'APLICACION',
    p_identificador_solicitud VARCHAR DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS
$$
DECLARE
    v_auditoria_id BIGINT;
BEGIN
    IF NULLIF(TRIM(p_esquema_entidad), '') IS NULL THEN
        RAISE EXCEPTION
            'El esquema de la entidad es obligatorio.'
            USING ERRCODE = '22023';
    END IF;

    IF NULLIF(TRIM(p_nombre_entidad), '') IS NULL THEN
        RAISE EXCEPTION
            'El nombre de la entidad es obligatorio.'
            USING ERRCODE = '22023';
    END IF;

    IF p_accion NOT IN
    (
        'INSERT',
        'UPDATE',
        'DELETE',
        'LOGIN',
        'LOGOUT',
        'LECTURA',
        'EXPORTACION',
        'EJECUCION',
        'OTRA'
    ) THEN
        RAISE EXCEPTION
            'La acción de auditoría % no es válida.',
            p_accion
            USING ERRCODE = '22023';
    END IF;

    IF p_accion IN ('INSERT', 'UPDATE', 'DELETE')
       AND NULLIF(TRIM(p_registro_id), '') IS NULL THEN
        RAISE EXCEPTION
            'La acción % requiere un identificador de registro.',
            p_accion
            USING ERRCODE = '23514';
    END IF;

    IF p_valores_anteriores IS NOT NULL
       AND jsonb_typeof(p_valores_anteriores) <> 'object' THEN
        RAISE EXCEPTION
            'valores_anteriores debe ser un objeto JSON.'
            USING ERRCODE = '22023';
    END IF;

    IF p_valores_nuevos IS NOT NULL
       AND jsonb_typeof(p_valores_nuevos) <> 'object' THEN
        RAISE EXCEPTION
            'valores_nuevos debe ser un objeto JSON.'
            USING ERRCODE = '22023';
    END IF;

    IF p_campos_modificados IS NOT NULL
       AND jsonb_typeof(p_campos_modificados) <> 'array' THEN
        RAISE EXCEPTION
            'campos_modificados debe ser un arreglo JSON.'
            USING ERRCODE = '22023';
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
        p_usuario_id,
        TRIM(p_esquema_entidad),
        TRIM(p_nombre_entidad),
        NULLIF(TRIM(p_registro_id), ''),
        p_accion,
        p_valores_anteriores,
        p_valores_nuevos,
        p_campos_modificados,
        p_direccion_ip,
        p_agente_usuario,
        p_origen,
        NULLIF(TRIM(p_identificador_solicitud), '')
    )
    RETURNING id
    INTO v_auditoria_id;

    RETURN v_auditoria_id;
END;
$$;

COMMENT ON FUNCTION
audit.fn_registrar_auditoria
(
    UUID,
    VARCHAR,
    VARCHAR,
    VARCHAR,
    VARCHAR,
    JSONB,
    JSONB,
    JSONB,
    INET,
    TEXT,
    VARCHAR,
    VARCHAR
) IS
'Registra manualmente un evento de auditoría y devuelve el identificador generado.';


/*
============================================================
 10. FUNCIÓN:
     operation.fn_adquirir_bloqueo
============================================================

 Propósito:
 Adquirir un bloqueo lógico para un proceso.

 Comportamiento:
 - Inserta una nueva clave cuando no existe.
 - Reutiliza la fila si el bloqueo está liberado, cancelado
   o expirado.
 - Recupera un bloqueo ADQUIRIDO cuya fecha_expiracion ya
   haya vencido.
 - Devuelve FALSE si existe un bloqueo activo no vencido.

 Retorno:
 TRUE  = bloqueo adquirido.
 FALSE = recurso ocupado.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_adquirir_bloqueo
(
    p_tipo_proceso VARCHAR,
    p_clave_bloqueo VARCHAR,
    p_propietario VARCHAR,
    p_identificador_proceso VARCHAR,
    p_duracion INTERVAL,
    p_entidad_tipo VARCHAR DEFAULT NULL,
    p_entidad_id VARCHAR DEFAULT NULL,
    p_metadatos JSONB DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS
$$
DECLARE
    v_control_id UUID;
BEGIN
    IF p_tipo_proceso NOT IN
    (
        'SIMULACION',
        'ANALISIS_IA',
        'CARGA_MERCADO',
        'ENVIO_NOTIFICACION',
        'TRABAJO_PROGRAMADO',
        'MANTENIMIENTO',
        'OTRO'
    ) THEN
        RAISE EXCEPTION
            'El tipo de proceso % no es válido.',
            p_tipo_proceso
            USING ERRCODE = '22023';
    END IF;

    IF NULLIF(TRIM(p_clave_bloqueo), '') IS NULL THEN
        RAISE EXCEPTION
            'La clave de bloqueo es obligatoria.'
            USING ERRCODE = '22023';
    END IF;

    IF NULLIF(TRIM(p_propietario), '') IS NULL THEN
        RAISE EXCEPTION
            'El propietario del bloqueo es obligatorio.'
            USING ERRCODE = '22023';
    END IF;

    IF NULLIF(TRIM(p_identificador_proceso), '') IS NULL THEN
        RAISE EXCEPTION
            'El identificador del proceso es obligatorio.'
            USING ERRCODE = '22023';
    END IF;

    IF p_duracion IS NULL
       OR p_duracion <= INTERVAL '0 seconds' THEN
        RAISE EXCEPTION
            'La duración del bloqueo debe ser mayor a cero.'
            USING ERRCODE = '22023';
    END IF;

    IF
    (
        p_entidad_tipo IS NULL
        AND p_entidad_id IS NOT NULL
    )
    OR
    (
        p_entidad_tipo IS NOT NULL
        AND p_entidad_id IS NULL
    ) THEN
        RAISE EXCEPTION
            'entidad_tipo y entidad_id deben enviarse juntos.'
            USING ERRCODE = '22023';
    END IF;

    IF p_metadatos IS NOT NULL
       AND jsonb_typeof(p_metadatos) <> 'object' THEN
        RAISE EXCEPTION
            'Los metadatos deben ser un objeto JSON.'
            USING ERRCODE = '22023';
    END IF;

    /*
     Se utiliza INSERT ... ON CONFLICT para manejar de forma
     atómica dos trabajadores que intentan adquirir la misma
     clave al mismo tiempo.
    */

    INSERT INTO operation.control_procesos
    (
        tipo_proceso,
        entidad_tipo,
        entidad_id,
        clave_bloqueo,
        estado,
        propietario,
        identificador_proceso,
        fecha_adquisicion,
        fecha_expiracion,
        fecha_liberacion,
        latido_actualizacion,
        metadatos
    )
    VALUES
    (
        p_tipo_proceso,
        NULLIF(TRIM(p_entidad_tipo), ''),
        NULLIF(TRIM(p_entidad_id), ''),
        TRIM(p_clave_bloqueo),
        'ADQUIRIDO',
        TRIM(p_propietario),
        TRIM(p_identificador_proceso),
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP + p_duracion,
        NULL,
        CURRENT_TIMESTAMP,
        p_metadatos
    )
    ON CONFLICT (clave_bloqueo)
    DO UPDATE
    SET
        tipo_proceso = EXCLUDED.tipo_proceso,
        entidad_tipo = EXCLUDED.entidad_tipo,
        entidad_id = EXCLUDED.entidad_id,
        estado = 'ADQUIRIDO',
        propietario = EXCLUDED.propietario,
        identificador_proceso =
            EXCLUDED.identificador_proceso,
        fecha_adquisicion = CURRENT_TIMESTAMP,
        fecha_expiracion =
            CURRENT_TIMESTAMP + p_duracion,
        fecha_liberacion = NULL,
        latido_actualizacion = CURRENT_TIMESTAMP,
        metadatos = EXCLUDED.metadatos
    WHERE
        operation.control_procesos.estado IN
        (
            'LIBERADO',
            'EXPIRADO',
            'CANCELADO'
        )
        OR operation.control_procesos.fecha_expiracion
           <= CURRENT_TIMESTAMP
    RETURNING id
    INTO v_control_id;

    RETURN v_control_id IS NOT NULL;

EXCEPTION
    WHEN unique_violation THEN
        /*
         Puede ocurrir si el identificador_proceso ya está
         siendo utilizado por otro bloqueo.
        */
        RETURN FALSE;
END;
$$;

COMMENT ON FUNCTION
operation.fn_adquirir_bloqueo
(
    VARCHAR,
    VARCHAR,
    VARCHAR,
    VARCHAR,
    INTERVAL,
    VARCHAR,
    VARCHAR,
    JSONB
) IS
'Adquiere de forma atómica un bloqueo lógico nuevo, liberado o vencido. Devuelve false cuando el recurso continúa ocupado.';


/*
============================================================
 11. FUNCIÓN:
     operation.fn_actualizar_latido
============================================================

 Propósito:
 Confirmar que el proceso propietario de un bloqueo
 continúa activo.

 Opcionalmente puede extenderse su fecha de expiración.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_actualizar_latido
(
    p_clave_bloqueo VARCHAR,
    p_identificador_proceso VARCHAR,
    p_extension INTERVAL DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS
$$
DECLARE
    v_filas INTEGER;
BEGIN
    IF NULLIF(TRIM(p_clave_bloqueo), '') IS NULL
       OR NULLIF(TRIM(p_identificador_proceso), '') IS NULL THEN
        RETURN FALSE;
    END IF;

    IF p_extension IS NOT NULL
       AND p_extension <= INTERVAL '0 seconds' THEN
        RAISE EXCEPTION
            'La extensión del bloqueo debe ser mayor a cero.'
            USING ERRCODE = '22023';
    END IF;

    UPDATE operation.control_procesos
    SET
        latido_actualizacion = CURRENT_TIMESTAMP,
        fecha_expiracion =
            CASE
                WHEN p_extension IS NULL
                    THEN fecha_expiracion
                ELSE CURRENT_TIMESTAMP + p_extension
            END
    WHERE clave_bloqueo = TRIM(p_clave_bloqueo)
      AND identificador_proceso =
          TRIM(p_identificador_proceso)
      AND estado = 'ADQUIRIDO'
      AND fecha_expiracion > CURRENT_TIMESTAMP;

    GET DIAGNOSTICS v_filas = ROW_COUNT;

    RETURN v_filas = 1;
END;
$$;

COMMENT ON FUNCTION
operation.fn_actualizar_latido(VARCHAR, VARCHAR, INTERVAL) IS
'Actualiza la señal de actividad de un bloqueo adquirido y opcionalmente extiende su vigencia.';


/*
============================================================
 12. FUNCIÓN:
     operation.fn_liberar_bloqueo
============================================================

 Propósito:
 Liberar un bloqueo únicamente cuando la clave y el
 identificador coinciden con el proceso propietario.

 Retorno:
 TRUE cuando el bloqueo fue liberado.
 FALSE cuando no existe o pertenece a otro proceso.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_liberar_bloqueo
(
    p_clave_bloqueo VARCHAR,
    p_identificador_proceso VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS
$$
DECLARE
    v_filas INTEGER;
BEGIN
    IF NULLIF(TRIM(p_clave_bloqueo), '') IS NULL
       OR NULLIF(TRIM(p_identificador_proceso), '') IS NULL THEN
        RETURN FALSE;
    END IF;

    UPDATE operation.control_procesos
    SET
        estado = 'LIBERADO',
        fecha_liberacion = CURRENT_TIMESTAMP,
        latido_actualizacion = CURRENT_TIMESTAMP
    WHERE clave_bloqueo = TRIM(p_clave_bloqueo)
      AND identificador_proceso =
          TRIM(p_identificador_proceso)
      AND estado = 'ADQUIRIDO';

    GET DIAGNOSTICS v_filas = ROW_COUNT;

    RETURN v_filas = 1;
END;
$$;

COMMENT ON FUNCTION
operation.fn_liberar_bloqueo(VARCHAR, VARCHAR) IS
'Libera un bloqueo lógico únicamente cuando la clave y el identificador corresponden al proceso propietario.';


/*
============================================================
 13. FUNCIÓN:
     operation.fn_marcar_bloqueos_expirados
============================================================

 Propósito:
 Marcar como EXPIRADOS los bloqueos ADQUIRIDOS cuya fecha
 de expiración ya fue superada.

 Retorno:
 Cantidad de bloqueos actualizados.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_marcar_bloqueos_expirados()
RETURNS INTEGER
LANGUAGE plpgsql
AS
$$
DECLARE
    v_filas INTEGER;
BEGIN
    UPDATE operation.control_procesos
    SET
        estado = 'EXPIRADO',
        fecha_liberacion = CURRENT_TIMESTAMP
    WHERE estado = 'ADQUIRIDO'
      AND fecha_expiracion <= CURRENT_TIMESTAMP;

    GET DIAGNOSTICS v_filas = ROW_COUNT;

    RETURN v_filas;
END;
$$;

COMMENT ON FUNCTION
operation.fn_marcar_bloqueos_expirados() IS
'Marca como expirados los bloqueos adquiridos cuya fecha de vigencia ya terminó.';


/*
============================================================
 14. FUNCIÓN:
     operation.fn_cancelar_bloqueo
============================================================

 Propósito:
 Cancelar administrativamente un bloqueo activo.

 Esta función puede utilizarse cuando un administrador
 determina que un trabajo debe detenerse.
============================================================
*/

CREATE OR REPLACE FUNCTION operation.fn_cancelar_bloqueo
(
    p_clave_bloqueo VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS
$$
DECLARE
    v_filas INTEGER;
BEGIN
    IF NULLIF(TRIM(p_clave_bloqueo), '') IS NULL THEN
        RETURN FALSE;
    END IF;

    UPDATE operation.control_procesos
    SET
        estado = 'CANCELADO',
        fecha_liberacion = CURRENT_TIMESTAMP,
        latido_actualizacion = CURRENT_TIMESTAMP
    WHERE clave_bloqueo = TRIM(p_clave_bloqueo)
      AND estado = 'ADQUIRIDO';

    GET DIAGNOSTICS v_filas = ROW_COUNT;

    RETURN v_filas = 1;
END;
$$;

COMMENT ON FUNCTION
operation.fn_cancelar_bloqueo(VARCHAR) IS
'Cancela administrativamente un bloqueo lógico que continúa en estado adquirido.';


/*
============================================================
 15. CONFIRMACIÓN
============================================================
*/

COMMIT;