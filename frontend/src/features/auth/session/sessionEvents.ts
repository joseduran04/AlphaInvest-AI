type SessionInvalidatedListener = () => void

const sessionInvalidatedListeners = new Set<SessionInvalidatedListener>()

export function subscribeToSessionInvalidation(listener: SessionInvalidatedListener): () => void {
  sessionInvalidatedListeners.add(listener)

  return () => {
    sessionInvalidatedListeners.delete(listener)
  }
}

export function notifySessionInvalidated(): void {
  sessionInvalidatedListeners.forEach((listener) => {
    listener()
  })
}
