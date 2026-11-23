from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import require_admin
from app.modules.usuarios.schemas import UsuarioPublico
from app.modules.usuarios.service import AdminUsuarioService

router = APIRouter(prefix="/admin/usuarios", tags=["Administración de usuarios"])


def get_admin_usuario_service() -> AdminUsuarioService:
    return AdminUsuarioService()


@router.get("")
def listar_usuarios(
    _: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[AdminUsuarioService, Depends(get_admin_usuario_service)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> dict[str, object]:
    return service.listar(skip, limit)


@router.post("/{usuario_id}/activar", response_model=UsuarioPublico)
def activar_usuario(
    usuario_id: int,
    admin: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[AdminUsuarioService, Depends(get_admin_usuario_service)],
) -> UsuarioPublico:
    return service.cambiar_estado(usuario_id, True, admin.id)


@router.post("/{usuario_id}/desactivar", response_model=UsuarioPublico)
def desactivar_usuario(
    usuario_id: int,
    admin: Annotated[UsuarioPublico, Depends(require_admin)],
    service: Annotated[AdminUsuarioService, Depends(get_admin_usuario_service)],
) -> UsuarioPublico:
    return service.cambiar_estado(usuario_id, False, admin.id)
