# Informe de conformidad: cierre de la Fase 1 y del plan de corrección COR-009

**Fecha**: 2026-11-21
**Auditor**: `verificador`. No participó en redactar, aprobar ni aplicar lo auditado.
**Lector**: Jairo. Contiene información interna (secciones 2.5 y 5) y no se comparte con el equipo.
**Base**: `docs/informes/conformidad-plan-correccion-2026-11-21.md` (COR-001 a COR-008 verificadas; hallazgos
H-04 a H-56).
**Alcance**: COR-009 completa y su efecto conjunto sobre el sistema. Es la única pasada del `verificador` sobre este
plan de corrección (regla 11 de `CLAUDE.md`).
**Método**: `git diff HEAD` (HEAD = b954d30) sobre el árbol de trabajo, con cada bloque atribuido a su origen.
Comprobación por programa de los textos citados en las secciones 5 y 6 de COR-009 frente al repositorio. Recuento por
programa de identificadores, fuentes, cobertura y fines de línea, leyendo bytes. Matriz leída en modo solo lectura,
con lectura directa del XML del archivo y sin bibliotecas que escriban, y hash calculado antes y después. Texto de los
dos PDF de `docs/fuentes/` extraído en modo lectura con el entorno `.venv` del proyecto. No hay código: `src/`, `app/`,
`tests/` y `data/fixtures/` solo tienen `.gitkeep`, así que no se ejecutan `ruff`, `mypy` ni `pytest`.

## 1. Veredicto

**COR-009 no queda `verificada` todavía.** Se aplicó literalmente y solo sobre su lista cerrada, con una excepción. Al
reescribir FR-002-12, la aplicación borró el salto de línea que separaba ese requisito de FR-002-13. FR-002-13 quedó
pegado al final de la línea de FR-002-12 (`002:240`) y dejó de ser un elemento de la lista de requisitos (**H-57,
bloqueante**). El resto de la aplicación es conforme. Resultado propuesto: **no verificada**. Pasa a `verificada`
cuando una corrección mecánica restituya ese salto de línea (sección 7).

**La Fase 1 todavía no puede cerrarse.** Faltan dos cosas, las dos de corrección rápida:
1. **H-57 (bloqueante)**: restituir FR-002-13 como requisito propio.
2. **H-58 (mayor, regla 3)**: `pie-de-pagina.md:46` sigue citando como fuente el formato de vinculación, que no está
   en `docs/fuentes/`. Los datos que respalda sí constan en el documento general de la propuesta (portada).

Con las dos resueltas en una COR-010 y verificadas en su cierre, la Fase 1 queda en condiciones de cerrarse. Los
hallazgos menores (H-59 a H-70) no impiden cerrarla. Los 10 NC anteriores quedaron resueltos, con **0 NC abiertos** en
`docs/specs/`. Los specs siguen en v0 hasta el acuerdo de alcance con la investigadora principal (`000:4`), como
corresponde.

## 2. Comprobaciones obligatorias

### 2.1 Integridad

| Control | Resultado | Evidencia |
|---|---|---|
| SHA-256 de la matriz | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual antes y después de leerla, igual al de `contrato-datos.md:369` (apéndice A) | `sha256sum data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` |
| `data/raw/` y `docs/fuentes/` | Sin cambios: `git status --porcelain docs/fuentes data/raw` vacío; ninguno aparece en `git diff HEAD --stat` | — |
| Árbol de trabajo | 21 archivos modificados, 1 borrado (`docs/planes/_plantilla-plan.md`) y 5 sin seguimiento (`COR-009.md`, `conformidad-plan-correccion-2026-11-21.md`, `hallazgos-matriz-para-equipo.md`, `_plantilla-plan-spec.md`, `RETOMAR_2026-11-21.md`) | `git status --porcelain` |
| Fines de línea | `trazabilidad.md`: 10 977 bytes, 191 `\n`, 191 `\r\n`, sin `\r` sueltos y sin BOM. Los demás specs y `plan-modulo/SKILL.md`: 0 `\r` (LF), como en HEAD | lectura de bytes |

### 2.2 Atribución de cada bloque de `git diff HEAD`

