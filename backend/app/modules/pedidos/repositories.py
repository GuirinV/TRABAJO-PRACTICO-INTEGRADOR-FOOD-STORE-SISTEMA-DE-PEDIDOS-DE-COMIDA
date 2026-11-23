from sqlmodel import Session, func, select

from app.modules.pedidos.models import DetallePedido, Pedido


class PedidoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, pedido_id: int) -> Pedido | None:
        return self.session.get(Pedido, pedido_id)

    def list_by_usuario(self, usuario_id: int) -> list[Pedido]:
        statement = select(Pedido).where(Pedido.usuario_id == usuario_id).order_by(Pedido.creado_en.desc())
        return list(self.session.exec(statement).all())

    def list_all(self) -> list[Pedido]:
        return list(self.session.exec(select(Pedido).order_by(Pedido.creado_en.desc())).all())

    def count(self) -> int:
        return int(self.session.exec(select(func.count()).select_from(Pedido)).one())

    def count_by_estado(self) -> dict[str, int]:
        rows = self.session.exec(
            select(Pedido.estado, func.count()).group_by(Pedido.estado)
        ).all()
        return {estado: int(total) for estado, total in rows}

    def add(self, pedido: Pedido) -> Pedido:
        self.session.add(pedido)
        self.session.flush()
        self.session.refresh(pedido)
        return pedido

    def add_detalle(self, detalle: DetallePedido) -> DetallePedido:
        self.session.add(detalle)
        self.session.flush()
        self.session.refresh(detalle)
        return detalle
