# ESPECIFICACIÓN DE REQUISITOS DE SOFTWARE

## AlphaInvest AI

**Sistema web inteligente de apoyo para la toma de decisiones de inversión mediante aprendizaje automático y arquitectura distribuida**

---

## Control del documento

| Campo                | Información                                            |
| -------------------- | ------------------------------------------------------ |
| Nombre del proyecto  | AlphaInvest AI                                         |
| Tipo de documento    | Especificación de Requisitos de Software               |
| Versión              | 0.1                                                    |
| Estado               | Borrador inicial                                       |
| Carrera              | Ingeniería Informática                                 |
| Centro universitario | Centro Universitario de Ciencias Exactas e Ingenierías |
| Institución          | Universidad de Guadalajara                             |
| Metodología          | Scrum                                                  |
| Tipo de sistema      | Aplicación web distribuida                             |
| Fecha                | Julio de 2026                                          |

---

# 1. Introducción

## 1.1 Propósito

El presente documento tiene como propósito establecer los requisitos funcionales, no funcionales, reglas de negocio, restricciones, actores y características generales de AlphaInvest AI.

AlphaInvest AI será una plataforma web orientada a inversionistas principiantes e intermedios. El sistema integrará información financiera, datos históricos del mercado, noticias económicas, indicadores bursátiles y modelos de aprendizaje automático para generar análisis, simulaciones y recomendaciones explicables.

Este documento funcionará como referencia para el diseño de la arquitectura, el desarrollo de los servicios, la construcción de las bases de datos, la implementación de la interfaz web, la creación de los modelos de inteligencia artificial y la ejecución de pruebas.

## 1.2 Problema identificado

Los inversionistas principiantes suelen consultar diferentes plataformas para obtener precios, noticias, reportes empresariales, indicadores financieros e información histórica.

La información se encuentra distribuida entre numerosas fuentes y puede ser difícil de interpretar para una persona que no cuenta con conocimientos avanzados sobre mercados financieros.

Además, algunas plataformas presentan datos financieros sin explicar claramente cómo se relacionan factores como la volatilidad, el rendimiento histórico, las noticias, los resultados trimestrales, el riesgo y el horizonte de inversión.

Esta situación puede ocasionar que los usuarios tomen decisiones basadas en información incompleta, tendencias de redes sociales o recomendaciones sin suficiente fundamento.

## 1.3 Solución propuesta

AlphaInvest AI centralizará información financiera proveniente de servicios externos y aplicará técnicas de análisis de datos, minería de datos, procesamiento de lenguaje natural y aprendizaje automático.

El sistema permitirá que el usuario:

- Consulte información financiera de empresas y fondos cotizados.
- Revise noticias relacionadas con empresas y mercados.
- Identifique el sentimiento de las noticias.
- Obtenga una clasificación de riesgo.
- Consulte tendencias estimadas mediante modelos de aprendizaje automático.
- Genere portafolios virtuales.
- Simule inversiones históricas.
- Compare escenarios de inversión.
- Reciba explicaciones sobre los factores considerados por los modelos.

AlphaInvest AI será una herramienta de apoyo informativo y educativo. No ejecutará operaciones bursátiles ni garantizará rendimientos.

## 1.4 Objetivo general

Desarrollar una plataforma web inteligente que integre datos financieros, noticias económicas, indicadores bursátiles y modelos de aprendizaje automático para generar análisis explicables, clasificaciones de riesgo y simulaciones de inversión dirigidas a inversionistas principiantes e intermedios.

## 1.5 Objetivos específicos

### OE-001

Implementar un sistema de registro, autenticación y administración de usuarios mediante mecanismos seguros.

### OE-002

Determinar el perfil de riesgo del usuario considerando su experiencia, objetivos, horizonte de inversión y tolerancia a pérdidas.

### OE-003

Consultar información financiera e histórica de acciones y fondos cotizados mediante servicios externos.

