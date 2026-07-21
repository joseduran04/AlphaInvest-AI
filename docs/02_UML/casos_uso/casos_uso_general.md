# Diagrama general de casos de uso

## AlphaInvest AI

## 1. Objetivo

El diagrama general de casos de uso representa las principales interacciones entre los actores y los módulos funcionales de AlphaInvest AI.

Su finalidad es transformar los requerimientos funcionales definidos en el SRS en una representación visual del comportamiento esperado del sistema.

## 2. Alcance del diagrama

El diagrama incluye los siguientes módulos:

1. Autenticación y usuarios.
2. Perfil de inversión.
3. Mercado financiero.
4. Noticias financieras.
5. Watchlist.
6. Portafolios virtuales.
7. Simulación de inversiones.
8. Inteligencia artificial.
9. Administración.

También representa la interacción con proveedores externos de datos financieros, noticias, correo electrónico e identidad.

## 3. Actores

### 3.1 Usuario inversionista

Representa a una persona registrada que utiliza la plataforma para consultar activos, administrar portafolios virtuales, realizar simulaciones y obtener análisis informativos.

### 3.2 Administrador

Representa a la persona responsable de consultar usuarios, monitorear los servicios, revisar auditorías y consultar información sobre los modelos desplegados.

### 3.3 API financiera

Representa a los proveedores externos que entregan precios, información histórica, indicadores financieros y datos empresariales.

### 3.4 API de noticias

Representa a los proveedores externos que proporcionan noticias financieras y económicas.

### 3.5 Servicio de correo

Representa al proveedor utilizado para enviar mensajes de recuperación, verificación o notificación.

### 3.6 Proveedor de identidad

Representa un servicio interno o externo responsable de validar credenciales, tokens o mecanismos de autenticación.

## 4. Relaciones principales

El usuario inversionista interactúa directamente con las funciones de autenticación, mercado, noticias, perfil de riesgo, watchlists, portafolios, simulaciones e inteligencia artificial.

El administrador utiliza las funciones de autenticación y el módulo administrativo.

Las consultas del mercado dependen de una API financiera externa.

Las consultas de noticias dependen de una API de noticias externa.

La recuperación de acceso utiliza un servicio de correo.

Los análisis de inteligencia artificial registran la versión del modelo utilizado para mantener trazabilidad.

## 5. Relaciones include

Las relaciones `include` representan acciones obligatorias reutilizadas por otros casos de uso.

| Caso principal             | Caso incluido                  | Justificación                                      |
| -------------------------- | ------------------------------ | -------------------------------------------------- |
| Iniciar sesión             | Validar credenciales           | Toda autenticación requiere verificar la identidad |
| Recuperar acceso           | Enviar correo                  | La recuperación requiere enviar instrucciones      |
| Completar cuestionario     | Calcular perfil                | Las respuestas deben procesarse                    |
| Consultar perfil de riesgo | Explicar clasificación         | El resultado debe ser comprensible                 |
| Buscar activo              | Consultar proveedor de mercado | La información proviene de una fuente financiera   |
| Comparar activos           | Calcular métricas              | La comparación necesita indicadores comunes        |
| Consultar noticias         | Obtener noticias externas      | Se requieren fuentes externas                      |
| Consultar sentimiento      | Analizar sentimiento           | La clasificación requiere un modelo NLP            |
| Crear simulación           | Validar distribución           | Los porcentajes deben sumar 100 %                  |
| Ejecutar simulación        | Calcular métricas              | El sistema debe obtener resultados y riesgo        |
| Obtener recomendación      | Ejecutar modelos               | La recomendación utiliza resultados de IA          |
| Obtener recomendación      | Generar explicación            | La recomendación debe ser explicable               |
| Obtener recomendación      | Mostrar advertencia            | Los resultados no son asesoría financiera          |
| Generar análisis           | Registrar versión              | Cada resultado debe mantener trazabilidad          |

## 6. Relaciones extend

La relación `extend` representa una función condicional u opcional.

| Caso base                     | Caso de extensión  | Condición                                |
| ----------------------------- | ------------------ | ---------------------------------------- |
| Ejecutar simulación histórica | Guardar simulación | El usuario decide conservar el resultado |

## 7. Correspondencia con el SRS

Los casos de uso CU-001 a CU-038 corresponden con los requerimientos funcionales RF-001 a RF-064.

Un caso de uso puede atender varios requerimientos funcionales. Por ejemplo, administrar posiciones virtuales incluye agregar, modificar y eliminar activos dentro de un portafolio.

## 8. Decisiones de diseño

El diagrama utiliza paquetes para evitar representar todos los casos de uso como una lista desorganizada.

Las operaciones internas reutilizables se muestran como casos incluidos, aunque no siempre correspondan a una pantalla independiente.

Los servicios externos se representan como actores porque interactúan con AlphaInvest AI, pero no forman parte de su control interno.

El sistema se limita a proporcionar análisis informativos y simulaciones. No se incluyen compras, ventas ni conexión con casas de bolsa.

## 9. Resultado esperado

Este diagrama servirá como entrada para:

- La especificación detallada de casos de uso.
- El diagrama de clases.
- Los diagramas de secuencia.
- El diseño de los servicios.
- El modelo entidad–relación.
- La definición de endpoints.
- Los casos de prueba.
