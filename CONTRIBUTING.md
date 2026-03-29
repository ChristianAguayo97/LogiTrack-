# Contribución a LogiTrack

## Estrategia de Ramas

| Rama | Propósito |
|------|-----------|
| `main` | Código en producción |
| `fix/*` | Arreglos de bugs |
| `feature/*` | Nuevas funcionalidades |
| `docs/*` | Documentación |
| `test/*` | Pruebas unitarias |
| `refactor/*` | Refactorización de código |

### Flujo de Trabajo

1. Crear rama desde `main`: `git checkout -b feature/nueva-funcionalidad`
2. Trabajar en la rama y hacer commits siguiendo la convención
3. Push y crear Pull Request hacia `main`
4. Luego de aprobado, hacer merge a `main`

## Convención de Commits

Formato: `<tipo>[ámbito]: <descripción>`

### Tipos

| Tipo | Descripción |
|------|-------------|
| `feat` | Nueva funcionalidad |
| `fix` | Arreglo de bug |
| `docs` | Documentación |
| `style` | Formato/código sin lógica |
| `refactor` | Refactorización |
| `test` | Pruebas |
| `build` | Build/dependencias |
| `ci` | CI/CD |
| `chore` | Mantenimiento |

### Reglas

- Usar tiempo presente: "add" no "added"
- Mantener descripción bajo 72 caracteres
- Referenciar issues: `Closes #123`

### Ejemplos

```bash
git commit -m "feat: agregar módulo de usuarios"
git commit -m "fix: corregir error en listar envíos"
git commit -m "test: añadir pruebas de prioridad"
```

## Reglas Importantes

- **Nunca** commitear archivos sensibles (.env, credenciales)
- **Nunca** hacer force push a main
- Usar ramas temáticas para cada cambio
- Un cambio lógico por commit
