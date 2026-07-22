/*
============================================================
 AlphaInvest AI
 Script: 06_market_tables.sql

 Propósito:
 Crear las tablas del dominio de mercado financiero:
 mercados, tipos de activo, activos, fuentes de datos,
 precios históricos, indicadores y referencias de noticias.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql

 Esquema:
 - market
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: market.mercados
============================================================
*/

CREATE TABLE IF NOT EXISTS market.mercados
(
    id UUID
        CONSTRAINT pk_mercados
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    codigo VARCHAR(30) NOT NULL,

    nombre VARCHAR(150) NOT NULL,

    pais VARCHAR(100) NOT NULL,

    zona_horaria VARCHAR(80) NOT NULL,

    moneda CHAR(3) NOT NULL,

    activo BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_mercados_codigo
        UNIQUE (codigo),

    CONSTRAINT ck_mercados_codigo_no_vacio
        CHECK (LENGTH(TRIM(codigo)) > 0),

    CONSTRAINT ck_mercados_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_mercados_pais_no_vacio
        CHECK (LENGTH(TRIM(pais)) > 0),

    CONSTRAINT ck_mercados_zona_horaria_no_vacia
        CHECK (LENGTH(TRIM(zona_horaria)) > 0),

    CONSTRAINT ck_mercados_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        )
);

COMMENT ON TABLE market.mercados IS
'Catálogo de bolsas, mercados y plataformas donde cotizan los activos.';

COMMENT ON COLUMN market.mercados.codigo IS
'Código único del mercado, por ejemplo NASDAQ, NYSE, BMV o CRYPTO.';

COMMENT ON COLUMN market.mercados.zona_horaria IS
'Zona horaria IANA del mercado, por ejemplo America/New_York.';

COMMENT ON COLUMN market.mercados.moneda IS
'Código ISO de tres letras de la moneda principal del mercado.';


/*
============================================================
 2. TABLA: market.tipos_activo
============================================================
*/

CREATE TABLE IF NOT EXISTS market.tipos_activo
(
    id UUID
        CONSTRAINT pk_tipos_activo
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    codigo VARCHAR(30) NOT NULL,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255) NULL,

    activo BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_tipos_activo_codigo
        UNIQUE (codigo),

    CONSTRAINT uq_tipos_activo_nombre
        UNIQUE (nombre),

    CONSTRAINT ck_tipos_activo_codigo_no_vacio
        CHECK (LENGTH(TRIM(codigo)) > 0),

    CONSTRAINT ck_tipos_activo_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0)
);

COMMENT ON TABLE market.tipos_activo IS
'Catálogo de clases de instrumentos financieros.';

COMMENT ON COLUMN market.tipos_activo.codigo IS
'Código técnico del tipo de activo, por ejemplo ACCION, ETF o CRIPTOMONEDA.';


/*
============================================================
 3. TABLA: market.activos
============================================================
*/

