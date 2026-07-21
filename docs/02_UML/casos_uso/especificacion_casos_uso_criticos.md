# Especificación detallada de casos de uso críticos

## AlphaInvest AI

---

## Control del documento

| Campo                 | Información                              |
| --------------------- | ---------------------------------------- |
| Proyecto              | AlphaInvest AI                           |
| Documento             | Especificación detallada de casos de uso |
| Versión               | 0.1                                      |
| Estado                | Borrador inicial                         |
| Fecha                 | Julio de 2026                            |
| Documento relacionado | SRS de AlphaInvest AI                    |
| Diagrama relacionado  | Diagrama general de casos de uso         |

---

# 1. Introducción

## 1.1 Propósito

El presente documento describe detalladamente los casos de uso críticos de AlphaInvest AI.

Los casos seleccionados representan las funciones que tienen mayor impacto en:

- La arquitectura del sistema.
- El modelo de datos.
- Los servicios del backend.
- La seguridad.
- Los modelos de inteligencia artificial.
- Las simulaciones.
- Las recomendaciones.
- La administración.

Cada caso de uso contiene actores, objetivo, precondiciones, disparador, flujo principal, flujos alternativos, excepciones, postcondiciones, reglas de negocio, datos involucrados y requerimientos relacionados.

## 1.2 Casos de uso incluidos

Los casos de uso críticos documentados son:

| Identificador | Caso de uso                      |
| ------------- | -------------------------------- |
| CU-001        | Registrar usuario                |
| CU-002        | Iniciar sesión                   |
| CU-007        | Completar cuestionario de riesgo |
| CU-009        | Buscar activo                    |
| CU-019        | Crear portafolio                 |
| CU-023        | Ejecutar simulación histórica    |
| CU-026        | Analizar activo                  |
| CU-029        | Obtener recomendación            |
| CU-033        | Administrar estado de usuario    |

---

# 2. CU-001 — Registrar usuario

## 2.1 Información general

| Campo               | Descripción                                          |
| ------------------- | ---------------------------------------------------- |
| Identificador       | CU-001                                               |
| Nombre              | Registrar usuario                                    |
| Actor principal     | Usuario inversionista                                |
| Actores secundarios | Servicio de correo                                   |
| Objetivo            | Crear una cuenta de usuario dentro de AlphaInvest AI |
| Prioridad           | Alta                                                 |
| Frecuencia          | Media                                                |
| Módulo              | Autenticación y usuarios                             |

## 2.2 Precondiciones

- El usuario no deberá tener una cuenta registrada con el mismo correo electrónico.
- El sistema de autenticación deberá estar disponible.
- La aplicación deberá tener conexión con la base de datos.
- El usuario deberá encontrarse en la pantalla de registro.

## 2.3 Disparador

El usuario selecciona la opción **Crear cuenta**.

## 2.4 Flujo principal

1. El sistema muestra el formulario de registro.
2. El usuario introduce su nombre.
3. El usuario introduce su correo electrónico.
4. El usuario introduce una contraseña.
5. El usuario confirma la contraseña.
6. El usuario acepta los términos de uso y la advertencia financiera.
7. El usuario selecciona la opción de registro.
8. El sistema valida que todos los campos obligatorios estén completos.
9. El sistema valida el formato del correo electrónico.
10. El sistema valida que las contraseñas coincidan.
11. El sistema valida que la contraseña cumpla con los requisitos de seguridad.
12. El sistema verifica que el correo no se encuentre registrado.
13. El sistema genera el hash seguro de la contraseña.
14. El sistema registra la cuenta con estado activo.
15. El sistema asigna el rol de usuario inversionista.
16. El sistema registra el evento de creación para auditoría.
17. El sistema muestra un mensaje de registro exitoso.
18. El sistema redirige al usuario hacia la pantalla de inicio de sesión.

## 2.5 Flujos alternativos

### FA-001 — Campos incompletos

1. El sistema detecta uno o más campos obligatorios vacíos.
2. El sistema identifica los campos que deben completarse.
3. El sistema no registra la cuenta.
4. El usuario corrige la información.

### FA-002 — Correo inválido

1. El sistema determina que el correo no tiene un formato válido.
2. El sistema muestra un mensaje de validación.
3. El usuario corrige el correo electrónico.

### FA-003 — Contraseñas diferentes

1. El sistema detecta que la contraseña y su confirmación no coinciden.
2. El sistema muestra un mensaje de error.
3. El usuario introduce nuevamente las contraseñas.

### FA-004 — Contraseña insegura

1. El sistema determina que la contraseña no cumple los requisitos mínimos.
2. El sistema muestra las reglas pendientes.
3. El usuario introduce una nueva contraseña.

### FA-005 — Correo previamente registrado

1. El sistema encuentra una cuenta asociada con el correo electrónico.
2. El sistema rechaza el registro.
3. El sistema informa que el correo ya está en uso.
4. El sistema puede mostrar la opción de recuperación de acceso.

## 2.6 Excepciones

### EX-001 — Error de base de datos

1. El sistema no puede guardar la cuenta.
2. El sistema revierte cualquier operación parcial.
3. El sistema registra el error.
4. El sistema muestra un mensaje general sin revelar información técnica.

### EX-002 — Servicio no disponible

1. El servicio de autenticación no responde.
2. El sistema informa que el registro no está disponible temporalmente.
3. No se crea ninguna cuenta incompleta.

## 2.7 Postcondiciones

### Éxito

- Existe una nueva cuenta registrada.
- La contraseña está almacenada mediante hash.
- El usuario tiene asignado un rol.
- Se registró un evento de auditoría.

### Fallo

- No se crea ninguna cuenta.
- No se almacenan contraseñas en texto plano.
- El sistema conserva la consistencia de los datos.

## 2.8 Reglas de negocio

