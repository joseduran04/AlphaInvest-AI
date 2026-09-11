import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'

import { ApiError } from '@/api/errors'
import { AuthLoadingState } from '@/features/auth/components/AuthLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { loginSchema, type LoginFormValues } from '@/features/auth/validation/loginSchema'

interface LoginLocationState {
  from?: {
    pathname?: string
  }
}

function getLoginErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return 'No fue posible iniciar sesión. Intenta nuevamente.'
  }

  if (error.kind === 'network') {
    return 'No fue posible conectar con el servidor.'
  }

  if (error.kind === 'timeout') {
    return 'El servidor tardó demasiado en responder.'
  }

  if (error.status === 401) {
    return 'Correo o contraseña incorrectos.'
  }

  if (error.status === 403) {
    return error.message
  }

  return error.message
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, status, isAuthenticated } = useAuth()

  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      correo: '',
      password: '',
    },
  })

  if (status === 'checking') {
    return <AuthLoadingState />
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />
  }

  const state = location.state as LoginLocationState | null
  const destination = state?.from?.pathname ?? '/app'

  const onSubmit = async (values: LoginFormValues): Promise<void> => {
    setSubmitError(null)

    try {
      await login(values)
      navigate(destination, { replace: true })
    } catch (error) {
      setSubmitError(getLoginErrorMessage(error))
    }
  }

  return (
    <main>
      <section>
        <p>AlphaInvest AI</p>
        <h1>Iniciar sesión</h1>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div>
            <label htmlFor="correo">Correo electrónico</label>
            <input id="correo" type="email" autoComplete="email" {...register('correo')} />

            {errors.correo ? <p role="alert">{errors.correo.message}</p> : null}
          </div>

          <div>
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register('password')}
            />

            {errors.password ? <p role="alert">{errors.password.message}</p> : null}
          </div>

          {submitError ? <p role="alert">{submitError}</p> : null}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>
        <p>
          ¿No tienes una cuenta? <Link to="/register">Crear cuenta</Link>
        </p>
      </section>
    </main>
  )
}
