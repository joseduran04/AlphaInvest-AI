/*
============================================================
 AlphaInvest AI
 Script: 11_indexes.sql

 Propósito:
 Crear índices normales, compuestos, parciales y únicos
 para optimizar las consultas frecuentes y reforzar reglas
 de integridad que no pueden expresarse adecuadamente
 mediante restricciones CHECK convencionales.

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

 Esquemas:
 - auth
 - profile
 - market
 - portfolio
 - simulation
 - ai
 - audit
 - operation

 Consideraciones:
 - Las PK y restricciones UNIQUE ya generan índices.
 - Las FK no generan índices automáticamente en PostgreSQL.
 - Los índices parciales reducen tamaño y costo de búsqueda.
 - Los índices deben corresponder a consultas reales.
============================================================
*/

BEGIN;


/*
============================================================
 1. ÍNDICES DEL ESQUEMA auth
============================================================
*/

/*
------------------------------------------------------------
 Usuarios por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuarios_estado
ON auth.usuarios
(
    estado
);

COMMENT ON INDEX auth.idx_usuarios_estado IS
'Optimiza consultas y filtros de usuarios por estado operativo.';


/*
------------------------------------------------------------
 Usuarios por fecha de creación
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuarios_fecha_creacion
ON auth.usuarios
(
    fecha_creacion DESC
);

COMMENT ON INDEX auth.idx_usuarios_fecha_creacion IS
'Optimiza listados administrativos ordenados por fecha de registro.';


/*
------------------------------------------------------------
 Usuarios bloqueados temporalmente
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuarios_bloqueados_hasta
ON auth.usuarios
(
    bloqueado_hasta
)
WHERE bloqueado_hasta IS NOT NULL;

COMMENT ON INDEX auth.idx_usuarios_bloqueados_hasta IS
'Permite localizar usuarios con bloqueos temporales y revisar bloqueos vencidos.';


/*
------------------------------------------------------------
 Roles asignados a un usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuario_roles_usuario
ON auth.usuario_roles
(
    usuario_id
);

COMMENT ON INDEX auth.idx_usuario_roles_usuario IS
'Optimiza la consulta de roles asignados a un usuario.';


/*
------------------------------------------------------------
 Usuarios pertenecientes a un rol
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuario_roles_rol
ON auth.usuario_roles
(
    rol_id
);

COMMENT ON INDEX auth.idx_usuario_roles_rol IS
'Optimiza la consulta de usuarios asignados a un rol.';


/*
------------------------------------------------------------
 Asignaciones realizadas por otro usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_usuario_roles_asignado_por
ON auth.usuario_roles
(
    asignado_por
)
WHERE asignado_por IS NOT NULL;

COMMENT ON INDEX auth.idx_usuario_roles_asignado_por IS
'Facilita la auditoría de asignaciones de roles realizadas por administradores.';


/*
------------------------------------------------------------
 Permisos asociados a un rol
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol
ON auth.rol_permisos
(
    rol_id
);

COMMENT ON INDEX auth.idx_rol_permisos_rol IS
'Optimiza la carga de permisos asociados a un rol.';


/*
------------------------------------------------------------
 Roles asociados a un permiso
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_rol_permisos_permiso
ON auth.rol_permisos
(
    permiso_id
);

COMMENT ON INDEX auth.idx_rol_permisos_permiso IS
'Optimiza la consulta inversa de roles que contienen un permiso.';


/*
------------------------------------------------------------
 Sesiones activas por usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_sesiones_usuario_activas
ON auth.sesiones
(
    usuario_id,
    fecha_expiracion
)
WHERE activa = TRUE;

COMMENT ON INDEX auth.idx_sesiones_usuario_activas IS
'Optimiza la validación y administración de sesiones activas por usuario.';


/*
------------------------------------------------------------
 Sesiones que requieren expiración
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_sesiones_activas_expiracion
ON auth.sesiones
(
    fecha_expiracion
)
WHERE activa = TRUE;

COMMENT ON INDEX auth.idx_sesiones_activas_expiracion IS
'Permite localizar eficientemente sesiones activas que ya vencieron o están próximas a vencer.';


/*
------------------------------------------------------------
 Historial de aceptaciones por usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_aceptaciones_terminos_usuario_fecha
ON auth.aceptaciones_terminos
(
    usuario_id,
    fecha_aceptacion DESC
);

COMMENT ON INDEX auth.idx_aceptaciones_terminos_usuario_fecha IS
'Optimiza la consulta del historial de términos y privacidad aceptados por cada usuario.';


/*
============================================================
 2. ÍNDICES BASE DEL ESQUEMA ai
============================================================
*/

/*
------------------------------------------------------------
 Versiones de un modelo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_versiones_modelo_modelo
ON ai.versiones_modelo
(
    modelo_id,
    fecha_registro DESC
);

COMMENT ON INDEX ai.idx_versiones_modelo_modelo IS
'Optimiza el listado cronológico de versiones registradas para un modelo de IA.';


/*
------------------------------------------------------------
 Una sola versión activa por modelo
------------------------------------------------------------
*/