- RN-001: Cada correo podrá asociarse con una sola cuenta activa.
- RN-005: Una cuenta desactivada no podrá acceder a funciones protegidas.
- El usuario deberá aceptar los términos de uso.
- La contraseña nunca deberá almacenarse en texto original.
- El rol inicial será usuario inversionista.

## 2.9 Datos involucrados

- Identificador del usuario.
- Nombre.
- Correo electrónico.
- Hash de contraseña.
- Rol.
- Estado de la cuenta.
- Fecha de registro.
- Fecha de actualización.
- Aceptación de términos.

## 2.10 Requerimientos relacionados

- RF-001 Registrar usuario.
- RF-002 Validar correo único.
- RF-003 Validar contraseña.
- RNF-004 Seguridad de contraseñas.
- RNF-006 Autorización.
- RNF-015 Auditoría.

## 2.11 Criterios de aceptación

- No se permitirá registrar dos usuarios con el mismo correo.
- La contraseña no podrá consultarse posteriormente en texto plano.
- El usuario deberá recibir una respuesta clara cuando los datos sean inválidos.
- Un registro exitoso deberá poder utilizarse posteriormente para iniciar sesión.

---

# 3. CU-002 — Iniciar sesión

## 3.1 Información general

| Campo               | Descripción                                          |
| ------------------- | ---------------------------------------------------- |
| Identificador       | CU-002                                               |
| Nombre              | Iniciar sesión                                       |
| Actor principal     | Usuario o administrador                              |
| Actores secundarios | Proveedor de identidad                               |
| Objetivo            | Permitir el acceso seguro a las funciones protegidas |
| Prioridad           | Alta                                                 |
| Frecuencia          | Alta                                                 |
| Módulo              | Autenticación y usuarios                             |

## 3.2 Precondiciones

- El usuario deberá tener una cuenta registrada.
- La cuenta deberá encontrarse activa.
- El servicio de autenticación deberá estar disponible.

## 3.3 Disparador

El usuario selecciona la opción **Iniciar sesión**.

## 3.4 Flujo principal

1. El sistema muestra el formulario de acceso.
2. El usuario introduce su correo electrónico.
3. El usuario introduce su contraseña.
4. El usuario selecciona la opción de iniciar sesión.
5. El sistema valida que los campos estén completos.
6. El sistema busca la cuenta mediante el correo electrónico.
7. El sistema valida el estado de la cuenta.
8. El sistema compara la contraseña con el hash almacenado.
9. El sistema obtiene el rol del usuario.
10. El sistema genera el token de acceso.
11. El sistema genera el mecanismo de renovación de sesión.
12. El sistema registra el acceso exitoso.
13. El sistema devuelve la información básica de sesión.
14. El sistema redirige al usuario al dashboard correspondiente.

## 3.5 Flujos alternativos

### FA-001 — Credenciales incorrectas

1. El sistema no encuentra la cuenta o la contraseña no coincide.
2. El sistema rechaza el acceso.
3. El sistema muestra un mensaje genérico de credenciales inválidas.
4. El sistema registra el intento fallido.

### FA-002 — Cuenta desactivada

1. El sistema identifica que la cuenta está desactivada.
2. El sistema rechaza el acceso.
3. El sistema informa que la cuenta no se encuentra disponible.

### FA-003 — Campos incompletos

1. El sistema identifica campos vacíos.
2. El sistema solicita completarlos.
3. No se envía la solicitud de autenticación.

### FA-004 — Sesión ya activa

1. El sistema detecta una sesión válida.
2. El sistema permite continuar hacia el dashboard.
3. El sistema puede renovar el token cuando corresponda.

## 3.6 Excepciones

### EX-001 — Error del servicio de autenticación

1. El sistema no puede validar las credenciales.
2. El sistema registra el error.
3. El sistema informa que el acceso no está disponible temporalmente.

### EX-002 — Error de generación del token

1. Las credenciales son válidas, pero el token no puede generarse.
2. El sistema no inicia la sesión.
3. El sistema registra el incidente técnico.

## 3.7 Postcondiciones

### Éxito

- Existe una sesión autenticada.
- El usuario recibe un token válido.
- El sistema conoce el rol y permisos del usuario.
- Se registra el inicio de sesión.

### Fallo

- No se genera una sesión válida.
- No se revela si un correo específico existe en el sistema.
- Se registra el intento fallido cuando corresponda.

## 3.8 Reglas de negocio

- Las cuentas desactivadas no podrán iniciar sesión.
- El usuario solo podrá acceder a funciones autorizadas por su rol.
- Los mensajes de error no deberán revelar información sensible.
- El token deberá tener un periodo de expiración.

## 3.9 Datos involucrados

- Correo electrónico.
- Hash de contraseña.
- Estado de cuenta.
- Rol.
- Token de acceso.
- Token de renovación.
- Fecha y hora de acceso.
- Dirección o información técnica de la sesión.

## 3.10 Requerimientos relacionados

- RF-004 Iniciar sesión.
- RF-007 Renovar sesión.
- RNF-005 Comunicación segura.
- RNF-006 Autorización.
- RNF-007 Protección de secretos.
- RNF-015 Auditoría.

## 3.11 Criterios de aceptación

- Las credenciales correctas deberán producir una sesión válida.
- Una cuenta desactivada no deberá acceder.
- El token deberá expirar.
- El administrador deberá recibir permisos diferentes al usuario común.

---

# 4. CU-007 — Completar cuestionario de riesgo

## 4.1 Información general

| Campo            | Descripción                                   |
| ---------------- | --------------------------------------------- |
| Identificador    | CU-007                                        |
| Nombre           | Completar cuestionario de riesgo              |
| Actor principal  | Usuario inversionista                         |
| Actor secundario | Servicio de inteligencia artificial           |
| Objetivo         | Determinar el perfil de riesgo del usuario    |
| Prioridad        | Alta                                          |
| Frecuencia       | Baja o media                                  |
| Módulo           | Perfil de inversión e inteligencia artificial |

