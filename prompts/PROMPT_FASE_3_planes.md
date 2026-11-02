# Prompt para Claude Code — Fase 3: planes por módulo

> Usar solo con la arquitectura aprobada.

---

Lee `CLAUDE.md`, `docs/arquitectura/arquitectura.md` y la skill `plan-modulo`. Vas a ejecutar la
**Fase 3**: un `docs/planes/<modulo>/plan.md` por cada módulo de la lista cerrada de la arquitectura,
desde `docs/planes/_plantilla-plan.md`. No escribas código.

## Reglas
- Un plan por módulo; ningún módulo que la arquitectura no defina.
- La sección de pruebas va completa antes que las tareas; cada prueba cita su escenario o criterio y
  su fixture.
- Incluye un plan para el **constructor de fixtures** (`tests/fixtures_builder.py`) con un fixture por
  caso borde de `contrato-datos.md`; los demás planes dependen de él.
- Orden sugerido de ejecución en `docs/planes/README.md`, según dependencias.
- Actualiza la columna «Tarea» de `trazabilidad.md`.
- Cierra con el subagente `verificador` (fase planes) y `docs/informes/fase-3-resumen.md`.

Al terminar, **detente** y muéstrame el orden de ejecución propuesto.

---

## Fase 4 (referencia): implementación de un módulo

```
Lee CLAUDE.md. Con el subagente `implementador`, ejecuta docs/planes/<modulo>/plan.md tarea por tarea
(pruebas primero). Las vistas las hace `disenador-front`. Al terminar, audita con `verificador` y
muéstrame su informe. No empieces otro módulo.
```
