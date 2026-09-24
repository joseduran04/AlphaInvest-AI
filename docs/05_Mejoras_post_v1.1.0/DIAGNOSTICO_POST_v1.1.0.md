# Diagnóstico post-v1.1.0

Rama: `feature/post-v1.1.0-diagnostico` (derivada de `develop` = `v1.1.0` = `7b76c74`).
El tag `v1.1.0` no se modificó.

## Baseline verificada en esta sesión

| Área | Resultado | Nota |
|---|---|---|
| Frontend tests | 120/120 PASS | Vitest |
| TypeScript / Oxlint / Prettier | PASS | |
| Build producción / npm audit | PASS / 0 vulnerabilidades | |
| Backend tests | 765 PASS | Faltan ~78 por el entorno: 11 módulos requieren `torch` y 19 de integración requieren Supabase |
| Ruff | PASS | |
| Mypy | PASS salvo `torch` no instalado | |
| Docker / PostgreSQL / MongoDB / Playwright | No ejecutable en este entorno | Validar en Windows |

## Causas raíz compartidas

1. **Cobertura de Market Data por configuración.** El worker sincroniza precios **y noticias** solo para `APP_WORKER_PRICE_SYNC_SYMBOLS` (en el `.env` actual: `AAPL`). Los demás activos solo se actualizan con sincronización manual.
2. **Dos fuentes de precios sin coordinar:**
   - Simulación: fuente `Alpha Vantage` (`worker_simulation_source_name`).
   - Análisis IA: fuente `Yahoo Finance` (`asset_analysis_runtime_service.PRICE_SOURCE_NAME`). Solo la carga el script manual `scripts/market/bootstrap_yahoo_history.py` (AAPL).
   - Sincronización API/worker: solo `Alpha Vantage`.
   - Portafolios: último precio de **cualquier** fuente.
3. **Cuota de Alpha Vantage.** Precios y noticias consumen la misma API key: 2 llamadas por símbolo por día.

## Backlog clasificado

| ID | Hallazgo | Causa raíz | Clasificación | Estado |
|---|---|---|---|---|
| AI-SIM-001 | META cortada al 11/09 | El motor usa como fin efectivo la última fecha común con precios guardados (`HistoricalCalendarAligner`). META no se sincroniza automáticamente. Pendiente confirmar con el script de diagnóstico. | Limitación de Market Data + UX | UX corregida (aviso de periodo recortado). La causa de datos depende de la decisión WS1. |
| AI-SIM-002 | "Monto inicial" 559.02 vs capital asignado 10,000 | `monto_inicial` y `precio_inicial` son informativos: el motor no los usa y asigna capital × %. | UX/UI | Corregido: etiquetas "de referencia", ayuda y capital asignado calculado. |
| AI-SIM-003 | Anualizado 6181%, Sharpe 146 | Fórmulas correctas: CAGR con días naturales, volatilidad √252, Sharpe = (CAGR − rf)/vol. Sobre 10 días la extrapolación explota. | Comportamiento esperado + UX | Corregido: rendimiento del periodo como dato principal. En periodos < 1 año las métricas anualizadas pasan a un detalle plegable con explicación (criterio GIPS). |
| AI-PORT-001 | Ganancia total 339.75 con posición de P/L 2.73 | `create_position` no descuenta `saldo_efectivo`, pero el esquema define el saldo como "no asignado a posiciones". El resumen calcula `total = efectivo + posiciones` y `ganancia = total − capital_inicial`. | Bug confirmado (semántica efectivo/posición) | **Requiere decisión** (ver abajo). |
| AI-PORT-002 | Colores P/L | Sin estilo por signo. | UX/UI | Corregido en posiciones, resumen, valoraciones y dashboard. |
| AI-PORT-003 | Evolución del portafolio | Existe `valoraciones_portafolio` (snapshots). No hace falta nueva persistencia. | Mejora funcional | Pendiente, después de PORT-001. |
| AI-NEWS-001 | AMZN sin noticias | El worker de noticias usa la misma lista de símbolos (solo AAPL). | Limitación de configuración | Pendiente decisión WS1. |
| AI-NEWS-002 | Noticias poco relacionadas | Alpha Vantage `NEWS_SENTIMENT` con `tickers=` devuelve cualquier artículo que mencione el ticker, sin orden por relevancia y sin umbral. Se toman los primeros `limit`. | Mejora funcional | Pendiente: umbral o orden por `relevance_score` de ticker. Primero medir la distribución con el script. |
| AI-NEWS-003 | Métricas técnicas de noticias | Las etiquetas vienen del proveedor (Bearish … Bullish), escala documentada por Alpha Vantage. | UX/UI | Pendiente: traducir etiquetas 1:1 sin inventar umbrales. |
| AI-PROFILE-001 | ¿El perfil se usa? | Sí, en recomendaciones (`recommendation_engine`: nivel de riesgo y perfil conservador). No se usa en simulación ni en portafolios. | Mejora funcional | Pendiente: contextualizar volatilidad/drawdown/concentración. |
| AI-AI-001 | IA demasiado técnica | — | UX/UI | Pendiente. |
| AI-ML-001 | Ciclo de vida de modelos | Ver la sección siguiente. | Limitación documentada | Pendiente documentación. |

## Estado real de los modelos (artefactos en `backend/artifacts/ai`)

| Modelo | Algoritmo | Datos | Horizonte | Métrica test | Estado en metadata |
|---|---|---|---|---|---|
| Predicción de tendencia 0.1.0 | XGBoost 3 clases | Solo AAPL (Yahoo), 2000–2026 | 5 sesiones | accuracy 0.31, macro F1 0.26 | `PROTOTYPE_EVALUATED`: "no justifican uso financiero productivo" |
| Pronóstico de precio 0.1.0 | Mediana histórica del rendimiento a 5 sesiones | Solo AAPL | 5 sesiones (evaluados 1, 5, 10, 20) | R² −0.009, dirección 0.55 | `PROTOTYPE_EVALUATED` |
| Sentimiento 0.1.0 | FinBERT afinado | Financial PhraseBank | — | macro F1 validación 0.82 | — |

- **Horizontes corto/medio/largo:** no existen modelos para ellos. Solo hay horizonte de 5 sesiones. No se deben simular en la interfaz.
- **"Ejecutar análisis" es inferencia, no entrenamiento.** El entrenamiento se hace con los scripts de `backend/scripts/ai`.

## Decisiones pendientes

1. **PORT-001:** ¿agregar una posición equivale a comprar con el efectivo del portafolio?
2. **WS1:** qué activos sincroniza el worker, y si Yahoo Finance pasa a ser la fuente principal de precios.

## Registro de decisiones

- 2026-09-23: los cambios de interfaz no modifican contratos API ni la base de datos.
- 2026-09-23: el criterio de anualización se basa en GIPS: no anualizar periodos menores a un año.
