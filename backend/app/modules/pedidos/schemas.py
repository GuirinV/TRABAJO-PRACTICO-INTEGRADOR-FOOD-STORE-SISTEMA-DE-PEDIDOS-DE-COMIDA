from datetime import datetime
from enum import StrEnum

from pydantic import Field
from sqlmodel import SQLModel


class FormaPago(StrEnum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"


class EstadoPedido(StrEnum):
    PENDIENTE = "PENDIENTE"
    EN_PREPARACION = "EN_PREPARACION"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class ItemCarrito(SQLModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class PedidoCrear(SQLModel):
    items: list[ItemCarrito] = Field(min_length=1)
    forma_pago: FormaPago
    direccion_entrega: str = Field(min_length=5, max_length=200)


class EstadoPedidoActualizar(SQLModel):
    estado: EstadoPedido


class DetallePedidoPublico(SQLModel):
    id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoPublico(SQLModel):
    id: int
    usuario_id: int
    estado: EstadoPedido
    forma_pago: FormaPago
    direccion_entrega: str
    total: float
    creado_en: datetime
    items: list[DetallePedidoPublico]


class ListaPedidos(SQLModel):
    total: int
    items: list[PedidoPublico]


class ResumenPedidos(SQLModel):
    pendientes: int
    en_preparacion: int
    entregados: int
    cancelados: int
    total_pedidos: int
