# Informe de conformidad — Fase 3 (planes por spec)

**Fecha**: 2026-11-22 · **Auditor**: subagente `verificador` (no participó en la redacción de los planes)
**Objeto**: `docs/planes/001-lectura-verificacion/plan.md`, `docs/planes/002-mapa-interactivo/plan.md`,
`docs/planes/003-tablero-conclusiones/plan.md`, `docs/planes/README.md` y la columna «Tarea» de
`docs/specs/trazabilidad.md`.
**Referencias**: `docs/arquitectura/arquitectura.md` (aprobada el 22-nov-2026), ADR-001 a ADR-005,
`docs/planes/_plantilla-plan-spec.md`, skills `trazabilidad`, `plan-modulo`, `calidad-python`, `contrato-matriz`,
`.claude/skills/analisis-impacto/references/invariantes.md`, `prompts/PROMPT_FASE_3_planes.md`.

## Veredicto

**Conforme con reservas.** Los tres planes cubren los 89 requisitos FR/NFR, todas sus tareas citan requisitos
existentes, los 122 escenarios de los specs tienen al menos una prueba y ningún plan toca un módulo fuera de la lista
cerrada M01 a M23 ni contradice la tabla de módulos por plan (arquitectura §6.4). Las reglas inviolables se respetan.
No hay hallazgos de severidad alta. Hay **seis hallazgos de severidad media** (F3-01 a F3-06) que dejan huecos o
contradicciones entre planes y que conviene resolver, o aceptar de forma expresa, al aprobar los planes; ninguno
impide empezar la fase 1 del plan 001 salvo lo indicado en la sección 8.

## 1. Resumen numérico

Comprobado con un programa que extrae los identificadores de los specs y de los planes (expande rangos «a» y listas
«1.4, 1.7») y compara la columna «Tarea» de `trazabilidad.md` con los «Requisitos:» de cada tarea.

| Medida | Valor |
|---|---|
| FR/NFR definidos en los specs | 89 |
| FR/NFR con al menos una tarea | 89 (ninguno sin tarea) |
| Tareas (001 / 002 / 003) | 61 / 50 / 57 = 168 (coincide con lo declarado) |
| Pruebas (001 / 002 / 003) | 95 / 68 / 51 = 214 (coincide con lo declarado) |
| IDs repetidos de tarea o prueba | 0 |
| Tareas que citan un requisito inexistente | 0 |
| Escenarios `US-…` definidos / con al menos una prueba | 122 / 122 |
| Criterios `SC-…` definidos / con al menos una prueba `P-…` | 35 / 33 (faltan SC-000-03 y SC-003-05; ver F3-10) |
| Filas de `trazabilidad.md` cuya columna «Tarea» difiere de los planes | 6 de 89 (F3-07) |
| `trazabilidad.md` | 191 líneas, CRLF; el diff contra `HEAD` solo cambia la columna «Tarea» (89 inserciones, 89 eliminaciones) |

Las tareas sin «Requisitos:» son las de escribir pruebas (citan las pruebas, que citan su escenario), como en la
plantilla, y las de cierre con «Requisitos: —» (T-001-03, T-001-90 a 92, T-001-95, T-002-01, T-002-46, T-002-47,
T-003-01, T-003-94, T-003-95): no son excesos.

