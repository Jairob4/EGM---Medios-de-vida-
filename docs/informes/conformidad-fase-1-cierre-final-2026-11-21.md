# Informe de conformidad: cierre final de la Fase 1 y del plan de corrección COR-009 + COR-010

**Fecha**: 2026-11-21
**Auditor**: `verificador`. No participó en redactar, aprobar ni aplicar lo auditado.
**Lector**: Jairo. Contiene información interna (secciones 2.3 y 2.6) y no se comparte con el equipo.
**Base**: `docs/informes/conformidad-fase-1-cierre-2026-11-21.md` (COR-009 en `aplicada` por H-57 y H-58; hallazgos
menores H-59 a H-70).
**Alcance**: COR-010 completa, las ediciones de la sesión principal (S1 a S4, H-61, H-63, H-66 y H-67) y su efecto
conjunto con COR-009 sobre el sistema. Es la única pasada del `verificador` sobre este plan de corrección (regla 11
de `CLAUDE.md`).
**Método**:
- `git diff HEAD` (HEAD = b954d30) sobre el árbol de trabajo, con cada bloque atribuido a su origen. Las horas de
  modificación separan lo anterior a la auditoría previa (hasta las 17:26) de lo posterior (17:56 y de 20:38 a
  20:41).
- Comprobación por programa de los 31 textos de 5.A y 5.B de COR-010 frente al repositorio (coincidencia exacta,
  una vez cada uno).
- Reconstrucción del apéndice B tal como lo dejó COR-009 (texto de HEAD más los reemplazos de I-02,
  `COR-009:141-147`) y comparación línea a línea con el archivo interno.
- Recuento por programa de identificadores, fuentes, cobertura, referencias y fines de línea, leyendo bytes.
- Matriz leída en modo solo lectura, abriendo el archivo como zip, sin bibliotecas que escriban. Hash calculado antes
  y después de leerla.
- Texto de los dos PDF de `docs/fuentes/` extraído en modo lectura con el entorno `.venv` del proyecto.
- No hay código: `src/`, `app/`, `tests/` y `data/fixtures/` solo tienen `.gitkeep`, así que no se ejecutan `ruff`,
  `mypy` ni `pytest`.

## 1. Veredicto

- **COR-009: `verificada`.** H-57 (bloqueante) y H-58 (mayor) quedan cerrados por COR-010. El resto de COR-009 ya era
  conforme en la auditoría anterior, y COR-010 no lo altera. H-61 queda anotado en la sección 9 (texto en la sección 6).
- **COR-010: `verificada`.** Se aplicó literalmente y solo sobre su lista cerrada de 15 archivos. Sus secciones 7 y
  8 coinciden con el repositorio. La única diferencia es una búsqueda esperada mal estimada en su propia sección 8
  (`tabla 3` en specs: 2 y no 1), y el corrector ya la declaró como desviación.
- **La Fase 1 puede cerrarse.**
  - Los 14 hallazgos H-57 a H-70 están cerrados.
  - Hay 0 NC abiertos en `docs/specs/`.
  - Ningún hallazgo nuevo es bloqueante ni mayor: H-71 y H-72 son menores.
  - El cierre sigue sujeto a las compuertas de `README_KIT.md:45-46` (su revisión de los specs) y al commit del
    trabajo, que hace usted (Q9).
  - Los specs siguen en v0 hasta el acuerdo de alcance con la investigadora principal (`000:4`).

## 2. Comprobaciones obligatorias

### 2.1 Integridad

| Control | Resultado | Evidencia |
|---|---|---|
| SHA-256 de la matriz | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual antes y después de leerla, igual al registrado en `contrato-datos.md:373` (apéndice A) | `sha256sum` y `hashlib` sobre `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` |
| `data/raw/` y `docs/fuentes/` | Sin cambios: `git status --porcelain docs/fuentes data/raw` vacío | — |
| Árbol de trabajo | 24 modificados, 1 borrado (`docs/planes/_plantilla-plan.md`) y 8 sin seguimiento. Los nuevos desde la auditoría anterior son `COR-010.md` e `interno-tabla3-hoja-egm.md` | `git status --porcelain --untracked-files=all` |
| Fines de línea | `trazabilidad.md`: 11 003 bytes, 191 `\r\n`, 191 `\n`, 191 `\r` (ningún `\r` suelto), sin BOM. `contrato-datos.md` termina en la «Nota de lectura» del apéndice A con un solo `\n` final | lectura de bytes |

