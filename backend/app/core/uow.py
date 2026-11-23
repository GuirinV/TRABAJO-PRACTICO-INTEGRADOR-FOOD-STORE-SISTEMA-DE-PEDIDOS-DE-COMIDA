from types import TracebackType
from typing import Self

from sqlmodel import Session

from app.core.database import engine
from app.modules.catalogo.repositories import CategoriaRepository, ProductoRepository
from app.modules.pedidos.repositories import PedidoRepository
from app.modules.usuarios.repositories import UsuarioRepository


class UnitOfWork:
    def __init__(self) -> None:
        self.session: Session | None = None
        self.usuarios: UsuarioRepository
        self.categorias: CategoriaRepository
        self.productos: ProductoRepository
        self.pedidos: PedidoRepository

    def __enter__(self) -> Self:
        self.session = Session(engine)
        self.usuarios = UsuarioRepository(self.session)
        self.categorias = CategoriaRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if self.session is None:
            return False

        try:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
        finally:
            self.session.close()
            self.session = None
        return False