## 4.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- El cuestionario deberá encontrarse activo.
- Las preguntas y respuestas posibles deberán estar configuradas.
- El modelo o sistema de clasificación deberá estar disponible.

## 4.3 Disparador

El usuario selecciona la opción **Determinar mi perfil de riesgo**.

## 4.4 Flujo principal

1. El sistema consulta el cuestionario vigente.
2. El sistema muestra las instrucciones.
3. El sistema presenta las preguntas del cuestionario.
4. El usuario responde cada pregunta.
5. El sistema valida que todas las preguntas obligatorias tengan respuesta.
6. El usuario envía el cuestionario.
7. El sistema registra las respuestas.
8. El sistema transforma las respuestas en variables de entrada.
9. El sistema ejecuta el algoritmo de clasificación.
10. El sistema calcula el nivel de confianza.
11. El sistema clasifica al usuario como conservador, moderado o agresivo.
12. El sistema identifica los factores principales de la clasificación.
13. El sistema desactiva el perfil de riesgo anterior, en caso de existir.
14. El sistema registra el nuevo perfil como vigente.
15. El sistema registra la versión del modelo utilizado.
16. El sistema muestra el resultado y su explicación.
17. El sistema muestra una advertencia informativa.

## 4.5 Flujos alternativos

### FA-001 — Respuestas incompletas

1. El sistema detecta preguntas obligatorias sin responder.
2. El sistema destaca dichas preguntas.
3. El usuario completa las respuestas faltantes.

### FA-002 — Usuario vuelve a realizar el cuestionario

1. El sistema informa que existe un perfil vigente.
2. El usuario confirma que desea generar una nueva evaluación.
3. El sistema ejecuta nuevamente el flujo principal.
4. El perfil anterior se conserva en el historial.

### FA-003 — Clasificación basada en reglas

1. El modelo principal no está disponible.
2. El sistema utiliza un mecanismo de clasificación basado en puntuación.
3. El sistema registra el método utilizado.
4. El resultado se presenta con su correspondiente explicación.

## 4.6 Excepciones

### EX-001 — Modelo no disponible

1. El servicio de IA no responde.
2. El sistema conserva temporalmente las respuestas.
3. El sistema registra el error.
4. El sistema informa que la clasificación no pudo completarse.

### EX-002 — Error al guardar respuestas

1. El sistema no puede persistir las respuestas.
2. No se registra un perfil incompleto.
3. El sistema informa el error.
4. El usuario puede intentar nuevamente.

## 4.7 Postcondiciones

### Éxito

- Existe un perfil de riesgo vigente.
- Las respuestas están asociadas con el usuario.
- Se conserva el historial anterior.
- Se registra la versión del algoritmo.

### Fallo

- El perfil vigente anterior no se modifica.
- Las respuestas no generan una clasificación parcial.

## 4.8 Reglas de negocio

- RN-002: Cada usuario tendrá un único perfil de riesgo vigente.
- RN-003: El usuario podrá repetir el cuestionario.
- RN-004: Las clasificaciones anteriores deberán conservarse.
- El cuestionario deberá completarse antes de generar el perfil.
- Toda clasificación deberá registrar el modelo o método utilizado.

## 4.9 Datos involucrados

- Usuario.
- Cuestionario.
- Preguntas.
- Respuestas.
- Puntuación.
- Clasificación.
- Nivel de confianza.
- Factores explicativos.
- Fecha de evaluación.
- Versión del modelo.
- Estado vigente o histórico.

## 4.10 Requerimientos relacionados

- RF-011 Contestar cuestionario.
- RF-012 Clasificar perfil de riesgo.
- RF-013 Explicar perfil.
- RF-014 Actualizar perfil.
- RF-015 Consultar historial.
- RNF-026 Explicabilidad.
- RNF-027 Trazabilidad de modelos.

## 4.11 Criterios de aceptación

- El sistema deberá producir uno de los perfiles definidos.
- El resultado deberá incluir una explicación.
- El perfil anterior deberá mantenerse en el historial.
- Solo un perfil podrá marcarse como vigente.

---

# 5. CU-009 — Buscar activo

## 5.1 Información general

| Campo            | Descripción                                        |
| ---------------- | -------------------------------------------------- |
| Identificador    | CU-009                                             |
| Nombre           | Buscar activo                                      |
| Actor principal  | Usuario inversionista                              |
| Actor secundario | API financiera                                     |
| Objetivo         | Localizar acciones o ETF disponibles para análisis |
| Prioridad        | Alta                                               |
| Frecuencia       | Alta                                               |
| Módulo           | Mercado financiero                                 |

## 5.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- El servicio de mercado deberá estar disponible.
- Deberá existir conexión con la fuente financiera o datos almacenados en caché.

## 5.3 Disparador

El usuario introduce un símbolo bursátil o nombre dentro del buscador.

## 5.4 Flujo principal

1. El usuario accede al módulo de mercado.
2. El sistema muestra el campo de búsqueda.
3. El usuario introduce un símbolo o nombre.
4. El sistema valida la longitud y formato de la búsqueda.
5. El sistema consulta primero los activos almacenados localmente.
6. Cuando sea necesario, el sistema consulta la API financiera.
7. El sistema normaliza los resultados.
8. El sistema elimina duplicados.
9. El sistema ordena los resultados por relevancia.
10. El sistema muestra símbolo, nombre, tipo de activo y mercado.
11. El usuario selecciona un resultado.
12. El sistema abre la pantalla de detalle del activo.

## 5.5 Flujos alternativos

### FA-001 — Resultado disponible en caché

1. El sistema encuentra una respuesta vigente en caché.
2. El sistema utiliza la información almacenada.
3. No realiza una llamada adicional al proveedor.

### FA-002 — Múltiples coincidencias

