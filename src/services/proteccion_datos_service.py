import re


def enmascarar_dni(dni: str) -> str:
    if not dni or len(dni) < 4:
        return "****"
    return dni[:2] + "****" + dni[-2:]


def enmascarar_email(email: str) -> str:
    if not email or "@" not in email:
        return "****@****.***"
    partes = email.split("@")
    usuario = partes[0]
    dominio = partes[1] if len(partes) > 1 else ""
    if len(usuario) <= 2:
        return usuario[0] + "***@" + dominio
    return usuario[:2] + "***@" + dominio


def enmascarar_id(id_valor) -> str:
    return "****"


def enmascarar_telefono(telefono: str) -> str:
    if not telefono or len(telefono) < 4:
        return "****"
    return "***" + telefono[-4:]


def enmascarar_datos_personales(datos: dict) -> dict:
    datos_enmascarados = datos.copy()
    campos_sensibles = ["dni", "documento", "nro_documento", "telefono", "telefono_contacto", "remitente_id", "destinatario_id"]
    
    for campo in campos_sensibles:
        if campo in datos_enmascarados and datos_enmascarados[campo]:
            if campo in ["dni", "documento", "nro_documento"]:
                datos_enmascarados[campo] = enmascarar_dni(str(datos_enmascarados[campo]))
            elif campo in ["remitente_id", "destinatario_id"]:
                datos_enmascarados[campo] = enmascarar_id(datos_enmascarados[campo])
            else:
                datos_enmascarados[campo] = enmascarar_telefono(str(datos_enmascarados[campo]))
    
    if "email" in datos_enmascarados and datos_enmascarados["email"]:
        datos_enmascarados["email"] = enmascarar_email(datos_enmascarados["email"])
    
    return datos_enmascarados
