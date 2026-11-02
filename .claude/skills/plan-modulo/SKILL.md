---
name: plan-modulo
description: Escribir y ejecutar el plan.md de un módulo del proyecto EGM (tareas trazadas a requisitos, pruebas primero, definición de terminado). Usar al crear un plan en docs/planes/<modulo>/ y al implementar un módulo a partir de su plan.
---

# Planes por módulo

## Precondiciones

- Specs aprobados y `docs/arquitectura/arquitectura.md` aprobado con la lista de módulos.
- Un plan por módulo de la arquitectura: `docs/planes/<modulo>/plan.md`, desde
  `docs/planes/_plantilla-plan.md`. No inventar módulos que la arquitectura no define.

## Reglas del plan

1. **Alcance cerrado**: lista de requisitos (FR/NFR/SC) que el módulo satisface, tomada de
   `trazabilidad.md`. Lo que no está ahí no se implementa.
2. **Pruebas primero**: la sección de pruebas se escribe antes de las tareas de implementación; cada
   prueba cita su escenario `US-…` o criterio `SC-…` y su fixture.
3. **Tareas atómicas** `T-<modulo>-<nn>`: verbo + resultado verificable + requisitos + archivos.
   Una tarea cabe en una sesión de trabajo y deja las pruebas en verde.
4. **Dependencias explícitas** entre módulos (qué interfaz consume y de quién).
5. **Riesgos y decisiones abiertas** con referencia a ADR o `[NEEDS CLARIFICATION]`.
6. **Definición de terminado** común (en la plantilla) más lo propio del módulo.

## Ejecución (subagente `implementador`)

1. Leer el plan, los specs citados y `contrato-matriz`.
2. Escribir las pruebas de la tarea; verificar que fallan.
3. Implementar lo mínimo para pasarlas; respetar `calidad-python`.
4. Marcar la tarea `[x]` en el plan y actualizar la columna *Tarea/Prueba* de `trazabilidad.md`.
5. Al terminar el módulo: pedir verificación al subagente `verificador`. No marcar el módulo como
   terminado con hallazgos abiertos.

Si una tarea exige algo fuera del plan: detenerse y reportarlo; no ampliar el alcance por iniciativa propia.
