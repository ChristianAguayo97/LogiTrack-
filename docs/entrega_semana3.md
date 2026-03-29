# Entrega Semana 3 - LogiTrack

## Introducción

El presente documento corresponde a la entrega de la Semana 3 del proyecto LogiTrack para la materia Laboratorio de Construcción de Software.

Se presenta el incremento funcional mínimo alcanzado, consistente en una API REST construida con FastAPI, el modelo de Machine Learning integrado al flujo de creación de envíos, y un conjunto de pruebas automatizadas que validan el comportamiento del sistema.

---

## 1. Repositorio y estructura del proyecto

### 1.1 Estructura del proyecto

El repositorio respeta la estructura estándar indicada por la materia:

| Carpeta | Contenido |
|---------|-----------|
| `/docs` | Documentación técnica, guía de estudio y README. |
| `/src` | Código fuente: modelos, routers, servicios (IA, auditoría, protección de datos) y configuración de base de datos. |
| `/tests` | Pruebas automatizadas con pytest (unitarias e integración). |
| `/models_ml` | Modelo de Machine Learning exportado (archivo .pkl) utilizado para la priorización de envíos. |
| `/src/ml` | Script de entrenamiento del modelo y dataset. |
| `/.github/workflows` | Definición del pipeline de CI con GitHub Actions. |
| `README.md` | Instrucciones de instalación, despliegue local, estrategia de ramas y convención de commits. |
| `CONTRIBUTING.md` | Guía para contribuir al proyecto: cómo crear ramas, abrir Pull Requests y ejecutar tests. |
| `requirements.txt` | Dependencias de Python necesarias para ejecutar el proyecto. |

---

## 2. Estrategia de ramas (Branching)

Para mantener el orden y garantizar que la rama principal sea siempre estable, el equipo adoptó el siguiente flujo simplificado:

| Rama | Propósito |
|------|-----------|
| `main` | Rama principal. Contiene código estable, probado y listo para entregas. No se realiza push directo a esta rama. |
| `feature/<nombre>` | Ramas temporales creadas desde main para desarrollar nuevas funcionalidades. |
| `fix/<nombre>` | Ramas para corregir errores detectados en el código. |
| `docs/<nombre>` | Para cambios en la documentación. |
| `test/<nombre>` | Para añadir o corregir tests. |
| `refactor/<nombre>` | Cambio en el código que no añade funcionalidad ni arregla bugs. |
| `ci/<nombre>` | Para cambios en el pipeline de CI/CD. |

**Flujo de trabajo:** se crea una rama feature/ o fix/ a partir de main, se realizan los commits con la convención acordada, se sube al repositorio remoto y se abre un Pull Request (PR) hacia main. El PR requiere al menos una aprobación de otro miembro del equipo antes de fusionarse.

---

## 3. Convención de commits

El equipo utiliza Conventional Commits para mantener un historial de cambios legible y trazable. El formato es:

```
<tipo>: <descripción breve en infinitivo>
```

| Prefijo | Uso | Ejemplo |
|---------|-----|---------|
| `feat:` | Nueva funcionalidad | `feat: implementar alta de envío` |
| `test:` | Agregar o corregir pruebas automatizadas | `test: agregar test de tracking ID único` |
| `fix:` | Corrección de errores | `fix: corregir validación de consentimiento` |
| `docs:` | Cambios exclusivos en documentación | `docs: actualizar README con pasos de CI` |
| `refactor:` | Reestructuración sin cambio de comportamiento | `refactor: extraer lógica de prioridad a servicio` |
| `build:` | Cambios en build o dependencias | `build: agregar sqlite fallback` |
| `ci:` | Cambios en pipeline CI/CD | `ci: crear workflow de GitHub Actions` |

---

## 4. Pipeline de Integración Continua (CI)

El repositorio cuenta con un pipeline de CI configurado mediante GitHub Actions. El archivo de configuración se encuentra en `.github/workflows/python-app.yml`.

### 4.1 Disparadores

El pipeline se ejecuta automáticamente ante los siguientes eventos:

- Push a la rama main.
- Apertura o actualización de un Pull Request hacia main.

### 4.2 Pasos del pipeline

| # | Paso | Descripción |
|---|------|-------------|
| 1 | Checkout del código | Descarga el código del repositorio en el runner de Ubuntu. |
| 2 | Configurar Python 3.10 | Instala la versión de Python especificada usando actions/setup-python. |
| 3 | Instalar dependencias | Ejecuta `pip install -r requirements.txt` para instalar FastAPI, SQLModel, scikit-learn, pytest y el resto de librerías. |
| 4 | Entrenar modelo de IA | Ejecuta `python -m src.ml.entrenar_modelo` para generar el archivo modelo_prioridad.pkl antes de correr los tests. |
| 5 | Ejecutar tests con pytest | Corre la suite completa de pruebas automatizadas con `pytest -v`. El pipeline falla si algún test no pasa. |

