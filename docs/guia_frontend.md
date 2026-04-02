## Comandos para el front end

```bash
# Comprobar version node y npm (requiere instalar node.js en tu computadora)
node -v
npm -v

# Crear entorno vite en la carpeta "frontend"
npm create vite@latest frontend
# Pasos: Select a framework: React | Select a variant: JavaScript | Install with npm and start now? Yes

# Instalar la dependencia react router (para manejar varias direcciones)
cd frontend
npm install react-router-dom

# Instalar los paquetes para el proyecto (hay que estar en la carpeta frontend)
cd frontend
npm install

# Iniciar la aplicacion
npm run dev


```
---

## Estructura de carpetas

frontend/
    node_modules        -> Todas las carpetas que necesitemos (administrada por vite y npm)
    public              -> allí es donde van los assets como imagenes, fuentes, videos o cualquier documento publico.
    src                 -> allí se encuentra el código fuente de la aplicación
        app.jsx         -> componente principal de la aplicacion
        package.json    -> scripts que se pueden ejecutar en vite y TODAS LAS DEPENDENCIAS instaladas
            actualmente tiene dos dependencias instaladas, (react para construir componentes y react dom para dibujar los componentes en el html)
            devDependencies son las dependencias usadas por nuestra computadora y no seran subidas a produccion
            


---

---

## Comandos Útiles para BACKEND

```bash
# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux)
python -m venv . venv

# Instalar dependencias
pip install -r requirements.txt

# Entrenar modelo de ML
python -m src.ml.entrenar_modelo

# Ejecutar servidor
fastapi dev src/main.py

# Ejecutar tests
pytest tests/ -v

# Ejecutar linter
ruff check .

# Ver documentación Swagger
# Abrir http://localhost:8000/docs
```

## Flujo Completo de la Aplicación

```
1. Usuario crea envío (POST /envios/)
          ↓
2. FastAPI valida los datos (CrearEnvio)
          ↓
3. Se crea objeto Envio en memoria
          ↓
4. Se llama a predecir_prioridad(envio)
          ↓
5. _obtener_features() convierte a números
          ↓
6. Random Forest predice: Alta/Media/Baja
          ↓
7. Se guarda en MySQL con prioridad asignada
          ↓
8. Se devuelve respuesta al usuario
```