import json
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np


DATASET_PATH = Path(__file__).parent / "dataset_prioridad.json"
MODELOS_DIR = Path(__file__).parent.parent.parent / "models_ml"


def cargar_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    
    X = []
    y = []
    
    for item in datos:
        tipo_express = 1 if item["tipo_envio"].lower() == "express" else 0
        
        es_fragil = 1 if item["restriccion"].lower() == "fragil" else 0
        es_frio = 1 if item["restriccion"].lower() == "frio" else 0
        es_toxico = 1 if item["restriccion"].lower() == "toxico" else 0
        es_inflamble = 1 if item["restriccion"].lower() in ["inflamable"] else 0
        es_perecedero = 1 if item["restriccion"].lower() == "perecedero" else 0
        
        ventana = item["ventana_horaria"].lower()
        es_manana = 1 if ventana == "manana" else 0
        es_tarde = 1 if ventana == "tarde" else 0
        es_noche = 1 if ventana == "noche" else 0
        
        features = [
            item["distancia_estimada"],
            item["volumen_kg"],
            es_fragil,
            es_frio,
            es_toxico,
            es_inflamble,
            es_perecedero,
            item["saturacion_ruta"],
            tipo_express,
            es_manana,
            es_tarde,
            es_noche,
        ]
        
        X.append(features)
        y.append(item["prioridad"])
    
    return np.array(X), np.array(y)

def entrenar_modelo():
    X, y = cargar_dataset()
    for clase in np.unique(y):
        count = np.sum(y == clase)
        print(f"   {clase}: {count} ({count/len(y)*100:.1f}%)")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )
    modelo.fit(X_train, y_train)
    MODELOS_DIR.mkdir(exist_ok=True)
    modelo_path = MODELOS_DIR / "modelo_prioridad.pkl"
    with open(modelo_path, "wb") as f:
        pickle.dump(modelo, f)
    return modelo

if __name__ == "__main__":
    print("Iniciando entrenamiento del modelo...")
    entrenar_modelo()
    print("Modelo guardado exitosamente en models_ml/modelo_prioridad.pkl")