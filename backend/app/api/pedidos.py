from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, require_admin
from app.modules.pedidos.schemas import (
    EstadoPedidoActualizar,
    ListaPedidos,
    PedidoCrear,
    PedidoPublico,
    ResumenPedidos,
)
from app.modules.pedidos.service import PedidoService
from app.modules.usuarios.schemas import UsuarioPublico

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


def get_pedido_service() -> PedidoService:
    return PedidoService()


@router.post("", response_model=PedidoPublico, status_code=201)
def crear_pedido(
    datos: PedidoCrear,
    usuario: Annotated[UsuarioPublico, Depends(get_current_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> PedidoPublico:
    return service.crear(datos, usuario)


@router.get("", response_model=ListaPedidos)
def listar_pedidos(
    usuario: Annotated[UsuarioPublico, Depends(get_current_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> ListaPedidos:
    return service.listar(usuario)


@router.get("/resumen", response_model=ResumenPedidos)
def resumen_pedidos(
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> ResumenPedidos:
    return service.resumen()


@router.get("/{pedido_id}", response_model=PedidoPublico)
def obtener_pedido(
    pedido_id: int,
    usuario: Annotated[UsuarioPublico, Depends(get_current_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> PedidoPublico:
    return service.obtener(pedido_id, usuario)


@router.post("/{pedido_id}/cancelar", response_model=PedidoPublico)
def cancelar_pedido(
    pedido_id: int,
    usuario: Annotated[UsuarioPublico, Depends(get_current_user)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> PedidoPublico:
    return service.cancelar(pedido_id, usuario)


@router.patch("/{pedido_id}/estado", response_model=PedidoPublico)
def cambiar_estado_pedido(
    pedido_id: int,
    datos: EstadoPedidoActualizar,
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[PedidoService, Depends(get_pedido_service)],
) -> PedidoPublico:
    return service.cambiar_estado(pedido_id, datos.estado)
