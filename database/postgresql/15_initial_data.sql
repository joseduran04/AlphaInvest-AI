/*
============================================================
 AlphaInvest AI
 Script: 15_initial_data.sql

 Propósito:
 Cargar un universo inicial y controlado de activos financieros
 para habilitar consultas, listas de seguimiento, portafolios,
 simulaciones y análisis posteriores.

 Dependencias:
 - 06_market_tables.sql
 - 14_seed_catalogs.sql

 Características:
 - Compatible con PostgreSQL.
 - Transaccional.
 - Idempotente mediante la restricción UNIQUE
   (mercado_id, simbolo).
 - No crea usuarios, contraseñas, precios históricos,
   ejecuciones, predicciones ni resultados ficticios.
============================================================
*/

BEGIN;

/*
============================================================
 1. ACCIONES DE ESTADOS UNIDOS
============================================================
*/

INSERT INTO market.activos
(
    mercado_id,
    tipo_activo_id,
    simbolo,
    nombre,
    descripcion,
    moneda,
    sector,
    industria,
    isin,
    estado
)
SELECT
    m.id,
    t.id,
    v.simbolo,
    v.nombre,
    v.descripcion,
    'USD',
    v.sector,
    v.industria,
    v.isin,
    'ACTIVO'
FROM market.mercados AS m
CROSS JOIN market.tipos_activo AS t
CROSS JOIN
(
    VALUES
        ('AAPL', 'Apple Inc.', 'Empresa de tecnología y electrónica de consumo.', 'Tecnología', 'Electrónica de consumo', 'US0378331005'),
        ('MSFT', 'Microsoft Corporation', 'Empresa de software, nube y servicios tecnológicos.', 'Tecnología', 'Software e infraestructura', 'US5949181045'),
        ('NVDA', 'NVIDIA Corporation', 'Empresa especializada en semiconductores y procesamiento acelerado.', 'Tecnología', 'Semiconductores', 'US67066G1040'),
        ('AMZN', 'Amazon.com, Inc.', 'Empresa de comercio electrónico y servicios de computación en la nube.', 'Consumo discrecional', 'Comercio electrónico', 'US0231351067'),
        ('GOOGL', 'Alphabet Inc. Class A', 'Empresa de servicios digitales, publicidad y tecnología.', 'Comunicación', 'Servicios de Internet', 'US02079K3059'),
        ('META', 'Meta Platforms, Inc.', 'Empresa de plataformas sociales y publicidad digital.', 'Comunicación', 'Plataformas digitales', 'US30303M1027'),
        ('TSLA', 'Tesla, Inc.', 'Empresa de vehículos eléctricos, energía y almacenamiento.', 'Consumo discrecional', 'Automóviles', 'US88160R1014')
) AS v(simbolo, nombre, descripcion, sector, industria, isin)
WHERE m.codigo = 'NASDAQ'
  AND t.codigo = 'ACCION'
ON CONFLICT (mercado_id, simbolo)
DO UPDATE SET
    tipo_activo_id = EXCLUDED.tipo_activo_id,
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    moneda = EXCLUDED.moneda,
    sector = EXCLUDED.sector,
    industria = EXCLUDED.industria,
    isin = EXCLUDED.isin,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 2. ETF DE REFERENCIA
============================================================
*/

INSERT INTO market.activos
(
    mercado_id,
    tipo_activo_id,
    simbolo,
    nombre,
    descripcion,
    moneda,
    sector,
    industria,
    isin,
    estado
)
SELECT
    m.id,
    t.id,
    v.simbolo,
    v.nombre,
    v.descripcion,
    'USD',
    'Fondos diversificados',
    'Fondos cotizados',
    v.isin,
    'ACTIVO'
FROM market.mercados AS m
CROSS JOIN market.tipos_activo AS t
CROSS JOIN
(
    VALUES
        ('SPY', 'SPDR S&P 500 ETF Trust', 'ETF de referencia que busca replicar el índice S&P 500.', 'US78462F1030'),
        ('QQQ', 'Invesco QQQ Trust', 'ETF orientado a empresas no financieras del Nasdaq-100.', 'US46090E1038')
) AS v(simbolo, nombre, descripcion, isin)
WHERE m.codigo = 'NYSE'
  AND t.codigo = 'ETF'
ON CONFLICT (mercado_id, simbolo)
DO UPDATE SET
    tipo_activo_id = EXCLUDED.tipo_activo_id,
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    moneda = EXCLUDED.moneda,
    sector = EXCLUDED.sector,
    industria = EXCLUDED.industria,
    isin = EXCLUDED.isin,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 3. ACCIONES MEXICANAS
============================================================
*/

