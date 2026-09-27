import type { AssetResponse, SimulationAssetResultResponse } from '@/api/types'
import { getFinancialToneClass } from '@/lib/financialTone'
import { formatCurrency } from '@/lib/formatters'
import {
  buildAssetBreakdown,
  formatQuantity,
  formatSignedCurrency,
  formatSignedPercentage,
} from '@/lib/simulationBreakdown'

interface SimulationAssetBreakdownProps {
  result: SimulationAssetResultResponse
  marketAsset?: AssetResponse
  /** Moneda de la simulación. */
  currency: string
  /** Capital inicial total de la simulación, para explicar el % asignado. */
  initialCapital: string
  /** Si el periodo dura al menos un año, la volatilidad anualizada se muestra sin plegar. */
  annualizationIsRepresentative: boolean
}

function detailString(detail: Record<string, unknown> | null, key: string): string | null {
  const value = detail?.[key]

  return typeof value === 'string' ? value : null
}

function formatPercentage(value: string | null): string {
  if (value === null) {
    return 'No disponible'
  }

  const parsed = Number(value)

  return Number.isFinite(parsed) ? `${parsed.toFixed(2)} %` : value
}

/**
 * Resultado de un activo explicado paso a paso:
 * dinero asignado → acciones compradas → precio al final → valor final,
 * seguido de las operaciones que producen cada cifra.
 */