CREATE UNIQUE INDEX IF NOT EXISTS uq_version_activa_modelo
ON ai.versiones_modelo
(
    modelo_id
)
WHERE activa = TRUE;

COMMENT ON INDEX ai.uq_version_activa_modelo IS
'Garantiza que cada modelo de IA tenga como máximo una versión marcada como activa.';


/*
------------------------------------------------------------
 Modelos por tipo y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_modelos_ia_tipo_estado
ON ai.modelos_ia
(
    tipo,
    estado
);

COMMENT ON INDEX ai.idx_modelos_ia_tipo_estado IS
'Optimiza la selección de modelos disponibles según su tipo y estado.';


/*
============================================================
 3. ÍNDICES DEL ESQUEMA profile
============================================================
*/

/*
------------------------------------------------------------
 Cuestionarios por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_cuestionarios_estado
ON profile.cuestionarios
(
    estado
);

COMMENT ON INDEX profile.idx_cuestionarios_estado IS
'Optimiza la búsqueda de cuestionarios publicados, inactivos o en borrador.';


/*
------------------------------------------------------------
 Preguntas ordenadas de un cuestionario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_preguntas_cuestionario_orden
ON profile.preguntas
(
    cuestionario_id,
    orden
);

COMMENT ON INDEX profile.idx_preguntas_cuestionario_orden IS
'Optimiza la carga ordenada de preguntas pertenecientes a un cuestionario.';


/*
------------------------------------------------------------
 Opciones ordenadas de una pregunta
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_opciones_respuesta_pregunta_orden
ON profile.opciones_respuesta
(
    pregunta_id,
    orden
);

COMMENT ON INDEX profile.idx_opciones_respuesta_pregunta_orden IS
'Optimiza la carga ordenada de opciones para cada pregunta.';


/*
------------------------------------------------------------
 Evaluaciones de un usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evaluaciones_riesgo_usuario_fecha
ON profile.evaluaciones_riesgo
(
    usuario_id,
    fecha_evaluacion DESC
);

COMMENT ON INDEX profile.idx_evaluaciones_riesgo_usuario_fecha IS
'Optimiza la consulta del historial de evaluaciones de riesgo de un usuario.';


/*
------------------------------------------------------------
 Evaluaciones por cuestionario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evaluaciones_riesgo_cuestionario
ON profile.evaluaciones_riesgo
(
    cuestionario_id
);

COMMENT ON INDEX profile.idx_evaluaciones_riesgo_cuestionario IS
'Optimiza reportes de evaluaciones agrupadas por cuestionario.';


/*
------------------------------------------------------------
 Evaluaciones procesadas por una versión de modelo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evaluaciones_riesgo_version_modelo
ON profile.evaluaciones_riesgo
(
    version_modelo_id
)
WHERE version_modelo_id IS NOT NULL;

COMMENT ON INDEX profile.idx_evaluaciones_riesgo_version_modelo IS
'Permite identificar las evaluaciones procesadas por una versión específica de IA.';


/*
------------------------------------------------------------
 Respuestas por pregunta
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_respuestas_usuario_pregunta
ON profile.respuestas_usuario
(
    pregunta_id
);

COMMENT ON INDEX profile.idx_respuestas_usuario_pregunta IS
'Optimiza análisis estadísticos de las respuestas obtenidas para cada pregunta.';


/*
------------------------------------------------------------
 Respuestas por opción
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_respuestas_usuario_opcion
ON profile.respuestas_usuario
(
    opcion_id
)
WHERE opcion_id IS NOT NULL;

COMMENT ON INDEX profile.idx_respuestas_usuario_opcion IS
'Optimiza reportes sobre las opciones elegidas por los usuarios.';


/*
------------------------------------------------------------
 Perfiles por usuario e historial
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_perfiles_riesgo_usuario_fecha
ON profile.perfiles_riesgo
(
    usuario_id,
    fecha_inicio DESC
);

COMMENT ON INDEX profile.idx_perfiles_riesgo_usuario_fecha IS
'Optimiza la consulta histórica de perfiles de riesgo por usuario.';


/*
------------------------------------------------------------
 Un solo perfil vigente por usuario
------------------------------------------------------------
*/

CREATE UNIQUE INDEX IF NOT EXISTS uq_perfil_vigente_usuario
ON profile.perfiles_riesgo
(
    usuario_id
)
WHERE vigente = TRUE;

COMMENT ON INDEX profile.uq_perfil_vigente_usuario IS
'Garantiza que un usuario tenga como máximo un perfil de riesgo vigente.';


/*
------------------------------------------------------------
 Perfiles por clasificación
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_perfiles_riesgo_clasificacion
ON profile.perfiles_riesgo
(
    clasificacion
)
WHERE vigente = TRUE;

COMMENT ON INDEX profile.idx_perfiles_riesgo_clasificacion IS
'Optimiza consultas sobre la distribución actual de perfiles de riesgo.';


/*
============================================================
 4. ÍNDICES DEL ESQUEMA market
============================================================
*/

