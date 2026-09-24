import { useEffect, useRef, useState } from 'react'

/** Ancho observado de un contenedor (con valor inicial para pruebas/SSR). */
export function useElementWidth<T extends HTMLElement>(fallback = 640) {
  const ref = useRef<T>(null)
  const [width, setWidth] = useState(fallback)

  useEffect(() => {
    const element = ref.current

    if (!element || typeof ResizeObserver === 'undefined') {
      return
    }

    const observer = new ResizeObserver((entries) => {
      const nextWidth = entries[0]?.contentRect.width

      if (nextWidth && nextWidth > 0) {
        setWidth(nextWidth)
      }
    })

    observer.observe(element)

    return () => observer.disconnect()
  }, [])

  return { ref, width }
}
