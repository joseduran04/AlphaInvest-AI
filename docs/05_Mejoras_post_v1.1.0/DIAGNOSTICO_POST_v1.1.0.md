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
| AI-SIM-001 | META cortada al 11/09 | **Confirmado:** META solo tenía precios de Alpha Vantage hasta el 11/09 (carga manual del 13/09). El motor usa como fin efectivo la última fecha común con precios. | Limitación de Market Data + UX | **Corregido:** aviso en la interfaz, sincronización automática de activos en uso con Yahoo como fuente principal, y la simulación elige por activo la fuente con datos más recientes. |
| AI-SIM-002 | "Monto inicial" 559.02 vs capital asignado 10,000 | `monto_inicial` y `precio_inicial` son informativos: el motor no los usa y asigna capital × %. | UX/UI | Corregido: etiquetas "de referencia", ayuda y capital asignado calculado. |
| AI-SIM-003 | Anualizado 6181%, Sharpe 146 | Fórmulas correctas: CAGR con días naturales, volatilidad √252, Sharpe = (CAGR − rf)/vol. Sobre 10 días la extrapolación explota. | Comportamiento esperado + UX | Corregido: rendimiento del periodo como dato principal. En periodos < 1 año las métricas anualizadas pasan a un detalle plegable con explicación (criterio GIPS). |
| AI-PORT-001 | Ganancia total 339.75 con posición de P/L 2.73 | `create_position` no descontaba `saldo_efectivo`, aunque el esquema define el saldo como "no asignado a posiciones". | Bug confirmado | **Corregido:** agregar, editar y eliminar posiciones mueve el efectivo (409 si no alcanza o si la moneda es distinta). Script `scripts/portfolio/reconcile_cash_balances.py` para datos existentes (1 portafolio afectado). |
| AI-PORT-002 | Colores P/L | Sin estilo por signo. | UX/UI | Corregido en posiciones, resumen, valoraciones y dashboard. |
| AI-PORT-003 | Evolución del portafolio | Existe `valoraciones_portafolio` (snapshots). No hace falta nueva persistencia. | Mejora funcional | Pendiente, después de PORT-001. |
| AI-NEWS-001 | AMZN sin noticias | El worker de noticias usaba la misma lista fija (solo AAPL) y corría cada 30 min, agotando la cuota de Alpha Vantage. | Limitación de configuración | **Corregido:** noticias para activos en uso, una vez al día (migración `5b7e2d9f4a10`). |
| AI-NEWS-002 | Noticias poco relacionadas | Medido: las 231 noticias de AAPL tienen relevancia ≥ 0.5 (promedio 0.79). Un umbral por puntaje casi no filtraría nada; el origen es el etiquetado de tickers de Alpha Vantage. | Limitación del proveedor | Pendiente: evaluar reglas deterministas (ticker/empresa en el título o resumen). |
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

## Evidencia del diagnóstico (2026-09-23)

- Yahoo y Alpha Vantage coinciden en apertura y cierre (diferencias de redondeo; Yahoo redondea el volumen a centenas).
- Alpha Vantage: `cierre_ajustado` vacío en todas las filas; solo 100 sesiones (`compact`).
- Yahoo: cierre ajustado, histórico completo, dividendos (META pagó 0.525 el 2026-09-21).
- Noticias: trabajo cada 30 min solo para AAPL. Hubo ejecuciones FALLIDA por límite de consultas.

## Licencia de Yahoo Finance

`yfinance` no es una API oficial de Yahoo. Sus datos se ofrecen para uso personal, educativo y de investigación, según los términos de Yahoo. AlphaInvest AI es un proyecto académico sin fines comerciales. Para un uso comercial habría que contratar un proveedor con licencia. Alpha Vantage se mantiene como respaldo.

## Pasos de operación después de estos cambios

1. Aplicar la migración: `PYTHONPATH=src alembic upgrade head` (desde `backend/`).
2. Corregir el efectivo existente:
   - Simulacro: `PYTHONPATH=src python scripts/portfolio/reconcile_cash_balances.py`.
   - Aplicar: agregar `--apply`.
3. Reiniciar el worker. Los activos en uso se sincronizan en la siguiente corrida de precios (23:00 hora de México). También se puede lanzar una sincronización manual.

## Registro de decisiones

- 2026-09-23: los cambios de interfaz no modifican contratos API ni la base de datos.
- 2026-09-23: el criterio de anualización se basa en GIPS: no anualizar periodos menores a un año.
- 2026-09-23 (Jose): agregar una posición es una compra virtual que descuenta efectivo.
- 2026-09-23 (Jose): el worker sincroniza los activos en uso; Yahoo Finance es la fuente principal de precios y Alpha Vantage el respaldo (y la fuente de noticias).
- 2026-09-23: no hay conversión de divisas, así que se rechazan posiciones en una moneda distinta a la base del portafolio.