1. El sistema encuentra varios activos con nombres similares.
2. El sistema muestra las coincidencias.
3. El usuario selecciona el activo correcto.

### FA-003 — Sin resultados

1. El sistema no encuentra coincidencias.
2. El sistema informa que no existen resultados.
3. El sistema sugiere verificar el símbolo o utilizar otro término.

### FA-004 — Datos locales desactualizados

1. El sistema encuentra el activo, pero detecta que la información está vencida.
2. El sistema solicita una actualización al proveedor.
3. El sistema almacena la nueva fecha de actualización.

## 5.6 Excepciones

### EX-001 — API financiera no disponible

1. El proveedor no responde.
2. El sistema utiliza datos almacenados cuando estén disponibles.
3. El sistema informa que la información podría no estar actualizada.
4. El sistema registra el error externo.

### EX-002 — Límite de consultas agotado

1. El proveedor rechaza la solicitud por límite de uso.
2. El sistema utiliza la caché disponible.
3. El sistema evita realizar nuevos intentos inmediatos.
4. El sistema registra el evento.

## 5.7 Postcondiciones

### Éxito

- El usuario recibe una lista de activos coincidentes.
- Puede acceder al detalle del activo.
- Los datos consultados pueden almacenarse temporalmente.

### Fallo

- No se modifican portafolios ni datos personales.
- Se informa claramente la falta de resultados o disponibilidad.

## 5.8 Reglas de negocio

- Los datos externos deberán registrar fecha de actualización.
- El sistema deberá respetar los límites del proveedor.
- Los resultados podrán almacenarse en caché.
- Solo deberán mostrarse activos soportados por la primera versión.

## 5.9 Datos involucrados

- Símbolo bursátil.
- Nombre del activo.
- Tipo de activo.
- Mercado.
- Moneda.
- País.
- Identificador externo.
- Fuente.
- Fecha de actualización.

## 5.10 Requerimientos relacionados

- RF-016 Buscar activo.
- RF-017 Consultar empresa.
- RF-024 Actualizar datos financieros.
- RNF-013 Tolerancia a errores.
- RNF-014 Caché.
- RNF-028 Calidad de datos.

## 5.11 Criterios de aceptación

- La búsqueda deberá aceptar nombre o símbolo.
- Los resultados deberán identificar claramente el tipo de activo.
- La caída del proveedor no deberá provocar un error no controlado.
- Los datos deberán mostrar su fecha de actualización.

---

# 6. CU-019 — Crear portafolio

## 6.1 Información general

| Campo           | Descripción                            |
| --------------- | -------------------------------------- |
| Identificador   | CU-019                                 |
| Nombre          | Crear portafolio                       |
| Actor principal | Usuario inversionista                  |
| Objetivo        | Crear un contenedor virtual de activos |
| Prioridad       | Alta                                   |
| Frecuencia      | Media                                  |
| Módulo          | Portafolios                            |

## 6.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- La cuenta deberá estar activa.
- El servicio de portafolios deberá estar disponible.

## 6.3 Disparador

El usuario selecciona la opción **Nuevo portafolio**.

## 6.4 Flujo principal

1. El sistema muestra el formulario de creación.
2. El usuario introduce el nombre del portafolio.
3. El usuario puede introducir una descripción.
4. El usuario selecciona la moneda base.
5. El usuario selecciona la opción de guardar.
6. El sistema valida los campos.
7. El sistema verifica que el usuario no tenga otro portafolio con el mismo nombre.
8. El sistema crea el portafolio.
9. El sistema asigna el portafolio al usuario autenticado.
10. El sistema registra la fecha de creación.
11. El sistema registra el evento para auditoría.
12. El sistema muestra el portafolio vacío.
13. El sistema ofrece la opción de agregar activos.

## 6.5 Flujos alternativos

### FA-001 — Nombre duplicado

1. El sistema detecta un portafolio con el mismo nombre para el usuario.
2. El sistema solicita utilizar un nombre diferente.
3. No se crea un portafolio duplicado.

### FA-002 — Descripción omitida

1. El usuario deja vacía la descripción.
2. El sistema permite continuar.
3. El portafolio se crea sin descripción.

### FA-003 — Cancelar operación

1. El usuario selecciona cancelar.
2. El sistema descarta la información temporal.
3. El usuario regresa al listado de portafolios.

## 6.6 Excepciones

### EX-001 — Error de persistencia

1. El sistema no puede guardar el portafolio.
2. El sistema revierte la operación.
3. El sistema registra el error.
4. El usuario recibe un mensaje general.

## 6.7 Postcondiciones

### Éxito

- Existe un nuevo portafolio.
- El portafolio pertenece al usuario.
- Inicialmente no contiene posiciones.
- Puede recibir activos posteriormente.

### Fallo

- No se crea información incompleta.
- No se afectan otros portafolios.

## 6.8 Reglas de negocio

- RN-008: Un usuario podrá crear varios portafolios.
- RN-009: Un portafolio deberá contener activos para calcular estadísticas.
- El nombre deberá ser único dentro de los portafolios activos del mismo usuario.
- Un usuario no podrá consultar portafolios ajenos.

## 6.9 Datos involucrados

- Identificador del portafolio.
- Usuario propietario.
- Nombre.
- Descripción.
- Moneda base.
- Estado.
- Fecha de creación.
- Fecha de actualización.

## 6.10 Requerimientos relacionados

- RF-034 Crear portafolio.
- RF-035 Agregar activo.
- RF-038 Calcular valor.
- RNF-006 Autorización.
- RNF-015 Auditoría.

## 6.11 Criterios de aceptación

- El portafolio deberá quedar asociado con el usuario autenticado.
- Otro usuario no deberá poder consultarlo.
- El portafolio podrá crearse sin activos.
- No deberá calcular rendimiento mientras esté vacío.

---