| Archivo | Bloques | Atribución |
|---|---|---|
| `contrato-datos.md` | §2.1 (`:33-34`); §3.1, dos viñetas (`:75-76`); §4.1, frase de $v_{\text{emp}}$ y $v_{\text{IE}}$, columna «Se usa en», dos viñetas y búsqueda de anclas (`:127-146`); §5 «Filtros» (`:209`); §7.4 (`:272`); §9, fila nueva (`:331`) y fila de rechazo (`:341`); apéndice B, aviso, viñeta y NC (`:409-426`) | COR-009: I-05/07, Q6, H-33/H-50 y Q4, I-01, Q2, I-10, I-07 e I-02 |
| `000-vision-alcance.md` | Actores (`:26`); NFR-000-17 (`:90`); NFR-000-19 (`:92`); SC-000-11, 17 y 19; «Puntos abiertos» (`:120`); notas `:133`, `:136` y `:137` | COR-009: H-38, I-04 y Q7, I-03, H-30, Q7, I-03, I-04, Q1, H-18 y H-31 |
| `001-lectura-verificacion/spec.md` | US-001-2 (`:74`); prueba independiente de US-001-4 (`:171`); US-001-4.7 y 4.9 a 4.12; US-001-3.3; US-001-3.17; US-001-5 (`:337-338`); FR-001-12; FR-001-29; entidad «Advertencia»; SC-001-04 | COR-009: H-38, H-21, I-05/06/07 y Q7, H-30, Q2, Q7, H-04, I-05/06/07 y Q7 |
| `002-mapa-interactivo/spec.md` | US-002-4.5, 4.6, 4.11 y 4.13; US-002-3.2 y 3.3; FR-002-12 (con Q8); FR-002-18; FR-002-19 | COR-009: I-08, I-09, I-01, H-30 y Q8. **El salto de línea anterior a FR-002-13 se perdió (H-57)** |
| `003-tablero-conclusiones/spec.md` | Historia 1 (`:10-11`); US-003-1.1 y 1.4; US-003-3.5; Edge Cases (`:223-224`); FR-003-01, 14 y 21; SC-003-06 | COR-009: H-21, H-34, I-10, Q5 y H-41 |
| `trazabilidad.md` | 8 fuentes y 8 coberturas | COR-009, 5.B, 5.D, Q2, Q5 y Q7 |
| Skills `contrato-matriz` y `referencia-v4.md` | Observación interna (`SKILL.md:64`); fórmulas (`referencia-v4.md:50`) | COR-009: I-02 y 5.E |
| `sistema-diseno-egm/SKILL.md`, `pie-de-pagina.md` | Cajonera (`:20`) y cabecera (`:42`); fuentes del colofón (`:46-47`) | COR-009: H-32 y Q3 |
| `calidad-python`, `plan-modulo`, `trazabilidad` (skills); `implementador.md`; prompts de las fases 2 y 3; `README_KIT.md`; `README.md` | Versión de Python; plan por spec; ejemplo `T-001-04`; pendientes del kit | COR-009: H-56, I-12, Q9, Q11 y H-55 |
| `_plantilla-plan-spec.md` (sin seguimiento) | `:9`, `:114` y `:258` | COR-009: Q10 = 2, emoji y Q9 = 1 |
| `CLAUDE.md` | Regla 9 reescrita (`:33-42`); `:53` y `:68` | Sesión principal: regla 9 por orden de Jairo del 21-nov-2026; I-12 |
| `invariantes.md` | `:39`, `:45`, `:49`; sección «Decisiones del 21-nov-2026» (`:51-68`); «Pendientes» (`:71`) | Sesión principal: 5.C. Amplía el texto de 5.C con las respuestas Q1 a Q11 de la sección 6, con el mismo contenido (ver H-67) |
| `docs/planes/_plantilla-plan.md` | Borrado | Sesión principal: Q10 = 2 (`COR-009:354`) |
| `COR-005.md` | Estado (`:3`); ratificación (`:446`); sección 9 (`:477-499`) | Ratificación de Jairo del 21-nov-2026 y sección 9 del plan anterior (sesión principal) |

**Ningún bloque queda sin justificación.** El borrado de la plantilla lo hizo la sesión principal, y no el
`corrector`, porque el corrector no tiene herramienta para borrar. Está previsto en `COR-009:113` y aprobado en Q10,
así que no contradice la regla 11.

### 2.3 COR-009: aplicación literal (pregunta 1)

- **Textos.** Se comprobaron por programa las 36 citas en bloque y los escenarios de 5.B a 5.E, y las citas entre
  comillas de 5.D y de las opciones elegidas en la sección 6. Todas están en su destino, salvo cuatro diferencias:
  - Dos son solo el corte de línea del archivo de destino (`003:10-11` y `contrato:145-146`).
  - Dos son inserciones de la frase de Q7: en FR-001-29 y en US-001-5, donde la «o» pasa a coma para enumerar cuatro
    formas.
