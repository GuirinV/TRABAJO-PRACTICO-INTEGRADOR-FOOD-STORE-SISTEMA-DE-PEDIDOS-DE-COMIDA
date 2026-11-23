# Food Store

Sistema web de pedidos de comida desarrollado para el TPI de Programación 4. Incluye API REST con FastAPI y SQLModel, frontend React + TypeScript, autenticación JWT mediante cookie HttpOnly y roles `user` y `admin`.

## Requisitos

- Python 3.11–3.13.
- Node.js 20 o superior y npm.
- SQLite para desarrollo local o PostgreSQL 15 o superior.

## Estructura

```text
backend/
  app/
    api/                 # Routers y dependencias HTTP
    core/                # Configuración, seguridad, DB y Unit of Work
    modules/             # usuarios/, catalogo/ y pedidos/ por dominio
frontend/
  src/features/          # auth, catalog, cart, orders y admin
  src/api/               # cliente Axios
  src/stores/            # carrito Zustand
```

El backend separa Router → Service → Unit of Work → Repository → Model/Schema. El commit de las operaciones ocurre en `UnitOfWork.__exit__`; los servicios no confirman directamente la sesión.

## Configuración y ejecución local

### Backend

Desde la raíz del proyecto, crear el entorno virtual e instalar las dependencias:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

La configuración inicial utiliza SQLite y crea `backend/food_store.db` al iniciar la API. Aplicar el seed:

```powershell
python -m app.seed
```

Iniciar la API:

```powershell
uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000/api/v1>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

### Frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
npm.cmd install
Copy-Item .env.example .env.local
npm.cmd run dev
```

Abrir la dirección que muestre Vite, normalmente <http://localhost:5173>. Para generar el build de producción:

```powershell
npm.cmd run build
```

## Variables de entorno

Las variables del backend se leen desde `backend/.env` (copiado desde el `.env.example` de la raíz):

| Variable | Descripción | Desarrollo |
| --- | --- | --- |
| `DATABASE_URL` | URL SQLAlchemy. SQLite local o PostgreSQL | `sqlite:///./food_store.db` |
| `SECRET_KEY` | Clave para firmar los JWT | Cambiar por una clave aleatoria |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración de la cookie de sesión | `60` |
| `CORS_ORIGINS` | Orígenes permitidos separados por coma | `http://localhost:5173` |
| `APP_NAME` | Título de la API | `Food Store API` |
| `API_V1_PREFIX` | Prefijo de API | `/api/v1` |
| `SEED_ADMIN_NAME` | Nombre del admin seed | `Food Store Admin` |
| `SEED_ADMIN_EMAIL` | Email del admin seed | `admin@foodstore.local` |
| `SEED_ADMIN_PASSWORD` | Contraseña inicial del admin | `Admin1234!` |
| `VITE_API_URL` | URL base que usa Axios | `http://127.0.0.1:8000/api/v1` |

Para PostgreSQL, configurar por ejemplo `DATABASE_URL=postgresql+psycopg2://usuario:clave@localhost:5432/food_store`. Crear previamente la base de datos. En despliegues HTTPS, configurar la cookie segura y una clave secreta fuerte.

## Usuario del seed

El seed idempotente crea o completa las categorías y productos iniciales sin duplicarlos. También crea el admin si no existe.

- Email: `admin@foodstore.local`
- Contraseña inicial: `Admin1234!`

Se pueden cambiar antes de ejecutar el seed mediante `SEED_ADMIN_EMAIL`, `SEED_ADMIN_PASSWORD` y `SEED_ADMIN_NAME`. Cambiar la contraseña de ejemplo antes de cualquier despliegue.

## Flujo principal para probar

1. Registrarse desde la interfaz y luego iniciar sesión.
2. Agregar productos disponibles al carrito y confirmar el pedido.
3. Consultar “Mis pedidos” y cancelar uno pendiente para verificar la restitución del stock.
4. Ingresar con el usuario seed para gestionar el catálogo, usuarios y estados de pedidos en `/admin`.

El frontend no accede al token JWT: el navegador envía la cookie `access_token` HttpOnly usando Axios con `withCredentials`.

## Repositorio

URL del repositorio: <https://github.com/GuirinV/TRABAJO-PRACTICO-INTEGRADOR-FOOD-STORE-SISTEMA-DE-PEDIDOS-DE-COMIDA.git>