export function SimulationAssetBreakdown({
  result,
  marketAsset,
  currency,
  initialCapital,
  annualizationIsRepresentative,
}: SimulationAssetBreakdownProps) {
  const symbol = marketAsset?.symbol ?? 'Activo'
  const assetTitle = marketAsset ? `${marketAsset.symbol} · ${marketAsset.name}` : result.activo_id
  const priceCurrency = marketAsset?.currency ?? currency
  const isShare = /acci|etf/i.test(marketAsset?.asset_type.name ?? '')
  const unitsLabel = isShare ? 'acciones' : 'unidades'
  const unitLabel = isShare ? 'acción' : 'unidad'
  const boughtLabel = isShare ? 'Acciones compradas' : 'Unidades compradas'

  const breakdown = buildAssetBreakdown({
    allocatedCapital: result.capital_asignado,
    initialPrice: result.precio_inicial,
    finalPrice: result.precio_final,
    initialQuantity: result.cantidad_inicial,
    finalQuantity: detailString(result.detalle, 'cantidad_final'),
    finalValue: result.valor_final,
    profitLoss: result.ganancia_perdida,
    contributions: detailString(result.detalle, 'aportaciones_totales'),
  })

  const money = (value: number) => formatCurrency(value, currency)
  const price = (value: number) => formatCurrency(value, priceCurrency)

  const volatility = (
    <div>
      <dt>Volatilidad anualizada</dt>
      <dd>{formatPercentage(result.volatilidad)}</dd>
      <span className="metric-hint">
        Qué tanto subía y bajaba el precio día con día, escalado a un año. Más alta = más riesgo.
      </span>
    </div>
  )

  return (
    <article className="simulation-result-asset">
      <header className="simulation-result-asset__header">
        <div>
          <strong>{assetTitle}</strong>
          <span>
            {marketAsset
              ? `${marketAsset.asset_type.name} · ${marketAsset.market.name}`
              : 'Información de mercado no disponible'}
          </span>
        </div>

        <div className="simulation-result-asset__return">
          <span className={getFinancialToneClass(result.rendimiento_porcentaje)}>
            {formatPercentage(result.rendimiento_porcentaje)}
          </span>
          <span className="metric-hint">rendimiento</span>
        </div>
      </header>

      {breakdown === null ? (
        <p className="metric-hint">
          No hay datos suficientes para explicar el cálculo de este activo.
        </p>
      ) : (
        <>
          <ol className="asset-flow" aria-label={`Cómo se obtuvo el resultado de ${symbol}`}>
            <li className="asset-flow__step">
              <span className="asset-flow__index" aria-hidden="true">
                1
              </span>
              <span className="asset-flow__label">Dinero asignado</span>
              <strong className="asset-flow__value">{money(breakdown.allocatedCapital)}</strong>
              <span className="asset-flow__note">
                {formatPercentage(result.porcentaje_asignado)} de{' '}
                {formatCurrency(initialCapital, currency)}
              </span>
            </li>

            <li className="asset-flow__step">
              <span className="asset-flow__index" aria-hidden="true">
                2
              </span>
              <span className="asset-flow__label">{boughtLabel}</span>
              <strong className="asset-flow__value">
                {formatQuantity(breakdown.initialQuantity)}
              </strong>
              <span className="asset-flow__note">
                {`a ${price(breakdown.initialPrice)} cada una`}
              </span>
            </li>

            <li className="asset-flow__step">
              <span className="asset-flow__index" aria-hidden="true">
                3
              </span>
              <span className="asset-flow__label">Precio al final</span>
              <strong className="asset-flow__value">{price(breakdown.finalPrice)}</strong>
              <span className={`asset-flow__note ${getFinancialToneClass(breakdown.priceChange)}`}>
                {`${formatSignedCurrency(breakdown.priceChange, priceCurrency)} por ${unitLabel} (${formatSignedPercentage(breakdown.priceChangePercentage)})`}
              </span>
            </li>

            <li className="asset-flow__step asset-flow__step--result">
              <span className="asset-flow__index" aria-hidden="true">
                4
              </span>
              <span className="asset-flow__label">Valor final</span>
              <strong className="asset-flow__value">{money(breakdown.finalValue)}</strong>
              <span className={`asset-flow__note ${getFinancialToneClass(breakdown.profitLoss)}`}>
                {`${breakdown.profitLoss >= 0 ? 'Ganancia' : 'Pérdida'} ${formatSignedCurrency(breakdown.profitLoss, currency)}`}
              </span>
            </li>
          </ol>

          <div className="asset-formula">
            <strong className="asset-formula__title">¿De dónde salen estas cifras?</strong>

            <p className="metric-hint">
              {`No se compran ${unitsLabel} completas: con ${money(breakdown.allocatedCapital)} se compra la fracción que alcance (como en los brókers que permiten acciones fraccionarias). Por eso la ganancia es el cambio de precio multiplicado por las ${unitsLabel} que tienes, no solo el cambio de precio.`}
            </p>

            <dl className="asset-formula__rows">
              {breakdown.hasCommission ? (
                <div>
                  <dt>{`Dinero que compra ${unitsLabel}`}</dt>
                  <dd>
                    <span className="asset-formula__expression">
                      {`${money(breakdown.allocatedCapital)} − ${money(breakdown.commission)} de comisión`}
                    </span>
                    <span className="asset-formula__result">
                      {`= ${money(breakdown.investedAtStart)}`}
                    </span>
                  </dd>
                </div>
              ) : null}

              <div>
                <dt>{boughtLabel}</dt>
                <dd>
                  <span className="asset-formula__expression">
                    {`${money(breakdown.investedAtStart)} ÷ ${price(breakdown.initialPrice)}`}
                  </span>
                  <span className="asset-formula__result">
                    {`= ${formatQuantity(breakdown.initialQuantity)}`}
                  </span>
                </dd>
              </div>

              <div>
                <dt>{`Cambio por ${unitLabel}`}</dt>
                <dd>
                  <span className="asset-formula__expression">
                    {`${price(breakdown.finalPrice)} − ${price(breakdown.initialPrice)}`}
                  </span>
                  <span
                    className={`asset-formula__result ${getFinancialToneClass(breakdown.priceChange)}`}
                  >
                    {`= ${formatSignedCurrency(breakdown.priceChange, priceCurrency)}`}
                  </span>
                </dd>
              </div>

              {breakdown.hasContributions ? (
                <>
                  <div>
                    <dt>Valor final</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`${formatQuantity(breakdown.finalQuantity)} ${unitsLabel} × ${price(breakdown.finalPrice)}`}
                      </span>
                      <span className="asset-formula__result">
                        {`= ${money(breakdown.finalValue)}`}
                      </span>
                    </dd>
                  </div>

                  <div>
                    <dt>Aportaciones</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`Con cada aportación se compraron más ${unitsLabel}: pasaste de ${formatQuantity(breakdown.initialQuantity)} a ${formatQuantity(breakdown.finalQuantity)}.`}
                      </span>
                      <span className="asset-formula__result">
                        {`= ${money(breakdown.contributions)}`}
                      </span>
                    </dd>
                  </div>

                  <div>
                    <dt>Ganancia / pérdida</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`${money(breakdown.finalValue)} − ${money(breakdown.allocatedCapital)} asignados`}
                      </span>
                      <span
                        className={`asset-formula__result ${getFinancialToneClass(breakdown.profitLoss)}`}
                      >
                        {`= ${formatSignedCurrency(breakdown.profitLoss, currency)}`}
                      </span>
                    </dd>
                  </div>

                  <div>
                    <dt>Sin contar aportaciones</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`${formatSignedCurrency(breakdown.profitLoss, currency)} − ${money(breakdown.contributions)} aportados`}
                      </span>
                      <span
                        className={`asset-formula__result ${getFinancialToneClass(breakdown.profitLoss - breakdown.contributions)}`}
                      >
                        {`= ${formatSignedCurrency(breakdown.profitLoss - breakdown.contributions, currency)}`}
                      </span>
                    </dd>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <dt>Ganancia / pérdida</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`${formatSignedCurrency(breakdown.priceChange, priceCurrency)} × ${formatQuantity(breakdown.initialQuantity)} ${unitsLabel}${breakdown.hasCommission ? ` − ${money(breakdown.commission)} de comisión` : ''}`}
                      </span>
                      <span
                        className={`asset-formula__result ${getFinancialToneClass(breakdown.profitLoss)}`}
                      >
                        {`= ${formatSignedCurrency(breakdown.profitLoss, currency)}`}
                      </span>
                    </dd>
                  </div>

                  <div>
                    <dt>Valor final</dt>
                    <dd>
                      <span className="asset-formula__expression">
                        {`${money(breakdown.allocatedCapital)} ${breakdown.profitLoss >= 0 ? '+' : '−'} ${money(Math.abs(breakdown.profitLoss))}`}
                      </span>
                      <span className="asset-formula__result">
                        {`= ${money(breakdown.finalValue)}`}
                      </span>
                    </dd>
                  </div>
                </>
              )}
            </dl>

            <p className="metric-hint">
              Las cifras se muestran redondeadas a dos decimales; el cálculo usa todos los
              decimales, por lo que puede haber diferencias de un centavo.
            </p>
          </div>
        </>
      )}

      <dl className="simulation-result-asset__grid">
        <div>
          <dt>Drawdown máximo</dt>
          <dd>{formatPercentage(result.maximo_drawdown_porcentaje)}</dd>
          <span className="metric-hint">
            La peor caída del valor desde un máximo previo durante el periodo.
          </span>
        </div>

        {annualizationIsRepresentative ? volatility : null}
      </dl>

      <details className="technical-details">
        <summary>Datos técnicos</summary>

        <dl className="simulation-result-asset__grid">
          <div>
            <dt>Cantidad inicial</dt>
            <dd>{breakdown ? formatQuantity(breakdown.initialQuantity, 8) : 'No disponible'}</dd>
          </div>

          <div>
            <dt>Cantidad final</dt>
            <dd>{breakdown ? formatQuantity(breakdown.finalQuantity, 8) : 'No disponible'}</dd>
          </div>

          <div>
            <dt>Aportaciones</dt>
            <dd>{breakdown ? money(breakdown.contributions) : 'No disponible'}</dd>
          </div>

          {annualizationIsRepresentative ? null : volatility}
        </dl>

        {annualizationIsRepresentative ? null : (
          <p className="metric-hint">
            La volatilidad se expresa anualizada; en periodos menores a un año es poco
            representativa.
          </p>
        )}
      </details>
    </article>
  )
}