- **Respuestas de la sección 6**:
  - Q1 = 1 (`000:133`); Q2 = 1 (`contrato:272`, US-001-3.17, `traz:139`); Q4 = 1 (`contrato:141-142`); Q5 = 1
    (FR-003-21, `traz:94`); Q6 = 1 (`contrato:75-76`).
  - Q7 = 1: FR-001-29; NFR-000-17; SC-000-17; `001:337-338`; US-001-4.7; cobertura de NFR-000-17.
  - Q8 = 1 (FR-002-12); Q9 = 1 (`_plantilla-plan-spec.md:258`); Q10 = 2 (`:9` y el borrado); Q11 = 1
    (`PROMPT_FASE_3_planes.md:14`).
  - Q3 = 3: `pie-de-pagina.md:13-14` intactas; `:47` nueva. Ver la desviación 1.
- **Lista cerrada.** El `corrector` editó solo los archivos 1 a 15 y 17 a 20 de 5.A. No tocó `CLAUDE.md`,
  `invariantes.md`, `verificador.md`, `RETOMAR`, `PROMPT_FASE_1`, `hallazgos-matriz-para-equipo.md`, COR-001 a
  COR-008 ni `docs/informes/`.
- **Sección 7.** Coincide con el repositorio, archivo por archivo. Incluye las 8 fuentes y las 8 coberturas de
  `trazabilidad.md` y el detalle «se quita “tutora” y “director”» de `pie-de-pagina.md:46`.
- **Sección 8.** Todas las búsquedas se reproducen:

| Búsqueda | Sección 8 | Encontrado |
|---|---|---|
| `NEEDS CLARIFICATION` en `docs/specs/` sin `_plantilla/` | 0 | 0 |
| `Propuesta sin fuente` en specs y `trazabilidad.md` | 0 | 0 |
| `15 MB` / `15 728 640` en specs | 0 / 1 línea | 0 / 1 línea (`000:92`) |
| `45 minutos` | 7 líneas (000: 2; 001: 5) | 2 y 5 |
| `aviso` en specs | 0 | 0 |
| `T-lectura` | 0 fuera de COR-009 | 0 |
| `_plantilla-plan.md` vigente | 0; registro en `invariantes.md:67` | `invariantes.md:67` |
| Escenarios | 120 (61, 29, 30) | 120 (61, 29, 30) |

  Pero la sección 8 tiene defectos de registro (H-61). Repite cuatro viñetas con cifras distintas
  (`COR-009:404-407`, con 119 escenarios, frente a `:400-403`, con 120). Además dice «Sin desviaciones» (`:417`),
  cuando el corrector informó tres. Su comprobación «Ningún FR perdió su escenario» es cierta, pero no detectó H-57.

**Juicio sobre las tres desviaciones que informó el corrector:**
1. **`pie-de-pagina.md:46-47`: aceptable como aplicación, pero deja abierto H-58.** Q3 = 3 da un solo texto para
   `:46-47`. El comentario de usted («También se quita “tutora” de `:46`») supone que `:46` sigue existiendo, así que
   conservar `:46` sin «tutora» ni «director» es una lectura razonable de lo aprobado. El problema es de fondo, no de
   aplicación. **Sí: `:46` sigue citando el «formato de vinculación de semillerista (25-sep-2026)» como fuente de
   «Grupo, semillero y nombre del proyecto».** Ese formato no está en `docs/fuentes/`: solo se menciona en
   `estado_proyecto_2026-10-31.md:8`, que registra sus actividades y no su contenido. Es la regla 3 (H-58).
2. **`001:313` (hoy `:337-338`): no es una desviación.** Q7 pide ese cambio de forma expresa (`COR-009:454`). Cambiar
   «o tras 45 minutos» por «, tras 45 minutos» es lo mínimo que hace falta para enumerar cuatro formas. Conforme.
3. **`plan-modulo/SKILL.md` reescrito entero: aceptable.** El diff solo cambia las líneas pedidas (`:3`, `:6`, `:11`,
   `:15`, `:18`, `:20` y `:30`), con la unión de líneas que exigen los textos nuevos. Los finales de línea siguen en LF
   (0 `\r`). Fuera de esas líneas, el contenido es el mismo. Quedan restos de «módulo» que COR-009 no pidió cambiar
   (H-62).

