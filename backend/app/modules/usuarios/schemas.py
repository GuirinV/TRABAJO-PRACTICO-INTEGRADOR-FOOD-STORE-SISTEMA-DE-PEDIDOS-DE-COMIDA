from pydantic import EmailStr, Field as SchemaField
from sqlmodel import SQLModel


class RegistroUsuario(SQLModel):
    nombre: str = SchemaField(min_length=1, max_length=100)
    email: EmailStr
    password: str = SchemaField(min_length=8, max_length=128)


class UsuarioPublico(SQLModel):
    id: int
    nombre: str
    email: str
    rol: str
    disabled: bool
