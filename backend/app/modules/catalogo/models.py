from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.pedidos.models import DetallePedido


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=100, unique=True, index=True)
    descripcion: str | None = Field(default=None, max_length=500)
    activo: bool = Field(default=True)

    productos: list["Producto"] = Relationship(back_populates="categoria")


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=150, index=True)
    descripcion: str | None = Field(default=None, max_length=1000)
    precio: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    activo: bool = Field(default=True)
    categoria_id: int = Field(foreign_key="categorias.id", index=True)

    categoria: Categoria = Relationship(back_populates="productos")
    detalles: list["DetallePedido"] = Relationship(back_populates="producto")
