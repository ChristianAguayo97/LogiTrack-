import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from src.main import app
from src.routers.deps.db_sessions import get_db


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
    response = client.post("/envios/", json=datos)
    assert response.status_code == 201
    data = response.json()
    assert data["remitente_id"] == 1
    assert data["estado"] == "Pendiente"
    assert "tracking_id" in data


def test_listar_envios(client: TestClient):
    response = client.get("/envios/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_obtener_envio_inexistente(client: TestClient):
    response = client.get("/envios/9999")
    assert response.status_code == 404


def test_cambiar_estado(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
    }
    crear = client.post("/envios/", json=datos)
    tracking_id = crear.json()["tracking_id"]

    response = client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito")
    assert response.status_code == 200
    assert response.json()["estado"] == "En transito"
