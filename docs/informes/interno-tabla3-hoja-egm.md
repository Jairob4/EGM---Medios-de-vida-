# Observación interna sobre la tabla 3 de la hoja EGM

> **Documento interno, para Jairo y el mantenedor.** Es un hallazgo del grupo B de la regla 9 de `CLAUDE.md`
> (decisión de Jairo, 21-nov-2026). No se comparte con el equipo ni se cita en la interfaz ni en ningún otro
> texto. Solo se comunica al equipo en la sección dirigida a él del informe final de fase, como nota del
> grupo B, cuando Jairo apruebe ese informe.
>
> **Origen.** Es el apéndice B de `docs/specs/contrato-datos.md` («Interna — no publicar»), trasladado íntegro y sin
> cambios por COR-010 (decisión de Jairo, 21-nov-2026, hallazgo H-69 de
> `docs/informes/conformidad-fase-1-cierre-2026-11-21.md`). En el texto trasladado, «este apéndice» designa este
> archivo, y «sección 6» y «sección 7, punto 6» son las secciones de `docs/specs/contrato-datos.md`. El contrato
> conserva solo lo que el comportamiento necesita: la tabla 3 no es comparable y no se lee ni se compara (§7,
> punto 7).

## Apéndice B. Interna — no publicar

> Información interna para Jairo y el mantenedor. Es un hallazgo del grupo B de la regla 9 de `CLAUDE.md`: nunca se menciona en la interfaz ni en ningún otro texto, y solo se comunica al equipo en la sección dirigida a él del informe final de fase, como nota del grupo B, cuando Jairo apruebe ese informe.

La tabla 3 de la hoja `EGM` aplica el criterio `"Sí*"` sobre `$M$2:$M$200` (columna «Humano», valores 1/0) en
lugar de la columna de enfoque de género/diferencial. Por eso vale 0 en todas sus celdas con cualquier dato que
respete la lista. Comprobado en B26 y J26 del archivo vigente. La nota A41 de la hoja describe el bloque en
términos de la columna de enfoque.

Consecuencias para la herramienta:

- Calcula el enfoque desde su columna (sección 6) y no necesita esa tabla para funcionar.
- La tabla queda fuera de las comparables de la sección 7, y la interfaz no muestra esa comparación
  (sección 7, punto 6).
- La discrepancia conocida queda en los registros internos del proyecto: este apéndice, los informes para Jairo y `docs/informes/hallazgos-matriz-para-equipo.md` (B-01). La herramienta no la calcula ni la anota en sus registros de ejecución, que no contienen datos de la matriz (`NFR-000-17`). `[Fuente: decisión de Jairo, 2-nov-2026, para «queda en registros internos» y para que los registros de ejecución no contengan datos de la matriz; doc. técnico §9.1, para «no la calcula», porque excluye esa tabla de la comparación; decisión de Jairo, 21-nov-2026, para el registro de hallazgos y la comunicación en el informe final.]`

Los N.º 2 y 7 se muestran «Sin clasificar», con la advertencia de la sección 6; nada más.
`[Fuente: decisión de Jairo, 2-nov-2026]`

Decidido: la discrepancia se comunica al equipo en el informe final de fase, como nota del grupo B. `[Fuente: decisión de Jairo, 21-nov-2026]`
