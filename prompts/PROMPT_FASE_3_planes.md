# Prompt para Claude Code — Fase 3: planes por spec

> Usar solo con la arquitectura aprobada.

---

Lee `CLAUDE.md`, `docs/arquitectura/arquitectura.md` y la skill `plan-modulo`. Vas a ejecutar la
**Fase 3**: un `docs/planes/NNN-<feature>/plan.md` por cada spec de feature (001, 002 y 003), desde `docs/planes/_plantilla-plan-spec.md`. No escribas código.

## Reglas
- Un plan por spec; ninguna tarea sobre un módulo que la arquitectura no defina.
- En cada historia, las pruebas antes que su implementación; cada prueba cita su escenario o criterio y su fixture.
- El constructor de fixtures (`tests/fixtures_builder.py`), con un fixture por caso borde de `contrato-datos.md`, va en la fase de preparación del plan 001; los planes 002 y 003 dependen de él. Cada NFR-000 se asigna en «Requisitos que cubre este plan» a los planes cuyas historias afecta.
- Orden sugerido de ejecución en `docs/planes/README.md`, según dependencias.
- Actualiza la columna «Tarea» de `trazabilidad.md`.
- Cierra con el subagente `verificador` (fase planes) y `docs/informes/fase-3-resumen.md`.

Al terminar, **detente** y muéstrame el orden de ejecución propuesto.

---

## Fase 4 (referencia): implementación de un plan

```
Lee CLAUDE.md. Con el subagente `implementador`, ejecuta docs/planes/NNN-<feature>/plan.md tarea por tarea
(pruebas primero). Las vistas las hace `disenador-front`. Al terminar, audita con `verificador` y
muéstrame su informe. No empieces otro plan.
```
