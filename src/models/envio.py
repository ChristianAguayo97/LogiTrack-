from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from src.models.enums import Restriccion, EstadoEnvio, Prioridad, TipoEnvio, VentanaHorario


class EnvioBase(SQLModel):
    remitente_id: int
    destinatario_id: int
    peso_paquete: float = Field(ge=0)
    distancia_estimada: float = Field(ge=0)
    restricciones: Restriccion = Restriccion.NINGUNO
    tiene_caducidad: bool = False
    tipo_envio: TipoEnvio = TipoEnvio.NORMAL
    ventana_horario: VentanaHorario = VentanaHorario.MAÑANA
    creado_por_usuario_id: int
    
class CrearEnvio(EnvioBase):
    pass

class ActualizarEnvio(SQLModel):
    remitente_id: Optional[int] = None
    destinatario_id: Optional[int] = None
    peso_paquete: Optional[float] = Field(default=None, ge=0)
    distancia_estimada: Optional[float] = Field(default=None, ge=0)
    restricciones: Optional[Restriccion] = None
    tiene_caducidad: Optional[bool] = None
    tipo_envio: Optional[TipoEnvio] = None
    ventana_horario: Optional[VentanaHorario] = None

class MostrarEnvio(EnvioBase):
    tracking_id: int
    estado: EstadoEnvio
    prioridad: Optional[Prioridad] = None
    f_creacion: datetime
    f_actualizacion: datetime
    model_config = {"from_attributes": True}

class Envio(EnvioBase, table=True):
    __tablename__ = "envio"
    tracking_id: Optional[int] = Field(default=None, primary_key=True)
    estado: EstadoEnvio = Field(default=EstadoEnvio.PENDIENTE)
    prioridad: Optional[Prioridad] = Field(default=None)
    f_creacion: datetime = Field(default_factory=datetime.now)
    f_actualizacion: datetime = Field(default_factory=datetime.now)
