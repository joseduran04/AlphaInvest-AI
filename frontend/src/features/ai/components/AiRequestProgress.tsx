import type { AnalysisRequestStatus } from '@/api/types'

interface AiRequestProgressProps {
  status: AnalysisRequestStatus
  progressPercentage: string
  pendingTitle?: string
  pendingDescription?: string
  executingTitle: string
  executingDescription: string
}

function parseProgress(value: string): number {
  const progress = Number(value)

  if (!Number.isFinite(progress)) {
    return 0
  }

  return Math.min(100, Math.max(0, progress))
}

function formatProgress(value: number): string {
  return new Intl.NumberFormat('es-MX', {
    maximumFractionDigits: 2,
  }).format(value)
}

export function AiRequestProgress({
  status,
  progressPercentage,
  pendingTitle = 'Esperando procesamiento',
  pendingDescription = 'La solicitud fue registrada y está esperando ser procesada.',
  executingTitle,
  executingDescription,
}: AiRequestProgressProps) {
  const progress = parseProgress(progressPercentage)
  const isPendingWithoutProgress = status === 'PENDIENTE' && progress === 0

  return (
    <div className="ai-request__processing">
      <strong>{isPendingWithoutProgress ? pendingTitle : executingTitle}</strong>

      <p>{isPendingWithoutProgress ? pendingDescription : executingDescription}</p>

      {!isPendingWithoutProgress ? (
        <>
          <progress max={100} value={progress} />
          <span>{formatProgress(progress)} %</span>
        </>
      ) : (
        <span className="ai-request__waiting">En espera</span>
      )}
    </div>
  )
}
