from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from src.models.envio import Envio, MostrarEnvio
from src.models.usuario import Rol
from src.routers.deps.db_sessions import SessionDep
from src.routers.deps.auth import UsuarioDep, requiere_cliente
from src.services.proteccion_datos_service import enmascarar_datos_personales


envio_cliente_router = APIRouter(prefix="/cliente", tags=["Cliente"])


@envio_cliente_router.get("/envios", response_model=list[dict])
def listar_envios_cliente(
    session: SessionDep,
    usuario: UsuarioDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    requiere_cliente(usuario)
    query = select(Envio).where(
        (Envio.remitente_id == usuario.id) | (Envio.destinatario_id == usuario.id)
    )
    envios = session.exec(query.offset(skip).limit(limit)).all()
    
    envios_dict = []
    for envio in envios:
        datos = {
            "tracking_id": envio.tracking_id,
            "estado": envio.estado.value,
            "prioridad": envio.prioridad.value if envio.prioridad else None,
            "tipo_envio": envio.tipo_envio.value,
            "peso_paquete": envio.peso_paquete,
            "distancia_estimada": envio.distancia_estimada,
            "restricciones": envio.restricciones.value,
            "ventana_horario": envio.ventana_horario.value,
            "f_creacion": envio.f_creacion.isoformat(),
            "f_actualizacion": envio.f_actualizacion.isoformat(),
            "remitente_id": envio.remitente_id,
            "destinatario_id": envio.destinatario_id,
        }
        if usuario.rol == Rol.CLIENTE:
            datos_protegidos = enmascarar_datos_personales(datos)
            envios_dict.append(datos_protegidos)
        else:
            envios_dict.append(datos)
    
    return envios_dict


@envio_cliente_router.get("/envios/{tracking_id}", response_model=dict)
def ver_envio_cliente(
    tracking_id: int,
    session: SessionDep,
    usuario: UsuarioDep,
):
    requiere_cliente(usuario)
    envio = session.get(Envio, tracking_id)
    if not envio:
        raise HTTPException(status_code=404, detail="Envío no encontrado")
    
    if envio.remitente_id != usuario.id and envio.destinatario_id != usuario.id:
        raise HTTPException(status_code=403, detail="No tenés acceso a este envío")
    
    datos = {
        "tracking_id": envio.tracking_id,
        "estado": envio.estado.value,
        "prioridad": envio.prioridad.value if envio.prioridad else None,
        "tipo_envio": envio.tipo_envio.value,
        "peso_paquete": envio.peso_paquete,
        "distancia_estimada": envio.distancia_estimada,
        "restricciones": envio.restricciones.value,
        "ventana_horario": envio.ventana_horario.value,
        "f_creacion": envio.f_creacion.isoformat(),
        "f_actualizacion": envio.f_actualizacion.isoformat(),
        "remitente_id": envio.remitente_id,
        "destinatario_id": envio.destinatario_id,
    }
    
    return enmascarar_datos_personales(datos)