## 2. Reglas inviolables e invariantes

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA-256 de la matriz | Coincide: `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1` | `sha256sum data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx`; `contrato-datos.md:374` |
| `docs/fuentes/` y `data/raw/` sin cambios | Sin cambios | `git status --short docs/fuentes data` vacío |
| Sin código escrito | `src/`, `app/` y `tests/` solo tienen `.gitkeep` | `find src app tests -type f` |
| `data/raw/` solo se lee, en integración, contra el apéndice A | Plan 001 conforme (`001:45-47`, `001:405-409`, `001:466`, `001:477`, `001:524`, `001:580`). Excepciones en los planes 002 y 003 | F3-06 |
| Ninguna cifra de la lámina 7 | Conforme. Ningún esperado ni fixture reproduce la tabla de la lámina 7 (`docs/fuentes/presentacion_equipo_2026-10_texto.md:92-112`); los planes lo prohíben (`001:227`, `002:180`, `003:567`) | — |
| Nada de la tabla 3 | Conforme. Ningún plan nombra la tabla 3; solo dicen «tabla no comparable» y exigen que ningún texto la nombre (`001:364`, `001:528`, `002:537`, `003:569`) | — |
| Conteos y no porcentajes | Conforme (`002:474`, `003:208-211`, `003:328`, `003:334`); M11 apagado, $n_{min} = 100$ | — |
| Commits los hace Jairo | Conforme (`001:875`, `002:649`, `003:266`, `003:604`, `README.md:3`) | — |
| Valores del apéndice A en los esperados | Conformes con `contrato-datos.md:368-404` (27 documentos, $\lvert E\rvert = 7$, $N = 1$, 6 de 48 celdas, $T_4$, fuentes, metodologías, años, enfoque) | `001:405-408`, `002:257`, `003:237-240`, `003:374` |
| Python y dependencia del núcleo | `.venv` con 3.13.15 y `openpyxl` 3.1.5, como dice `001:36-39` | `.venv/pyvenv.cfg` |

Decisiones del 21 y 22-nov-2026 (`invariantes.md:57-109`), comprobadas una a una en los planes: activo solo si deja
fuera algo (`002:333`); la leyenda espera a «Actualizar vista» (`002:323`); «Restablecer» inmediato (`002:324`);
no empíricos como «Sin nivel» y entrada «Sin nivel» con 0 en el mapa (`002:332`, `003:422`); filtros borrados tras
carga nueva (`002:334`, `002:239-240`); mensaje de error de contrato con lo esperado y lo encontrado y sin nombre de
archivo (`001:481`, `001:620`); rechazo previo que conserva la sesión (`001:618`, `001:623`); error de contrato que
termina la sesión (`001:620`); 45 min fijos y E7 a los 43 (`001:698`, `001:700`; `flujos.md:63`); 10 s de gracia
(`001:697`); huella como control del proceso, no función (`001:409`, ninguna tarea la implementa en la herramienta);
FR-003-21 obligatorio (`003:240`, `003:595`); colofón con solo «Datos» y 3ie por defecto (`001:626`, `002:271`);
tipografías locales (`001:663-665`); PNG desde el SVG en el cliente (`002:472`); `.xlsx` con filtros, archivo y fecha
(`002:469`); título «Evidencias sobre medios de vida» (`002:271`); NC-INT-2 (`003:423`); plantilla por spec y
constructor en la preparación del 001 (`001:309-331`). Sin desviaciones.

## 3. Módulos por plan (arquitectura §6.4)

Ninguna tarea toca un módulo fuera de M01 a M23. Coincidencia con `arquitectura.md:697-721`:

- Plan 001 crea M01 a M05, M07, M08, M10, M13 a M19, M21 a M23 (`001:5`, `001:294-299`): coincide.
- Plan 002 crea M06, M12, M20; amplía M07, M10, M14, M15, M17, M18, M19, M22, M23; usa M01, M04, M05, M13; no toca
  M02, M03, M08, M09, M11, M16, M21 (`002:154-156`): coincide.
- Plan 003 crea M09, M11; amplía M06, M07, M10, M14, M17, M18, M22, M23; usa M15 (`003:449`, `003:484`) y no cambia M19
  (`003:480-481`): coincide.
- NFR-000 por plan (`arquitectura.md:723-726`): coinciden, con dos desvíos menores registrados en F3-15 y F3-17.

## 4. Solapes y dependencias entre planes

Sin implementaciones duplicadas: M06 lo crea el 002 y el 003 solo agrega `cumple_documento` (`003:438-440`, `003:548`);
M07 se reparte sin repetir (001 conteos base `001:441-447`; 002 filtro y desglose `002:235-238`; 003 coocurrencias
`003:389-391`); M15 lo crea el 001 y el 002 agrega `aplicar_filtro` (`001:648-651`, `002:239-240`). US-001-4.10 y
US-001-5.4 a 5.6 salen del 001 (`001:120-123`) y están en el 002 (P-002-36, P-002-19, P-002-38, P-002-48), sin copia
doble. Los huecos de entrega están en F3-01 a F3-03.

Hitos del 001 frente a lo que consumen 002 y 003 (`001:766-790`, `002:566-586`, `003:537-552`): coinciden, salvo
FX-A (F3-02), M07 con filtro fuera de `mapa` (F3-03) y la descripción de N2 (F3-13).

