# SafeLease AI

**Motor de Fraude Open Source para procesos de arriendo de propiedades.**

Sistema backend que combina **Django** (admin, lógica de negocio, ORM) y **FastAPI** (API pública de alta concurrencia) para soportar flujos de arriendo con detección de fraude. Los servicios se ejecutan como procesos separados y se comunican por HTTP interno.

---

## Autor y empresa

| | |
|---|---|
| **Autor** | Mauricio Durán Torres |
| **Mail** | mauriciodurant@gmail.com |
| **Empresa** | IntegralTech Solutions SpA |
| **País** | Chile |

---

## Requisitos del sistema (desarrollo local)

Probado en **macOS** (Apple Silicon M3, 24 GB RAM). Equivalente en Intel o Linux debería funcionar sin cambios.

| Requisito | Versión / Nota |
|-----------|-----------------|
| **Python** | 3.12+ (recomendado: [pyenv](https://github.com/pyenv/pyenv) o instalación oficial) |
| **PostgreSQL** | 16 (local o vía Docker) |
| **Docker** (opcional) | Para levantar solo la base de datos o todo el stack |
| **RAM** | 24 GB suficiente; con Docker + Django + FastAPI + PostgreSQL ~2–3 GB en uso |

---

## Dependencias del proyecto

Todas las dependencias están en `requirements.txt`. Resumen por bloque:

| Bloque | Paquetes | Uso |
|--------|----------|-----|
| **Django** | Django, djangorestframework | Backend principal, admin, ORM, API interna |
| **FastAPI** | fastapi, uvicorn, starlette | API pública, servidor ASGI |
| **Base de datos** | psycopg[binary] | Conexión a PostgreSQL |
| **Config** | python-dotenv, pydantic | Variables de entorno, validación |
| **Comunicación interna** | httpx | Llamadas HTTP entre Django y FastAPI |
| **Desarrollo** | ruff, black, mypy, pytest, pytest-django | Linting, formato, tipos, tests |

Instalación:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Primeros pasos (ejecución local en MacBook Pro M3)

### 1. Clonar y entrar al proyecto

```bash
git clone <url-del-repo> safelease-ai
cd safelease-ai
```

### 2. Entorno virtual y dependencias

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Variables de entorno

Copia el ejemplo y ajusta si hace falta (claves, hosts, URLs internas):

```bash
cp .env.example .env
# Opcional: también puedes usar infra/.env (el backend carga ambos)
cp .env.example infra/.env
```

En **desarrollo local** asegura al menos en `.env` o `infra/.env`:

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=1`, `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
- `DJANGO_INTERNAL_URL=http://127.0.0.1:8000`, `FASTAPI_INTERNAL_URL=http://127.0.0.1:8001`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST=127.0.0.1`, `DB_PORT=5432`

### 4. Base de datos PostgreSQL

**Opción A – Docker (recomendado en Mac):**

```bash
cd infra
docker compose up -d db
cd ..
```

**Opción B – PostgreSQL instalado en el sistema:**

Crea usuario y base `safelease` y deja el servicio escuchando en `127.0.0.1:5432`. Usa los mismos valores que en `.env`.

### 5. Migraciones Django

```bash
cd backend/django_app
python manage.py migrate
cd ../..
```

### 6. Levantar los dos servicios (dos terminales)

**Terminal 1 – Django (puerto 8000):**

```bash
cd backend/django_app
source ../../.venv/bin/activate
python manage.py runserver 8000
```

**Terminal 2 – FastAPI (puerto 8001):**

```bash
cd backend
source ../.venv/bin/activate
uvicorn fastapi_app.main:app --reload --port 8001
```

### 7. Comprobar que todo responde

- **Django**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (crear superusuario con `python manage.py createsuperuser` si hace falta)
- **FastAPI**: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) (Swagger)
- **Comunicación FastAPI → Django**: [http://127.0.0.1:8001/django-status](http://127.0.0.1:8001/django-status)

---

## Arquitectura

Django y FastAPI corren como **procesos separados** y se comunican por **HTTP interno** (cliente `httpx`). Detalle de componentes, URLs internas, Docker y posibles extensiones (p. ej. cola):

→ **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

---

## Estructura del repositorio

```
safelease-ai/
├── backend/
│   ├── django_app/          # Django (admin, ORM, API interna)
│   ├── fastapi_app/         # FastAPI (API pública)
│   └── shared/               # Config y clientes HTTP compartidos
├── docs/
│   └── ARCHITECTURE.md       # Diseño y despliegue
├── infra/
│   ├── docker-compose.yml    # db + django + fastapi
│   └── .env                  # Variables para compose y servicios
├── .env.example
├── requirements.txt
└── README.md
```

---

## Ejecutar todo con Docker (opcional)

Desde `infra/` puedes levantar base de datos + Django + FastAPI:

```bash
cd infra
docker compose up -d
```

- Django: http://localhost:8000  
- FastAPI: http://localhost:8001  

Las URLs internas entre servicios se resuelven por nombre de servicio (`django`, `fastapi`). Ver [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Licencia

Por definir (proyecto Open Source).
