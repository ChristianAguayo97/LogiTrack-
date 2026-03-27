# LogiTrack API - Grupo 7 📦

API desarrollada en Python con FastAPI para la gestión integral de envíos logísticos. Este proyecto es un incremento funcional y académico para la materia **Laboratorio de Construcción de Software**.

## 📁 Estructura del Repositorio

El proyecto sigue una estructura de directorios estándar para facilitar la mantenibilidad y la integración continua:

* `/docs`: Documentación técnica, matriz de trazabilidad y requerimientos.
* `/src`: Código fuente de la aplicación (modelos, rutas, servicios de IA y configuración de base de datos).
* `/tests`: Pruebas automatizadas (unitarias y de integración) utilizando `pytest`.
* `/models_ml`: Modelos de Machine Learning exportados para la asignación de prioridad de los paquetes.

---

## 🚀 Configuración y Despliegue Local

### Prerrequisitos
* Python 3.10 o superior.
* Git.

### Pasos de instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd LogiTrack-
   ```

2. **Crear y activar un entorno virtual:**
   Para crear el entorno virtual y mantener la terminal limpia sin que se muestre el usuario local de la máquina, podés definir el nombre del prompt:
   ```bash
   python -m venv venv --prompt="LogiTrack"
   ```
   
   Luego, activalo según tu sistema operativo:
   * **Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   * **Linux/macOS:**
     ```bash
     source venv/bin/activate
     ```

3. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Levantar el servidor de desarrollo:**
   ```bash
   uvicorn src.main:app --reload
   ```
   > **Nota:** Una vez que el servidor esté corriendo, podés acceder a la documentación interactiva (Swagger/OpenAPI) en `http://127.0.0.1:8000/docs`.

---

## 🧪 Ejecución de Pruebas (Testing)

El proyecto incluye un entorno de pruebas configurado con una base de datos SQLite en memoria (mock) para no afectar los datos reales. Para ejecutar la suite de pruebas completa:

```bash
pytest -v
```

---

## 🌿 Estrategia de Ramas (Branching)

Para mantener el orden y asegurar que la rama principal siempre sea estable, utilizamos un flujo de trabajo simplificado:

* **`main`**: Rama principal. Contiene el código estable, probado y listo para entregas. **No se pushea directamente a esta rama.**
* **`feature/<nombre-descriptivo>`**: Ramas temporales creadas a partir de `main` para desarrollar nuevas funcionalidades o tests (ej: `feature/alta-envios`).
* **`fix/<nombre-descriptivo>`**: Ramas para solucionar errores.

**Flujo de trabajo:** Se crea una rama `feature/`, se realizan los commits, se sube al repositorio remoto y se abre un **Pull Request (PR)** hacia `main`.

---

## 💬 Convención de Commits

Utilizamos Conventional Commits para tener un historial de cambios legible y trazable:

* `feat:` Para agregar una nueva funcionalidad.
* `test:` Para añadir o corregir pruebas automatizadas.
* `fix:` Para solucionar un error en el código.
* `docs:` Para cambios exclusivos en la documentación.
* `refactor:` Para reestructurar el código sin cambiar su comportamiento.

---

## ⚙️ Integración Continua (CI)

El repositorio cuenta con un pipeline de CI configurado mediante **GitHub Actions**.  
Cada vez que se realiza un `push` o se abre un `Pull Request` hacia la rama `main`, el pipeline ejecuta automáticamente:
1. La configuración del entorno con Python 3.10.
2. La instalación de dependencias.
3. La ejecución de todas las pruebas con `pytest`.