**Apéndice A.** No cambia, como afirma COR-009 §3. La lectura de la matriz confirma las fórmulas de 5.E:
- B6 y J6 condicionan por D, G y H (B6 también por L).
- B16 y J16 añaden J = «Evaluación de impacto».
- B26 y J26 aplican `"Sí*"` sobre M.
- B36 y B37 condicionan solo por D y J. Ver H-65.

### 2.4 Identificadores, fuentes y cobertura (pregunta 2)

| Elemento | Recuento | Detalle |
|---|---|---|
| Requisitos | **89** | FR-001: 29; FR-002: 19; FR-003: 22; NFR-000: 19 |
| SC | **35** | SC-000: 19; SC-001: 5; SC-002: 5; SC-003: 6 |
| Escenarios | **120** | 001: 61; 002: 29; 003: 30. Coincide con lo que dice el corrector. Hay 8 nuevos: US-001-3.17, US-001-4.9 a 4.12, US-002-3.3, US-002-4.13 y US-003-3.5 |
| Historias | 15 | 5 por spec |

- **Unicidad y huecos.** Ningún ID se define dos veces. No hay huecos en FR, NFR, SC ni escenarios. FR-002-13 está
  definido, pero no al inicio de línea (H-57).
- **Referencias colgantes.** Ninguna. Se revisaron todas las menciones de FR, NFR, SC y US en los cinco specs y en
  `trazabilidad.md`.
- **Fuente.** Los 89 requisitos tienen `[Fuente: …]`. FR-002-18 ya tiene fuente (decisión de Jairo, 21-nov-2026). Ver
  H-60, sobre cuatro reglas nuevas sin fecha propia.
- **Cobertura.** Los 89 tienen escenario o SC, y todo lo citado existe. Hay una cobertura parcial: la cláusula de Q8
  de FR-002-12 (H-59).

### 2.5 Reglas inviolables (pregunta 5)

- **Regla 1.** Matriz intacta (2.1). Ninguna escritura en `data/raw/`.
- **Regla 3.** Incumplida en `pie-de-pagina.md:46` (H-58). Las decisiones de la sección 6 constan con fecha en
  COR-009 y en `invariantes.md:51-68`. Cuatro textos nuevos del contrato y de FR-002-12 no la repiten (H-60). La cita
  de 3ie de `pie-de-pagina.md:28-30` sí está verificada, porque coincide con la lista de referencias del documento
  general de la propuesta: «International Initiative for Impact Evaluation (3ie). (2019). Building Peaceful Societies
  Evidence Gap Map […] Licencia CC BY-NC-SA 4.0». El NC que dejó el analista en `COR-009:439` queda resuelto sin
  cambios. `COR-005:490` fecha una edición «entre el 3 y el 4-nov-2026» sin respaldo para el 4-nov (H-66).
- **Regla 5.** `sistema-diseno-egm/SKILL.md:20` ya dice «ningún estudio registrado» y «brecha provisional». Conforme.
- **Regla 6.** Ningún texto nuevo usa porcentajes. Los escenarios nuevos usan «n de N». Conforme.
- **Regla 7.** Ningún texto nuevo usa la tabla de `presentacion_equipo_2026-10_texto.md:96-104`. Los escenarios
  nuevos describen su propia matriz sintética (US-002-4.13, US-003-3.5, US-001-3.17, US-001-4.9 a 4.12) o el apéndice
  A. Las menciones de «lámina 7» del repositorio son prohibiciones o comprobaciones. Conforme.
- **Regla 9 nueva (`CLAUDE.md:33-42`).** La tabla 3 de la hoja EGM no aparece en ningún texto ni interfaz para el
  equipo. No hay interfaz construida, y `docs/interfaz/` solo tiene `.gitkeep`. Aparece en textos internos para usted
  o para los subagentes:
  - `contrato:407-426` (apéndice B, «Interna — no publicar»);
  - `contrato-matriz/SKILL.md:64` y `referencia-v4.md:47-51`;
  - `invariantes.md:39` y `:66`;
  - `CLAUDE.md:41`;
  - `README_KIT.md:53`;
  - `hallazgos-matriz-para-equipo.md:35`, B-01;
  - informes, correcciones y notas fechadas.

  El apéndice B y la skill ya siguen la regla nueva. Hay un riesgo de proceso al compartir el contrato (H-69).
- **Regla 11.** Se respetó el flujo: propuesta del analista, aprobación de usted (`COR-009:342-358`), aplicación del
  corrector y esta auditoría única. La sesión principal solo editó lo que 5.A le asigna, con el texto aprobado.