### 2.2 Atribución de cada bloque de `git diff HEAD` (pregunta 1)

Los bloques anteriores a la auditoría previa se atribuyeron en `conformidad-fase-1-cierre-2026-11-21.md` §2.2, y esta
auditoría no encuentra cambios en ellos. Los archivos sin cambio desde entonces son 001, `sistema-diseno-egm/SKILL.md`,
`calidad-python/SKILL.md`, `_plantilla-plan-spec.md`, `PROMPT_FASE_2_arquitectura.md`, `README.md` y `COR-009.md`. Lo
posterior se atribuye así:

| Archivo | Bloque nuevo | Atribución |
|---|---|---|
| `002-mapa-interactivo/spec.md` | `:105` (título de US-002-4.2); `:165-168` (US-002-4.14); `:226` (caso borde); `:246` (FR-002-12: frase de entrada común y fuente); `:246-247` (salto de línea antes de FR-002-13, idéntico a la línea de HEAD) | COR-010 5.A.1: H-70, H-59, H-59, H-59 y H-60, H-57 |
| `003-tablero-conclusiones/spec.md` | `:224` («o documentos no empíricos») | COR-010 5.A.2: H-59 |
| `contrato-datos.md` | `:75-76` y `:141-142` (fuente del 21-nov); `:209` (fecha de Q4); `:272` (Q2); §9 `:346-347` y `:362-363` (cuatro filas); §7 punto 7 `:283-284`; borrado del apéndice B y de la línea en blanco previa | COR-010 5.A.3: H-60, Q4 de COR-010, H-60, H-60, H-69, H-69 |
| `000-vision-alcance.md` | `:136` («y §6.7») | COR-010 5.A.4: H-64 |
| `trazabilidad.md` | `:162` y `:183` (US-002-4.14) | COR-010 5.A.5 |
| `pie-de-pagina.md` | `:46` | COR-010 5.A.6: H-58 con Q1 = 1. `:47` es de COR-009 (Q3) y no cambia |
| `referencia-v4.md` | `:50` | COR-010 5.A.7: H-65. Sustituye el texto de COR-009 5.E |
| `contrato-matriz/SKILL.md` | `:64` (remisión al archivo interno) | COR-010 5.A.8: H-69, dentro del párrafo que reescribió COR-009 I-02 |
| `plan-modulo/SKILL.md` | `:16` y `:21` | COR-010 5.A.9: H-62 |
| `trazabilidad/SKILL.md` | `:3`, `:31` y `:32` | COR-010 5.A.10: H-62 |
| `implementador.md` | `:12` | COR-010 5.A.11: H-62. La descripción de `:3` es de COR-009 |
| `PROMPT_FASE_3_planes.md` | `:12` | COR-010 5.A.12: H-62 |
| `PROMPT_FASE_1_specs.md` | `:62` | COR-010 5.A.13: H-69. Es el único bloque del archivo |
| `README_KIT.md` | `:51` | COR-010 5.A.14: H-68 |
| `verificador.md` | `:3` y `:16` | COR-010 5.A.15: Q3 = 1 |
| `CLAUDE.md` | `:80` | Sesión principal, S2. Lo demás (`:33-42`, `:53`, `:68`) ya estaba atribuido |
| `invariantes.md` | `:38` y `:46` (remisiones); `:39` (archivo interno y puntuación); sección «Decisiones del 21-nov-2026 (COR-010)» (`:70-73`) | Sesión principal: S3 y H-67. La cabecera (`:4-5`) la autoriza a editarlo |
| `hallazgos-matriz-para-equipo.md` (sin seguimiento) | B-01 (`:35`); citas por sección en A-01 a A-04; A-03 completo; B-03 dentro de su tabla; estados «Sin implementar» | Sesión principal: S4 y H-63 |
| `COR-005.md` | sección 9, observación H-48 (`:490`) | Sesión principal: H-66 |
| `interno-tabla3-hoja-egm.md` (nuevo) | Archivo completo | Sesión principal: S1 |
| `COR-010.md` (nuevo) | Propuesta, decisión y secciones 7 y 8 | Analista, sesión principal (decisión) y corrector |
| `fase-1-resumen.md` | — | `verificador` (Q5 = 2; este encargo lo rehace) |

