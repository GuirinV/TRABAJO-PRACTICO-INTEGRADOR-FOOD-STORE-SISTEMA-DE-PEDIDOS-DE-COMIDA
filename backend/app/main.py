from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_usuarios import router as admin_usuarios_router
from app.api.auth import router as auth_router
from app.api.catalogo import categorias_router, productos_router
from app.api.pedidos import router as pedidos_router
from app.core.config import settings
from app.core.database import create_db_and_tables


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_usuarios_router, prefix=settings.api_v1_prefix)
app.include_router(categorias_router, prefix=settings.api_v1_prefix)
app.include_router(productos_router, prefix=settings.api_v1_prefix)
app.include_router(pedidos_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()


@app.get("/", tags=["Sistema"])
def root() -> dict[str, str]:
    return {"message": "Food Store API"}


@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"status": "ok"}
