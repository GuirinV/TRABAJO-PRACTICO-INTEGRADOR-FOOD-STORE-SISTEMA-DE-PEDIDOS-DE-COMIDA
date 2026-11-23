from fastapi import Cookie, Depends, HTTPException

from app.core.security import get_subject
from app.modules.usuarios.schemas import UsuarioPublico
from app.modules.usuarios.service import UsuarioService


def get_usuario_service() -> UsuarioService:
    return UsuarioService()


def get_current_user(
    access_token: str | None = Cookie(default=None),
    service: UsuarioService = Depends(get_usuario_service),
) -> UsuarioPublico:
    if access_token is None:
        raise HTTPException(status_code=401, detail="No hay una sesión activa")
    subject = get_subject(access_token)
    if subject is None or not subject.isdigit():
        raise HTTPException(status_code=401, detail="Sesión inválida")
    return service.obtener(int(subject))


def require_admin(user: UsuarioPublico = Depends(get_current_user)) -> UsuarioPublico:
    if user.rol != "admin":
        raise HTTPException(status_code=403, detail="Se requiere rol admin")
    return user