# 7. CU-023 — Ejecutar simulación histórica

## 7.1 Información general

| Campo               | Descripción                                              |
| ------------------- | -------------------------------------------------------- |
| Identificador       | CU-023                                                   |
| Nombre              | Ejecutar simulación histórica                            |
| Actor principal     | Usuario inversionista                                    |
| Actores secundarios | API financiera y servicio de simulación                  |
| Objetivo            | Calcular el resultado hipotético de una inversión pasada |
| Prioridad           | Alta                                                     |
| Frecuencia          | Media o alta                                             |
| Módulo              | Simulación                                               |

## 7.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- La simulación deberá tener capital mayor que cero.
- Deberán existir uno o más activos seleccionados.
- Los porcentajes deberán sumar 100 %.
- La fecha inicial deberá ser anterior a la fecha final.
- Deberán existir datos históricos suficientes.

## 7.3 Disparador

El usuario selecciona **Ejecutar simulación**.

## 7.4 Flujo principal

1. El usuario introduce el capital inicial.
2. El usuario selecciona la moneda.
3. El usuario define la fecha inicial.
4. El usuario define la fecha final.
5. El usuario agrega uno o más activos.
6. El usuario asigna un porcentaje a cada activo.
7. El sistema valida que el capital sea mayor que cero.
8. El sistema valida las fechas.
9. El sistema valida que la distribución sea igual a 100 %.
10. El sistema consulta los precios históricos.
11. El sistema valida la calidad y suficiencia de los datos.
12. El sistema determina el precio inicial disponible de cada activo.
13. El sistema distribuye el capital.
14. El sistema calcula la cantidad virtual adquirida.
15. El sistema calcula la evolución del valor del portafolio.
16. El sistema calcula el valor final.
17. El sistema calcula la ganancia o pérdida.
18. El sistema calcula el rendimiento porcentual.
19. El sistema calcula la volatilidad.
20. El sistema calcula las métricas adicionales disponibles.
21. El sistema genera la serie histórica para la gráfica.
22. El sistema muestra los resultados.
23. El sistema muestra las limitaciones del cálculo.
24. El usuario puede decidir guardar la simulación.

## 7.5 Flujos alternativos

### FA-001 — Distribución diferente de 100 %

1. El sistema detecta que los porcentajes no suman 100 %.
2. El sistema rechaza la ejecución.
3. El sistema muestra la diferencia pendiente.
4. El usuario corrige la distribución.

### FA-002 — Día inicial sin cotización

1. La fecha inicial corresponde a un día no operativo.
2. El sistema utiliza el siguiente precio disponible.
3. El sistema informa la fecha efectiva utilizada.

### FA-003 — Día final sin cotización

1. La fecha final corresponde a un día no operativo.
2. El sistema utiliza el último precio disponible anterior.
3. El sistema informa la fecha efectiva utilizada.

### FA-004 — Datos parciales

1. Uno de los activos no tiene información suficiente.
2. El sistema informa cuál activo presenta el problema.
3. El usuario puede retirarlo o modificar el periodo.

### FA-005 — Simulación no guardada

1. El usuario consulta los resultados.
2. El usuario abandona la pantalla sin guardar.
3. El resultado temporal no se agrega al historial.

## 7.6 Excepciones

### EX-001 — Error de proveedor financiero

1. El sistema no obtiene los precios requeridos.
2. El sistema intenta utilizar datos almacenados.
3. Si no existen datos suficientes, cancela la simulación.
4. El sistema registra el error.

### EX-002 — Error de cálculo

1. El servicio encuentra datos inválidos o una operación no válida.
2. El sistema cancela el resultado.
3. No se presenta una simulación parcial como válida.
4. El error se registra para análisis.

## 7.7 Postcondiciones

### Éxito

- Existe un resultado temporal de simulación.
- Se muestran métricas y gráfica.
- El usuario puede guardarlo.
- Se conserva la trazabilidad de los datos utilizados.

### Fallo

- No se muestra un resultado engañoso o incompleto.
- No se guarda una simulación inválida.

## 7.8 Reglas de negocio

- RN-012: Los porcentajes deberán sumar 100 %.
- RN-013: El capital deberá ser mayor que cero.
- RN-014: La fecha inicial deberá ser anterior a la fecha final.
- RN-015: Las métricas se calcularán cuando existan datos suficientes.
- La simulación no representa una operación real.
- Los resultados deberán indicar las fechas efectivas utilizadas.

## 7.9 Datos involucrados

- Usuario.
- Capital inicial.
- Moneda.
- Fechas solicitadas.
- Fechas efectivas.
- Activos.
- Porcentajes.
- Precios históricos.
- Cantidades virtuales.
- Valor inicial.
- Valor final.
- Ganancia o pérdida.
- Rendimiento.
- Volatilidad.
- Serie histórica.
- Fuente de datos.

## 7.10 Requerimientos relacionados

- RF-041 Crear simulación.
- RF-042 Distribuir capital.
- RF-043 Ejecutar simulación.
- RF-044 Calcular rendimiento.
- RF-045 Calcular riesgo.
- RF-046 Mostrar gráfica.
- RF-047 Guardar simulación.
- RNF-028 Calidad de datos.

## 7.11 Criterios de aceptación

- El sistema deberá rechazar distribuciones diferentes de 100 %.
- El resultado deberá mostrar capital inicial y final.
- La simulación deberá manejar días sin operación bursátil.
- Los cálculos deberán ser reproducibles con los mismos datos.

---

# 8. CU-026 — Analizar activo

## 8.1 Información general

| Campo               | Descripción                                             |
| ------------------- | ------------------------------------------------------- |
| Identificador       | CU-026                                                  |
| Nombre              | Analizar activo                                         |
| Actor principal     | Usuario inversionista                                   |
| Actores secundarios | Servicio de mercado, noticias e inteligencia artificial |
| Objetivo            | Obtener métricas y resultados de IA para un activo      |
| Prioridad           | Alta                                                    |
| Frecuencia          | Alta                                                    |
| Módulo              | Inteligencia artificial                                 |

