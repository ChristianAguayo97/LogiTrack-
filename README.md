# LogiTrack

Sistema de gestión del ciclo de vida de envíos desarrollado en Python/FastAPI (backend) y JavaScript/React (frontend).

## Estructura

```
/docs       - Documentación
/frontend   - Interfaz visual
/src        - Código fuente
/models_ml  - Modelo de machine learning
/tests      - Pruebas unitarias
```

## Instalación

Requiere tener instalado Python 3.10, MySQL Community Server y Node.JS

```bash
# Activar entorno virtual (Windows)
.venv/Scripts/activate
# Activar entorno virtual (Linux)
python -m venv .venv
# Instalar dependencias del backend
pip install -r requirements.txt
# Instalar dependencias del frontend
npm install
```

## Ejecución

```bash
# Ejecutar el backend
fastapi dev src/main.py
# Ejecutar el frontend
npm run dev
```

## Tests

```bash
# Ejecutar pruebas unitarias del backend
pytest tests/
```
