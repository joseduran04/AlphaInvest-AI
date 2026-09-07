/*
===============================================================================
AlphaInvest AI
Cuestionario inicial de perfil de riesgo
===============================================================================

Objetivo:
- Crear el cuestionario inicial.
- Crear preguntas de opción única.
- Crear opciones con puntuación.
- Publicar el cuestionario.

Clasificaciones previstas:
- CONSERVADOR
- MODERADO_CONSERVADOR
- MODERADO
- MODERADO_AGRESIVO
- AGRESIVO
===============================================================================
*/

BEGIN;

DO $$
DECLARE
    v_cuestionario_id UUID;

    v_pregunta_1 UUID;
    v_pregunta_2 UUID;
    v_pregunta_3 UUID;
    v_pregunta_4 UUID;
    v_pregunta_5 UUID;
    v_pregunta_6 UUID;
    v_pregunta_7 UUID;
    v_pregunta_8 UUID;
    v_pregunta_9 UUID;
    v_pregunta_10 UUID;
BEGIN
    /*
    ---------------------------------------------------------------------------
    1. Crear o recuperar cuestionario
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.cuestionarios (
        nombre,
        descripcion,
        version,
        estado,
        fecha_publicacion
    )
    VALUES (
        'Cuestionario inicial de perfil de riesgo',
        'Cuestionario para evaluar conocimientos, horizonte de inversión, capacidad financiera y tolerancia al riesgo del inversionista.',
        '1.0',
        'PUBLICADO',
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (nombre, version)
    DO UPDATE SET
        descripcion = EXCLUDED.descripcion,
        estado = 'PUBLICADO',
        fecha_publicacion = COALESCE(
            profile.cuestionarios.fecha_publicacion,
            CURRENT_TIMESTAMP
        ),
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_cuestionario_id;

    /*
    ---------------------------------------------------------------------------
    2. Pregunta 1
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Cuál es tu principal objetivo de inversión?',
        'OPCION_UNICA',
        1,
        1.0000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_1;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_1, 'Proteger el capital y evitar pérdidas', 1.0000, 1, TRUE),
        (v_pregunta_1, 'Obtener rendimientos ligeramente superiores a la inflación', 2.0000, 2, TRUE),
        (v_pregunta_1, 'Equilibrar crecimiento y estabilidad', 3.0000, 3, TRUE),
        (v_pregunta_1, 'Buscar crecimiento elevado aceptando variaciones', 4.0000, 4, TRUE),
        (v_pregunta_1, 'Maximizar el crecimiento aceptando pérdidas importantes', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    3. Pregunta 2
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Durante cuánto tiempo planeas mantener tu inversión?',
        'OPCION_UNICA',
        2,
        1.2000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_2;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_2, 'Menos de 1 año', 1.0000, 1, TRUE),
        (v_pregunta_2, 'Entre 1 y 3 años', 2.0000, 2, TRUE),
        (v_pregunta_2, 'Entre 3 y 5 años', 3.0000, 3, TRUE),
        (v_pregunta_2, 'Entre 5 y 10 años', 4.0000, 4, TRUE),
        (v_pregunta_2, 'Más de 10 años', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    4. Pregunta 3
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué porcentaje de tus ingresos mensuales podrías destinar a inversiones?',
        'OPCION_UNICA',
        3,
        1.0000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_3;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_3, 'Menos del 5 %', 1.0000, 1, TRUE),
        (v_pregunta_3, 'Entre el 5 % y el 10 %', 2.0000, 2, TRUE),
        (v_pregunta_3, 'Entre el 11 % y el 20 %', 3.0000, 3, TRUE),
        (v_pregunta_3, 'Entre el 21 % y el 30 %', 4.0000, 4, TRUE),
        (v_pregunta_3, 'Más del 30 %', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    5. Pregunta 4
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Cómo describirías tu fondo de emergencia?',
        'OPCION_UNICA',
        4,
        1.1000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_4;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_4, 'No cuento con fondo de emergencia', 1.0000, 1, TRUE),
        (v_pregunta_4, 'Cubre menos de 1 mes de gastos', 2.0000, 2, TRUE),
        (v_pregunta_4, 'Cubre entre 1 y 3 meses de gastos', 3.0000, 3, TRUE),
        (v_pregunta_4, 'Cubre entre 3 y 6 meses de gastos', 4.0000, 4, TRUE),
        (v_pregunta_4, 'Cubre más de 6 meses de gastos', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    6. Pregunta 5
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué experiencia tienes invirtiendo?',
        'OPCION_UNICA',
        5,
        1.1000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_5;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_5, 'No tengo experiencia', 1.0000, 1, TRUE),
        (v_pregunta_5, 'Solo conozco productos de ahorro', 2.0000, 2, TRUE),
        (v_pregunta_5, 'He invertido en fondos o instrumentos de deuda', 3.0000, 3, TRUE),
        (v_pregunta_5, 'He invertido en acciones o fondos de renta variable', 4.0000, 4, TRUE),
        (v_pregunta_5, 'Tengo experiencia amplia en distintos instrumentos', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    7. Pregunta 6
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué harías si tu inversión perdiera un 10 % de su valor en un mes?',
        'OPCION_UNICA',
        6,
        1.5000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_6;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_6, 'Vendería inmediatamente toda la inversión', 1.0000, 1, TRUE),
        (v_pregunta_6, 'Vendería una parte para reducir el riesgo', 2.0000, 2, TRUE),
        (v_pregunta_6, 'Mantendría la inversión y esperaría', 3.0000, 3, TRUE),
        (v_pregunta_6, 'Invertiría un poco más aprovechando la caída', 4.0000, 4, TRUE),
        (v_pregunta_6, 'Aumentaría considerablemente la inversión', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    8. Pregunta 7
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Cuál sería la pérdida temporal máxima que aceptarías en un año?',
        'OPCION_UNICA',
        7,
        1.5000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_7;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_7, 'No aceptaría ninguna pérdida', 1.0000, 1, TRUE),
        (v_pregunta_7, 'Hasta un 5 %', 2.0000, 2, TRUE),
        (v_pregunta_7, 'Hasta un 10 %', 3.0000, 3, TRUE),
        (v_pregunta_7, 'Hasta un 20 %', 4.0000, 4, TRUE),
        (v_pregunta_7, 'Más de un 20 %', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    9. Pregunta 8
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué tipo de rendimiento esperas obtener anualmente?',
        'OPCION_UNICA',
        8,
        1.2000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_8;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_8, 'Conservar el valor del dinero', 1.0000, 1, TRUE),
        (v_pregunta_8, 'Entre un 4 % y un 6 %', 2.0000, 2, TRUE),
        (v_pregunta_8, 'Entre un 7 % y un 10 %', 3.0000, 3, TRUE),
        (v_pregunta_8, 'Entre un 11 % y un 15 %', 4.0000, 4, TRUE),
        (v_pregunta_8, 'Más de un 15 %', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    10. Pregunta 9
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué tan estable es tu fuente principal de ingresos?',
        'OPCION_UNICA',
        9,
        1.1000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_9;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_9, 'Muy inestable o sin ingresos regulares', 1.0000, 1, TRUE),
        (v_pregunta_9, 'Variable y poco predecible', 2.0000, 2, TRUE),
        (v_pregunta_9, 'Moderadamente estable', 3.0000, 3, TRUE),
        (v_pregunta_9, 'Estable', 4.0000, 4, TRUE),
        (v_pregunta_9, 'Muy estable y con ingresos diversificados', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;

    /*
    ---------------------------------------------------------------------------
    11. Pregunta 10
    ---------------------------------------------------------------------------
    */

    INSERT INTO profile.preguntas (
        cuestionario_id,
        texto,
        tipo,
        orden,
        ponderacion,
        obligatoria,
        activa
    )
    VALUES (
        v_cuestionario_id,
        '¿Qué proporción de tu patrimonio total representaría esta inversión?',
        'OPCION_UNICA',
        10,
        1.2000,
        TRUE,
        TRUE
    )
    ON CONFLICT (cuestionario_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        tipo = EXCLUDED.tipo,
        ponderacion = EXCLUDED.ponderacion,
        obligatoria = TRUE,
        activa = TRUE,
        fecha_actualizacion = CURRENT_TIMESTAMP
    RETURNING id INTO v_pregunta_10;

    INSERT INTO profile.opciones_respuesta (
        pregunta_id,
        texto,
        valor,
        orden,
        activa
    )
    VALUES
        (v_pregunta_10, 'Más del 75 %', 1.0000, 1, TRUE),
        (v_pregunta_10, 'Entre el 51 % y el 75 %', 2.0000, 2, TRUE),
        (v_pregunta_10, 'Entre el 26 % y el 50 %', 3.0000, 3, TRUE),
        (v_pregunta_10, 'Entre el 10 % y el 25 %', 4.0000, 4, TRUE),
        (v_pregunta_10, 'Menos del 10 %', 5.0000, 5, TRUE)
    ON CONFLICT (pregunta_id, orden)
    DO UPDATE SET
        texto = EXCLUDED.texto,
        valor = EXCLUDED.valor,
        activa = TRUE;
END
$$;

COMMIT;