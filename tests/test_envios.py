import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from src.main import app
from src.routers.deps.db_sessions import get_db


HEADERS_OPERADOR = {"x-usuario-id": "1", "x-usuario-nombre": "Operador Test", "x-usuario-rol": "Operador"}
HEADERS_SUPERVISOR = {"x-usuario-id": "2", "x-usuario-nombre": "Supervisor Test", "x-usuario-rol": "Supervisor"}


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_crear_envio(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 100.0,
        "creado_por_usuario_id": 1,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response.status_code == 201
    data = response.json()
    assert data["remitente_id"] == 1
    assert data["estado"] == "Pendiente"
    assert "tracking_id" in data


def test_listar_envios(client: TestClient):
    response = client.get("/envios/", headers=HEADERS_OPERADOR)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_obtener_envio_inexistente(client: TestClient):
    response = client.get("/envios/9999", headers=HEADERS_OPERADOR)
    assert response.status_code == 404


def test_cambiar_estado_operador_exitoso(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    tracking_id = crear.json()["tracking_id"]
    response = client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito", headers=HEADERS_OPERADOR)
    assert response.status_code == 200
    assert response.json()["estado"] == "En transito"


def test_cambiar_estado_supervisor_exitoso(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    tracking_id = crear.json()["tracking_id"]
    response = client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    assert response.json()["estado"] == "En transito"


def test_alta_envio_incompleto(client: TestClient):
    datos_incompletos = {"remitente_id": 1}
    response = client.post("/envios/", json=datos_incompletos, headers=HEADERS_OPERADOR)
    assert response.status_code == 422


def test_prioridad_alta_ml(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 64.7,
        "distancia_estimada": 909.6,
        "restricciones": "Inflamable",
        "saturacion_ruta": 0.46,
        "tipo_envio": "Express",
        "ventana_horario": "Tarde",
        "creado_por_usuario_id": 1
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert response.status_code == 201
    data = response.json()
    assert data["prioridad"] == "Alta"


def test_auditoria_requiere_supervisor(client: TestClient):
    response = client.get("/auditoria/", headers=HEADERS_OPERADOR)
    assert response.status_code == 403


def test_auditoria_listar_como_supervisor(client: TestClient):
    response = client.get("/auditoria/", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
