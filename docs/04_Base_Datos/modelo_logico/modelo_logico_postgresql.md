# AlphaInvest AI

## Modelo lógico de base de datos PostgreSQL

## 1. Propósito

El modelo lógico define la estructura relacional utilizada por AlphaInvest AI para almacenar información estructurada, transaccional y auditable.

La base de datos principal será PostgreSQL y estará dividida lógicamente en los siguientes esquemas:

```text
auth
profile
market
portfolio
simulation
ai
audit
operation
```

La separación por esquemas permite organizar las tablas por dominio y establecer una propiedad lógica de los datos para cada servicio.

## 2. Convenciones

### Nombres

Se utilizarán las siguientes convenciones:

```text
Esquemas:              snake_case
Tablas:                plural
Columnas:              snake_case
Claves primarias:      id
Claves foráneas:       entidad_id
Índices:               idx_tabla_columnas
Restricciones únicas:  uq_tabla_columnas
Restricciones CHECK:   ck_tabla_regla
Claves foráneas:       fk_tabla_referencia
```

### Tipos generales

| Información                     | Tipo PostgreSQL |
| ------------------------------- | --------------- |
| Identificadores principales     | `UUID`          |
| Identificadores de gran volumen | `BIGINT`        |
| Fecha sin hora                  | `DATE`          |
| Fecha y hora                    | `TIMESTAMPTZ`   |
| Cantidad monetaria              | `NUMERIC(20,4)` |
| Precio financiero               | `NUMERIC(20,8)` |
| Cantidad de activos             | `NUMERIC(24,8)` |
| Porcentaje o confianza          | `NUMERIC(12,8)` |
| Texto variable                  | `TEXT`          |
| Información flexible            | `JSONB`         |
| Dirección IP                    | `INET`          |
| Estado lógico                   | `VARCHAR`       |
| Indicadores lógicos             | `BOOLEAN`       |

Las fechas y horas deben almacenarse mediante `TIMESTAMPTZ`.

La aplicación será responsable de presentarlas en la zona horaria correspondiente al usuario.

## 3. Extensiones de PostgreSQL

La implementación física deberá habilitar:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

Esta extensión permitirá generar identificadores UUID mediante:

```sql
gen_random_uuid()
```

Opcionalmente puede habilitarse:

```sql
CREATE EXTENSION IF NOT EXISTS citext;
```

El tipo `CITEXT` puede utilizarse para correos electrónicos y otros valores que deban compararse sin distinguir mayúsculas y minúsculas.

---

# 4. Esquema auth

## 4.1 Tabla auth.usuarios

Almacena los usuarios registrados.

| Columna             | Tipo         | Nulo | Regla                            |
| ------------------- | ------------ | ---: | -------------------------------- |
| id                  | UUID         |   No | PK                               |
| nombres             | VARCHAR(100) |   No |                                  |
| apellidos           | VARCHAR(100) |   No |                                  |
| correo              | CITEXT       |   No | UNIQUE                           |
| password_hash       | VARCHAR(255) |   No |                                  |
| estado              | VARCHAR(30)  |   No | Default `PENDIENTE_VERIFICACION` |
| correo_verificado   | BOOLEAN      |   No | Default `FALSE`                  |
| intentos_fallidos   | INTEGER      |   No | Default `0`                      |
| bloqueado_hasta     | TIMESTAMPTZ  |   Sí |                                  |
| ultimo_acceso       | TIMESTAMPTZ  |   Sí |                                  |
| fecha_creacion      | TIMESTAMPTZ  |   No | Default `CURRENT_TIMESTAMP`      |
| fecha_actualizacion | TIMESTAMPTZ  |   No | Default `CURRENT_TIMESTAMP`      |

Clave primaria:

```text
PK (id)
```

Restricciones:

```text
UNIQUE (correo)

CHECK (intentos_fallidos >= 0)

CHECK (
    estado IN (
        'PENDIENTE_VERIFICACION',
        'ACTIVO',
        'BLOQUEADO',
        'INACTIVO'
    )
)
```

Reglas:

- El correo no puede repetirse.
- La contraseña nunca se almacena en texto plano.
- Un usuario inactivo conserva su historial.
- Los usuarios no deben eliminarse físicamente en operaciones normales.

Índices:

```text
idx_usuarios_estado
idx_usuarios_fecha_creacion
```

---

## 4.2 Tabla auth.roles

| Columna        | Tipo         | Nulo | Regla          |
| -------------- | ------------ | ---: | -------------- |
| id             | UUID         |   No | PK             |
| nombre         | VARCHAR(50)  |   No | UNIQUE         |
| descripcion    | VARCHAR(255) |   Sí |                |
| activo         | BOOLEAN      |   No | Default `TRUE` |
| fecha_creacion | TIMESTAMPTZ  |   No |                |

Restricciones:

```text
UNIQUE (nombre)
```

Roles iniciales:

```text
INVERSIONISTA
ADMINISTRADOR
ANALISTA
SOPORTE
```

---

## 4.3 Tabla auth.permisos

| Columna     | Tipo         | Nulo | Regla          |
| ----------- | ------------ | ---: | -------------- |
| id          | UUID         |   No | PK             |
| codigo      | VARCHAR(100) |   No | UNIQUE         |
| nombre      | VARCHAR(100) |   No |                |
| descripcion | VARCHAR(255) |   Sí |                |
| modulo      | VARCHAR(50)  |   No |                |
| activo      | BOOLEAN      |   No | Default `TRUE` |

Ejemplos:

```text
users.read
users.update
assets.manage
models.activate
audit.read
simulations.execute
recommendations.generate
```

---

## 4.4 Tabla auth.usuario_roles

Resuelve la relación muchos a muchos entre usuarios y roles.

| Columna          | Tipo        | Nulo | Regla  |
| ---------------- | ----------- | ---: | ------ |
| usuario_id       | UUID        |   No | PK, FK |
| rol_id           | UUID        |   No | PK, FK |
| asignado_por     | UUID        |   Sí | FK     |
| fecha_asignacion | TIMESTAMPTZ |   No |        |

Clave primaria compuesta:

```text
PK (usuario_id, rol_id)
```

Claves foráneas:

```text
usuario_id  → auth.usuarios.id
rol_id      → auth.roles.id
asignado_por → auth.usuarios.id
```

Eliminación:

```text
usuario_id  ON DELETE CASCADE
rol_id      ON DELETE RESTRICT
asignado_por ON DELETE SET NULL
```

---

## 4.5 Tabla auth.rol_permisos

| Columna          | Tipo        | Nulo | Regla  |
| ---------------- | ----------- | ---: | ------ |
| rol_id           | UUID        |   No | PK, FK |
| permiso_id       | UUID        |   No | PK, FK |
| fecha_asignacion | TIMESTAMPTZ |   No |        |

