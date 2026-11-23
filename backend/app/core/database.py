from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.modules.catalogo.models import Categoria, Producto
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.usuarios.models import Usuario


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