/*
------------------------------------------------------------
 Mercados activos
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_mercados_activos
ON market.mercados
(
    nombre
)
WHERE activo = TRUE;

COMMENT ON INDEX market.idx_mercados_activos IS
'Optimiza la carga del catálogo de mercados habilitados.';


/*
------------------------------------------------------------
 Tipos de activo habilitados
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_tipos_activo_activos
ON market.tipos_activo
(
    nombre
)
WHERE activo = TRUE;

COMMENT ON INDEX market.idx_tipos_activo_activos IS
'Optimiza la carga de tipos de activo habilitados.';


/*
------------------------------------------------------------
 Activos por tipo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_activos_tipo
ON market.activos
(
    tipo_activo_id
);

COMMENT ON INDEX market.idx_activos_tipo IS
'Optimiza la consulta de activos pertenecientes a una clase financiera.';


/*
------------------------------------------------------------
 Activos por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_activos_estado
ON market.activos
(
    estado
);

COMMENT ON INDEX market.idx_activos_estado IS
'Optimiza filtros de instrumentos activos, suspendidos o inactivos.';


/*
------------------------------------------------------------
 Activos por mercado y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_activos_mercado_estado
ON market.activos
(
    mercado_id,
    estado
);

COMMENT ON INDEX market.idx_activos_mercado_estado IS
'Optimiza la consulta de activos disponibles dentro de un mercado.';


/*
------------------------------------------------------------
 Activos por sector
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_activos_sector
ON market.activos
(
    sector
)
WHERE sector IS NOT NULL
  AND estado = 'ACTIVO';

COMMENT ON INDEX market.idx_activos_sector IS
'Optimiza filtros y agrupaciones de activos activos por sector económico.';


/*
------------------------------------------------------------
 Fuentes activas por prioridad
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_fuentes_financieras_activas_prioridad
ON market.fuentes_financieras
(
    prioridad,
    nombre
)
WHERE activa = TRUE;

COMMENT ON INDEX market.idx_fuentes_financieras_activas_prioridad IS
'Optimiza la selección de proveedores habilitados de acuerdo con su prioridad.';


/*
------------------------------------------------------------
 Precios históricos por activo y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_precios_historicos_activo_fecha
ON market.precios_historicos
(
    activo_id,
    fecha DESC
);

COMMENT ON INDEX market.idx_precios_historicos_activo_fecha IS
'Optimiza series de precios ordenadas desde la cotización más reciente.';


/*
------------------------------------------------------------
 Precios históricos por fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_precios_historicos_fecha
ON market.precios_historicos
(
    fecha DESC
);

COMMENT ON INDEX market.idx_precios_historicos_fecha IS
'Optimiza procesos masivos que consultan precios de todos los activos para una fecha.';


/*
------------------------------------------------------------
 Precios por fuente y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_precios_historicos_fuente_fecha
ON market.precios_historicos
(
    fuente_id,
    fecha DESC
);

COMMENT ON INDEX market.idx_precios_historicos_fuente_fecha IS
'Optimiza auditorías y verificaciones de datos cargados desde cada proveedor.';


/*
------------------------------------------------------------
 Indicadores por activo, tipo y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_indicadores_activo_tipo_fecha
ON market.indicadores_financieros
(
    activo_id,
    tipo_indicador,
    fecha DESC
);

COMMENT ON INDEX market.idx_indicadores_activo_tipo_fecha IS
'Optimiza la recuperación de series de indicadores técnicos por activo.';


/*
------------------------------------------------------------
 Indicadores por fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_indicadores_fecha
ON market.indicadores_financieros
(
    fecha DESC
);

COMMENT ON INDEX market.idx_indicadores_fecha IS
'Optimiza procesos de cálculo y análisis de indicadores correspondientes a una fecha.';


/*
------------------------------------------------------------
 Noticias por activo y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_noticias_activo_fecha
ON market.noticias_referencia
(
    activo_id,
    fecha_publicacion DESC
);

COMMENT ON INDEX market.idx_noticias_activo_fecha IS
'Optimiza la consulta de noticias recientes relacionadas con un activo.';


/*
------------------------------------------------------------
 Noticias por fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_noticias_fecha_publicacion
ON market.noticias_referencia
(
    fecha_publicacion DESC
);

COMMENT ON INDEX market.idx_noticias_fecha_publicacion IS
'Optimiza la consulta cronológica de noticias financieras recientes.';


/*
============================================================
 5. ÍNDICES DEL ESQUEMA portfolio
============================================================
*/

/*
------------------------------------------------------------
 Listas de seguimiento de un usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_listas_seguimiento_usuario
ON portfolio.listas_seguimiento
(
    usuario_id,
    activa
);

COMMENT ON INDEX portfolio.idx_listas_seguimiento_usuario IS
'Optimiza la consulta de listas activas e inactivas pertenecientes a un usuario.';


/*
------------------------------------------------------------
 Una lista predeterminada activa por usuario
------------------------------------------------------------
*/

