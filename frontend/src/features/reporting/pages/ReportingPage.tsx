import { Link } from 'react-router'

import '@/styles/reporting.css'

const reportSections = [
  {
    title: 'Activos',
    description:
      'Consulta información consolidada de activos, mercados, precios, fuentes y variaciones registradas.',
    to: '/app/reports/assets',
  },
  {
    title: 'Portafolios',
    description:
      'Analiza tus portafolios, posiciones, capital invertido, valor estimado y rendimiento.',
    to: '/app/reports/portfolios',
  },
  {
    title: 'Simulaciones',
    description:
      'Revisa ejecuciones, resultados y métricas financieras obtenidas en tus simulaciones.',
    to: '/app/reports/simulations',
  },
  {
    title: 'Recomendaciones',
    description: 'Consulta las recomendaciones generadas, su contexto, nivel de riesgo y estado.',
    to: '/app/reports/recommendations',
  },
] as const

export function ReportingPage() {
  return (
    <section className="reporting-page">
      <header className="reporting-page__header">
        <div>
          <p className="app__eyebrow">Reportes</p>
          <h1>Centro de reportes</h1>
          <p className="app__description">
            Consulta y exporta la información consolidada generada por AlphaInvest AI.
          </p>
        </div>
      </header>

      <section className="reporting-overview">
        <header className="reporting-overview__header">
          <div>
            <p className="reporting-overview__eyebrow">Información consolidada</p>
            <h2>Reportes disponibles</h2>
            <p>Selecciona el área de información que deseas consultar.</p>
          </div>
        </header>

        <div className="reporting-cards">
          {reportSections.map((report) => (
            <article className="reporting-card" key={report.to}>
              <div className="reporting-card__content">
                <h3>{report.title}</h3>
                <p>{report.description}</p>
              </div>

              <Link className="reporting-card__link" to={report.to}>
                Consultar reporte
              </Link>
            </article>
          ))}
        </div>
      </section>
    </section>
  )
}
