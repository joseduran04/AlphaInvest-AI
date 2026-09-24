/**
 * Ficha del modelo de IA visible en AlphaInvest AI.
 *
 * Los modelos de tendencia y pronóstico de precio (v0.1.0) se retiraron de la
 * interfaz: en pruebas no superaron al azar (31 % vs 33 %) ni a un valor
 * constante (R² −0.009). Siguen en el backend y en backend/artifacts.
 *
 * Fuente: backend/artifacts/ai/<modelo>/0.1.0/metadata.json.
 * IMPORTANTE: actualizar estas fichas cuando se registre una versión nueva.
 */

export interface AiModelCard {
  name: string
  version: string
  whatItDoes: string
  trainingData: string
  horizon: string | null
  testResult: string
  limitations: string[]
}

export const SENTIMENT_MODEL_CARD: AiModelCard = {
  name: 'Análisis de sentimiento',
  version: '0.1.0',
  whatItDoes:
    'Clasifica el tono de una noticia financiera en inglés como positivo, neutral o negativo para la empresa (FinBERT ajustado).',
  trainingData:
    'Financial PhraseBank: 4,840 frases financieras en inglés etiquetadas por personas.',
  horizon: null,
  testResult: 'Clasificó correctamente 85 % de las frases de prueba (F1 macro 0.83).',
  limitations: [
    'Mide el tono del texto, no el efecto real de la noticia en el precio.',
    'Fue entrenado con frases cortas en inglés; textos largos o en otro idioma pueden clasificarse peor.',
  ],
}