CREATE UNIQUE INDEX IF NOT EXISTS uq_lista_predeterminada_usuario
ON portfolio.listas_seguimiento
(
    usuario_id
)
WHERE predeterminada = TRUE
  AND activa = TRUE;

COMMENT ON INDEX portfolio.uq_lista_predeterminada_usuario IS
'Garantiza que cada usuario tenga como máximo una lista predeterminada activa.';


/*
------------------------------------------------------------
 Listas que contienen un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_lista_activos_activo
ON portfolio.lista_activos
(
    activo_id
);

COMMENT ON INDEX portfolio.idx_lista_activos_activo IS
'Optimiza la consulta inversa de listas que contienen un activo determinado.';


/*
------------------------------------------------------------
 Alertas inferiores configuradas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_lista_activos_alerta_minimo
ON portfolio.lista_activos
(
    precio_alerta_minimo
)
WHERE precio_alerta_minimo IS NOT NULL;

COMMENT ON INDEX portfolio.idx_lista_activos_alerta_minimo IS
'Apoya el procesamiento de alertas cuando un precio desciende hasta un límite configurado.';


/*
------------------------------------------------------------
 Alertas superiores configuradas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_lista_activos_alerta_maximo
ON portfolio.lista_activos
(
    precio_alerta_maximo
)
WHERE precio_alerta_maximo IS NOT NULL;

COMMENT ON INDEX portfolio.idx_lista_activos_alerta_maximo IS
'Apoya el procesamiento de alertas cuando un precio alcanza un límite superior configurado.';


/*
------------------------------------------------------------
 Portafolios por usuario y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_portafolios_usuario_estado
ON portfolio.portafolios
(
    usuario_id,
    estado
);

COMMENT ON INDEX portfolio.idx_portafolios_usuario_estado IS
'Optimiza la consulta de portafolios activos, cerrados o archivados de un usuario.';


/*
------------------------------------------------------------
 Posiciones de un portafolio por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_posiciones_portafolio_estado
ON portfolio.posiciones
(
    portafolio_id,
    estado
);

COMMENT ON INDEX portfolio.idx_posiciones_portafolio_estado IS
'Optimiza la carga de posiciones abiertas o cerradas de un portafolio.';


/*
------------------------------------------------------------
 Portafolios que contienen un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_posiciones_activo_estado
ON portfolio.posiciones
(
    activo_id,
    estado
);

COMMENT ON INDEX portfolio.idx_posiciones_activo_estado IS
'Optimiza la consulta de portafolios que contienen posiciones en un activo.';


/*
------------------------------------------------------------
 Valoraciones históricas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_valoraciones_portafolio_fecha
ON portfolio.valoraciones_portafolio
(
    portafolio_id,
    fecha_hora DESC
);

COMMENT ON INDEX portfolio.idx_valoraciones_portafolio_fecha IS
'Optimiza la recuperación de la evolución histórica de un portafolio.';


/*
============================================================
 6. ÍNDICES DEL ESQUEMA simulation
============================================================
*/

/*
------------------------------------------------------------
 Configuraciones por usuario y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_configuraciones_usuario_estado
ON simulation.configuraciones
(
    usuario_id,
    estado
);

COMMENT ON INDEX simulation.idx_configuraciones_usuario_estado IS
'Optimiza la consulta de configuraciones de simulación pertenecientes a un usuario.';


/*
------------------------------------------------------------
 Configuraciones relacionadas con un portafolio
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_configuraciones_portafolio
ON simulation.configuraciones
(
    portafolio_id
)
WHERE portafolio_id IS NOT NULL;

COMMENT ON INDEX simulation.idx_configuraciones_portafolio IS
'Optimiza la consulta de simulaciones originadas desde un portafolio.';


/*
------------------------------------------------------------
 Configuraciones por tipo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_configuraciones_tipo_estado
ON simulation.configuraciones
(
    tipo_simulacion,
    estado
);

COMMENT ON INDEX simulation.idx_configuraciones_tipo_estado IS
'Optimiza reportes y filtros por metodología de simulación.';


/*
------------------------------------------------------------
 Configuraciones que incluyen un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_configuracion_activos_activo
ON simulation.configuracion_activos
(
    activo_id
);

COMMENT ON INDEX simulation.idx_configuracion_activos_activo IS
'Optimiza la consulta de configuraciones que incluyen un activo específico.';


/*
------------------------------------------------------------
 Ejecuciones por configuración y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_simulacion_configuracion_fecha
ON simulation.ejecuciones
(
    configuracion_id,
    fecha_solicitud DESC
);

COMMENT ON INDEX simulation.idx_ejecuciones_simulacion_configuracion_fecha IS
'Optimiza el historial de ejecuciones correspondientes a una configuración.';


/*
------------------------------------------------------------
 Ejecuciones por usuario y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_simulacion_usuario_estado
ON simulation.ejecuciones
(
    usuario_id,
    estado,
    fecha_solicitud DESC
);

COMMENT ON INDEX simulation.idx_ejecuciones_simulacion_usuario_estado IS
'Optimiza la consulta de ejecuciones de simulación de un usuario por estado.';


/*
------------------------------------------------------------
 Cola de simulaciones pendientes
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_simulacion_pendientes
ON simulation.ejecuciones
(
    fecha_solicitud
)
WHERE estado = 'PENDIENTE';

COMMENT ON INDEX simulation.idx_ejecuciones_simulacion_pendientes IS
'Optimiza la selección de simulaciones pendientes por orden de solicitud.';


/*
------------------------------------------------------------
 Simulaciones activas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_simulacion_activas
ON simulation.ejecuciones
(
    fecha_inicio
)
WHERE estado = 'EJECUTANDO';

COMMENT ON INDEX simulation.idx_ejecuciones_simulacion_activas IS
'Facilita la supervisión de simulaciones actualmente en ejecución.';


/*
------------------------------------------------------------
 Ejecuciones por versión del modelo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_simulacion_modelo
ON simulation.ejecuciones
(
    version_modelo_id
)
WHERE version_modelo_id IS NOT NULL;

COMMENT ON INDEX simulation.idx_ejecuciones_simulacion_modelo IS
'Permite analizar qué ejecuciones utilizaron una versión específica de IA.';


/*
------------------------------------------------------------
 Resultados que incluyen un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_resultados_activo_activo
ON simulation.resultados_activo
(
    activo_id
);

COMMENT ON INDEX simulation.idx_resultados_activo_activo IS
'Optimiza análisis históricos de resultados de simulación para un activo.';


/*
============================================================
 7. ÍNDICES DE ANÁLISIS DEL ESQUEMA ai
============================================================
*/

