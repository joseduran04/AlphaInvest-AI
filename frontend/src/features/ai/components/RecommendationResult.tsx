import type {
  AssetResponse,
  RecommendationAssetResponse,
  RecommendationEvidenceResponse,
  RecommendationResultResponse,
} from '@/api/types'

interface RecommendationResultProps {
  result: RecommendationResultResponse
  asset?: AssetResponse
}

function formatProbability(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'No disponible'
  }

  return `${(numericValue * 100).toFixed(2)} %`
}

function formatDecimal(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return 'No disponible'
  }

  const numericValue = Number(value)

  if (!Number.isFinite(numericValue)) {
    return 'No disponible'
  }

  return numericValue.toFixed(4)
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatRecommendationType(value: string): string {
  switch (value) {
    case 'OBSERVAR':
      return 'Observar'
    case 'COMPRAR_SIMULADO':
      return 'Compra simulada'
    case 'MANTENER':
      return 'Mantener'
    case 'REDUCIR':
      return 'Reducir'
    case 'VENDER_SIMULADO':
      return 'Venta simulada'
    case 'DIVERSIFICAR':
      return 'Diversificar'
    case 'REBALANCEAR':
      return 'Rebalancear'
    case 'EVITAR':
      return 'Evitar'
    default:
      return value
  }
}

function formatRiskLevel(value: string): string {
  return value.replaceAll('_', ' ').toLocaleLowerCase('es-MX')
}

function formatAction(value: string): string {
  return value.replaceAll('_', ' ').toLocaleLowerCase('es-MX')
}

function RecommendationAsset({
  recommendation,
  asset,
}: {
  recommendation: RecommendationAssetResponse
  asset?: AssetResponse
}) {
  return (
    <article className="ai-recommendation-asset">
      <header>
        <div>
          <strong>{asset ? `${asset.symbol} · ${asset.name}` : 'Activo analizado'}</strong>
          <span>{formatAction(recommendation.action)}</span>
        </div>
      </header>

      <dl className="ai-result-grid">
        <div>
          <dt>Precio de referencia</dt>
          <dd>{formatDecimal(recommendation.reference_price)}</dd>
        </div>

        <div>
          <dt>Precio objetivo</dt>
          <dd>{formatDecimal(recommendation.target_price)}</dd>
        </div>

        <div>
          <dt>Confianza</dt>
          <dd>{formatProbability(recommendation.confidence)}</dd>
        </div>

        <div>
          <dt>Prioridad</dt>
          <dd>{recommendation.priority}</dd>
        </div>

        {recommendation.target_percentage ? (
          <div>
            <dt>Porcentaje objetivo</dt>
            <dd>{formatDecimal(recommendation.target_percentage)}</dd>
          </div>
        ) : null}

        {recommendation.loss_limit ? (
          <div>
            <dt>Límite de pérdida</dt>
            <dd>{formatDecimal(recommendation.loss_limit)}</dd>
          </div>
        ) : null}
      </dl>

      {recommendation.justification ? (
        <div className="ai-result__summary">
          <h4>Justificación del activo</h4>
          <p>{recommendation.justification}</p>
        </div>
      ) : null}
    </article>
  )
}

function RecommendationEvidence({ evidence }: { evidence: RecommendationEvidenceResponse }) {
  return (
    <article className="ai-recommendation-evidence">
      <header>
        <strong>{evidence.evidence_type.replaceAll('_', ' ')}</strong>
        <span>{evidence.source_entity}</span>
      </header>

      <p>{evidence.description}</p>

      {evidence.numeric_value !== null && evidence.numeric_value !== undefined ? (
        <dl className="ai-result-grid">
          <div>
            <dt>Valor</dt>
            <dd>
              {formatDecimal(evidence.numeric_value)}
              {evidence.unit ? ` ${evidence.unit}` : ''}
            </dd>
          </div>

          {evidence.weight ? (
            <div>
              <dt>Peso</dt>
              <dd>{formatDecimal(evidence.weight)}</dd>
            </div>
          ) : null}

          {evidence.contribution ? (
            <div>
              <dt>Contribución</dt>
              <dd>{evidence.contribution.toLocaleLowerCase('es-MX')}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </article>
  )
}

export function RecommendationResult({ result, asset }: RecommendationResultProps) {
  return (
    <section className="ai-result">
      <header className="ai-result__header">
        <div>
          <p className="app__eyebrow">Recomendación completada</p>
          <h3>{result.title}</h3>
          <p>{result.summary}</p>
        </div>

        <span className="ai-recommendation-type">{formatRecommendationType(result.type)}</span>
      </header>

      <dl className="ai-result-grid">
        <div>
          <dt>Nivel de riesgo</dt>
          <dd>{formatRiskLevel(result.risk_level)}</dd>
        </div>

        <div>
          <dt>Horizonte</dt>
          <dd>{result.horizon.replaceAll('_', ' ').toLocaleLowerCase('es-MX')}</dd>
        </div>

        <div>
          <dt>Confianza</dt>
          <dd>{formatProbability(result.confidence)}</dd>
        </div>

        <div>
          <dt>Prioridad</dt>
          <dd>{result.priority}</dd>
        </div>

        <div>
          <dt>Estado</dt>
          <dd>{result.status.toLocaleLowerCase('es-MX')}</dd>
        </div>

        <div>
          <dt>Generada</dt>
          <dd>{formatDateTime(result.generated_at)}</dd>
        </div>
      </dl>

      <div className="ai-result__summary">
        <h4>Justificación</h4>
        <p>{result.justification}</p>
      </div>

      {result.assets.length > 0 ? (
        <section className="ai-recommendation-section">
          <h4>Acción sobre el activo</h4>

          {result.assets.map((recommendation) => (
            <RecommendationAsset
              key={`${recommendation.asset_id}-${recommendation.priority}`}
              recommendation={recommendation}
              asset={recommendation.asset_id === asset?.id ? asset : undefined}
            />
          ))}
        </section>
      ) : null}

      {result.evidence.length > 0 ? (
        <section className="ai-recommendation-section">
          <h4>Evidencias consideradas</h4>

          <div className="ai-recommendation-evidence-list">
            {result.evidence.map((evidence) => (
              <RecommendationEvidence key={evidence.id} evidence={evidence} />
            ))}
          </div>
        </section>
      ) : null}

      <aside className="ai-result__disclaimer">
        <strong>Advertencia</strong>
        <p>{result.warning}</p>
      </aside>
    </section>
  )
}
