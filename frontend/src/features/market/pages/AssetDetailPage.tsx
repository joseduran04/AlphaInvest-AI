import { type FormEvent, useState } from 'react'
import { Link, useParams } from 'react-router'

import type { FinancialIndicatorType, IndicatorCalculationRequest } from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { useAsset } from '@/features/market/hooks/useAsset'
import { useAssetIndicators } from '@/features/market/hooks/useAssetIndicators'
import { useCalculateIndicators } from '@/features/market/hooks/useCalculateIndicators'
import { useFinancialSources } from '@/features/market/hooks/useFinancialSources'
import { useLatestPrice } from '@/features/market/hooks/useLatestPrice'
import { usePriceHistory } from '@/features/market/hooks/usePriceHistory'
import { useSyncAssetPrices } from '@/features/market/hooks/useSyncAssetPrices'

import { AssetPriceChart } from '@/features/market/components/AssetPriceChart'

import '@/styles/asset-detail.css'

const HISTORY_PAGE_SIZE = 20
const INDICATOR_LIMIT = 50

type DirectIndicatorType = Extract<
  FinancialIndicatorType,
  'SMA' | 'EMA' | 'RSI' | 'VOLATILIDAD' | 'MACD'
>

interface IndicatorFormState {
  sourceId: string
  indicatorType: DirectIndicatorType
  period: string
  fastPeriod: string
  slowPeriod: string
  signalPeriod: string
}

const initialIndicatorForm: IndicatorFormState = {
  sourceId: '',
  indicatorType: 'SMA',
  period: '20',
  fastPeriod: '12',
  slowPeriod: '26',
  signalPeriod: '9',
}

function formatDate(value: string): string {
  const date = new Date(`${value}T00:00:00`)

  return new Intl.DateTimeFormat('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatMoney(value: string, currency: string): string {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return `${value} ${currency}`
  }

  try {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency,
      maximumFractionDigits: 4,
    }).format(numericValue)
  } catch {
    return `${numericValue.toLocaleString('es-MX')} ${currency}`
  }
}

function formatNumber(value: string): string {
  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return value
  }

  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits: 6,
  }).format(numericValue)
}

function parseIndicatorPeriod(value: string): number | null {
  const parsed = Number(value)

  if (!Number.isInteger(parsed) || parsed < 2 || parsed > 500) {
    return null
  }

  return parsed
}