/*
------------------------------------------------------------
 Solicitudes por usuario y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_usuario_fecha
ON ai.solicitudes_analisis
(
    usuario_id,
    fecha_solicitud DESC
);

COMMENT ON INDEX ai.idx_solicitudes_analisis_usuario_fecha IS
'Optimiza el historial de análisis solicitados por un usuario.';


/*
------------------------------------------------------------
 Solicitudes por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_estado_fecha
ON ai.solicitudes_analisis
(
    estado,
    fecha_solicitud
);

COMMENT ON INDEX ai.idx_solicitudes_analisis_estado_fecha IS
'Optimiza búsquedas operativas de solicitudes según su estado.';


/*
------------------------------------------------------------
 Cola de análisis pendientes
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_pendientes
ON ai.solicitudes_analisis
(
    fecha_solicitud
)
WHERE estado = 'PENDIENTE';

COMMENT ON INDEX ai.idx_solicitudes_analisis_pendientes IS
'Optimiza la selección de solicitudes de IA pendientes de procesamiento.';


/*
------------------------------------------------------------
 Análisis actualmente en ejecución
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_activas
ON ai.solicitudes_analisis
(
    fecha_inicio
)
WHERE estado = 'EJECUTANDO';

COMMENT ON INDEX ai.idx_solicitudes_analisis_activas IS
'Facilita la supervisión de solicitudes de IA en ejecución.';


/*
------------------------------------------------------------
 Solicitudes relacionadas con portafolios
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_portafolio
ON ai.solicitudes_analisis
(
    portafolio_id,
    fecha_solicitud DESC
)
WHERE portafolio_id IS NOT NULL;

COMMENT ON INDEX ai.idx_solicitudes_analisis_portafolio IS
'Optimiza el historial de análisis realizados sobre un portafolio.';


/*
------------------------------------------------------------
 Solicitudes relacionadas con perfiles
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_perfil
ON ai.solicitudes_analisis
(
    perfil_riesgo_id
)
WHERE perfil_riesgo_id IS NOT NULL;

COMMENT ON INDEX ai.idx_solicitudes_analisis_perfil IS
'Optimiza consultas de análisis personalizados mediante un perfil de riesgo.';


/*
------------------------------------------------------------
 Solicitudes expirables
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_solicitudes_analisis_expiracion
ON ai.solicitudes_analisis
(
    fecha_expiracion
)
WHERE fecha_expiracion IS NOT NULL
  AND estado = 'COMPLETADA';

COMMENT ON INDEX ai.idx_solicitudes_analisis_expiracion IS
'Facilita la identificación de análisis completados que han quedado desactualizados.';


/*
------------------------------------------------------------
 Predicciones históricas de un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_predicciones_activo_fechas
ON ai.predicciones_activo
(
    activo_id,
    fecha_base DESC,
    fecha_objetivo
);

COMMENT ON INDEX ai.idx_predicciones_activo_fechas IS
'Optimiza el historial de predicciones generadas para un activo.';


/*
------------------------------------------------------------
 Predicciones por modelo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_predicciones_version_modelo
ON ai.predicciones_activo
(
    version_modelo_id
);

COMMENT ON INDEX ai.idx_predicciones_version_modelo IS
'Permite analizar las predicciones generadas por una versión específica del modelo.';


/*
------------------------------------------------------------
 Predicciones por tendencia
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_predicciones_tendencia_confianza
ON ai.predicciones_activo
(
    tendencia,
    confianza DESC
);

COMMENT ON INDEX ai.idx_predicciones_tendencia_confianza IS
'Optimiza consultas de predicciones por tendencia y nivel de confianza.';


/*
------------------------------------------------------------
 Sentimiento por activo y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_sentimiento_activo_fecha
ON ai.analisis_sentimiento
(
    activo_id,
    fecha_analisis DESC
)
WHERE activo_id IS NOT NULL;

COMMENT ON INDEX ai.idx_sentimiento_activo_fecha IS
'Optimiza la consulta cronológica del sentimiento relacionado con un activo.';


/*
------------------------------------------------------------
 Sentimiento por noticia
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_sentimiento_noticia
ON ai.analisis_sentimiento
(
    noticia_referencia_id
)
WHERE noticia_referencia_id IS NOT NULL;

COMMENT ON INDEX ai.idx_sentimiento_noticia IS
'Optimiza la localización de análisis realizados sobre una noticia concreta.';


/*
------------------------------------------------------------
 Sentimiento por clasificación
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_sentimiento_clasificacion_fecha
ON ai.analisis_sentimiento
(
    sentimiento,
    fecha_analisis DESC
);

COMMENT ON INDEX ai.idx_sentimiento_clasificacion_fecha IS
'Optimiza análisis agregados de sentimiento positivo, neutral o negativo.';


/*
------------------------------------------------------------
 Recomendaciones por usuario y estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_recomendaciones_usuario_estado_fecha
ON ai.recomendaciones
(
    usuario_id,
    estado,
    fecha_generacion DESC
);

COMMENT ON INDEX ai.idx_recomendaciones_usuario_estado_fecha IS
'Optimiza la consulta de recomendaciones de un usuario según su estado.';


/*
------------------------------------------------------------
 Recomendaciones vinculadas a portafolios
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_recomendaciones_portafolio_fecha
ON ai.recomendaciones
(
    portafolio_id,
    fecha_generacion DESC
)
WHERE portafolio_id IS NOT NULL;

COMMENT ON INDEX ai.idx_recomendaciones_portafolio_fecha IS
'Optimiza el historial de recomendaciones asociadas con un portafolio.';


/*
------------------------------------------------------------
 Recomendaciones pendientes y vigentes
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_recomendaciones_vigentes
ON ai.recomendaciones
(
    usuario_id,
    fecha_expiracion,
    prioridad
)
WHERE estado IN
(
    'GENERADA',
    'MOSTRADA'
);

COMMENT ON INDEX ai.idx_recomendaciones_vigentes IS
'Optimiza la consulta de recomendaciones pendientes de decisión y todavía vigentes.';


/*
------------------------------------------------------------
 Recomendaciones por modelo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_recomendaciones_version_modelo
ON ai.recomendaciones
(
    version_modelo_id
);

COMMENT ON INDEX ai.idx_recomendaciones_version_modelo IS
'Permite evaluar recomendaciones generadas por una versión determinada del modelo.';


/*
------------------------------------------------------------
 Recomendaciones relacionadas con un activo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_recomendacion_activos_activo
ON ai.recomendacion_activos
(
    activo_id
);

COMMENT ON INDEX ai.idx_recomendacion_activos_activo IS
'Optimiza la consulta de recomendaciones relacionadas con un activo.';


/*
------------------------------------------------------------
 Evidencias de una solicitud por tipo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evidencias_solicitud_tipo
ON ai.evidencias_analisis
(
    solicitud_id,
    tipo_evidencia
);

COMMENT ON INDEX ai.idx_evidencias_solicitud_tipo IS
'Optimiza la explicación de resultados agrupando evidencias por tipo.';


/*
------------------------------------------------------------
 Evidencias de una recomendación
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evidencias_recomendacion
ON ai.evidencias_analisis
(
    recomendacion_id,
    peso DESC
)
WHERE recomendacion_id IS NOT NULL;

COMMENT ON INDEX ai.idx_evidencias_recomendacion IS
'Optimiza la recuperación de evidencias de una recomendación ordenadas por importancia.';


/*
------------------------------------------------------------
 Evidencias de una predicción
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_evidencias_prediccion
ON ai.evidencias_analisis
(
    prediccion_id,
    peso DESC
)
WHERE prediccion_id IS NOT NULL;

COMMENT ON INDEX ai.idx_evidencias_prediccion IS
'Optimiza la recuperación de evidencias de una predicción ordenadas por importancia.';


/*
============================================================
 8. ÍNDICES DEL ESQUEMA audit
============================================================
*/

