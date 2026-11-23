from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import RegistroUsuario, UsuarioPublico


class UsuarioService:
    def __init__(self, uow_factory=UnitOfWork) -> None:
        self.uow_factory = uow_factory

    def registrar(self, datos: RegistroUsuario) -> UsuarioPublico:
        with self.uow_factory() as uow:
            if uow.usuarios.get_by_email(str(datos.email)):
                raise HTTPException(status_code=409, detail="El email ya está registrado")
            usuario = Usuario(
                nombre=datos.nombre,
                email=str(datos.email),
                password_hash=hash_password(datos.password),
            )
            try:
                guardado = uow.usuarios.add(usuario)
            except IntegrityError as error:
                raise HTTPException(status_code=409, detail="El email ya está registrado") from error
            return UsuarioPublico.model_validate(guardado)

    def obtener(self, usuario_id: int) -> UsuarioPublico:
        with self.uow_factory() as uow:
            usuario = uow.usuarios.get(usuario_id)
            if usuario is None:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
            if usuario.disabled:
                raise HTTPException(status_code=400, detail="La cuenta está desactivada")
            return UsuarioPublico.model_validate(usuario)

    def autenticar(self, email: str, password: str) -> UsuarioPublico:
        from app.core.security import verify_password

        with self.uow_factory() as uow:
            usuario = uow.usuarios.get_by_email(email)
            if usuario is None or not verify_password(password, usuario.password_hash):
                raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
            if usuario.disabled:
                raise HTTPException(status_code=400, detail="La cuenta está desactivada")
            return UsuarioPublico.model_validate(usuario)


class AdminUsuarioService:
    def __init__(self, uow_factory=UnitOfWork) -> None:
        self.uow_factory = uow_factory

    def listar(self, skip: int, limit: int) -> dict[str, object]:
        with self.uow_factory() as uow:
            total = uow.usuarios.count()
            usuarios = uow.usuarios.list(skip, limit)
            items = [UsuarioPublico.model_validate(usuario) for usuario in usuarios]
            return {"total": total, "items": items}

    def cambiar_estado(self, usuario_id: int, activo: bool, admin_id: int) -> UsuarioPublico:
        with self.uow_factory() as uow:
            usuario = uow.usuarios.get(usuario_id)
            if usuario is None:
                raise HTTPException(status_code=404, detail="Usuario inexistente")
            if usuario_id == admin_id and not activo:
                raise HTTPException(status_code=400, detail="No podés desactivarte a vos mismo")
            usuario.disabled = not activo
            uow.session.add(usuario)
            uow.session.flush()
            return UsuarioPublico.model_validate(usuario)
