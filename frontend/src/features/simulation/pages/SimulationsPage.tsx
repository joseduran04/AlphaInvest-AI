import { useState } from 'react'

import type { SimulationConfigurationListQuery, SimulationConfigurationStatus } from '@/api/types'
import { PageEmptyState } from '@/components/PageEmptyState'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { CreateSimulationConfigurationForm } from '@/features/simulation/components/CreateSimulationConfigurationForm'
import { useSimulationConfigurations } from '@/features/simulation/hooks/useSimulationConfigurations'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/simulation.css'

const PAGE_SIZE = 20

function formatSimulationStatus(status: SimulationConfigurationStatus): string {
  switch (status) {
    case 'BORRADOR':
      return 'Borrador'
    case 'LISTA':
      return 'Lista'
    case 'ARCHIVADA':
      return 'Archivada'
  }
}

function formatSimulationType(type: string): string {
  switch (type) {
    case 'HISTORICA':
      return 'Histórica'
    case 'MONTE_CARLO':
      return 'Monte Carlo'
    case 'PROYECCION':
      return 'Proyección'
    case 'ESCENARIO':
      return 'Escenario'
    default:
      return type
  }
}

export function SimulationsPage() {
  const { hasPermission } = useAuth()

  const canReadSimulations = hasPermission('simulaciones.leer')
  const canCreateSimulations = hasPermission('simulaciones.crear')

  const [status, setStatus] = useState<SimulationConfigurationStatus | ''>('')
  const [page, setPage] = useState(0)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const params: SimulationConfigurationListQuery = {
    estado: status || undefined,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  }

  const configurationsQuery = useSimulationConfigurations(params, canReadSimulations)

  if (!canReadSimulations) {
    return (
      <PageErrorState
        title="Acceso restringido"
        message="Tu usuario no cuenta con permiso para consultar simulaciones."
      />
    )
  }

  const configurations = configurationsQuery.data?.items ?? []
  const total = configurationsQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const firstResult = total === 0 ? 0 : page * PAGE_SIZE + 1
  const lastResult = Math.min((page + 1) * PAGE_SIZE, total)

  function handleStatusChange(nextStatus: SimulationConfigurationStatus | '') {
    setStatus(nextStatus)
    setPage(0)
  }

  return (
    <section className="simulation-page">
      <header className="simulation-page__header">
        <div>
          <p className="app__eyebrow">Simulaciones</p>
          <h1>Simulaciones de inversión</h1>
          <p className="app__description">
            Configura escenarios históricos para analizar el comportamiento de una estrategia de
            inversión utilizando información de mercado.
          </p>
        </div>

        {canCreateSimulations && !showCreateForm ? (
          <button
            className="button button--primary"
            type="button"
            onClick={() => setShowCreateForm(true)}
          >
            Nueva simulación
          </button>
        ) : null}
      </header>

      {canCreateSimulations && showCreateForm ? (
        <CreateSimulationConfigurationForm
          onCancel={() => setShowCreateForm(false)}
          onCreated={() => setShowCreateForm(false)}
        />
      ) : null}

      <section className="simulation-filters">
        <header className="simulation-filters__header">
          <div>
            <h2>Filtros</h2>
            <p>Consulta las configuraciones según su estado actual.</p>
          </div>
        </header>

        <div className="simulation-filters__grid">
          <label className="simulation-field">
            <span>Estado</span>

            <select
              value={status}
              onChange={(event) =>
                handleStatusChange(event.target.value as SimulationConfigurationStatus | '')
              }
            >
              <option value="">Todos</option>
              <option value="BORRADOR">Borrador</option>
              <option value="LISTA">Lista</option>
              <option value="ARCHIVADA">Archivada</option>
            </select>
          </label>
        </div>
      </section>

      <section className="simulation-results">
        <header className="simulation-results__header">
          <div>
            <p className="simulation-results__eyebrow">Resultados</p>
            <h2>Configuraciones registradas</h2>
          </div>

          {!configurationsQuery.isPending && !configurationsQuery.isError ? (
            <span className="simulation-results__count">{total} registros</span>
          ) : null}
        </header>

        {configurationsQuery.isPending ? (
          <PageLoadingState message="Cargando simulaciones..." />
        ) : configurationsQuery.isError ? (
          <PageErrorState
            title="No fue posible cargar las simulaciones"
            message={configurationsQuery.error.message}
            onRetry={() => {
              void configurationsQuery.refetch()
            }}
          />
        ) : configurations.length === 0 ? (
          <PageEmptyState
            title="No se encontraron simulaciones"
            description={
              status
                ? 'No existen configuraciones con el estado seleccionado.'
                : 'Todavía no existen configuraciones de simulación registradas.'
            }
            action={
              status ? (
                <button
                  className="button button--secondary"
                  type="button"
                  onClick={() => handleStatusChange('')}
                >
                  Mostrar todas
                </button>
              ) : canCreateSimulations ? (
                <button
                  className="button button--primary"
                  type="button"
                  onClick={() => setShowCreateForm(true)}
                >
                  Nueva simulación
                </button>
              ) : undefined
            }
          />
        ) : (
          <>
            <div className="simulation-cards">
              {configurations.map((configuration) => (
                <article className="simulation-card" key={configuration.id}>
                  <header className="simulation-card__header">
                    <div>
                      <strong>{configuration.nombre}</strong>
                      <span>{formatSimulationType(configuration.tipo_simulacion)}</span>
                    </div>

                    <span
                      className={`simulation-status simulation-status--${configuration.estado.toLowerCase()}`}
                    >
                      {formatSimulationStatus(configuration.estado)}
                    </span>
                  </header>

                  {configuration.descripcion ? (
                    <p className="simulation-card__description">{configuration.descripcion}</p>
                  ) : null}

                  <dl className="simulation-card__details">
                    <div>
                      <dt>Capital inicial</dt>
                      <dd>
                        {formatCurrency(configuration.capital_inicial, configuration.moneda_base)}
                      </dd>
                    </div>

                    <div>
                      <dt>Moneda base</dt>
                      <dd>{configuration.moneda_base}</dd>
                    </div>

                    <div>
                      <dt>Fecha de inicio</dt>
                      <dd>{configuration.fecha_inicio}</dd>
                    </div>

                    <div>
                      <dt>Fecha final</dt>
                      <dd>{configuration.fecha_fin}</dd>
                    </div>
                  </dl>

                  <p className="simulation-card__pending-detail">
                    La configuración de activos, distribución y ejecución estará disponible en el
                    detalle de la simulación.
                  </p>
                </article>
              ))}
            </div>

            <footer className="simulation-pagination">
              <p>
                Mostrando {firstResult}–{lastResult} de {total}
              </p>

              <div className="simulation-pagination__controls">
                <button
                  className="button button--secondary"
                  type="button"
                  disabled={page === 0}
                  onClick={() => setPage((current) => Math.max(0, current - 1))}
                >
                  Anterior
                </button>

                <span>
                  Página {page + 1} de {totalPages}
                </span>

                <button
                  className="button button--secondary"
                  type="button"
                  disabled={(page + 1) * PAGE_SIZE >= total}
                  onClick={() => setPage((current) => current + 1)}
                >
                  Siguiente
                </button>
              </div>
            </footer>
          </>
        )}
      </section>
    </section>
  )
}