/*
------------------------------------------------------------
 Auditoría por usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_registros_auditoria_usuario_fecha
ON audit.registros_auditoria
(
    usuario_id,
    fecha_evento DESC
)
WHERE usuario_id IS NOT NULL;

COMMENT ON INDEX audit.idx_registros_auditoria_usuario_fecha IS
'Optimiza la consulta cronológica de acciones realizadas por un usuario.';


/*
------------------------------------------------------------
 Auditoría de una entidad
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_registros_auditoria_entidad_registro
ON audit.registros_auditoria
(
    esquema_entidad,
    nombre_entidad,
    registro_id,
    fecha_evento DESC
);

COMMENT ON INDEX audit.idx_registros_auditoria_entidad_registro IS
'Optimiza la recuperación del historial completo de un registro o entidad.';


/*
------------------------------------------------------------
 Correlación por solicitud
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_registros_auditoria_solicitud
ON audit.registros_auditoria
(
    identificador_solicitud
)
WHERE identificador_solicitud IS NOT NULL;

COMMENT ON INDEX audit.idx_registros_auditoria_solicitud IS
'Permite localizar las acciones asociadas con una petición o flujo de ejecución.';


/*
------------------------------------------------------------
 Auditoría por acción
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_registros_auditoria_accion_fecha
ON audit.registros_auditoria
(
    accion,
    fecha_evento DESC
);

COMMENT ON INDEX audit.idx_registros_auditoria_accion_fecha IS
'Optimiza reportes de auditoría agrupados por tipo de acción.';


/*
------------------------------------------------------------
 Eventos de seguridad por fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_eventos_seguridad_fecha
ON audit.eventos_seguridad
(
    fecha_evento DESC
);

COMMENT ON INDEX audit.idx_eventos_seguridad_fecha IS
'Optimiza la supervisión cronológica de eventos de seguridad.';


/*
------------------------------------------------------------
 Eventos de seguridad por usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_eventos_seguridad_usuario_fecha
ON audit.eventos_seguridad
(
    usuario_id,
    fecha_evento DESC
)
WHERE usuario_id IS NOT NULL;

COMMENT ON INDEX audit.idx_eventos_seguridad_usuario_fecha IS
'Optimiza la investigación del historial de seguridad de un usuario.';


/*
------------------------------------------------------------
 Eventos por correo intentado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_eventos_seguridad_correo_fecha
ON audit.eventos_seguridad
(
    correo_intentado,
    fecha_evento DESC
)
WHERE correo_intentado IS NOT NULL;

COMMENT ON INDEX audit.idx_eventos_seguridad_correo_fecha IS
'Optimiza la detección de múltiples intentos sobre una dirección de correo.';


/*
------------------------------------------------------------
 Eventos pendientes de revisión
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_eventos_seguridad_pendientes_revision
ON audit.eventos_seguridad
(
    severidad,
    fecha_evento
)
WHERE revisado = FALSE;

COMMENT ON INDEX audit.idx_eventos_seguridad_pendientes_revision IS
'Optimiza la cola de eventos de seguridad que todavía deben revisarse.';


/*
------------------------------------------------------------
 Errores por nivel y fecha
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_errores_aplicacion_nivel_fecha
ON audit.errores_aplicacion
(
    nivel,
    fecha_error DESC
);

COMMENT ON INDEX audit.idx_errores_aplicacion_nivel_fecha IS
'Optimiza la supervisión de errores por nivel de gravedad.';


/*
------------------------------------------------------------
 Errores por servicio
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_errores_aplicacion_servicio_fecha
ON audit.errores_aplicacion
(
    servicio,
    fecha_error DESC
);

COMMENT ON INDEX audit.idx_errores_aplicacion_servicio_fecha IS
'Optimiza el análisis de errores agrupados por servicio.';


/*
------------------------------------------------------------
 Errores pendientes de resolución
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_errores_aplicacion_pendientes
ON audit.errores_aplicacion
(
    nivel,
    fecha_error
)
WHERE resuelto = FALSE;

COMMENT ON INDEX audit.idx_errores_aplicacion_pendientes IS
'Optimiza la cola de errores que todavía no han sido resueltos.';


/*
------------------------------------------------------------
 Errores por identificador de solicitud
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_errores_aplicacion_solicitud
ON audit.errores_aplicacion
(
    identificador_solicitud
)
WHERE identificador_solicitud IS NOT NULL;

COMMENT ON INDEX audit.idx_errores_aplicacion_solicitud IS
'Permite correlacionar errores técnicos con una solicitud específica.';


/*
------------------------------------------------------------
 Errores por identificador de proceso
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_errores_aplicacion_proceso
ON audit.errores_aplicacion
(
    identificador_proceso
)
WHERE identificador_proceso IS NOT NULL;

COMMENT ON INDEX audit.idx_errores_aplicacion_proceso IS
'Permite correlacionar errores técnicos con procesos de segundo plano.';


/*
============================================================
 9. ÍNDICES DEL ESQUEMA operation
============================================================
*/

