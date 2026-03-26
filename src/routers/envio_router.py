from fastapi import APIRouter, Query, HTTPException
from sqlmodel import select
from src.models.envio import Envio, CrearEnvio, ActualizarEnvio, MostrarEnvio
from src.models.enums import EstadoEnvio
from src.routers.deps.db_sessions import SessionDep
from src.services.prioridad_service import predecir_prioridad


envio_router = APIRouter(prefix="/envios", tags=["Envíos"])


@envio_router.post("/", response_model=MostrarEnvio, status_code=201)
def crear_envio(datos: CrearEnvio, session: SessionDep):
    envio = Envio.model_validate(datos)
    prioridad = predecir_prioridad(envio)
    envio.prioridad = prioridad
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio


@envio_router.get("/", response_model=list[MostrarEnvio])
def listar_envios(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: EstadoEnvio | None = None,
):
    query = select(Envio)
    if estado:
        query = query.where(Envio.estado == estado)
    envios = session.exec(query.offset(skip).limit(limit)).all()
    return envios


@envio_router.get("/{tracking_id}", response_model=MostrarEnvio)
def obtener_envio(tracking_id: int, session: SessionDep):
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@envio_router.patch("/{tracking_id}", response_model=MostrarEnvio)
def actualizar_envio(tracking_id: int, datos: ActualizarEnvio, session: SessionDep):
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    datos_dict = datos.model_dump(exclude_unset=True)
    for key, value in datos_dict.items():
        if value is not None and value != "":
            setattr(envio, key, value)
    prioridad = predecir_prioridad(envio)
    envio.prioridad = prioridad
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio


@envio_router.patch("/{tracking_id}/estado", response_model=MostrarEnvio)
def cambiar_estado(tracking_id: int, estado: EstadoEnvio, session: SessionDep):
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    envio.estado = estado
    session.add(envio)
    session.commit()
    session.refresh(envio)
    return envio
