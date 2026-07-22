/*
============================================================
 AlphaInvest AI
 Script: 03_auth_tables.sql

 Propósito:
 Crear las tablas del dominio de identidad, autenticación,
 autorización, sesiones y aceptación de términos.

 Dependencias:
 - 01_extensions.sql
 - 02_schemas.sql

 Esquema:
 - auth
============================================================
*/

BEGIN;

/*
============================================================
 1. TABLA: auth.usuarios
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.usuarios
(
    id UUID
        CONSTRAINT pk_usuarios
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    nombres VARCHAR(100) NOT NULL,

    apellidos VARCHAR(100) NOT NULL,

    correo CITEXT NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    estado VARCHAR(30) NOT NULL
        DEFAULT 'PENDIENTE_VERIFICACION',

    correo_verificado BOOLEAN NOT NULL
        DEFAULT FALSE,

    intentos_fallidos INTEGER NOT NULL
        DEFAULT 0,

    bloqueado_hasta TIMESTAMPTZ NULL,

    ultimo_acceso TIMESTAMPTZ NULL,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_usuarios_correo
        UNIQUE (correo),

    CONSTRAINT ck_usuarios_nombres_no_vacios
        CHECK (LENGTH(TRIM(nombres)) > 0),

    CONSTRAINT ck_usuarios_apellidos_no_vacios
        CHECK (LENGTH(TRIM(apellidos)) > 0),

    CONSTRAINT ck_usuarios_correo_no_vacio
        CHECK (LENGTH(TRIM(correo::TEXT)) > 0),

    CONSTRAINT ck_usuarios_password_hash_no_vacio
        CHECK (LENGTH(TRIM(password_hash)) > 0),

    CONSTRAINT ck_usuarios_intentos_fallidos
        CHECK (intentos_fallidos >= 0),

    CONSTRAINT ck_usuarios_estado
        CHECK
        (
            estado IN
            (
                'PENDIENTE_VERIFICACION',
                'ACTIVO',
                'BLOQUEADO',
                'INACTIVO'
            )
        )
);

COMMENT ON TABLE auth.usuarios IS
'Usuarios registrados en AlphaInvest AI.';

COMMENT ON COLUMN auth.usuarios.id IS
'Identificador UUID del usuario.';

COMMENT ON COLUMN auth.usuarios.correo IS
'Correo único del usuario, comparado sin distinguir mayúsculas y minúsculas.';

COMMENT ON COLUMN auth.usuarios.password_hash IS
'Hash seguro de la contraseña. Nunca debe contener la contraseña en texto plano.';

COMMENT ON COLUMN auth.usuarios.estado IS
'Estado operativo de la cuenta del usuario.';

COMMENT ON COLUMN auth.usuarios.bloqueado_hasta IS
'Fecha y hora hasta la que permanecerá bloqueada temporalmente la cuenta.';

COMMENT ON COLUMN auth.usuarios.fecha_actualizacion IS
'Fecha de la modificación más reciente del usuario.';


/*
============================================================
 2. TABLA: auth.roles
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.roles
(
    id UUID
        CONSTRAINT pk_roles
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    nombre VARCHAR(50) NOT NULL,

    descripcion VARCHAR(255) NULL,

    activo BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_roles_nombre
        UNIQUE (nombre),

    CONSTRAINT ck_roles_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0)
);

COMMENT ON TABLE auth.roles IS
'Catálogo de roles disponibles en AlphaInvest AI.';

COMMENT ON COLUMN auth.roles.nombre IS
'Nombre único del rol, por ejemplo INVERSIONISTA o ADMINISTRADOR.';


/*
============================================================
 3. TABLA: auth.permisos
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.permisos
(
    id UUID
        CONSTRAINT pk_permisos
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    codigo VARCHAR(100) NOT NULL,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255) NULL,

    modulo VARCHAR(50) NOT NULL,

    activo BOOLEAN NOT NULL
        DEFAULT TRUE,

    fecha_creacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_permisos_codigo
        UNIQUE (codigo),

    CONSTRAINT ck_permisos_codigo_no_vacio
        CHECK (LENGTH(TRIM(codigo)) > 0),

    CONSTRAINT ck_permisos_nombre_no_vacio
        CHECK (LENGTH(TRIM(nombre)) > 0),

    CONSTRAINT ck_permisos_modulo_no_vacio
        CHECK (LENGTH(TRIM(modulo)) > 0)
);

COMMENT ON TABLE auth.permisos IS
'Catálogo de acciones permitidas dentro del sistema.';

COMMENT ON COLUMN auth.permisos.codigo IS
'Código técnico único del permiso, por ejemplo users.read.';

COMMENT ON COLUMN auth.permisos.modulo IS
'Módulo funcional al que pertenece el permiso.';


/*
============================================================
 4. TABLA: auth.usuario_roles
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.usuario_roles
(
    usuario_id UUID NOT NULL,

    rol_id UUID NOT NULL,

    asignado_por UUID NULL,

    fecha_asignacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuario_roles
        PRIMARY KEY (usuario_id, rol_id),

    CONSTRAINT fk_usuario_roles_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_usuario_roles_rol
        FOREIGN KEY (rol_id)
        REFERENCES auth.roles (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_usuario_roles_asignado_por
        FOREIGN KEY (asignado_por)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT ck_usuario_roles_asignacion
        CHECK
        (
            asignado_por IS NULL
            OR asignado_por <> usuario_id
        )
);

COMMENT ON TABLE auth.usuario_roles IS
'Relación muchos a muchos entre usuarios y roles.';

COMMENT ON COLUMN auth.usuario_roles.asignado_por IS
'Administrador que realizó la asignación. Puede ser NULL para asignaciones automáticas.';


/*
============================================================
 5. TABLA: auth.rol_permisos
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.rol_permisos
(
    rol_id UUID NOT NULL,

    permiso_id UUID NOT NULL,

    fecha_asignacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_rol_permisos
        PRIMARY KEY (rol_id, permiso_id),

    CONSTRAINT fk_rol_permisos_rol
        FOREIGN KEY (rol_id)
        REFERENCES auth.roles (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_rol_permisos_permiso
        FOREIGN KEY (permiso_id)
        REFERENCES auth.permisos (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

COMMENT ON TABLE auth.rol_permisos IS
'Relación muchos a muchos entre roles y permisos.';


/*
============================================================
 6. TABLA: auth.sesiones
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.sesiones
(
    id UUID
        CONSTRAINT pk_sesiones
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    refresh_token_hash VARCHAR(255) NOT NULL,

    direccion_ip INET NULL,

    agente_usuario VARCHAR(500) NULL,

    fecha_inicio TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    fecha_expiracion TIMESTAMPTZ NOT NULL,

    fecha_revocacion TIMESTAMPTZ NULL,

    activa BOOLEAN NOT NULL
        DEFAULT TRUE,

    CONSTRAINT fk_sesiones_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT uq_sesiones_refresh_token_hash
        UNIQUE (refresh_token_hash),

    CONSTRAINT ck_sesiones_refresh_token_no_vacio
        CHECK (LENGTH(TRIM(refresh_token_hash)) > 0),

    CONSTRAINT ck_sesiones_fecha_expiracion
        CHECK (fecha_expiracion > fecha_inicio),

    CONSTRAINT ck_sesiones_fecha_revocacion
        CHECK
        (
            fecha_revocacion IS NULL
            OR fecha_revocacion >= fecha_inicio
        ),

    CONSTRAINT ck_sesiones_estado_revocacion
        CHECK
        (
            NOT activa
            OR fecha_revocacion IS NULL
        )
);

COMMENT ON TABLE auth.sesiones IS
'Sesiones autenticadas y refresh tokens revocables de los usuarios.';

COMMENT ON COLUMN auth.sesiones.refresh_token_hash IS
'Hash del refresh token. El token original no debe guardarse.';

COMMENT ON COLUMN auth.sesiones.direccion_ip IS
'Dirección IPv4 o IPv6 desde la cual se inició la sesión.';

COMMENT ON COLUMN auth.sesiones.fecha_revocacion IS
'Fecha en la que la sesión fue cerrada o revocada.';


/*
============================================================
 7. TABLA: auth.aceptaciones_terminos
============================================================
*/

