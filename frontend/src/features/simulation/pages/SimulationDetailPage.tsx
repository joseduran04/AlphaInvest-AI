import { useState } from 'react'
import { Link, useParams } from 'react-router'

import { ApiError } from '@/api/errors'
import type {
  ContributionFrequency,
  SimulationConfigurationStatus,
  SimulationType,
} from '@/api/types'
import { PageErrorState } from '@/components/PageErrorState'
import { PageLoadingState } from '@/components/PageLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { ArchiveSimulationConfigurationSection } from '@/features/simulation/components/ArchiveSimulationConfigurationSection'
import { EditSimulationConfigurationForm } from '@/features/simulation/components/EditSimulationConfigurationForm'
import { SimulationAssetsSection } from '@/features/simulation/components/SimulationAssetsSection'
import { SimulationExecutionsSection } from '@/features/simulation/components/SimulationExecutionsSection'
import { useSimulationConfiguration } from '@/features/simulation/hooks/useSimulationConfiguration'
import { formatCurrency } from '@/lib/formatters'

import '@/styles/simulation.css'

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

function formatSimulationType(type: SimulationType): string {
  switch (type) {
    case 'HISTORICA':
      return 'Histórica'
    case 'MONTE_CARLO':
      return 'Monte Carlo'
    case 'PROYECCION':
      return 'Proyección'
    case 'ESCENARIO':
      return 'Escenario'
  }
}

function formatContributionFrequency(frequency: ContributionFrequency | null): string {
  switch (frequency) {
    case 'SEMANAL':
      return 'Semanal'
    case 'QUINCENAL':
      return 'Quincenal'
    case 'MENSUAL':
      return 'Mensual'
    case 'TRIMESTRAL':
      return 'Trimestral'
    case 'SEMESTRAL':
      return 'Semestral'
    case 'ANUAL':
      return 'Anual'
    case null:
      return 'Sin aportación periódica'
  }
}