Clave primaria:

```text
PK (rol_id, permiso_id)
```

Eliminación:

```text
rol_id      ON DELETE CASCADE
permiso_id  ON DELETE CASCADE
```

---

## 4.6 Tabla auth.sesiones

| Columna            | Tipo         | Nulo | Regla          |
| ------------------ | ------------ | ---: | -------------- |
| id                 | UUID         |   No | PK             |
| usuario_id         | UUID         |   No | FK             |
| refresh_token_hash | VARCHAR(255) |   No |                |
| direccion_ip       | INET         |   Sí |                |
| agente_usuario     | VARCHAR(500) |   Sí |                |
| fecha_inicio       | TIMESTAMPTZ  |   No |                |
| fecha_expiracion   | TIMESTAMPTZ  |   No |                |
| fecha_revocacion   | TIMESTAMPTZ  |   Sí |                |
| activa             | BOOLEAN      |   No | Default `TRUE` |

Restricciones:

```text
CHECK (fecha_expiracion > fecha_inicio)
```

Índices:

```text
idx_sesiones_usuario_activa
idx_sesiones_fecha_expiracion
```

Eliminación:

```text
usuario_id ON DELETE CASCADE
```

---

## 4.7 Tabla auth.aceptaciones_terminos

| Columna            | Tipo        | Nulo | Regla |
| ------------------ | ----------- | ---: | ----- |
| id                 | UUID        |   No | PK    |
| usuario_id         | UUID        |   No | FK    |
| version_terminos   | VARCHAR(30) |   No |       |
| version_privacidad | VARCHAR(30) |   No |       |
| fecha_aceptacion   | TIMESTAMPTZ |   No |       |
| direccion_ip       | INET        |   Sí |       |

Restricción única:

```text
UNIQUE (
    usuario_id,
    version_terminos,
    version_privacidad
)
```

El historial de aceptación no debe eliminarse cuando una versión sea reemplazada.

---

# 5. Esquema profile

## 5.1 Tabla profile.cuestionarios

| Columna           | Tipo         | Nulo |
| ----------------- | ------------ | ---: |
| id                | UUID         |   No |
| nombre            | VARCHAR(150) |   No |
| descripcion       | TEXT         |   Sí |
| version           | VARCHAR(30)  |   No |
| estado            | VARCHAR(30)  |   No |
| fecha_publicacion | TIMESTAMPTZ  |   Sí |
| fecha_creacion    | TIMESTAMPTZ  |   No |

Restricción:

```text
UNIQUE (nombre, version)
```

Estados:

```text
BORRADOR
PUBLICADO
INACTIVO
```

---

## 5.2 Tabla profile.preguntas

| Columna         | Tipo          | Nulo |
| --------------- | ------------- | ---: |
| id              | UUID          |   No |
| cuestionario_id | UUID          |   No |
| texto           | TEXT          |   No |
| tipo            | VARCHAR(30)   |   No |
| orden           | INTEGER       |   No |
| ponderacion     | NUMERIC(10,4) |   No |
| obligatoria     | BOOLEAN       |   No |
| activa          | BOOLEAN       |   No |

Restricciones:

```text
UNIQUE (cuestionario_id, orden)

CHECK (orden > 0)

CHECK (ponderacion >= 0)

CHECK (
    tipo IN (
        'OPCION_UNICA',
        'OPCION_MULTIPLE',
        'NUMERICA',
        'TEXTO'
    )
)
```

---

## 5.3 Tabla profile.opciones_respuesta

| Columna     | Tipo          | Nulo |
| ----------- | ------------- | ---: |
| id          | UUID          |   No |
| pregunta_id | UUID          |   No |
| texto       | VARCHAR(500)  |   No |
| valor       | NUMERIC(10,4) |   No |
| orden       | INTEGER       |   No |
| activa      | BOOLEAN       |   No |

Restricciones:

```text
UNIQUE (pregunta_id, orden)

CHECK (orden > 0)
```

---

## 5.4 Tabla profile.evaluaciones_riesgo

| Columna              | Tipo          | Nulo |
| -------------------- | ------------- | ---: |
| id                   | UUID          |   No |
| usuario_id           | UUID          |   No |
| cuestionario_id      | UUID          |   No |
| version_cuestionario | VARCHAR(30)   |   No |
| puntuacion_total     | NUMERIC(12,4) |   No |
| clasificacion        | VARCHAR(40)   |   No |
| confianza            | NUMERIC(12,8) |   Sí |
| metodo_clasificacion | VARCHAR(50)   |   No |
| version_modelo_id    | UUID          |   Sí |
| fecha_evaluacion     | TIMESTAMPTZ   |   No |
| estado               | VARCHAR(30)   |   No |

Restricciones:

```text
CHECK (puntuacion_total >= 0)

CHECK (
    confianza IS NULL
    OR confianza BETWEEN 0 AND 1
)

CHECK (
    estado IN (
        'COMPLETADA',
        'INVALIDA',
        'CANCELADA'
    )
)
```

---

## 5.5 Tabla profile.respuestas_usuario

| Columna             | Tipo          | Nulo |
| ------------------- | ------------- | ---: |
| id                  | UUID          |   No |
| evaluacion_id       | UUID          |   No |
| pregunta_id         | UUID          |   No |
| opcion_id           | UUID          |   Sí |
| valor_numerico      | NUMERIC(20,6) |   Sí |
| respuesta_texto     | TEXT          |   Sí |
| puntuacion_obtenida | NUMERIC(12,4) |   No |

Restricción:

```text
UNIQUE (evaluacion_id, pregunta_id)
```

Debe existir al menos uno de los siguientes valores:

```text
opcion_id
valor_numerico
respuesta_texto
```

Regla `CHECK`:

```text
CHECK (
    opcion_id IS NOT NULL
    OR valor_numerico IS NOT NULL
    OR respuesta_texto IS NOT NULL
)
```

---

## 5.6 Tabla profile.perfiles_riesgo

| Columna        | Tipo          | Nulo |
| -------------- | ------------- | ---: |
| id             | UUID          |   No |
| usuario_id     | UUID          |   No |
| evaluacion_id  | UUID          |   No |
| clasificacion  | VARCHAR(40)   |   No |
| puntuacion     | NUMERIC(12,4) |   No |
| confianza      | NUMERIC(12,8) |   Sí |
| descripcion    | TEXT          |   No |
| vigente        | BOOLEAN       |   No |
| fecha_inicio   | TIMESTAMPTZ   |   No |
| fecha_fin      | TIMESTAMPTZ   |   Sí |
| fecha_creacion | TIMESTAMPTZ   |   No |

