/*
============================================================
 AlphaInvest AI
 Script: 07_portfolio_tables.sql

 Propósito:
 Crear las tablas para listas de seguimiento,
 portafolios virtuales, posiciones de activos y
 valoraciones históricas.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql
 - 03_auth_tables.sql
 - 06_market_tables.sql

 Esquema:
 - portfolio
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: portfolio.listas_seguimiento
============================================================
*/

CREATE TABLE IF NOT EXISTS portfolio.listas_seguimiento
(
    id UUID
        CONSTRAINT pk_listas_seguimiento
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(500) NULL,

    predeterminada BOOLEAN NOT NULL
        DEFAULT FALSE,

    activa BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_listas_seguimiento_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_listas_seguimiento_usuario_nombre
        UNIQUE (usuario_id, nombre),

    CONSTRAINT ck_listas_seguimiento_nombre
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_listas_seguimiento_descripcion
        CHECK
        (
            descripcion IS NULL
            OR LENGTH(TRIM(descripcion)) > 0
        )
);

COMMENT ON TABLE portfolio.listas_seguimiento IS
'Listas personalizadas de activos financieros guardadas por los usuarios.';

COMMENT ON COLUMN portfolio.listas_seguimiento.usuario_id IS
'Usuario propietario de la lista de seguimiento.';

COMMENT ON COLUMN portfolio.listas_seguimiento.predeterminada IS
'Indica si la lista es la lista principal del usuario.';

COMMENT ON COLUMN portfolio.listas_seguimiento.activa IS
'Permite ocultar o deshabilitar una lista sin eliminarla físicamente.';


/*
============================================================
 2. TABLA: portfolio.lista_activos
============================================================
*/

