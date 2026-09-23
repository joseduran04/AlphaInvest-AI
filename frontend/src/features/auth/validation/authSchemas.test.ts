import { describe, expect, it } from 'vitest'

import { loginSchema } from './loginSchema'
import { registerSchema } from './registerSchema'

describe('loginSchema', () => {
  it('acepta credenciales válidas', () => {
    const result = loginSchema.safeParse({
      correo: 'usuario@alphainvest.test',
      password: 'password',
    })

    expect(result.success).toBe(true)
  })

  it('rechaza un correo inválido', () => {
    const result = loginSchema.safeParse({
      correo: 'correo-invalido',
      password: 'password',
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe('Ingresa un correo electrónico válido')
    }
  })

  it('rechaza una contraseña vacía', () => {
    const result = loginSchema.safeParse({
      correo: 'usuario@alphainvest.test',
      password: '',
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(result.error.issues[0]?.message).toBe('Ingresa tu contraseña')
    }
  })
})

describe('registerSchema', () => {
  const validRegistration = {
    nombres: 'José',
    apellidos: 'Durán',
    correo: 'usuario@alphainvest.test',
    password: 'Password123!',
    passwordConfirmation: 'Password123!',
    acceptTerms: true,
    acceptPrivacy: true,
  }

  it('acepta un registro válido', () => {
    const result = registerSchema.safeParse(validRegistration)

    expect(result.success).toBe(true)
  })

  it('aplica trim a nombres y apellidos', () => {
    const result = registerSchema.safeParse({
      ...validRegistration,
      nombres: '  José  ',
      apellidos: '  Durán  ',
    })

    expect(result.success).toBe(true)

    if (result.success) {
      expect(result.data.nombres).toBe('José')
      expect(result.data.apellidos).toBe('Durán')
    }
  })

  it('rechaza contraseñas menores a 12 caracteres', () => {
    const result = registerSchema.safeParse({
      ...validRegistration,
      password: 'Corta123!',
      passwordConfirmation: 'Corta123!',
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(result.error.issues.some((issue) => issue.path[0] === 'password')).toBe(true)
    }
  })

  it('rechaza contraseñas que no coinciden', () => {
    const result = registerSchema.safeParse({
      ...validRegistration,
      passwordConfirmation: 'OtraPassword123!',
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(
        result.error.issues.some(
          (issue) =>
            issue.path[0] === 'passwordConfirmation' &&
            issue.message === 'Las contraseñas no coinciden',
        ),
      ).toBe(true)
    }
  })

  it('requiere aceptar los términos y condiciones', () => {
    const result = registerSchema.safeParse({
      ...validRegistration,
      acceptTerms: false,
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(
        result.error.issues.some(
          (issue) =>
            issue.path[0] === 'acceptTerms' &&
            issue.message === 'Debes aceptar los términos y condiciones',
        ),
      ).toBe(true)
    }
  })

  it('requiere aceptar el aviso de privacidad', () => {
    const result = registerSchema.safeParse({
      ...validRegistration,
      acceptPrivacy: false,
    })

    expect(result.success).toBe(false)

    if (!result.success) {
      expect(
        result.error.issues.some(
          (issue) =>
            issue.path[0] === 'acceptPrivacy' &&
            issue.message === 'Debes aceptar el aviso de privacidad',
        ),
      ).toBe(true)
    }
  })
})