## 5. Pruebas antes que implementación y fases de la plantilla

En todas las historias de los tres planes la tabla de pruebas y las tareas «Escribir P-…» van antes de las de
implementación (comprobado por programa: cada prueba citada en «Pruebas:» de una tarea de implementación tiene una
tarea de escritura anterior), con las excepciones de F3-11. Las fases siguen la plantilla (preparación, base que
bloquea, una fase por historia, cierre); las fases añadidas (001 fase 6 «Fachada», 002 fase 8 «Accesibilidad») están
justificadas. El orden de historias se aparta de la prioridad del spec con razón escrita (`001:27-32`, `002:28-29`,
`003:27-30`).

## 6. Hallazgos

| ID | Severidad | Tipo | Hallazgo y evidencia |
|---|---|---|---|
| F3-01 | Media | Hueco | **Escenarios delegados al plan 003 que el 003 no recoge.** El 001 deja «US-001-4.6 completo» al 003 (`001:96`, `001:118-119`, `001:790`) y el 002 le deja la parte del tablero de US-002-4.6 y de US-002-4.14 (`002:101-103`, `002:332`, `002:593`). Además, la parte del tablero de US-001-4.10 («el mapa **y el tablero** muestran la vista sin filtros», `spec 001:220-223`) no la toma nadie: el 002 solo prueba el mapa (`002:334`). El plan 003 no cita ninguno de los cuatro (búsqueda de «4.6», «4.14» y «US-001-4» sin resultados). P-003-64 (`003:471`) y P-003-50 (`003:422`) se parecen, pero no los citan y P-003-50 usa otro fixture («3 de 4» con FX-003-07, frente a «2 de 3» del escenario, `spec 002:165-168`). El programa los cuenta como cubiertos solo por sus partes del mapa o del núcleo. |
| F3-02 | Media | Hueco (dependencia sin plan que la entregue) | **FX-A.** El 003 dice que la «réplica sintética de la instancia de ejemplo» la crea el plan 001 (`003:165`, `003:545`) y la usa en 17 pruebas (P-003-10, 11, 13, 16, 20, 22, 24, 28, 30 a 33, 36, 40, 43, 49, 62). El catálogo de fixtures del 001 (`001:221-285`) no la incluye ni la menciona. |
| F3-03 | Media | Hueco (dependencia sin plan que la entregue) | **M07 con filtro fuera de `mapa`.** La arquitectura da `filtro` a `conjuntos`, `evaluacion_impacto` y `coocurrencias` y asigna «filtro» al 002 (`arquitectura.md:431-445`); el 001 dice que el 002 agrega el parámetro (`001:775-776`). El 002 solo lo agrega a `mapa` (T-002-07, `002:235-238`). El 003 espera del 002 «`mapa` y `evaluacion_impacto` con filtro» (`003:549`) y lo necesita para la conclusión 2 y las cifras filtradas (T-003-23, `003:299`; T-003-54, `003:441-443`). Ninguna tarea agrega `filtro` a `conjuntos` ni a `evaluacion_impacto`. |
| F3-04 | Media | Contradicción | **Nombre del constructor.** El 001 fija `tests/constructor.py` (`001:174`, `001:190-192`) y el 002 lo sigue (`002:144`), pero el 003 usa `tests/fixtures_builder.py` (`003:144`, `003:160`, `003:193`). O-1 (`001:837-838`) solo registra la diferencia con el prompt y `calidad-python`, no la del plan 003. |
| F3-05 | Media | Contradicción | **Carpetas de pruebas de navegador y del guion.** El 001 usa `tests/navegador/` (`001:178`, `001:634`, `001:707`); el 002, `tests/e2e/` (`002:148`, `002:177`, `002:277`, `002:342`, `002:399`, `002:479`, `002:516`) y dice que «la decide el plan 001» (`002:156`); el 003 pone su prueba de navegador P-003-90 en `tests/integracion/` (`003:497`). El guion M19 está en `app/cliente/` en el 001 (`001:170`, `001:669`, `001:721`) y en `app/estaticos/` en el 002 (`002:141`, `002:298`, `002:369`, `002:416`, `002:489`). |
| F3-06 | Media | Regla de pruebas | **Esperados tomados de `data/raw/` y no del apéndice A.** P-002-44 compara con «sus celdas leídas en la prueba de forma independiente (el apéndice A no los trae)» (`002:391`); P-002-39 hace lo mismo con referencia y año (`002:386`); P-003-45 igual con los textos del N.º 7 (`003:376`). `calidad-python` pide esperados escritos a mano desde el contrato o `referencia-v4.md`, y el encargo limita `data/raw/` a la prueba de integración contra el apéndice A. Además, el 003 dice «una sola prueba de integración lee `data/raw/`» (`003:38`), pero son dos (P-003-15 y P-003-45). |
| F3-07 | Baja | Trazabilidad | **Columna «Tarea» de `trazabilidad.md`: 6 de 89 filas difieren de los planes.** `:9` NFR-000-03 omite T-002-49 (`002:536-538`); `:12` NFR-000-06 lista T-001-07 y T-001-25, que no citan NFR-000-06 (`001:324-327`, `001:441-447`), y omite T-002-02 y T-002-13 (`002:178-180`, `002:285-289`); `:20` NFR-000-14 omite T-002-48 (`002:534-535`); `:25` NFR-000-19 omite T-001-51 (`001:589-593`); `:30` FR-001-05 omite T-001-05 (`001:314-318`); `:49` FR-001-24 lista T-001-24, que no cita FR-001-24 (`001:435-440`). Las otras 83 filas coinciden. |
| F3-08 | Baja | Trazabilidad / proceso | **Estado y responsable de la columna «Tarea».** Las 89 filas siguen en «especificado» (`trazabilidad.md:7-95`), aunque la skill `trazabilidad` prevé «diseñado» y «planificado». El 001 dice que la columna «Tarea» la llena la sesión principal «al aprobar este plan» (`001:732-733`), pero se llenó con los planes en borrador (`001:3`, `002:3`, `003:3`); y T-002-46 (`002:530-531`) y T-003-95 (`003:508-509`) vuelven a encargar al implementador la columna «Tarea». |
| F3-09 | Media | Dato no verificado (regla 3) | **«Jairo autoriza las descargas»** (`001:829-831`) se afirma sin fuente: no consta en `invariantes.md` ni en ADR-003. T-001-02 necesita descargar dependencias, el navegador de Playwright y axe-core (`001:39-44`, `001:214-216`), y T-001-67 y T-001-68 las tipografías y htmx. Debería ir como `[NEEDS CLARIFICATION]` hasta que Jairo lo decida. |
| F3-10 | Baja | Cobertura | **Pruebas sin ID y criterios sin prueba.** P-001-02 (`001:343`), P-002-12 (`002:265`), P-002-22 (`002:320`) y P-002-33 (`002:331`) citan un caso borde por su nombre o un NC, no un escenario ni un SC. SC-000-03 y SC-003-05 no tienen prueba `P-…`: los cubren revisiones manuales (T-001-93 `001:737-739`, T-002-49 `002:536`, T-003-92 `003:501-503`; T-003-93 `003:504-505`, sujeta a NC-P003-5). Es coherente con criterios de revisión humana, pero debe constar así en la trazabilidad. |
| F3-11 | Baja | Pruebas primero | P-002-68 se escribe en T-002-43 (`002:516`, fase 8), pero la citan como prueba T-002-25 (`002:369`), T-002-32 (`002:415`) y T-002-37 (`002:450`), de fases anteriores. P-001-01 y P-001-02 se escriben en la misma tarea que el código que prueban (T-001-07 `001:324-327`; T-001-09 `001:332-338`); en T-001-09 es una prueba de caracterización, aceptable. |
| F3-12 | Baja | Plantilla / `plan-modulo` | Las 50 tareas del 002 no tienen la etiqueta `[US-002-n]` (la ponen solo en los títulos de fase, `002:647-648`) ni el campo «Módulos:» (0 de 50), que la plantilla y `plan-modulo` («cada tarea indica los módulos») piden. Los planes 001 y 003 lo traen en 38 de 61 y 40 de 57 (el resto son tareas de escribir pruebas o de cierre). T-002-44 hace que el `disenador-front` escriba en el propio plan (`002:517-519`). |
| F3-13 | Baja | Hitos | **N2 promete piezas de la fase 8.** `001:781-783` y `README.md:7` incluyen en N2 (fase 7) las sesiones y el registro de actividad de M19, pero el reloj inyectable, la inactividad y el registro de actividad llegan en la fase 8 (T-001-82 `001:711-714`, T-001-84 `001:718-721`), después del punto de control de N2 (`001:679`). El 002 los necesita (`002:580-582`; P-002-19, 38, 48). No afecta al camino crítico, que exige el 001 completo (`README.md:16`), pero sí a la propuesta de adelantar el 002 tras N1 (`001:792-793`). |
| F3-14 | Baja | Texto desactualizado | El 002 dice que el 001 «se escribe en paralelo» (`002:566`, `002:603`) y el 003, «en redacción» y «aún sin plan aprobado» (`003:538`, `003:565`), cuando los tres ya están escritos y la ejecución es uno a la vez (`README.md:3`). |
| F3-15 | Baja | Cobertura | **SC-000-05 y SC-000-02 en todas las vistas.** SC-000-05 pide 360 px sin desplazamiento horizontal en todas las vistas (`000-vision-alcance.md:101`); para el tablero solo hay axe a 360 px (P-003-90, `003:495`) y capturas (T-003-91); la arquitectura no da NFR-000-05 al 003 (`arquitectura.md:724-726`). El 001 deja SC-000-02 a las vistas V3 a V9 de 002 y 003 (`001:124`), pero ninguna prueba del 002 cita SC-000-02 (P-002-14 y P-002-40 lo comprueban sin citarlo). |
| F3-16 | Baja | Contradicción (amplía O-2) | El 002 dice que el bloque de filtros «funciona con formularios reales y htmx solo evita recargar» y que las rutas van «por envío de formulario» (`002:362-367`), pero sin guion no viaja la ficha `X-EGM-Sesion` (`001:196-197`), así que sin guion no hay sesión. Es el mismo conflicto de O-2 (`001:839-841`) llevado al plan 002. |
| F3-17 | Baja | Divergencia con la arquitectura | El 002 da a M06 la entrada «Sin nivel» por documentos no empíricos (T-002-20 `002:346-351`, R-2 `002:605-608`), que `arquitectura.md:416` asigna al 003 («amplía con documentos y “Sin nivel” de no empíricos»). El 003 lo acepta (`003:547-548`), así que no hay solape, pero la tabla de la arquitectura queda inexacta. El 002 lleva NFR-000-09 (`002:82`), que `arquitectura.md:724` no le asigna. NC-P003-1 propone una quinta categoría «sin diligenciar» que FR-003-07 no nombra (`003:570-572`): si se adopta, puede requerir una corrección del spec por el flujo de la regla 11. |

