import { z } from 'zod'

export const registerSchema = z
  .object({
    nombres: z
      .string()
      .trim()
      .min(1, 'Ingresa tu nombre')
      .max(100, 'El nombre no puede superar 100 caracteres'),
    apellidos: z
      .string()
      .trim()
      .min(1, 'Ingresa tus apellidos')
      .max(100, 'Los apellidos no pueden superar 100 caracteres'),
    correo: z.email('Ingresa un correo electrónico válido'),
    password: z
      .string()
      .min(12, 'La contraseña debe tener al menos 12 caracteres')
      .max(128, 'La contraseña no puede superar 128 caracteres'),
    passwordConfirmation: z.string().min(1, 'Confirma tu contraseña'),
    acceptTerms: z.boolean().refine((value) => value, {
      message: 'Debes aceptar los términos y condiciones',
    }),
    acceptPrivacy: z.boolean().refine((value) => value, {
      message: 'Debes aceptar el aviso de privacidad',
    }),
  })
  .refine((data) => data.password === data.passwordConfirmation, {
    message: 'Las contraseñas no coinciden',
    path: ['passwordConfirmation'],
  })

export type RegisterFormValues = z.infer<typeof registerSchema>
