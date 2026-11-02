---
name: trazabilidad
description: Mantener y auditar la matriz de trazabilidad fuente → requisito → componente → tarea → prueba del proyecto EGM, y emitir informes de conformidad. Usar al cerrar cualquier fase, al revisar arquitectura o planes contra los specs, y antes de dar un módulo por terminado.
---

# Trazabilidad y conformidad

## Archivo

`docs/specs/trazabilidad.md`, una tabla única:

| Requisito | Fuente | Componente (ADR/arquitectura) | Tarea (plan) | Prueba | Estado |
|---|---|---|---|---|---|
| FR-001-03 | Instrucciones B20 | `lectura` | T-lectura-04 | `tests/unit/test_conteo.py::test_inclusion` | verificado |

Estados: `especificado` → `diseñado` → `planificado` → `implementado` → `verificado`.
Cada fase llena su columna; ninguna fase borra lo de la anterior.

## Comprobaciones por fase

**Fase specs**
- Todo FR/NFR tiene fuente (skill `especificacion-srs`).
- Todo FR está cubierto por al menos un escenario o SC.

**Fase arquitectura**
- Todo FR y NFR está asignado a al menos un componente.
- Todo componente cubre al menos un requisito (componente sin requisito = alcance no pedido: reportar).
- Cada ADR cita los requisitos que lo motivan.

**Fase planes**
- Toda tarea cita requisitos; todo requisito del módulo tiene tarea.
- Las pruebas derivadas de escenarios aparecen en el plan **antes** que las tareas de implementación.

**Fase código**
- Toda prueba cita en su docstring el ID del escenario/SC que comprueba.
- Los esperados de las pruebas salen de fixtures o de `referencia-v4.md`, nunca de la implementación.

## Informe de conformidad

Escribir `docs/informes/conformidad-<fase>-<AAAA-MM-DD>.md` con:

1. Resumen: requisitos totales, cubiertos, sin cubrir.
2. **Huecos**: requisitos sin componente, tarea o prueba.
3. **Excesos**: componentes, tareas o código sin requisito (posible ampliación de alcance).
4. **Contradicciones** entre specs, arquitectura y planes.
5. `[NEEDS CLARIFICATION]` abiertos.

Reportar hallazgos; no corregirlos dentro de la auditoría.
