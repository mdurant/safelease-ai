# Arquitectura: Django + FastAPI separados

## Modelo recomendado (procesos separados)

```
                    ┌─────────────────┐
                    │   Cliente       │
                    │   (navegador,   │
                    │   móvil, etc.)  │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   FastAPI        │  │   Django         │  │   (opcional)    │
│   :8001          │  │   :8000         │  │   Cola (Celery) │
│                  │  │                  │  │   más adelante   │
│  API pública     │──│  Admin, API      │  └────────┬────────┘
│  alta concurrencia│  │  interna, ORM   │           │
└────────┬─────────┘  └────────┬────────┘           │
         │                     │                    │
         │   HTTP interno      │                    │
         │   (httpx)            │                    │
         └──────────┬──────────┘                    │
                    │                               │
                    ▼                               ▼
             ┌──────────────────────────────────────────┐
             │            PostgreSQL (:5432)            │
             └──────────────────────────────────────────┘
```

- **Django**: admin, lógica de negocio, ORM, migraciones. Expone API REST interna (o solo admin).
- **FastAPI**: API pública, alta concurrencia, validación con Pydantic. Llama a Django por HTTP cuando necesita datos o acciones que viven en Django.
- **Comunicación**: HTTP interno con `httpx` (cliente asíncrono/síncrono). Más adelante se puede añadir cola (Celery/Redis) para tareas asíncronas.

## Ventajas

| Aspecto | Beneficio |
|--------|-----------|
| **Desacoplamiento** | Cada servicio tiene su stack y ciclo de vida. |
| **Despliegue** | Escalar FastAPI y Django por separado; desplegar uno sin tocar el otro. |
| **Claridad** | Responsabilidades bien definidas (Django = admin/ORM, FastAPI = API pública). |
| **Tecnología** | Puedes cambiar uno sin reescribir el otro. |

---

## Cómo hacerlo

### 1. Variables de entorno (URLs internas)

Cada proceso debe conocer la URL base del otro para las llamadas HTTP internas.

**Desarrollo local** (ambos en la misma máquina):

```env
# URL donde escucha Django (para que FastAPI u otros lo llamen)
DJANGO_INTERNAL_URL=http://127.0.0.1:8000

# URL donde escucha FastAPI (para que Django lo llame si hace falta)
FASTAPI_INTERNAL_URL=http://127.0.0.1:8001
```

**Docker / producción** (misma red interna):

```env
DJANGO_INTERNAL_URL=http://django:8000
FASTAPI_INTERNAL_URL=http://fastapi:8001
```

Usa nombres de servicio de Docker como hostname; no hace falta exponer puertos entre servicios para el tráfico interno.

### 2. Ejecutar ambos procesos

**Terminal 1 – Django:**

```bash
cd backend/django_app
python manage.py runserver 8000
```

**Terminal 2 – FastAPI:**

```bash
cd backend
source ../.venv/bin/activate   # o activar .venv desde la raíz
uvicorn fastapi_app.main:app --reload --port 8001
```

O con Docker Compose (ver sección 4).

### 3. Comunicación HTTP interno (httpx)

- **FastAPI → Django**: desde un endpoint o un servicio de FastAPI, usar `httpx` (async o sync) contra `DJANGO_INTERNAL_URL` (por ejemplo `GET /api/health`, `GET /api/...`).
- **Django → FastAPI**: desde una view o un management command, usar `httpx` contra `FASTAPI_INTERNAL_URL` si necesitas algo que solo expone FastAPI.

En este repo:

- **`backend/shared/`**: configuración común (lectura de `DJANGO_INTERNAL_URL` / `FASTAPI_INTERNAL_URL`) y opcionalmente clientes HTTP reutilizables.
- **FastAPI**: en `main.py` o en routers se inyecta la URL de Django y se usa `httpx` para llamar a Django.
- **Django**: en `settings.py` se lee `FASTAPI_INTERNAL_URL`; donde haga falta llamar a FastAPI se usa `httpx` con esa URL.

### 4. Docker Compose (opcional pero recomendado)

- Un servicio `django` (runserver o gunicorn) en el puerto 8000.
- Un servicio `fastapi` (uvicorn) en el puerto 8001.
- Misma red: `django` y `fastapi` se resuelven por nombre.
- Variables de entorno en compose (o en `.env` de infra) con `DJANGO_INTERNAL_URL=http://django:8000` y `FASTAPI_INTERNAL_URL=http://fastapi:8001`.

Así se replica en local la misma topología que en producción (dos procesos separados comunicados por HTTP interno).

### 5. Más adelante: cola (Celery + Redis)

- Para tareas pesadas o asíncronas (emails, reportes, ML), añadir Redis y Celery.
- Django o FastAPI encolan tareas; workers Celery las procesan. La comunicación “entre servicios” sigue siendo por HTTP para lo síncrono; la cola es para trabajo en background.

---

## Resumen de pasos

1. Definir `DJANGO_INTERNAL_URL` y `FASTAPI_INTERNAL_URL` en `.env` (local y Docker).
2. Levantar Django en un proceso y FastAPI en otro (o con docker-compose).
3. En FastAPI (y en Django si aplica) usar `httpx` contra la URL del otro servicio.
4. Centralizar URLs y clientes HTTP en `backend/shared/`.
5. Opcional: levantar todo con Docker Compose desde `infra/`.

---

## Ejecutar con Docker Compose

Desde el directorio `infra/`:

```bash
cd infra
docker compose up -d db    # solo BD
# o todo:
docker compose up -d       # db + django + fastapi
```

- **Django**: http://localhost:8000 (admin en /admin/, API interna en /api/health).
- **FastAPI**: http://localhost:8001 (health en /health, ejemplo de llamada a Django en /django-status).

En este modo, `DJANGO_INTERNAL_URL` y `FASTAPI_INTERNAL_URL` se configuran en el compose con los nombres de servicio (`http://django:8000`, `http://fastapi:8001`).
