from src.models.usuario import Auditoria, Rol
from src.routers.deps.db_sessions import SessionDep


def registrar_auditoria(
    session: SessionDep,
    usuario_id: int,
    usuario_nombre: str,
    usuario_rol: Rol,
    envio_id: int,
    accion: str,
    detalle: str,
):
    auditoria = Auditoria(
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        usuario_rol=usuario_rol.value,
        envio_id=envio_id,
        accion=accion,
        detalle=detalle,
    )
    session.add(auditoria)
    session.commit()
