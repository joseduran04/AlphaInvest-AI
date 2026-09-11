import { PageState } from '@/components/PageState'

interface PageLoadingStateProps {
  message?: string
}

export function PageLoadingState({ message = 'Cargando información...' }: PageLoadingStateProps) {
  return <PageState title={message} description="Espera un momento." />
}