## 8.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- El activo deberá ser válido y estar soportado.
- Deberán existir datos financieros suficientes.
- El servicio de IA deberá tener un modelo activo.

## 8.3 Disparador

El usuario selecciona **Analizar activo** desde el detalle de una empresa.

## 8.4 Flujo principal

1. El sistema identifica el activo seleccionado.
2. El sistema obtiene los datos históricos necesarios.
3. El sistema obtiene los indicadores financieros disponibles.
4. El sistema obtiene las noticias recientes relacionadas.
5. El sistema consulta o calcula el sentimiento de las noticias.
6. El sistema valida la calidad de las variables.
7. El sistema transforma los datos al formato requerido.
8. El sistema selecciona la versión activa de los modelos.
9. El sistema ejecuta el modelo de clasificación de riesgo.
10. El sistema ejecuta el modelo de estimación de tendencia.
11. El sistema calcula niveles de confianza.
12. El sistema identifica las variables más influyentes.
13. El sistema genera una explicación.
14. El sistema registra los datos de entrada resumidos.
15. El sistema registra la versión de cada modelo.
16. El sistema guarda el resultado del análisis.
17. El sistema muestra riesgo, tendencia, confianza y explicación.
18. El sistema muestra una advertencia financiera.

## 8.5 Flujos alternativos

### FA-001 — Análisis reciente disponible

1. El sistema encuentra un análisis reciente y vigente.
2. El sistema muestra el resultado almacenado.
3. El usuario puede solicitar una actualización cuando esté permitida.

### FA-002 — Noticias no disponibles

1. El sistema no encuentra noticias recientes.
2. El sistema ejecuta el análisis con variables financieras.
3. El sistema informa que el componente de noticias no fue considerado.

### FA-003 — Indicador faltante

1. El sistema detecta una variable ausente.
2. El proceso aplica la estrategia de datos faltantes autorizada.
3. El resultado registra qué variable no estuvo disponible.

### FA-004 — Modelo alternativo

1. El modelo principal no se encuentra disponible.
2. El sistema utiliza una versión de respaldo.
3. El resultado registra la versión realmente utilizada.

## 8.6 Excepciones

### EX-001 — Datos insuficientes

1. El sistema determina que no existe información suficiente.
2. El análisis se cancela.
3. El sistema informa la razón al usuario.

### EX-002 — Error del modelo

1. El modelo devuelve un error.
2. El sistema no guarda un resultado incompleto.
3. El incidente queda registrado.
4. Se informa que el análisis no pudo completarse.

## 8.7 Postcondiciones

### Éxito

- Existe un análisis asociado con el usuario y el activo.
- Se registran resultados y versiones de modelos.
- El usuario recibe una explicación y advertencia.

### Fallo

- No se presenta una predicción incompleta.
- El error queda disponible para monitoreo.

## 8.8 Reglas de negocio

- Cada análisis deberá registrar la versión de los modelos.
- Los resultados deberán incluir fecha de generación.
- El sistema deberá indicar el nivel de confianza.
- El análisis no deberá expresarse como certeza.
- Los datos faltantes deberán quedar registrados.

## 8.9 Datos involucrados

- Usuario.
- Activo.
- Periodo de análisis.
- Datos históricos.
- Indicadores.
- Noticias.
- Sentimiento.
- Clasificación de riesgo.
- Tendencia.
- Confianza.
- Explicación.
- Versión de modelos.
- Fecha de análisis.

## 8.10 Requerimientos relacionados

- RF-050 Clasificar riesgo.
- RF-051 Estimar tendencia.
- RF-052 Mostrar confianza.
- RF-054 Explicar recomendación.
- RF-055 Registrar versión.
- RF-056 Guardar análisis.
- RNF-026 Explicabilidad.
- RNF-027 Trazabilidad.

## 8.11 Criterios de aceptación

- El resultado deberá registrar la versión del modelo.
- No deberá generarse un análisis con datos insuficientes.
- El usuario deberá conocer la fecha del análisis.
- La salida deberá incluir una explicación comprensible.

---

# 9. CU-029 — Obtener recomendación

## 9.1 Información general

| Campo               | Descripción                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| Identificador       | CU-029                                                                   |
| Nombre              | Obtener recomendación                                                    |
| Actor principal     | Usuario inversionista                                                    |
| Actores secundarios | Servicio de IA, mercado y noticias                                       |
| Objetivo            | Generar una orientación informativa compatible con el perfil del usuario |
| Prioridad           | Alta                                                                     |
| Frecuencia          | Media o alta                                                             |
| Módulo              | Inteligencia artificial y recomendaciones                                |

## 9.2 Precondiciones

- El usuario deberá haber iniciado sesión.
- El usuario deberá tener un perfil de riesgo vigente.
- El activo deberá contar con un análisis válido.
- Los modelos y reglas de recomendación deberán estar disponibles.

## 9.3 Disparador

El usuario selecciona **Obtener recomendación**.

## 9.4 Flujo principal

1. El sistema identifica al usuario.
2. El sistema obtiene su perfil de riesgo vigente.
3. El sistema obtiene el activo seleccionado.
4. El sistema obtiene el análisis financiero más reciente.
5. El sistema obtiene la clasificación de riesgo del activo.
6. El sistema obtiene la tendencia estimada.
7. El sistema obtiene el sentimiento agregado de noticias.
8. El sistema valida la vigencia de los datos.
9. El sistema aplica las reglas de compatibilidad.
10. El sistema ejecuta el modelo o motor de recomendación.
11. El sistema genera una categoría informativa.
12. El sistema calcula el nivel de confianza.
13. El sistema identifica los factores principales.
14. El sistema genera una explicación personalizada.
15. El sistema registra las versiones de modelos y reglas.
16. El sistema guarda la recomendación.
17. El sistema muestra la categoría, confianza y explicación.
18. El sistema muestra la advertencia financiera.

