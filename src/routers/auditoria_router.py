from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from src.models.usuario import Auditoria, Rol
from src.routers.deps.db_sessions import SessionDep
from src.routers.deps.auth import UsuarioDep, requiere_supervisor


auditoria_router = APIRouter(prefix="/auditoria", tags=["Auditoría"])


@auditoria_router.get("/")
def listar_auditoria(
    session: SessionDep,
    usuario: UsuarioDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    envio_id: int | None = None,
):
    requiere_supervisor(usuario)
    query = select(Auditoria)
    if envio_id:
        query = query.where(Auditoria.envio_id == envio_id)
    query = query.order_by(Auditoria.f_accion.desc())
    registros = session.exec(query.offset(skip).limit(limit)).all()
    return registros


@auditoria_router.get("/usuarios/{usuario_id}")
def auditoria_por_usuario(
    usuario_id: int,
    session: SessionDep,
    usuario: UsuarioDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    requiere_supervisor(usuario)
    query = select(Auditoria).where(Auditoria.usuario_id == usuario_id)
    query = query.order_by(Auditoria.f_accion.desc())
    registros = session.exec(query.offset(skip).limit(limit)).all()
    return registros
