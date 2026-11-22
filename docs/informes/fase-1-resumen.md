# Resumen de cierre de la Fase 1 (specs)

**Fecha**: 2026-11-21, estado final (versiones anteriores: 2026-11-01, 2026-11-02 y la primera del 2026-11-21)
**Autor**: `verificador`
**Lector**: Jairo. Es un documento interno y no se comparte con el equipo.
**Fuente**: `docs/informes/conformidad-fase-1-cierre-final-2026-11-21.md`, que contiene la evidencia de cada dato, y
`docs/informes/conformidad-fase-1-cierre-2026-11-21.md`, de la pasada anterior.

## 1. Estado de la fase

**La Fase 1 está completa y puede cerrarse.**
- No queda ningún `[NEEDS CLARIFICATION]` abierto en los specs.
- Las diez correcciones COR-001 a COR-010 quedan `verificada`.
- No hay hallazgos bloqueantes ni mayores abiertos.
- Todavía no hay código, arquitectura ni planes.

**Qué resolvió COR-010.** Cerró los dos defectos que impedían verificar COR-009:
- **H-57.** FR-002-13 vuelve a tener línea propia.
- **H-58.** La fuente del colofón ahora está en el repositorio.

Además, COR-010 resolvió los hallazgos menores de specs y skills:
- H-59 y H-60: la entrada «Sin nivel» con solo documentos no empíricos, ahora con escenario (US-002-4.14), y la fecha
  de cuatro reglas;
- H-62: «plan» en lugar de «módulo» como unidad de plan;
- H-64, H-65 y H-68: tres citas de fuentes;
- H-69: la observación interna sale del contrato;
- H-70: «celda vacía» en un título.

La sesión principal cerró los de registro (H-63, H-66 y H-67), y H-61 queda anotado en la sección 9 de COR-009.