Restricciones:

```text
UNIQUE (evaluacion_id)

CHECK (puntuacion >= 0)

CHECK (
    confianza IS NULL
    OR confianza BETWEEN 0 AND 1
)

CHECK (
    fecha_fin IS NULL
    OR fecha_fin >= fecha_inicio
)
```

Debe existir un único perfil vigente por usuario.

Índice único parcial:

```sql
CREATE UNIQUE INDEX uq_perfil_vigente_usuario
ON profile.perfiles_riesgo (usuario_id)
WHERE vigente = TRUE;
```

---

# 6. Esquema market

## 6.1 Tabla market.mercados

| Columna      | Tipo         | Nulo |
| ------------ | ------------ | ---: |
| id           | UUID         |   No |
| codigo       | VARCHAR(30)  |   No |
| nombre       | VARCHAR(150) |   No |
| pais         | VARCHAR(100) |   No |
| zona_horaria | VARCHAR(80)  |   No |
| moneda       | CHAR(3)      |   No |
| activo       | BOOLEAN      |   No |

Restricción:

```text
UNIQUE (codigo)
```

---

## 6.2 Tabla market.tipos_activo

| Columna     | Tipo         | Nulo |
| ----------- | ------------ | ---: |
| id          | UUID         |   No |
| codigo      | VARCHAR(30)  |   No |
| nombre      | VARCHAR(100) |   No |
| descripcion | VARCHAR(255) |   Sí |

Valores iniciales:

```text
ACCION
ETF
INDICE
BONO
CRIPTOMONEDA
FONDO
```

---

## 6.3 Tabla market.activos

| Columna             | Tipo         | Nulo |
| ------------------- | ------------ | ---: |
| id                  | UUID         |   No |
| mercado_id          | UUID         |   No |
| tipo_activo_id      | UUID         |   No |
| simbolo             | VARCHAR(30)  |   No |
| nombre              | VARCHAR(200) |   No |
| descripcion         | TEXT         |   Sí |
| moneda              | CHAR(3)      |   No |
| sector              | VARCHAR(100) |   Sí |
| industria           | VARCHAR(150) |   Sí |
| isin                | VARCHAR(30)  |   Sí |
| estado              | VARCHAR(30)  |   No |
| fecha_alta          | TIMESTAMPTZ  |   No |
| fecha_actualizacion | TIMESTAMPTZ  |   No |

Restricciones:

```text
UNIQUE (mercado_id, simbolo)

UNIQUE (isin)

CHECK (
    estado IN (
        'ACTIVO',
        'INACTIVO',
        'SUSPENDIDO'
    )
)
```

El valor `isin` puede ser nulo cuando la fuente no lo proporcione.

---

## 6.4 Tabla market.fuentes_financieras

| Columna         | Tipo         | Nulo |
| --------------- | ------------ | ---: |
| id              | UUID         |   No |
| nombre          | VARCHAR(100) |   No |
| proveedor       | VARCHAR(100) |   No |
| url_base        | VARCHAR(500) |   Sí |
| prioridad       | INTEGER      |   No |
| activa          | BOOLEAN      |   No |
| ultima_consulta | TIMESTAMPTZ  |   Sí |

Restricciones:

```text
UNIQUE (nombre)

CHECK (prioridad > 0)
```

---

## 6.5 Tabla market.precios_historicos

| Columna         | Tipo          | Nulo |
| --------------- | ------------- | ---: |
| id              | BIGINT        |   No |
| activo_id       | UUID          |   No |
| fuente_id       | UUID          |   No |
| fecha           | DATE          |   No |
| apertura        | NUMERIC(20,8) |   Sí |
| maximo          | NUMERIC(20,8) |   Sí |
| minimo          | NUMERIC(20,8) |   Sí |
| cierre          | NUMERIC(20,8) |   No |
| cierre_ajustado | NUMERIC(20,8) |   Sí |
| volumen         | NUMERIC(24,4) |   Sí |
| moneda          | CHAR(3)       |   No |
| fecha_registro  | TIMESTAMPTZ   |   No |

Restricción única:

```text
UNIQUE (activo_id, fuente_id, fecha)
```

Validaciones:

```text
CHECK (apertura IS NULL OR apertura >= 0)
CHECK (maximo IS NULL OR maximo >= 0)
CHECK (minimo IS NULL OR minimo >= 0)
CHECK (cierre >= 0)
CHECK (cierre_ajustado IS NULL OR cierre_ajustado >= 0)
CHECK (volumen IS NULL OR volumen >= 0)
CHECK (maximo IS NULL OR minimo IS NULL OR maximo >= minimo)
```

Índice principal:

```text
idx_precios_activo_fecha
```

Definición:

```text
(activo_id, fecha DESC)
```

---

## 6.6 Tabla market.indicadores_financieros

| Columna        | Tipo          | Nulo |
| -------------- | ------------- | ---: |
| id             | BIGINT        |   No |
| activo_id      | UUID          |   No |
| tipo_indicador | VARCHAR(50)   |   No |
| fecha          | DATE          |   No |
| valor          | NUMERIC(24,8) |   No |
| periodo        | VARCHAR(30)   |   No |
| parametros     | JSONB         |   Sí |
| fecha_calculo  | TIMESTAMPTZ   |   No |

Restricción:

```text
UNIQUE (
    activo_id,
    tipo_indicador,
    fecha,
    periodo
)
```

Ejemplos de indicadores:

```text
SMA
EMA
RSI
MACD
VOLATILIDAD
BETA
DRAWDOWN
```

---

## 6.7 Tabla market.noticias_referencia

| Columna           | Tipo          | Nulo |
| ----------------- | ------------- | ---: |
| id                | UUID          |   No |
| activo_id         | UUID          |   No |
| mongo_document_id | VARCHAR(100)  |   No |
| titulo            | VARCHAR(500)  |   No |
| fuente            | VARCHAR(150)  |   No |
| url               | VARCHAR(1000) |   Sí |
| fecha_publicacion | TIMESTAMPTZ   |   No |
| idioma            | VARCHAR(10)   |   Sí |
| relevancia        | NUMERIC(12,8) |   Sí |
| fecha_registro    | TIMESTAMPTZ   |   No |

Restricciones:

```text
UNIQUE (activo_id, mongo_document_id)

CHECK (
    relevancia IS NULL
    OR relevancia BETWEEN 0 AND 1
)
```

---

# 7. Esquema portfolio

## 7.1 Tabla portfolio.listas_seguimiento