No se encontraron excesos de alcance: ninguna tarea implementa la vista de red, el módulo no supervisado, filtros
por intervención, dimensión o enfoque, ni una vista tabular de la matriz. `coocurrencias` responde a FR-003-08.

## 7. `[NEEDS CLARIFICATION]` y observaciones para COR-013

| ID | Tema | Dónde | Bloquea |
|---|---|---|---|
| NC-ARQ-1 | Parte del libro que se descomprime a más de lo declarado | `001:332-338`, `001:804-807` | Se resuelve en T-001-09; si es adverso, detiene T-001-13 y T-001-15 |
| NC-P001-1 | Vista del resultado de una carga aceptada antes del plan 002 | `001:808-812` | T-001-66 (fase 7) y la definición de terminado (`001:859`) |
| NC-P001-2 | Archivos de los logos para SC-000-11 | `001:813-818` | Solo T-001-94 (revisión manual) |
| NC-P002-1 | Qué plan aloja US-001-4.10 (mapa) y US-001-5.4 a 5.6 | `002:623` | Nada. El 001 ya las excluye (`001:120-123`) y el 002 las tiene: se puede dar por cerrada |
| NC-P002-2 | Lector de pantalla para P-002-65 | `002:624` | Fase 8 del 002 |
| NC-P002-3 | Sintaxis del encabezado del archivo de definiciones | `002:625` | T-002-34 |
| NC-P002-4 | Destino del enlace de un DOI | `002:626` | T-002-29 |
| NC-P002-5 | Orden de los valores presentes sin lista | `002:627` | T-002-20 |
| NC-P003-1 | Base y «sin diligenciar» de la conclusión 3 | `003:570-572` | T-003-24, T-003-27 |
| NC-P003-2 | Trazabilidad de las cifras de celdas | `003:573-575` | T-003-08, T-003-13, T-003-15 (fase 2 del 003) |
| NC-P003-3 | Forma de la conclusión 4 | `003:576-580` | T-003-44, T-003-47 |
| NC-P003-4 | Campo vacío en la conclusión 6 | `003:581-582` | T-003-46 |
| NC-P003-5 | Quién y cuándo comprueba SC-003-05 | `003:583-585` | T-003-93 |

