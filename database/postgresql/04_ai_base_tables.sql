/*
============================================================
 AlphaInvest AI
 Script: 04_ai_base_tables.sql

 Propósito:
 Crear las tablas principales para el registro,
 versionado y control de modelos de inteligencia artificial.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql

 Esquema:
 - ai
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: ai.modelos_ia
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.modelos_ia
(
    id UUID
        CONSTRAINT pk_modelos_ia
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    codigo VARCHAR(100) NOT NULL,

    nombre VARCHAR(150) NOT NULL,

    tipo VARCHAR(50) NOT NULL,

    objetivo VARCHAR(150) NOT NULL,

    descripcion TEXT NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'DESARROLLO',

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_modelos_ia_codigo
        UNIQUE (codigo),

    CONSTRAINT ck_modelos_ia_codigo_no_vacio
        CHECK (LENGTH(TRIM(codigo)) > 0),

    CONSTRAINT ck_modelos_ia_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_modelos_ia_tipo_no_vacio
        CHECK (LENGTH(TRIM(tipo)) > 0),

    CONSTRAINT ck_modelos_ia_objetivo_no_vacio
        CHECK (LENGTH(TRIM(objetivo)) > 0),

    CONSTRAINT ck_modelos_ia_estado
        CHECK
        (
            estado IN
            (
                'DESARROLLO',
                'VALIDACION',
                'ACTIVO',
                'INACTIVO',
                'RETIRADO'
            )
        )
);

COMMENT ON TABLE ai.modelos_ia IS
'Definición conceptual de los modelos de inteligencia artificial utilizados por AlphaInvest AI.';

COMMENT ON COLUMN ai.modelos_ia.codigo IS
'Código técnico único del modelo.';

COMMENT ON COLUMN ai.modelos_ia.nombre IS
'Nombre descriptivo del modelo.';

COMMENT ON COLUMN ai.modelos_ia.tipo IS
'Tipo funcional del modelo, por ejemplo CLASIFICACION, REGRESION o NLP.';

COMMENT ON COLUMN ai.modelos_ia.objetivo IS
'Objetivo principal del modelo, por ejemplo clasificar riesgo o predecir tendencia.';

COMMENT ON COLUMN ai.modelos_ia.estado IS
'Estado general del modelo independientemente de sus versiones.';


/*
============================================================
 2. TABLA: ai.versiones_modelo
============================================================
*/

CREATE TABLE IF NOT EXISTS ai.versiones_modelo
(
    id UUID
        CONSTRAINT pk_versiones_modelo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    modelo_id UUID NOT NULL,

    version VARCHAR(30) NOT NULL,

    ruta_artefacto VARCHAR(1000) NOT NULL,

    checksum VARCHAR(255) NOT NULL,

    algoritmo VARCHAR(100) NOT NULL,

    framework VARCHAR(100) NULL,

    hiperparametros JSONB NULL,

    metricas JSONB NULL,

    conjunto_entrenamiento JSONB NULL,

    fecha_entrenamiento TIMESTAMPTZ NOT NULL,

    fecha_activacion TIMESTAMPTZ NULL,

    fecha_desactivacion TIMESTAMPTZ NULL,

    activa BOOLEAN NOT NULL
        DEFAULT FALSE,

    creada_por UUID NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_versiones_modelo_modelo
        FOREIGN KEY (modelo_id)
        REFERENCES ai.modelos_ia (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_versiones_modelo_creada_por
        FOREIGN KEY (creada_por)
        REFERENCES app_auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uq_versiones_modelo_version
        UNIQUE (modelo_id, version),

    CONSTRAINT uq_versiones_modelo_checksum
        UNIQUE (checksum),

    CONSTRAINT ck_versiones_modelo_version_no_vacia
        CHECK (LENGTH(TRIM(version)) > 0),

    CONSTRAINT ck_versiones_modelo_ruta_no_vacia
        CHECK (LENGTH(TRIM(ruta_artefacto)) > 0),

    CONSTRAINT ck_versiones_modelo_checksum_no_vacio
        CHECK (LENGTH(TRIM(checksum)) > 0),

    CONSTRAINT ck_versiones_modelo_algoritmo_no_vacio
        CHECK (LENGTH(TRIM(algoritmo)) > 0),

    CONSTRAINT ck_versiones_modelo_fecha_activacion
        CHECK
        (
            fecha_activacion IS NULL
            OR fecha_activacion >= fecha_entrenamiento
        ),

    CONSTRAINT ck_versiones_modelo_fecha_desactivacion
        CHECK
        (
            fecha_desactivacion IS NULL
            OR fecha_activacion IS NULL
            OR fecha_desactivacion >= fecha_activacion
        ),

    CONSTRAINT ck_versiones_modelo_estado_activo
        CHECK
        (
            activa = FALSE
            OR fecha_activacion IS NOT NULL
        ),

    CONSTRAINT ck_versiones_modelo_hiperparametros_json
        CHECK
        (
            hiperparametros IS NULL
            OR jsonb_typeof(hiperparametros) = 'object'
        ),

    CONSTRAINT ck_versiones_modelo_metricas_json
        CHECK
        (
            metricas IS NULL
            OR jsonb_typeof(metricas) = 'object'
        ),

    CONSTRAINT ck_versiones_modelo_conjunto_json
        CHECK
        (
            conjunto_entrenamiento IS NULL
            OR jsonb_typeof(conjunto_entrenamiento) = 'object'
        )
);

COMMENT ON TABLE ai.versiones_modelo IS
'Versiones entrenadas y desplegables de cada modelo de inteligencia artificial.';

COMMENT ON COLUMN ai.versiones_modelo.modelo_id IS
'Modelo conceptual al que pertenece la versión.';

COMMENT ON COLUMN ai.versiones_modelo.version IS
'Número o identificador de versión, por ejemplo 1.0.0.';

COMMENT ON COLUMN ai.versiones_modelo.ruta_artefacto IS
'Ubicación del archivo del modelo en almacenamiento de objetos.';

COMMENT ON COLUMN ai.versiones_modelo.checksum IS
'Hash utilizado para verificar la integridad del artefacto.';

COMMENT ON COLUMN ai.versiones_modelo.hiperparametros IS
'Configuración de entrenamiento almacenada como objeto JSON.';

COMMENT ON COLUMN ai.versiones_modelo.metricas IS
'Métricas de evaluación del modelo almacenadas como objeto JSON.';

COMMENT ON COLUMN ai.versiones_modelo.conjunto_entrenamiento IS
'Metadatos del conjunto de datos usado durante el entrenamiento.';

COMMENT ON COLUMN ai.versiones_modelo.activa IS
'Indica si la versión está habilitada para inferencias en producción.';

COMMENT ON COLUMN ai.versiones_modelo.creada_por IS
'Usuario administrador o analista que registró la versión.';

COMMIT;