## 3. `trazabilidad.md` (pregunta 3)

- **Estructura.** 191 líneas, todas CRLF, y 89 requisitos en cada tabla, sin filas repetidas, faltantes ni
  sobrantes. Todo sigue en `especificado`, con las columnas de componente, tarea y prueba vacías, como corresponde a
  la fase.
- **Fuentes.** 88 de 89 coinciden literalmente con el spec. La de FR-002-12 (`traz:66`) es equivalente: resume las
  tres fechas y muestra «(provisional)», lo que cierra H-53.
- **Cobertura.** Las 8 celdas cambiadas citan escenarios que existen. Las 89 filas tienen al menos un escenario o SC.

## 4. `[NEEDS CLARIFICATION]` y marcas (pregunta 4)

- **`docs/specs/` sin `_plantilla/`: 0.** Se cumple el esperado. Los 10 del informe anterior están resueltos:
  `contrato:209` y `:426`, `000:120`, FR-001-29 (tres), FR-002-12, FR-002-19 y `003:224`.
- **Skills y agentes.** No queda ningún NC abierto. Las menciones de `especificacion-srs`, `plan-modulo`,
  `protocolo-correccion`, `trazabilidad`, `arquitecto.md` y `analista-impacto.md` son instrucciones de uso, no marcas.
  El de `calidad-python/SKILL.md:24` se cerró.
- **`[Propuesta sin fuente]`**: 0 en specs y skills.
- **`[POR CONFIRMAR]`**: una sola marca de dato, `pie-de-pagina.md:21` (su nombre y su rol en el colofón). Las
  menciones de `pie-de-pagina.md:4` y `disenador-front.md:30` explican la regla.

## 5. Hallazgos

Severidad: **bloqueante** impide dar por verificada la corrección; **mayor** impide cerrar la Fase 1 o empezar la
siguiente sin corregirlo; **menor**, ninguna de las dos. Ningún hallazgo propone cambios en la matriz, sus columnas,
listas, dimensiones, intervenciones, criterios ni metodología.

### Bloqueante

**H-57. FR-002-13 quedó pegado a FR-002-12 (`002:240`).** La línea termina en «…[Fuente: decisión de Jairo,
3-nov-2026. Decisión provisional, a discutir con el equipo.]- **FR-002-13**: Con un filtro activo, la herramienta MUST
mantenerlo siempre visible…». En HEAD, FR-002-13 tenía línea propia (`git show HEAD:…:231`), y el archivo pasó de una
línea por requisito a 264 líneas con dos requisitos en una. I-08 (`COR-009:198-200`) solo pedía reemplazar el texto de
FR-002-12 y quitar su NC final. FR-002-13 no estaba en la lista de cambios. Al mostrar el documento, FR-002-13 queda
dentro de FR-002-12, y una búsqueda de requisitos por inicio de línea no lo encuentra. Ese es el método que usarán los
planes de la Fase 3. **Corrección propuesta**: restituir el salto de línea antes de `- **FR-002-13**`, sin cambiar
ningún carácter más. Es mecánica y no necesita ninguna decisión nueva, porque devuelve el texto aprobado.

### Mayor

**H-58. `pie-de-pagina.md:46` cita una fuente que no está en el repositorio (regla 3).** «Grupo, semillero y nombre
del proyecto: formato de vinculación de semillerista (25-sep-2026).» El formato no está en `docs/fuentes/`. Los tres
datos sí constan en las fuentes:
- la sigla del grupo y el semillero, en la portada del documento general de la propuesta («Semillero Desarrollo Rural
  y Economía Solidaria · Grupo GIOE · Universidad del Magdalena»);
- el nombre del proyecto, en la presentación del equipo (`estado_proyecto_2026-10-31.md:11`).

El `disenador-front` toma esta guía en la Fase 2. **Corrección propuesta** (texto para `:46`): «- Sigla del grupo y
semillero: documento general de la propuesta (portada). Nombre del proyecto: presentación del equipo (octubre de
2026).». La línea `:47` no cambia.

### Menores

**H-59. «Sin nivel» con solo documentos no empíricos (Q8): una contradicción y un hueco de cobertura.**
- `003:224` sigue diciendo que la entrada «Sin nivel» se ofrece «cuando existan esos estudios (FR-002-12)», y
  FR-002-12 (`002:240`) la ofrece también con documentos no empíricos.