Observaciones para COR-013 (no se corrigen aquí):

- **O-1** constructor `tests.constructor` frente a `fixtures_builder.py` (`001:837-838`; `002:617-620`). Ampliar con F3-04.
- **O-2** ADR-003 punto 2 frente al punto 4 (`001:839-841`). Ampliar con F3-16.
- **O-3** firmas de M07 con `filtro` antes de que exista `Filtro` (`001:842-844`). Relacionada con F3-03.
- **O-4** NFR-000-16 asignado al 002 con M21 creado en el 001 (`001:845-846`).
- **F2-13** fecha de la nota de revisión de ADR-003 (`conformidad-fase-2-cierre-2026-11-22.md:184`).
- **F2-14** `pie-de-pagina.md` da por confirmados todos los datos con «Herramienta» pendiente (`conformidad-fase-2-cierre-2026-11-22.md:191`).
- Candidatas de este informe: F3-17 (tabla de M06 en la arquitectura y NFR-000-09 en §6.4). F3-01 a F3-15 son de los
  planes, que están en borrador: se resuelven al revisarlos antes de aprobarlos, sin COR, salvo que Jairo indique otra cosa.

## 8. Lo que bloquea el plan 001

Bloquean **el inicio**:

1. **Aprobación del plan 001 por Jairo** (estado «borrador», `001:3`; `CLAUDE.md`: no se escribe código sin plan aprobado).
2. **F3-09, autorización de las descargas** (dependencias, navegador de pruebas, axe-core, htmx, tipografías): sin ella
   no se puede cerrar T-001-02.

