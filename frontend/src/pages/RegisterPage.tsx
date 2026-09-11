import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, Navigate, useNavigate } from 'react-router'

import { ApiError } from '@/api/errors'
import type { RegisterRequest } from '@/api/types'
import { registerRequest } from '@/features/auth/api/authApi'
import { AuthLoadingState } from '@/features/auth/components/AuthLoadingState'
import { useAuth } from '@/features/auth/hooks/useAuth'
import { registerSchema, type RegisterFormValues } from '@/features/auth/validation/registerSchema'

const TERMS_VERSION = '1.0'
const PRIVACY_VERSION = '1.0'

function getRegisterErrorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return 'No fue posible completar el registro. Intenta nuevamente.'
  }

  if (error.kind === 'network') {
    return 'No fue posible conectar con el servidor.'
  }

  if (error.kind === 'timeout') {
    return 'El servidor tardó demasiado en responder.'
  }

  if (error.status === 409) {
    return 'Ya existe una cuenta registrada con ese correo electrónico.'
  }

  if (error.status === 422) {
    return 'Revisa los datos ingresados e intenta nuevamente.'
  }

  return error.message
}

export function RegisterPage() {
  const navigate = useNavigate()
  const { status, isAuthenticated } = useAuth()

  const [submitError, setSubmitError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      nombres: '',
      apellidos: '',
      correo: '',
      password: '',
      passwordConfirmation: '',
      acceptTerms: false,
      acceptPrivacy: false,
    },
  })

  if (status === 'checking') {
    return <AuthLoadingState />
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />
  }

  const onSubmit = async (values: RegisterFormValues): Promise<void> => {
    setSubmitError(null)

    const payload: RegisterRequest = {
      nombres: values.nombres,
      apellidos: values.apellidos,
      correo: values.correo,
      password: values.password,
      version_terminos: TERMS_VERSION,
      version_privacidad: PRIVACY_VERSION,
    }

    try {
      await registerRequest(payload)

      navigate('/login', {
        replace: true,
        state: {
          registrationSuccess: true,
        },
      })
    } catch (error) {
      setSubmitError(getRegisterErrorMessage(error))
    }
  }

  return (
    <main>
      <section>
        <p>AlphaInvest AI</p>
        <h1>Crear cuenta</h1>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div>
            <label htmlFor="nombres">Nombre</label>
            <input id="nombres" type="text" autoComplete="given-name" {...register('nombres')} />

            {errors.nombres ? <p role="alert">{errors.nombres.message}</p> : null}
          </div>

          <div>
            <label htmlFor="apellidos">Apellidos</label>
            <input
              id="apellidos"
              type="text"
              autoComplete="family-name"
              {...register('apellidos')}
            />

            {errors.apellidos ? <p role="alert">{errors.apellidos.message}</p> : null}
          </div>

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
              autoComplete="new-password"
              {...register('password')}
            />

            {errors.password ? <p role="alert">{errors.password.message}</p> : null}
          </div>

          <div>
            <label htmlFor="passwordConfirmation">Confirmar contraseña</label>
            <input
              id="passwordConfirmation"
              type="password"
              autoComplete="new-password"
              {...register('passwordConfirmation')}
            />

            {errors.passwordConfirmation ? (
              <p role="alert">{errors.passwordConfirmation.message}</p>
            ) : null}
          </div>

          <div>
            <label>
              <input type="checkbox" {...register('acceptTerms')} />
              Acepto los términos y condiciones
            </label>

            {errors.acceptTerms ? <p role="alert">{errors.acceptTerms.message}</p> : null}
          </div>

          <div>
            <label>
              <input type="checkbox" {...register('acceptPrivacy')} />
              Acepto el aviso de privacidad
            </label>

            {errors.acceptPrivacy ? <p role="alert">{errors.acceptPrivacy.message}</p> : null}
          </div>

          {submitError ? <p role="alert">{submitError}</p> : null}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <p>
          ¿Ya tienes una cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </section>
    </main>
  )
}