- Ningún escenario comprueba la cláusula de Q8, y US-003-3.5 la evita a propósito (`COR-009:224`).
- Ningún texto dice qué muestra el mapa en esa entrada cuando no agrupa estudios (`COR-009:458`).

Propuesta: en `003:224`, «cuando existan esos estudios o documentos no empíricos (FR-002-12)», y un escenario con
documentos no empíricos y ningún estudio del mapa sin nivel.

**H-60. Cuatro reglas nuevas no llevan la fecha de su decisión.**
- Q6 (`contrato:75-76`) queda bajo la fuente del 1-nov-2026 (`:70`).
- Q4 (`:141-142`) queda bajo la del 2-nov-2026 (`:135`).
- Q2 (`:272`) queda bajo «decisión de Jairo, 2-nov-2026».
- La cláusula de Q8 de FR-002-12 queda bajo «decisión de Jairo, 3-nov-2026».

Las cuatro son del 21-nov-2026 (`COR-009:345-352`). Además, los casos de Q4 y Q6 no están en la tabla de casos borde
del contrato (§9), que es la que recorre SC-001-02, y no tienen escenario. Propuesta: agregar «decisión de Jairo,
21-nov-2026» a esas cuatro fuentes y dos filas en §9.

**H-61. Defectos de registro en COR-009 §8.** Hay viñetas duplicadas con cifras distintas (`:400-403` frente a
`:404-407`, con 120 y 119 escenarios), y «Sin desviaciones» en `:417` frente a las tres que informó el corrector.
Propuesta: que la sección 9 lo deje anotado.

**H-62. Restos de «módulo» y una regla de orden distinta de la plantilla.**
- `CLAUDE.md:80` («código y pruebas de un módulo según su `plan.md`»).
- `implementador.md:12` («implementa módulos»).
- `plan-modulo/SKILL.md:22` («lo propio del módulo»).
- `trazabilidad/SKILL.md:3` («antes de dar un módulo por terminado») y `:31` («todo requisito del módulo tiene
  tarea»).
- `PROMPT_FASE_3_planes.md:12` y `plan-modulo/SKILL.md:16` piden «la sección de pruebas completa antes que las
  tareas». La plantilla pone las pruebas dentro de cada historia (`_plantilla-plan-spec.md:98-110`), con tareas de
  preparación y base antes (`:105-120`).

No cambian lo que se decidió, pero pueden confundir al redactar los planes. Propuesta: «plan» en lugar de «módulo», y
«en cada historia, las pruebas antes que su implementación».

**H-63. `hallazgos-matriz-para-equipo.md` no cuadra con el contrato corregido** (pregunta 8).
- **Líneas desplazadas.** Las citas de línea son anteriores a COR-009:
  - A-01: «§9 (línea 331)» es hoy `:336`, y «apéndice A, líneas 395-396» es hoy `:400-402`.
  - A-02: «línea 386» es hoy `:388` y `:390`.
  - A-03: «`contrato-datos.md`:205» es hoy `:209`, y «392-395» es hoy `:397-400`.
  - A-04: «línea 398» es hoy `:403`.
- **Tratamiento incompleto.** A-03 aplica bien la decisión 10, pero en «Especificado en» faltan FR-003-14 y la fila
  nueva de §9 (`contrato:331`). Tampoco dice que los documentos «Empírico pendiente» de A-03 (N.º 10, 11, 13, 15, 16
  y 24), con el nivel vacío, sí salen con el filtro de nivel activo (`COR-009:225`).
- **Formato.** Una línea en blanco (`:37`) separa B-03 de la tabla del grupo B, así que B-03 no se muestra como fila.
- **Estado.** B-02 y B-03 tienen el estado «No aplica», que no es ninguno de los tres que fija la regla 9
  (`CLAUDE.md:38`).

Lo demás cuadra con los specs: B-01 con el apéndice B y §7.6; A-02 con FR-001-13; A-04 con FR-001-16 y FR-001-27;
B-03 con COR-009 5.E. Propuesta: citar secciones en lugar de líneas. El archivo no se reescribe en esta auditoría.

**H-64. `000:136` cita el umbral $N_{min}$ en «§6.2 a §6.4».** El texto del documento técnico pone la precondición
$N \ge N_{min}$ también en §6.7 (combinaciones de intervenciones, columnas G y H). El $n_{min}$ de §6.6 es otro
parámetro, el de las proporciones. Propuesta: «§6.2 a §6.4 y §6.7».