### OE-004

Recopilar y procesar noticias económicas relacionadas con empresas y mercados financieros.

### OE-005

Clasificar el sentimiento de las noticias financieras mediante procesamiento de lenguaje natural.

### OE-006

Calcular indicadores de rendimiento, volatilidad y riesgo para los activos analizados.

### OE-007

Aplicar algoritmos de aprendizaje automático para clasificar el riesgo y estimar tendencias financieras.

### OE-008

Generar recomendaciones explicables basadas en datos históricos, indicadores financieros, noticias y perfil del usuario.

### OE-009

Permitir la creación y administración de portafolios virtuales.

### OE-010

Implementar un simulador histórico que permita evaluar el comportamiento hipotético de una inversión.

### OE-011

Presentar resultados mediante gráficas, tablas, indicadores y estadísticas comprensibles.

### OE-012

Implementar una arquitectura distribuida basada en servicios desplegados en infraestructura de nube.

## 1.6 Alcance

La primera versión de AlphaInvest AI incluirá:

- Registro e inicio de sesión.
- Administración básica del perfil del usuario.
- Cuestionario para determinar el perfil de riesgo.
- Consulta de acciones de empresas estadounidenses.
- Consulta de fondos cotizados o ETF.
- Consulta de precios e información histórica.
- Consulta de indicadores financieros.
- Obtención y clasificación de noticias.
- Creación de listas de seguimiento.
- Creación de portafolios virtuales.
- Simulación histórica de inversiones.
- Clasificación de riesgo de activos.
- Estimación de tendencias mediante aprendizaje automático.
- Generación de recomendaciones explicables.
- Visualización de estadísticas.
- Historial de simulaciones y análisis.
- Panel administrativo básico.
- Registro de eventos y errores del sistema.

## 1.7 Funciones fuera del alcance

La primera versión no realizará las siguientes funciones:

- Compra o venta real de acciones.
- Conexión directa con casas de bolsa.
- Administración de dinero real.
- Transferencias financieras.
- Custodia de activos.
- Garantía de rendimientos.
- Operaciones automáticas de trading.
- Trading de alta frecuencia.
- Análisis de opciones financieras.
- Análisis de futuros financieros.
- Operaciones en Forex.
- Declaraciones fiscales.
- Sustitución de un asesor financiero certificado.
- Diagnóstico definitivo sobre el comportamiento futuro de un activo.

## 1.8 Advertencia financiera

Los análisis, clasificaciones, simulaciones y recomendaciones producidos por AlphaInvest AI tendrán fines informativos, educativos y académicos.

Los resultados no deberán interpretarse como una garantía de rendimiento ni como asesoría financiera profesional.

El usuario será responsable de verificar la información y tomar sus propias decisiones.

---

# 2. Descripción general

## 2.1 Perspectiva del producto

AlphaInvest AI será una aplicación web responsiva basada en una arquitectura distribuida.

El frontend se comunicará con una puerta de enlace o API Gateway. La puerta de enlace dirigirá las solicitudes hacia distintos servicios funcionales.

Los servicios principales serán:

- Servicio de autenticación.
- Servicio de mercado.
- Servicio de noticias.
- Servicio de inteligencia artificial.
- Servicio de simulación.
- Servicio de portafolios.
- Servicio de notificaciones.

El sistema utilizará una base de datos relacional para información estructurada y una base de datos documental para noticias, resultados de procesamiento y registros técnicos.

## 2.2 Arquitectura general

La solución estará formada por los siguientes componentes:

### Frontend

Aplicación web desarrollada con React y TypeScript.

### API Gateway

Punto principal de comunicación entre la interfaz web y los servicios internos.

### Servicio de autenticación

Responsable del registro, inicio de sesión, recuperación de acceso, autorización y administración de perfiles.

### Servicio de mercado

Responsable de consultar, procesar y proporcionar información financiera.