Conviene resolver **antes de la tarea indicada**, para no rehacer trabajo:

3. **O-1 y F3-04** (nombre del constructor) antes de T-001-04.
4. **F3-02** (FX-A): agregarla al catálogo del 001 antes de T-001-07, o pasarla al 003.
5. **F3-05** (carpetas de navegador y del guion) antes de T-001-61.
6. **NC-P001-1** antes de T-001-66 y **O-2** antes de T-001-68 y T-001-69 (fase 7).
7. **NC-ARQ-1** se resuelve dentro del plan (T-001-09); solo detiene T-001-13 y T-001-15 si el resultado es adverso.

No bloquean el 001: NC-P001-2, O-3, O-4, F2-13, F2-14, los NC de los planes 002 y 003, y F3-01, F3-03, F3-06 a F3-17
(se resuelven antes de aprobar o ejecutar los planes 002 y 003).

## 9. Viabilidad frente al 6-dic-2026 (opinión técnica, sin decidir alcance)

El camino crítico de `README.md:14-21` suma **114 tareas y 160 pruebas** (001 completo: 61 y 95; 002 fases 1 a 4:
25 y 38; 003 fases 1 a 5: 28 y 27) de las 168 y 214 totales, en unos 14 días naturales desde el 23-nov. Son unas ocho
tareas por día, con unos dieciséis puntos de detención para resumen y commit de Jairo. El orden es correcto: la
dependencia 001 → 002 → 003 es real y los hitos N1 y N2 están bien puestos. El riesgo se concentra en el plan 001: su
mitad web (fases 7 y 8, 17 tareas, con 6 pruebas de navegador y el montaje de Playwright y axe) y la posibilidad de que
NC-ARQ-1 detenga el plan. En opinión de este auditor el plazo es **ajustado, con riesgo alto**; los puntos que más
tiempo liberarían, si Jairo decide recortar, son las pruebas de navegador de la sesión del 001 (P-001-90, 93, 94) y la
fase 8 del 002, que ya están fuera del mínimo del 002.