**H-65. `referencia-v4.md:50` describe mal el bloque 4.** El texto dice que se usan «las columnas D […], G y H […] y
la de cada dimensión (L a S)», y que «los bloques 2 y 4 condicionan además por la columna J». B36 y B37 condicionan
solo por D y J. Además, «filas 2 a 200 […] (rango fijo 2:200)» repite el dato. Propuesta: «El bloque 4 condiciona
solo por D y J.».

**H-66. `COR-005:490` registra que `invariantes.md` se editó «entre el 3 y el 4-nov-2026».** La edición ya está en el
commit b954d30, del 3-nov-2026 a las 13:05 (`git log`), así que el 4-nov no tiene respaldo (regla 3). Propuesta:
«a más tardar el 3-nov-2026 (commit b954d30)».

**H-67. `invariantes.md` conserva textos anteriores sin remitir a los del 21-nov.**
- `:38` dice que un filtro está activo «solo cuando se aplica» y da tres formas de terminar la sesión.
- `:46` agrega «Sin nivel» solo «cuando existan esos estudios».
- `:39` une dos oraciones sin puntuación («(21-nov-2026) y no se anota»).

La sección `:51-68` es correcta y prevalece. Propuesta: añadir «(ver Decisiones del 21-nov-2026)» en `:38` y `:46`.
Lo edita la sesión principal.

**H-68. `README_KIT.md:51` atribuye al equipo el stack web.** Dice «Stack web (ADR-003) y despliegue (ADR-004), que
el equipo decide después de la demostración». `000:124` solo deja al equipo el despliegue. El stack lo propone el
ADR-003 (`arquitecto.md:24`, `PROMPT_FASE_2_arquitectura.md:12`). Propuesta: «Stack web (lo propone el ADR-003).
Despliegue (ADR-004), que el equipo decide después de la demostración.».

**H-69. El apéndice B viaja dentro de un spec que se compartirá con la investigadora principal.** El acuerdo de
alcance (`000:4`) se hará sobre los specs, y `contrato-datos.md:407-426` contiene la observación de la tabla 3. La
regla 9 prohíbe mencionarla en cualquier texto para el equipo antes del informe final aprobado (`CLAUDE.md:40-42`).
Ya lo advertía `fase-1-resumen.md:187`. Propuesta: compartir una copia del contrato sin el apéndice B. Es una pauta
de proceso; no cambia ningún spec.

**H-70. Queda un uso de «celda vacía» para una celda del mapa.** Es el título de US-002-4.2 (`002:105`), «Celda vacía
por el filtro». COR-009 corrigió ese doble sentido en 003 (H-34), pero no aquí. Propuesta: «Celda sin estudios por el
filtro».

## 6. Estado de los hallazgos abiertos del informe del 21-nov (pregunta 7)

| ID | Estado | Evidencia |
|---|---|---|
| H-04 | Cerrado | FR-001-12 (`001:410`), entidad (`:437`), SC-001-04 (`:448`) |
| H-05 | Cerrado | `000:133`, con fuente del 21-nov-2026 (Q1) |
| H-18 | Cerrado, con una precisión | `000:136`; ver H-64 |
| H-21 | Cerrado | `003:10-11`; US-003-1.4 (`003:34-37`); `001:171` |
| H-28 | Cerrado | `contrato:272`; US-001-3.17; `traz:139`. Fecha en H-60 |
| H-29 | Cerrado en cuanto a los datos de `:13-14` (Q3 = 3, `pie:47`) | Sigue la cita sin respaldo de `:46`: H-58 |
| H-30 | Cerrado | SC-000-11 (`000:108`); US-001-3.3 y `traz:146`; US-002-3.3 y `traz:158`; FR-002-18 (`002:245`); H-52 |
| H-31 | Cerrado | `000:137` |
| H-32 | Cerrado | `sistema-diseno-egm/SKILL.md:20` y `:42` |
| H-33 | Cerrado | `contrato:127`, `:133` y `:141-146` |
| H-34 | Cerrado en 003 | FR-003-01 (`003:233`), US-003-1.1. Queda `002:105` (H-70) |
| H-37 | Cerrado | FR-003-21 (`003:253`), `traz:94` |
| H-38 | Cerrado | `001:74`; `000:26` |
| H-39 | Cerrado | `contrato:75-76`. Fecha y §9 en H-60 |
| H-40 | Cerrado | `traz:143` (SC-001-02); NC retirados |
| H-41 | Cerrado | SC-003-06 (`003:273`) |
| H-48 | Cerrado | `COR-005:490`; precisión de fecha en H-66 |
| H-49 | Cerrado | `COR-005:446` |
| H-50 | Cerrado | `contrato:133` |
| H-51 | Cerrado | Q7: FR-001-29; NFR-000-17 (`000:90`); SC-000-17; US-001-4.7 |
| H-52 | Cerrado | US-001-4.9 |
| H-53 | Cerrado | `traz:66` («provisional»); no quedan NC que mostrar |
| H-54 | Cerrado por este encargo | `docs/informes/fase-1-resumen.md`, reescrito hoy |
| H-55 | Cerrado | `README_KIT.md:48-53`; precisión en H-68 |
| H-56 | Cerrado | `calidad-python/SKILL.md:24` |

