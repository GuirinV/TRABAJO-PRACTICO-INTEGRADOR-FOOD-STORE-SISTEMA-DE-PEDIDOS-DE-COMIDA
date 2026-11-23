from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_current_user, get_usuario_service
from app.core.config import settings
from app.core.security import create_access_token
from app.modules.usuarios.schemas import RegistroUsuario, UsuarioPublico
from app.modules.usuarios.service import UsuarioService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioPublico, status_code=201)
def register(
    datos: RegistroUsuario,
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> UsuarioPublico:
    return service.registrar(datos)


@router.post("/token")
def login(
    response: Response,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> dict[str, str]:
    user = service.autenticar(form.username, form.password)
    response.set_cookie(
        key="access_token",
        value=create_access_token(str(user.id)),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    return {"message": "Sesión iniciada"}


@router.post("/logout", status_code=204)
def logout(response: Response) -> Response:
    response.delete_cookie(key="access_token", path="/")
    response.status_code = 204
    return response


@router.get("/me", response_model=UsuarioPublico)
def me(user: Annotated[UsuarioPublico, Depends(get_current_user)]) -> UsuarioPublico:
    return user