export function AssetDetailPage() {
  const { assetId } = useParams<{ assetId: string }>()
  const { hasPermission } = useAuth()

  const canReadPrices = hasPermission('precios.leer')
  const canSyncPrices = hasPermission('precios.cargar')
  const canReadIndicators = hasPermission('indicadores.leer')
  const canCalculateIndicators = hasPermission('indicadores.calcular')
  const canReadSources = hasPermission('fuentes.leer')

  const [historyPage, setHistoryPage] = useState(0)
  const [indicatorForm, setIndicatorForm] = useState<IndicatorFormState>(initialIndicatorForm)
  const [indicatorFormError, setIndicatorFormError] = useState<string | null>(null)

  const resolvedAssetId = assetId ?? null

  const assetQuery = useAsset(resolvedAssetId)

  const latestPriceQuery = useLatestPrice(resolvedAssetId, {}, canReadPrices)

  const priceHistoryQuery = usePriceHistory(
    resolvedAssetId,
    {
      limit: HISTORY_PAGE_SIZE,
      offset: historyPage * HISTORY_PAGE_SIZE,
    },
    canReadPrices,
  )

  const indicatorsQuery = useAssetIndicators(
    resolvedAssetId,
    {
      limit: INDICATOR_LIMIT,
      offset: 0,
    },
    canReadIndicators,
  )

  const sourcesQuery = useFinancialSources({}, canCalculateIndicators && canReadSources)

  const syncPricesMutation = useSyncAssetPrices(assetId ?? '')
  const calculateIndicatorsMutation = useCalculateIndicators(assetId ?? '')

  if (!assetId) {
    return (
      <PageErrorState
        title="Activo no válido"
        message="No se recibió un identificador de activo válido."
      />
    )
  }

  if (assetQuery.isPending) {
    return <PageLoadingState message="Cargando detalle del activo..." />
  }

  if (assetQuery.isError) {
    return (
      <PageErrorState
        title="No fue posible cargar el activo"
        message={assetQuery.error.message}
        onRetry={() => {
          void assetQuery.refetch()
        }}
      />
    )
  }

  const asset = assetQuery.data

  const historyItems = priceHistoryQuery.data?.items ?? []
  const historyTotal = priceHistoryQuery.data?.total ?? 0
  const historyTotalPages = Math.max(1, Math.ceil(historyTotal / HISTORY_PAGE_SIZE))

  function handleIndicatorSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setIndicatorFormError(null)

    if (!indicatorForm.sourceId) {
      setIndicatorFormError('Selecciona una fuente financiera.')
      return
    }

    let calculation: IndicatorCalculationRequest['calculations'][number]

    if (indicatorForm.indicatorType === 'MACD') {
      const fastPeriod = parseIndicatorPeriod(indicatorForm.fastPeriod)
      const slowPeriod = parseIndicatorPeriod(indicatorForm.slowPeriod)
      const signalPeriod = parseIndicatorPeriod(indicatorForm.signalPeriod)

      if (fastPeriod === null || slowPeriod === null || signalPeriod === null) {
        setIndicatorFormError('Los periodos de MACD deben ser enteros entre 2 y 500.')
        return
      }

      if (slowPeriod <= fastPeriod) {
        setIndicatorFormError('El periodo lento de MACD debe ser mayor que el periodo rápido.')
        return
      }

      calculation = {
        indicator_type: 'MACD',
        fast_period: fastPeriod,
        slow_period: slowPeriod,
        signal_period: signalPeriod,
      }
    } else {
      const period = parseIndicatorPeriod(indicatorForm.period)

      if (period === null) {
        setIndicatorFormError('El periodo debe ser un número entero entre 2 y 500.')
        return
      }

      calculation = {
        indicator_type: indicatorForm.indicatorType,
        period,
      }
    }

    calculateIndicatorsMutation.mutate({
      source_id: indicatorForm.sourceId,
      calculations: [calculation],
    })
  }

  return (
    <section className="asset-detail-page">
      <div className="asset-detail-page__back">
        <Link to="/app/market">← Volver al mercado</Link>
      </div>

      <header className="asset-detail-page__header">
        <div>
          <p className="app__eyebrow">Mercado</p>
          <h1>
            {asset.symbol} · {asset.name}
          </h1>
          <p className="app__description">
            Consulta la información registrada, precios históricos e indicadores financieros
            disponibles para este activo.
          </p>
        </div>

        <span className={`market-status market-status--${asset.status.toLowerCase()}`}>
          {asset.status}
        </span>
      </header>

      <section className="asset-detail-summary">
        <article className="asset-detail-card">
          <header className="asset-detail-card__header">
            <div>
              <span className="asset-detail-card__eyebrow">Información general</span>
              <h2>Datos del activo</h2>
            </div>
          </header>

          <dl className="asset-detail-data-grid">
            <div>
              <dt>Símbolo</dt>
              <dd>{asset.symbol}</dd>
            </div>

            <div>
              <dt>Mercado</dt>
              <dd>
                {asset.market.name} ({asset.market.code})
              </dd>
            </div>

            <div>
              <dt>Tipo</dt>
              <dd>{asset.asset_type.name}</dd>
            </div>

            <div>
              <dt>Moneda</dt>
              <dd>{asset.currency}</dd>
            </div>

            <div>
              <dt>Sector</dt>
              <dd>{asset.sector ?? 'No disponible'}</dd>
            </div>

            <div>
              <dt>Industria</dt>
              <dd>{asset.industry ?? 'No disponible'}</dd>
            </div>

            <div>
              <dt>ISIN</dt>
              <dd>{asset.isin ?? 'No disponible'}</dd>
            </div>

            <div>
              <dt>Actualizado</dt>
              <dd>{formatDateTime(asset.updated_at)}</dd>
            </div>
          </dl>

          {asset.description ? (
            <p className="asset-detail-description">{asset.description}</p>
          ) : null}
        </article>

        {canReadPrices ? (
          <article className="asset-detail-card">
            <header className="asset-detail-card__header">
              <div>
                <span className="asset-detail-card__eyebrow">Precio</span>
                <h2>Último precio registrado</h2>
              </div>

              {canSyncPrices ? (
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={syncPricesMutation.isPending}
                  onClick={() => {
                    syncPricesMutation.mutate()
                  }}
                >
                  {syncPricesMutation.isPending ? 'Sincronizando...' : 'Sincronizar precios'}
                </button>
              ) : null}
            </header>

            {latestPriceQuery.isPending ? (
              <div className="asset-detail-inline-state">Cargando último precio...</div>
            ) : latestPriceQuery.isError ? (
              <div className="asset-detail-inline-state asset-detail-inline-state--error">
                <p>{latestPriceQuery.error.message}</p>

                <button
                  className="button button--secondary"
                  type="button"
                  onClick={() => {
                    void latestPriceQuery.refetch()
                  }}
                >
                  Reintentar
                </button>
              </div>
            ) : (
              <div className="asset-detail-latest-price">
                <strong>
                  {formatMoney(
                    latestPriceQuery.data.price.close,
                    latestPriceQuery.data.price.currency,
                  )}
                </strong>

                <span>
                  {formatDate(latestPriceQuery.data.price.date)} ·{' '}
                  {latestPriceQuery.data.price.source.name}
                </span>
              </div>
            )}

            {syncPricesMutation.isError ? (
              <p className="asset-detail-feedback asset-detail-feedback--error">
                {syncPricesMutation.error.message}
              </p>
            ) : null}

            {syncPricesMutation.isSuccess ? (
              <div className="asset-detail-feedback asset-detail-feedback--success">
                <strong>Sincronización completada</strong>
                <span>
                  Recibidos: {syncPricesMutation.data.received} · Creados:{' '}
                  {syncPricesMutation.data.created} · Actualizados:{' '}
                  {syncPricesMutation.data.updated}
                </span>
              </div>
            ) : null}
          </article>
        ) : null}
      </section>

      {canReadPrices ? (
        <section className="asset-detail-card">
          <header className="asset-detail-card__header">
            <div>
              <span className="asset-detail-card__eyebrow">Gráfica</span>
              <h2>Evolución del precio</h2>
            </div>
          </header>

          <AssetPriceChart assetId={asset.id} symbol={asset.symbol} />
        </section>
      ) : null}

      {canReadPrices ? (
        <section className="asset-detail-card">
          <header className="asset-detail-card__header">
            <div>
              <span className="asset-detail-card__eyebrow">Histórico de precios</span>
              <h2>Precios registrados</h2>
            </div>
          </header>

          {priceHistoryQuery.isPending ? (
            <div className="asset-detail-inline-state">Cargando histórico...</div>
          ) : priceHistoryQuery.isError ? (
            <div className="asset-detail-inline-state asset-detail-inline-state--error">
              <p>{priceHistoryQuery.error.message}</p>

              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  void priceHistoryQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : historyItems.length === 0 ? (
            <div className="asset-detail-inline-state">
              No hay precios históricos registrados para este activo.
            </div>
          ) : (
            <>
              <div className="asset-detail-table-wrapper">
                <table className="asset-detail-table">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Apertura</th>
                      <th>Máximo</th>
                      <th>Mínimo</th>
                      <th>Cierre</th>
                      <th>Volumen</th>
                      <th>Fuente</th>
                    </tr>
                  </thead>

                  <tbody>
                    {historyItems.map((price) => (
                      <tr key={price.id}>
                        <td>{formatDate(price.date)}</td>
                        <td>
                          {price.open === null ? '—' : formatMoney(price.open, price.currency)}
                        </td>
                        <td>
                          {price.high === null ? '—' : formatMoney(price.high, price.currency)}
                        </td>
                        <td>{price.low === null ? '—' : formatMoney(price.low, price.currency)}</td>
                        <td>
                          <strong>{formatMoney(price.close, price.currency)}</strong>
                        </td>
                        <td>{price.volume === null ? '—' : formatNumber(price.volume)}</td>
                        <td>{price.source.name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <footer className="asset-detail-pagination">
                <span>
                  Página {historyPage + 1} de {historyTotalPages}
                </span>

                <div>
                  <button
                    className="button button--secondary"
                    type="button"
                    disabled={historyPage === 0}
                    onClick={() => setHistoryPage((current) => Math.max(current - 1, 0))}
                  >
                    Anterior
                  </button>

                  <button
                    className="button button--secondary"
                    type="button"
                    disabled={(historyPage + 1) * HISTORY_PAGE_SIZE >= historyTotal}
                    onClick={() => setHistoryPage((current) => current + 1)}
                  >
                    Siguiente
                  </button>
                </div>
              </footer>
            </>
          )}
        </section>
      ) : null}

      {canReadIndicators ? (
        <section className="asset-detail-card">
          <header className="asset-detail-card__header">
            <div>
              <span className="asset-detail-card__eyebrow">Indicadores técnicos</span>
              <h2>Indicadores calculados</h2>
            </div>
          </header>

          {indicatorsQuery.isPending ? (
            <div className="asset-detail-inline-state">Cargando indicadores...</div>
          ) : indicatorsQuery.isError ? (
            <div className="asset-detail-inline-state asset-detail-inline-state--error">
              <p>{indicatorsQuery.error.message}</p>

              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  void indicatorsQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : indicatorsQuery.data.items.length === 0 ? (
            <div className="asset-detail-inline-state">
              No hay indicadores calculados para este activo.
            </div>
          ) : (
            <div className="asset-detail-table-wrapper">
              <table className="asset-detail-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Indicador</th>
                    <th>Periodo</th>
                    <th>Valor</th>
                    <th>Calculado</th>
                  </tr>
                </thead>

                <tbody>
                  {indicatorsQuery.data.items.map((indicator) => (
                    <tr key={indicator.id}>
                      <td>{formatDate(indicator.date)}</td>
                      <td>{indicator.indicator_type}</td>
                      <td>{indicator.period}</td>
                      <td>
                        <strong>{formatNumber(indicator.value)}</strong>
                      </td>
                      <td>{formatDateTime(indicator.calculated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : null}

      {canCalculateIndicators ? (
        <section className="asset-detail-card">
          <header className="asset-detail-card__header">
            <div>
              <span className="asset-detail-card__eyebrow">Cálculo técnico</span>
              <h2>Calcular indicador</h2>
            </div>
          </header>

          {!canReadSources ? (
            <div className="asset-detail-inline-state asset-detail-inline-state--error">
              Tu usuario puede calcular indicadores, pero no puede consultar las fuentes financieras
              necesarias para seleccionar una fuente.
            </div>
          ) : sourcesQuery.isPending ? (
            <div className="asset-detail-inline-state">Cargando fuentes financieras...</div>
          ) : sourcesQuery.isError ? (
            <div className="asset-detail-inline-state asset-detail-inline-state--error">
              <p>{sourcesQuery.error.message}</p>

              <button
                className="button button--secondary"
                type="button"
                onClick={() => {
                  void sourcesQuery.refetch()
                }}
              >
                Reintentar
              </button>
            </div>
          ) : sourcesQuery.data.items.length === 0 ? (
            <div className="asset-detail-inline-state">
              No hay fuentes financieras activas disponibles.
            </div>
          ) : (
            <form className="asset-indicator-form" onSubmit={handleIndicatorSubmit}>
              <div className="asset-indicator-form__grid">
                <label className="market-field">
                  <span>Fuente financiera</span>
                  <select
                    required
                    value={indicatorForm.sourceId}
                    onChange={(event) =>
                      setIndicatorForm((current) => ({
                        ...current,
                        sourceId: event.target.value,
                      }))
                    }
                  >
                    <option value="">Selecciona una fuente</option>

                    {sourcesQuery.data.items.map((source) => (
                      <option key={source.id} value={source.id}>
                        {source.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="market-field">
                  <span>Indicador</span>
                  <select
                    value={indicatorForm.indicatorType}
                    onChange={(event) => {
                      setIndicatorFormError(null)

                      setIndicatorForm((current) => ({
                        ...current,
                        indicatorType: event.target.value as DirectIndicatorType,
                      }))
                    }}
                  >
                    <option value="SMA">SMA</option>
                    <option value="EMA">EMA</option>
                    <option value="RSI">RSI</option>
                    <option value="VOLATILIDAD">Volatilidad</option>
                    <option value="MACD">MACD</option>
                  </select>
                </label>

                {indicatorForm.indicatorType === 'MACD' ? (
                  <>
                    <label className="market-field">
                      <span>Periodo rápido</span>
                      <input
                        type="number"
                        min={2}
                        max={500}
                        required
                        value={indicatorForm.fastPeriod}
                        onChange={(event) =>
                          setIndicatorForm((current) => ({
                            ...current,
                            fastPeriod: event.target.value,
                          }))
                        }
                      />
                    </label>

                    <label className="market-field">
                      <span>Periodo lento</span>
                      <input
                        type="number"
                        min={2}
                        max={500}
                        required
                        value={indicatorForm.slowPeriod}
                        onChange={(event) =>
                          setIndicatorForm((current) => ({
                            ...current,
                            slowPeriod: event.target.value,
                          }))
                        }
                      />
                    </label>

                    <label className="market-field">
                      <span>Periodo de señal</span>
                      <input
                        type="number"
                        min={2}
                        max={500}
                        required
                        value={indicatorForm.signalPeriod}
                        onChange={(event) =>
                          setIndicatorForm((current) => ({
                            ...current,
                            signalPeriod: event.target.value,
                          }))
                        }
                      />
                    </label>
                  </>
                ) : (
                  <label className="market-field">
                    <span>Periodo</span>
                    <input
                      type="number"
                      min={2}
                      max={500}
                      required
                      value={indicatorForm.period}
                      onChange={(event) =>
                        setIndicatorForm((current) => ({
                          ...current,
                          period: event.target.value,
                        }))
                      }
                    />
                  </label>
                )}
              </div>

              {indicatorFormError ? (
                <p className="asset-detail-feedback asset-detail-feedback--error">
                  {indicatorFormError}
                </p>
              ) : null}

              {calculateIndicatorsMutation.isError ? (
                <p className="asset-detail-feedback asset-detail-feedback--error">
                  {calculateIndicatorsMutation.error.message}
                </p>
              ) : null}

              {calculateIndicatorsMutation.isSuccess ? (
                <div className="asset-detail-feedback asset-detail-feedback--success">
                  <strong>Cálculo completado</strong>
                  <span>
                    Calculados: {calculateIndicatorsMutation.data.total_calculated} · Creados:{' '}
                    {calculateIndicatorsMutation.data.total_created} · Actualizados:{' '}
                    {calculateIndicatorsMutation.data.total_updated}
                  </span>
                </div>
              ) : null}

              <div className="asset-indicator-form__actions">
                <button
                  className="button button--primary"
                  type="submit"
                  disabled={calculateIndicatorsMutation.isPending}
                >
                  {calculateIndicatorsMutation.isPending ? 'Calculando...' : 'Calcular indicador'}
                </button>
              </div>
            </form>
          )}
        </section>
      ) : null}
    </section>
  )
}
