# EGM · Medios de vida — contexto permanente para Claude Code

## Qué es este proyecto

Aplicación web de **solo lectura** que lee la matriz bibliográfica del estado del arte del proyecto
«Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los medios de vida
de la población víctima en Colombia» (semillero Desarrollo Rural y Economía Solidaria, grupo GIOE,
Universidad del Magdalena) y presenta:

1. el mapa de evidencias y brechas (EGM) interactivo, al estilo del de 3ie;
2. un tablero analítico con conclusiones calculadas, cada una trazable hasta las filas de la matriz.

Autor de la herramienta: Jairo de Jesús Blanco Pérez (semillerista). El equipo de investigación
(investigadora principal Amanda Vargas Prieto; coinvestigadora Lina Martínez) es dueño de la matriz,
de las categorías y de la metodología.

## Reglas inviolables

1. **La matriz es del equipo y es de solo lectura.** Nunca escribir, guardar ni «corregir»
   `data/raw/`. Abrir siempre en modo lectura. Las pruebas usan `data/fixtures/`.
2. **No proponer cambios en el área del equipo** (matriz, columnas, listas, dimensiones, intervenciones,
   criterios, metodología). La herramienta se adapta a la matriz, no al revés.
3. **No afirmar lo que no se sabe.** Todo dato no verificado en `docs/fuentes/` o en la matriz se marca
   `[NEEDS CLARIFICATION: …]`. Nunca inventar fechas, responsables, códigos ni categorías.
4. **Cada número mostrado es trazable** a la lista de filas (N.º de la matriz) que lo producen.
5. **Brechas provisionales.** Una celda en 0 se comunica como «ningún estudio registrado», nunca como
   «no investigado».
6. **Conteos, no porcentajes**, mientras el número de estudios sea pequeño (umbral en los specs).
7. **Las cifras de la lámina 7 de la presentación del equipo son inventadas.** Nunca usarlas como datos
   ni como esperados de prueba.
8. Textos dirigidos al equipo: en español, de **usted**, sin jerga técnica ni fórmulas, sin preguntas
   al equipo (solo propuestas).
9. **Observación técnica sobre la tabla 3 de la hoja EGM** (ver `contrato-matriz`): es información
   interna. No mencionarla en ningún texto o interfaz para el equipo sin autorización explícita de Jairo.
10. El módulo de aprendizaje no supervisado y la vista de red están **fuera del alcance actual**
    (escala futura). No implementarlos; sí dejar el núcleo extensible para ellos.
11. Ninguna corrección de specs, arquitectura, interfaz o planes se aplica directamente. Flujo
    obligatorio: `analista-impacto` → aprobación de Jairo → `corrector`, por cada corrección, y
    `verificador` una sola vez al cerrar todo el plan de corrección, nunca por corrección. La sesión
    principal no edita esos archivos para corregirlos.

## Flujo de trabajo (con compuertas)

`specs` → (revisión de Jairo) → `arquitectura + ADR + flujos de interfaz` → (revisión) →
`plan.md por módulo` → (revisión) → `código + pruebas, un módulo a la vez` → `verificación`.

- No escribir código sin un `plan.md` aprobado. No escribir planes sin arquitectura aprobada.
- Toda tarea de un plan cita los requisitos que satisface (FR/NFR/SC). Toda prueba cita el escenario
  o criterio que comprueba. Ver skill `trazabilidad`.
- Al terminar una fase: detenerse, resumir y listar los `[NEEDS CLARIFICATION]` abiertos.

## Mapa del repositorio

| Ruta | Contenido |
|---|---|
| `docs/fuentes/` | Fuentes de verdad, solo lectura (presentación del equipo, documentos de la propuesta, estado del proyecto) |
| `docs/specs/` | `000-vision-alcance.md`, `contrato-datos.md`, `NNN-<feature>/spec.md`, `trazabilidad.md` |
| `docs/arquitectura/` | `arquitectura.md`, `adr/` |
| `docs/interfaz/` | Flujos y bocetos |
| `docs/planes/` | `_plantilla-plan.md`, `<modulo>/plan.md` |
| `docs/informes/` | Informes de fase y de conformidad (los escribe el `verificador`) |
| `docs/correcciones/` | Propuestas de corrección `COR-NNN` |
| `data/raw/` | Matriz vigente (solo lectura) |
| `data/fixtures/` | Matrices sintéticas para pruebas |
| `src/egm/` | Núcleo Python (lectura, validación, modelo, análisis), sin dependencias de la web |
| `app/` | Capa web (stack según ADR) |
| `tests/` | `unit/`, `integracion/`, `propiedades/` |

## Subagentes

- `arquitecto` — arquitectura y ADR; solo lectura sobre código.
- `implementador` — código y pruebas de un módulo según su `plan.md`.
- `disenador-front` — flujos, bocetos, sistema de diseño, plantillas y CSS.
- `verificador` — auditoría de conformidad contra los specs; solo lectura; nunca corrige lo que audita.
- `analista-impacto` — solo lectura; explica, propone y evalúa correcciones.
- `corrector` — aplica solo propuestas aprobadas.

## Convenciones

- Documentación e interfaz en español. Identificadores del dominio en español sin tildes
  (`intervencion`, `dimension`, `nivel_evidencia`).
- Toda expresión matemática en LaTeX (`$…$` en Markdown).
- El análisis de datos y el dashboard con filtros se implementan en **Python** (restricción de Jairo).