**Integridad.**
- La matriz está intacta: SHA-256 `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual al del
  apéndice A del contrato.
- `data/raw/` y `docs/fuentes/` no tienen cambios.
- El trabajo del 21-nov-2026 sigue sin commit. El último commit es b954d30, del 3-nov-2026.

**Versión de Python.** 3.13.15, en el entorno aislado `.venv/` del proyecto, que git ignora. Se comprobó el
21-nov-2026.

## 2. Specs y su versión

Todos los specs están en **v0 — propuesta, alcance por acordar** con la investigadora principal. Se crearon el
1-nov-2026, y su última modificación es la de COR-010, del 21-nov-2026.

| Spec | Contenido |
|---|---|
| `docs/specs/000-vision-alcance.md` | Visión, actores, alcance, NFR y SC globales |
| `docs/specs/contrato-datos.md` | Contrato con la matriz, con el apéndice A (instancia de ejemplo). Ya no tiene apéndice interno |
| `docs/specs/001-lectura-verificacion/spec.md` | Lectura, validación, conteo y verificación (P1) |
| `docs/specs/002-mapa-interactivo/spec.md` | Mapa interactivo (P2) |
| `docs/specs/003-tablero-conclusiones/spec.md` | Tablero y conclusiones (P3) |
| `docs/specs/trazabilidad.md` | Fuente y cobertura de los 89 requisitos; todos en estado «especificado» |

**Registro interno.** La observación interna que antes iba en el apéndice B del contrato está ahora en
`docs/informes/interno-tabla3-hoja-egm.md`, con el mismo texto. Es un registro interno del grupo B de la regla 9 de
`CLAUDE.md` y no se comparte con el equipo. El contrato ya no la contiene, así que puede compartirse completo con la
investigadora principal para el acuerdo de alcance.

## 3. Recuentos

| Spec | FR | NFR | SC | Historias | Escenarios |
|---|---|---|---|---|---|
| 000 | 0 | 19 | 19 | — | — |
| 001 | 29 | 0 | 5 | 5 | 61 |
| 002 | 19 | 0 | 5 | 5 | 30 |
| 003 | 22 | 0 | 6 | 5 | 30 |
| **Total** | **70** | **19** | **35** | **15** | **121** |

- **89 requisitos**, todos con fuente y con escenario o SC.
- Ningún identificador se repite, no hay huecos de numeración y ninguna referencia queda sin destino. Cada requisito
  empieza en su propia línea.
- `trazabilidad.md` tiene los 89 requisitos en cada tabla, y la fuente de cada uno equivale a la de su spec.
  Conserva sus 191 líneas con fin de línea CRLF.

## 4. Correcciones

| COR | Tema | Estado |
|---|---|---|
| COR-001 | Alcance de las tablas de la hoja EGM y resultado de una comparación incompleta | verificada |
| COR-002 | Estados de documento cuando el tipo de documento no tiene lista | verificada |
| COR-003 | Rótulo «Pendiente de codificación» frente a las referencias pendientes del equipo | verificada |
| COR-004 | Reglas citadas como fuente o decisión sin marca de propuesta | verificada |
| COR-005 | Filtros, sesión, carga fallida, «Sin nivel», intervención secundaria y colofón | verificada (ratificada por usted el 21-nov-2026) |
| COR-006 | Sincronización de la skill `contrato-matriz` | verificada |
| COR-007 | Fecha en `trazabilidad.md` y mayúsculas de dos marcas | verificada |
| COR-008 | Límite de tamaño del archivo cargado | verificada |
| COR-009 | Cierre de la Fase 1: sus decisiones del 21-nov-2026, hallazgos abiertos y plantilla de planes | verificada (tras COR-010) |
| COR-010 | Cierre de COR-009 y de los hallazgos H-57 a H-70 | verificada |

La sesión principal pasa este resultado a la sección 9 de COR-009 y de COR-010, con los textos propuestos en el
informe de cierre final (sección 6).

## 5. Decisiones de usted, por fecha

**31-oct-2026**
- La herramienta es una aplicación web, y el análisis y el tablero con filtros se hacen en Python.
- La vista de red y el módulo de aprendizaje no supervisado quedan fuera del alcance actual.
- El colofón muestra información del grupo, con un diseño académico y no genérico.

**1-nov-2026**
- **Matriz y hoja EGM.** El bloque de dimensiones va entre dos encabezados que lo delimitan. La hoja EGM solo sirve
  para verificar y se localiza por títulos.
- **Filtros.** Mapa y tablero tienen los mismos cuatro filtros, con estado compartido, «n de N» y el rótulo
  «ningún estudio registrado con los filtros activos». El filtro de nivel y la leyenda son un solo control. El año se
  filtra por rango.
- **Porcentajes y escalabilidad.** Solo se muestran conteos ($n_{min} = 100$). La herramienta sirve para las versiones
  presentes y futuras de esta matriz.

**2-nov-2026**
- **Errores de contrato.** La lista de errores de contrato es cerrada; todo lo demás es advertencia o nota.
- **Carga y sesión.** La matriz se carga desde el navegador, se valida antes de leerla y vive solo durante la
  sesión. Cada sesión es independiente.
- **Versión local y colofón.** La primera versión es local, para la demostración. El colofón lleva el código
  Minciencias COL0016423, el correo de contacto y los logos, y omite la categoría y la línea de investigación.
- **Otras.** No se incluye la métrica de avance por fila. La versión de Python la elige Claude Code. Las
  definiciones de filas y columnas vienen de un archivo aparte. El despliegue lo decide el equipo después de la
  demostración.

**3-nov-2026**
- **Orden y año.** Las dimensiones siguen el orden del archivo. Un año que no se reconoce se trata como advertencia.
- **Sesión y carga.** La sesión termina a los 45 minutos de inactividad. Una carga nueva reemplaza a la anterior.
- **«Sin nivel».** Es provisional y se debe discutir con el equipo.
- **Colofón.** Muestra «Matriz: <nombre del archivo>, leída el <fecha>, <n> documentos», sin deducir ninguna versión.
- **Límite de tamaño.** Es de 15 MB (COR-008).
- **COR-005.** Se aprobó COR-005.

**21-nov-2026** (COR-009, sección 6, Q1 a Q11)
- **Filtros.**
  - Un filtro solo está activo si, al aplicarlo con «Actualizar vista», deja fuera algún valor o estrecha el rango de
    años.
  - Ocultar o mostrar un nivel en la leyenda espera a «Actualizar vista».
  - «Restablecer» aplica de inmediato la vista sin filtros; así se cumple FR-002-18, que queda aprobado.
- **Documentos no empíricos.** En las cifras de documentos se tratan como «Sin nivel», y esa entrada aparece también
  cuando solo hay documentos no empíricos.
- **Carga nueva.**
  - **Error de contrato.** Una carga con error de contrato limpia todo y termina la sesión. El mensaje indica lo
    esperado y lo encontrado, sin el nombre del archivo ni filas de datos, también en la primera carga.
  - **Carga válida.** Una carga válida borra los filtros.
  - **Rechazo por tipo o tamaño.** Si se rechaza por tipo o tamaño, se conserva la matriz anterior.
- **Límites fijos.** El límite de tamaño es de 15 MiB (15 728 640 bytes), fijo. La inactividad es de 45 minutos,
  fija.
- **Huella, advertencias y verificación.**
  - La huella SHA-256 es un control del proyecto y no una función de la herramienta (Q1).
  - Ante anclas ambiguas y bloques de dimensiones degenerados, la herramienta advierte y sigue (Q4 y Q6).
  - Las diferencias con la hoja EGM también se explican por espacios en los extremos de un valor (Q2).
  - FR-003-21 es obligatorio (Q5).
- **Colofón.** El nombre completo del grupo, la ciudad y el director los confirma usted (Q3).
- **Planes.** La Fase 3 hace un plan por spec, con `_plantilla-plan-spec.md`; la plantilla por módulo se eliminó
  (Q10). El constructor de fixtures va en el plan 001, y cada NFR-000 va en los planes que afecta (Q11). Los commits
  los hace usted (Q9).
- **Regla 9.** Las inconsistencias de la matriz se clasifican en grupos A y B, se registran en
  `hallazgos-matriz-para-equipo.md` y solo se comunican al equipo en el informe final de fase.
- **COR-005.** Usted ratificó COR-005 completa.

**21-nov-2026** (COR-010, opción A; Q1 a Q4 = 1)
- **«Sin nivel».** La entrada es la misma en la leyenda del mapa y en la del tablero. Si solo existe por los
  documentos no empíricos, en el mapa cuenta 0 estudios.
- **Registro interno.** La observación interna sale del contrato y pasa a `docs/informes/interno-tabla3-hoja-egm.md`.
  El contrato solo indica qué tablas de la hoja se comparan.
- **Planes.** «Plan» es la unidad de plan y «módulo», la de la arquitectura. En cada historia, las pruebas van antes
  que su implementación (Q3: también en `verificador.md`).
- **Colofón.** El nombre del proyecto se cita del estado del proyecto al 31-oct-2026 (Q1).
- **Otras.** Basta SC-001-02 para las filas nuevas de casos borde (Q2). La fecha del 21-nov-2026 se anota también en
  la regla de filtros del contrato (Q4).

## 6. `[NEEDS CLARIFICATION]` abiertos

**Ninguno** en `docs/specs/` ni en las skills. Los dos de `docs/specs/_plantilla/` son de la plantilla y no del
proyecto. Los dos que dejó el analista en COR-010 se resolvieron con los PDF de `docs/fuentes/`, y esta auditoría los
comprobó.

Queda una sola marca de dato pendiente: `[POR CONFIRMAR]` en `pie-de-pagina.md:21`, que corresponde a su nombre y su
rol en el colofón (sección 7).

## 7. Pendientes que no son de specs y bloquean algo concreto

| Pendiente | Qué bloquea | Dónde consta |
|---|---|---|
| Logos de Minciencias y de la Universidad del Magdalena, en `docs/interfaz/logos/` (la carpeta aún no existe) | SC-000-11: la revisión del colofón en modo claro y oscuro y a 360 px no se puede hacer sin los archivos | `pie-de-pagina.md:36-37`; `000-vision-alcance.md:108` |
| Permiso de uso de los logos institucionales | Publicar los logos en el colofón | `README_KIT.md:50` |
| Su nombre y su rol en el colofón | La línea «Herramienta» del colofón. Mientras no lo indique, la línea se omite completa | `pie-de-pagina.md:21`; `pie-de-pagina.md:4-5` |
| Stack web | El contexto técnico de los planes (Fase 3) y el código (Fase 4). Lo propone el ADR-003 en la Fase 2, salvo que usted lo decida antes | `README_KIT.md:51`; `arquitecto.md:24` |

## 8. Hallazgos menores que quedan

No impiden cerrar la fase. El detalle está en el informe de cierre final, sección 4.

- **H-71.** El caso borde de `002:226` habla de «documentos no empíricos sin nivel». La regla (FR-002-12 y FR-003-14)
  trata como «Sin nivel» a todo documento no empírico. El requisito manda y no hay contradicción de cobertura. Si
  desea afinar la redacción, puede hacerlo en una corrección futura.
- **H-72.** `prompts/RETOMAR_2026-11-21.md` es anterior a COR-009 y COR-010: sus pendientes ya están resueltos y cita
  textos que cambiaron. Se propone no usarlo para retomar el trabajo. La Fase 2 parte de `CLAUDE.md` y de este
  resumen.

## 9. Qué necesita la Fase 2 para empezar

1. **Su revisión de los specs.** Es la compuerta de `README_KIT.md:45-46`.
2. **Las secciones 9 de COR-009 y COR-010**, completadas por la sesión principal con los textos del informe de cierre
   final, y su estado en `verificada`.
3. **Versionar el trabajo del 21-nov-2026.** Lo hace usted (Q9). Incluye:
   - los archivos nuevos sin seguimiento: `docs/planes/_plantilla-plan-spec.md`, `docs/correcciones/COR-009.md` y
     `COR-010.md`, los tres informes de conformidad del 21-nov, `hallazgos-matriz-para-equipo.md` e
     `interno-tabla3-hoja-egm.md`;
   - el borrado de `docs/planes/_plantilla-plan.md`.
4. **Los dos marcadores de `prompts/PROMPT_FASE_2_arquitectura.md`**, llenos antes de pegar el prompt:
   - `:11` «[Respuestas a los NEEDS CLARIFICATION de la fase 1]». Texto propuesto: «No queda ningún NC abierto. Las
     respuestas del 21-nov-2026 están en la sección 6 de `docs/correcciones/COR-009.md` y de `COR-010.md`, y en
     `invariantes.md` («Decisiones del 21-nov-2026»).»
   - `:12` «[Stack web, si ya lo decidió; si no, el ADR-003 lo propone]». Texto propuesto, si no lo ha decidido:
     «Sin decidir: el ADR-003 lo propone (Python, con control total de HTML y CSS).»
5. **Los logos en `docs/interfaz/logos/`** antes de que el `disenador-front` haga los bocetos del colofón. Sin ellos,
   los bocetos pueden avanzar, pero SC-000-11 no se puede comprobar.