INSERT INTO market.activos
(
    mercado_id,
    tipo_activo_id,
    simbolo,
    nombre,
    descripcion,
    moneda,
    sector,
    industria,
    isin,
    estado
)
SELECT
    m.id,
    t.id,
    v.simbolo,
    v.nombre,
    v.descripcion,
    'MXN',
    v.sector,
    v.industria,
    v.isin,
    'ACTIVO'
FROM market.mercados AS m
CROSS JOIN market.tipos_activo AS t
CROSS JOIN
(
    VALUES
        ('AMXL', 'América Móvil, S.A.B. de C.V.', 'Empresa mexicana de telecomunicaciones.', 'Comunicación', 'Telecomunicaciones', 'MXP001691213'),
        ('WALMEX', 'Wal-Mart de México, S.A.B. de C.V.', 'Empresa mexicana del sector comercio minorista.', 'Consumo básico', 'Comercio minorista', 'MX01WA000038'),
        ('FEMSAUBD', 'Fomento Económico Mexicano, S.A.B. de C.V.', 'Empresa mexicana de bebidas, comercio y logística.', 'Consumo básico', 'Bebidas y comercio', 'MXP320321310'),
        ('GFNORTEO', 'Grupo Financiero Banorte, S.A.B. de C.V.', 'Grupo financiero mexicano con servicios bancarios y de inversión.', 'Financiero', 'Banca diversificada', 'MXP370711014')
) AS v(simbolo, nombre, descripcion, sector, industria, isin)
WHERE m.codigo = 'BMV'
  AND t.codigo = 'ACCION'
ON CONFLICT (mercado_id, simbolo)
DO UPDATE SET
    tipo_activo_id = EXCLUDED.tipo_activo_id,
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    moneda = EXCLUDED.moneda,
    sector = EXCLUDED.sector,
    industria = EXCLUDED.industria,
    isin = EXCLUDED.isin,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 4. CRIPTOACTIVOS
 Los símbolos se almacenan como pares contra USD para evitar
 ambigüedad en futuras integraciones de precios.
============================================================
*/

INSERT INTO market.activos
(
    mercado_id,
    tipo_activo_id,
    simbolo,
    nombre,
    descripcion,
    moneda,
    sector,
    industria,
    isin,
    estado
)
SELECT
    m.id,
    t.id,
    v.simbolo,
    v.nombre,
    v.descripcion,
    'USD',
    'Activos digitales',
    'Criptoactivos',
    NULL,
    'ACTIVO'
FROM market.mercados AS m
CROSS JOIN market.tipos_activo AS t
CROSS JOIN
(
    VALUES
        ('BTC-USD', 'Bitcoin', 'Par de referencia de Bitcoin expresado en dólares estadounidenses.'),
        ('ETH-USD', 'Ethereum', 'Par de referencia de Ether expresado en dólares estadounidenses.')
) AS v(simbolo, nombre, descripcion)
WHERE m.codigo = 'CRYPTO'
  AND t.codigo = 'CRIPTO'
ON CONFLICT (mercado_id, simbolo)
DO UPDATE SET
    tipo_activo_id = EXCLUDED.tipo_activo_id,
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    moneda = EXCLUDED.moneda,
    sector = EXCLUDED.sector,
    industria = EXCLUDED.industria,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;


/*
============================================================
 5. DIVISAS
============================================================
*/

INSERT INTO market.activos
(
    mercado_id,
    tipo_activo_id,
    simbolo,
    nombre,
    descripcion,
    moneda,
    sector,
    industria,
    isin,
    estado
)
SELECT
    m.id,
    t.id,
    v.simbolo,
    v.nombre,
    v.descripcion,
    v.moneda,
    'Mercado cambiario',
    'Divisas',
    NULL,
    'ACTIVO'
FROM market.mercados AS m
CROSS JOIN market.tipos_activo AS t
CROSS JOIN
(
    VALUES
        ('USD/MXN', 'Dólar estadounidense / Peso mexicano', 'Tipo de cambio del dólar estadounidense frente al peso mexicano.', 'MXN'),
        ('EUR/USD', 'Euro / Dólar estadounidense', 'Tipo de cambio del euro frente al dólar estadounidense.', 'USD')
) AS v(simbolo, nombre, descripcion, moneda)
WHERE m.codigo = 'FOREX'
  AND t.codigo = 'DIVISA'
ON CONFLICT (mercado_id, simbolo)
DO UPDATE SET
    tipo_activo_id = EXCLUDED.tipo_activo_id,
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    moneda = EXCLUDED.moneda,
    sector = EXCLUDED.sector,
    industria = EXCLUDED.industria,
    estado = EXCLUDED.estado,
    fecha_actualizacion = CURRENT_TIMESTAMP;

COMMIT;