import { describe, expect, it, vi } from 'vitest'

import { notifySessionInvalidated, subscribeToSessionInvalidation } from './sessionEvents'

describe('sessionEvents', () => {
  it('notifica al listener suscrito cuando la sesión es invalidada', () => {
    const listener = vi.fn()
    const unsubscribe = subscribeToSessionInvalidation(listener)

    notifySessionInvalidated()

    expect(listener).toHaveBeenCalledTimes(1)

    unsubscribe()
  })

  it('notifica a todos los listeners suscritos', () => {
    const firstListener = vi.fn()
    const secondListener = vi.fn()

    const unsubscribeFirst = subscribeToSessionInvalidation(firstListener)
    const unsubscribeSecond = subscribeToSessionInvalidation(secondListener)

    notifySessionInvalidated()

    expect(firstListener).toHaveBeenCalledTimes(1)
    expect(secondListener).toHaveBeenCalledTimes(1)

    unsubscribeFirst()
    unsubscribeSecond()
  })

  it('deja de notificar al listener después de cancelar la suscripción', () => {
    const listener = vi.fn()
    const unsubscribe = subscribeToSessionInvalidation(listener)

    unsubscribe()
    notifySessionInvalidated()

    expect(listener).not.toHaveBeenCalled()
  })
})