## 9.5 Categorías propuestas

Las categorías iniciales podrán ser:

- Compatible para análisis.
- Compatible con precaución.
- Riesgo superior al perfil.
- Información insuficiente.
- Requiere mayor diversificación.

Estas categorías deberán evitar expresiones absolutas como:

- Compra garantizada.
- Ganancia segura.
- Venta inmediata.
- Rendimiento asegurado.

## 9.6 Flujos alternativos

### FA-001 — Usuario sin perfil de riesgo

1. El sistema detecta que no existe un perfil vigente.
2. El sistema detiene la recomendación.
3. El sistema invita al usuario a realizar el cuestionario.

### FA-002 — Análisis desactualizado

1. El sistema determina que el análisis ha vencido.
2. El sistema ejecuta o solicita una actualización.
3. La recomendación utiliza el análisis actualizado.

### FA-003 — Riesgo superior al perfil

1. El activo tiene una clasificación superior a la tolerancia del usuario.
2. El sistema genera una recomendación de precaución.
3. El sistema explica la diferencia de riesgo.

### FA-004 — Información insuficiente

1. Faltan datos necesarios.
2. El sistema no genera una recomendación categórica.
3. El sistema muestra la categoría de información insuficiente.

## 9.7 Excepciones

### EX-001 — Error del motor de recomendación

1. El servicio no puede generar el resultado.
2. El sistema no guarda una recomendación incompleta.
3. El error se registra.
4. Se informa al usuario.

### EX-002 — Inconsistencia de versiones

1. Los resultados utilizados corresponden a versiones incompatibles.
2. El sistema cancela la recomendación.
3. El sistema solicita un nuevo análisis.

## 9.8 Postcondiciones

### Éxito

- Existe una recomendación registrada.
- Está asociada con el usuario, activo y análisis.
- Incluye confianza, explicación y advertencia.
- Registra las versiones utilizadas.

### Fallo

- No se guarda una recomendación parcial.
- No se muestra una afirmación financiera engañosa.

## 9.9 Reglas de negocio

- RN-019: La recomendación deberá corresponder con el perfil vigente.
- RN-020: No deberá expresarse como garantía.
- RN-021: Deberá mostrar una advertencia.
- Cada recomendación deberá vincularse con un análisis.
- La recomendación deberá tener fecha de generación y vigencia.
- La explicación deberá identificar factores relevantes.

## 9.10 Datos involucrados

- Usuario.
- Perfil de riesgo.
- Activo.
- Análisis.
- Riesgo del activo.
- Tendencia.
- Sentimiento.
- Categoría.
- Confianza.
- Explicación.
- Advertencia.
- Versiones.
- Fecha de generación.
- Fecha de vigencia.

## 9.11 Requerimientos relacionados

- RF-053 Generar recomendación.
- RF-054 Explicar recomendación.
- RF-055 Registrar modelo.
- RF-056 Guardar análisis.
- RF-057 Mostrar advertencia.
- RNF-026 Explicabilidad.
- RNF-027 Trazabilidad.

## 9.12 Criterios de aceptación

- No deberá generarse una recomendación personalizada sin perfil de riesgo.
- El resultado deberá incluir explicación y advertencia.
- Deberá poder identificarse el análisis utilizado.
- Una recomendación vencida deberá indicarse como desactualizada.

---

# 10. CU-033 — Administrar estado de usuario

## 10.1 Información general

| Campo           | Descripción                             |
| --------------- | --------------------------------------- |
| Identificador   | CU-033                                  |
| Nombre          | Administrar estado de usuario           |
| Actor principal | Administrador                           |
| Objetivo        | Activar o desactivar cuentas de usuario |
| Prioridad       | Media                                   |
| Frecuencia      | Baja                                    |
| Módulo          | Administración                          |

## 10.2 Precondiciones

- El administrador deberá haber iniciado sesión.
- El administrador deberá tener permisos suficientes.
- La cuenta objetivo deberá existir.

## 10.3 Disparador

El administrador selecciona un usuario y la opción de cambiar estado.

## 10.4 Flujo principal

1. El administrador accede al módulo de usuarios.
2. El sistema valida el rol del administrador.
3. El sistema muestra las cuentas registradas.
4. El administrador busca una cuenta.
5. El sistema muestra la información autorizada.
6. El administrador selecciona cambiar estado.
7. El sistema muestra el estado actual.
8. El administrador selecciona activar o desactivar.
9. El administrador introduce un motivo.
10. El sistema solicita confirmación.
11. El administrador confirma.
12. El sistema valida que la operación esté permitida.
13. El sistema actualiza el estado.
14. Cuando se desactiva una cuenta, el sistema invalida sus sesiones.
15. El sistema registra el administrador responsable.
16. El sistema registra el estado anterior, nuevo estado y motivo.
17. El sistema informa que la operación fue exitosa.

## 10.5 Flujos alternativos

### FA-001 — Cancelar operación

1. El administrador no confirma el cambio.
2. El sistema conserva el estado anterior.
3. No se genera un registro de modificación.

### FA-002 — Activar cuenta desactivada

1. El administrador selecciona una cuenta desactivada.
2. El sistema solicita el motivo de reactivación.
3. El sistema cambia el estado a activo.
4. El usuario podrá autenticarse nuevamente.

### FA-003 — Cuenta ya tiene el estado solicitado

1. El sistema detecta que no existe cambio real.
2. El sistema informa que la cuenta ya tiene ese estado.
3. No realiza una actualización innecesaria.

## 10.6 Excepciones

### EX-001 — Administrador sin permisos

1. El sistema detecta que el actor no cuenta con permisos.
2. El sistema rechaza la operación.
3. El intento queda registrado.

