from sqlmodel import Session, func, or_, select

from app.modules.catalogo.models import Categoria, Producto


class CategoriaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, categoria_id: int, activos_solo: bool = False) -> Categoria | None:
        statement = select(Categoria).where(Categoria.id == categoria_id)
        if activos_solo:
            statement = statement.where(Categoria.activo.is_(True))
        return self.session.exec(statement).first()

    def list(self, activos_solo: bool = True) -> list[Categoria]:
        statement = select(Categoria)
        if activos_solo:
            statement = statement.where(Categoria.activo.is_(True))
        return list(self.session.exec(statement).all())

    def count(self, activos_solo: bool = True) -> int:
        statement = select(func.count()).select_from(Categoria)
        if activos_solo:
            statement = statement.where(Categoria.activo.is_(True))
        return int(self.session.exec(statement).one())

    def add(self, categoria: Categoria) -> Categoria:
        self.session.add(categoria)
        self.session.flush()
        self.session.refresh(categoria)
        return categoria


class ProductoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, producto_id: int, activos_solo: bool = False) -> Producto | None:
        statement = select(Producto).where(Producto.id == producto_id)
        if activos_solo:
            statement = statement.where(Producto.activo.is_(True))
        return self.session.exec(statement).first()

    def get_with_category(self, producto_id: int) -> tuple[Producto, Categoria] | None:
        statement = (
            select(Producto, Categoria)
            .join(Categoria, Producto.categoria_id == Categoria.id)
            .where(Producto.id == producto_id)
        )
        result = self.session.exec(statement).first()
        if result is None:
            return None
        return result

    def add(self, producto: Producto) -> Producto:
        self.session.add(producto)
        self.session.flush()
        self.session.refresh(producto)
        return producto

    def list(
        self,
        skip: int,
        limit: int,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        activos_solo: bool = True,
    ) -> list[Producto]:
        statement = select(Producto)
        if activos_solo:
            statement = statement.where(Producto.activo.is_(True))
        if search:
            statement = statement.where(
                or_(Producto.nombre.ilike(f"%{search}%"), Producto.descripcion.ilike(f"%{search}%"))
            )
        if categoria_id is not None:
            statement = statement.where(Producto.categoria_id == categoria_id)
        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)
        return list(self.session.exec(statement.offset(skip).limit(limit)).all())

    def count(
        self,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        activos_solo: bool = True,
    ) -> int:
        statement = select(func.count()).select_from(Producto)
        if activos_solo:
            statement = statement.where(Producto.activo.is_(True))
        if search:
            statement = statement.where(
                or_(Producto.nombre.ilike(f"%{search}%"), Producto.descripcion.ilike(f"%{search}%"))
            )
        if categoria_id is not None:
            statement = statement.where(Producto.categoria_id == categoria_id)
        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)
        return int(self.session.exec(statement).one())