### Servicio de noticias

Responsable de recopilar, almacenar y consultar noticias económicas.

### Servicio de inteligencia artificial

Responsable de ejecutar los modelos de perfil de riesgo, clasificación de activos, análisis de sentimiento y estimación de tendencias.

### Servicio de simulación

Responsable de calcular escenarios históricos y métricas de portafolios.

### Servicio de portafolios

Responsable de administrar portafolios virtuales, activos y listas de seguimiento.

### Servicios externos

APIs financieras, fuentes de noticias y repositorios públicos de reportes empresariales.

## 2.3 Usuarios del sistema

### Usuario inversionista

Persona interesada en consultar información financiera, analizar activos, crear portafolios virtuales y ejecutar simulaciones.

### Administrador

Persona encargada de consultar usuarios, revisar registros, monitorear servicios y administrar elementos generales del sistema.

### Servicios externos

Sistemas que proporcionan precios, información financiera, reportes empresariales o noticias.

## 2.4 Características de los usuarios

El usuario objetivo podrá tener conocimientos financieros básicos o intermedios.

No será obligatorio que conozca algoritmos de aprendizaje automático, análisis técnico avanzado o arquitectura de sistemas.

La interfaz deberá presentar explicaciones claras, reducir el uso de términos financieros innecesariamente complejos y mostrar advertencias cuando exista incertidumbre en los resultados.

## 2.5 Entorno operativo

La plataforma podrá utilizarse desde navegadores web modernos en computadoras, tabletas y teléfonos inteligentes.

El sistema será desplegado en servicios de nube y no dependerá de la configuración de un servidor local para su operación final.

## 2.6 Suposiciones y dependencias

El funcionamiento del sistema dependerá de:

- Disponibilidad de las APIs financieras.
- Disponibilidad de las fuentes de noticias.
- Calidad de los datos históricos.
- Límites de consulta establecidos por proveedores externos.
- Conectividad a Internet.
- Disponibilidad de los servicios de nube.
- Disponibilidad de los modelos de aprendizaje automático desplegados.

## 2.7 Restricciones generales

- La aplicación deberá operar mediante Internet.
- Las claves de las APIs no deberán almacenarse directamente en el código.
- Los servicios deberán comunicarse mediante interfaces documentadas.
- La aplicación no deberá ejecutar operaciones financieras reales.
- La plataforma deberá señalar que sus resultados son informativos.
- La arquitectura final deberá distribuir funciones en diferentes servicios.
- Los modelos deberán evaluarse con datos suficientes y métricas documentadas.
- El sistema deberá almacenar trazabilidad de los análisis realizados.

---

# 3. Actores

## 3.1 Usuario

El usuario podrá:

- Registrarse.
- Iniciar y cerrar sesión.
- Recuperar el acceso a su cuenta.
- Completar su perfil.
- Realizar el cuestionario de riesgo.
- Consultar activos.
- Consultar noticias.
- Crear portafolios.
- Crear listas de seguimiento.
- Ejecutar simulaciones.
- Solicitar análisis mediante inteligencia artificial.
- Consultar explicaciones.
- Revisar su historial.

## 3.2 Administrador

El administrador podrá:

- Iniciar sesión.
- Consultar usuarios.
- Cambiar el estado de una cuenta.
- Consultar estadísticas generales.
- Consultar registros de auditoría.
- Revisar errores de integración.
- Consultar el estado de los servicios.
- Administrar catálogos autorizados.
- Consultar información sobre versiones de modelos.

## 3.3 Servicios externos

Los servicios externos podrán proporcionar:

- Precios actuales.
- Datos históricos.
- Indicadores financieros.
- Información empresarial.
- Noticias financieras.
- Reportes financieros.
- Calendarios de resultados trimestrales.

---

# 4. Módulos funcionales

## 4.1 Autenticación y usuarios