**Ningún bloque queda sin justificación.** La sesión principal solo editó lo que le asigna COR-010 5.B o lo que el
informe anterior dejaba a su cargo (H-63, H-66, H-67), y nada de ello es un spec, una arquitectura, una interfaz ni un
plan. El corrector no tocó ninguno de los archivos de 5.B.

### 2.3 COR-010: aplicación literal, secciones 7 y 8, y archivo interno (pregunta 1)

- **Textos.** Los 31 textos de 5.A y de S2 y S4 están en su destino exactamente una vez. Esto incluye:
  - el salto de línea de H-57;
  - las dos frases y la fuente de FR-002-12;
  - el caso borde y el escenario US-002-4.14, con la línea en blanco previa;
  - las cuatro filas de §9, en su lugar;
  - las seis fuentes del 21-nov-2026 (`contrato:75`, `:76`, `:141`, `:142`, `:209` y `:272`);
  - el punto 7 de §7;
  - los textos de H-58, H-62, H-64, H-65, H-68 y Q3.
- **FR-002-13** (`002:247`) es idéntico, carácter por carácter, a su línea en HEAD.
- **Orden.** Se respetó el orden obligatorio: el archivo interno (20:38:45) es anterior al contrato sin apéndice
  (20:40:01).
- **Lista cerrada.** Los 15 archivos de 5.A coinciden con la sección 7. No hay ningún otro archivo modificado después
  de las 20:38, salvo los de 5.B y `COR-010.md`.
- **Sección 7.** Coincide con el repositorio, archivo por archivo.
- **Sección 8.** Se reproducen todas sus búsquedas:

| Búsqueda | Sección 8 | Encontrado |
|---|---|---|
| Líneas con dos requisitos o dos escenarios en specs | 0 | 0 |
| `^- \*\*FR-002-13\*\*` en 002 | 1 | 1 (`:247`) |
| `[Aa]péndice B` en specs, `.claude/`, `CLAUDE.md`, `README*`, `PROMPT_FASE_*`, `hallazgos-…`, `docs/planes/` | 0 | 0 |
| `tabla 3` en specs | 1 previsto; 2 informados | 2 (`contrato:283` y `:284`) |
| `Sí\*` o `columna «Humano»` en specs | 0 | 0 |
| `Celda vacía por el filtro` | 0 | 0 fuera de `COR-010.md` |
| `US-002-4.14` | 1 en 002 y 2 en `trazabilidad.md` | 1 y 2 |
| `trazabilidad.md` | CRLF, 89 por tabla | 191 CRLF; 89 por tabla |
| Escenarios | 121 | 121 |
| «módulo» en los archivos de H-62 | Solo con el sentido de arquitectura | `plan-modulo/SKILL.md:10`, `:11` y `:19`; `PROMPT_FASE_3_planes.md:11`; `CLAUDE.md:38` y `:43` (conservados por `COR-010:84`) |

- **Archivo interno de la tabla 3.** `interno-tabla3-hoja-egm.md:15-34` es **idéntico** al apéndice B que dejó COR-009.
  - El apéndice se reconstruyó tomando `git show HEAD:docs/specs/contrato-datos.md:402-424` y aplicando los tres
    reemplazos de I-02 (`COR-009:142-147`). El texto así obtenido es el que el informe anterior vio en `contrato:407-426`.
  - `diff` entre ese texto y las líneas 15 a 34 del archivo interno: sin diferencias.
  - La cabecera (`:1-13`) lo declara interno (regla 9), explica su origen (COR-010, H-69) y aclara qué designan
    «este apéndice» y las secciones citadas.

### 2.4 Identificadores, fuentes y cobertura (pregunta 3)

| Elemento | Recuento | Detalle |
|---|---|---|
| Requisitos | **89** | FR-001: 29; FR-002: 19; FR-003: 22; NFR-000: 19 |
| SC | **35** | SC-000: 19; SC-001: 5; SC-002: 5; SC-003: 6 |
| Escenarios | **121** | 001: 61; 002: 30 (historia 4: 14); 003: 30. Coincide con el corrector. El nuevo es US-002-4.14 |
| Historias | 15 | 5 por spec |

- **Unicidad y huecos.** Ningún ID se define dos veces. No hay huecos en FR, NFR, SC ni escenarios. Todos los
  requisitos empiezan en línea propia.
