from sqlmodel import Session, func, select

from app.modules.usuarios.models import Usuario


class UsuarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)

    def get_by_email(self, email: str) -> Usuario | None:
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()

    def list(self, skip: int = 0, limit: int = 100) -> list[Usuario]:
        statement = select(Usuario).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def count(self) -> int:
        return int(self.session.exec(select(func.count()).select_from(Usuario)).one())

    def add(self, usuario: Usuario) -> Usuario:
        self.session.add(usuario)
        self.session.flush()
        self.session.refresh(usuario)
        return usuario
