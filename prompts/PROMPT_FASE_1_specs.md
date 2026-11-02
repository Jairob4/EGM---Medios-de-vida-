# Prompt para Claude Code — Fase 1: estructura del repositorio y specs

> Pegar en Claude Code desde la raíz del repositorio, después de copiar el kit y las fuentes
> (ver `README_KIT.md`). Recomendado: iniciar en modo plan y aprobar el plan antes de ejecutar.

---

## Contexto

Lee `CLAUDE.md` completo. Vas a ejecutar la **Fase 1** del proyecto EGM: crear la estructura del
repositorio y escribir los specs. **No escribas código de la aplicación, ni arquitectura, ni planes de
módulo en esta fase.**

Carga antes de empezar las skills `especificacion-srs`, `contrato-matriz` y `trazabilidad`.

## Fuentes (las únicas válidas para requisitos)

| Fuente | Ruta | Cómo citarla |
|---|---|---|
| Presentación del equipo (oct-2026, 11 láminas) | `docs/fuentes/presentacion_equipo_2026-10_texto.md` (texto extraído; el `.pptx` original, si está, tiene prioridad) | `[Fuente: lámina n]` |
| Propuesta, versión general (21-oct-2026) | `docs/fuentes/propuesta_herramienta_general.pdf` | `[Fuente: doc. general §x]` |
| Propuesta, versión técnica (21-oct-2026), **opcional** | `docs/fuentes/propuesta_herramienta_tecnica.pdf` | `[Fuente: doc. técnico §x]` |
| Estado del proyecto (31-oct-2026) | `docs/fuentes/estado_proyecto_2026-10-31.md` | `[Fuente: estado §x]` |
| Matriz bibliográfica vigente | `data/raw/*.xlsx` | `[Fuente: Matriz <hoja>!<celda>]` |
| Decisiones de Jairo del 31-oct-2026 (abajo) | este prompt | `[Fuente: decisión de Jairo, 31-oct-2026]` |

Decisiones de Jairo del 31-oct-2026:
1. La herramienta se construye como **aplicación web**.
2. El análisis de datos y el dashboard con filtros se implementan **en Python**.
3. El módulo de aprendizaje no supervisado queda como **escala futura** (fuera de alcance).
4. El pie de página muestra información del grupo de investigación (skill `sistema-diseno-egm`,
   `references/pie-de-pagina.md`).
5. Diseño no genérico, acorde con la formalidad académica del proyecto.

Si falta alguna fuente obligatoria de la tabla, **detente** y lista cuáles faltan antes de hacer nada más.
Si falta solo la versión técnica, continúa y marca `[NEEDS CLARIFICATION]` donde necesites un detalle
que la versión general no trae.

## Tareas

### T1. Estructura del repositorio
Crea exactamente esta estructura (carpetas vacías con `.gitkeep`; sin código):

```
docs/fuentes/  docs/specs/_plantilla/  docs/arquitectura/adr/  docs/interfaz/bocetos/
docs/planes/  docs/informes/
data/raw/  data/fixtures/
src/egm/lectura/  src/egm/validacion/  src/egm/modelo/  src/egm/analisis/
app/
tests/unit/  tests/integracion/  tests/propiedades/
```

Además: `README.md` (qué es, estado «fase de specs», mapa de carpetas) y `.gitignore` para Python.
Las subcarpetas de `src/egm/` son provisionales: las confirma la arquitectura.

### T2. Contrato de datos → `docs/specs/contrato-datos.md`
1. Abre la matriz de `data/raw/` **en modo lectura** y extrae: hojas, encabezados A–Y, validaciones de
   datos (listas), fórmulas de la hoja `EGM` y si el archivo trae valores calculados.
2. Compáralo con `.claude/skills/contrato-matriz/references/referencia-v4.md` y registra cada diferencia.
3. Registra el **SHA-256** del archivo (el `verificador` lo usará para comprobar que nunca se modificó).
4. Escribe el contrato: reglas de lectura, definiciones formales en LaTeX ($E$, $S(i,j)$, $T_1$, $T_2$,
   $T_4$), regla de la columna U, casos borde y valores esperados verificados. La observación interna
   sobre la tabla 3 va en una sección marcada «Interna — no publicar».

### T3. Visión y alcance → `docs/specs/000-vision-alcance.md`
Con la plantilla como guía de estilo (no es un spec de feature): propósito, actores (equipo de
investigación, investigadora principal, Jairo como mantenedor), alcance (F2, F3, F4 de la propuesta),
fuera de alcance (vista de red F5, módulo no supervisado, edición de la matriz, autenticación salvo que
una fuente lo pida), restricciones (decisiones de Jairo, solo lectura, no cambiar la matriz) y
**NFR globales** `NFR-000-nn` (solo lectura, trazabilidad, español y usted, accesibilidad WCAG 2.2 AA,
funcionamiento desde 360 px, adaptación automática a nuevas categorías de la matriz, conteos en lugar
de porcentajes con pocos estudios).

### T4. Specs de features con `docs/specs/_plantilla/spec-template.md`
- `docs/specs/001-lectura-verificacion/spec.md` — P1: leer la matriz, validarla contra el contrato,
  contar, verificar contra la hoja EGM y reportar advertencias legibles.
- `docs/specs/002-mapa-interactivo/spec.md` — P2: mapa con burbujas, detalle por celda con sus estudios,
  definiciones de filas y columnas, filtros (tipo de fuente, metodología, nivel de evidencia, año),
  mostrar u ocultar niveles desde la leyenda, exportar.
- `docs/specs/003-tablero-conclusiones/spec.md` — P3: cifras clave y las seis conclusiones del doc.
  general §5, cada una con su conteo de estudios y la lista de N.º que la sostienen; cuidados del §7.

Usa como esperados de los escenarios los valores reales de la matriz (contrato) o fixtures sintéticos
descritos en el propio escenario. **Nunca** las cifras de la lámina 7.

### T5. Trazabilidad → `docs/specs/trazabilidad.md`
Una fila por requisito con su fuente; columnas de componente, tarea y prueba vacías; estado
`especificado`.

### T6. Verificación de la fase
Invoca al subagente `verificador` para auditar la fase de specs. Luego escribe
`docs/informes/fase-1-resumen.md` con: archivos creados, conteo de requisitos por spec, diferencias
encontradas en la matriz y la **lista completa de `[NEEDS CLARIFICATION]`**, agrupada por spec.

## Criterios de terminado
- [ ] Estructura creada; ningún archivo de código de aplicación.
- [ ] `data/raw/` y `docs/fuentes/` sin modificar (hash registrado).
- [ ] Todo FR/NFR con fuente y con escenario o SC que lo verifique; IDs únicos.
- [ ] Ninguna tecnología nombrada en los specs (salvo la restricción de Python citada como decisión).
- [ ] Informe del verificador sin huecos abiertos, o con sus huecos listados en el resumen.

Al terminar, **detente** y muéstrame el resumen. No avances a la arquitectura.
