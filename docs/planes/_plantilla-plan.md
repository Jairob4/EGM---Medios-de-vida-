# Plan del módulo: [NOMBRE]

**Creado**: [FECHA] · **Estado**: borrador | aprobado | en ejecución | terminado
**Arquitectura**: `docs/arquitectura/arquitectura.md` §[n] · **ADR relacionados**: [ADR-xxx]

## 1. Propósito

[Una o dos frases: qué responsabilidad tiene el módulo dentro de la arquitectura.]

## 2. Alcance (requisitos que satisface)

| Requisito | Resumen | Escenario / criterio que lo verifica |
|---|---|---|
| FR-xxx-nn | | US-xxx-n.m / SC-xxx-nn |

Fuera de alcance de este módulo: [lista]

## 3. Interfaces

- **Consume**: [módulo → contrato (tipos, funciones o endpoints)]
- **Expone**: [contrato público del módulo]

## 4. Pruebas (se escriben antes que el código)

| ID prueba | Tipo (unit / integración / propiedades / e2e) | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-[modulo]-01 | | US-xxx-n.m | `data/fixtures/...` | |

## 5. Tareas

- [ ] **T-[modulo]-01** — [verbo + resultado verificable]. Requisitos: [FR-…]. Pruebas: [P-…]. Archivos: [rutas].
- [ ] **T-[modulo]-02** — …

## 6. Dependencias

[Módulos o tareas que deben estar terminados antes.]

## 7. Riesgos y decisiones abiertas

- [Riesgo] → [mitigación] · [NEEDS CLARIFICATION: …]

## 8. Definición de terminado

- [ ] Todas las pruebas de §4 en verde; cobertura del módulo según `calidad-python`.
- [ ] Lint y tipado sin errores.
- [ ] `trazabilidad.md` actualizado (tarea y prueba por requisito).
- [ ] Ningún archivo de `data/raw/` ni `docs/fuentes/` modificado.
- [ ] Informe del `verificador` sin huecos ni excesos abiertos.
- [ ] [Criterios propios del módulo]
