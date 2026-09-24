import type { AiModelCard } from '@/lib/aiModelCards'

interface ModelCardDetailsProps {
  card: AiModelCard
}

/** Ficha plegable con lo que hace el modelo, sus datos y sus límites. */
export function ModelCardDetails({ card }: ModelCardDetailsProps) {
  return (
    <details className="technical-details">
      <summary>
        Sobre el modelo: {card.name} v{card.version}
      </summary>

      <dl className="model-card">
        <div>
          <dt>Qué hace</dt>
          <dd>{card.whatItDoes}</dd>
        </div>

        <div>
          <dt>Datos de entrenamiento</dt>
          <dd>{card.trainingData}</dd>
        </div>

        {card.horizon ? (
          <div>
            <dt>Horizonte</dt>
            <dd>{card.horizon}</dd>
          </div>
        ) : null}

        <div>
          <dt>Resultado en pruebas</dt>
          <dd>{card.testResult}</dd>
        </div>

        <div>
          <dt>Limitaciones</dt>
          <dd>
            <ul>
              {card.limitations.map((limitation) => (
                <li key={limitation}>{limitation}</li>
              ))}
            </ul>
          </dd>
        </div>
      </dl>
    </details>
  )
}