El pipeline utiliza variables de entorno de base de datos simuladas (fake credentials) para que el módulo de conexión no lance excepciones durante los tests, ya que estos usan una base de datos SQLite en memoria que no requiere MySQL real.

---

## 5. Incremento Funcional

El incremento implementado es una API REST construida con FastAPI y SQLModel, que cubre las funcionalidades core del MVP: gestión de envíos, control de roles, auditoría y priorización automática mediante Machine Learning.

### 5.1 API REST de gestión de envíos

| Método | Ruta | Rol requerido | Descripción |
|--------|------|---------------|-------------|
| POST | `/envios/` | Operador / Supervisor | Crear un nuevo envío. Valida consentimiento, genera tracking ID y asigna prioridad mediante ML. |
| GET | `/envios/` | Cualquiera autenticado | Listar envíos con filtros opcionales por estado, destinatario_id o remitente_id. |
| GET | `/envios/{tracking_id}` | Cualquiera autenticado | Obtener el detalle completo de un envío por tracking ID. |
| PATCH | `/envios/{tracking_id}` | Operador / Supervisor | Actualizar datos del envío. Recalcula prioridad y registra auditoría. |
| PATCH | `/envios/{tracking_id}/estado` | Supervisor | Cambiar el estado del envío. Solo disponible para Supervisores. Registra en bitácora de auditoría. |
| PATCH | `/envios/{tracking_id}/cancelar` | Supervisor | Cancelar un envío. Registra timestamp y usuario en auditoría. |
| GET | `/auditoria/` | Supervisor | Listar todos los registros de auditoría. Bitácora inmutable de acciones. |
| GET | `/cliente/envios` | Cliente | Vista pública de envíos con datos personales enmascarados (protección Ley 25.326). |
| GET | `/health` | Público | Health check del servicio. |

### 5.2 Control de roles

La autenticación es simulada (mock) mediante headers HTTP: `x-usuario-id`, `x-usuario-nombre` y `x-usuario-rol`. Existen tres roles definidos:

- **Operador**: puede crear y consultar envíos.
- **Supervisor**: puede hacer todo lo anterior más cambiar estados, cancelar envíos y consultar auditoría.
- **Cliente**: accede únicamente al endpoint público con datos enmascarados.

### 5.3 Modelo de Machine Learning (priorización)

El modelo de clasificación utiliza el algoritmo Random Forest (scikit-learn) entrenado sobre el dataset generado en la Entrega 2. Se exporta como archivo .pkl y se carga en tiempo de ejecución para predecir la prioridad de cada envío al momento de crearlo o actualizarlo.

**Features utilizadas como entrada del modelo:**

- Distancia estimada (float, en km)
- Peso del paquete (float, en kg)
- Restricciones (frágil, frío, tóxico, inflamable, perecedero, ninguno) — codificadas como variables binarias
- Saturación de ruta (float, entre 0 y 1)
- Tipo de envío (Normal / Express) — codificado como binario
- Ventana horaria (mañana / tarde / noche) — codificada como variables binarias

El modelo predice una de tres categorías: Alta, Media o Baja prioridad. Si el archivo .pkl no existe al iniciar, se aplica una función de prioridad por defecto basada en reglas simples (fallback).

El entrenamiento del modelo se realiza como paso explícito del pipeline de CI (paso 4), asegurando que la integración continua siempre trabaje con un modelo actualizado.

---

## 6. Matriz de Trazabilidad

### 6.1 Ramas utilizadas en el proyecto

| Rama | Tipo | Contenido |
|------|------|-----------|
| `main` | main | Estado final del proyecto (documentación) |
| `feature/nueva-funcionalidad` | feature | Estructura inicial del proyecto + features |
| `fix/arreglo-base` | fix | Fix en método que lista los envíos |
| `test/pruebas` | test | Tests de prioridad IA + datos incompletos |
| `docs/documentacion` | docs | Readme original |
| `refactor/refactorizacion` | refactor | SQLite fallback (sin server MySQL) |
| `ci/pipeline` | ci | Workflow GitHub Actions |

### 6.2 Matriz Historia ↔ Caso de Prueba ↔ Rama ↔ Commit

