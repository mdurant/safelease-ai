# Ambiente local — Paso a paso (Backend + Frontend)

Guía para levantar **Django**, **FastAPI** y **React** en tu máquina. Probado en macOS (Apple Silicon).

---

## Requisitos previos

| Herramienta | Versión | Comprobación |
|-------------|---------|----------------|
| **Python** | 3.12+ | `python3 --version` |
| **Node.js** | 18+ (LTS) | `node --version` |
| **npm** | 9+ | `npm --version` |
| **PostgreSQL** | 14+ (o Docker) | `psql --version` o `docker --version` |

---

## Paso 1: Clonar e instalar dependencias Python

Desde la raíz del proyecto:

```bash
cd /Users/mdurant/proyectos/safelease-ai

# Entorno virtual (si aún no lo tienes)
python3 -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate

# Dependencias backend
pip install -r requirements.txt
```

---

## Paso 2: Variables de entorno

El proyecto carga variables desde **`.env`** en la raíz y/o desde **`infra/.env`** (si usas solo uno, basta con **`infra/.env`**).

```bash
# Copiar ejemplo (el archivo de config está en infra/)
cp .env.example infra/.env
```

Abre **`infra/.env`** y deja al menos esto (desarrollo local):

```env
DJANGO_SECRET_KEY=dev-secret-change-in-prod
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DJANGO_INTERNAL_URL=http://127.0.0.1:8000
FASTAPI_INTERNAL_URL=http://127.0.0.1:8001

DB_NAME=safelease
DB_USER=safelease
DB_PASSWORD=safelease
DB_HOST=127.0.0.1
DB_PORT=5432
```

---

## Paso 3: Base de datos PostgreSQL

**Opción A — Docker (recomendado):**

```bash
cd infra
docker compose up -d db
cd ..
```

Comprueba que el contenedor está arriba: `docker ps` (debe verse el servicio `db`).

**Opción B — PostgreSQL instalado en el sistema:**

Crea la base y el usuario (ejemplo):

```bash
createuser -s safelease
createdb -O safelease safelease
# Ajusta en .env si usas otro usuario/contraseña
```

---

## Paso 4: Migraciones y datos iniciales (Django)

Desde la raíz del proyecto, con el venv activado:

```bash
cd backend/django_app

# Crear migraciones de la app core (si no existen)
python manage.py makemigrations core

# Aplicar todas las migraciones
python manage.py migrate

# Seed: roles + usuario demo (email: demo@safelease.local, password: password)
python manage.py seed_auth

cd ../..
```

Si aparece algún error de migraciones, revisa que `DB_*` en `infra/.env` (o `.env` en la raíz) coincida con tu PostgreSQL.

**Si sale `InconsistentMigrationHistory` (admin applied before core):** la base se migró antes de usar el usuario custom. En desarrollo, la solución más simple es **resetear la base** y volver a migrar:

```bash
# Desde la raíz (PostgreSQL local; ajusta usuario si no es safelease)
dropdb safelease
createdb -O safelease safelease

# Con Docker (DROP y CREATE por separado; no pueden ir en la misma transacción):
cd infra
docker compose exec db psql -U safelease -d postgres -c "DROP DATABASE IF EXISTS safelease;"
docker compose exec db psql -U safelease -d postgres -c "CREATE DATABASE safelease OWNER safelease;"
cd ..

# Luego de nuevo
cd backend/django_app
python manage.py migrate
python manage.py seed_auth
```

---

## Paso 5: Levantar el backend (dos terminales)

**Terminal 1 — Django (puerto 8000):**

```bash
cd /Users/mdurant/proyectos/safelease-ai
source .venv/bin/activate
cd backend/django_app
python manage.py runserver 8000
```

Deja esta terminal abierta. Deberías ver algo como: `Starting development server at http://127.0.0.1:8000/`.

**Terminal 2 — FastAPI (puerto 8001):**

```bash
cd /Users/mdurant/proyectos/safelease-ai
source .venv/bin/activate
cd backend
uvicorn fastapi_app.main:app --reload --port 8001
```

Deja esta terminal abierta. Deberías ver: `Uvicorn running on http://127.0.0.1:8001`.

---

## Paso 6: Levantar el frontend (tercera terminal)

```bash
cd /Users/mdurant/proyectos/safelease-ai/frontend

# Primera vez: instalar dependencias
npm install

# Servidor de desarrollo (Vite)
npm run dev
```

Deberías ver algo como: `Local: http://localhost:5173/`. Deja esta terminal abierta.

---

## Paso 7: Comprobar que todo funciona

| Qué | URL | Qué esperar |
|-----|-----|-------------|
| **Django** | http://127.0.0.1:8000/api/health | `{"status":"ok","service":"django"}` |
| **Django Admin** | http://127.0.0.1:8000/admin/ | Página de login (crear superusuario si quieres: `python manage.py createsuperuser`) |
| **FastAPI** | http://127.0.0.1:8001/health | `{"status":"ok","service":"fastapi"}` |
| **FastAPI → Django** | http://127.0.0.1:8001/django-status | Respuesta con estado de Django |
| **API Auth (vía proxy)** | http://127.0.0.1:8001/api/auth/me/ | 401 sin token (normal) |
| **Frontend** | http://localhost:5173 | App React (login, registro, etc.) |

**Login de prueba en el frontend:**

- URL: http://localhost:5173/ingresar  
- Email: **demo@safelease.local**  
- Contraseña: **password**

---

## Resumen de comandos (copiar/pegar)

Asumiendo que ya tienes `.venv`, `.env` y PostgreSQL (o Docker `db`) listos:

```bash
# 1) Migraciones y seed (una vez)
cd /Users/mdurant/proyectos/safelease-ai && source .venv/bin/activate
cd backend/django_app && python manage.py migrate && python manage.py seed_auth && cd ../..

# 2) Terminal 1 — Django
cd /Users/mdurant/proyectos/safelease-ai && source .venv/bin/activate && cd backend/django_app && python manage.py runserver 8000

# 3) Terminal 2 — FastAPI
cd /Users/mdurant/proyectos/safelease-ai && source .venv/bin/activate && cd backend && uvicorn fastapi_app.main:app --reload --port 8001

# 4) Terminal 3 — Frontend
cd /Users/mdurant/proyectos/safelease-ai/frontend && npm install && npm run dev
```

---

## Problemas frecuentes

- **"InconsistentMigrationHistory: Migration admin.0001_initial is applied before its dependency core.0001_initial":** La base se migró cuando el proyecto usaba el User por defecto; ahora se usa `core.Usuario`. En **desarrollo** resetea la base (ver recuadro encima de Paso 5): `dropdb safelease` y `createdb -O safelease safelease`, luego `migrate` y `seed_auth`.
- **"could not connect to server" (PostgreSQL):** Revisa que PostgreSQL esté corriendo y que `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` en `infra/.env` (o `.env`) sean correctos. Si usas Docker: `docker compose -f infra/docker-compose.yml up -d db`.
- **"ModuleNotFoundError: No module named 'core'":** Ejecuta los comandos desde `backend/django_app` (donde está `manage.py`) con el venv activado desde la raíz.
- **Frontend no conecta al backend:** El proxy de Vite envía `/api` a `http://127.0.0.1:8001`. Comprueba que FastAPI esté en 8001 y Django en 8000.
- **CORS:** Si llamas al frontend desde otra URL, añádela en `CORS_ALLOWED_ORIGINS` (Django y FastAPI) o en `.env` como `CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`.
