from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from src.models.envio import Envio, CrearEnvio, ActualizarEnvio, MostrarEnvio
from src.models.enums import EstadoEnvio
from src.routers.deps.db_sessions import SessionDep
from src.routers.deps.auth import UsuarioDep, requiere_supervisor, requiere_operador_o_supervisor
from src.services.prioridad_service import predecir_prioridad
from src.services.auditoria_service import registrar_auditoria


envio_router = APIRouter(prefix="/envios", tags=["Envíos"])


@envio_router.post("/", response_model=MostrarEnvio, status_code=201)
def crear_envio(datos: CrearEnvio, session: SessionDep, usuario: UsuarioDep):
    requiere_operador_o_supervisor(usuario)
    if not datos.consentimiento_datos:
        raise HTTPException(
            status_code=400,
            detail="Se requiere consentimiento para el tratamiento de datos personales (Ley 25.326, Art. 5)",
        )
    envio = Envio.model_validate(datos)
    prioridad = predecir_prioridad(envio)
    envio.prioridad = prioridad
    session.add(envio)
    session.commit()
    session.refresh(envio)
    registrar_auditoria(
        session=session,
        usuario_id=usuario.id,
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol,
        envio_id=envio.tracking_id,
        accion="CREAR",
        detalle=f"Envío creado con prioridad {prioridad.value}",
    )
    return envio


@envio_router.get("/", response_model=list[MostrarEnvio])
def listar_envios(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: EstadoEnvio | None = None,
    destinatario_id: int | None = None,
    remitente_id: int | None = None,
):
    query = select(Envio)
    if estado:
        query = query.where(Envio.estado == estado)
    if destinatario_id is not None:
        query = query.where(Envio.destinatario_id == destinatario_id)
    if remitente_id is not None:
        query = query.where(Envio.remitente_id == remitente_id)
    envios = session.exec(query.offset(skip).limit(limit)).all()
    return envios


@envio_router.get("/{tracking_id}", response_model=MostrarEnvio)
def obtener_envio(tracking_id: int, session: SessionDep, usuario: UsuarioDep):
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    return envio


@envio_router.patch("/{tracking_id}", response_model=MostrarEnvio)
def actualizar_envio(tracking_id: int, datos: ActualizarEnvio, session: SessionDep, usuario: UsuarioDep):
    requiere_operador_o_supervisor(usuario)
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
    registrar_auditoria(
        session=session,
        usuario_id=usuario.id,
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol,
        envio_id=envio.tracking_id,
        accion="ACTUALIZAR",
        detalle=f"Campos actualizados: {list(datos_dict.keys())}",
    )
    return envio


@envio_router.patch("/{tracking_id}/estado", response_model=MostrarEnvio)
def cambiar_estado(tracking_id: int, estado: EstadoEnvio, session: SessionDep, usuario: UsuarioDep):
    requiere_supervisor(usuario)
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    estado_anterior = envio.estado
    envio.estado = estado
    session.add(envio)
    session.commit()
    session.refresh(envio)
    registrar_auditoria(
        session=session,
        usuario_id=usuario.id,
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol,
        envio_id=envio.tracking_id,
        accion="CAMBIAR_ESTADO",
        detalle=f"Estado cambiado de '{estado_anterior.value}' a '{estado.value}'",
    )
    return envio


@envio_router.patch("/{tracking_id}/cancelar", response_model=MostrarEnvio)
def cancelar_envio(tracking_id: int, session: SessionDep, usuario: UsuarioDep):
    requiere_supervisor(usuario)
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    estado_anterior = envio.estado
    envio.estado = EstadoEnvio.CANCELADO
    session.add(envio)
    session.commit()
    session.refresh(envio)
    registrar_auditoria(
        session=session,
        usuario_id=usuario.id,
        usuario_nombre=usuario.nombre,
        usuario_rol=usuario.rol,
        envio_id=envio.tracking_id,
        accion="CANCELAR",
        detalle=f"Envío cancelado. Estado anterior: '{estado_anterior.value}'",
    )
    return envio
