/**
 * Fichas de los modelos de IA activos en AlphaInvest AI.
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

export const TREND_MODEL_CARD: AiModelCard = {
  name: 'Predicción de tendencia',
  version: '0.1.0',
  whatItDoes:
    'Clasifica el movimiento de las próximas 5 sesiones en alcista, neutral o bajista (cambios menores a ±2 % cuentan como neutral) a partir de precio, volumen e indicadores técnicos (SMA, EMA, RSI, MACD, volatilidad).',
  trainingData: 'Histórico diario de AAPL (Yahoo Finance), 2000 a agosto de 2026.',
  horizon: '5 sesiones de mercado',
  testResult:
    'Acertó 31 % de los casos en el periodo de prueba; con tres opciones, el azar daría cerca de 33 %.',
  limitations: [
    'Se entrenó solo con AAPL; en otros activos su comportamiento no fue evaluado.',
    'Sus métricas no justifican usarlo para decisiones de inversión reales.',
  ],
}

export const PRICE_FORECAST_MODEL_CARD: AiModelCard = {
  name: 'Pronóstico de precio',
  version: '0.1.0',
  whatItDoes:
    'Aplica al último precio el rendimiento mediano histórico de AAPL a 5 sesiones (+0.75 %). Los modelos Ridge, Huber y XGBoost evaluados no superaron a esta regla simple.',
  trainingData: 'Histórico diario de AAPL (Yahoo Finance), 2000 a agosto de 2026.',
  horizon: '5 sesiones de mercado',
  testResult:
    'Acertó la dirección del precio en 55 % de los casos de prueba; su R² fue −0.009, es decir, no explica los movimientos mejor que un valor constante.',
  limitations: [
    'Da el mismo porcentaje para cualquier activo y cualquier fecha.',
    'Es una referencia estadística educativa, no un pronóstico.',
  ],
}

export const SENTIMENT_MODEL_CARD: AiModelCard = {
  name: 'Análisis de sentimiento',
  version: '0.1.0',
  whatItDoes:
    'Clasifica el tono de un texto financiero en inglés como positivo, neutral o negativo (FinBERT ajustado).',
  trainingData:
    'Financial PhraseBank: 4,840 frases financieras en inglés etiquetadas por personas.',
  horizon: null,
  testResult: 'Clasificó correctamente 85 % de las frases de prueba (F1 macro 0.83).',
  limitations: [
    'Mide el tono del texto, no el efecto real de la noticia en el precio.',
    'Fue entrenado con frases cortas en inglés; textos largos o en otro idioma pueden clasificarse peor.',
  ],
}

/** Único horizonte con modelo entrenado en la versión actual. */
export const SUPPORTED_ANALYSIS_HORIZON = 'CORTO_PLAZO'

export const ANALYSIS_HORIZON_OPTIONS: ReadonlyArray<{
  value: 'INTRADIA' | 'CORTO_PLAZO' | 'MEDIANO_PLAZO' | 'LARGO_PLAZO'
  label: string
  supported: boolean
}> = [
  { value: 'CORTO_PLAZO', label: 'Corto plazo (5 sesiones)', supported: true },
  { value: 'INTRADIA', label: 'Intradía (sin modelo entrenado)', supported: false },
  { value: 'MEDIANO_PLAZO', label: 'Mediano plazo (sin modelo entrenado)', supported: false },
  { value: 'LARGO_PLAZO', label: 'Largo plazo (sin modelo entrenado)', supported: false },
]
