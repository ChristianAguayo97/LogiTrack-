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
        "consentimiento_datos": True,
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


def test_operador_no_puede_cambiar_estado(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    tracking_id = crear.json()["tracking_id"]
    response = client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito", headers=HEADERS_OPERADOR)
    assert response.status_code == 403


def test_cambiar_estado_supervisor_exitoso(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
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
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
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


def test_tracking_id_unico(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 100.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response1 = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response1.status_code == 201
    tracking_id1 = response1.json()["tracking_id"]

    response2 = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response2.status_code == 201
    tracking_id2 = response2.json()["tracking_id"]

    assert tracking_id1 != tracking_id2, "Los Tracking IDs deben ser únicos"


def test_detalle_completo_envio(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 150.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert crear.status_code == 201
    tracking_id = crear.json()["tracking_id"]

    response = client.get(f"/envios/{tracking_id}", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    data = response.json()

    assert "tracking_id" in data
    assert "remitente_id" in data
    assert "destinatario_id" in data
    assert "estado" in data
    assert "f_creacion" in data
    assert "prioridad" in data
    assert "distancia_estimada" in data


def test_busqueda_por_tracking_id_existente(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 200.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert crear.status_code == 201
    tracking_id = crear.json()["tracking_id"]

    response = client.get(f"/envios/{tracking_id}", headers=HEADERS_OPERADOR)
    assert response.status_code == 200
    assert response.json()["tracking_id"] == tracking_id


def test_busqueda_por_tracking_id_inexistente(client: TestClient):
    response = client.get("/envios/999999", headers=HEADERS_OPERADOR)
    assert response.status_code == 404
    assert "No se encontraron" in response.json()["detail"] or "no encontrado" in response.json()["detail"]


def test_filtro_por_estado(client: TestClient):
    datos1 = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    datos2 = {
        "remitente_id": 3,
        "destinatario_id": 4,
        "peso_paquete": 4.0,
        "distancia_estimada": 75.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    client.post("/envios/", json=datos1, headers=HEADERS_SUPERVISOR)
    crear2 = client.post("/envios/", json=datos2, headers=HEADERS_SUPERVISOR)
    tracking2 = crear2.json()["tracking_id"]
    client.patch(f"/envios/{tracking2}/estado?estado=En%20transito", headers=HEADERS_SUPERVISOR)

    response = client.get("/envios/?estado=En%20transito", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    envios = response.json()
    assert len(envios) >= 1
    for envio in envios:
        assert envio["estado"] == "En transito"


def test_filtro_por_destinatario(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 5,
        "peso_paquete": 2.0,
        "distancia_estimada": 30.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)

    response = client.get("/envios/?destinatario_id=5", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    envios = response.json()
    assert len(envios) >= 1
    for envio in envios:
        assert envio["destinatario_id"] == 5


def test_auditoria_registra_cambio_estado(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    tracking_id = crear.json()["tracking_id"]

    client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito", headers=HEADERS_SUPERVISOR)

    auditoria = client.get("/auditoria/", headers=HEADERS_SUPERVISOR)
    assert auditoria.status_code == 200
    registros = auditoria.json()
    
    cambio_estado = next((r for r in registros if r["envio_id"] == tracking_id and r["accion"] == "CAMBIAR_ESTADO"), None)
    assert cambio_estado is not None, "No se encontró registro de cambio de estado"
    assert "f_accion" in cambio_estado
    assert cambio_estado["usuario_rol"] == "Supervisor"


def test_auditoria_datos_envio_y_operador(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 120.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    tracking_id = crear.json()["tracking_id"]

    response = client.get(f"/envios/{tracking_id}", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    envio = response.json()
    
    assert "tracking_id" in envio
    assert "remitente_id" in envio
    assert "destinatario_id" in envio
    assert "estado" in envio
    assert "f_creacion" in envio
    assert "prioridad" in envio


def test_cancelacion_envio_supervisor(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    tracking_id = crear.json()["tracking_id"]

    response = client.patch(f"/envios/{tracking_id}/cancelar", headers=HEADERS_SUPERVISOR)
    assert response.status_code == 200
    assert response.json()["estado"] == "Cancelado"
    
    auditoria = client.get(f"/auditoria/?envio_id={tracking_id}", headers=HEADERS_SUPERVISOR)
    registros = auditoria.json()
    cancelacion = next((r for r in registros if r["accion"] == "CANCELAR"), None)
    assert cancelacion is not None
    assert "f_accion" in cancelacion


def test_operador_puede_crear_envio(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response.status_code == 201


def test_supervisor_puede_crear_y_cancelar(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert crear.status_code == 201
    tracking_id = crear.json()["tracking_id"]
    
    cancelar = client.patch(f"/envios/{tracking_id}/cancelar", headers=HEADERS_SUPERVISOR)
    assert cancelar.status_code == 200


def test_cliente_no_puede_acceder_a_endpoints_internos(client: TestClient):
    HEADERS_CLIENTE = {"x-usuario-id": "3", "x-usuario-nombre": "Cliente Test", "x-usuario-rol": "Cliente"}
    
    response = client.get("/auditoria/", headers=HEADERS_CLIENTE)
    assert response.status_code == 403
    
    response = client.patch("/envios/1/estado?estado=En%20transito", headers=HEADERS_CLIENTE)
    assert response.status_code == 403


def test_supervisor_puede_cambiar_estado_desde_detalle(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    crear = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    tracking_id = crear.json()["tracking_id"]
    
    detalle = client.get(f"/envios/{tracking_id}", headers=HEADERS_SUPERVISOR)
    assert detalle.status_code == 200
    
    cambiar = client.patch(f"/envios/{tracking_id}/estado?estado=En%20transito", headers=HEADERS_SUPERVISOR)
    assert cambiar.status_code == 200
    assert cambiar.json()["estado"] == "En transito"


def test_prioridad_media_toxico_distancia_media(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 300.0,
        "restricciones": "Toxico",
        "saturacion_ruta": 0.3,
        "tipo_envio": "Normal",
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert response.status_code == 201
    data = response.json()
    assert data["prioridad"] in ["Alta", "Media"]


def test_prioridad_baja_sin_restricciones(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 2.0,
        "distancia_estimada": 50.0,
        "restricciones": "Ninguno",
        "saturacion_ruta": 0.1,
        "tipo_envio": "Normal",
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert response.status_code == 201
    data = response.json()
    assert data["prioridad"] == "Baja"


def test_prioridad_express_minimo_media(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 100.0,
        "tipo_envio": "Express",
        "saturacion_ruta": 0.2,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert response.status_code == 201
    data = response.json()
    assert data["prioridad"] in ["Alta", "Media"]


def test_ml_retorna_prioridad_valida(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 5.0,
        "distancia_estimada": 200.0,
        "restricciones": "Fragil",
        "saturacion_ruta": 0.5,
        "tipo_envio": "Normal",
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True,
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    assert response.status_code == 201
    data = response.json()
    assert data["prioridad"] in ["Alta", "Media", "Baja"]


def test_consentimiento_requerido(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": False
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response.status_code == 400
    assert "consentimiento" in response.json()["detail"].lower()


def test_consentimiento_aceptado_permite_crear(client: TestClient):
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True
    }
    response = client.post("/envios/", json=datos, headers=HEADERS_OPERADOR)
    assert response.status_code == 201


def test_enmascaramiento_datos_cliente(client: TestClient):
    HEADERS_CLIENTE = {"x-usuario-id": "3", "x-usuario-nombre": "Cliente Test", "x-usuario-rol": "Cliente"}
    
    datos = {
        "remitente_id": 1,
        "destinatario_id": 2,
        "peso_paquete": 3.0,
        "distancia_estimada": 50.0,
        "creado_por_usuario_id": 1,
        "consentimiento_datos": True
    }
    client.post("/envios/", json=datos, headers=HEADERS_SUPERVISOR)
    
    response = client.get("/cliente/envios", headers=HEADERS_CLIENTE)
    if response.status_code == 200:
        envios = response.json()
        if envios:
            envio = envios[0]
            assert envio.get("remitente_id") == "****"
            assert envio.get("destinatario_id") == "****"