/*
------------------------------------------------------------
 Notificaciones de un usuario
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_fecha
ON operation.notificaciones
(
    usuario_id,
    fecha_creacion DESC
);

COMMENT ON INDEX operation.idx_notificaciones_usuario_fecha IS
'Optimiza la consulta cronológica de notificaciones de un usuario.';


/*
------------------------------------------------------------
 Notificaciones no leídas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_notificaciones_usuario_no_leidas
ON operation.notificaciones
(
    usuario_id,
    fecha_envio DESC
)
WHERE fecha_envio IS NOT NULL
  AND fecha_lectura IS NULL
  AND estado = 'ENVIADA';

COMMENT ON INDEX operation.idx_notificaciones_usuario_no_leidas IS
'Optimiza la consulta de notificaciones enviadas que todavía no han sido leídas.';


/*
------------------------------------------------------------
 Cola de notificaciones pendientes
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_notificaciones_pendientes
ON operation.notificaciones
(
    fecha_programada,
    prioridad,
    fecha_creacion
)
WHERE estado IN
(
    'PENDIENTE',
    'PROGRAMADA'
);

COMMENT ON INDEX operation.idx_notificaciones_pendientes IS
'Optimiza la selección de notificaciones pendientes o programadas para envío.';


/*
------------------------------------------------------------
 Notificaciones fallidas
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_notificaciones_fallidas
ON operation.notificaciones
(
    fecha_creacion
)
WHERE estado = 'FALLIDA';

COMMENT ON INDEX operation.idx_notificaciones_fallidas IS
'Facilita la supervisión y posible reintento de notificaciones fallidas.';


/*
------------------------------------------------------------
 Referencia de una notificación
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_notificaciones_referencia
ON operation.notificaciones
(
    referencia_tipo,
    referencia_id
)
WHERE referencia_tipo IS NOT NULL
  AND referencia_id IS NOT NULL;

COMMENT ON INDEX operation.idx_notificaciones_referencia IS
'Optimiza la consulta de notificaciones relacionadas con una entidad del sistema.';


/*
------------------------------------------------------------
 Trabajos activos próximos a ejecutarse
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_trabajos_programados_activos
ON operation.trabajos_programados
(
    siguiente_ejecucion
)
WHERE activo = TRUE
  AND tipo IN ('CRON', 'INTERVALO');

COMMENT ON INDEX operation.idx_trabajos_programados_activos IS
'Optimiza la selección de trabajos automáticos activos próximos a ejecutarse.';


/*
------------------------------------------------------------
 Trabajos por tipo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_trabajos_programados_tipo_activo
ON operation.trabajos_programados
(
    tipo,
    activo
);

COMMENT ON INDEX operation.idx_trabajos_programados_tipo_activo IS
'Optimiza filtros de trabajos manuales, CRON o por intervalo.';


/*
------------------------------------------------------------
 Ejecuciones históricas de un trabajo
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_trabajo_fecha
ON operation.ejecuciones_trabajo
(
    trabajo_id,
    fecha_solicitud DESC
);

COMMENT ON INDEX operation.idx_ejecuciones_trabajo_fecha IS
'Optimiza el historial cronológico de ejecuciones de un trabajo.';


/*
------------------------------------------------------------
 Ejecuciones por estado
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_trabajo_estado
ON operation.ejecuciones_trabajo
(
    estado,
    fecha_solicitud
);

COMMENT ON INDEX operation.idx_ejecuciones_trabajo_estado IS
'Optimiza la supervisión de ejecuciones según su estado.';


/*
------------------------------------------------------------
 Cola de trabajos pendientes
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_trabajo_pendientes
ON operation.ejecuciones_trabajo
(
    fecha_programada,
    fecha_solicitud
)
WHERE estado = 'PENDIENTE';

COMMENT ON INDEX operation.idx_ejecuciones_trabajo_pendientes IS
'Optimiza la selección de ejecuciones pendientes de trabajos programados.';


/*
------------------------------------------------------------
 Trabajos actualmente en ejecución
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_ejecuciones_trabajo_activas
ON operation.ejecuciones_trabajo
(
    fecha_inicio
)
WHERE estado = 'EJECUTANDO';

COMMENT ON INDEX operation.idx_ejecuciones_trabajo_activas IS
'Facilita la supervisión de trabajos que están siendo procesados.';


/*
------------------------------------------------------------
 Bloqueos adquiridos próximos a expirar
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_control_procesos_expiracion
ON operation.control_procesos
(
    fecha_expiracion
)
WHERE estado = 'ADQUIRIDO';

COMMENT ON INDEX operation.idx_control_procesos_expiracion IS
'Optimiza la detección de bloqueos activos vencidos o próximos a vencer.';


/*
------------------------------------------------------------
 Bloqueos por tipo de proceso
------------------------------------------------------------
*/

CREATE INDEX IF NOT EXISTS idx_control_procesos_tipo_estado
ON operation.control_procesos
(
    tipo_proceso,
    estado
);

COMMENT ON INDEX operation.idx_control_procesos_tipo_estado IS
'Optimiza la consulta de bloqueos según el tipo y estado del proceso.';


/*
============================================================
 10. CONFIRMACIÓN
============================================================
*/

COMMIT;