Gestionará el registro, inicio de sesión, recuperación de acceso, roles, sesiones y perfiles.

## 4.2 Perfil de inversión

Administrará el cuestionario financiero y la clasificación del usuario como conservador, moderado o agresivo.

## 4.3 Mercado

Permitirá buscar empresas y consultar precios, indicadores e información histórica.

## 4.4 Noticias

Permitirá consultar noticias financieras, identificar empresas relacionadas y mostrar el sentimiento estimado.

## 4.5 Inteligencia artificial

Ejecutará modelos de clasificación de riesgo, análisis de sentimiento, estimación de tendencias y generación de explicaciones.

## 4.6 Portafolios

Permitirá crear portafolios virtuales y administrar sus activos.

## 4.7 Watchlist

Permitirá guardar activos para darles seguimiento sin agregarlos a un portafolio.

## 4.8 Simulación

Permitirá evaluar escenarios hipotéticos utilizando precios históricos.

## 4.9 Recomendaciones

Combinará el perfil del usuario, indicadores, riesgo, noticias y resultados de los modelos para presentar una orientación explicable.

## 4.10 Administración

Permitirá revisar usuarios, servicios, auditorías, errores y estadísticas del sistema.

---

# 5. Requerimientos funcionales

## 5.1 Autenticación

### RF-001 — Registrar usuario

El sistema deberá permitir el registro de un usuario mediante nombre, correo electrónico y contraseña.

### RF-002 — Validar correo único

El sistema deberá verificar que el correo electrónico no se encuentre asociado con otra cuenta.

### RF-003 — Validar contraseña

El sistema deberá verificar que la contraseña cumpla los requisitos mínimos de seguridad.

### RF-004 — Iniciar sesión

El sistema deberá permitir que un usuario registrado inicie sesión mediante correo electrónico y contraseña.

### RF-005 — Cerrar sesión

El sistema deberá permitir que el usuario cierre su sesión activa.

### RF-006 — Recuperar acceso

El sistema deberá proporcionar un mecanismo para recuperar el acceso a una cuenta.

### RF-007 — Renovar sesión

El sistema deberá permitir renovar una sesión válida sin solicitar nuevamente las credenciales dentro del periodo autorizado.

### RF-008 — Consultar perfil

El sistema deberá permitir que el usuario consulte la información de su perfil.

### RF-009 — Actualizar perfil

El sistema deberá permitir que el usuario actualice la información permitida de su perfil.

### RF-010 — Desactivar cuenta

El sistema deberá permitir que el usuario solicite la desactivación de su cuenta.

## 5.2 Perfil de inversión

### RF-011 — Contestar cuestionario

El sistema deberá permitir que el usuario responda un cuestionario relacionado con sus objetivos y tolerancia al riesgo.

### RF-012 — Clasificar perfil de riesgo

El sistema deberá clasificar al usuario dentro de un perfil conservador, moderado o agresivo.

### RF-013 — Explicar perfil de riesgo

El sistema deberá mostrar los factores principales que influyeron en la clasificación del perfil.

### RF-014 — Actualizar perfil de riesgo

El sistema deberá permitir que el usuario vuelva a responder el cuestionario.

### RF-015 — Consultar historial de perfiles

El sistema deberá conservar las clasificaciones anteriores del usuario para fines de trazabilidad.

## 5.3 Mercado

### RF-016 — Buscar activo

El sistema deberá permitir buscar activos mediante símbolo bursátil o nombre de la empresa.

### RF-017 — Consultar empresa

El sistema deberá mostrar nombre, símbolo, sector, industria, mercado, país y descripción de una empresa.

### RF-018 — Consultar precio

El sistema deberá mostrar el precio disponible más reciente del activo.

### RF-019 — Consultar datos históricos

El sistema deberá permitir consultar precios históricos dentro de periodos definidos.

### RF-020 — Consultar indicadores

