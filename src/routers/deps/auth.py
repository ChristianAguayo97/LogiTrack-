from typing import Annotated
from fastapi import Depends, Header, HTTPException
from src.models.usuario import Usuario, Rol


def get_current_user(
    x_usuario_id: Annotated[int, Header()] = 1,
    x_usuario_nombre: Annotated[str, Header()] = "Usuario Demo",
    x_usuario_rol: Annotated[str, Header()] = "Operador",
) -> Usuario:
    return Usuario(
        id=x_usuario_id,
        nombre=x_usuario_nombre,
        email=f"{x_usuario_nombre.lower().replace(' ', '.')}@logitrack.com",
        rol=Rol(x_usuario_rol),
        activo=True,
    )


UsuarioDep = Annotated[Usuario, Depends(get_current_user)]


def requiere_supervisor(usuario: Usuario) -> None:
    if usuario.rol != Rol.SUPERVISOR:
        raise HTTPException(
            status_code=403,
            detail=f"Acceso denegado. Se requiere rol Supervisor. Rol actual: {usuario.rol.value}",
        )


def requiere_operador_o_supervisor(usuario: Usuario) -> None:
    if usuario.rol not in [Rol.OPERADOR, Rol.SUPERVISOR]:
        raise HTTPException(
            status_code=403,
            detail=f"Acceso denegado. Se requiere rol Operador o Supervisor. Rol actual: {usuario.rol.value}",
        )


def requiere_cliente(usuario: Usuario) -> None:
    if usuario.rol != Rol.CLIENTE:
        raise HTTPException(
            status_code=403,
            detail=f"Acceso denegado. Se requiere rol Cliente. Rol actual: {usuario.rol.value}",
        )
