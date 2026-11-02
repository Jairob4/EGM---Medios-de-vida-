# Prompt para Claude Code — Fase 2: arquitectura, ADR y flujos de interfaz

> Usar solo después de aprobar la fase 1 y resolver (o aceptar como abiertos) sus `[NEEDS CLARIFICATION]`.

---

Lee `CLAUDE.md` y `docs/informes/fase-1-resumen.md`. Vas a ejecutar la **Fase 2**. No escribas código
de la aplicación ni planes de módulo.

Decisiones de Jairo tomadas después de la fase 1 (completar antes de pegar):
- [Respuestas a los NEEDS CLARIFICATION de la fase 1]
- [Stack web, si ya lo decidió; si no, el ADR-003 lo propone]

## Tareas
1. **Subagente `arquitecto`**: `docs/arquitectura/arquitectura.md` y los ADR 001–004 descritos en su
   definición. Debe cerrar la **lista de módulos** con responsabilidad, interfaz pública y requisitos
   cubiertos, y llenar la columna «Componente» de `trazabilidad.md`.
2. **Subagente `disenador-front`** (después del arquitecto, sobre su lista de vistas): `flujos.md`,
   bocetos HTML de baja fidelidad con datos reales de la matriz y `tokens.css`.
3. **Subagente `verificador`**: auditoría de la fase de arquitectura (cobertura de FR/NFR, componentes
   sin requisito, coherencia entre flujos y historias).
4. Resumen en `docs/informes/fase-2-resumen.md`: módulos, ADR con su estado, decisiones abiertas.

Al terminar, **detente** y muéstrame el resumen y los bocetos.