El sistema deberá mostrar indicadores financieros disponibles, como beta, capitalización, utilidad por acción y relación precio-utilidad.

### RF-021 — Consultar rendimiento

El sistema deberá calcular el rendimiento de un activo para periodos seleccionados.

### RF-022 — Consultar volatilidad

El sistema deberá calcular una medida de volatilidad utilizando datos históricos.

### RF-023 — Comparar activos

El sistema deberá permitir comparar como mínimo dos activos mediante indicadores y rendimientos históricos.

### RF-024 — Actualizar datos financieros

El sistema deberá actualizar la información financiera respetando los límites de las APIs externas.

## 5.4 Noticias

### RF-025 — Consultar noticias

El sistema deberá mostrar noticias financieras relacionadas con empresas o mercados.

### RF-026 — Filtrar noticias

El sistema deberá permitir filtrar noticias por empresa, fecha y sentimiento.

### RF-027 — Asociar noticia con empresa

El sistema deberá identificar las empresas relacionadas con una noticia cuando sea posible.

### RF-028 — Clasificar sentimiento

El sistema deberá clasificar el sentimiento de una noticia como positivo, neutral o negativo.

### RF-029 — Mostrar confianza del sentimiento

El sistema deberá mostrar la confianza o probabilidad estimada por el modelo de sentimiento.

### RF-030 — Resumir noticia

El sistema podrá generar un resumen breve del contenido disponible de la noticia.

## 5.5 Watchlist y portafolios

### RF-031 — Crear watchlist

El sistema deberá permitir crear una lista de seguimiento.

### RF-032 — Agregar activo a watchlist

El sistema deberá permitir agregar un activo a una lista de seguimiento.

### RF-033 — Eliminar activo de watchlist

El sistema deberá permitir eliminar un activo de una lista de seguimiento.

### RF-034 — Crear portafolio

El sistema deberá permitir crear uno o varios portafolios virtuales.

### RF-035 — Agregar activo a portafolio

El sistema deberá permitir registrar un activo, cantidad, precio y fecha de compra simulada.

### RF-036 — Actualizar activo de portafolio

El sistema deberá permitir modificar los datos permitidos de una posición virtual.

### RF-037 — Eliminar activo de portafolio

El sistema deberá permitir eliminar una posición virtual.

### RF-038 — Calcular valor de portafolio

El sistema deberá calcular el valor estimado del portafolio utilizando los datos financieros disponibles.

### RF-039 — Mostrar distribución

El sistema deberá mostrar la distribución del portafolio por activo y sector.

### RF-040 — Calcular rendimiento del portafolio

El sistema deberá calcular el rendimiento histórico del portafolio virtual.

## 5.6 Simulación

### RF-041 — Crear simulación

El sistema deberá permitir crear una simulación indicando capital, periodo, perfil de riesgo y activos.

### RF-042 — Distribuir capital

El sistema deberá distribuir el capital virtual de acuerdo con los porcentajes establecidos.

### RF-043 — Ejecutar simulación histórica

El sistema deberá calcular el resultado hipotético de una inversión utilizando precios históricos.

### RF-044 — Calcular rendimiento simulado

El sistema deberá calcular la ganancia, pérdida y porcentaje de rendimiento del escenario.

### RF-045 — Calcular métricas de riesgo

El sistema deberá calcular métricas como volatilidad y rendimiento ajustado al riesgo cuando existan datos suficientes.

### RF-046 — Mostrar gráfica de simulación

El sistema deberá mostrar la evolución histórica del capital simulado.

### RF-047 — Guardar simulación

El sistema deberá permitir guardar los datos y resultados de una simulación.

### RF-048 — Consultar historial de simulaciones

El sistema deberá permitir consultar simulaciones realizadas anteriormente.

### RF-049 — Comparar simulaciones

El sistema deberá permitir comparar los resultados de diferentes simulaciones.

## 5.7 Inteligencia artificial y recomendaciones

