# LogiTrack - Guía de Estudio

## Proyecto de Gestión de Envíos con Machine Learning

---

## Tabla de Contenidos

1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Modelos de Datos](#modelos-de-datos)
3. [Router y Endpoints](#router-y-endpoints)
4. [Servicio de Prioridad (ML)](#servicio-de-prioridad-ml)
5. [Script de Entrenamiento](#script-de-entrenamiento)
6. [Tests](#tests)
7. [Métricas de ML Explicadas](#métricas-de-ml-explicadas)

---

## 1. Estructura del Proyecto

```
LogiTrack2/
├── src/
│   ├── config/
│   │   └── db.py              # Conexión a MySQL
│   ├── models/
│   │   ├── enums.py           # Enumeraciones
│   │   └── envio.py           # Modelo de envío
│   ├── routers/
│   │   ├── deps/
│   │   │   └── db_sessions.py # Sesión de BD
│   │   └── envio_router.py    # Endpoints de la API
│   ├── services/
│   │   └── prioridad_service.py # Lógica de ML
│   ├── ml/
│   │   ├── dataset_prioridad.json # Dataset de entrenamiento
│   │   └── entrenar_modelo.py  # Script de entrenamiento
│   └── main.py                # Punto de entrada
├── tests/
│   ├── conftest.py            # Configuración de tests
│   └── test_envios.py         # Tests unitarios
├── models_ml/                 # Modelos entrenados (generados)
└── requirements.txt            # Dependencias
```

---

## 2. Modelos de Datos

### 2.1 Enums (`src/models/enums.py`)

Los enums definen valores fijos y predefinidos.

```python
from enum import Enum

# Enum para restricciones del paquete
class Restriccion(str, Enum):
    FRIO = "Frio"
    FRAGIL = "Fragil"
    TOXICO = "Toxico"
    INFLAMABLE = "Inflamble"
    PERECEDERO = "Perecedero"
    NINGUNO = "Ninguno"

# Enum para tipo de envío
class TipoEnvio(str, Enum):
    NORMAL = "Normal"
    EXPRESS = "Express"

# Enum para estado del envío
class EstadoEnvio(str, Enum):
    PENDIENTE = "Pendiente"
    EN_TRANSITO = "En transito"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"

# Enum para prioridad (resultado del ML)
class Prioridad(str, Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"

# Enum para ventana horaria
class VentanaHorario(str, Enum):
    MAÑANA = "Mañana"
    TARDE = "Tarde"
    NOCHE = "Noche"
```

**¿Por qué usar Enums?**
- Evitan errores de tipeo
- Limitan los valores posibles
- Mejor autocompletado en el IDE

---

### 2.2 Modelo Envío (`src/models/envio.py`)

El modelo define la estructura de la tabla en la base de datos.

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from src.models.enums import (
    Restriccion, EstadoEnvio, Prioridad, 
    TipoEnvio, VentanaHorario
)

# ============================================
# EnvioBase: Campos comunes a todas las clases
# ============================================
class EnvioBase(SQLModel):
    remitente_id: int                    # ID del remitente
    destinatario_id: int                # ID del destinatario
    peso_paquete: float = Field(ge=0)  # Peso en kg (mínimo 0)
    distancia_estimada: float = Field(ge=0)  # Distancia en km
    restricciones: Restriccion = Restriccion.NINGUNO  # Restricción del paquete
    tiene_caducidad: bool = False      # ¿Expira?
    tipo_envio: TipoEnvio = TipoEnvio.NORMAL  # Normal o Express
    ventana_horario: VentanaHorario = VentanaHorario.MAÑANA  # Horario de entrega
    saturacion_ruta: float = Field(ge=0, le=1, default=0.0)  # Saturación (0 a 1)
    creado_por_usuario_id: int         # Usuario que creó el envío

# ============================================
# CrearEnvio: Para crear nuevos envíos
# ============================================
class CrearEnvio(EnvioBase):
    pass  # Hereda todos los campos de EnvioBase

# ============================================
# ActualizarEnvio: Para actualizar envíos
# Todos los campos son opcionales (None por defecto)
# ============================================
class ActualizarEnvio(SQLModel):
    remitente_id: Optional[int] = None
    destinatario_id: Optional[int] = None
    peso_paquete: Optional[float] = Field(default=None, ge=0)
    distancia_estimada: Optional[float] = Field(default=None, ge=0)
    restricciones: Optional[Restriccion] = None
    tiene_caducidad: Optional[bool] = None
    tipo_envio: Optional[TipoEnvio] = None
    ventana_horario: Optional[VentanaHorario] = None
    saturacion_ruta: Optional[float] = Field(default=None, ge=0, le=1)

# ============================================
# MostrarEnvio: Lo que devolvemos al usuario
# ============================================
class MostrarEnvio(EnvioBase):
    tracking_id: int                    # ID único de seguimiento
    estado: EstadoEnvio                 # Estado actual
    prioridad: Optional[Prioridad] = None  # Prioridad ML (puede ser None)
    f_creacion: datetime               # Fecha de creación
    f_actualizacion: datetime          # Última modificación
    model_config = {"from_attributes": True}  # Permite convertir de objeto a dict

# ============================================
# Envio: La tabla real de la base de datos
# ============================================
class Envio(EnvioBase, table=True):    # table=True = es una tabla de BD
    __tablename__ = "envio"            # Nombre de la tabla en MySQL
    
    tracking_id: Optional[int] = Field(default=None, primary_key=True)
    # Primary key = clave primaria, identifica cada registro único
    
    estado: EstadoEnvio = Field(default=EstadoEnvio.PENDIENTE)
    # Default = valor inicial cuando se crea
    
    prioridad: Optional[Prioridad] = Field(default=None)
    # Empieza en None, el ML la asigna después
    
    f_creacion: datetime = Field(default_factory=datetime.now)
    # default_factory = función que se ejecuta para obtener el valor por defecto
    
    f_actualizacion: datetime = Field(default_factory=datetime.now)
```

---

## 3. Router y Endpoints

### 3.1 Configuración de Base de Datos (`src/routers/deps/db_sessions.py`)

```python
from typing import Generator, Annotated
from fastapi import Depends
from sqlmodel import Session
from src.config.db import engine

# Generator: tipo especial que yield (produce) valores
# Se usa para crear sesiones de BD que se cierran automáticamente
def get_db() -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos.
    
    Returns:
        Generator[Session, None, None]:
        - Yield: produce una sesión
        - None: no hay más tipos en el generador
    """
    with Session(engine) as session:  # Abre conexión a MySQL
        yield session                 # Usa la sesión, luego la cierra automáticamente

# Annotated + Depends: forma elegante de injectar la sesión
# SessionDep será automáticamente una sesión de BD en cualquier endpoint
SessionDep = Annotated[Session, Depends(get_db)]
```

---

### 3.2 Endpoints (`src/routers/envio_router.py`)

```python
from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from src.models.envio import Envio, CrearEnvio, ActualizarEnvio, MostrarEnvio
from src.models.enums import EstadoEnvio
from src.routers.deps.db_sessions import SessionDep
from src.services.prioridad_service import predecir_prioridad

# APIRouter: agrupa endpoints relacionados
envio_router = APIRouter(prefix="/envios", tags=["Envíos"])
# prefix = todas las rutas empezarán con /envios
# tags = categoría en la documentación Swagger

# ============================================
# POST /envios/ - Crear un nuevo envío
# ============================================
@envio_router.post("/", response_model=MostrarEnvio, status_code=201)
def crear_envio(datos: CrearEnvio, session: SessionDep):
    """
    Crea un nuevo envío en la base de datos.
    
    Args:
        datos: Datos del envío a crear (validado por CrearEnvio)
        session: Sesión de base de datos (inyectada automáticamente)
    
    Returns:
        MostrarEnvio: El envío creado con ID y prioridad asignada
    """
    # 1. Convertir datos JSON a objeto Envio
    envio = Envio.model_validate(datos)
    
    # 2. Calcular prioridad con ML
    prioridad = predecir_prioridad(envio)
    envio.prioridad = prioridad
    
    # 3. Guardar en base de datos
    session.add(envio)      # Preparar para insertar
    session.commit()        # Ejecutar INSERT
    session.refresh(envio)  # Recargar para obtener ID generado
    
    # 4. Devolver respuesta
    return envio

# ============================================
# GET /envios/ - Listar envíos
# ============================================
@envio_router.get("/", response_model=list[MostrarEnvio])
def listar_envios(
    session: SessionDep,
    skip: int = Query(0, ge=0),        # Paginación: desde qué registro
    limit: int = Query(100, ge=1, le=500),  # Máximo registros a devolver
    estado: EstadoEnvio | None = None,   # Filtro opcional por estado
):
    """
    Lista todos los envíos con paginación y filtros.
    
    Query params:
        skip: cuántos registros saltar (default 0)
        limit: cuántos max返回 (default 100, max 500)
        estado: filtrar por estado específico (opcional)
    """
    query = select(Envio)  # SELECT * FROM envio
    
    # Si se proporcionó estado, agregar WHERE
    if estado:
        query = query.where(Envio.estado == estado)
    
    # Aplicar paginación
    envios = session.exec(
        query.offset(skip).limit(limit)
    ).all()
    
    return envios

# ============================================
# GET /envios/{tracking_id} - Obtener uno
# ============================================
@envio_router.get("/{tracking_id}", response_model=MostrarEnvio)
def obtener_envio(tracking_id: int, session: SessionDep):
    """
    Obtiene un envío específico por su tracking_id.
    
    Args:
        tracking_id: ID único del envío
    
    Raises:
        HTTPException 404: Si el envío no existe
    """
    envio = session.get(Envio, tracking_id)  # SELECT * FROM envio WHERE tracking_id = ?
    
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    return envio

# ============================================
# PATCH /envios/{tracking_id} - Actualizar
# ============================================
@envio_router.patch("/{tracking_id}", response_model=MostrarEnvio)
def actualizar_envio(tracking_id: int, datos: ActualizarEnvio, session: SessionDep):
    """
    Actualiza campos específicos de un envío.
    Solo actualiza los campos que el usuario envió.
    """
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    # model_dump: convertir a dict
    # exclude_unset=True: solo incluir campos que el usuario SÍ envió
    datos_dict = datos.model_dump(exclude_unset=True)
    
    # Actualizar solo campos no nulos ni vacíos
    for key, value in datos_dict.items():
        if value is not None and value != "":
            setattr(envio, key, value)
    
    # Recalcular prioridad con los nuevos datos
    prioridad = predecir_prioridad(envio)
    envio.prioridad = prioridad
    
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio

# ============================================
# PATCH /envios/{tracking_id}/estado - Cambiar estado
# ============================================
@envio_router.patch("/{tracking_id}/estado", response_model=MostrarEnvio)
def cambiar_estado(tracking_id: int, estado: EstadoEnvio, session: SessionDep):
    """
    Cambia solo el estado de un envío.
    """
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    envio.estado = estado
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio
```

---

## 4. Servicio de Prioridad (ML)

### 4.1 Servicio de Predicción (`src/services/prioridad_service.py`)

```python
import json
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from src.models.envio import Envio
from src.models.enums import Prioridad, TipoEnvio, Restriccion, VentanaHorario

# Directorio donde se guarda el modelo entrenado
MODELOS_DIR = Path(__file__).parent.parent.parent / "models_ml"
MODELOS_DIR.mkdir(exist_ok=True)

# ============================================
# Convertir datos del envío a features numéricos
# ============================================
def _obtener_features(envio: Envio) -> list:
    """
    Convierte los datos del envío a una lista de números
    que el modelo de ML puede entender.
    
    Los modelos de ML solo trabajan con números, no con texto.
    Por eso convertimos las categorías a 0 o 1 (one-hot encoding).
    
    Returns:
        list: Lista de 12 números (features)
    """
    # Tipo de envío: 0 = Normal, 1 = Express
    tipo_express = 1 if envio.tipo_envio == TipoEnvio.EXPRESS else 0
    
    # Restricciones: una para cada tipo (0 o 1)
    # Esto es "one-hot encoding": solo una puede ser 1
    es_fragil = 1 if envio.restriccion == Restriccion.FRAGIL else 0
    es_frio = 1 if envio.restriccion == Restriccion.FRIO else 0
    es_toxico = 1 if envio.restriccion == Restriccion.TOXICO else 0
    es_inflamble = 1 if envio.restriccion == Restriccion.INFLAMABLE else 0
    es_perecedero = 1 if envio.restriccion == Restriccion.PERECEDERO else 0
    
    # Ventana horaria: también one-hot encoding
    es_manana = 1 if envio.ventana_horario == VentanaHorario.MAÑANA else 0
    es_tarde = 1 if envio.ventana_horario == VentanaHorario.TARDE else 0
    es_noche = 1 if envio.ventana_horario == VentanaHorario.NOCHE else 0
    
    # Retornar lista de features
    # - Primeros 2: valores continuos (distancia, peso)
    # - Siguientes 5: restricciones (0 o 1)
    # - Siguiente 1: saturación (0.0 a 1.0)
    # - Siguiente 1: tipo express (0 o 1)
    # - Últimos 3: ventana horaria (0 o 1)
    return [
        envio.distancia_estimada,  # Feature 1: distancia en km
        envio.peso_paquete,       # Feature 2: peso en kg
        es_fragil,                # Feature 3: ¿es frágil?
        es_frio,                  # Feature 4: ¿es frío?
        es_toxico,                # Feature 5: ¿es tóxico?
        es_inflamble,             # Feature 6: ¿es inflamable?
        es_perecedero,            # Feature 7: ¿es perecedero?
        envio.saturacion_ruta,    # Feature 8: saturación de ruta (0-1)
        tipo_express,              # Feature 9: ¿es express?
        es_manana,                # Feature 10: ¿ventana mañana?
        es_tarde,                 # Feature 11: ¿ventana tarde?
        es_noche,                 # Feature 12: ¿ventana noche?
    ]

# ============================================
# Predicción principal
# ============================================
def predecir_prioridad(envio: Envio) -> Prioridad:
    """
    Predice la prioridad de un envío usando el modelo entrenado.
    
    Args:
        envio: El envío a clasificar
    
    Returns:
        Prioridad: Alta, Media o Baja
    
    Raises:
        RuntimeError: Si el modelo no está entrenado
    """
    modelo_path = MODELOS_DIR / "modelo_prioridad.pkl"
    
    if modelo_path.exists():
        # Cargar el modelo desde el archivo .pkl
        with open(modelo_path, "rb") as f:
            modelo = pickle.load(f)
        
        # Convertir envío a features numéricos
        features = _obtener_features(envio)
        
        # El modelo predice: devuelve "Alta", "Media" o "Baja"
        prediccion = modelo.predict([features])[0]
        
        # Convertir string a enum
        return Prioridad(prediccion)
    
    # Si no existe modelo, lanzar error
    raise RuntimeError(
        "Modelo de ML no encontrado. Ejecuta 'python -m src.ml.entrenar_modelo'"
    )
```

---

## 5. Script de Entrenamiento

### 5.1 Entrenamiento del Modelo (`src/ml/entrenar_modelo.py`)

```python
import json
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, 
    accuracy_score, 
    confusion_matrix
)
import numpy as np

# Rutas de archivos
DATASET_PATH = Path(__file__).parent / "dataset_prioridad.json"
MODELOS_DIR = Path(__file__).parent.parent.parent / "models_ml"

# ============================================
# Cargar dataset desde JSON
# ============================================
def cargar_dataset():
    """
    Lee el archivo JSON y convierte los datos a arrays NumPy.
    
    El dataset tiene formato:
    [
        {"distancia_estimada": 100, "volumen_kg": 5, ...},
        ...
    ]
    
    Returns:
        X: array de features (características)
        y: array de etiquetas (prioridades)
    """
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        datos = json.load(f)
    
    X = []  # Features
    y = []  # Etiquetas (prioridades)
    
    for item in datos:
        # Convertir tipo_envio a binario
        tipo_express = 1 if item["tipo_envio"].lower() == "express" else 0
        
        # Convertir restricción a one-hot encoding
        restriccion = item["restriccion"].lower()
        es_fragil = 1 if restriccion == "fragil" else 0
        es_frio = 1 if restriccion == "frio" else 0
        es_toxico = 1 if restriccion == "toxico" else 0
        es_inflamble = 1 if restriccion in ["inflamble", "inflamable"] else 0
        es_perecedero = 1 if restriccion == "perecedero" else 0
        
        # Convertir ventana horaria a one-hot encoding
        ventana = item["ventana_horaria"].lower()
        es_manana = 1 if ventana == "manana" else 0
        es_tarde = 1 if ventana == "tarde" else 0
        es_noche = 1 if ventana == "noche" else 0
        
        # Armar array de features
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
        y.append(item["prioridad"])  # "Alta", "Media" o "Baja"
    
    return np.array(X), np.array(y)

# ============================================
# Entrenar y guardar modelo
# ============================================
def entrenar_modelo():
    """
    Pipeline completo de entrenamiento:
    1. Cargar datos
    2. Dividir en train/test
    3. Entrenar modelo
    4. Evaluar
    5. Guardar
    """
    print("=" * 50)
    print("ENTRENAMIENTO DEL MODELO DE PRIORIDAD")
    print("=" * 50)
    
    # 1. Cargar dataset
    print("\n1. Cargando dataset...")
    X, y = cargar_dataset()
    print(f"   Dataset cargado: {len(X)} muestras")
    print(f"   Features: {X.shape[1]}")
    print(f"   Clases: {np.unique(y)}")
    
    # 2. Ver distribución de clases
    print("\n2. Distribución de clases:")
    for clase in np.unique(y):
        count = np.sum(y == clase)
        print(f"   {clase}: {count} ({count/len(y)*100:.1f}%)")
    
    # 3. Dividir datos: 80% entrenamiento, 20% prueba
    # stratify=y asegura que haya mismo porcentaje de cada clase en ambos grupos
    print("\n3. Dividiendo datos (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,      # 20% para test
        random_state=42,     # Semilla para reproducibilidad
        stratify=y           # Mantener proporción de clases
    )
    print(f"   Train: {len(X_train)} | Test: {len(X_test)}")
    
    # 4. Crear y entrenar Random Forest
    print("\n4. Entrenando Random Forest...")
    modelo = RandomForestClassifier(
        n_estimators=100,    # 100 árboles
        max_depth=10,        # Profundidad máxima de cada árbol
        random_state=42,     # Semilla para reproducibilidad
        class_weight="balanced"  # Manejar clases desbalanceadas
    )
    modelo.fit(X_train, y_train)  # .fit() = entrenar
    print("   Modelo entrenado!")
    
    # 5. Evaluar modelo
    print("\n5. Evaluando modelo...")
    y_pred = modelo.predict(X_test)  # Predecir sobre datos de prueba
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n   Accuracy: {accuracy:.2%}")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("   Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # 6. Guardar modelo
    print("\n6. Guardando modelo...")
    MODELOS_DIR.mkdir(exist_ok=True)
    modelo_path = MODELOS_DIR / "modelo_prioridad.pkl"
    
    with open(modelo_path, "wb") as f:  # "wb" = write binary
        pickle.dump(modelo, f)
    
    print(f"   Modelo guardado en: {modelo_path}")
    print("\n" + "=" * 50)
    print("ENTRENAMIENTO COMPLETADO")
    print("=" * 50)
    
    return modelo

# Ejecutar si se llama directamente
if __name__ == "__main__":
    entrenar_modelo()
```

---

## 6. Tests

### 6.1 Configuración de Tests (`tests/conftest.py`)

```python
import sys
from pathlib import Path

# Agregar el directorio padre al path de Python
# Esto permite importar módulos de src/
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

### 6.2 Tests de Envíos (`tests/test_envios.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from src.main import app
from src.routers.deps.db_sessions import get_db

# ============================================
# Fixture: Crear base de datos en memoria
# ============================================
@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una base de datos SQLite en memoria para cada test.
    Se reinicia completamente antes de cada test.
    """
    # create_engine: crea conexión
    # StaticPool: reutiliza una sola conexión
    # sqlite://: base de datos en memoria (no crea archivo)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Crear todas las tablas
    SQLModel.metadata.create_all(engine)
    
    # Yield: devuelve la sesión, luego la cleanup después del test
    with Session(engine) as session:
        yield session

# ============================================
# Fixture: Cliente de tests
# ============================================
@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Crea un cliente FastAPI que usa la BD en memoria.
    """
    def get_session_override():
        return session
    
    # Sobrescribir la dependencia get_db con nuestra sesión de test
    app.dependency_overrides[get_db] = get_session_override
    
    client = TestClient(app)
    yield client
    
    # Limpiar sobrescrituras después del test
    app.dependency_overrides.clear()

# ============================================
# Test: Health check
# ============================================
def test_health_check(client: TestClient):
    """
    Verifica que el endpoint /health funcione.
    """
    response = client.get("/health")
    assert response.status_code == 200  # ¿Código 200?
    assert response.json() == {"status": "healthy"}  # ¿Respuesta correcta?

# ============================================
# Test: Crear envío
# ============================================
def test_crear_envio(client: TestClient):
    """
    Verifica que se puede crear un envío correctamente.
    """
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 100.0,
        "creado_por_usuario_id": 1,
    }
    
    response = client.post("/envios/", json=datos)
    
    assert response.status_code == 201  # ¿Creado?
    data = response.json()
    assert data["remitente_id"] == 1  # ¿Datos correctos?
    assert data["estado"] == "Pendiente"  # ¿Estado inicial?
    assert "tracking_id" in data  # ¿Se generó ID?
    assert "prioridad" in data    # ¿Se asignó prioridad?

# ============================================
# Test: Listar envíos
# ============================================
def test_listar_envios(client: TestClient):
    """
    Verifica que se pueden listar los envíos.
    """
    response = client.get("/envios/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # ¿Devuelve lista?

# ============================================
# Test: Obtener envío inexistente
# ============================================
def test_obtener_envio_inexistente(client: TestClient):
    """
    Verifica que devuelve 404 si el envío no existe.
    """
    response = client.get("/envios/9999")
    assert response.status_code == 404

# ============================================
# Test: Cambiar estado
# ============================================
def test_cambiar_estado(client: TestClient):
    """
    Verifica que se puede cambiar el estado de un envío.
    """
    # Primero crear un envío
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
    }
    crear = client.post("/envios/", json=datos)
    tracking_id = crear.json()["tracking_id"]
    
    # Cambiar estado
    response = client.patch(
        f"/envios/{tracking_id}/estado?estado=En%20transito"
    )
    
    assert response.status_code == 200
    assert response.json()["estado"] == "En transito"
```

---

## 7. Métricas de ML Explicadas

### 7.1 Accuracy (Precisión Global)

```
Accuracy = (Predicciones Correctas) / (Total Predicciones)
```

**Ejemplo:**
- 36 predicciones totales
- 28 correctas
- Accuracy = 28/36 = 0.777 = 77.78%

**Interpretación:** El modelo acierta el 77.78% de las veces.

---

### 7.2 Precision (Precisión por Clase)

```
Precision = Verdaderos Positivos / (Verdaderos Positivos + Falsos Positivos)
```

**Para clase "Alta":**
- Predijo 14 como "Alta"
- De esos, 10 eran realmente "Alta" (VP)
- 4 eran otra clase (FP)
- Precision = 10/14 = 71%

**Interpretación:** De cada 14 veces que dice "Alta", 10 son correctas.

---

### 7.3 Recall (Exhaustividad por Clase)

```
Recall = Verdaderos Positivos / (Verdaderos Positivos + Falsos Negativos)
```

**Para clase "Alta":**
- Había 12 "Alta" reales
- Detectó 10 como "Alta" (VP)
- No detectó 2 (FN)
- Recall = 10/12 = 83%

**Interpretación:** De cada 12 "Alta" reales, detecta 10.

---

### 7.4 F1-Score

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Para clase "Alta":**
- Precision = 0.71
- Recall = 0.83
- F1 = 2 × (0.71 × 0.83) / (0.71 + 0.83)
- F1 = 1.18 / 1.54 = 0.77 = 77%

**Interpretación:** Combina precision y recall en un solo número.

---

### 7.5 Confusion Matrix (Matriz de Confusión)

```
                 Predicho
              Alta  Baja  Media
Real Alta    [ 10    0     2 ]
Real Baja    [  0   12     0 ]
Real Media   [  4    2     6 ]
```

**Interpretación:**
- **Diagonal principal (10, 12, 6):** Acertó
- **Fuera de diagonal:** Errores

**Errores específicos:**
- 2 "Alta" se predijeron como "Media"
- 4 "Media" se predijeron como "Alta"
- 2 "Media" se predijeron como "Baja"

---

### 7.6 Random Forest (Cómo funciona)

```
¿Qué es?

Random Forest = "Bosque Aleatorio"

Es un conjunto de muchos árboles de decisión que votan.
El resultado final es la mayoría de votos.

¿Cómo votan los árboles?

1. Cada árbol ve datos ligeramente diferentes (muestreo)
2. Cada árbol toma sus propias decisiones
3. El resultado es lo que majority de árboles voted

¿Por qué es robusto?

- Individualmente pueden cometer errores
- Pero juntos (en mayoría) son muy precisos
- No se sobreajustan fácilmente
```

---

## Comandos Útiles

```bash
# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux)
python -m venv . venv

# Instalar dependencias
pip install -r requirements.txt

# Entrenar modelo de ML
python -m src.ml.entrenar_modelo

# Ejecutar servidor
fastapi dev src/main.py

# Ejecutar tests
pytest tests/ -v

# Ejecutar linter
ruff check .

# Ver documentación Swagger
# Abrir http://localhost:8000/docs
```

## Flujo Completo de la Aplicación

```
1. Usuario crea envío (POST /envios/)
          ↓
2. FastAPI valida los datos (CrearEnvio)
          ↓
3. Se crea objeto Envio en memoria
          ↓
4. Se llama a predecir_prioridad(envio)
          ↓
5. _obtener_features() convierte a números
          ↓
6. Random Forest predice: Alta/Media/Baja
          ↓
7. Se guarda en MySQL con prioridad asignada
          ↓
8. Se devuelve respuesta al usuario
```

---

**Documento creado para estudio - LogiTrack 2026**
