import json
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from src.models.envio import Envio
from src.models.enums import Prioridad, TipoEnvio, Restriccion, VentanaHorario


MODELOS_DIR = Path(__file__).parent.parent.parent / "models_ml"
MODELOS_DIR.mkdir(exist_ok=True)


def _obtener_features(envio: Envio) -> list:
    tipo_express = 1 if envio.tipo_envio == TipoEnvio.EXPRESS else 0
    
    es_fragil = 1 if envio.restricciones == Restriccion.FRAGIL else 0
    es_frio = 1 if envio.restricciones == Restriccion.FRIO else 0
    es_toxico = 1 if envio.restricciones == Restriccion.TOXICO else 0
    es_inflamble = 1 if envio.restricciones == Restriccion.INFLAMABLE else 0
    es_perecedero = 1 if envio.restricciones == Restriccion.PERECEDERO else 0
    
    es_manana = 1 if envio.ventana_horario == VentanaHorario.MAÑANA else 0
    es_tarde = 1 if envio.ventana_horario == VentanaHorario.TARDE else 0
    es_noche = 1 if envio.ventana_horario == VentanaHorario.NOCHE else 0
    
    return [
        float(envio.distancia_estimada),
        float(envio.peso_paquete),
        float(es_fragil),
        float(es_frio),
        float(es_toxico),
        float(es_inflamble),
        float(es_perecedero),
        float(envio.saturacion_ruta),
        float(tipo_express),
        float(es_manana),
        float(es_tarde),
        float(es_noche),
    ]


def predecir_prioridad(envio: Envio) -> Prioridad:
    modelo_path = MODELOS_DIR / "modelo_prioridad.pkl"
    
    if modelo_path.exists():
        with open(modelo_path, "rb") as f:
            modelo = pickle.load(f)
        features = _obtener_features(envio)
        prediccion = modelo.predict([features])[0]
        return Prioridad(prediccion)
    
    return _prioridad_default(envio)


def _prioridad_default(envio: Envio) -> Prioridad:
    if envio.tipo_envio == TipoEnvio.EXPRESS and envio.saturacion_ruta > 0.5:
        return Prioridad.ALTA
    elif envio.restricciones in [Restriccion.INFLAMABLE, Restriccion.TOXICO]:
        return Prioridad.ALTA
    elif envio.restricciones == Restriccion.PERECEDERO:
        return Prioridad.MEDIA
    return Prioridad.BAJA