### RF-050 — Clasificar riesgo del activo

El sistema deberá clasificar el riesgo de un activo en niveles definidos.

### RF-051 — Estimar tendencia

El sistema deberá estimar una tendencia alcista, neutral o bajista para un horizonte definido.

### RF-052 — Mostrar confianza de tendencia

El sistema deberá mostrar el nivel de confianza calculado por el modelo.

### RF-053 — Generar recomendación

El sistema deberá generar una recomendación informativa compatible con el perfil del usuario.

### RF-054 — Explicar recomendación

El sistema deberá mostrar los factores que tuvieron mayor influencia en la recomendación.

### RF-055 — Registrar versión del modelo

El sistema deberá registrar la versión del modelo utilizada en cada análisis.

### RF-056 — Guardar análisis

El sistema deberá almacenar el resultado del análisis para permitir su consulta posterior.

### RF-057 — Mostrar advertencia

El sistema deberá presentar una advertencia que indique que los resultados no constituyen asesoría financiera.

## 5.8 Administración

### RF-058 — Consultar usuarios

El administrador deberá poder consultar las cuentas registradas.

### RF-059 — Cambiar estado de usuario

El administrador deberá poder activar o desactivar una cuenta.

### RF-060 — Consultar auditoría

El administrador deberá poder consultar registros de eventos relevantes.

### RF-061 — Consultar errores

El administrador deberá poder consultar errores de integración y procesamiento.

### RF-062 — Consultar estadísticas

El administrador deberá poder consultar estadísticas generales de uso.

### RF-063 — Consultar estado de servicios

El administrador deberá poder consultar la disponibilidad de los servicios internos.

### RF-064 — Consultar modelos

El administrador deberá poder consultar las versiones y métricas principales de los modelos desplegados.

---

# 6. Requerimientos no funcionales

## RNF-001 — Disponibilidad web

El sistema deberá estar disponible mediante un navegador web moderno.

## RNF-002 — Diseño responsivo

La interfaz deberá adaptarse a computadoras, tabletas y teléfonos inteligentes.

## RNF-003 — Tiempo de respuesta

Las operaciones comunes deberán responder en menos de tres segundos en condiciones normales, sin considerar retrasos ajenos ocasionados por proveedores externos.

## RNF-004 — Seguridad de contraseñas

Las contraseñas deberán almacenarse mediante un algoritmo de hash seguro y no podrán recuperarse en texto original.

## RNF-005 — Comunicación segura

La comunicación de producción deberá realizarse mediante HTTPS.

## RNF-006 — Autorización

Los recursos protegidos deberán validar la identidad y los permisos del usuario.

## RNF-007 — Protección de secretos

Las claves de acceso, contraseñas y secretos deberán administrarse mediante variables de entorno o servicios especializados.

## RNF-008 — Arquitectura distribuida

Las funciones principales deberán estar distribuidas entre diferentes servicios desplegables.

## RNF-009 — Interoperabilidad

Los servicios deberán intercambiar información mediante REST, JSON y otros protocolos documentados.

## RNF-010 — Documentación de APIs

Las APIs deberán contar con documentación OpenAPI.

## RNF-011 — Escalabilidad

Los servicios deberán poder escalarse de manera independiente.

## RNF-012 — Concurrencia

El sistema deberá permitir la ejecución concurrente de consultas externas y procesos de análisis.

## RNF-013 — Tolerancia a errores externos

El sistema deberá manejar errores, tiempos de espera y límites de las APIs externas.

## RNF-014 — Caché

El sistema deberá implementar almacenamiento temporal para disminuir consultas repetitivas a proveedores externos.

## RNF-015 — Auditoría

El sistema deberá registrar accesos, modificaciones importantes, análisis y errores.

## RNF-016 — Mantenibilidad

El código deberá organizarse por responsabilidades y seguir convenciones definidas.

## RNF-017 — Control de versiones

