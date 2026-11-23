from pydantic import Field
from sqlmodel import SQLModel


class CategoriaCrear(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)


class CategoriaActualizar(SQLModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = Field(default=None, max_length=500)


class CategoriaPublica(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    activo: bool


class ProductoCrear(SQLModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=1000)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    disponible: bool = True
    categoria_id: int


class ProductoActualizar(SQLModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=1000)
    precio: float | None = Field(default=None, gt=0)
    categoria_id: int | None = None


class ProductoEstadoActualizar(SQLModel):
    stock: int | None = Field(default=None, ge=0)
    disponible: bool | None = None


class ProductoPublico(SQLModel):
    id: int
    nombre: str
    descripcion: str | None
    precio: float
    stock: int
    disponible: bool
    activo: bool
    categoria_id: int


class ListaCategorias(SQLModel):
    total: int
    items: list[CategoriaPublica]


class ListaProductos(SQLModel):
    total: int
    items: list[ProductoPublico]
