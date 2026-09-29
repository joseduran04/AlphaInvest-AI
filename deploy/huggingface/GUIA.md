# Publicar AlphaInvest AI en Hugging Face Spaces

La app completa (frontend, API y worker) corre en un Space gratuito
(2 vCPU, 16 GB de RAM). PostgreSQL sigue en Supabase y MongoDB en Atlas.

```
Navegador ──HTTPS──▶ Space de Hugging Face (nginx :7860)
                        ├── /        → frontend (React compilado)
                        └── /api/    → API FastAPI (127.0.0.1:8000)
                     worker (tareas programadas) en el mismo contenedor
                        │
                        ├──▶ Supabase (PostgreSQL, puerto 5432, TLS)
                        ├──▶ MongoDB Atlas (noticias)
                        └──▶ Yahoo Finance / Alpha Vantage
```

## 0. Antes de empezar

- `backend/.env` debe apuntar a **MongoDB Atlas** (`APP_MONGODB_URI=mongodb+srv://...`).
- En Atlas → **Network Access**, agrega `0.0.0.0/0` ("Allow access from anywhere").
  Hugging Face no tiene IP fija; tu usuario y contraseña de Atlas siguen protegiendo el acceso.

## 1. Cuenta y token (una sola vez)

1. Crea tu cuenta en <https://huggingface.co/join>.
2. Ve a **Settings → Access Tokens → Create new token**, tipo **Write**. Cópialo.

## 2. Instalar la herramienta y entrar (en la RAÍZ del proyecto, Git Bash)

```bash
pip install huggingface_hub
hf auth login
```

Pega el token cuando lo pida. No lo pegues en el chat ni en el repo.

## 3. Revisar qué se va a subir (en la RAÍZ)

Cambia `TU_USUARIO` por tu usuario de Hugging Face:

```bash
python deploy/huggingface/publish_space.py --space TU_USUARIO/alphainvest --dry-run
```

Muestra la URL pública, cuántos archivos se suben y los **nombres** de los Secrets.
No muestra valores ni cambia nada.

## 4. Publicar (en la RAÍZ)

```bash
python deploy/huggingface/publish_space.py --space TU_USUARIO/alphainvest
```

El script:

1. Crea el Space (Docker, hardware gratuito).
2. Copia las variables `APP_*` de `backend/.env` como **Secrets**, con
   `APP_ENV=production`, `APP_DEBUG=false` y CORS limitado a la URL del Space.
3. Crea la variable `VITE_API_BASE_URL` con la URL del Space.
4. Sube backend, modelos (~440 MB) y frontend en un solo commit.

## 5. Esperar la construcción

Abre `https://huggingface.co/spaces/TU_USUARIO/alphainvest`. La pestaña **Logs**
muestra el avance; la primera vez tarda de 10 a 20 minutos (instala PyTorch).
Cuando diga **Running**, abre la URL directa:

```
https://TU_USUARIO-alphainvest.hf.space
```

Usa esa URL directa (no la vista dentro de huggingface.co) para iniciar sesión.

## Actualizar después de un cambio (en la RAÍZ)

```bash
python deploy/huggingface/publish_space.py --space TU_USUARIO/alphainvest --skip-secrets
```

Si cambiaste algo en `backend/.env`, corre el comando sin `--skip-secrets`.

## Qué saber

- **Se duerme** si nadie la abre en 48 horas. Al entrar despierta sola (1–2 minutos).
  Mientras duerme, el worker no ejecuta tareas. Ábrela un rato antes de presentar.
- Si un proceso (API, worker o nginx) falla, el contenedor se reinicia solo.
  El error queda en la pestaña **Logs** del Space.
- El Space es **público** para que el comité lo abra sin cuenta. Los Secrets no se ven.
