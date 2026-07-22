/*
============================================================
 AlphaInvest AI
 Script: 08_simulation_tables.sql

 Propósito:
 Crear las tablas destinadas a configurar, ejecutar
 y almacenar resultados de simulaciones financieras.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql
 - 06_market_tables.sql
 - 07_portfolio_tables.sql

 Esquema:
 - simulation
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: simulation.configuraciones
============================================================
*/

CREATE TABLE IF NOT EXISTS simulation.configuraciones
(
    id UUID
        CONSTRAINT pk_configuraciones_simulacion
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    portafolio_id UUID NULL,

    nombre VARCHAR(150) NOT NULL,

    descripcion TEXT NULL,

    tipo_simulacion VARCHAR(40) NOT NULL,

    capital_inicial NUMERIC(24,8) NOT NULL,

    moneda_base CHAR(3) NOT NULL
        DEFAULT 'USD',

    fecha_inicio DATE NOT NULL,

    fecha_fin DATE NOT NULL,

    aportacion_periodica NUMERIC(24,8) NOT NULL
        DEFAULT 0,

    frecuencia_aportacion VARCHAR(30) NULL,

    comision_porcentaje NUMERIC(12,8) NOT NULL
        DEFAULT 0,

    inflacion_anual NUMERIC(12,8) NULL,

    tasa_libre_riesgo NUMERIC(12,8) NULL,

    numero_escenarios INTEGER NOT NULL
        DEFAULT 1,

    semilla_aleatoria BIGINT NULL,

    parametros JSONB NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'BORRADOR',

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_configuraciones_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_configuraciones_portafolio
        FOREIGN KEY (portafolio_id)
        REFERENCES portfolio.portafolios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uq_configuraciones_usuario_nombre
        UNIQUE (usuario_id, nombre),

    CONSTRAINT ck_configuraciones_nombre
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_configuraciones_descripcion
        CHECK
        (
            descripcion IS NULL
            OR LENGTH(TRIM(descripcion)) > 0
        ),

    CONSTRAINT ck_configuraciones_tipo
        CHECK
        (
            tipo_simulacion IN
            (
                'HISTORICA',
                'MONTE_CARLO',
                'PROYECCION',
                'ESCENARIO'
            )
        ),

    CONSTRAINT ck_configuraciones_capital_inicial
        CHECK (capital_inicial > 0),

    CONSTRAINT ck_configuraciones_moneda
        CHECK
        (
            moneda_base = UPPER(moneda_base)
            AND moneda_base ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_configuraciones_fechas
        CHECK (fecha_fin > fecha_inicio),

    CONSTRAINT ck_configuraciones_aportacion
        CHECK (aportacion_periodica >= 0),

    CONSTRAINT ck_configuraciones_frecuencia_aportacion
        CHECK
        (
            (
                aportacion_periodica = 0
                AND frecuencia_aportacion IS NULL
            )
            OR
            (
                aportacion_periodica > 0
                AND frecuencia_aportacion IN
                (
                    'SEMANAL',
                    'QUINCENAL',
                    'MENSUAL',
                    'TRIMESTRAL',
                    'SEMESTRAL',
                    'ANUAL'
                )
            )
        ),

    CONSTRAINT ck_configuraciones_comision
        CHECK
        (
            comision_porcentaje BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_configuraciones_inflacion
        CHECK
        (
            inflacion_anual IS NULL
            OR inflacion_anual > -100
        ),

    CONSTRAINT ck_configuraciones_tasa_libre_riesgo
        CHECK
        (
            tasa_libre_riesgo IS NULL
            OR tasa_libre_riesgo > -100
        ),

    CONSTRAINT ck_configuraciones_numero_escenarios
        CHECK
        (
            numero_escenarios BETWEEN 1 AND 1000000
        ),

    CONSTRAINT ck_configuraciones_parametros_json
        CHECK
        (
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
        ),

    CONSTRAINT ck_configuraciones_estado
        CHECK
        (
            estado IN
            (
                'BORRADOR',
                'LISTA',
                'ARCHIVADA'
            )
        ),

    CONSTRAINT ck_configuraciones_monte_carlo
        CHECK
        (
            tipo_simulacion <> 'MONTE_CARLO'
            OR numero_escenarios > 1
        )
);

COMMENT ON TABLE simulation.configuraciones IS
'Parámetros definidos por el usuario para ejecutar una simulación financiera.';

COMMENT ON COLUMN simulation.configuraciones.portafolio_id IS
'Portafolio opcional utilizado como origen de la configuración.';

COMMENT ON COLUMN simulation.configuraciones.tipo_simulacion IS
'Metodología de simulación: histórica, Monte Carlo, proyección o escenario.';

COMMENT ON COLUMN simulation.configuraciones.aportacion_periodica IS
'Monto virtual agregado periódicamente durante la simulación.';

COMMENT ON COLUMN simulation.configuraciones.comision_porcentaje IS
'Porcentaje de comisión aplicado a las operaciones simuladas.';

COMMENT ON COLUMN simulation.configuraciones.inflacion_anual IS
'Porcentaje anual estimado de inflación.';

COMMENT ON COLUMN simulation.configuraciones.tasa_libre_riesgo IS
'Tasa anual utilizada para métricas como el índice de Sharpe.';

COMMENT ON COLUMN simulation.configuraciones.numero_escenarios IS
'Cantidad de escenarios generados, especialmente para simulaciones Monte Carlo.';

COMMENT ON COLUMN simulation.configuraciones.semilla_aleatoria IS
'Semilla opcional para reproducir resultados pseudoaleatorios.';


/*
============================================================
 2. TABLA: simulation.configuracion_activos
============================================================
*/

CREATE TABLE IF NOT EXISTS simulation.configuracion_activos
(
    configuracion_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    porcentaje_asignado NUMERIC(12,8) NOT NULL,

    monto_inicial NUMERIC(24,8) NULL,

    precio_inicial NUMERIC(20,8) NULL,

    orden INTEGER NOT NULL,

    parametros JSONB NULL,

    fecha_agregado TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_configuracion_activos
        PRIMARY KEY (configuracion_id, activo_id),

    CONSTRAINT fk_configuracion_activos_configuracion
        FOREIGN KEY (configuracion_id)
        REFERENCES simulation.configuraciones (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_configuracion_activos_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_configuracion_activos_orden
        UNIQUE (configuracion_id, orden),

    CONSTRAINT ck_configuracion_activos_porcentaje
        CHECK
        (
            porcentaje_asignado > 0
            AND porcentaje_asignado <= 100
        ),

    CONSTRAINT ck_configuracion_activos_monto
        CHECK
        (
            monto_inicial IS NULL
            OR monto_inicial >= 0
        ),

    CONSTRAINT ck_configuracion_activos_precio
        CHECK
        (
            precio_inicial IS NULL
            OR precio_inicial >= 0
        ),

    CONSTRAINT ck_configuracion_activos_orden
        CHECK (orden > 0),

    CONSTRAINT ck_configuracion_activos_parametros
        CHECK
        (
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
        )
);

COMMENT ON TABLE simulation.configuracion_activos IS
'Distribución de activos incluida en una configuración de simulación.';

COMMENT ON COLUMN simulation.configuracion_activos.porcentaje_asignado IS
'Porcentaje del capital asignado al activo dentro de la simulación.';

COMMENT ON COLUMN simulation.configuracion_activos.monto_inicial IS
'Monto calculado o especificado para el activo al inicio de la simulación.';

COMMENT ON COLUMN simulation.configuracion_activos.precio_inicial IS
'Precio utilizado para adquirir virtualmente el activo al inicio.';


/*
============================================================
 3. TABLA: simulation.ejecuciones
============================================================
*/

CREATE TABLE IF NOT EXISTS simulation.ejecuciones
(
    id UUID
        CONSTRAINT pk_ejecuciones_simulacion
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    configuracion_id UUID NOT NULL,

    usuario_id UUID NOT NULL,

    version_modelo_id UUID NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'PENDIENTE',

    porcentaje_progreso NUMERIC(7,4) NOT NULL
        DEFAULT 0,

    fecha_solicitud TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_inicio TIMESTAMPTZ NULL,

    fecha_fin TIMESTAMPTZ NULL,

    mensaje_error TEXT NULL,

    parametros_ejecucion JSONB NULL,

    identificador_proceso VARCHAR(150) NULL,

    CONSTRAINT fk_ejecuciones_configuracion
        FOREIGN KEY (configuracion_id)
        REFERENCES simulation.configuraciones (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_ejecuciones_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_ejecuciones_version_modelo
        FOREIGN KEY (version_modelo_id)
        REFERENCES ai.versiones_modelo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_ejecuciones_identificador_proceso
        UNIQUE (identificador_proceso),

    CONSTRAINT ck_ejecuciones_estado
        CHECK
        (
            estado IN
            (
                'PENDIENTE',
                'EJECUTANDO',
                'COMPLETADA',
                'FALLIDA',
                'CANCELADA'
            )
        ),

    CONSTRAINT ck_ejecuciones_progreso
        CHECK
        (
            porcentaje_progreso BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_ejecuciones_fechas
        CHECK
        (
            fecha_inicio IS NULL
            OR fecha_inicio >= fecha_solicitud
        ),

    CONSTRAINT ck_ejecuciones_fecha_fin
        CHECK
        (
            fecha_fin IS NULL
            OR
            (
                fecha_inicio IS NOT NULL
                AND fecha_fin >= fecha_inicio
            )
        ),

    CONSTRAINT ck_ejecuciones_estado_inicio
        CHECK
        (
            estado = 'PENDIENTE'
            OR fecha_inicio IS NOT NULL
        ),

    CONSTRAINT ck_ejecuciones_estado_fin
        CHECK
        (
            estado NOT IN
            (
                'COMPLETADA',
                'FALLIDA',
                'CANCELADA'
            )
            OR fecha_fin IS NOT NULL
        ),

    CONSTRAINT ck_ejecuciones_completada_progreso
        CHECK
        (
            estado <> 'COMPLETADA'
            OR porcentaje_progreso = 100
        ),

    CONSTRAINT ck_ejecuciones_error
        CHECK
        (
            estado <> 'FALLIDA'
            OR NULLIF(TRIM(mensaje_error), '') IS NOT NULL
        ),

    CONSTRAINT ck_ejecuciones_parametros_json
        CHECK
        (
            parametros_ejecucion IS NULL
            OR jsonb_typeof(parametros_ejecucion) = 'object'
        ),

    CONSTRAINT ck_ejecuciones_identificador
        CHECK
        (
            identificador_proceso IS NULL
            OR LENGTH(TRIM(identificador_proceso)) > 0
        )
);

COMMENT ON TABLE simulation.ejecuciones IS
'Historial de ejecuciones realizadas a partir de una configuración de simulación.';

COMMENT ON COLUMN simulation.ejecuciones.version_modelo_id IS
'Versión del modelo de IA utilizada, cuando la simulación depende de predicciones.';

COMMENT ON COLUMN simulation.ejecuciones.porcentaje_progreso IS
'Porcentaje de avance de la ejecución, entre cero y cien.';

COMMENT ON COLUMN simulation.ejecuciones.identificador_proceso IS
'Identificador externo del trabajo ejecutado por un servicio o cola de tareas.';

COMMENT ON COLUMN simulation.ejecuciones.mensaje_error IS
'Descripción del error cuando la ejecución termina con estado FALLIDA.';


/*
============================================================
 4. TABLA: simulation.resultados
============================================================
*/

CREATE TABLE IF NOT EXISTS simulation.resultados
(
    id UUID
        CONSTRAINT pk_resultados_simulacion
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    ejecucion_id UUID NOT NULL,

    capital_inicial NUMERIC(24,8) NOT NULL,

    aportaciones_totales NUMERIC(24,8) NOT NULL
        DEFAULT 0,

    capital_final NUMERIC(24,8) NOT NULL,

    ganancia_perdida NUMERIC(24,8) NOT NULL,

    rendimiento_total_porcentaje NUMERIC(16,8) NOT NULL,

    rendimiento_anualizado_porcentaje NUMERIC(16,8) NULL,

    volatilidad_anualizada NUMERIC(16,8) NULL,

    indice_sharpe NUMERIC(16,8) NULL,

    maximo_drawdown_porcentaje NUMERIC(16,8) NULL,

    valor_en_riesgo NUMERIC(24,8) NULL,

    nivel_confianza_var NUMERIC(12,8) NULL,

    mejor_escenario NUMERIC(24,8) NULL,

    peor_escenario NUMERIC(24,8) NULL,

    mediana_escenarios NUMERIC(24,8) NULL,

    probabilidad_ganancia NUMERIC(12,8) NULL,

    moneda CHAR(3) NOT NULL,

    resumen JSONB NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_resultados_ejecucion
        FOREIGN KEY (ejecucion_id)
        REFERENCES simulation.ejecuciones (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_resultados_ejecucion
        UNIQUE (ejecucion_id),

    CONSTRAINT ck_resultados_capital_inicial
        CHECK (capital_inicial > 0),

    CONSTRAINT ck_resultados_aportaciones
        CHECK (aportaciones_totales >= 0),

    CONSTRAINT ck_resultados_capital_final
        CHECK (capital_final >= 0),

    CONSTRAINT ck_resultados_volatilidad
        CHECK
        (
            volatilidad_anualizada IS NULL
            OR volatilidad_anualizada >= 0
        ),

    CONSTRAINT ck_resultados_drawdown
        CHECK
        (
            maximo_drawdown_porcentaje IS NULL
            OR maximo_drawdown_porcentaje BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_resultados_var
        CHECK
        (
            valor_en_riesgo IS NULL
            OR valor_en_riesgo >= 0
        ),

    CONSTRAINT ck_resultados_nivel_confianza
        CHECK
        (
            nivel_confianza_var IS NULL
            OR nivel_confianza_var BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_resultados_probabilidad_ganancia
        CHECK
        (
            probabilidad_ganancia IS NULL
            OR probabilidad_ganancia BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_resultados_escenarios
        CHECK
        (
            mejor_escenario IS NULL
            OR peor_escenario IS NULL
            OR mejor_escenario >= peor_escenario
        ),

    CONSTRAINT ck_resultados_mediana_escenarios
        CHECK
        (
            mediana_escenarios IS NULL
            OR mejor_escenario IS NULL
            OR peor_escenario IS NULL
            OR mediana_escenarios BETWEEN peor_escenario AND mejor_escenario
        ),

    CONSTRAINT ck_resultados_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_resultados_resumen_json
        CHECK
        (
            resumen IS NULL
            OR jsonb_typeof(resumen) = 'object'
        )
);

COMMENT ON TABLE simulation.resultados IS
'Resultado general consolidado de una ejecución de simulación.';

COMMENT ON COLUMN simulation.resultados.capital_final IS
'Valor virtual final obtenido al concluir el periodo simulado.';

COMMENT ON COLUMN simulation.resultados.ganancia_perdida IS
'Diferencia entre el capital final y el capital total aportado.';

COMMENT ON COLUMN simulation.resultados.rendimiento_total_porcentaje IS
'Rendimiento acumulado durante todo el periodo de simulación.';

COMMENT ON COLUMN simulation.resultados.indice_sharpe IS
'Rendimiento ajustado por riesgo respecto de la tasa libre de riesgo.';

COMMENT ON COLUMN simulation.resultados.maximo_drawdown_porcentaje IS
'Mayor caída porcentual desde un máximo hasta un mínimo posterior.';

COMMENT ON COLUMN simulation.resultados.valor_en_riesgo IS
'Estimación de pérdida potencial para un nivel de confianza determinado.';

COMMENT ON COLUMN simulation.resultados.probabilidad_ganancia IS
'Proporción de escenarios cuyo capital final supera el capital total aportado.';


/*
============================================================
 5. TABLA: simulation.resultados_activo
============================================================
*/

CREATE TABLE IF NOT EXISTS simulation.resultados_activo
(
    id UUID
        CONSTRAINT pk_resultados_activo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    resultado_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    porcentaje_asignado NUMERIC(12,8) NOT NULL,

    capital_asignado NUMERIC(24,8) NOT NULL,

    cantidad_inicial NUMERIC(24,8) NULL,

    precio_inicial NUMERIC(20,8) NOT NULL,

    precio_final NUMERIC(20,8) NOT NULL,

    valor_final NUMERIC(24,8) NOT NULL,

    ganancia_perdida NUMERIC(24,8) NOT NULL,

    rendimiento_porcentaje NUMERIC(16,8) NOT NULL,

    volatilidad NUMERIC(16,8) NULL,

    maximo_drawdown_porcentaje NUMERIC(16,8) NULL,

    detalle JSONB NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_resultados_activo_resultado
        FOREIGN KEY (resultado_id)
        REFERENCES simulation.resultados (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_resultados_activo_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_resultados_activo
        UNIQUE (resultado_id, activo_id),

    CONSTRAINT ck_resultados_activo_porcentaje
        CHECK
        (
            porcentaje_asignado > 0
            AND porcentaje_asignado <= 100
        ),

    CONSTRAINT ck_resultados_activo_capital
        CHECK (capital_asignado >= 0),

    CONSTRAINT ck_resultados_activo_cantidad
        CHECK
        (
            cantidad_inicial IS NULL
            OR cantidad_inicial >= 0
        ),

    CONSTRAINT ck_resultados_activo_precio_inicial
        CHECK (precio_inicial >= 0),

    CONSTRAINT ck_resultados_activo_precio_final
        CHECK (precio_final >= 0),

    CONSTRAINT ck_resultados_activo_valor_final
        CHECK (valor_final >= 0),

    CONSTRAINT ck_resultados_activo_volatilidad
        CHECK
        (
            volatilidad IS NULL
            OR volatilidad >= 0
        ),

    CONSTRAINT ck_resultados_activo_drawdown
        CHECK
        (
            maximo_drawdown_porcentaje IS NULL
            OR maximo_drawdown_porcentaje BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_resultados_activo_detalle_json
        CHECK
        (
            detalle IS NULL
            OR jsonb_typeof(detalle) = 'object'
        )
);

COMMENT ON TABLE simulation.resultados_activo IS
'Resultado individual de cada activo incluido en una simulación.';

COMMENT ON COLUMN simulation.resultados_activo.capital_asignado IS
'Monto inicial virtual asignado al activo.';

COMMENT ON COLUMN simulation.resultados_activo.valor_final IS
'Valor virtual del activo al finalizar la simulación.';

COMMENT ON COLUMN simulation.resultados_activo.ganancia_perdida IS
'Diferencia entre el valor final y el capital asignado.';

COMMENT ON COLUMN simulation.resultados_activo.detalle IS
'Información adicional, como series, percentiles o métricas específicas.';


/*
============================================================
 6. CONFIRMACIÓN
============================================================
*/

COMMIT;