| Columna             | Tipo         | Nulo |
| ------------------- | ------------ | ---: |
| id                  | UUID         |   No |
| usuario_id          | UUID         |   No |
| nombre              | VARCHAR(100) |   No |
| descripcion         | VARCHAR(255) |   Sí |
| predeterminada      | BOOLEAN      |   No |
| fecha_creacion      | TIMESTAMPTZ  |   No |
| fecha_actualizacion | TIMESTAMPTZ  |   No |

Restricción:

```text
UNIQUE (usuario_id, nombre)
```

Un usuario solo debe tener una lista predeterminada.

Índice único parcial:

```sql
CREATE UNIQUE INDEX uq_lista_predeterminada_usuario
ON portfolio.listas_seguimiento (usuario_id)
WHERE predeterminada = TRUE;
```

---

## 7.2 Tabla portfolio.lista_activos

| Columna          | Tipo         | Nulo |
| ---------------- | ------------ | ---: |
| lista_id         | UUID         |   No |
| activo_id        | UUID         |   No |
| fecha_agregacion | TIMESTAMPTZ  |   No |
| notas            | VARCHAR(500) |   Sí |

Clave primaria:

```text
PK (lista_id, activo_id)
```

---

## 7.3 Tabla portfolio.portafolios

| Columna             | Tipo          | Nulo |
| ------------------- | ------------- | ---: |
| id                  | UUID          |   No |
| usuario_id          | UUID          |   No |
| nombre              | VARCHAR(150)  |   No |
| descripcion         | TEXT          |   Sí |
| moneda_base         | CHAR(3)       |   No |
| capital_inicial     | NUMERIC(20,4) |   No |
| estado              | VARCHAR(30)   |   No |
| fecha_creacion      | TIMESTAMPTZ   |   No |
| fecha_actualizacion | TIMESTAMPTZ   |   No |

Restricciones:

```text
UNIQUE (usuario_id, nombre)

CHECK (capital_inicial >= 0)

CHECK (
    estado IN (
        'ACTIVO',
        'ARCHIVADO',
        'INACTIVO'
    )
)
```

---

## 7.4 Tabla portfolio.posiciones_portafolio

| Columna             | Tipo          | Nulo |
| ------------------- | ------------- | ---: |
| id                  | UUID          |   No |
| portafolio_id       | UUID          |   No |
| activo_id           | UUID          |   No |
| cantidad_virtual    | NUMERIC(24,8) |   No |
| precio_promedio     | NUMERIC(20,8) |   No |
| capital_asignado    | NUMERIC(20,4) |   No |
| porcentaje_objetivo | NUMERIC(8,4)  |   Sí |
| fecha_apertura      | TIMESTAMPTZ   |   No |
| fecha_actualizacion | TIMESTAMPTZ   |   No |
| estado              | VARCHAR(30)   |   No |

Restricciones:

```text
UNIQUE (portafolio_id, activo_id)

CHECK (cantidad_virtual >= 0)
CHECK (precio_promedio >= 0)
CHECK (capital_asignado >= 0)

CHECK (
    porcentaje_objetivo IS NULL
    OR porcentaje_objetivo BETWEEN 0 AND 100
)
```

---

## 7.5 Tabla portfolio.valoraciones_portafolio

| Columna                | Tipo          | Nulo |
| ---------------------- | ------------- | ---: |
| id                     | BIGINT        |   No |
| portafolio_id          | UUID          |   No |
| fecha                  | TIMESTAMPTZ   |   No |
| valor_total            | NUMERIC(20,4) |   No |
| ganancia_perdida       | NUMERIC(20,4) |   No |
| rendimiento_porcentual | NUMERIC(12,8) |   No |
| volatilidad            | NUMERIC(12,8) |   Sí |
| moneda                 | CHAR(3)       |   No |

Restricción:

```text
UNIQUE (portafolio_id, fecha)
```

---

# 8. Esquema simulation

## 8.1 Tabla simulation.simulaciones

| Columna                 | Tipo          | Nulo |
| ----------------------- | ------------- | ---: |
| id                      | UUID          |   No |
| usuario_id              | UUID          |   No |
| nombre                  | VARCHAR(150)  |   No |
| capital_inicial         | NUMERIC(20,4) |   No |
| moneda                  | CHAR(3)       |   No |
| fecha_inicio_solicitada | DATE          |   No |
| fecha_fin_solicitada    | DATE          |   No |
| fecha_inicio_efectiva   | DATE          |   Sí |
| fecha_fin_efectiva      | DATE          |   Sí |
| estado                  | VARCHAR(30)   |   No |
| guardada                | BOOLEAN       |   No |
| fecha_ejecucion         | TIMESTAMPTZ   |   No |
| fecha_guardado          | TIMESTAMPTZ   |   Sí |

Restricciones:

```text
CHECK (capital_inicial > 0)

CHECK (
    fecha_inicio_solicitada
    < fecha_fin_solicitada
)

CHECK (
    fecha_inicio_efectiva IS NULL
    OR fecha_fin_efectiva IS NULL
    OR fecha_inicio_efectiva <= fecha_fin_efectiva
)

CHECK (
    estado IN (
        'TEMPORAL',
        'EJECUTADA',
        'GUARDADA',
        'FALLIDA',
        'EXPIRADA'
    )
)
```

---

## 8.2 Tabla simulation.simulacion_activos

| Columna          | Tipo          | Nulo |
| ---------------- | ------------- | ---: |
| id               | UUID          |   No |
| simulacion_id    | UUID          |   No |
| activo_id        | UUID          |   No |
| porcentaje       | NUMERIC(8,4)  |   No |
| capital_asignado | NUMERIC(20,4) |   No |
| precio_inicial   | NUMERIC(20,8) |   Sí |
| precio_final     | NUMERIC(20,8) |   Sí |
| cantidad_virtual | NUMERIC(24,8) |   Sí |
| valor_final      | NUMERIC(20,4) |   Sí |
| rendimiento      | NUMERIC(12,8) |   Sí |

Restricciones:

```text
UNIQUE (simulacion_id, activo_id)

CHECK (porcentaje > 0 AND porcentaje <= 100)

CHECK (capital_asignado >= 0)

CHECK (
    precio_inicial IS NULL
    OR precio_inicial >= 0
)

CHECK (
    precio_final IS NULL
    OR precio_final >= 0
)
```

La suma de porcentajes debe ser exactamente 100.

Esta regla no puede garantizarse con un `CHECK` simple porque involucra varias filas. Se aplicará mediante:

- Transacción del servicio.
- Función de validación.
- Trigger diferible, cuando sea necesario.

---

## 8.3 Tabla simulation.resultados_simulacion

