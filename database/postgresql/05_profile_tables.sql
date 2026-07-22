/*
============================================================
 AlphaInvest AI
 Script: 05_profile_tables.sql

 Propósito:
 Crear las tablas para cuestionarios, preguntas,
 evaluaciones y perfiles de riesgo de los usuarios.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 04_ai_base_tables.sql

 Esquema:
 - profile
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: profile.cuestionarios
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.cuestionarios
(
    id UUID
        CONSTRAINT pk_cuestionarios
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    nombre VARCHAR(150) NOT NULL,

    descripcion TEXT NULL,

    version VARCHAR(30) NOT NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'BORRADOR',

    fecha_publicacion TIMESTAMPTZ NULL,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_cuestionarios_nombre_version
        UNIQUE (nombre, version),

    CONSTRAINT ck_cuestionarios_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_cuestionarios_version_no_vacia
        CHECK (LENGTH(TRIM(version)) > 0),

    CONSTRAINT ck_cuestionarios_estado
        CHECK
        (
            estado IN
            (
                'BORRADOR',
                'PUBLICADO',
                'INACTIVO'
            )
        ),

    CONSTRAINT ck_cuestionarios_publicacion
        CHECK
        (
            estado <> 'PUBLICADO'
            OR fecha_publicacion IS NOT NULL
        )
);

COMMENT ON TABLE profile.cuestionarios IS
'Versiones de los cuestionarios utilizados para evaluar el perfil de riesgo.';

COMMENT ON COLUMN profile.cuestionarios.version IS
'Versión funcional del cuestionario, por ejemplo 1.0.0.';

COMMENT ON COLUMN profile.cuestionarios.estado IS
'Estado del cuestionario: BORRADOR, PUBLICADO o INACTIVO.';

COMMENT ON COLUMN profile.cuestionarios.fecha_publicacion IS
'Fecha a partir de la cual el cuestionario puede ser contestado.';


/*
============================================================
 2. TABLA: profile.preguntas
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.preguntas
(
    id UUID
        CONSTRAINT pk_preguntas
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    cuestionario_id UUID NOT NULL,

    texto TEXT NOT NULL,

    tipo VARCHAR(30) NOT NULL,

    orden INTEGER NOT NULL,

    ponderacion NUMERIC(10,4) NOT NULL
        DEFAULT 1,

    obligatoria BOOLEAN NOT NULL
        DEFAULT TRUE,

    activa BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_preguntas_cuestionario
        FOREIGN KEY (cuestionario_id)
        REFERENCES profile.cuestionarios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_preguntas_cuestionario_orden
        UNIQUE (cuestionario_id, orden),

    CONSTRAINT ck_preguntas_texto_no_vacio
        CHECK (LENGTH(TRIM(texto)) > 0),

    CONSTRAINT ck_preguntas_tipo
        CHECK
        (
            tipo IN
            (
                'OPCION_UNICA',
                'OPCION_MULTIPLE',
                'NUMERICA',
                'TEXTO'
            )
        ),

    CONSTRAINT ck_preguntas_orden
        CHECK (orden > 0),

    CONSTRAINT ck_preguntas_ponderacion
        CHECK (ponderacion >= 0)
);

COMMENT ON TABLE profile.preguntas IS
'Preguntas pertenecientes a una versión específica de cuestionario.';

COMMENT ON COLUMN profile.preguntas.tipo IS
'Tipo de respuesta esperado para la pregunta.';

COMMENT ON COLUMN profile.preguntas.orden IS
'Posición de la pregunta dentro del cuestionario.';

COMMENT ON COLUMN profile.preguntas.ponderacion IS
'Peso de la pregunta dentro del cálculo de riesgo.';


/*
============================================================
 3. TABLA: profile.opciones_respuesta
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.opciones_respuesta
(
    id UUID
        CONSTRAINT pk_opciones_respuesta
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    pregunta_id UUID NOT NULL,

    texto VARCHAR(500) NOT NULL,

    valor NUMERIC(10,4) NOT NULL,

    orden INTEGER NOT NULL,

    activa BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_opciones_respuesta_pregunta
        FOREIGN KEY (pregunta_id)
        REFERENCES profile.preguntas (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_opciones_respuesta_pregunta_orden
        UNIQUE (pregunta_id, orden),

    CONSTRAINT ck_opciones_respuesta_texto_no_vacio
        CHECK (LENGTH(TRIM(texto)) > 0),

    CONSTRAINT ck_opciones_respuesta_orden
        CHECK (orden > 0)
);

COMMENT ON TABLE profile.opciones_respuesta IS
'Opciones disponibles para las preguntas cerradas del cuestionario.';

COMMENT ON COLUMN profile.opciones_respuesta.valor IS
'Valor utilizado para calcular la puntuación del perfil de riesgo.';


/*
============================================================
 4. TABLA: profile.evaluaciones_riesgo
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.evaluaciones_riesgo
(
    id UUID
        CONSTRAINT pk_evaluaciones_riesgo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    cuestionario_id UUID NOT NULL,

    version_cuestionario VARCHAR(30) NOT NULL,

    puntuacion_total NUMERIC(12,4) NOT NULL,

    clasificacion VARCHAR(40) NOT NULL,

    confianza NUMERIC(12,8) NULL,

    metodo_clasificacion VARCHAR(50) NOT NULL,

    version_modelo_id UUID NULL,

    fecha_evaluacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'COMPLETADA',

    detalle_calculo JSONB NULL,

    CONSTRAINT fk_evaluaciones_riesgo_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_evaluaciones_riesgo_cuestionario
        FOREIGN KEY (cuestionario_id)
        REFERENCES profile.cuestionarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_evaluaciones_riesgo_version_modelo
        FOREIGN KEY (version_modelo_id)
        REFERENCES ai.versiones_modelo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_evaluaciones_version_no_vacia
        CHECK (LENGTH(TRIM(version_cuestionario)) > 0),

    CONSTRAINT ck_evaluaciones_puntuacion_total
        CHECK (puntuacion_total >= 0),

    CONSTRAINT ck_evaluaciones_clasificacion_no_vacia
        CHECK (LENGTH(TRIM(clasificacion)) > 0),

    CONSTRAINT ck_evaluaciones_confianza
        CHECK
        (
            confianza IS NULL
            OR confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_evaluaciones_metodo
        CHECK
        (
            metodo_clasificacion IN
            (
                'REGLAS',
                'INTELIGENCIA_ARTIFICIAL',
                'HIBRIDO'
            )
        ),

    CONSTRAINT ck_evaluaciones_modelo_metodo
        CHECK
        (
            metodo_clasificacion = 'REGLAS'
            OR version_modelo_id IS NOT NULL
        ),

    CONSTRAINT ck_evaluaciones_estado
        CHECK
        (
            estado IN
            (
                'COMPLETADA',
                'INVALIDA',
                'CANCELADA'
            )
        ),

    CONSTRAINT ck_evaluaciones_detalle_json
        CHECK
        (
            detalle_calculo IS NULL
            OR jsonb_typeof(detalle_calculo) = 'object'
        )
);

COMMENT ON TABLE profile.evaluaciones_riesgo IS
'Resultados de cada aplicación del cuestionario de perfil de riesgo.';

COMMENT ON COLUMN profile.evaluaciones_riesgo.version_cuestionario IS
'Copia de la versión utilizada para preservar la trazabilidad histórica.';

COMMENT ON COLUMN profile.evaluaciones_riesgo.clasificacion IS
'Clasificación resultante, por ejemplo CONSERVADOR, MODERADO o AGRESIVO.';

COMMENT ON COLUMN profile.evaluaciones_riesgo.confianza IS
'Nivel de confianza del método de clasificación, entre cero y uno.';

COMMENT ON COLUMN profile.evaluaciones_riesgo.metodo_clasificacion IS
'Método utilizado para obtener la clasificación.';

COMMENT ON COLUMN profile.evaluaciones_riesgo.detalle_calculo IS
'Información adicional sobre puntuaciones, reglas o resultados del modelo.';


/*
============================================================
 5. TABLA: profile.respuestas_usuario
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.respuestas_usuario
(
    id UUID
        CONSTRAINT pk_respuestas_usuario
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    evaluacion_id UUID NOT NULL,

    pregunta_id UUID NOT NULL,

    opcion_id UUID NULL,

    valor_numerico NUMERIC(20,6) NULL,

    respuesta_texto TEXT NULL,

    puntuacion_obtenida NUMERIC(12,4) NOT NULL
        DEFAULT 0,

    fecha_respuesta TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_respuestas_usuario_evaluacion
        FOREIGN KEY (evaluacion_id)
        REFERENCES profile.evaluaciones_riesgo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_respuestas_usuario_pregunta
        FOREIGN KEY (pregunta_id)
        REFERENCES profile.preguntas (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_respuestas_usuario_opcion
        FOREIGN KEY (opcion_id)
        REFERENCES profile.opciones_respuesta (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_respuestas_usuario_evaluacion_pregunta
        UNIQUE (evaluacion_id, pregunta_id),

    CONSTRAINT ck_respuestas_usuario_contenido
        CHECK
        (
            opcion_id IS NOT NULL
            OR valor_numerico IS NOT NULL
            OR NULLIF(TRIM(respuesta_texto), '') IS NOT NULL
        ),

    CONSTRAINT ck_respuestas_usuario_puntuacion
        CHECK (puntuacion_obtenida >= 0)
);

COMMENT ON TABLE profile.respuestas_usuario IS
'Respuestas proporcionadas por el usuario durante una evaluación de riesgo.';

COMMENT ON COLUMN profile.respuestas_usuario.opcion_id IS
'Opción seleccionada cuando la pregunta es cerrada.';

COMMENT ON COLUMN profile.respuestas_usuario.valor_numerico IS
'Valor contestado cuando la pregunta es numérica.';

COMMENT ON COLUMN profile.respuestas_usuario.respuesta_texto IS
'Contenido respondido cuando la pregunta permite texto libre.';

COMMENT ON COLUMN profile.respuestas_usuario.puntuacion_obtenida IS
'Puntuación calculada para la respuesta específica.';


/*
============================================================
 6. TABLA: profile.perfiles_riesgo
============================================================
*/

