from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.pedidos.models import Pedido


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=100)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    rol: str = Field(default="user", max_length=20)
    disabled: bool = Field(default=False)

    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
