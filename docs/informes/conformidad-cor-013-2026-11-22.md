# Conformidad del plan de corrección COR-013 (auditoría única, regla 11)

**Fecha**: 2026-11-22 · **Auditor**: `verificador` (no participó en redactar ni aplicar COR-013)
**Objeto**: `docs/correcciones/COR-013.md`, estado `aplicada`; opción A con P1 (a) y P2 (a), aprobada por Jairo el
2026-11-22 (§6). Textos exactos: §2.1, bloques A a O. Lo que reportó el `corrector`: §7 y §8.
**Fase**: planes (Fase 3). No hay código que auditar: COR-013 no toca `src/`, `app/` ni `tests/`, así que no se
ejecutaron `ruff`, `mypy` ni `pytest`.

## Veredicto

**Conforme.** Ninguna no conformidad. Seis observaciones, ninguna bloqueante (sección 6).

| Corrección | Resultado |
|---|---|
| COR-013 | **verificada** |

## 1. Resumen

| Comprobación | Resultado |
|---|---|
| Los 25 puntos aplicados literalmente (A a M en los 13 archivos de §5, N y O de la sesión principal) | Sí: 131 de 131 textos comprobados (sección 2) |
| `trazabilidad.md`: 89 filas, «Tarea» comparada celda por celda con los tres planes | 89 de 89 coinciden; 0 celdas vacías en «Componente» o «Tarea» |
| Estados de `trazabilidad.md` | 89 en `diseñado`; 0 en `especificado` |
| `trazabilidad.md` con CRLF | 193 líneas, las 193 terminan en CRLF |
| `fixtures_builder` fuera de los registros (COR e informes) | 0 |
| `tests/e2e` | 0 fuera de los registros |
| `[NEEDS CLARIFICATION: NC-P00` en `docs/planes/` | 0 |
| FR-003-07 con cinco categorías en el plan 003 | Sí (sección 3.3) |
| Huella de `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual a la esperada |
| Contradicciones nuevas | Ninguna |
| `[NEEDS CLARIFICATION]` abiertos | NC-ARQ-1, que sigue abierto a propósito: se resuelve en T-001-09 (`docs/planes/README.md:27`; COR-013 §4) |

## 2. Aplicación literal de los 25 puntos

Método: para cada sustitución de §2.1 se buscó el texto nuevo, y donde había texto anterior se comprobó que ya no
está. Se compararon los textos con los espacios normalizados, porque el plan 001 corta las líneas (por ejemplo, A1
está en `001:190-191` en dos líneas). Resultado: 131 comprobaciones, 0 fallos.

| Bloque | Archivo | Puntos (§1.1) | Evidencia (línea del texto nuevo) | Resultado |
|---|---|---|---|---|
| A1 a A15 | `docs/planes/001-lectura-verificacion/plan.md` | 1, 2, 3, 4, 8, 9, 10, 11, 13, 16, 18, 21, 25 | A1 `:190`; A2 `:282`; A3 `:323`; A4 `:335-336`; A5 `:337`, `:830` (ya no queda «(COR-013)» ni «para COR-013»); A6 `:836`; A7 `:814-816` (con la frase de P2 (a)); A8 `:821`; A9 `:862-863`; A10 `:840`; A11 `:777`; A12 `:785-787`; A13 `:793`; A14 `:733`; A15 `:873` | Aplicado |
| B1 a B12 | `docs/planes/002-mapa-interactivo/plan.md` | 1, 3, 4, 5, 6, 8, 11, 12, 14, 15, 16, 22 | B1 `:145`, `:615`; B2 `:141-142`, `:149`, `:157`, `:520` (0 menciones de «e2e»); B3 `:226`, `:236`, `:567`; B4 `:384`, `:389`, `:630`, `:646`; B5 `:367` (ya no queda «, P-002-68.»); B6: etiquetas `[US-002-n]` en T-002-09 a T-002-42 y «Módulos:» en las 34 tareas listadas, comprobados tarea por tarea; T-002-44 `:515-517`; Notas `:642`, `:648`; B7 `:564`, `:601` (0 menciones de «en paralelo»); B8 `:265`, `:385`; B9 `:364`; B10 `:330`, `:332`, `:591`; B11 `:618-622`; B12 `:528-529` | Aplicado |
| C1 a C11 | `docs/planes/003-tablero-conclusiones/plan.md` | 1, 2, 4, 5, 6, 8, 10, 14, 15, 23, 24 | C1 `:144`, `:160`, `:194`; C2 `:165`, `:166`, `:172`, `:181`; C3 `:366`, `:377`, `:385`; C4 `:431`, `:436`, T-003-56; C5 `:474-478`, `:489`, `:107-108`; C6 `:101`, `:500`, `:502`, `:505`, `:611`; C7 `:570` (0 menciones de «en redacción»); C8 `:64`, `:66`, `:285`, `:303-304`, `:312`; C9 `:575-579`, `:591`; C10 T-003-95; C11 `:601` | Aplicado |
| D1, D2 | `docs/planes/README.md` | 4, 13 | D1 `:7`; D2 `:25-28` | Aplicado |
| E1 a E4 | `docs/arquitectura/arquitectura.md` | 3, 15, 17, 18 | E1 `:417`; E2 `:443`; E3 `:670`; E4 §6.4 (párrafo «NFR-000 por plan») | Aplicado |
| F1, F2 | `docs/arquitectura/adr/ADR-003-stack-web-python.md` | 16, 19 | F1 `:8` (ya no queda «2026-11-21» en la nota); F2: punto 2 reescrito y nota nueva `:11`; sin «aviso fijo» (variante P1 (b) no aplicada, como se decidió) | Aplicado |
| G1, G2 | `docs/specs/003-tablero-conclusiones/spec.md` | 24 | G1 `:239`; G2 `:75`; LF conservado | Aplicado |
| H1 a H4 | `docs/specs/trazabilidad.md` | 1, 3, 8, 15, 24 | H1 `:5`; H2: 89 filas en `diseñado`; H3 `:82`; H4: las 8 celdas (sección 3.1) | Aplicado |
| I | `docs/interfaz/bocetos/tablero.html` | 24 | `:120` encabezado «Sin diligenciar»; `:121` dos celdas `0` tras «1 (N.º 7)» y cuatro `colspan="6"` (0 `colspan="5"`) | Aplicado |
| J | `docs/interfaz/flujos.md` | 24 | `:260`, `:261` | Aplicado |
| K | `.claude/skills/calidad-python/SKILL.md` | 4 | `:43` | Aplicado |
| L | `prompts/PROMPT_FASE_3_planes.md` | 4 | `:13` | Aplicado |
| M | `.claude/skills/sistema-diseno-egm/references/pie-de-pagina.md` | 20 | Texto nuevo presente; «Los datos de este archivo están confirmados» ya no está | Aplicado |
| N | `CLAUDE.md` (sesión principal) | 5 | `:75` | Aplicado |
| O | `.claude/skills/analisis-impacto/references/invariantes.md` (sesión principal) | registro | `:128`, en «Decisiones del 22-nov-2026 (Fase 3, planes)» (`:108`): opción A, P1 (a), P2 (a), FR-003-07, constructor y estados | Aplicado |

Punto 7 (F3-07) no tenía cambio. Las seis celdas siguen bien: la comparación de la sección 3.1 no encuentra
diferencias.

Los 12 NC (puntos 21 a 23) figuran como decididos con la fecha 22-nov-2026: NC-P001-1 y NC-P001-2 (`001:814-816`,
`:821`, `:862-863`), NC-P002-1 a NC-P002-5 (`002:618-622`) y NC-P003-1 a NC-P003-5 (`003:575-579`). Su contenido es
igual al registro de Jairo en `invariantes.md:115-127`.

## 3. Consistencia del sistema completo

### 3.1 Columna «Tarea» de `trazabilidad.md` contra los planes (89 filas)

Método: de cada tarea de los tres planes se tomaron los ID FR/NFR/SC de su campo «Requisitos:» (rangos «X a Y»
expandidos, citas «(soporte)» y «(apoyo)» incluidas). Para cada requisito se armó el conjunto de tareas que lo
citan y se comparó con la celda «Tarea» de su fila.

- 89 filas, **89 coincidencias exactas**, 0 diferencias en ambos sentidos.
- Las 8 celdas de H4 coinciden con las tareas: NFR-000-01 (T-003-63), NFR-000-05 (T-003-90, T-003-91), FR-001-29,
  FR-002-18 y FR-002-19 (T-003-63), FR-002-12 (T-003-56), FR-003-06 y FR-003-14 (T-002-07).
- Los planes citan ID que no tienen fila: SC-000-06, 12, 13, 17, 18, 19; SC-001-02, 03; SC-002-01 a 05; SC-003-02,
  03, 06. Es lo esperado, porque la tabla principal solo tiene FR y NFR. No es un hueco.
- Las tareas que no tienen «Requisitos:» son las de escribir pruebas (T-002-05, 09 a 11, 17 a 19, 26 a 28, 33, 38,
  43) y la de pedir la verificación (T-002-50). Citan sus pruebas, y cada prueba cita su escenario, que es la
  convención aceptada en `conformidad-fase-3-2026-11-22.md:38`.

### 3.2 Arquitectura, ADR y planes

- **§6.4 frente a «Requisitos que cubre este plan»**: el plan 001 tiene NFR-000-01, 02, 03, 04, 05, 06, 09, 11, 12,
  13, 14, 15, 17, 18 y 19, que son los doce de E4 más la base de 04, 05 y 13. El plan 002 tiene 04, 05, 08, 09, 10, 13
  y 16. El plan 003 tiene 02, 03, 04, 05, 07, 08 y 13. Los tres coinciden con E4. NFR-000-01 en el 003 figura como «solo
  comprueba» (`003:107-108`), igual que FR-001-29, FR-002-12, FR-002-15, FR-002-18 y FR-002-19. NFR-000-03, 06 y 14 en
  el 002 figuran como «respeta sin ser su dueño» o como «(soporte)» y «(apoyo)» (`002:95-96`, `:181`, `:533`, `:536`).
- **Carpetas**: `tests/constructor.py` y `tests/navegador/` (`001:174`, `:178`, `:188`; `002:145`, `:149`; `003:144`,
  `:502`) y `app/cliente/` para M19 y `app/estaticos/` para M18 (`001:169-170`; `002:141-142`; arquitectura
  `:621`, `:626`). M23 `tests.constructor` está en `arquitectura.md:683` y `:720`. No queda ningún otro nombre.
- **M07 con `filtro`**: lo crea el 001 sin el parámetro (`arquitectura.md:443`; `001:777`), lo agrega T-002-07
  (`002:236`) y lo usa el 003 (T-003-23, T-003-54). El orden de los planes lo permite.
- **ADR-003**: en `docs/`, `.claude/skills/`, `CLAUDE.md` y `prompts/` (sin contar los registros) no queda ninguna frase
  que diga que la herramienta funciona sin guion. Las búsquedas fueron «formularios y enlaces reales», «sin
  JavaScript», «sin guion», «formularios reales» y «mejora progresiva»; la única coincidencia es el registro de
  `invariantes.md:128`. El punto 2 nuevo, T-002-24 (`002:364`) y M19 (`arquitectura.md:626-640`) dicen lo mismo.
- **Sesión y actividad**: el hito N2 (`001:783-787`), el README (`:7`) y M19 «Planes: 001 (carga, sesión, actividad,
  cierre)» dicen lo mismo: la actividad llega en la fase 8 del 001 (`001:685`).
- **ADR-001, 002, 004 y 005**: COR-013 no los toca. Ninguno contiene `fixtures_builder`, `e2e` ni la frase retirada de
  ADR-003.

### 3.3 FR-003-07 con cinco categorías

- Spec: FR-003-07 (`spec.md:239`) y US-003-2.4 (`spec.md:75`) toman como base los estudios del mapa y tienen cinco
  categorías. Son coherentes con el contrato §6 (`contrato-datos.md:235`, «Celda vacía o solo espacios → Sin
  diligenciar») y con el apéndice A, «Enfoque (en $M$): 1 Sin clasificar (N.º 7)».
- Plan 003: definición operativa (`:64`), P-003-24 (`:285`, «… y 0 sin diligenciar»), P-003-25 (`:286`, la suma por
  categorías es el número de estudios), FX-003-10 con enfoque vacío (`:176`), T-003-24 (`:303-305`), T-003-27
  (`:312`) y NC-P003-1 (`:575`). En los specs, los planes, la interfaz y la arquitectura no quedan «cuatro grupos»,
  «cuatro categorías» ni «cuatro columnas».
- Interfaz: el boceto tiene seis columnas (`tablero.html:120-121`) y `flujos.md:260-261` dice lo mismo, con los valores
  de v4 «0, 0, 0, 1 (N.º 7), 0», que salen del apéndice A.
- `trazabilidad.md:82` lleva la fuente nueva.

### 3.4 Pruebas primero y esperados

- P-001-01 se escribe antes del catálogo (`001:323`). P-001-02 queda declarada como prueba de caracterización
  (`001:335-336`).
- P-003-58 se escribe en T-003-52 (`003:436`), antes de T-003-56. P-003-65 a P-003-67 se escriben en T-003-60, antes
  de T-003-63. Las cuatro filas existen, una por ID (`003:431`, `:474-476`).
- Los esperados nuevos salen del apéndice A (FX-A: 27 documentos, $E$ = N.º 7, 10, 11, 13, 15, 16 y 24, $M$ = N.º 7,
  6 × 8 celdas, comparado con `contrato-datos.md:391-409`) o de fixtures descritos a mano (FX-003-06, «4 estudios del
  mapa», `003:172`; FX-12, «2 estudios del mapa … y 1 documento no empírico», `002:197`, de donde sale «2 de 3» en
  P-003-58). P-002-44 y P-003-45 ya no leen `data/raw/`. Solo la abren P-002-04, P-002-39 y P-003-15, en modo lectura
  (`002:255`, `:384`, `:646`; `003:243`).

## 4. Búsquedas

| Búsqueda | Coincidencias fuera de los registros | Coincidencias en los registros |
|---|---|---|
| `fixtures_builder` | 0 | COR-009:494, 495; COR-013 (8); `conformidad-fase-3-2026-11-22.md:107`, `:145`; `fase-3-resumen.md:44` |
| `tests/e2e` | 0 | COR-013:21, 95, 257, 277; `conformidad-fase-3-2026-11-22.md:108` |
| `[NEEDS CLARIFICATION: NC-P00` en `docs/planes/` | 0 | — |
| Filas «\| especificado \|» en `trazabilidad.md` | 0 (89 «\| diseñado \|») | — |
| Líneas de `trazabilidad.md` con CRLF | 193 de 193 | — |
| «lámina 7» y «tabla 3» en los archivos tocados | Solo en frases que prohíben usarlas (`001:59`, `:226`, `:854`, `:872`; `002:181`, `:633`; `003:48`, `:572`; `tablero.html:13`; `flujos.md:13`) | — |

## 5. Las tres desviaciones que reportó el `corrector`

| Desviación | Evidencia | Clasificación | Motivo |
|---|---|---|---|
| (a) «especificado» aparece una vez en `trazabilidad.md` | `trazabilidad.md:5`, el párrafo de H1 | **Observación** (OBS-1) | Ahí se nombra el primer estado de la escala, no el estado de una fila. El texto es el que Jairo aprobó tal cual (§2.1 H1). Las filas en ese estado son 0, que es lo que pide la comprobación. |
| (b) El plan 003 dice «La parte B (T-003-44) espera NC-P003-3» | `003:533`; también T-003-44, «según la forma que fije NC-P003-3» (`003:393`), frente a NC-P003-3 decidido (`003:577`) | **Observación** (OBS-2) | La condición de la que depende la frase ya se cumplió. La decisión está en el mismo plan y no se contradice: no cambia ninguna tarea, prueba ni requisito. La frase no estaba en §2.1, y el `corrector` hizo bien en no tocarla. Puede hacer creer que T-003-44 está bloqueada. Propuesta para una corrección posterior: «La parte B (T-003-44) sigue la forma decidida en NC-P003-3 (22-nov-2026).» y, en T-003-44, «según la forma decidida en NC-P003-3». |
| (c) `_plantilla-plan-spec.md` conserva «e2e» y «en paralelo» | `_plantilla-plan-spec.md:134` («unit / integración / propiedades / e2e»), `:96` y `:261` («en paralelo») | **Observación** (OBS-3) | La plantilla es genérica y no estaba en la lista cerrada de §5. Las dos frases con «en paralelo» explican la marca `[P]` y no hablan de ejecutar planes a la vez, así que son correctas. El tipo «e2e» no coincide con el tipo «navegador» que ahora usan los tres planes. Solo afectaría a planes nuevos, y no hay ninguno previsto. Propuesta: cambiar «e2e» por «navegador» en una corrección posterior. |

## 6. Observaciones

- **OBS-1**: ver la sección 5 (a).
- **OBS-2**: ver la sección 5 (b).
- **OBS-3**: ver la sección 5 (c).
- **OBS-4**: en el plan 001, la viñeta «Fixtures (M23)» de «Dependencias con otros módulos o specs» (`001:788-791`)
  enumera lo que el plan entrega a 002 y 003, pero no nombra FX-A (`instancia_ejemplo.xlsx`), aunque el catálogo
  (`001:282`) y T-001-07 (`001:323-324`) sí la incluyen y el plan 002 la espera (`002:567`). No contradice nada;
  queda incompleta. Propuesta: agregar «FX-A (`instancia_ejemplo.xlsx`)» a esa viñeta.
- **OBS-5**: el resumen «Requisito → tarea» del plan 003 (`003:603-612`) no tiene entradas para FR-001-29, FR-002-12,
  FR-002-18, FR-002-19 y NFR-000-01, aunque T-003-56 y T-003-63 los citan desde COR-013. Esto sigue la convención del
  plan: el resumen solo lista los requisitos propios, y esos cinco figuran como «solo comprueba» en `003:107-108`.
  `trazabilidad.md` sí los tiene. Propuesta opcional: una línea final en el resumen que remita a `003:107-108`.
- **OBS-6**: P-003-67 (`003:476`, texto aprobado en C5) pide la vista «resultado» después del plan 002. El plan 001
  dice que esa vista provisional existe «mientras no exista el mapa» y que «con el plan 002 la carga lleva al mapa»
  (`001:814-816`). Sin embargo, `GET /` sigue pidiendo `GET /vista/resultado` para recuperar la sesión (`001:200`), y el
  plan 002 no dice si esa ruta se conserva, se retira o se redirige (0 menciones de `vista/resultado` en
  `002-mapa-interactivo/plan.md`). Hoy no hay contradicción, pero falta decir qué pasa con la ruta cuando llegue el
  mapa. Propuesta: que el plan 002 lo diga en una corrección posterior, y que P-003-67 se lea como «las vistas que
  existan».

Ninguna de las seis cambia lo que la herramienta lee, calcula o muestra, ni contradice una regla de `CLAUDE.md`. Si
Jairo quiere atenderlas, por la regla 11 van en una corrección nueva, no en COR-013.

## 7. Reglas inviolables

| Regla | Resultado |
|---|---|
| 1. Matriz intacta | Huella SHA-256 igual a la registrada; ningún archivo de `data/raw/` en los cambios de COR-013 (§7) |
| 3. Sin datos no verificados | R-7 lleva ahora su fuente (`001:836`); los NC decididos coinciden con `invariantes.md`; FR-003-07 cita la decisión de Jairo |
| 7. Sin cifras de la lámina 7 | Los esperados nuevos salen del apéndice A o de fixtures descritos a mano (sección 3.4) |
| 8. Textos para el equipo | El único texto nuevo que el equipo verá es el encabezado «Sin diligenciar», que es una categoría del contrato §6 |
| 9. Hallazgos de la matriz | Ningún texto tocado menciona la tabla 3 ni hallazgos de la matriz |
| 10. Fuera de alcance | Nada sobre la vista de red ni el módulo no supervisado |
| 11. Flujo de corrección | Hubo propuesta, aprobación de Jairo (§6) y aplicación por el `corrector` (§7); N y O los aplicó la sesión principal; esta es la auditoría única del plan |

## 8. Resultado para la sección 9 de COR-013

COR-013: **verificada**, 2026-11-22. Las 25 partes están aplicadas tal como se aprobaron, y el sistema completo
(specs, arquitectura y ADR, interfaz, los tres planes y su índice) es coherente. Las 89 filas de «Tarea» coinciden con
los planes y la matriz está intacta. No hay no conformidades. Quedan seis observaciones no bloqueantes (OBS-1 a OBS-6),
que pueden atenderse en una corrección posterior si Jairo lo decide.