| Columna                | Tipo          | Nulo |
| ---------------------- | ------------- | ---: |
| id                     | UUID          |   No |
| simulacion_id          | UUID          |   No |
| valor_final            | NUMERIC(20,4) |   No |
| ganancia_perdida       | NUMERIC(20,4) |   No |
| rendimiento_porcentual | NUMERIC(12,8) |   No |
| volatilidad            | NUMERIC(12,8) |   Sí |
| maximo_drawdown        | NUMERIC(12,8) |   Sí |
| indice_sharpe          | NUMERIC(12,8) |   Sí |
| dias_analizados        | INTEGER       |   No |
| advertencias           | JSONB         |   Sí |
| fecha_calculo          | TIMESTAMPTZ   |   No |

Restricciones:

```text
UNIQUE (simulacion_id)

CHECK (valor_final >= 0)
CHECK (dias_analizados > 0)

CHECK (
    maximo_drawdown IS NULL
    OR maximo_drawdown BETWEEN 0 AND 1
)
```

Relación:

```text
simulation.simulaciones 1 ─── 0..1 simulation.resultados_simulacion
```

---

## 8.4 Tabla simulation.series_simulacion_referencia

| Columna            | Tipo         | Nulo |
| ------------------ | ------------ | ---: |
| id                 | UUID         |   No |
| simulacion_id      | UUID         |   No |
| mongo_document_id  | VARCHAR(100) |   No |
| cantidad_puntos    | INTEGER      |   No |
| fecha_primer_punto | DATE         |   No |
| fecha_ultimo_punto | DATE         |   No |
| fecha_registro     | TIMESTAMPTZ  |   No |

Restricciones:

```text
UNIQUE (simulacion_id)

UNIQUE (mongo_document_id)

CHECK (cantidad_puntos > 0)

CHECK (
    fecha_primer_punto
    <= fecha_ultimo_punto
)
```

---

# 9. Esquema ai

## 9.1 Tabla ai.modelos_ia

| Columna        | Tipo         | Nulo |
| -------------- | ------------ | ---: |
| id             | UUID         |   No |
| codigo         | VARCHAR(100) |   No |
| nombre         | VARCHAR(150) |   No |
| tipo           | VARCHAR(50)  |   No |
| objetivo       | VARCHAR(150) |   No |
| descripcion    | TEXT         |   Sí |
| estado         | VARCHAR(30)  |   No |
| fecha_creacion | TIMESTAMPTZ  |   No |

Restricciones:

```text
UNIQUE (codigo)

CHECK (
    estado IN (
        'DESARROLLO',
        'ACTIVO',
        'INACTIVO',
        'RETIRADO'
    )
)
```

---

## 9.2 Tabla ai.versiones_modelo

| Columna             | Tipo          | Nulo |
| ------------------- | ------------- | ---: |
| id                  | UUID          |   No |
| modelo_id           | UUID          |   No |
| version             | VARCHAR(30)   |   No |
| ruta_artefacto      | VARCHAR(1000) |   No |
| checksum            | VARCHAR(255)  |   No |
| algoritmo           | VARCHAR(100)  |   No |
| hiperparametros     | JSONB         |   Sí |
| metricas            | JSONB         |   Sí |
| fecha_entrenamiento | TIMESTAMPTZ   |   No |
| fecha_activacion    | TIMESTAMPTZ   |   Sí |
| activa              | BOOLEAN       |   No |

Restricciones:

```text
UNIQUE (modelo_id, version)

UNIQUE (checksum)
```

Debe existir una única versión activa por modelo:

```sql
CREATE UNIQUE INDEX uq_version_activa_modelo
ON ai.versiones_modelo (modelo_id)
WHERE activa = TRUE;
```

---

## 9.3 Tabla ai.analisis_activos

| Columna                 | Tipo          | Nulo |
| ----------------------- | ------------- | ---: |
| id                      | UUID          |   No |
| usuario_id              | UUID          |   No |
| activo_id               | UUID          |   No |
| fecha_inicio            | DATE          |   No |
| fecha_fin               | DATE          |   No |
| clasificacion_riesgo    | VARCHAR(40)   |   No |
| puntuacion_riesgo       | NUMERIC(12,8) |   No |
| clasificacion_tendencia | VARCHAR(40)   |   No |
| confianza_tendencia     | NUMERIC(12,8) |   No |
| sentimiento_agregado    | VARCHAR(30)   |   Sí |
| puntuacion_sentimiento  | NUMERIC(12,8) |   Sí |
| confianza_general       | NUMERIC(12,8) |   No |
| explicacion             | TEXT          |   No |
| fecha_generacion        | TIMESTAMPTZ   |   No |
| valido_hasta            | TIMESTAMPTZ   |   No |
| estado                  | VARCHAR(30)   |   No |

Restricciones:

```text
CHECK (fecha_inicio < fecha_fin)

CHECK (puntuacion_riesgo BETWEEN 0 AND 1)

CHECK (confianza_tendencia BETWEEN 0 AND 1)

CHECK (
    puntuacion_sentimiento IS NULL
    OR puntuacion_sentimiento BETWEEN -1 AND 1
)

CHECK (confianza_general BETWEEN 0 AND 1)

CHECK (valido_hasta > fecha_generacion)

CHECK (
    estado IN (
        'GENERADO',
        'VENCIDO',
        'INVALIDO'
    )
)
```

Índices:

```text
idx_analisis_usuario_fecha
idx_analisis_activo_fecha
idx_analisis_valido_hasta
```

---

## 9.4 Tabla ai.analisis_modelos

| Columna             | Tipo        | Nulo |
| ------------------- | ----------- | ---: |
| analisis_id         | UUID        |   No |
| version_modelo_id   | UUID        |   No |
| tipo_resultado      | VARCHAR(50) |   No |
| tiempo_ejecucion_ms | INTEGER     |   Sí |
| fecha_ejecucion     | TIMESTAMPTZ |   No |

Clave primaria:

```text
PK (
    analisis_id,
    version_modelo_id,
    tipo_resultado
)
```

Restricción:

```text
CHECK (
    tiempo_ejecucion_ms IS NULL
    OR tiempo_ejecucion_ms >= 0
)
```

---

## 9.5 Tabla ai.predicciones

| Columna          | Tipo          | Nulo |
| ---------------- | ------------- | ---: |
| id               | UUID          |   No |
| analisis_id      | UUID          |   No |
| tipo             | VARCHAR(50)   |   No |
| horizonte        | VARCHAR(30)   |   No |
| valor_estimado   | NUMERIC(24,8) |   Sí |
| clasificacion    | VARCHAR(50)   |   Sí |
| confianza        | NUMERIC(12,8) |   No |
| fecha_objetivo   | DATE          |   Sí |
| fecha_generacion | TIMESTAMPTZ   |   No |