- **Referencias colgantes.** Ninguna. Se revisaron todos los ID de FR, NFR, SC y US citados en:
  - los cinco specs y `trazabilidad.md`;
  - `hallazgos-matriz-para-equipo.md` e `interno-tabla3-hoja-egm.md`;
  - `invariantes.md`, `README_KIT.md` y las skills `sistema-diseno-egm` y `contrato-matriz`.
- **Fuente.** Los 89 requisitos tienen `[Fuente: …]`.
- **Cobertura.** Los 89 tienen escenario o SC en `trazabilidad.md`, y todo lo citado existe. La cláusula de Q8 de
  FR-002-12 ya tiene escenario (US-002-4.14), que también cubre FR-003-14.
- **`trazabilidad.md` al día.**
  - 178 filas de requisito: 89 por tabla, sin repetidos, faltantes ni sobrantes.
  - Todos los requisitos siguen en `especificado`, como corresponde a la fase.
  - La fuente de FR-002-12 (`traz:66`) sigue siendo equivalente a la del spec: ya incluía «decisión de Jairo,
    21-nov-2026».

### 2.5 `[NEEDS CLARIFICATION]` y marcas (pregunta 4)

- **`docs/specs/` sin `_plantilla/`: 0 NC.** Se cumple el esperado.
- Los dos NC que dejó el analista en COR-010 los resolvió la sesión principal, y esta auditoría los comprueba en los
  PDF:
  - **Portada del documento general.** Dice «Semillero Desarrollo Rural y Economía Solidaria · Grupo GIOE ·
    Universidad del Magdalena».
  - **§6.7 del documento técnico.** Dice «Precondición N ≥ Nmin (parámetro)».
- **`[Propuesta sin fuente]`**: 0 en specs, skills y agentes.
- **`[POR CONFIRMAR]`**: queda una sola marca de dato, `pie-de-pagina.md:21` (su nombre y su rol en el colofón). Las
  menciones de `pie-de-pagina.md:4` y `disenador-front.md:30` explican la regla y no son marcas.
- **Skills, agentes y plantilla de planes.** Las menciones de `NEEDS CLARIFICATION` son instrucciones de uso, no
  marcas. Están en `analista-impacto.md:39`, `arquitecto.md:31`, `especificacion-srs`, `plan-modulo`,
  `protocolo-correccion`, `trazabilidad` y `_plantilla-plan-spec.md`.

### 2.6 Reglas de `CLAUDE.md` (pregunta 5)

- **Regla 1.** Matriz intacta (2.1).
- **Regla 3.**
  - H-58 está resuelto. `pie-de-pagina.md:46` cita dos fuentes que están en el repositorio: la portada del documento
    general (comprobada en el PDF) y `estado_proyecto_2026-10-31.md:11` (§2).
  - Las cuatro reglas de H-60 ya llevan la fecha de su decisión.
  - `000:136` cita bien el documento técnico (§6.7 comprobado).
  - `referencia-v4.md:50` coincide con las fórmulas del archivo. Las de los bloques 1 a 3 condicionan por D, G y H, y B6, B16 y
    B26, también la dimensión. J6 y J16 no exigen dimensión. B16 y J16 exigen J = «Evaluación de impacto». B26 y J26
    aplican `"Sí*"` sobre M. B36 y B37 condicionan solo por D y J.
  - `README_KIT.md:51` ya no atribuye el stack al equipo.
  - Ningún texto nuevo afirma algo sin fuente.
- **Regla 7.** Ningún texto nuevo usa la tabla de la lámina 7 (`presentacion_equipo_2026-10_texto.md:92-104`).
  US-002-4.14 describe su propia matriz sintética: dos estudios de nivel «Estudio de caso» y un documento no empírico.
  Conforme.
