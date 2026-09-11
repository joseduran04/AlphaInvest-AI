import { z } from 'zod'

export const loginSchema = z.object({
  correo: z.email('Ingresa un correo electrónico válido'),
  password: z.string().min(1, 'Ingresa tu contraseña'),
})

export type LoginFormValues = z.infer<typeof loginSchema>