CREATE TABLE IF NOT EXISTS profile.perfiles_riesgo
(
    id UUID
        CONSTRAINT pk_perfiles_riesgo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    evaluacion_id UUID NOT NULL,

    clasificacion VARCHAR(40) NOT NULL,

    puntuacion NUMERIC(12,4) NOT NULL,

    confianza NUMERIC(12,8) NULL,

    descripcion TEXT NOT NULL,

    vigente BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_inicio TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_fin TIMESTAMPTZ NULL,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_perfiles_riesgo_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_perfiles_riesgo_evaluacion
        FOREIGN KEY (evaluacion_id)
        REFERENCES profile.evaluaciones_riesgo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_perfiles_riesgo_evaluacion
        UNIQUE (evaluacion_id),

    CONSTRAINT ck_perfiles_riesgo_clasificacion
        CHECK
        (
            clasificacion IN
            (
                'CONSERVADOR',
                'MODERADO_CONSERVADOR',
                'MODERADO',
                'MODERADO_AGRESIVO',
                'AGRESIVO'
            )
        ),

    CONSTRAINT ck_perfiles_riesgo_puntuacion
        CHECK (puntuacion >= 0),

    CONSTRAINT ck_perfiles_riesgo_confianza
        CHECK
        (
            confianza IS NULL
            OR confianza BETWEEN 0 AND 1
        ),

    CONSTRAINT ck_perfiles_riesgo_descripcion
        CHECK (LENGTH(TRIM(descripcion)) > 0),

    CONSTRAINT ck_perfiles_riesgo_fechas
        CHECK
        (
            fecha_fin IS NULL
            OR fecha_fin >= fecha_inicio
        ),

    CONSTRAINT ck_perfiles_riesgo_vigencia
        CHECK
        (
            (vigente = TRUE AND fecha_fin IS NULL)
            OR
            (vigente = FALSE)
        )
);

COMMENT ON TABLE profile.perfiles_riesgo IS
'Historial de perfiles de riesgo obtenidos por los usuarios.';

COMMENT ON COLUMN profile.perfiles_riesgo.evaluacion_id IS
'Evaluación específica que originó el perfil.';

COMMENT ON COLUMN profile.perfiles_riesgo.vigente IS
'Indica si el perfil debe utilizarse actualmente para personalizar recomendaciones.';

COMMENT ON COLUMN profile.perfiles_riesgo.fecha_fin IS
'Fecha de finalización de la vigencia del perfil.';


/*
============================================================
 7. CONFIRMACIÓN
============================================================
*/

COMMIT;