Restricciones:

```text
CHECK (confianza BETWEEN 0 AND 1)

CHECK (
    valor_estimado IS NOT NULL
    OR clasificacion IS NOT NULL
)
```

---

## 9.6 Tabla ai.factores_explicativos

| Columna        | Tipo          | Nulo |
| -------------- | ------------- | ---: |
| id             | UUID          |   No |
| analisis_id    | UUID          |   No |
| variable       | VARCHAR(150)  |   No |
| valor_variable | VARCHAR(500)  |   Sí |
| importancia    | NUMERIC(12,8) |   No |
| impacto        | VARCHAR(30)   |   No |
| metodo         | VARCHAR(50)   |   No |
| orden          | INTEGER       |   No |

Restricciones:

```text
UNIQUE (analisis_id, orden)

CHECK (importancia >= 0)

CHECK (orden > 0)

CHECK (
    impacto IN (
        'POSITIVO',
        'NEGATIVO',
        'NEUTRAL'
    )
)
```

---

## 9.7 Tabla ai.analisis_sentimiento

| Columna               | Tipo          | Nulo |
| --------------------- | ------------- | ---: |
| id                    | UUID          |   No |
| analisis_id           | UUID          |   No |
| noticia_referencia_id | UUID          |   No |
| mongo_document_id     | VARCHAR(100)  |   No |
| clasificacion         | VARCHAR(30)   |   No |
| puntuacion            | NUMERIC(12,8) |   No |
| confianza             | NUMERIC(12,8) |   No |
| version_modelo_id     | UUID          |   No |
| fecha_analisis        | TIMESTAMPTZ   |   No |

Restricciones:

```text
UNIQUE (
    analisis_id,
    noticia_referencia_id,
    version_modelo_id
)

CHECK (puntuacion BETWEEN -1 AND 1)

CHECK (confianza BETWEEN 0 AND 1)

CHECK (
    clasificacion IN (
        'POSITIVO',
        'NEUTRAL',
        'NEGATIVO'
    )
)
```

---

## 9.8 Tabla ai.recomendaciones

| Columna           | Tipo          | Nulo |
| ----------------- | ------------- | ---: |
| id                | UUID          |   No |
| usuario_id        | UUID          |   No |
| analisis_id       | UUID          |   No |
| perfil_riesgo_id  | UUID          |   No |
| categoria         | VARCHAR(60)   |   No |
| compatibilidad    | NUMERIC(12,8) |   No |
| confianza         | NUMERIC(12,8) |   No |
| explicacion       | TEXT          |   No |
| advertencia       | TEXT          |   No |
| version_modelo_id | UUID          |   Sí |
| fecha_generacion  | TIMESTAMPTZ   |   No |
| valido_hasta      | TIMESTAMPTZ   |   No |
| estado            | VARCHAR(30)   |   No |

Restricciones:

```text
CHECK (compatibilidad BETWEEN 0 AND 1)

CHECK (confianza BETWEEN 0 AND 1)

CHECK (valido_hasta > fecha_generacion)

CHECK (
    categoria IN (
        'COMPATIBLE',
        'COMPATIBLE_CON_PRECAUCION',
        'RIESGO_SUPERIOR_AL_PERFIL',
        'INFORMACION_INSUFICIENTE'
    )
)

CHECK (
    estado IN (
        'VIGENTE',
        'VENCIDA',
        'INVALIDADA'
    )
)
```

Regla:

```text
usuario_id debe corresponder al propietario del análisis
```

Esta validación deberá ejecutarse en el servicio y, cuando sea conveniente, mediante una función de base de datos.

---

## 9.9 Tabla ai.factores_recomendacion

| Columna          | Tipo          | Nulo |
| ---------------- | ------------- | ---: |
| id               | UUID          |   No |
| recomendacion_id | UUID          |   No |
| factor           | VARCHAR(200)  |   No |
| valor            | VARCHAR(500)  |   Sí |
| impacto          | VARCHAR(30)   |   No |
| importancia      | NUMERIC(12,8) |   No |
| orden            | INTEGER       |   No |

Restricciones:

```text
UNIQUE (recomendacion_id, orden)

CHECK (importancia >= 0)

CHECK (orden > 0)
```

---

## 9.10 Tabla ai.reglas_recomendacion

| Columna        | Tipo         | Nulo |
| -------------- | ------------ | ---: |
| id             | UUID         |   No |
| codigo         | VARCHAR(100) |   No |
| nombre         | VARCHAR(150) |   No |
| condicion      | JSONB        |   No |
| resultado      | VARCHAR(60)  |   No |
| prioridad      | INTEGER      |   No |
| version        | VARCHAR(30)  |   No |
| activa         | BOOLEAN      |   No |
| fecha_creacion | TIMESTAMPTZ  |   No |

Restricciones:

```text
UNIQUE (codigo, version)

CHECK (prioridad > 0)
```

---

## 9.11 Tabla ai.recomendacion_reglas

| Columna              | Tipo        | Nulo |
| -------------------- | ----------- | ---: |
| recomendacion_id     | UUID        |   No |
| regla_id             | UUID        |   No |
| cumplida             | BOOLEAN     |   No |
| resultado_evaluacion | JSONB       |   Sí |
| fecha_evaluacion     | TIMESTAMPTZ |   No |

Clave primaria:

```text
PK (recomendacion_id, regla_id)
```

---

# 10. Esquema audit

## 10.1 Tabla audit.eventos_auditoria

| Columna            | Tipo         | Nulo |
| ------------------ | ------------ | ---: |
| id                 | UUID         |   No |
| usuario_id         | UUID         |   Sí |
| tipo_evento        | VARCHAR(80)  |   No |
| accion             | VARCHAR(100) |   No |
| entidad            | VARCHAR(100) |   Sí |
| entidad_id         | VARCHAR(100) |   Sí |
| servicio           | VARCHAR(100) |   No |
| resultado          | VARCHAR(30)  |   No |
| direccion_ip       | INET         |   Sí |
| agente_usuario     | VARCHAR(500) |   Sí |
| correlation_id     | UUID         |   No |
| valores_anteriores | JSONB        |   Sí |
| valores_nuevos     | JSONB        |   Sí |
| detalle            | JSONB        |   Sí |
| fecha_evento       | TIMESTAMPTZ  |   No |

Índices:

```text
idx_auditoria_correlation_id
idx_auditoria_usuario_fecha
idx_auditoria_tipo_fecha
idx_auditoria_servicio_fecha
```

Eliminación:

```text
usuario_id ON DELETE SET NULL
```

Los eventos no deben eliminarse cuando se desactive un usuario.