CREATE TABLE IF NOT EXISTS auth.aceptaciones_terminos
(
    id UUID
        CONSTRAINT pk_aceptaciones_terminos
        PRIMARY KEY
        DEFAULT gen_random_uuid(),

    usuario_id UUID NOT NULL,

    version_terminos VARCHAR(30) NOT NULL,

    version_privacidad VARCHAR(30) NOT NULL,

    fecha_aceptacion TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    direccion_ip INET NULL,

    CONSTRAINT fk_aceptaciones_terminos_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES auth.usuarios (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_aceptaciones_terminos_versiones
        UNIQUE
        (
            usuario_id,
            version_terminos,
            version_privacidad
        ),

    CONSTRAINT ck_aceptaciones_version_terminos
        CHECK (LENGTH(TRIM(version_terminos)) > 0),

    CONSTRAINT ck_aceptaciones_version_privacidad
        CHECK (LENGTH(TRIM(version_privacidad)) > 0)
);

COMMENT ON TABLE auth.aceptaciones_terminos IS
'Historial de aceptación de términos de servicio y políticas de privacidad.';

COMMENT ON COLUMN auth.aceptaciones_terminos.version_terminos IS
'Versión de los términos aceptados por el usuario.';

COMMENT ON COLUMN auth.aceptaciones_terminos.version_privacidad IS
'Versión de la política de privacidad aceptada por el usuario.';


/*
============================================================
 8. CONFIRMACIÓN
============================================================
*/

COMMIT;