- **Regla 9.**
  - **Qué dice el contrato.** `contrato:283` dice: «La tabla 3 de la hoja no es comparable: no se lee ni se compara,
    y la herramienta no la calcula». Su fuente (`:284`) es «decisión de Jairo, 2-nov-2026; doc. técnico §9.1, para la
    tabla 3».
  - **Describe solo el comportamiento, no la discrepancia.** No nombra el criterio, ni la columna que evalúa, ni que
    vale 0, ni la palabra «discrepancia». Es la misma información que ya daba el punto 6, que lista «tablas
    verificadas: 1, 2 y 4». Usted aprobó ese texto exacto al aprobar H-69 (`COR-010:148-151`, opción A).
  - **Observación, sin severidad.** El §9.1 del documento técnico, citado como fuente, explica la exclusión «por el
    hallazgo (a)», y su §3.4 (a) describe la discrepancia. Quien siga la fuente desde el contrato llega a esa
    descripción. Es una consecuencia de citar la fuente, que exige la regla 3. Solo importa si el documento técnico
    no se ha entregado al equipo; si se entregó, la discrepancia ya está en ese documento.
  - **Textos para el equipo.** Ninguno describe la discrepancia de la tabla 3.
    - En `docs/specs/` la tabla 3 solo aparece en `contrato:283-284`.
    - `docs/interfaz/` solo tiene `bocetos/.gitkeep`.
    - La descripción está solo en textos internos: `interno-tabla3-hoja-egm.md`, `contrato-matriz/SKILL.md:64`,
      `referencia-v4.md:47-51`, `invariantes.md:39` y `:72`, `hallazgos-matriz-para-equipo.md:35` (B-01), los informes
      y las correcciones.
    - `CLAUDE.md:41`, `README_KIT.md:53` y `PROMPT_FASE_1_specs.md:62` la nombran sin describirla.
    - `fase-1-resumen.md` no la describe.
- **Regla 11.** Se respetó el flujo:
  - propuesta del analista;
  - aprobación de usted (`COR-010:213-223`);
  - aplicación del corrector, solo sobre 5.A;
  - ediciones de la sesión principal, solo sobre 5.B y los registros que le dejó el informe anterior;
  - esta auditoría, única.

  La sesión principal no editó ningún spec, arquitectura, interfaz ni plan.

## 3. Estado de los hallazgos H-57 a H-70 (pregunta 2)

| ID | Estado | Evidencia |
|---|---|---|
| H-57 | Cerrado | FR-002-13 en su propia línea (`002:247`), idéntico a HEAD. 0 líneas con dos requisitos |
| H-58 | Cerrado | `pie-de-pagina.md:46`. Las dos fuentes comprobadas (portada del PDF; `estado_proyecto_2026-10-31.md:11`) |
| H-59 | Cerrado | `003:224` alineado con FR-002-12. Lo que muestra el mapa, en FR-002-12 (`002:246`) y en el caso borde (`002:226`). Escenario US-002-4.14 (`002:165-168`); `traz:162` y `:183`. Ver H-71 |
| H-60 | Cerrado | Fuente del 21-nov-2026 en `contrato:75`, `:76`, `:141`, `:142` y `:272`, y en FR-002-12. Filas de Q4 y Q6 en §9 (`contrato:346-347` y `:362-363`) |
| H-61 | Se cierra al anotarse | La sección 9 de COR-009 lo registra (texto en la sección 6). `COR-009:400-417` no se modifica, por ser un registro |
| H-62 | Cerrado | `CLAUDE.md:80`; `implementador.md:12`; `plan-modulo/SKILL.md:16` y `:21`; `trazabilidad/SKILL.md:3`, `:31` y `:32`; `PROMPT_FASE_3_planes.md:12`; `verificador.md:3` y `:16`. «Módulo» queda solo con el sentido de la arquitectura |
| H-63 | Cerrado | `hallazgos-matriz-para-equipo.md`: citas por sección (`:26-29`); A-03 con FR-003-14, §9 y la salida de los empíricos pendientes (`:28`); B-03 dentro de la tabla (`:37`); estados «Sin implementar» (`:26-37`) |
| H-64 | Cerrado | `000:136` («§6.2 a §6.4 y §6.7»), comprobado en el PDF |
| H-65 | Cerrado | `referencia-v4.md:50`, coincide con las fórmulas de B6, J6, B16, J16, B26, J26, B36 y B37 |
| H-66 | Cerrado | `COR-005:490` («a más tardar el 3-nov-2026 (commit b954d30, 3-nov-2026 13:05)»); `git log` confirma la fecha |
| H-67 | Cerrado | `invariantes.md:38` y `:46` remiten a las decisiones del 21-nov; `:39` corrige la puntuación |
| H-68 | Cerrado | `README_KIT.md:51` |
| H-69 | Cerrado | Apéndice B fuera del contrato (archivo de 409 líneas que termina en el apéndice A). Contenido íntegro en `interno-tabla3-hoja-egm.md`. Remisiones actualizadas en `contrato-matriz/SKILL.md:64`, `invariantes.md:39`, `hallazgos-matriz-para-equipo.md:35` y `PROMPT_FASE_1_specs.md:62` |
| H-70 | Cerrado | `002:105` («Celda sin estudios por el filtro») |

