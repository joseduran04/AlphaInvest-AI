/*
============================================================
 AlphaInvest AI
 Script: 09_ai_analysis_tables.sql

 Propósito:
 Crear las tablas para registrar solicitudes de análisis,
 predicciones de activos, análisis de sentimiento,
 recomendaciones personalizadas y evidencias utilizadas
 por los modelos de inteligencia artificial.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql
 - 05_profile_tables.sql
 - 06_market_tables.sql
 - 07_portfolio_tables.sql
 - 08_simulation_tables.sql

 Esquema:
 - ai
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: ai.solicitudes_analisis
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.solicitudes_analisis
(
    id UUID
        CONSTRAINT pk_solicitudes_analisis
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    portafolio_id UUID NULL,

    perfil_riesgo_id UUID NULL,

    ejecucion_simulacion_id UUID NULL,

    tipo_analisis VARCHAR(50) NOT NULL,

    horizonte VARCHAR(30) NULL,

    fecha_referencia DATE NOT NULL
        DEFAULT CURRENT_DATE,

    parametros JSONB NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'PENDIENTE',

    porcentaje_progreso NUMERIC(7,4) NOT NULL
        DEFAULT 0,

    intentos_procesamiento INTEGER NOT NULL
        DEFAULT 0,

    fecha_solicitud TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_inicio TIMESTAMPTZ NULL,

    fecha_fin TIMESTAMPTZ NULL,

    mensaje_error TEXT NULL,

    identificador_proceso VARCHAR(150) NULL,

    fecha_expiracion TIMESTAMPTZ NULL,

    CONSTRAINT fk_solicitudes_analisis_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES app_auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_solicitudes_analisis_portafolio
        FOREIGN KEY (portafolio_id)
        REFERENCES portfolio.portafolios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_solicitudes_analisis_perfil
        FOREIGN KEY (perfil_riesgo_id)
        REFERENCES profile.perfiles_riesgo (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_solicitudes_analisis_simulacion
        FOREIGN KEY (ejecucion_simulacion_id)
        REFERENCES simulation.ejecuciones (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uq_solicitudes_analisis_proceso
        UNIQUE (identificador_proceso),

    CONSTRAINT ck_solicitudes_analisis_tipo
        CHECK
        (
            tipo_analisis IN
            (
                'ACTIVO',
                'PORTAFOLIO',
                'MERCADO',
                'SENTIMIENTO',
                'RECOMENDACION',
                'SIMULACION',
                'INTEGRAL'
            )
        ),

    CONSTRAINT ck_solicitudes_analisis_horizonte
        CHECK
        (
            horizonte IS NULL
            OR horizonte IN
            (
                'INTRADIA',
                'CORTO_PLAZO',
                'MEDIANO_PLAZO',
                'LARGO_PLAZO'
            )
        ),

    CONSTRAINT ck_solicitudes_analisis_estado
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

    CONSTRAINT ck_solicitudes_analisis_progreso
        CHECK
        (
            porcentaje_progreso BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_solicitudes_analisis_intentos
        CHECK
        (
            intentos_procesamiento >= 0
        ),

    CONSTRAINT ck_solicitudes_analisis_parametros
        CHECK
        (
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
        ),

    CONSTRAINT ck_solicitudes_analisis_fecha_inicio
        CHECK
        (
            fecha_inicio IS NULL
            OR fecha_inicio >= fecha_solicitud
        ),

    CONSTRAINT ck_solicitudes_analisis_fecha_fin
        CHECK
        (
            fecha_fin IS NULL
            OR
            (
                fecha_inicio IS NOT NULL
                AND fecha_fin >= fecha_inicio
            )
        ),

    CONSTRAINT ck_solicitudes_analisis_estado_inicio
        CHECK
        (
            estado = 'PENDIENTE'
            OR fecha_inicio IS NOT NULL
        ),

    CONSTRAINT ck_solicitudes_analisis_estado_fin
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

    CONSTRAINT ck_solicitudes_analisis_completada
        CHECK
        (
            estado <> 'COMPLETADA'
            OR porcentaje_progreso = 100
        ),

    CONSTRAINT ck_solicitudes_analisis_error
        CHECK
        (
            estado <> 'FALLIDA'
            OR NULLIF(TRIM(mensaje_error), '') IS NOT NULL
        ),

    CONSTRAINT ck_solicitudes_analisis_proceso
        CHECK
        (
            identificador_proceso IS NULL
            OR LENGTH(TRIM(identificador_proceso)) > 0
        ),

    CONSTRAINT ck_solicitudes_analisis_expiracion
        CHECK
        (
            fecha_expiracion IS NULL
            OR fecha_expiracion > fecha_solicitud
        )
);

COMMENT ON TABLE ai.solicitudes_analisis IS
'Solicitudes de procesamiento enviadas al motor de análisis de AlphaInvest AI.';

COMMENT ON COLUMN ai.solicitudes_analisis.portafolio_id IS
'Portafolio analizado cuando la solicitud se relaciona con una cartera virtual.';

COMMENT ON COLUMN ai.solicitudes_analisis.perfil_riesgo_id IS
'Perfil de riesgo utilizado para personalizar el análisis o recomendación.';

COMMENT ON COLUMN ai.solicitudes_analisis.ejecucion_simulacion_id IS
'Ejecución de simulación utilizada como contexto para el análisis.';

COMMENT ON COLUMN ai.solicitudes_analisis.tipo_analisis IS
'Tipo principal de procesamiento solicitado al motor de inteligencia artificial.';

COMMENT ON COLUMN ai.solicitudes_analisis.fecha_referencia IS
'Fecha de mercado utilizada como punto de referencia para el análisis.';

COMMENT ON COLUMN ai.solicitudes_analisis.identificador_proceso IS
'Identificador del trabajo externo ejecutado por el backend o una cola de tareas.';

COMMENT ON COLUMN ai.solicitudes_analisis.fecha_expiracion IS
'Fecha opcional después de la cual el resultado se considera desactualizado.';


/*
============================================================
 2. TABLA: ai.predicciones_activo
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.predicciones_activo
(
    id UUID
        CONSTRAINT pk_predicciones_activo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    solicitud_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    version_modelo_id UUID NOT NULL,

    fecha_base DATE NOT NULL,

    fecha_objetivo DATE NOT NULL,

    horizonte VARCHAR(30) NOT NULL,

    precio_base NUMERIC(20,8) NOT NULL,

    precio_predicho NUMERIC(20,8) NOT NULL,

    precio_minimo_estimado NUMERIC(20,8) NULL,

    precio_maximo_estimado NUMERIC(20,8) NULL,

    rendimiento_esperado_porcentaje NUMERIC(16,8) NULL,

    tendencia VARCHAR(20) NOT NULL,

    confianza NUMERIC(12,8) NOT NULL,

    probabilidad_alcista NUMERIC(12,8) NULL,

    probabilidad_neutral NUMERIC(12,8) NULL,

    probabilidad_bajista NUMERIC(12,8) NULL,

    caracteristicas_entrada JSONB NULL,

    salida_modelo JSONB NULL,

    fecha_generacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_predicciones_activo_solicitud
        FOREIGN KEY (solicitud_id)
        REFERENCES ai.solicitudes_analisis (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_predicciones_activo_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_predicciones_activo_version_modelo
        FOREIGN KEY (version_modelo_id)
        REFERENCES ai.versiones_modelo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_predicciones_solicitud_activo_fecha
        UNIQUE
        (
            solicitud_id,
            activo_id,
            fecha_objetivo
        ),

    CONSTRAINT ck_predicciones_fechas
        CHECK (fecha_objetivo > fecha_base),

    CONSTRAINT ck_predicciones_horizonte
        CHECK
        (
            horizonte IN
            (
                'INTRADIA',
                'CORTO_PLAZO',
                'MEDIANO_PLAZO',
                'LARGO_PLAZO'
            )
        ),

    CONSTRAINT ck_predicciones_precio_base
        CHECK (precio_base >= 0),

    CONSTRAINT ck_predicciones_precio_predicho
        CHECK (precio_predicho >= 0),

    CONSTRAINT ck_predicciones_precio_minimo
        CHECK
        (
            precio_minimo_estimado IS NULL
            OR precio_minimo_estimado >= 0
        ),

    CONSTRAINT ck_predicciones_precio_maximo
        CHECK
        (
            precio_maximo_estimado IS NULL
            OR precio_maximo_estimado >= 0
        ),

    CONSTRAINT ck_predicciones_intervalo
        CHECK
        (
            precio_minimo_estimado IS NULL
            OR precio_maximo_estimado IS NULL
            OR precio_maximo_estimado >= precio_minimo_estimado
        ),

    CONSTRAINT ck_predicciones_precio_en_intervalo
        CHECK
        (
            precio_minimo_estimado IS NULL
            OR precio_maximo_estimado IS NULL
            OR precio_predicho BETWEEN
                precio_minimo_estimado
                AND precio_maximo_estimado
        ),

    CONSTRAINT ck_predicciones_tendencia
        CHECK
        (
            tendencia IN
            (
                'ALCISTA',
                'NEUTRAL',
                'BAJISTA'
            )
        ),

    CONSTRAINT ck_predicciones_confianza
        CHECK
        (
            confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_predicciones_probabilidad_alcista
        CHECK
        (
            probabilidad_alcista IS NULL
            OR probabilidad_alcista BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_predicciones_probabilidad_neutral
        CHECK
        (
            probabilidad_neutral IS NULL
            OR probabilidad_neutral BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_predicciones_probabilidad_bajista
        CHECK
        (
            probabilidad_bajista IS NULL
            OR probabilidad_bajista BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_predicciones_probabilidades_completas
        CHECK
        (
            (
                probabilidad_alcista IS NULL
                AND probabilidad_neutral IS NULL
                AND probabilidad_bajista IS NULL
            )
            OR
            (
                probabilidad_alcista IS NOT NULL
                AND probabilidad_neutral IS NOT NULL
                AND probabilidad_bajista IS NOT NULL
            )
        ),

    CONSTRAINT ck_predicciones_probabilidades_suma
        CHECK
        (
            probabilidad_alcista IS NULL
            OR ABS
            (
                probabilidad_alcista
                + probabilidad_neutral
                + probabilidad_bajista
                - 1
            ) <= 0.0001
        ),

    CONSTRAINT ck_predicciones_caracteristicas_json
        CHECK
        (
            caracteristicas_entrada IS NULL
            OR jsonb_typeof(caracteristicas_entrada) = 'object'
        ),

    CONSTRAINT ck_predicciones_salida_json
        CHECK
        (
            salida_modelo IS NULL
            OR jsonb_typeof(salida_modelo) = 'object'
        )
);

COMMENT ON TABLE ai.predicciones_activo IS
'Predicciones generadas para activos financieros mediante modelos de inteligencia artificial.';

COMMENT ON COLUMN ai.predicciones_activo.fecha_base IS
'Fecha de la información de mercado utilizada para iniciar la predicción.';

COMMENT ON COLUMN ai.predicciones_activo.fecha_objetivo IS
'Fecha futura para la cual se genera el valor esperado.';

COMMENT ON COLUMN ai.predicciones_activo.precio_predicho IS
'Precio central estimado por el modelo.';

COMMENT ON COLUMN ai.predicciones_activo.precio_minimo_estimado IS
'Límite inferior estimado del intervalo de predicción.';

COMMENT ON COLUMN ai.predicciones_activo.precio_maximo_estimado IS
'Límite superior estimado del intervalo de predicción.';

COMMENT ON COLUMN ai.predicciones_activo.confianza IS
'Nivel de confianza normalizado entre cero y uno.';

COMMENT ON COLUMN ai.predicciones_activo.caracteristicas_entrada IS
'Variables de entrada o resumen de características utilizadas durante la inferencia.';

COMMENT ON COLUMN ai.predicciones_activo.salida_modelo IS
'Salida técnica adicional producida por el modelo.';


/*
============================================================
 3. TABLA: ai.analisis_sentimiento
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.analisis_sentimiento
(
    id UUID
        CONSTRAINT pk_analisis_sentimiento
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    solicitud_id UUID NOT NULL,

    activo_id UUID NULL,

    noticia_referencia_id UUID NULL,

    version_modelo_id UUID NOT NULL,

    tipo_fuente VARCHAR(30) NOT NULL,

    identificador_fuente VARCHAR(200) NULL,

    sentimiento VARCHAR(20) NOT NULL,

    puntuacion NUMERIC(12,8) NOT NULL,

    confianza NUMERIC(12,8) NOT NULL,

    probabilidad_positiva NUMERIC(12,8) NULL,

    probabilidad_neutral NUMERIC(12,8) NULL,

    probabilidad_negativa NUMERIC(12,8) NULL,

    relevancia NUMERIC(12,8) NULL,

    idioma VARCHAR(10) NULL,

    entidades_detectadas JSONB NULL,

    resumen TEXT NULL,

    fecha_contenido TIMESTAMPTZ NULL,

    fecha_analisis TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_analisis_sentimiento_solicitud
        FOREIGN KEY (solicitud_id)
        REFERENCES ai.solicitudes_analisis (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_analisis_sentimiento_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_analisis_sentimiento_noticia
        FOREIGN KEY (noticia_referencia_id)
        REFERENCES market.noticias_referencia (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_analisis_sentimiento_modelo
        FOREIGN KEY (version_modelo_id)
        REFERENCES ai.versiones_modelo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_analisis_sentimiento_solicitud_noticia
        UNIQUE
        (
            solicitud_id,
            noticia_referencia_id
        ),

    CONSTRAINT ck_analisis_sentimiento_tipo_fuente
        CHECK
        (
            tipo_fuente IN
            (
                'NOTICIA',
                'REPORTE',
                'COMUNICADO',
                'RED_SOCIAL',
                'TEXTO_USUARIO',
                'OTRO'
            )
        ),

    CONSTRAINT ck_analisis_sentimiento_identificador
        CHECK
        (
            identificador_fuente IS NULL
            OR LENGTH(TRIM(identificador_fuente)) > 0
        ),

    CONSTRAINT ck_analisis_sentimiento_clasificacion
        CHECK
        (
            sentimiento IN
            (
                'POSITIVO',
                'NEUTRAL',
                'NEGATIVO'
            )
        ),

    CONSTRAINT ck_analisis_sentimiento_puntuacion
        CHECK
        (
            puntuacion BETWEEN -1 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_confianza
        CHECK
        (
            confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_probabilidad_positiva
        CHECK
        (
            probabilidad_positiva IS NULL
            OR probabilidad_positiva BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_probabilidad_neutral
        CHECK
        (
            probabilidad_neutral IS NULL
            OR probabilidad_neutral BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_probabilidad_negativa
        CHECK
        (
            probabilidad_negativa IS NULL
            OR probabilidad_negativa BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_probabilidades_completas
        CHECK
        (
            (
                probabilidad_positiva IS NULL
                AND probabilidad_neutral IS NULL
                AND probabilidad_negativa IS NULL
            )
            OR
            (
                probabilidad_positiva IS NOT NULL
                AND probabilidad_neutral IS NOT NULL
                AND probabilidad_negativa IS NOT NULL
            )
        ),

    CONSTRAINT ck_analisis_sentimiento_probabilidades_suma
        CHECK
        (
            probabilidad_positiva IS NULL
            OR ABS
            (
                probabilidad_positiva
                + probabilidad_neutral
                + probabilidad_negativa
                - 1
            ) <= 0.0001
        ),

    CONSTRAINT ck_analisis_sentimiento_relevancia
        CHECK
        (
            relevancia IS NULL
            OR relevancia BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_analisis_sentimiento_idioma
        CHECK
        (
            idioma IS NULL
            OR LENGTH(TRIM(idioma)) BETWEEN 2 AND 10
        ),

    CONSTRAINT ck_analisis_sentimiento_entidades_json
        CHECK
        (
            entidades_detectadas IS NULL
            OR jsonb_typeof(entidades_detectadas) IN
            (
                'object',
                'array'
            )
        ),

    CONSTRAINT ck_analisis_sentimiento_resumen
        CHECK
        (
            resumen IS NULL
            OR LENGTH(TRIM(resumen)) > 0
        ),

    CONSTRAINT ck_analisis_sentimiento_noticia_fuente
        CHECK
        (
            tipo_fuente <> 'NOTICIA'
            OR
            (
                noticia_referencia_id IS NOT NULL
                OR identificador_fuente IS NOT NULL
            )
        )
);

COMMENT ON TABLE ai.analisis_sentimiento IS
'Resultados de clasificación de sentimiento obtenidos a partir de noticias, reportes u otros textos.';

COMMENT ON COLUMN ai.analisis_sentimiento.activo_id IS
'Activo financiero al que se asocia el contenido analizado.';

COMMENT ON COLUMN ai.analisis_sentimiento.noticia_referencia_id IS
'Referencia relacional de la noticia almacenada en el esquema market.';

COMMENT ON COLUMN ai.analisis_sentimiento.puntuacion IS
'Puntuación continua entre menos uno y uno, donde los valores negativos indican sentimiento negativo.';

COMMENT ON COLUMN ai.analisis_sentimiento.relevancia IS
'Nivel de relación del contenido con el activo o contexto analizado.';

COMMENT ON COLUMN ai.analisis_sentimiento.entidades_detectadas IS
'Empresas, activos, personas, países u otras entidades detectadas en el texto.';


/*
============================================================
 4. TABLA: ai.recomendaciones
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.recomendaciones
(
    id UUID
        CONSTRAINT pk_recomendaciones
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    solicitud_id UUID NOT NULL,

    usuario_id UUID NOT NULL,

    perfil_riesgo_id UUID NULL,

    portafolio_id UUID NULL,

    version_modelo_id UUID NOT NULL,

    tipo VARCHAR(40) NOT NULL,

    titulo VARCHAR(200) NOT NULL,

    resumen TEXT NOT NULL,

    justificacion TEXT NOT NULL,

    nivel_riesgo VARCHAR(30) NOT NULL,

    horizonte VARCHAR(30) NOT NULL,

    confianza NUMERIC(12,8) NOT NULL,

    prioridad INTEGER NOT NULL
        DEFAULT 1,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'GENERADA',

    advertencia TEXT NOT NULL,

    parametros JSONB NULL,

    fecha_generacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_expiracion TIMESTAMPTZ NULL,

    fecha_aceptacion TIMESTAMPTZ NULL,

    fecha_rechazo TIMESTAMPTZ NULL,

    CONSTRAINT fk_recomendaciones_solicitud
        FOREIGN KEY (solicitud_id)
        REFERENCES ai.solicitudes_analisis (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_recomendaciones_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES app_auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_recomendaciones_perfil
        FOREIGN KEY (perfil_riesgo_id)
        REFERENCES profile.perfiles_riesgo (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_recomendaciones_portafolio
        FOREIGN KEY (portafolio_id)
        REFERENCES portfolio.portafolios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_recomendaciones_version_modelo
        FOREIGN KEY (version_modelo_id)
        REFERENCES ai.versiones_modelo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_recomendaciones_tipo
        CHECK
        (
            tipo IN
            (
                'OBSERVAR',
                'COMPRAR_SIMULADO',
                'MANTENER',
                'REDUCIR',
                'VENDER_SIMULADO',
                'DIVERSIFICAR',
                'REBALANCEAR',
                'EVITAR'
            )
        ),

    CONSTRAINT ck_recomendaciones_titulo
        CHECK (LENGTH(TRIM(titulo)) > 0),

    CONSTRAINT ck_recomendaciones_resumen
        CHECK (LENGTH(TRIM(resumen)) > 0),

    CONSTRAINT ck_recomendaciones_justificacion
        CHECK (LENGTH(TRIM(justificacion)) > 0),

    CONSTRAINT ck_recomendaciones_nivel_riesgo
        CHECK
        (
            nivel_riesgo IN
            (
                'MUY_BAJO',
                'BAJO',
                'MEDIO',
                'ALTO',
                'MUY_ALTO'
            )
        ),

    CONSTRAINT ck_recomendaciones_horizonte
        CHECK
        (
            horizonte IN
            (
                'INTRADIA',
                'CORTO_PLAZO',
                'MEDIANO_PLAZO',
                'LARGO_PLAZO'
            )
        ),

    CONSTRAINT ck_recomendaciones_confianza
        CHECK
        (
            confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_recomendaciones_prioridad
        CHECK (prioridad > 0),

    CONSTRAINT ck_recomendaciones_estado
        CHECK
        (
            estado IN
            (
                'GENERADA',
                'MOSTRADA',
                'ACEPTADA',
                'RECHAZADA',
                'EXPIRADA',
                'RETIRADA'
            )
        ),

    CONSTRAINT ck_recomendaciones_advertencia
        CHECK (LENGTH(TRIM(advertencia)) > 0),

    CONSTRAINT ck_recomendaciones_parametros
        CHECK
        (
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
        ),

    CONSTRAINT ck_recomendaciones_expiracion
        CHECK
        (
            fecha_expiracion IS NULL
            OR fecha_expiracion > fecha_generacion
        ),

    CONSTRAINT ck_recomendaciones_aceptacion
        CHECK
        (
            fecha_aceptacion IS NULL
            OR fecha_aceptacion >= fecha_generacion
        ),

    CONSTRAINT ck_recomendaciones_rechazo
        CHECK
        (
            fecha_rechazo IS NULL
            OR fecha_rechazo >= fecha_generacion
        ),

    CONSTRAINT ck_recomendaciones_decision_unica
        CHECK
        (
            fecha_aceptacion IS NULL
            OR fecha_rechazo IS NULL
        ),

    CONSTRAINT ck_recomendaciones_estado_aceptada
        CHECK
        (
            estado <> 'ACEPTADA'
            OR
            (
                fecha_aceptacion IS NOT NULL
                AND fecha_rechazo IS NULL
            )
        ),

    CONSTRAINT ck_recomendaciones_estado_rechazada
        CHECK
        (
            estado <> 'RECHAZADA'
            OR
            (
                fecha_rechazo IS NOT NULL
                AND fecha_aceptacion IS NULL
            )
        )
);

COMMENT ON TABLE ai.recomendaciones IS
'Recomendaciones personalizadas generadas por los modelos de AlphaInvest AI.';

COMMENT ON COLUMN ai.recomendaciones.tipo IS
'Acción educativa o simulada sugerida por el sistema.';

COMMENT ON COLUMN ai.recomendaciones.nivel_riesgo IS
'Nivel de riesgo estimado de la recomendación.';

COMMENT ON COLUMN ai.recomendaciones.confianza IS
'Confianza del modelo en la recomendación, expresada entre cero y uno.';

COMMENT ON COLUMN ai.recomendaciones.advertencia IS
'Texto obligatorio que aclara que la recomendación no constituye asesoría financiera profesional.';

COMMENT ON COLUMN ai.recomendaciones.estado IS
'Estado del ciclo de vida de la recomendación.';


/*
============================================================
 5. TABLA: ai.recomendacion_activos
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.recomendacion_activos
(
    recomendacion_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    accion VARCHAR(30) NOT NULL,

    porcentaje_objetivo NUMERIC(12,8) NULL,

    precio_referencia NUMERIC(20,8) NULL,

    precio_objetivo NUMERIC(20,8) NULL,

    limite_perdida NUMERIC(20,8) NULL,

    confianza NUMERIC(12,8) NULL,

    prioridad INTEGER NOT NULL
        DEFAULT 1,

    justificacion TEXT NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_recomendacion_activos
        PRIMARY KEY
        (
            recomendacion_id,
            activo_id
        ),

    CONSTRAINT fk_recomendacion_activos_recomendacion
        FOREIGN KEY (recomendacion_id)
        REFERENCES ai.recomendaciones (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_recomendacion_activos_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_recomendacion_activos_accion
        CHECK
        (
            accion IN
            (
                'OBSERVAR',
                'AGREGAR',
                'MANTENER',
                'AUMENTAR',
                'REDUCIR',
                'RETIRAR',
                'EVITAR'
            )
        ),

    CONSTRAINT ck_recomendacion_activos_porcentaje
        CHECK
        (
            porcentaje_objetivo IS NULL
            OR porcentaje_objetivo BETWEEN 0 AND 100
        ),

    CONSTRAINT ck_recomendacion_activos_precio_referencia
        CHECK
        (
            precio_referencia IS NULL
            OR precio_referencia >= 0
        ),

    CONSTRAINT ck_recomendacion_activos_precio_objetivo
        CHECK
        (
            precio_objetivo IS NULL
            OR precio_objetivo >= 0
        ),

    CONSTRAINT ck_recomendacion_activos_limite_perdida
        CHECK
        (
            limite_perdida IS NULL
            OR limite_perdida >= 0
        ),

    CONSTRAINT ck_recomendacion_activos_confianza
        CHECK
        (
            confianza IS NULL
            OR confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_recomendacion_activos_prioridad
        CHECK (prioridad > 0),

    CONSTRAINT ck_recomendacion_activos_justificacion
        CHECK
        (
            justificacion IS NULL
            OR LENGTH(TRIM(justificacion)) > 0
        )
);

COMMENT ON TABLE ai.recomendacion_activos IS
'Activos financieros relacionados con una recomendación generada por el sistema.';

COMMENT ON COLUMN ai.recomendacion_activos.accion IS
'Acción específica sugerida para el activo dentro de una simulación o portafolio virtual.';

COMMENT ON COLUMN ai.recomendacion_activos.porcentaje_objetivo IS
'Participación porcentual sugerida dentro del portafolio virtual.';

COMMENT ON COLUMN ai.recomendacion_activos.precio_referencia IS
'Precio de mercado utilizado al momento de generar la recomendación.';

COMMENT ON COLUMN ai.recomendacion_activos.precio_objetivo IS
'Precio estimado o nivel de referencia esperado por el modelo.';

COMMENT ON COLUMN ai.recomendacion_activos.limite_perdida IS
'Nivel educativo de control de pérdida utilizado en simulaciones.';


/*
============================================================
 6. TABLA: ai.evidencias_analisis
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.evidencias_analisis
(
    id UUID
        CONSTRAINT pk_evidencias_analisis
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    solicitud_id UUID NOT NULL,

    recomendacion_id UUID NULL,

    prediccion_id UUID NULL,

    tipo_evidencia VARCHAR(40) NOT NULL,

    entidad_origen VARCHAR(100) NOT NULL,

    identificador_origen VARCHAR(200) NULL,

    descripcion TEXT NOT NULL,

    valor_numerico NUMERIC(24,8) NULL,

    unidad VARCHAR(30) NULL,

    peso NUMERIC(12,8) NULL,

    contribucion VARCHAR(20) NULL,

    datos JSONB NULL,

    fecha_evidencia TIMESTAMPTZ NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evidencias_analisis_solicitud
        FOREIGN KEY (solicitud_id)
        REFERENCES ai.solicitudes_analisis (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_evidencias_analisis_recomendacion
        FOREIGN KEY (recomendacion_id)
        REFERENCES ai.recomendaciones (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_evidencias_analisis_prediccion
        FOREIGN KEY (prediccion_id)
        REFERENCES ai.predicciones_activo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT ck_evidencias_analisis_tipo
        CHECK
        (
            tipo_evidencia IN
            (
                'PRECIO',
                'INDICADOR',
                'SENTIMIENTO',
                'FUNDAMENTAL',
                'PERFIL_RIESGO',
                'SIMULACION',
                'PORTAFOLIO',
                'MODELO',
                'OTRA'
            )
        ),

    CONSTRAINT ck_evidencias_analisis_entidad
        CHECK (LENGTH(TRIM(entidad_origen)) > 0),

    CONSTRAINT ck_evidencias_analisis_identificador
        CHECK
        (
            identificador_origen IS NULL
            OR LENGTH(TRIM(identificador_origen)) > 0
        ),

    CONSTRAINT ck_evidencias_analisis_descripcion
        CHECK (LENGTH(TRIM(descripcion)) > 0),

    CONSTRAINT ck_evidencias_analisis_unidad
        CHECK
        (
            unidad IS NULL
            OR LENGTH(TRIM(unidad)) > 0
        ),

    CONSTRAINT ck_evidencias_analisis_peso
        CHECK
        (
            peso IS NULL
            OR peso BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_evidencias_analisis_contribucion
        CHECK
        (
            contribucion IS NULL
            OR contribucion IN
            (
                'POSITIVA',
                'NEUTRAL',
                'NEGATIVA'
            )
        ),

    CONSTRAINT ck_evidencias_analisis_datos
        CHECK
        (
            datos IS NULL
            OR jsonb_typeof(datos) = 'object'
        ),

    CONSTRAINT ck_evidencias_analisis_destino
        CHECK
        (
            recomendacion_id IS NOT NULL
            OR prediccion_id IS NOT NULL
        )
);

COMMENT ON TABLE ai.evidencias_analisis IS
'Evidencias y factores utilizados para explicar predicciones y recomendaciones generadas por los modelos.';

COMMENT ON COLUMN ai.evidencias_analisis.entidad_origen IS
'Tabla, servicio, fuente o componente del que proviene la evidencia.';

COMMENT ON COLUMN ai.evidencias_analisis.identificador_origen IS
'Identificador externo o interno del registro utilizado como evidencia.';

COMMENT ON COLUMN ai.evidencias_analisis.peso IS
'Importancia relativa asignada a la evidencia, normalizada entre cero y uno.';

COMMENT ON COLUMN ai.evidencias_analisis.contribucion IS
'Dirección de la contribución de la evidencia sobre el resultado.';

COMMENT ON COLUMN ai.evidencias_analisis.datos IS
'Información adicional necesaria para explicar o reproducir la evidencia.';


/*
============================================================
 7. CONFIRMACIÓN
============================================================
*/

COMMIT;