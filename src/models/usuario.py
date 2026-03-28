from enum import Enum
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Rol(str, Enum):
    OPERADOR = "Operador"
    SUPERVISOR = "Supervisor"


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    id: int = Field(default=None, primary_key=True)
    nombre: str
    email: str
    rol: Rol
    activo: bool = True


def ahora_argentina() -> datetime:
    return datetime.now(timezone.utc).astimezone()


class Auditoria(SQLModel, table=True):
    __tablename__ = "auditoria"
    id: int = Field(default=None, primary_key=True)
    usuario_id: int
    usuario_nombre: str
    usuario_rol: str
    envio_id: int
    accion: str
    detalle: str
    f_accion: datetime = Field(default_factory=ahora_argentina)
