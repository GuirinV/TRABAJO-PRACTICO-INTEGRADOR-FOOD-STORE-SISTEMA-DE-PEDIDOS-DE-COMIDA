from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.catalogo.models import Producto
    from app.modules.usuarios.models import Usuario


class Pedido(SQLModel, table=True):
    __tablename__ = "pedidos"

    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuarios.id", index=True)
    estado: str = Field(default="PENDIENTE", max_length=30)
    forma_pago: str = Field(max_length=30)
    direccion_entrega: str = Field(min_length=5, max_length=200)
    total: float = Field(default=0, ge=0)
    creado_en: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    usuario: "Usuario" = Relationship(back_populates="pedidos")
    items: list["DetallePedido"] = Relationship(back_populates="pedido")


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalles_pedido"

    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)
    producto_id: int = Field(foreign_key="productos.id", index=True)
    nombre_producto: str = Field(max_length=150)
    precio_unitario: float = Field(gt=0)
    cantidad: int = Field(gt=0)
    subtotal: float = Field(ge=0)

    pedido: Pedido = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="detalles")