CREATE TABLE IF NOT EXISTS portfolio.lista_activos
(
    lista_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    precio_objetivo NUMERIC(20,8) NULL,

    precio_alerta_minimo NUMERIC(20,8) NULL,

    precio_alerta_maximo NUMERIC(20,8) NULL,

    notas VARCHAR(1000) NULL,

    fecha_agregado TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_lista_activos
        PRIMARY KEY (lista_id, activo_id),

    CONSTRAINT fk_lista_activos_lista
        FOREIGN KEY (lista_id)
        REFERENCES portfolio.listas_seguimiento (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_lista_activos_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT ck_lista_activos_precio_objetivo
        CHECK
        (
            precio_objetivo IS NULL
            OR precio_objetivo >= 0
        ),

    CONSTRAINT ck_lista_activos_alerta_minimo
        CHECK
        (
            precio_alerta_minimo IS NULL
            OR precio_alerta_minimo >= 0
        ),

    CONSTRAINT ck_lista_activos_alerta_maximo
        CHECK
        (
            precio_alerta_maximo IS NULL
            OR precio_alerta_maximo >= 0
        ),

    CONSTRAINT ck_lista_activos_rango_alertas
        CHECK
        (
            precio_alerta_minimo IS NULL
            OR precio_alerta_maximo IS NULL
            OR precio_alerta_maximo >= precio_alerta_minimo
        ),

    CONSTRAINT ck_lista_activos_notas
        CHECK
        (
            notas IS NULL
            OR LENGTH(TRIM(notas)) > 0
        )
);

COMMENT ON TABLE portfolio.lista_activos IS
'Activos financieros incluidos en las listas de seguimiento de los usuarios.';

COMMENT ON COLUMN portfolio.lista_activos.precio_objetivo IS
'Precio que el usuario considera como objetivo para el activo.';

COMMENT ON COLUMN portfolio.lista_activos.precio_alerta_minimo IS
'Precio inferior que puede generar una alerta para el usuario.';

COMMENT ON COLUMN portfolio.lista_activos.precio_alerta_maximo IS
'Precio superior que puede generar una alerta para el usuario.';


/*
============================================================
 3. TABLA: portfolio.portafolios
============================================================
*/

CREATE TABLE IF NOT EXISTS portfolio.portafolios
(
    id UUID
        CONSTRAINT pk_portafolios
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    nombre VARCHAR(150) NOT NULL,

    descripcion TEXT NULL,

    moneda_base CHAR(3) NOT NULL
        DEFAULT 'USD',

    capital_inicial NUMERIC(24,8) NOT NULL,

    saldo_efectivo NUMERIC(24,8) NOT NULL,

    tipo VARCHAR(30) NOT NULL
        DEFAULT 'VIRTUAL',

    estado VARCHAR(30) NOT NULL
        DEFAULT 'ACTIVO',

    fecha_inicio DATE NOT NULL
        DEFAULT CURRENT_DATE,

    fecha_cierre DATE NULL,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_portafolios_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_portafolios_usuario_nombre
        UNIQUE (usuario_id, nombre),

    CONSTRAINT ck_portafolios_nombre
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_portafolios_descripcion
        CHECK
        (
            descripcion IS NULL
            OR LENGTH(TRIM(descripcion)) > 0
        ),

    CONSTRAINT ck_portafolios_moneda_base
        CHECK
        (
            moneda_base = UPPER(moneda_base)
            AND moneda_base ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_portafolios_capital_inicial
        CHECK (capital_inicial >= 0),

    CONSTRAINT ck_portafolios_saldo_efectivo
        CHECK (saldo_efectivo >= 0),

    CONSTRAINT ck_portafolios_tipo
        CHECK
        (
            tipo IN
            (
                'VIRTUAL',
                'SIMULADO'
            )
        ),

    CONSTRAINT ck_portafolios_estado
        CHECK
        (
            estado IN
            (
                'ACTIVO',
                'CERRADO',
                'ARCHIVADO'
            )
        ),

    CONSTRAINT ck_portafolios_fechas
        CHECK
        (
            fecha_cierre IS NULL
            OR fecha_cierre >= fecha_inicio
        ),

    CONSTRAINT ck_portafolios_estado_cierre
        CHECK
        (
            estado <> 'CERRADO'
            OR fecha_cierre IS NOT NULL
        )
);

COMMENT ON TABLE portfolio.portafolios IS
'Portafolios virtuales utilizados para organizar y simular inversiones sin realizar operaciones reales.';

COMMENT ON COLUMN portfolio.portafolios.moneda_base IS
'Moneda utilizada para expresar el valor total del portafolio.';

COMMENT ON COLUMN portfolio.portafolios.capital_inicial IS
'Capital virtual con el que comenzó el portafolio.';

COMMENT ON COLUMN portfolio.portafolios.saldo_efectivo IS
'Saldo virtual disponible que todavía no está asignado a posiciones.';

COMMENT ON COLUMN portfolio.portafolios.tipo IS
'Tipo de portafolio: virtual administrado por el usuario o generado por una simulación.';

COMMENT ON COLUMN portfolio.portafolios.estado IS
'Estado operativo del portafolio.';


/*
============================================================
 4. TABLA: portfolio.posiciones
============================================================
*/

CREATE TABLE IF NOT EXISTS portfolio.posiciones
(
    id UUID
        CONSTRAINT pk_posiciones
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    portafolio_id UUID NOT NULL,

    activo_id UUID NOT NULL,

    cantidad NUMERIC(24,8) NOT NULL,

    precio_promedio_compra NUMERIC(20,8) NOT NULL,

    costo_total NUMERIC(24,8) NOT NULL,

    precio_actual NUMERIC(20,8) NULL,

    valor_actual NUMERIC(24,8) NULL,

    ganancia_perdida NUMERIC(24,8) NULL,

    rendimiento_porcentaje NUMERIC(16,8) NULL,

    moneda CHAR(3) NOT NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'ABIERTA',

    fecha_apertura TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_cierre TIMESTAMPTZ NULL,

    CONSTRAINT fk_posiciones_portafolio
        FOREIGN KEY (portafolio_id)
        REFERENCES portfolio.portafolios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_posiciones_activo
        FOREIGN KEY (activo_id)
        REFERENCES market.activos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_posiciones_portafolio_activo
        UNIQUE (portafolio_id, activo_id),

    CONSTRAINT ck_posiciones_cantidad
        CHECK (cantidad >= 0),

    CONSTRAINT ck_posiciones_precio_promedio
        CHECK (precio_promedio_compra >= 0),

    CONSTRAINT ck_posiciones_costo_total
        CHECK (costo_total >= 0),

    CONSTRAINT ck_posiciones_precio_actual
        CHECK
        (
            precio_actual IS NULL
            OR precio_actual >= 0
        ),

    CONSTRAINT ck_posiciones_valor_actual
        CHECK
        (
            valor_actual IS NULL
            OR valor_actual >= 0
        ),

    CONSTRAINT ck_posiciones_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_posiciones_estado
        CHECK
        (
            estado IN
            (
                'ABIERTA',
                'CERRADA'
            )
        ),

    CONSTRAINT ck_posiciones_fecha_cierre
        CHECK
        (
            fecha_cierre IS NULL
            OR fecha_cierre >= fecha_apertura
        ),

    CONSTRAINT ck_posiciones_estado_fecha_cierre
        CHECK
        (
            estado <> 'CERRADA'
            OR fecha_cierre IS NOT NULL
        ),

    CONSTRAINT ck_posiciones_cerrada_cantidad
        CHECK
        (
            estado <> 'CERRADA'
            OR cantidad = 0
        )
);

COMMENT ON TABLE portfolio.posiciones IS
'Posiciones agregadas de cada activo dentro de un portafolio virtual.';

COMMENT ON COLUMN portfolio.posiciones.cantidad IS
'Cantidad actual de unidades del activo dentro del portafolio.';

COMMENT ON COLUMN portfolio.posiciones.precio_promedio_compra IS
'Costo promedio ponderado de adquisición de las unidades actuales.';

COMMENT ON COLUMN portfolio.posiciones.costo_total IS
'Costo acumulado de la posición abierta.';

COMMENT ON COLUMN portfolio.posiciones.precio_actual IS
'Último precio conocido utilizado para valorar la posición.';

COMMENT ON COLUMN portfolio.posiciones.valor_actual IS
'Valor calculado de la posición con el precio más reciente.';

COMMENT ON COLUMN portfolio.posiciones.ganancia_perdida IS
'Diferencia entre el valor actual y el costo total de la posición.';

COMMENT ON COLUMN portfolio.posiciones.rendimiento_porcentaje IS
'Rendimiento porcentual acumulado de la posición.';


/*
============================================================
 5. TABLA: portfolio.valoraciones_portafolio
============================================================
*/

CREATE TABLE IF NOT EXISTS portfolio.valoraciones_portafolio
(
    id BIGINT
        GENERATED BY DEFAULT AS IDENTITY
        CONSTRAINT pk_valoraciones_portafolio
        PRIMARY KEY,

    portafolio_id UUID NOT NULL,

    fecha_hora TIMESTAMPTZ NOT NULL,

    saldo_efectivo NUMERIC(24,8) NOT NULL,

    valor_posiciones NUMERIC(24,8) NOT NULL,

    valor_total NUMERIC(24,8) NOT NULL,

    capital_invertido NUMERIC(24,8) NOT NULL,

    ganancia_perdida NUMERIC(24,8) NOT NULL,

    rendimiento_porcentaje NUMERIC(16,8) NULL,

    moneda CHAR(3) NOT NULL,

    detalle JSONB NULL,

    fecha_registro TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_valoraciones_portafolio
        FOREIGN KEY (portafolio_id)
        REFERENCES portfolio.portafolios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_valoraciones_portafolio_fecha
        UNIQUE (portafolio_id, fecha_hora),

    CONSTRAINT ck_valoraciones_saldo_efectivo
        CHECK (saldo_efectivo >= 0),

    CONSTRAINT ck_valoraciones_valor_posiciones
        CHECK (valor_posiciones >= 0),

    CONSTRAINT ck_valoraciones_valor_total
        CHECK (valor_total >= 0),

    CONSTRAINT ck_valoraciones_capital_invertido
        CHECK (capital_invertido >= 0),

    CONSTRAINT ck_valoraciones_moneda
        CHECK
        (
            moneda = UPPER(moneda)
            AND moneda ~ '^[A-Z]{3}$'
        ),

    CONSTRAINT ck_valoraciones_total_componentes
        CHECK
        (
            ABS
            (
                valor_total
                - (saldo_efectivo + valor_posiciones)
            ) <= 0.01
        ),

    CONSTRAINT ck_valoraciones_detalle_json
        CHECK
        (
            detalle IS NULL
            OR jsonb_typeof(detalle) = 'object'
        )
);

COMMENT ON TABLE portfolio.valoraciones_portafolio IS
'Histórico de la evolución del valor total de los portafolios virtuales.';

COMMENT ON COLUMN portfolio.valoraciones_portafolio.fecha_hora IS
'Momento exacto en que se realizó la valoración.';

COMMENT ON COLUMN portfolio.valoraciones_portafolio.valor_posiciones IS
'Suma del valor de mercado de todas las posiciones abiertas.';

COMMENT ON COLUMN portfolio.valoraciones_portafolio.valor_total IS
'Suma del saldo disponible y del valor de las posiciones.';

COMMENT ON COLUMN portfolio.valoraciones_portafolio.capital_invertido IS
'Capital virtual acumulado utilizado como base para calcular el rendimiento.';

COMMENT ON COLUMN portfolio.valoraciones_portafolio.detalle IS
'Desglose opcional de la valoración por activo o posición.';


/*
============================================================
 6. CONFIRMACIÓN
============================================================
*/

COMMIT;