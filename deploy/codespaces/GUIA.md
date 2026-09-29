# Publicar AlphaInvest AI en GitHub Codespaces

Un Codespace es una máquina virtual en la nube de GitHub/Microsoft
(2 núcleos, 8 GB de RAM). La cuenta gratuita incluye unas **60 horas al mes**
con esa máquina, sin tarjeta. La app corre ahí con una dirección pública HTTPS;
PostgreSQL sigue en Supabase y MongoDB en Atlas.

```
Navegador ──HTTPS──▶ Codespace (puerto 7860 público, nginx)
                        ├── /        → frontend
                        └── /api/    → API FastAPI
                     worker en el mismo contenedor
                        ├──▶ Supabase (PostgreSQL)
                        ├──▶ MongoDB Atlas
                        └──▶ Yahoo Finance / Alpha Vantage
```

## Una sola vez

### 1. MongoDB Atlas

**Network Access → Add IP Address → Allow access from anywhere (`0.0.0.0/0`)**.
El Codespace cambia de IP; tu usuario y contraseña de Atlas siguen protegiendo el acceso.

### 2. Subir los modelos a Hugging Face (en tu compu, en la RAÍZ, Git Bash)

Los modelos pesan ~440 MB y no están en Git. Se guardan gratis en un repositorio
de modelos de Hugging Face (esto sí es gratis; lo que cobra es ejecutar Spaces).

```bash
pip install huggingface_hub
hf auth login
python deploy/codespaces/subir_modelos.py --repo joseduran04/alphainvest-artifacts
```

`hf auth login` pide un token de https://huggingface.co/settings/tokens (tipo **Write**).

### 3. Subir el código a GitHub (en la RAÍZ)

```bash
git push
```

### 4. Aumentar el tiempo antes de que se apague

En GitHub: **Settings → Codespaces → Default idle timeout → 240 minutos**.

## Cada vez que quieras la app en línea

### 5. Abrir el Codespace

En https://github.com/joseduran04/AlphaInvest-AI → botón verde **Code** →
pestaña **Codespaces** → elige la rama `feature/post-v1.1.0-diagnostico` →
**Create codespace** (la primera vez) o abre el que ya existe.

### 6. Poner tu `.env` (solo la primera vez)

En el explorador de archivos del Codespace, arrastra tu `backend/.env` desde tu
compu a la carpeta `backend/`. Git lo ignora, así que no se sube al repositorio.

### 7. Levantar la app (terminal del Codespace)

```bash
bash deploy/codespaces/levantar.sh
```

La primera vez tarda 10-15 minutos (descarga modelos e instala PyTorch).
Al final imprime la dirección, del estilo:

```
https://<nombre-del-codespace>-7860.app.github.dev
```

La primera vez que alguien la abre, GitHub puede mostrar un aviso de
"puerto de desarrollo": se da **Continue**.

## Qué saber

- **No está encendida 24/7.** Se detiene tras el tiempo de inactividad o si la
  detienes tú. Para la exposición, ábrela 10 minutos antes y corre el paso 7
  (las veces siguientes tarda 1-2 minutos).
- **El worker solo trabaja mientras está encendida.** Antes de presentar, usa
  "Sincronizar todos los precios" en la app.
- **Horas gratis:** revisa tu consumo en GitHub → Settings → Billing. Detén el
  Codespace cuando no lo uses (**Codespaces → ⋯ → Stop codespace**).
- Logs: `docker logs -f alphainvest`. Detener la app: `docker stop alphainvest`.