### EX-002 — Intento de desactivar la propia cuenta

1. El administrador intenta desactivar su propia cuenta.
2. El sistema rechaza la operación para evitar pérdida de administración.
3. El evento queda registrado.

### EX-003 — Error de actualización

1. El sistema no puede guardar el cambio.
2. Mantiene el estado anterior.
3. Registra el error.
4. Informa que la operación no pudo completarse.

## 10.7 Postcondiciones

### Éxito

- La cuenta tiene el nuevo estado.
- El cambio queda registrado.
- Las sesiones se invalidan cuando corresponde.

### Fallo

- La cuenta mantiene el estado anterior.
- No se pierde la trazabilidad del intento.

## 10.8 Reglas de negocio

- RN-024: Las funciones administrativas requerirán el rol correspondiente.
- RN-025: Las acciones relevantes deberán auditarse.
- Una cuenta desactivada no podrá iniciar sesión.
- El cambio deberá incluir un motivo.
- El sistema deberá conservar el estado anterior.
- Un administrador no podrá desactivarse a sí mismo.

## 10.9 Datos involucrados

- Usuario objetivo.
- Administrador responsable.
- Estado anterior.
- Estado nuevo.
- Motivo.
- Fecha y hora.
- Sesiones invalidadas.
- Registro de auditoría.

## 10.10 Requerimientos relacionados

- RF-058 Consultar usuarios.
- RF-059 Cambiar estado.
- RF-060 Consultar auditoría.
- RNF-006 Autorización.
- RNF-015 Auditoría.

## 10.11 Criterios de aceptación

- Un usuario común no deberá ejecutar esta función.
- Una cuenta desactivada no deberá iniciar sesión.
- El cambio deberá aparecer en la auditoría.
- La operación deberá registrar al administrador responsable.

---

# 11. Matriz de trazabilidad de casos críticos

| Caso de uso | Requerimientos funcionales       | Entidades preliminares                                       |
| ----------- | -------------------------------- | ------------------------------------------------------------ |
| CU-001      | RF-001 a RF-003                  | Usuario, Rol, Aceptación de términos                         |
| CU-002      | RF-004, RF-005, RF-007           | Usuario, Sesión, Token, Auditoría                            |
| CU-007      | RF-011 a RF-015                  | Cuestionario, Pregunta, Respuesta, Perfil de riesgo, Modelo  |
| CU-009      | RF-016 a RF-024                  | Activo, Empresa, Mercado, Fuente de datos, Caché             |
| CU-019      | RF-034 a RF-040                  | Portafolio, Posición, Usuario, Activo                        |
| CU-023      | RF-041 a RF-049                  | Simulación, Detalle de simulación, Precio histórico, Métrica |
| CU-026      | RF-050 a RF-052, RF-055 y RF-056 | Análisis, Predicción, Modelo, Activo, Noticia                |
| CU-029      | RF-053 a RF-057                  | Recomendación, Explicación, Perfil, Análisis                 |
| CU-033      | RF-058 a RF-060                  | Usuario, Estado de usuario, Auditoría                        |

---

# 12. Entidades preliminares identificadas

A partir de los casos de uso se identifican inicialmente las siguientes entidades:

- Usuario.
- Rol.
- Sesión.
- Auditoría.
- Cuestionario.
- Pregunta.
- Opción de respuesta.
- Respuesta del usuario.
- Perfil de riesgo.
- Activo.
- Empresa.
- Mercado.
- Precio histórico.
- Indicador financiero.
- Fuente financiera.
- Noticia.
- Sentimiento.
- Watchlist.
- Detalle de watchlist.
- Portafolio.
- Posición de portafolio.
- Simulación.
- Detalle de simulación.
- Resultado de simulación.
- Modelo de inteligencia artificial.
- Versión de modelo.
- Análisis de activo.
- Predicción.
- Recomendación.
- Explicación.

Esta lista es preliminar y deberá validarse durante el desarrollo del modelo conceptual y del diagrama de clases.

---

# 13. Servicios preliminares identificados

Los casos de uso permiten identificar los siguientes servicios:

| Servicio           | Responsabilidades principales                              |
| ------------------ | ---------------------------------------------------------- |
| Auth Service       | Usuarios, sesiones, tokens, roles y acceso                 |
| Profile Service    | Cuestionario y perfil de riesgo                            |
| Market Service     | Activos, precios, indicadores y proveedores                |
| News Service       | Noticias, fuentes y sentimiento                            |
| Portfolio Service  | Watchlists, portafolios y posiciones                       |
| Simulation Service | Escenarios, métricas y resultados históricos               |
| AI Service         | Clasificación, tendencias, explicaciones y recomendaciones |
| Admin Service      | Usuarios, auditoría, errores y monitoreo                   |
| API Gateway        | Enrutamiento, seguridad y punto de entrada                 |

El servicio de perfil podrá integrarse inicialmente dentro del servicio de autenticación o inteligencia artificial para reducir la complejidad del prototipo.

---

# 14. Validación del documento

Antes de aprobar esta especificación se deberá verificar:

- Que cada caso corresponda con el SRS.
- Que los actores tengan permisos coherentes.
- Que las precondiciones sean verificables.
- Que los flujos alternativos no contradigan el flujo principal.
- Que las excepciones eviten estados incompletos.
- Que todas las recomendaciones incluyan advertencia.
- Que los resultados de IA registren su versión.
- Que los datos externos registren su fecha y fuente.
- Que las funciones administrativas generen auditoría.
- Que ninguna función ejecute operaciones financieras reales.

---

# 15. Resultado

La presente especificación permite iniciar:

- El diagrama de clases.
- El modelo entidad–relación.
- Los diagramas de secuencia.
- La definición de endpoints.
- El diseño de bases de datos.
- La elaboración de casos de prueba.