**COR-009 cierra 24 de los 25 hallazgos abiertos.** H-29 queda cerrado en sus datos, pero con la cita de `:46`
pendiente (H-58). El resumen de la fase (H-54) se rehízo en este mismo encargo.

## 7. Resultado para la sección 9 de COR-009

| COR | Resultado | Fecha | Motivo |
|---|---|---|---|
| COR-001 a COR-008 | `verificada` (sin cambio) | 2026-11-21 | COR-009 no altera lo que dejaron. Las reglas que COR-009 amplía son de COR-004 y COR-005: el contrato §5, FR-001-29, NFR-000-17 y FR-002-12 |
| COR-009 | **no verificada** | 2026-11-21 | H-57 (bloqueante). Pasa a `verificada` cuando se corrija H-57 |

**Texto propuesto para la sección 9 de COR-009:**

> **No verificada** el 21-nov-2026 (`docs/informes/conformidad-fase-1-cierre-2026-11-21.md`), en la auditoría única
> de cierre de este plan de corrección.
>
> - **Conforme.** La aplicación de 5.B a 5.E y de las respuestas Q1 a Q11 de la sección 6 es literal. Solo se
>   editaron los archivos 1 a 15 y 17 a 20 de 5.A. Todo bloque de `git diff HEAD` se atribuye a esta corrección, a
>   la sesión principal (CLAUDE.md, `invariantes.md`, borrado de `_plantilla-plan.md`) o a la ratificación y la
>   sección 9 de COR-005.
> - **Búsquedas y recuentos.** Se reproducen las búsquedas de la sección 8. Hay 89 requisitos, 120 escenarios
>   (61, 29 y 30) y 35 SC, con ID únicos, sin huecos ni referencias colgantes, y 0 NC en `docs/specs/`.
>   `trazabilidad.md` tiene 191 líneas, todas CRLF, y 89 requisitos por tabla.
> - **Integridad y reglas.** Matriz intacta (SHA-256 `7E1714DE…C3A1`) y `docs/fuentes/` sin cambios. Se cumplen las
>   reglas 7, 9 y 11. El apéndice A no cambia.
> - **Hallazgos que cierra.** H-04, H-05, H-18, H-21, H-28, H-30 a H-34, H-37 a H-41 y H-50 a H-53, más H-55 y
>   H-56. H-29 se cierra en sus datos.
> - **Desviaciones del corrector.** Son aceptables: `pie-de-pagina.md:46-47` es una lectura razonable de Q3; el
>   cambio de `001:337-338` lo pide Q7; y `plan-modulo` se reescribió sin cambios fuera de las líneas pedidas y en LF.
> - **Motivo del resultado.** **H-57 (bloqueante)**: al reescribir FR-002-12 se perdió el salto de línea anterior a
>   FR-002-13 (`002:240`). Restituirlo es mecánico.
> - **Observaciones.** H-58 (mayor, regla 3: `pie-de-pagina.md:46` cita el formato de vinculación, que no está en
>   `docs/fuentes/`) y H-59 a H-70 (menores). H-61 registra que la sección 8 duplica cuatro viñetas con cifras
>   distintas y declara «Sin desviaciones».
>
> Estado: `aplicada`. Pasa a `verificada` cuando la auditoría de cierre del plan que corrija H-57 confirme
> FR-002-13 en su propia línea.

**Camino propuesto.** Una COR-010 pequeña, por el flujo de la regla 11, con:
- H-57 (restituir el salto de línea);
- H-58 (texto de la sección 5);
- los menores que usted quiera incluir: H-59, H-60, H-62, H-64, H-65 y H-68 afectan a specs o skills.

H-61 y H-66 son de registro y los anota la sesión principal en la sección 9. H-63, H-67 y H-69 son de la sesión
principal o de proceso.