CREATE TABLE IF NOT EXISTS market.activos
(
    id UUID
        CONSTRAINT pk_activos
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    mercado_id UUID NOT NULL,

    tipo_activo_id UUID NOT NULL,

    simbolo VARCHAR(30) NOT NULL,

    nombre VARCHAR(200) NOT NULL,

    descripcion TEXT NULL,

    moneda CHAR(3) NOT NULL,

    sector VARCHAR(100) NULL,

    industria VARCHAR(150) NULL,

    isin VARCHAR(30) NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'ACTIVO',

    fecha_alta TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_activos_mercado
        FOREIGN KEY (mercado_id)
        REFERENCES market.mercados (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_activos_tipo
        FOREIGN KEY (tipo_activo_id)
        REFERENCES market.tipos_activo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_activos_mercado_simbolo
        UNIQUE (mercado_id, simbolo),

    CONSTRAINT uq_activos_isin
        UNIQUE (isin),

    CONSTRAINT ck_activos_simbolo_no_vacio
        CHECK (LENGTH(TRIM(simbolo)) > 0),

    CONSTRAINT ck_activos_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_activos_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_activos_isin_no_vacio
        CHECK
        (
            isin IS NULL
            OR LENGTH(TRIM(isin)) > 0
        ),

    CONSTRAINT ck_activos_estado
        CHECK
        (
            estado IN
            (
                'ACTIVO',
                'INACTIVO',
                'SUSPENDIDO'
            )
        )
);

COMMENT ON TABLE market.activos IS
'Instrumentos financieros disponibles para análisis, simulación y seguimiento.';

COMMENT ON COLUMN market.activos.simbolo IS
'Símbolo o ticker del activo dentro de su mercado.';

COMMENT ON COLUMN market.activos.isin IS
'Identificador internacional del instrumento, cuando se encuentre disponible.';

COMMENT ON COLUMN market.activos.estado IS
'Estado operativo del activo dentro de AlphaInvest AI.';


/*
============================================================
 4. TABLA: market.fuentes_financieras
============================================================
*/

CREATE TABLE IF NOT EXISTS market.fuentes_financieras
(
    id UUID
        CONSTRAINT pk_fuentes_financieras
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    nombre VARCHAR(100) NOT NULL,

    proveedor VARCHAR(100) NOT NULL,

    url_base VARCHAR(500) NULL,

    prioridad INTEGER NOT NULL
        DEFAULT 1,

    activa BOOLEAN NOT NULL
        DEFAULT TRUE,

    requiere_api_key BOOLEAN NOT NULL
        DEFAULT FALSE,

    limite_consultas_minuto INTEGER NULL,

    ultima_consulta TIMESTAMPTZ NULL,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_fuentes_financieras_nombre
        UNIQUE (nombre),

    CONSTRAINT ck_fuentes_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_fuentes_proveedor_no_vacio
        CHECK (LENGTH(TRIM(proveedor)) > 0),

    CONSTRAINT ck_fuentes_prioridad
        CHECK (prioridad > 0),

    CONSTRAINT ck_fuentes_limite_consultas
        CHECK
        (
            limite_consultas_minuto IS NULL
            OR limite_consultas_minuto > 0
        ),

    CONSTRAINT ck_fuentes_url
        CHECK
        (
            url_base IS NULL
            OR LENGTH(TRIM(url_base)) > 0
        )
);

COMMENT ON TABLE market.fuentes_financieras IS
'Proveedores externos utilizados para obtener precios, indicadores y datos de mercado.';

COMMENT ON COLUMN market.fuentes_financieras.prioridad IS
'Orden de preferencia utilizado cuando existen varias fuentes para el mismo dato.';

COMMENT ON COLUMN market.fuentes_financieras.requiere_api_key IS
'Indica si la fuente requiere una credencial externa.';

COMMENT ON COLUMN market.fuentes_financieras.limite_consultas_minuto IS
'Límite conocido de solicitudes por minuto del proveedor.';


/*
============================================================
 5. TABLA: market.precios_historicos
============================================================
*/

CREATE TABLE IF NOT EXISTS market.precios_historicos
(
    id BIGINT
        GENERATED BY DEFAULT AS IDENTITY
        CONSTRAINT pk_precios_historicos
        PRIMARY KEY,

    activo_id UUID NOT NULL,

    fuente_id UUID NOT NULL,

    fecha DATE NOT NULL,

    apertura NUMERIC(20,8) NULL,

    maximo NUMERIC(20,8) NULL,

    minimo NUMERIC(20,8) NULL,

    cierre NUMERIC(20,8) NOT NULL,

    cierre_ajustado NUMERIC(20,8) NULL,

    volumen NUMERIC(24,4) NULL,

    moneda CHAR(3) NOT NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_precios_historicos_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_precios_historicos_fuente
        FOREIGN KEY (fuente_id)
        REFERENCES market.fuentes_financieras (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_precios_activo_fuente_fecha
        UNIQUE (activo_id, fuente_id, fecha),

    CONSTRAINT ck_precios_apertura
        CHECK
        (
            apertura IS NULL
            OR apertura >= 0
        ),

    CONSTRAINT ck_precios_maximo
        CHECK
        (
            maximo IS NULL
            OR maximo >= 0
        ),

    CONSTRAINT ck_precios_minimo
        CHECK
        (
            minimo IS NULL
            OR minimo >= 0
        ),

    CONSTRAINT ck_precios_cierre
        CHECK (cierre >= 0),

    CONSTRAINT ck_precios_cierre_ajustado
        CHECK
        (
            cierre_ajustado IS NULL
            OR cierre_ajustado >= 0
        ),

    CONSTRAINT ck_precios_volumen
        CHECK
        (
            volumen IS NULL
            OR volumen >= 0
        ),

    CONSTRAINT ck_precios_maximo_minimo
        CHECK
        (
            maximo IS NULL
            OR minimo IS NULL
            OR maximo >= minimo
        ),

    CONSTRAINT ck_precios_apertura_rango
        CHECK
        (
            apertura IS NULL
            OR maximo IS NULL
            OR minimo IS NULL
            OR apertura BETWEEN minimo AND maximo
        ),

    CONSTRAINT ck_precios_cierre_rango
        CHECK
        (
            maximo IS NULL
            OR minimo IS NULL
            OR cierre BETWEEN minimo AND maximo
        ),

    CONSTRAINT ck_precios_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        )
);

COMMENT ON TABLE market.precios_historicos IS
'Precios históricos diarios o por periodo de los activos financieros.';

COMMENT ON COLUMN market.precios_historicos.fecha IS
'Fecha de cotización correspondiente al registro.';

COMMENT ON COLUMN market.precios_historicos.cierre_ajustado IS
'Precio ajustado por dividendos, divisiones u otros eventos corporativos.';

COMMENT ON COLUMN market.precios_historicos.volumen IS
'Cantidad negociada durante el periodo.';


/*
============================================================
 6. TABLA: market.indicadores_financieros
============================================================
*/

CREATE TABLE IF NOT EXISTS market.indicadores_financieros
(
    id BIGINT
        GENERATED BY DEFAULT AS IDENTITY
        CONSTRAINT pk_indicadores_financieros
        PRIMARY KEY,

    activo_id UUID NOT NULL,

    tipo_indicador VARCHAR(50) NOT NULL,

    fecha DATE NOT NULL,

    valor NUMERIC(24,8) NOT NULL,

    periodo VARCHAR(30) NOT NULL,

    parametros JSONB NULL,

    fuente_calculo VARCHAR(100) NULL,

    fecha_calculo TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_indicadores_financieros_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_indicadores_activo_tipo_fecha_periodo
        UNIQUE
        (
            activo_id,
            tipo_indicador,
            fecha,
            periodo
        ),

    CONSTRAINT ck_indicadores_tipo_no_vacio
        CHECK (LENGTH(TRIM(tipo_indicador)) > 0),

    CONSTRAINT ck_indicadores_periodo_no_vacio
        CHECK (LENGTH(TRIM(periodo)) > 0),

    CONSTRAINT ck_indicadores_parametros_json
        CHECK
        (
            parametros IS NULL
            OR jsonb_typeof(parametros) = 'object'
        ),

    CONSTRAINT ck_indicadores_fuente_calculo
        CHECK
        (
            fuente_calculo IS NULL
            OR LENGTH(TRIM(fuente_calculo)) > 0
        )
);

COMMENT ON TABLE market.indicadores_financieros IS
'Indicadores técnicos y estadísticos calculados para cada activo.';

COMMENT ON COLUMN market.indicadores_financieros.tipo_indicador IS
'Indicador calculado, por ejemplo SMA, EMA, RSI, MACD o VOLATILIDAD.';

COMMENT ON COLUMN market.indicadores_financieros.periodo IS
'Periodo o ventana utilizada, por ejemplo 14D, 30D o 200D.';

COMMENT ON COLUMN market.indicadores_financieros.parametros IS
'Parámetros adicionales utilizados para reproducir el cálculo.';


/*
============================================================
 7. TABLA: market.noticias_referencia
============================================================
*/

CREATE TABLE IF NOT EXISTS market.noticias_referencia
(
    id UUID
        CONSTRAINT pk_noticias_referencia
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    activo_id UUID NOT NULL,

    mongo_document_id VARCHAR(100) NOT NULL,

    titulo VARCHAR(500) NOT NULL,

    fuente VARCHAR(150) NOT NULL,

    url VARCHAR(1000) NULL,

    fecha_publicacion TIMESTAMPTZ NOT NULL,

    idioma VARCHAR(10) NULL,

    relevancia NUMERIC(12,8) NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_noticias_referencia_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_noticias_activo_documento
        UNIQUE (activo_id, mongo_document_id),

    CONSTRAINT ck_noticias_documento_no_vacio
        CHECK (LENGTH(TRIM(mongo_document_id)) > 0),

    CONSTRAINT ck_noticias_titulo_no_vacio
        CHECK (LENGTH(TRIM(titulo)) > 0),

    CONSTRAINT ck_noticias_fuente_no_vacia
        CHECK (LENGTH(TRIM(fuente)) > 0),

    CONSTRAINT ck_noticias_url
        CHECK
        (
            url IS NULL
            OR LENGTH(TRIM(url)) > 0
        ),

    CONSTRAINT ck_noticias_idioma
        CHECK
        (
            idioma IS NULL
            OR LENGTH(TRIM(idioma)) BETWEEN 2 AND 10
        ),

    CONSTRAINT ck_noticias_relevancia
        CHECK
        (
            relevancia IS NULL
            OR relevancia BETWEEN 0 AND 1
        )
);

COMMENT ON TABLE market.noticias_referencia IS
'Referencias relacionales hacia noticias completas almacenadas en MongoDB.';

COMMENT ON COLUMN market.noticias_referencia.mongo_document_id IS
'Identificador del documento correspondiente en MongoDB.';

COMMENT ON COLUMN market.noticias_referencia.relevancia IS
'Nivel de relación entre la noticia y el activo, expresado entre cero y uno.';

COMMIT;