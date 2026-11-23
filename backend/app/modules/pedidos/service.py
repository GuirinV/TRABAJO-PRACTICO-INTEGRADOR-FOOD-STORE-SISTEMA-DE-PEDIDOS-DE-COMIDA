from fastapi import HTTPException

from app.core.uow import UnitOfWork
from app.modules.catalogo.models import Producto
from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.schemas import (
    EstadoPedido,
    ListaPedidos,
    PedidoCrear,
    PedidoPublico,
    ResumenPedidos,
)
from app.modules.usuarios.schemas import UsuarioPublico


TRANSICIONES_VALIDAS: dict[EstadoPedido, set[EstadoPedido]] = {
    EstadoPedido.PENDIENTE: {EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO},
    EstadoPedido.EN_PREPARACION: {EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO},
    EstadoPedido.ENTREGADO: set(),
    EstadoPedido.CANCELADO: set(),
}


class PedidoService:
    def __init__(self, uow_factory=UnitOfWork) -> None:
        self.uow_factory = uow_factory

    @staticmethod
    def _a_schema(pedido: Pedido) -> PedidoPublico:
        return PedidoPublico.model_validate(pedido)

    def crear(self, datos: PedidoCrear, usuario: UsuarioPublico) -> PedidoPublico:
        with self.uow_factory() as uow:
            ids = [item.producto_id for item in datos.items]
            if len(ids) != len(set(ids)):
                raise HTTPException(status_code=400, detail="No se permiten productos repetidos")

            pedido = Pedido(
                usuario_id=usuario.id,
                forma_pago=datos.forma_pago.value,
                direccion_entrega=datos.direccion_entrega,
                estado=EstadoPedido.PENDIENTE.value,
                total=0,
            )
            uow.pedidos.add(pedido)
            total = 0.0
            for item in datos.items:
                resultado = uow.productos.get_with_category(item.producto_id)
                if resultado is None:
                    raise HTTPException(status_code=404, detail="Producto inexistente")
                producto, categoria = resultado
                if not producto.activo or not categoria.activo:
                    raise HTTPException(status_code=404, detail="Producto inexistente")
                if not producto.disponible:
                    raise HTTPException(status_code=400, detail="Producto no disponible")
                if producto.stock < item.cantidad:
                    raise HTTPException(status_code=400, detail="Stock insuficiente")

                producto.stock -= item.cantidad
                subtotal = producto.precio * item.cantidad
                total += subtotal
                uow.session.add(producto)
                uow.pedidos.add_detalle(
                    DetallePedido(
                        pedido_id=pedido.id,
                        producto_id=producto.id,
                        nombre_producto=producto.nombre,
                        precio_unitario=producto.precio,
                        cantidad=item.cantidad,
                        subtotal=subtotal,
                    )
                )

            pedido.total = total
            uow.session.add(pedido)
            uow.session.flush()
            uow.session.refresh(pedido)
            uow.session.refresh(pedido, attribute_names=["items"])
            return self._a_schema(pedido)

    def listar(self, usuario: UsuarioPublico) -> ListaPedidos:
        with self.uow_factory() as uow:
            pedidos = (
                uow.pedidos.list_all()
                if usuario.rol == "admin"
                else uow.pedidos.list_by_usuario(usuario.id)
            )
            items = [self._a_schema(pedido) for pedido in pedidos]
            total = uow.pedidos.count() if usuario.rol == "admin" else len(items)
            return ListaPedidos(total=total, items=items)

    def obtener(self, pedido_id: int, usuario: UsuarioPublico) -> PedidoPublico:
        with self.uow_factory() as uow:
            pedido = uow.pedidos.get(pedido_id)
            if pedido is None:
                raise HTTPException(status_code=404, detail="Pedido inexistente")
            if usuario.rol != "admin" and pedido.usuario_id != usuario.id:
                raise HTTPException(status_code=403, detail="No podés acceder a este pedido")
            uow.session.refresh(pedido, attribute_names=["items"])
            return self._a_schema(pedido)

    def cancelar(self, pedido_id: int, usuario: UsuarioPublico) -> PedidoPublico:
        with self.uow_factory() as uow:
            pedido = uow.pedidos.get(pedido_id)
            if pedido is None:
                raise HTTPException(status_code=404, detail="Pedido inexistente")
            if usuario.rol != "admin" and pedido.usuario_id != usuario.id:
                raise HTTPException(status_code=403, detail="No podés cancelar este pedido")
            if usuario.rol != "admin" and pedido.estado != EstadoPedido.PENDIENTE.value:
                raise HTTPException(status_code=400, detail="Solo podés cancelar pedidos pendientes")
            self._transicionar(uow, pedido, EstadoPedido.CANCELADO)
            uow.session.refresh(pedido, attribute_names=["items"])
            return self._a_schema(pedido)

    def cambiar_estado(self, pedido_id: int, estado: EstadoPedido) -> PedidoPublico:
        with self.uow_factory() as uow:
            pedido = uow.pedidos.get(pedido_id)
            if pedido is None:
                raise HTTPException(status_code=404, detail="Pedido inexistente")
            self._transicionar(uow, pedido, estado)
            uow.session.refresh(pedido, attribute_names=["items"])
            return self._a_schema(pedido)

    @staticmethod
    def _transicionar(uow: UnitOfWork, pedido: Pedido, nuevo_estado: EstadoPedido) -> None:
        try:
            estado_actual = EstadoPedido(pedido.estado)
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Estado de pedido inválido") from error
        if nuevo_estado not in TRANSICIONES_VALIDAS[estado_actual]:
            raise HTTPException(status_code=400, detail="Transición de estado inválida")
        if nuevo_estado == EstadoPedido.CANCELADO:
            uow.session.refresh(pedido, attribute_names=["items"])
            for detalle in pedido.items:
                producto = uow.productos.get(detalle.producto_id)
                if producto is None:
                    raise HTTPException(status_code=404, detail="Producto asociado inexistente")
                producto.stock += detalle.cantidad
                uow.session.add(producto)
        pedido.estado = nuevo_estado.value
        uow.session.add(pedido)
        uow.session.flush()

    def resumen(self) -> ResumenPedidos:
        with self.uow_factory() as uow:
            conteos = uow.pedidos.count_by_estado()
            return ResumenPedidos(
                pendientes=conteos.get(EstadoPedido.PENDIENTE.value, 0),
                en_preparacion=conteos.get(EstadoPedido.EN_PREPARACION.value, 0),
                entregados=conteos.get(EstadoPedido.ENTREGADO.value, 0),
                cancelados=conteos.get(EstadoPedido.CANCELADO.value, 0),
                total_pedidos=sum(conteos.values()),
            )