## 4. Hallazgos nuevos

Severidad: **bloqueante** impide dar por verificada la corrección; **mayor** impide cerrar la Fase 1 o empezar la
siguiente sin corregirlo; **menor**, ninguna de las dos. Ningún hallazgo propone cambios en la matriz, sus columnas,
listas, dimensiones, intervenciones, criterios ni metodología.

**No hay hallazgos bloqueantes ni mayores.**

### Menores

**H-71. «Documentos no empíricos sin nivel» admite una lectura más estrecha que la regla.**
- **Dónde.** El caso borde de `002:226` («si solo hay documentos no empíricos sin nivel y ningún estudio del mapa sin
  nivel») y `invariantes.md:55` y `:71`.
- **Qué dice la regla.** FR-002-12 (`002:246`, «o documentos no empíricos (FR-003-14)») y FR-003-14 (`003:246`)
  tratan como «Sin nivel» a **todo** documento no empírico, tenga o no el nivel diligenciado.
- **Lectura posible.** Un lector puede entender que la entrada solo aparece si los no empíricos tienen el nivel vacío.
- **Impacto.** El requisito manda y el escenario US-002-4.14 no fija el nivel del documento no empírico, así que no
  hay contradicción de cobertura. El texto es el que usted aprobó (`COR-010:119`).
- **Propuesta**, si desea afinarlo en una corrección futura: «si solo hay documentos no empíricos y ningún estudio
  del mapa sin nivel».

**H-72. `prompts/RETOMAR_2026-11-21.md` está desactualizado y puede inducir a error si se usa para retomar.** Es
anterior a COR-009 y COR-010:
- `:55` dice «un módulo a la vez».
- `:57` presenta `_plantilla-plan.md` como plantilla vigente.
- `:60-73` lista 10 NC que ya están resueltos y cita `contrato-datos.md:424`, del apéndice B que ya no está en el
  contrato.
- `:83` reproduce la regla 9 anterior.

COR-010 lo excluye a propósito (`COR-010:209`), por ser una nota fechada, y no es un spec. Propuesta: no usarlo para
retomar el trabajo. La Fase 2 parte de `CLAUDE.md` y `fase-1-resumen.md` (`PROMPT_FASE_2_arquitectura.md:7`).

## 5. Huecos, excesos y contradicciones

- **Huecos**: ninguno. Los 89 requisitos tienen fuente y escenario o SC. Las columnas de componente, tarea y prueba
  están vacías, como corresponde a la fase de specs.
- **Excesos**: ninguno. COR-010 no agrega requisitos, solo el escenario US-002-4.14 y cuatro filas de casos borde que
  aplican decisiones fechadas.
- **Contradicciones**: ninguna entre specs, contrato y skills. H-71 es de redacción y no contradice la regla.

## 6. Resultado para la sección 9 de COR-009 y de COR-010

| COR | Resultado | Fecha | Motivo |
|---|---|---|---|
| COR-001 a COR-008 | `verificada` (sin cambio) | 2026-11-21 | COR-010 no altera lo que dejaron |
| COR-009 | **`verificada`** | 2026-11-21 | H-57 y H-58 cerrados por COR-010; H-61 anotado |
| COR-010 | **`verificada`** | 2026-11-21 | Aplicación literal y sobre su lista cerrada; H-57 a H-70 cerrados |

**Texto propuesto para la sección 9 de COR-009:**

