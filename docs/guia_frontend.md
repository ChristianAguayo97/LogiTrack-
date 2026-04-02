## Comandos para el front end

```bash
# Comprobar version node y npm (requiere instalar node.js en tu computadora)
node -v
npm -v

# Crear entorno vite en la carpeta "frontend"
npm create vite@latest frontend
# Pasos: Select a framework: React | Select a variant: JavaScript | Install with npm and start now? Yes

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