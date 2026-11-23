from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response

from app.api.dependencies import require_admin
from app.modules.catalogo.schemas import (
    CategoriaActualizar,
    CategoriaCrear,
    CategoriaPublica,
    ListaCategorias,
    ListaProductos,
    ProductoActualizar,
    ProductoCrear,
    ProductoEstadoActualizar,
    ProductoPublico,
)
from app.modules.catalogo.service import CatalogoService
from app.modules.usuarios.schemas import UsuarioPublico

categorias_router = APIRouter(prefix="/categorias", tags=["Categorías"])
productos_router = APIRouter(prefix="/productos", tags=["Productos"])


def get_catalogo_service() -> CatalogoService:
    return CatalogoService()


@categorias_router.get("", response_model=ListaCategorias)
def listar_categorias(
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> ListaCategorias:
    return service.listar_categorias()


@categorias_router.get("/{categoria_id}", response_model=CategoriaPublica)
def obtener_categoria(
    categoria_id: int,
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> CategoriaPublica:
    return service.obtener_categoria(categoria_id)


@categorias_router.post("", response_model=CategoriaPublica, status_code=201)
def crear_categoria(
    datos: CategoriaCrear,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> CategoriaPublica:
    return service.crear_categoria(datos)


@categorias_router.put("/{categoria_id}", response_model=CategoriaPublica)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaActualizar,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> CategoriaPublica:
    return service.actualizar_categoria(categoria_id, datos)


@categorias_router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> Response:
    service.eliminar_categoria(categoria_id)
    return Response(status_code=204)


@productos_router.get("", response_model=ListaProductos)
def listar_productos(
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    categoria_id: int | None = Query(default=None, gt=0),
    disponible: bool | None = None,
) -> ListaProductos:
    return service.listar_productos(skip, limit, search, categoria_id, disponible)


@productos_router.get("/{producto_id}", response_model=ProductoPublico)
def obtener_producto(
    producto_id: int,
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> ProductoPublico:
    return service.obtener_producto(producto_id)


@productos_router.post("", response_model=ProductoPublico, status_code=201)
def crear_producto(
    datos: ProductoCrear,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> ProductoPublico:
    return service.crear_producto(datos)


@productos_router.put("/{producto_id}", response_model=ProductoPublico)
def actualizar_producto(
    producto_id: int,
    datos: ProductoActualizar,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> ProductoPublico:
    return service.actualizar_producto(producto_id, datos)


@productos_router.patch("/{producto_id}/estado", response_model=ProductoPublico)
def actualizar_estado_producto(
    producto_id: int,
    datos: ProductoEstadoActualizar,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> ProductoPublico:
    return service.actualizar_estado_producto(producto_id, datos)


@productos_router.delete("/{producto_id}", status_code=204)
def eliminar_producto(
    producto_id: int,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[CatalogoService, Depends(get_catalogo_service)],
) -> Response:
    service.eliminar_producto(producto_id)
    return Response(status_code=204)