| HU | Historia de Usuario | TC | Caso de Prueba | Función de test | Rama | Commit referencial |
|----|---------------------|-----|----------------|-----------------|------|-------------------|
| HU01 | Alta de envío | TC01 | Alta de envío exitosa | test_crear_envio | feature/nueva-funcionalidad | a0ccc1c |
| HU01 | Alta de envío | TC02 | Alta con campos incompletos | test_alta_envio_incompleto | feature/nueva-funcionalidad | a0ccc1c |
| HU01 | Alta de envío | TC03 | Tracking ID único | test_tracking_id_unico | feature/nueva-funcionalidad | a0ccc1c |
| HU02 | Listado de envíos | TC04 | Listado de envíos | test_listar_envios | fix/arreglo-base | 4166235 |
| HU03 | Detalle de envío | TC05 | Detalle completo del envío | test_detalle_completo_envio | feature/nueva-funcionalidad | a0ccc1c |
| HU04 | Búsqueda por tracking ID | TC06 | Búsqueda existente | test_busqueda_por_tracking_id_existente | feature/nueva-funcionalidad | a0ccc1c |
| HU04 | Búsqueda por tracking ID | TC07 | Búsqueda inexistente | test_busqueda_por_tracking_id_inexistente | feature/nueva-funcionalidad | a0ccc1c |
| HU05 | Filtro por destinatario | TC08 | Filtro por destinatario | test_filtro_por_destinatario | feature/nueva-funcionalidad | a0ccc1c |
| HU06 | Cambio de estado | TC09 | Cambio de estado exitoso (Supervisor) | test_cambiar_estado_supervisor_exitoso | feature/nueva-funcionalidad | a0ccc1c |
| HU17 | Restricción por rol | TC10 | Operador no puede cambiar estado | test_operador_no_puede_cambiar_estado | feature/nueva-funcionalidad | a0ccc1c |
| HU22 | Auditoría de estado | TC11 | Auditoría registra cambio de estado | test_auditoria_registra_cambio_estado | feature/nueva-funcionalidad | a0ccc1c |
| HU07 | Auditoría de envíos | TC12 | Auditoría datos envío y operador | test_auditoria_datos_envio_y_operador | feature/nueva-funcionalidad | a0ccc1c |
| HU08 | Cancelación de envío | TC13 | Cancelación con auditoría | test_cancelacion_envio_supervisor | feature/nueva-funcionalidad | a0ccc1c |
| HU23 | Login / control acceso | TC14 | Operador puede crear envío (rol) | test_operador_puede_crear_envio | feature/nueva-funcionalidad | a0ccc1c |
| HU24 | Funciones del supervisor | TC16 | Supervisor cambia estado desde detalle | test_supervisor_puede_cambiar_estado_desde_detalle | feature/nueva-funcionalidad | a0ccc1c |
| HU10 | Priorización IA | TC18 | Clasificación Alta prioridad | test_prioridad_alta_ml | test/pruebas | f054974 |
| HU10 | Priorización IA | TC19 | Clasificación Media prioridad | test_prioridad_media_toxico_distancia_media | test/pruebas | f054974 |
| HU10 | Priorización IA | TC20 | Clasificación Baja prioridad | test_prioridad_baja_sin_restricciones | test/pruebas | f054974 |
| HU10 | Priorización IA | TC21 | Express mínimo Media | test_prioridad_express_minimo_media | test/pruebas | f054974 |
| HU10 | Priorización IA | TC22 | ML retorna prioridad válida (sin null) | test_ml_retorna_prioridad_valida | test/pruebas | f054974 |
| HU26 | Consentimiento (Ley 25.326) | TC23 | Consentimiento requerido | test_consentimiento_requerido | feature/nueva-funcionalidad | a0ccc1c |

---

## 7. Documentación automática (Swagger/OpenAPI)

FastAPI genera documentación interactiva automáticamente. Con el servidor levantado localmente, se puede acceder a:

- `http://127.0.0.1:8000/docs` — Interfaz Swagger UI para explorar y probar todos los endpoints.
- `http://127.0.0.1:8000/redoc` — Documentación alternativa en formato ReDoc.

---

## 8. Notas adicionales

- La rama `test/pruebas` contiene los tests de priorización con Machine Learning, validando que el modelo retorne siempre una categoría válida (Alta, Media o Baja).
- La rama `refactor/refactorizacion` implementa el fallback de SQLite para entornos donde no hay acceso a MySQL, permitiendo que los tests se ejecuten sin base de datos externa.
- La rama `ci/pipeline` contiene la configuración del workflow de GitHub Actions que entrena el modelo y ejecuta los tests automáticamente en cada push a main.
