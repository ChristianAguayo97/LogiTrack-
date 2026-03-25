from enum import Enum

class Restriccion (str, Enum):
    FRIO = "Frio"
    FRAGIL = "Fragil"
    TOXICO = "Toxico"
    INFLAMABLE = "Inflamble"
    PERECEDERO = "Perecedero"
    NINGUNO = "Ninguno"
    
class TipoEnvio (str, Enum):
    NORMAL = "Normal"
    EXPRESS = "Express"

class EstadoEnvio(str, Enum):
    PENDIENTE = "Pendiente"
    EN_TRANSITO = "En transito"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"

class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    
class VentanaHorario(str, Enum):
    MAÑANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"