El código y la documentación deberán almacenarse en un repositorio Git.

## RNF-018 — Pruebas

Los componentes críticos deberán contar con pruebas automatizadas.

## RNF-019 — Calidad del software

La evaluación del sistema considerará características de calidad compatibles con ISO/IEC 25010.

## RNF-020 — Accesibilidad

La interfaz deberá aplicar principios básicos de accesibilidad, contraste, navegación y legibilidad.

## RNF-021 — Observabilidad

Los servicios deberán proporcionar registros y mecanismos de verificación de estado.

## RNF-022 — Persistencia

La información estructurada deberá almacenarse en una base de datos relacional.

## RNF-023 — Información documental

Las noticias, resultados extensos y registros flexibles podrán almacenarse en una base de datos documental.

## RNF-024 — Reproducibilidad

El entorno de ejecución deberá poder reproducirse mediante contenedores.

## RNF-025 — Despliegue

La versión final deberá desplegarse en infraestructura de nube y no depender de un servidor local.

## RNF-026 — Explicabilidad

Las recomendaciones generadas mediante aprendizaje automático deberán acompañarse de factores explicativos.

## RNF-027 — Trazabilidad de modelos

Cada resultado deberá poder relacionarse con la versión del modelo y la fecha de ejecución.

## RNF-028 — Calidad de datos

Los procesos deberán validar ausencia, formato y consistencia de los datos utilizados.

## RNF-029 — Rendimiento de modelos

Los modelos deberán evaluarse mediante métricas apropiadas antes de su integración.

## RNF-030 — Muestra de evaluación

La evaluación académica utilizará una muestra superior a 35 elementos.

---

# 7. Reglas de negocio

### RN-001

Cada correo electrónico podrá estar asociado con una sola cuenta activa.

### RN-002

Cada usuario tendrá un único perfil de riesgo vigente.

### RN-003

El usuario podrá volver a realizar el cuestionario de riesgo.

### RN-004

Las clasificaciones anteriores deberán conservarse para trazabilidad.

### RN-005

Una cuenta desactivada no podrá acceder a funciones protegidas.

### RN-006

Una watchlist pertenecerá a un único usuario.

### RN-007

Un usuario podrá crear varias watchlists.

### RN-008

Un usuario podrá crear varios portafolios virtuales.

### RN-009

Un portafolio deberá contener al menos un activo para calcular estadísticas.

### RN-010

Un activo podrá formar parte de diferentes portafolios.

### RN-011

Una simulación deberá pertenecer a un usuario registrado.

### RN-012

La suma de los porcentajes asignados en una simulación deberá ser igual al 100 %.

### RN-013

El capital de una simulación deberá ser mayor que cero.

### RN-014

La fecha inicial de una simulación deberá ser anterior a la fecha final.

### RN-015

Las métricas se calcularán únicamente cuando existan datos suficientes.

### RN-016

Las noticias deberán registrar su fuente y fecha de publicación.

### RN-017

Una noticia duplicada no deberá almacenarse nuevamente cuando pueda identificarse mediante su URL o identificador externo.

### RN-018

Cada análisis deberá registrar la fecha y versión del modelo utilizado.

### RN-019

Las recomendaciones deberán corresponder con el perfil de riesgo vigente del usuario.

### RN-020

Una recomendación no podrá expresarse como garantía de rendimiento.

### RN-021

El sistema deberá mostrar una advertencia financiera junto con los resultados relevantes.

### RN-022

Los datos financieros obtenidos de terceros deberán indicar su fecha de actualización.

### RN-023

Los resultados obtenidos de una API externa podrán almacenarse temporalmente para respetar límites de consumo.

### RN-024

Las funciones administrativas requerirán un rol de administrador.

### RN-025

Las acciones administrativas relevantes deberán registrarse para auditoría.

---

# 8. Casos de uso identificados