---

## 10.2 Tabla audit.errores_sistema

| Columna          | Tipo         | Nulo |
| ---------------- | ------------ | ---: |
| id               | UUID         |   No |
| usuario_id       | UUID         |   Sí |
| servicio         | VARCHAR(100) |   No |
| codigo_error     | VARCHAR(100) |   No |
| mensaje          | TEXT         |   No |
| detalle_tecnico  | TEXT         |   Sí |
| correlation_id   | UUID         |   No |
| nivel            | VARCHAR(30)  |   No |
| resuelto         | BOOLEAN      |   No |
| fecha_error      | TIMESTAMPTZ  |   No |
| fecha_resolucion | TIMESTAMPTZ  |   Sí |

Restricciones:

```text
CHECK (
    nivel IN (
        'INFO',
        'WARNING',
        'ERROR',
        'CRITICAL'
    )
)

CHECK (
    fecha_resolucion IS NULL
    OR fecha_resolucion >= fecha_error
)
```

---

# 11. Esquema operation

## 11.1 Tabla operation.tareas_programadas

| Columna                | Tipo         | Nulo |
| ---------------------- | ------------ | ---: |
| id                     | UUID         |   No |
| codigo                 | VARCHAR(100) |   No |
| nombre                 | VARCHAR(150) |   No |
| tipo                   | VARCHAR(50)  |   No |
| expresion_programacion | VARCHAR(100) |   No |
| ultima_ejecucion       | TIMESTAMPTZ  |   Sí |
| siguiente_ejecucion    | TIMESTAMPTZ  |   Sí |
| estado                 | VARCHAR(30)  |   No |
| activa                 | BOOLEAN      |   No |

Restricción:

```text
UNIQUE (codigo)
```

---

## 11.2 Tabla operation.ejecuciones_tarea

| Columna              | Tipo        | Nulo |
| -------------------- | ----------- | ---: |
| id                   | UUID        |   No |
| tarea_id             | UUID        |   No |
| fecha_inicio         | TIMESTAMPTZ |   No |
| fecha_fin            | TIMESTAMPTZ |   Sí |
| estado               | VARCHAR(30) |   No |
| registros_procesados | INTEGER     |   No |
| mensaje              | TEXT        |   Sí |
| detalle              | JSONB       |   Sí |

Restricciones:

```text
CHECK (registros_procesados >= 0)

CHECK (
    fecha_fin IS NULL
    OR fecha_fin >= fecha_inicio
)
```

Estados:

```text
EN_EJECUCION
COMPLETADA
FALLIDA
CANCELADA
```

---

# 12. Matriz de relaciones principales

| Tabla origen        | Relación    | Tabla destino         | Cardinalidad |
| ------------------- | ----------- | --------------------- | ------------ |
| usuarios            | posee       | usuario_roles         | 1:N          |
| roles               | contiene    | usuario_roles         | 1:N          |
| roles               | posee       | rol_permisos          | 1:N          |
| cuestionarios       | contiene    | preguntas             | 1:N          |
| preguntas           | contiene    | opciones_respuesta    | 1:N          |
| usuarios            | realiza     | evaluaciones_riesgo   | 1:N          |
| evaluaciones_riesgo | contiene    | respuestas_usuario    | 1:N          |
| evaluaciones_riesgo | genera      | perfiles_riesgo       | 1:1          |
| mercados            | lista       | activos               | 1:N          |
| activos             | registra    | precios_historicos    | 1:N          |
| usuarios            | administra  | portafolios           | 1:N          |
| portafolios         | contiene    | posiciones_portafolio | 1:N          |
| usuarios            | ejecuta     | simulaciones          | 1:N          |
| simulaciones        | contiene    | simulacion_activos    | 1:N          |
| simulaciones        | produce     | resultados_simulacion | 1:0..1       |
| modelos_ia          | contiene    | versiones_modelo      | 1:N          |
| usuarios            | solicita    | analisis_activos      | 1:N          |
| activos             | recibe      | analisis_activos      | 1:N          |
| analisis_activos    | utiliza     | versiones_modelo      | N:M          |
| analisis_activos    | genera      | predicciones          | 1:N          |
| analisis_activos    | genera      | recomendaciones       | 1:N          |
| perfiles_riesgo     | personaliza | recomendaciones       | 1:N          |
| recomendaciones     | evalúa      | reglas_recomendacion  | N:M          |
| tareas_programadas  | produce     | ejecuciones_tarea     | 1:N          |

---

# 13. Políticas de eliminación

## ON DELETE CASCADE

Puede utilizarse en registros subordinados sin valor histórico independiente:

```text
auth.usuario_roles
auth.rol_permisos
auth.sesiones
profile.preguntas
profile.opciones_respuesta
profile.respuestas_usuario
portfolio.lista_activos
portfolio.posiciones_portafolio
simulation.simulacion_activos
ai.predicciones
ai.factores_explicativos
ai.factores_recomendacion
ai.recomendacion_reglas
```

## ON DELETE RESTRICT

Debe utilizarse cuando el registro forma parte del historial:

```text
market.precios_historicos
profile.perfiles_riesgo
simulation.resultados_simulacion
ai.versiones_modelo
ai.analisis_activos
ai.recomendaciones
```

## ON DELETE SET NULL

Se utilizará cuando el registro deba conservarse, pero la relación pueda desaparecer:

```text
audit.eventos_auditoria.usuario_id
audit.errores_sistema.usuario_id
auth.usuario_roles.asignado_por
```

## Eliminación lógica

Las siguientes entidades utilizarán estado lógico:

```text
usuarios
roles
permisos
activos
fuentes_financieras
modelos_ia
reglas_recomendacion
```

---

# 14. Normalización

El modelo se encuentra diseñado principalmente en tercera forma normal.

## Primera forma normal

Cada columna contiene un valor atómico.

Ejemplo correcto:

```text
usuario_roles
├── usuario_id
└── rol_id
```

No se guardan varios roles dentro de una sola columna.

## Segunda forma normal

Las tablas con claves compuestas dependen completamente de su clave.

Ejemplo:

```text
lista_activos
PK (lista_id, activo_id)
```

La fecha de agregación depende de la combinación completa.

## Tercera forma normal

Los datos descriptivos se separan de las transacciones.

Ejemplo:

```text
activos
    ↓
tipo_activo_id
    ↓
tipos_activo
```

El nombre del tipo de activo no se repite en cada registro de activos.

Los campos `JSONB` se reservan para datos variables que no forman parte de las relaciones principales.

---

# 15. Índices prioritarios

Los siguientes índices deberán incluirse en la implementación física:

