from sqlmodel import select

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.modules.catalogo.models import Categoria, Producto
from app.modules.usuarios.models import Usuario


def seed() -> None:
    create_db_and_tables()
    with UnitOfWork() as uow:
        admin = uow.session.exec(
            select(Usuario).where(Usuario.email == settings.seed_admin_email)
        ).first()
        if admin is None:
            uow.session.add(
                Usuario(
                    nombre=settings.seed_admin_name,
                    email=settings.seed_admin_email,
                    password_hash=hash_password(settings.seed_admin_password),
                    rol="admin",
                )
            )

        category_names = ["Hamburguesas", "Pizzas", "Bebidas"]
        categories: dict[str, Categoria] = {}
        for name in category_names:
            category = uow.session.exec(
                select(Categoria).where(Categoria.nombre == name)
            ).first()
            if category is None:
                category = Categoria(nombre=name, descripcion=f"Productos de {name.lower()}")
                uow.session.add(category)
                uow.session.flush()
            categories[name] = category

        seed_products = [
            ("Hamburguesa clásica", "Carne, lechuga, tomate y queso", 8500.0, 20, "Hamburguesas"),
            ("Hamburguesa completa", "Carne, jamón, queso y huevo", 10500.0, 15, "Hamburguesas"),
            ("Pizza muzzarella", "Salsa de tomate y muzzarella", 12000.0, 12, "Pizzas"),
            ("Pizza napolitana", "Muzzarella, tomate y ajo", 13500.0, 10, "Pizzas"),
            ("Gaseosa", "Botella de 500 ml", 2500.0, 30, "Bebidas"),
        ]
        for name, description, price, stock, category_name in seed_products:
            existing = uow.session.exec(
                select(Producto).where(Producto.nombre == name)
            ).first()
            if existing is None:
                uow.session.add(
                    Producto(
                        nombre=name,
                        descripcion=description,
                        precio=price,
                        stock=stock,
                        disponible=True,
                        categoria_id=categories[category_name].id,
                    )
                )


if __name__ == "__main__":
    seed()
    print("Seed aplicado correctamente.")