function formatDate(value: string | null | undefined): string {
  if (!value) {
    return 'No disponible'
  }

  const dateOnlyMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)

  if (dateOnlyMatch) {
    const [, year, month, day] = dateOnlyMatch
    const date = new Date(Number(year), Number(month) - 1, Number(day))

    return new Intl.DateTimeFormat('es-MX', {
      dateStyle: 'medium',
    }).format(date)
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('es-MX', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function formatPercentage(value: string | null): string {
  if (value === null) {
    return 'No configurada'
  }

  const parsedValue = Number(value)

  if (!Number.isFinite(parsedValue)) {
    return value
  }

  return `${parsedValue.toFixed(2)} %`
}

function isNotFoundError(error: Error | null): boolean {
  return error instanceof ApiError && error.status === 404
}

export function SimulationDetailPage() {
  const { configurationId } = useParams<{ configurationId: string }>()
  const { hasPermission } = useAuth()

  const [showEditForm, setShowEditForm] = useState(false)

  const normalizedConfigurationId = configurationId ?? null

  const canUpdate = hasPermission('simulaciones.actualizar')
  const canArchive = hasPermission('simulaciones.archivar')
  const canReadExecutions = hasPermission('simulaciones.leer')
  const canExecute = hasPermission('simulaciones.ejecutar')

  const configurationQuery = useSimulationConfiguration(normalizedConfigurationId)

  if (!normalizedConfigurationId) {
    return (
      <PageErrorState
        title="Simulación no válida"
        message="No se proporcionó un identificador de configuración válido."
      />
    )
  }

  if (configurationQuery.isPending) {
    return <PageLoadingState message="Cargando configuración de simulación..." />
  }

  if (configurationQuery.isError) {
    if (isNotFoundError(configurationQuery.error)) {
      return (
        <PageErrorState
          title="Configuración no encontrada"
          message="La configuración solicitada no existe o no está disponible."
        />
      )
    }

    return (
      <PageErrorState
        title="No fue posible cargar la configuración"
        message={configurationQuery.error.message}
        onRetry={() => {
          void configurationQuery.refetch()
        }}
      />
    )
  }

  const configuration = configurationQuery.data
  const isDraft = configuration.estado === 'BORRADOR'
  const canEdit = canUpdate && isDraft

  return (
    <section className="simulation-detail-page">
      <nav className="simulation-detail-page__navigation" aria-label="Navegación de simulación">
        <Link className="simulation-detail-page__back" to="/app/simulations">
          ← Volver a simulaciones
        </Link>
      </nav>

      <header className="simulation-detail-page__header">
        <div>
          <p className="app__eyebrow">Simulación</p>
          <h1>{configuration.nombre}</h1>
          <p className="app__description">
            Consulta y administra la configuración de esta simulación.
          </p>
        </div>

        <div className="simulation-detail-page__header-actions">
          <span
            className={`simulation-status simulation-status--${configuration.estado.toLowerCase()}`}
          >
            {formatSimulationStatus(configuration.estado)}
          </span>

          {canEdit && !showEditForm ? (
            <button
              className="button button--secondary"
              type="button"
              onClick={() => setShowEditForm(true)}
            >
              Editar configuración
            </button>
          ) : null}
        </div>
      </header>

      {showEditForm && canEdit ? (
        <EditSimulationConfigurationForm
          configuration={configuration}
          onCancel={() => setShowEditForm(false)}
          onUpdated={() => setShowEditForm(false)}
        />
      ) : null}

      <section className="simulation-detail-section">
        <header className="simulation-detail-section__header">
          <div>
            <p className="simulation-results__eyebrow">Información general</p>
            <h2>Datos de la configuración</h2>
          </div>
        </header>

        <dl className="simulation-detail-grid">
          <div>
            <dt>Tipo</dt>
            <dd>{formatSimulationType(configuration.tipo_simulacion)}</dd>
          </div>

          <div>
            <dt>Moneda base</dt>
            <dd>{configuration.moneda_base}</dd>
          </div>

          <div>
            <dt>Capital inicial</dt>
            <dd>{formatCurrency(configuration.capital_inicial, configuration.moneda_base)}</dd>
          </div>

          <div>
            <dt>Estado</dt>
            <dd>{formatSimulationStatus(configuration.estado)}</dd>
          </div>

          <div>
            <dt>Fecha de inicio</dt>
            <dd>{formatDate(configuration.fecha_inicio)}</dd>
          </div>

          <div>
            <dt>Fecha final</dt>
            <dd>{formatDate(configuration.fecha_fin)}</dd>
          </div>

          <div>
            <dt>Creada</dt>
            <dd>{formatDate(configuration.fecha_creacion)}</dd>
          </div>

          <div>
            <dt>Última actualización</dt>
            <dd>{formatDate(configuration.fecha_actualizacion)}</dd>
          </div>
        </dl>

        <div className="simulation-detail-description">
          <span>Descripción</span>
          <p>{configuration.descripcion || 'Sin descripción registrada.'}</p>
        </div>
      </section>

      <section className="simulation-detail-section">
        <header className="simulation-detail-section__header">
          <div>
            <p className="simulation-results__eyebrow">Parámetros</p>
            <h2>Configuración financiera</h2>
          </div>
        </header>

        <dl className="simulation-detail-grid">
          <div>
            <dt>Aportación periódica</dt>
            <dd>{formatCurrency(configuration.aportacion_periodica, configuration.moneda_base)}</dd>
          </div>

          <div>
            <dt>Frecuencia</dt>
            <dd>{formatContributionFrequency(configuration.frecuencia_aportacion)}</dd>
          </div>

          <div>
            <dt>Comisión</dt>
            <dd>{formatPercentage(configuration.comision_porcentaje)}</dd>
          </div>

          <div>
            <dt>Inflación anual</dt>
            <dd>{formatPercentage(configuration.inflacion_anual)}</dd>
          </div>

          <div>
            <dt>Tasa libre de riesgo</dt>
            <dd>{formatPercentage(configuration.tasa_libre_riesgo)}</dd>
          </div>

          <div>
            <dt>Número de escenarios</dt>
            <dd>{configuration.numero_escenarios.toLocaleString('es-MX')}</dd>
          </div>

          <div>
            <dt>Semilla aleatoria</dt>
            <dd>{configuration.semilla_aleatoria ?? 'No configurada'}</dd>
          </div>

          <div>
            <dt>Portafolio relacionado</dt>
            <dd>{configuration.portafolio_id ?? 'Sin portafolio relacionado'}</dd>
          </div>
        </dl>
      </section>

      <SimulationAssetsSection
        configurationId={configuration.id}
        status={configuration.estado}
        currency={configuration.moneda_base}
        canUpdate={canUpdate}
      />

      <SimulationExecutionsSection
        configurationId={configuration.id}
        configurationStatus={configuration.estado}
        canRead={canReadExecutions}
        canExecute={canExecute}
      />

      {!isDraft ? (
        <section className="simulation-detail-section">
          <div className="simulation-detail-notice">
            <strong>
              {configuration.estado === 'LISTA'
                ? 'La configuración está lista.'
                : 'La configuración está archivada.'}
            </strong>
            <span>
              {configuration.estado === 'LISTA'
                ? 'Los parámetros generales ya no pueden modificarse.'
                : 'Una configuración archivada es de solo lectura.'}
            </span>
          </div>
        </section>
      ) : null}

      <ArchiveSimulationConfigurationSection
        configurationId={configuration.id}
        status={configuration.estado}
        canArchive={canArchive}
      />
    </section>
  )
}