- CU-001 Registrar usuario.
- CU-002 Iniciar sesión.
- CU-003 Cerrar sesión.
- CU-004 Recuperar acceso.
- CU-005 Consultar perfil.
- CU-006 Actualizar perfil.
- CU-007 Completar cuestionario de riesgo.
- CU-008 Consultar clasificación de riesgo.
- CU-009 Buscar activo.
- CU-010 Consultar detalle de empresa.
- CU-011 Consultar datos históricos.
- CU-012 Consultar indicadores financieros.
- CU-013 Comparar activos.
- CU-014 Consultar noticias.
- CU-015 Filtrar noticias.
- CU-016 Consultar sentimiento.
- CU-017 Crear watchlist.
- CU-018 Administrar activos de watchlist.
- CU-019 Crear portafolio.
- CU-020 Administrar posiciones virtuales.
- CU-021 Consultar rendimiento del portafolio.
- CU-022 Crear simulación.
- CU-023 Ejecutar simulación histórica.
- CU-024 Guardar simulación.
- CU-025 Comparar simulaciones.
- CU-026 Solicitar análisis de activo.
- CU-027 Consultar clasificación de riesgo.
- CU-028 Consultar tendencia estimada.
- CU-029 Obtener recomendación.
- CU-030 Consultar explicación.
- CU-031 Consultar historial de análisis.
- CU-032 Consultar usuarios.
- CU-033 Administrar estado de usuario.
- CU-034 Consultar registros de auditoría.
- CU-035 Consultar errores.
- CU-036 Consultar estadísticas administrativas.
- CU-037 Consultar estado de servicios.
- CU-038 Consultar versiones de modelos.

---

# 9. Criterios de aceptación generales

El prototipo se considerará funcional cuando:

- Permita registrar e iniciar sesión a un usuario.
- Permita completar el cuestionario de riesgo.
- Permita consultar datos financieros de activos seleccionados.
- Permita obtener y clasificar noticias financieras.
- Permita crear al menos un portafolio virtual.
- Permita ejecutar una simulación histórica.
- Permita generar una clasificación de riesgo.
- Permita generar una estimación de tendencia.
- Muestre una explicación de los resultados.
- Almacene el historial de simulaciones y análisis.
- Ejecute sus componentes principales mediante servicios distribuidos.
- Se encuentre desplegado en servicios de nube.
- Presente métricas de evaluación de los modelos.
- Muestre estadísticas obtenidas de una muestra superior a 35 registros.
- Incluya advertencias sobre las limitaciones de los resultados.

---

# 10. Matriz preliminar de trazabilidad

| Objetivo | Requerimientos relacionados                    |
| -------- | ---------------------------------------------- |
| OE-001   | RF-001 a RF-010                                |
| OE-002   | RF-011 a RF-015                                |
| OE-003   | RF-016 a RF-024                                |
| OE-004   | RF-025 a RF-030                                |
| OE-005   | RF-028, RF-029                                 |
| OE-006   | RF-021, RF-022, RF-038 a RF-045                |
| OE-007   | RF-050 a RF-052                                |
| OE-008   | RF-053 a RF-057                                |
| OE-009   | RF-031 a RF-040                                |
| OE-010   | RF-041 a RF-049                                |
| OE-011   | RF-019, RF-020, RF-039, RF-040, RF-046, RF-049 |
| OE-012   | RNF-008 a RNF-014 y RNF-025                    |

---

# 11. Aprobación del documento

El presente documento deberá revisarse antes de comenzar el diseño físico de las bases de datos y la implementación de los servicios.

Los cambios posteriores deberán registrarse mediante control de versiones.

| Responsable              | Actividad   | Estado                |
| ------------------------ | ----------- | --------------------- |
| Responsable del proyecto | Elaboración | Pendiente de revisión |
| Asesor académico         | Revisión    | Pendiente             |
| Comité o evaluador       | Validación  | Pendiente             |