```text
auth.usuarios(correo)

auth.sesiones(usuario_id, activa)

profile.perfiles_riesgo(usuario_id)
WHERE vigente = TRUE

market.activos(mercado_id, simbolo)

market.precios_historicos(activo_id, fecha DESC)

market.indicadores_financieros(
    activo_id,
    tipo_indicador,
    fecha DESC
)

market.noticias_referencia(
    activo_id,
    fecha_publicacion DESC
)

portfolio.portafolios(usuario_id)

portfolio.posiciones_portafolio(portafolio_id)

simulation.simulaciones(
    usuario_id,
    fecha_ejecucion DESC
)

ai.versiones_modelo(modelo_id)
WHERE activa = TRUE

ai.analisis_activos(
    usuario_id,
    fecha_generacion DESC
)

ai.analisis_activos(
    activo_id,
    fecha_generacion DESC
)

ai.recomendaciones(
    usuario_id,
    fecha_generacion DESC
)

audit.eventos_auditoria(correlation_id)

audit.eventos_auditoria(
    usuario_id,
    fecha_evento DESC
)
```

---

# 16. Reglas que requieren lógica adicional

Algunas reglas no pueden implementarse únicamente con restricciones simples.

## Porcentajes de simulación

La suma de los activos de una simulación debe ser 100.

```text
SUM(simulacion_activos.porcentaje) = 100
```

Se validará mediante:

- FastAPI antes de guardar.
- Transacción.
- Función PostgreSQL.
- Trigger diferible, cuando sea necesario.

## Propietario del análisis

Una recomendación solo puede pertenecer al mismo usuario propietario del análisis.

```text
recomendacion.usuario_id
=
analisis.usuario_id
```

Debe validarse en el servicio de recomendaciones.

## Perfil perteneciente al usuario

El perfil utilizado en la recomendación debe pertenecer al usuario:

```text
recomendacion.usuario_id
=
perfil_riesgo.usuario_id
```

## Vigencia del análisis

No debe generarse una recomendación utilizando un análisis vencido:

```text
analisis.valido_hasta > CURRENT_TIMESTAMP
```

## Perfil vigente

Al generar una recomendación, el perfil deberá estar marcado como vigente.

## Versión activa de modelo

Solo una versión de cada modelo puede mantenerse activa.

Esto se garantiza mediante índice único parcial.

---

# 17. Transacciones principales

## Registro de usuario

```text
INSERT usuario
INSERT rol inicial
INSERT aceptación de términos
INSERT evento de auditoría
COMMIT
```

Si falla cualquiera de los pasos:

```text
ROLLBACK
```

## Creación de perfil

```text
INSERT evaluación
INSERT respuestas
UPDATE perfil anterior vigente = FALSE
INSERT nuevo perfil vigente
INSERT auditoría
COMMIT
```

## Guardado de simulación

```text
UPDATE simulación
INSERT activos simulados
INSERT resultado
INSERT referencia MongoDB
INSERT auditoría
COMMIT
```

## Generación de análisis

```text
INSERT análisis
INSERT modelos utilizados
INSERT predicciones
INSERT factores explicativos
INSERT resultados de sentimiento
INSERT auditoría
COMMIT
```

## Generación de recomendación

```text
INSERT recomendación
INSERT factores
INSERT reglas evaluadas
INSERT auditoría
COMMIT
```

---

# 18. Propiedad lógica por servicio

| Servicio               | Esquemas o tablas principales                                                    |
| ---------------------- | -------------------------------------------------------------------------------- |
| Auth Service           | `auth.*`                                                                         |
| Profile Service        | `profile.*`                                                                      |
| Market Service         | `market.*`                                                                       |
| Portfolio Service      | `portfolio.*`                                                                    |
| Simulation Service     | `simulation.*`                                                                   |
| AI Service             | `ai.modelos_ia`, `ai.versiones_modelo`, `ai.analisis_activos`, `ai.predicciones` |
| Recommendation Service | `ai.recomendaciones`, `ai.factores_recomendacion`, `ai.reglas_recomendacion`     |
| Audit Service          | `audit.*`                                                                        |
| Worker Service         | `operation.*`                                                                    |

Un servicio no debería modificar directamente las tablas pertenecientes a otro dominio.

Durante el prototipo podrá utilizarse una sola base de datos y un solo usuario técnico, pero la aplicación deberá respetar la separación lógica.

---

# 19. Información almacenada fuera de PostgreSQL

## MongoDB

Se almacenará en MongoDB:

```text
Contenido completo de noticias
Textos procesados
Resultados NLP extensos
Series temporales de simulación
Metadatos documentales variables
```

PostgreSQL conservará:

```text
mongo_document_id
activo relacionado
simulación relacionada
fecha
fuente
información de control
```

## Object Storage

Se almacenará fuera de PostgreSQL:

```text
Modelos XGBoost
Modelos Random Forest
Transformers
Tokenizadores
Objetos SHAP
Archivos de metadatos
```

PostgreSQL conservará:

```text
ruta_artefacto
checksum
versión
métricas
fecha de entrenamiento
estado
```

---

# 20. Validación final

Antes de aprobar el modelo lógico se debe verificar:

```text
[ ] Todas las tablas tienen una clave primaria.
[ ] Todas las relaciones tienen claves foráneas.
[ ] Los correos son únicos.
[ ] Las contraseñas se almacenan como hash.
[ ] Las fechas utilizan TIMESTAMPTZ.
[ ] Los importes utilizan NUMERIC.
[ ] Los porcentajes tienen restricciones.
[ ] Las confianzas se encuentran entre 0 y 1.
[ ] Los puntajes de sentimiento se encuentran entre -1 y 1.
[ ] Solo existe un perfil vigente por usuario.
[ ] Solo existe una versión activa por modelo.
[ ] Un activo no se repite en el mismo portafolio.
[ ] Un activo no se repite en la misma simulación.
[ ] Cada simulación tiene como máximo un resultado.
[ ] Los análisis registran las versiones de modelos.
[ ] Las recomendaciones conservan el perfil utilizado.
[ ] Las reglas evaluadas se conservan.
[ ] La auditoría acepta eventos sin usuario.
[ ] Las noticias completas no se duplican en PostgreSQL.
[ ] Los modelos binarios no se guardan en PostgreSQL.
[ ] Las eliminaciones históricas utilizan RESTRICT.
```

## 21. Resultado

El modelo lógico de AlphaInvest AI queda normalizado, dividido por dominios y preparado para transformarse en un script físico PostgreSQL.

El siguiente paso será generar:

```text
schemas
tables
primary keys
foreign keys
unique constraints
check constraints
indexes
functions
triggers
initial catalogs
```

mediante sentencias SQL ejecutables.