> **Verificada** el 21-nov-2026, en dos pasadas del mismo plan de corrección:
> `docs/informes/conformidad-fase-1-cierre-2026-11-21.md` («no verificada» por H-57) y
> `docs/informes/conformidad-fase-1-cierre-final-2026-11-21.md` (cierre, tras COR-010).
>
> - **Aplicación.** La aplicación de 5.B a 5.E y de las respuestas Q1 a Q11 es literal. Solo se editaron los archivos
>   1 a 15 y 17 a 20 de 5.A, y el 16 lo borró la sesión principal. Todo bloque de `git diff HEAD` tiene origen
>   atribuido.
> - **Recuentos.** Tras COR-010 hay 89 requisitos, 121 escenarios y 35 SC, con ID únicos, sin huecos ni referencias
>   colgantes, y 0 NC en `docs/specs/`. `trazabilidad.md` tiene 191 líneas CRLF y 89 requisitos por tabla.
> - **Integridad.** Matriz intacta (SHA-256 `7E1714DE…C3A1`) y `docs/fuentes/` sin cambios.
> - **Motivo del primer resultado, ya resuelto.** H-57 (FR-002-13 pegado a FR-002-12) y H-58 (fuente del colofón
>   fuera del repositorio) los corrigió COR-010, verificada en el informe de cierre.
> - **Hallazgos que cierra.** H-04, H-05, H-18, H-21, H-28, H-30 a H-34, H-37 a H-41, H-50 a H-53, H-55 y H-56. H-29 se cerró del todo
>   con H-58.
> - **Desviaciones del corrector.** Las tres de la sección 7 son aceptables.
> - **H-61 (registro).** La sección 8 tiene dos defectos. Repite cuatro viñetas con cifras distintas: `:400-403`
>   frente a `:404-407`, con 120 y 119 escenarios; la cifra correcta era 120. Además declara «Sin desviaciones»
>   (`:417`), cuando el corrector informó tres en la sección 7. Esa sección no se reescribe porque es un registro;
>   esta nota la corrige.
>
> Estado: `verificada`.

**Texto propuesto para la sección 9 de COR-010:**

> **Verificada** el 21-nov-2026 (`docs/informes/conformidad-fase-1-cierre-final-2026-11-21.md`), en la auditoría
> única de cierre del plan de corrección COR-009 + COR-010.
>
> - **Aplicación literal.** Los 31 textos de 5.A y de S2 y S4 están en su destino, una vez cada uno. FR-002-13 es
>   idéntico a su línea de HEAD. Se respetó el orden S1 → borrado del apéndice B.
> - **Lista cerrada.** El corrector editó solo los 15 archivos de 5.A, y la sesión principal solo los de 5.B. Cada
>   bloque de `git diff HEAD` tiene origen atribuido.
> - **Secciones 7 y 8.** Coinciden con el repositorio. La búsqueda `tabla 3` en specs da 2 (`contrato:283-284`) y no
>   1, como ya declaró el corrector.
> - **Archivo interno.** `docs/informes/interno-tabla3-hoja-egm.md:15-34` es idéntico al apéndice B que dejó COR-009.
> - **Recuentos.** 89 requisitos, 121 escenarios (61, 30 y 30) y 35 SC; ID únicos, sin huecos ni referencias
>   colgantes; 0 NC en `docs/specs/`. `trazabilidad.md` tiene 191 líneas CRLF y 89 requisitos por tabla.
> - **Integridad y reglas.** Matriz intacta (SHA-256 `7E1714DE…C3A1`) y `docs/fuentes/` sin cambios. Se cumplen las
>   reglas 3, 7, 9 y 11. El punto 7 de §7 del contrato describe el comportamiento ante la tabla 3, no la discrepancia.
> - **Hallazgos que cierra.** H-57, H-58, H-59, H-60, H-62, H-64, H-65, H-68, H-69 y H-70. La sesión principal
>   cerró H-63, H-66 y H-67, y H-61 queda anotado en COR-009.
> - **Observaciones menores, que no invalidan la aplicación.** H-71: la redacción «documentos no empíricos sin
>   nivel» en `002:226`. H-72: `RETOMAR_2026-11-21.md` está desactualizado.
>
> Estado: `verificada`.

## 7. Pendientes que no son de specs

No impiden cerrar la Fase 1. Se detallan en `docs/informes/fase-1-resumen.md` §7 y §9:
- los logos en `docs/interfaz/logos/` (SC-000-11);
- el permiso de uso de los logos (`README_KIT.md:50`);
- su nombre y su rol en el colofón (`pie-de-pagina.md:21`);
- el stack web, que propone el ADR-003 (`README_KIT.md:51`);
- los dos marcadores de `PROMPT_FASE_2_arquitectura.md:11-12`;
- el commit del trabajo del 21-nov-2026.
