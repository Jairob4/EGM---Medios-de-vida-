---
name: plan-modulo
description: Escribir y ejecutar el plan.md de un spec del proyecto EGM (tareas trazadas a requisitos, pruebas primero, definición de terminado). Usar al crear un plan en docs/planes/NNN-<feature>/ y al implementar a partir de su plan.
---

# Planes por spec

## Precondiciones

- Specs aprobados y `docs/arquitectura/arquitectura.md` aprobado con la lista de módulos.
- Un plan por spec de feature: `docs/planes/NNN-<feature>/plan.md`, desde `docs/planes/_plantilla-plan-spec.md` (decisión de Jairo, 21-nov-2026). Cada tarea indica los módulos de la arquitectura que toca; no inventar módulos que la arquitectura no define.

## Reglas del plan

1. **Alcance cerrado**: lista de requisitos (FR/NFR/SC) que el plan cubre, tomada del spec y de `trazabilidad.md`. Lo que no está ahí no se implementa.
2. **Pruebas primero**: en cada historia, las pruebas antes que su implementación; cada prueba cita su escenario `US-…` o criterio `SC-…` y su fixture. Las tareas de preparación y base van antes de las historias, como en la plantilla.
3. **Tareas atómicas** `T-NNN-nn`: verbo + resultado verificable + requisitos + archivos.
   Una tarea cabe en una sesión de trabajo y deja las pruebas en verde.
4. **Dependencias explícitas** con otros planes y módulos (qué interfaz consume y de quién).
5. **Riesgos y decisiones abiertas** con referencia a ADR o `[NEEDS CLARIFICATION]`.
6. **Definición de terminado** común (en la plantilla) más lo propio del plan.

## Ejecución (subagente `implementador`)

1. Leer el plan, los specs citados y `contrato-matriz`.
2. Escribir las pruebas de la tarea; verificar que fallan.
3. Implementar lo mínimo para pasarlas; respetar `calidad-python`.
4. Marcar la tarea `[x]` en el plan y actualizar la columna *Tarea/Prueba* de `trazabilidad.md`.
5. Al terminar el plan: pedir verificación al subagente `verificador`. No marcar el plan como terminado con hallazgos abiertos.

Si una tarea exige algo fuera del plan: detenerse y reportarlo; no ampliar el alcance por iniciativa propia.
