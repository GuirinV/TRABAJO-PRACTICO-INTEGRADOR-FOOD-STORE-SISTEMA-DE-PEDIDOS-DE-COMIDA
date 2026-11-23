from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.uow import UnitOfWork
from app.modules.catalogo.models import Categoria, Producto
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


class CatalogoService:
    def __init__(self, uow_factory=UnitOfWork) -> None:
        self.uow_factory = uow_factory

    def listar_categorias(self) -> ListaCategorias:
        with self.uow_factory() as uow:
            total = uow.categorias.count()
            items = [CategoriaPublica.model_validate(c) for c in uow.categorias.list()]
            return ListaCategorias(total=total, items=items)

    def obtener_categoria(self, categoria_id: int) -> CategoriaPublica:
        with self.uow_factory() as uow:
            categoria = uow.categorias.get(categoria_id, activos_solo=True)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoría inexistente")
            return CategoriaPublica.model_validate(categoria)

    def crear_categoria(self, datos: CategoriaCrear) -> CategoriaPublica:
        with self.uow_factory() as uow:
            try:
                categoria = uow.categorias.add(Categoria(**datos.model_dump()))
            except IntegrityError as error:
                raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre") from error
            return CategoriaPublica.model_validate(categoria)

    def actualizar_categoria(self, categoria_id: int, datos: CategoriaActualizar) -> CategoriaPublica:
        with self.uow_factory() as uow:
            categoria = uow.categorias.get(categoria_id, activos_solo=True)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoría inexistente")
            for campo, valor in datos.model_dump(exclude_unset=True).items():
                setattr(categoria, campo, valor)
            uow.session.add(categoria)
            try:
                uow.session.flush()
            except IntegrityError as error:
                raise HTTPException(status_code=409, detail="Ya existe una categoría con ese nombre") from error
            return CategoriaPublica.model_validate(categoria)

    def eliminar_categoria(self, categoria_id: int) -> None:
        with self.uow_factory() as uow:
            categoria = uow.categorias.get(categoria_id, activos_solo=True)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoría inexistente")
            categoria.activo = False
            uow.session.add(categoria)

    def listar_productos(
        self,
        skip: int,
        limit: int,
        search: str | None,
        categoria_id: int | None,
        disponible: bool | None,
        admin: bool = False,
    ) -> ListaProductos:
        with self.uow_factory() as uow:
            total = uow.productos.count(search, categoria_id, disponible, activos_solo=not admin)
            productos = uow.productos.list(
                skip, limit, search, categoria_id, disponible, activos_solo=not admin
            )
            return ListaProductos(
                total=total,
                items=[ProductoPublico.model_validate(p) for p in productos],
            )

    def obtener_producto(self, producto_id: int) -> ProductoPublico:
        with self.uow_factory() as uow:
            producto = uow.productos.get(producto_id, activos_solo=True)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto inexistente")
            return ProductoPublico.model_validate(producto)

    def crear_producto(self, datos: ProductoCrear) -> ProductoPublico:
        with self.uow_factory() as uow:
            categoria = uow.categorias.get(datos.categoria_id, activos_solo=True)
            if categoria is None:
                raise HTTPException(status_code=404, detail="Categoría inexistente")
            producto = uow.productos.add(Producto(**datos.model_dump()))
            return ProductoPublico.model_validate(producto)

    def actualizar_producto(self, producto_id: int, datos: ProductoActualizar) -> ProductoPublico:
        with self.uow_factory() as uow:
            producto = uow.productos.get(producto_id, activos_solo=True)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto inexistente")
            cambios = datos.model_dump(exclude_unset=True)
            if "categoria_id" in cambios and uow.categorias.get(cambios["categoria_id"], True) is None:
                raise HTTPException(status_code=404, detail="Categoría inexistente")
            for campo, valor in cambios.items():
                setattr(producto, campo, valor)
            uow.session.add(producto)
            uow.session.flush()
            return ProductoPublico.model_validate(producto)

    def actualizar_estado_producto(
        self, producto_id: int, datos: ProductoEstadoActualizar
    ) -> ProductoPublico:
        with self.uow_factory() as uow:
            producto = uow.productos.get(producto_id, activos_solo=True)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto inexistente")
            for campo, valor in datos.model_dump(exclude_unset=True).items():
                setattr(producto, campo, valor)
            uow.session.add(producto)
            uow.session.flush()
            return ProductoPublico.model_validate(producto)

    def eliminar_producto(self, producto_id: int) -> None:
        with self.uow_factory() as uow:
            producto = uow.productos.get(producto_id, activos_solo=True)
            if producto is None:
                raise HTTPException(status_code=404, detail="Producto inexistente")
            producto.activo = False
            uow.session.add(producto)
