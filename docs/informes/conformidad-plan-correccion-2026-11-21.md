# Informe de conformidad: cierre del plan de corrección COR-001 a COR-008 (objeto principal: COR-005)

**Fecha**: 2026-11-21
**Auditor**: `verificador`. No participó en redactar ni en aplicar lo auditado.
**Lector**: Jairo. Contiene información interna (secciones 2.6 y 6) y no se comparte con el equipo.
**Alcance**: COR-005 completa, el efecto de COR-005 sobre COR-004, COR-006, COR-007 y COR-008 (ya verificadas por
`conformidad-correcciones-2026-11-03-b.md`) y sobre el sistema completo. Además, el estado de los hallazgos abiertos,
de los documentos desactualizados y de las dos plantillas de plan, para preparar el cierre de la Fase 1.
**Método**: `git diff 63bf5eb b954d30`, con cada bloque de cambios atribuido a la corrección que lo pide en su
sección 5. Comprobación literal, por programa, de cada texto de las secciones 5.1 a 5.5 de COR-005 en el spec de
destino. Recuento por programa de identificadores, fuentes, cobertura y fines de línea (bytes). Lectura de la matriz
en modo solo lectura, sin bibliotecas que escriban (lectura directa del XML del archivo), con el hash calculado antes y
después. No hay código, así que no se ejecutan `ruff`, `mypy` ni `pytest`: `src/`, `app/`, `tests/` y
`data/fixtures/` solo tienen `.gitkeep`.

## 1. Veredicto

**El plan de corrección puede cerrarse.** COR-005 se aplicó literalmente, solo en los ocho archivos de su lista
cerrada, y sus secciones 7 y 8 coinciden con el repositorio. No hay hallazgos bloqueantes. Las observaciones sobre
COR-005 (H-48 a H-53) son menores y no invalidan lo aplicado. Resultado propuesto para COR-005: **verificada con
observaciones** (sección 7). COR-001 a COR-004 y COR-006 a COR-008 siguen verificadas. COR-005 no altera nada de lo
que esas correcciones dejaron.

**La Fase 1 todavía no puede cerrarse.** Lo impiden cuatro cosas:
1. **Diez `[NEEDS CLARIFICATION]` abiertos** en los specs (sección 4) y una propuesta sin aprobar, FR-002-18 (P4,
   `002:236`), que se relaciona con el NC de FR-002-19. Son decisiones suyas. La compuerta de la fase pide que usted
   las responda o que decida expresamente pasarlas a la arquitectura (`README_KIT.md:44-45`).
2. **H-54 (mayor).** `docs/informes/fase-1-resumen.md` se quedó en el estado del 2-nov. `CLAUDE.md:48` pide
   resumir la fase y listar los NC abiertos al terminarla.
3. **H-29 (mayor, regla 3), abierto.** El colofón publicaría datos que no constan en `docs/fuentes/`.
4. **H-32 (pasa a mayor), abierto.** La guía de diseño contradice NFR-000-12, que ahora es una decisión suya. Debe
   corregirse antes de que empiecen los bocetos (Fase 2).

A esto se suman la revisión de los specs por usted y el acuerdo de alcance con la investigadora principal: los specs
siguen en v0 (`000:4`, `000:39`).

## 2. Comprobaciones obligatorias

### 2.1 Integridad

| Control | Resultado | Evidencia |
|---|---|---|
| SHA-256 de la matriz | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, igual antes y después de leerla, e igual al del 3-nov y al de `fase-1-resumen.md:174` | `sha256sum data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` |
| `data/raw/` en git | Sin cambios. El blob `6c7c4ed…` de `HEAD` coincide con `git hash-object` del archivo | `git ls-tree HEAD data/raw/` |
| `docs/fuentes/` | Sin cambios desde 63bf5eb: `git diff --stat 63bf5eb -- docs/fuentes data/raw` y `git diff HEAD -- …` están vacíos. Último commit que toca la ruta: 63bf5eb, que versionó `Documento_tecnico_herramienta_EGM.pdf` | `git log -- docs/fuentes data/raw` |
| Árbol de trabajo | Solo dos archivos sin seguimiento: `docs/planes/_plantilla-plan-spec.md` y `prompts/RETOMAR_2026-11-21.md` | `git status --short` |

### 2.2 Atribución de cada bloque de cambios de 63bf5eb a b954d30

El commit b954d30 cambia 19 archivos. Todos los bloques se atribuyen a una corrección o a un registro documentado,
salvo uno, que no está registrado (H-48).

| Archivo | Bloques | Atribución |
|---|---|---|
| `contrato-datos.md` | Regla 3 y regla 12 (marca) | COR-004 P1 y P3, más la mayúscula de COR-007 5.2 |
| | Regla 4 | COR-004 F5a, más el borrado de COR-006 5.3 |
| | Regla 10 | COR-004 P2 |
| | §5, párrafo de $M$ (`:173`) | COR-005 5.1 (b) |
| | §5, «Filtros» (`:205`) | COR-005 5.1 (a). Reemplaza la marca de F3 que había dejado COR-004 |
| | §7, puntos 2 y 4 | COR-004 F1 y F2 |
| | §9, dos filas (`:325-326`) | COR-005 5.1 (c) |
| | Apéndice B, marca (`:419`) | COR-004 F6b y F6d |
| `000-vision-alcance.md` | Fuera de alcance (`:58`); NFR-000-12 (`:85`); NFR-000-17 (`:90`); SC-000-09 (`:106`); SC-000-12 (`:109`); SC-000-17 (`:114`); NC de inactividad (`:121`); nota de fuentes (`:134`) | COR-005 5.2 (a) a (h). La fuente doble de NFR-000-17 viene de COR-004 F7 y F8 y se conserva |
| | NFR-000-19 (`:92`) y NC de tamaño (`:120`) | COR-008 5.1 y 5.2 |
| `001-lectura-verificacion/spec.md` | US-001-1.10 (`:65`); Given de US-001-4.1 y 4.2 (`:176-183`); US-001-4.7 y 4.8 (`:206-214`); US-001-5 (`:309-352`); fuente de FR-001-07 (`:381`); FR-001-28 y FR-001-29 (`:402-403`) | COR-005 5.3 (a) a (f) |
| | FR-001-20 (fuente) y FR-001-24 | COR-004 F9 y P3 |
| `002-mapa-interactivo/spec.md` | *When* de US-002-4.1, 4.3, 4.4 y 4.8; US-002-4.10 a 4.12 (`:145-158`); Edge Cases (`:206`, `:210`); FR-002-12 (`:230`); FR-002-19 (`:237`) | COR-005 5.4 (a) a (e) |
| | FR-002-01 | COR-004 P1 |
| `003-tablero-conclusiones/spec.md` | *When* de US-003-3.1; US-003-5.4 y 5.5 (`:203-211`); Edge Cases (`:218-219`) | COR-005 5.5 (a) a (c) |
| `trazabilidad.md` | NFR-000-12, FR-001-07 y FR-002-12 (fuente); FR-001-28, FR-001-29 y FR-002-19 (filas nuevas en las dos tablas); cobertura de NFR-000-17, FR-001-07 y FR-002-12 | COR-005 5.6 |
| | NFR-000-17 y FR-001-20 | COR-007 5.1 |
| | NFR-000-19 | COR-008 5.3 |
| | FR-001-24 y FR-002-01 | COR-004 (sección 7) |
| `pie-de-pagina.md` | `:25`, «Decisión de Jairo, 3-nov-2026» | COR-005 5.7 |
| `contrato-matriz/SKILL.md` | Regla 3 y observación interna | COR-006 5.1 y 5.2 |
| COR-001 a COR-004 | Estado y sección 9 | Registro de la sesión principal (informes del 3-nov) |
| COR-005 a COR-008 e informes del 3-nov | Archivos nuevos | Propuestas e informes |
| `invariantes.md` | Reescritura de 35 a 56 líneas | 3-nov-b §14 (INV-01 a INV-19) **más** una edición posterior, sin registro, que pasa las decisiones de COR-005 a invariantes (H-48) |

Ningún bloque de los specs, de `trazabilidad.md` ni de `pie-de-pagina.md` queda sin una corrección que lo pida.

### 2.3 COR-005: aplicación literal (pregunta 1)

- **Textos de 5.1 a 5.5.** Hay 24 textos citados (11 reemplazos o inserciones en párrafo, 6 bloques de escenarios,
  2 filas de §9 y 5 Edge Cases). Los 24 están en el spec de destino, carácter por carácter. Los reemplazos de
  palabras, como los *When* de 5.4 (a) y 5.5 (a), «indica» de 5.2 (d) y (h), los *Given* de 5.3 (b) y la fuente de
  5.3 (e), se comprobaron en el diff.
- **5.6.** Las tres fuentes y las tres coberturas coinciden con el texto pedido. Las seis filas nuevas están en su
  sitio: `traz:53-54`, `:73`, `:149-150` y `:169`.
- **5.7.** `pie-de-pagina.md:25` dice «Decisión de Jairo, 3-nov-2026: «Matriz:». No cambió nada más del archivo.
- **Lista cerrada.** Los archivos editados por COR-005 son exactamente los ocho de su sección 5. `invariantes.md` no
  lo editó el corrector (ver H-48). `CLAUDE.md`, la skill `contrato-matriz`, `sistema-diseno-egm/SKILL.md`,
  `data/raw/` y `docs/fuentes/` no tienen bloques atribuibles a COR-005.
- **«No se tocan».** FR-001-20, FR-002-15, FR-002-18, US-002-4.5, US-002-4.6, NFR-000-19, la línea del límite de
  tamaño, el apéndice B y las reglas 3, 4 y 12 conservan el texto que dejaron COR-004, COR-007 y COR-008.
- **Sección 7.** Coincide con el repositorio, incluida la desviación de forma declarada: la línea en blanco antes de
  `### Edge Cases`, en `001:353`.
- **Sección 8.** Todas sus cifras se reproducen:

| Búsqueda de 5.8 | Esperado | Encontrado |
|---|---|---|
| `NEEDS CLARIFICATION` en `docs/specs/` sin `_plantilla/` | 10 apariciones en 8 líneas | 10 en 8 |
| `Propuesta sin fuente` en el contrato | 0 | 0. Queda 1 en `002:236` (FR-002-18) |
| `Actualizar vista` | 11 líneas: contrato 1, 002 7, 003 3 | 1, 7, 3 |
| `45 minutos` | 000 3, 001 5 | 3, 5 |
| `30 minutos`, `registra archivo`, `10 MB` | 0 | 0 |
| `15 MB` | 1 | 1 (`000:92`) |
| `\r$` en `trazabilidad.md` | 191 | 191 |
| Restos de `deja activa`, `sesión sin matriz`, `una sesión nueva`, `cierra la herramienta` | 0 | 0 |

- **Apéndice A.** La matriz, leída de nuevo, confirma lo que COR-005 3.2 da por supuesto: $E$ = N.º 7, 10, 11, 13,
  15, 16 y 24. Solo el N.º 7 tiene intervención (principal y secundaria) y un nivel. Ninguna fila de $E$ tiene la
  principal vacía y la secundaria diligenciada, y ningún estudio del mapa queda «Sin nivel». Las decisiones e y d no
  cambian ningún valor del apéndice A.

### 2.4 Identificadores, fuentes y cobertura (pregunta 2)

| Elemento | Recuento | Detalle |
|---|---|---|
| Requisitos | **89** (86 + 3) | FR-001: 29; FR-002: 19; FR-003: 22; NFR-000: 19 |
| SC | 35 | SC-000: 19; SC-001: 5; SC-002: 5; SC-003: 6 |
| Escenarios | 112 | 001: 56; 002: 27; 003: 29. Coincide con COR-005 3.5 |
| Historias | 15 | US-001-1 a 5; US-002-1 a 5; US-003-1 a 5 |

- **Unicidad.** No hay ningún ID definido dos veces ni huecos de numeración en FR, NFR o SC.
- **Referencias colgantes.** Ninguna. Se revisaron todas las menciones de FR, NFR, SC y US en los cinco specs y en
  `trazabilidad.md`.
- **Fuente.** 88 de 89 requisitos tienen fuente. FR-002-18 sigue como «Propuesta sin fuente, pendiente de
  aprobación» (`002:236`, P4): ya estaba marcada y no es nueva.
- **Cobertura.** Los 89 tienen al menos un escenario o un SC en la tabla de cobertura, y todos los citados existen.
  Las coberturas parciales están en H-30 y H-52.

### 2.5 `trazabilidad.md` (pregunta 3)

- **Bytes.** 10 599 bytes, 191 `\n` y 191 `\r\n`, sin `\r` sueltos y sin BOM. El archivo termina en `\r\n`: son
  **191 líneas, todas CRLF**, como dice COR-005. Los demás specs no tienen CR, como dice COR-005 3.5.
- **Filas.** Hay 89 requisitos en cada tabla, sin filas repetidas, sin faltantes y sin sobrantes.
- **Fuente igual a la del spec.** Coincide en 87 de 89 requisitos, y en los otros 2 es equivalente:
  - FR-002-12 (`traz:66`): el spec agrega «Decisión provisional, a discutir con el equipo» (`002:230`). La tabla no
    lo muestra, conforme al texto literal de COR-005 5.6 (ver H-53).
  - FR-002-18 (`traz:72`): la tabla abrevia la marca de propuesta, igual que antes del plan.
- **Estado.** Todas las filas siguen en `especificado`, y las columnas de componente, tarea y prueba siguen vacías,
  como corresponde a la fase.

### 2.6 Reglas inviolables (pregunta 5)

- **Regla 7.** Ningún spec, skill, corrección ni prompt usa como dato o como esperado la tabla de `presentacion:98-104`
  (lámina 7). Las menciones de «lámina 7» son prohibiciones (`especificacion-srs/SKILL.md:41`, `invariantes.md:21`)
  o comprobaciones (`COR-003.md:35`, `COR-005.md:471`). Los escenarios nuevos de COR-005 usan matrices sintéticas
  descritas en el propio escenario (US-001-1.10, US-001-4.7, 4.8, US-002-4.11, 4.12) o tiempos (44 y 45 minutos).
  Conforme.
- **Regla 9.** La observación de la tabla 3 solo aparece en el apéndice B del contrato (`contrato:402-424`), bajo el
  aviso «Interna — no publicar» (`:402-405`). Ningún texto que agregó COR-005 la menciona. Tampoco aparece en
  `pie-de-pagina.md`, en `sistema-diseno-egm/` ni en `README.md`. `README_KIT.md:54` la nombra, pero es un documento
  del kit para usted, no para el equipo. Conforme.
- **Regla 3.** Lo que agregó COR-005 tiene fuente fechada en su sección 1.5, o un NC. H-29 sigue abierto fuera de lo
  que trató COR-005.
- **Regla 11.** Se respetó el flujo. La aprobación de COR-005 quedó registrada como una inferencia (H-49).

## 3. Efecto conjunto de COR-005 sobre el sistema

- **Sin solapamiento con COR-004, 006, 007 y 008.** El texto final de cada lugar es el de la última corrección que lo
  tocó. COR-005 reemplazó la marca de F3 de COR-004 (prevista en su sección 6) y conservó la fuente doble de
  NFR-000-17 (COR-004) y las filas de COR-007 y COR-008 en `trazabilidad.md`.
- **Contrato y specs coherentes.** La definición de filtro activo (`contrato:205`) se repite igual en FR-002-19
  (`002:237`). La excepción «Sin nivel» está en el contrato (`:205`, `:326`), en FR-002-12, en los Edge Cases de 002
  (`:206`, `:210`) y en los de 003 (`:218-219`). La regla 8 (`contrato:93`, «no genera nivel») es compatible con
  tratar «No aplica…» como «Sin nivel». El párrafo de $M$ (`:173`) es coherente con la fórmula de `:169`.
- **Sesión.** NFR-000-17, SC-000-17, US-001-5 y FR-001-28 describen el mismo inicio, las mismas tres formas de
  terminar y los mismos 45 minutos. NFR-000-18 y SC-000-18 («un filtro activado») son compatibles con la nueva
  definición de «activo».
- **Invariantes.** `invariantes.md:38`, `:45-48` y `:51-56` recogen las decisiones a, b, c, d, e y f, y los NC de
  COR-005, con el mismo contenido que los specs (H-48 trata solo el registro).
- **Hallazgos anteriores cerrados por COR-005:** H-08, H-16, H-20, H-35 y la fila NFR-000-17 de H-30. H-36 queda
  cerrado en la parte de la sesión. H-46 y H-47 ya estaban cerrados en sus registros (`COR-004.md:310`,
  `COR-005.md:12`, `COR-007.md:173`).

## 4. `[NEEDS CLARIFICATION]` abiertos en los specs (pregunta 4)

Hay **10 apariciones en 8 líneas**. La cuenta de «10 líneas» de la sesión principal incluye las 2 líneas de la
plantilla (`_plantilla/spec-template.md:88-89`), que no son del proyecto. Las ubicaciones coinciden con la referencia
recibida, sin diferencias de línea.

| # | Ubicación | Asunto | Opciones registradas en el spec |
|---|---|---|---|
| 1 | `contrato-datos.md:205` | Si un filtro aplicado sin dejar fuera ningún valor, o con el rango completo de años, cuenta como activo. Si cuenta, deja fuera los estudios con la celda vacía | (a) cuenta como activo; (b) solo si deja fuera algún valor o estrecha el rango |
| 2 | `contrato-datos.md:424` | *(Interno)* Si se comunica al equipo la discrepancia de la tabla 3 | Ninguna; mientras usted no indique otra cosa, se mantiene lo anterior |
| 3 | `000-vision-alcance.md:120` | Límite de NFR-000-19: (1) si 15 MB son 15 000 000 o 15 728 640 bytes; (2) si es fijo o configurable | (1) (a) 15 000 000; (b) 15 728 640. (2) (a) fijo; (b) configurable, con el valor de NFR-000-19 por defecto; (c) configurable, sin superarlo |
| 4 | `000-vision-alcance.md:121` | Si los 45 minutos de inactividad son fijos o configurables | (a) fijo en 45; (b) configurable, 45 por defecto |
| 5 | `001-lectura-verificacion/spec.md:403` (FR-001-29, 1.º) | Filtros ya aplicados tras una carga nueva válida | Ninguna |
| 6 | ídem (2.º) | Si el mensaje de error de contrato omite lo que nombran FR-001-02, 03, 22 y 23 (hoja, encabezado, columna, valor esperado y encontrados) y si la regla vale también para la primera carga | Ninguna; «Decisión de Jairo; no se aplica» |
| 7 | ídem (3.º) | Matriz anterior cuando la carga nueva se rechaza antes de leerla, por tipo o tamaño (NFR-000-19) | Ninguna |
| 8 | `002-mapa-interactivo/spec.md:230` (FR-002-12) | Si ocultar o mostrar una entrada de la leyenda espera a «Actualizar vista» o se aplica de inmediato (US-002-4.5) | El texto enuncia las dos alternativas, sin la etiqueta «Opciones». COR-005, sección 4, NC-4, las registra como (a) espera; (b) se aplica al momento |
| 9 | `002-mapa-interactivo/spec.md:237` (FR-002-19) | Si «Restablecer» aplica de inmediato o solo devuelve los controles hasta pulsar «Actualizar vista» | Dos alternativas enunciadas con su consecuencia: la primera duplica FR-002-18 y la segunda no cumple «una sola acción». Sin opciones etiquetadas |
| 10 | `003-tablero-conclusiones/spec.md:219` | Si «Sin nivel» vale también para los documentos no empíricos en las cifras de documentos del tablero | Ninguna |

Diferencia con la referencia: solo de forma, en los NC 8 y 9. El spec enuncia las alternativas dentro de la pregunta,
mientras que la referencia los da como «sin opciones registradas». Fuera de `docs/specs/` queda un NC ya resuelto:
`calidad-python/SKILL.md:24` (H-56).

## 5. Hallazgos nuevos

Severidad: **bloqueante** impide cerrar el plan de corrección; **mayor** impide cerrar la Fase 1 o empezar la
siguiente sin corregirlo; **menor**, ninguna de las dos. Ningún hallazgo propone cambios en la matriz, sus columnas,
dimensiones, criterios ni metodología.

### Bloqueantes

Ninguno.

### Mayores

**H-54. `fase-1-resumen.md` está desactualizado y no puede servir de resumen de cierre.**
- `:3`: fecha 2026-11-02. `:9`: «Sin commit», cuando ya hay dos commits de la fase.
- `:38-43`: 84 requisitos y 88 escenarios, cuando hoy son 89 y 112, y 2 propuestas sin fuente (FR-001-24, ya
  decidida).
- `:126-149`: 6 NC, con las propuestas de 10 MB (`:137`) y de 30 minutos (`:138`), cuando hoy son 10 NC con 15 MB y
  45 minutos.
- `:151-162`: seis propuestas pendientes, de las que cinco ya decidió (COR-004).
- `:174-175`: dice que el documento técnico «sigue sin versionar», y 63bf5eb lo versionó.

`CLAUDE.md:48` pide un resumen con los NC abiertos al terminar la fase. Propuesta: rehacer el resumen con los datos de
este informe cuando usted dé la fase por revisada.

**H-29 (abierto desde el 2-nov). El colofón publicaría datos no verificados (regla 3).** `pie-de-pagina.md:13-14` da
«Organización y Empresa (GIOE)», «Santa Marta» y «Director del grupo: Óscar García Vargas». `:46-47` los atribuye al
formato de vinculación, que no está en `docs/fuentes/`. Se repitió la búsqueda hoy, incluido el texto extraído de los
dos PDF: solo aparece la sigla «Grupo GIOE». Las líneas no llevan `[POR CONFIRMAR]`. Propuesta: llevarlo por el flujo
de corrección antes de la Fase 2.

**H-32 (abierto desde el 2-nov; pasa de menor a mayor). La guía de diseño contradice una decisión vigente.**
`sistema-diseno-egm/SKILL.md:44` pide mostrar en la cabecera «Matriz v4, 27 documentos, leída el …». NFR-000-12
(`000:85`) e `invariantes.md:48` prohíben ahora, como decisión suya del 3-nov-2026, deducir una versión y escribir
valores a mano. `:21` sigue diciendo que un cajón vacío «es una brecha», en contra de la regla 5 de `CLAUDE.md`. El
`disenador-front` toma esta guía en la Fase 2. COR-005 lo dejó fuera a propósito (3.4, `COR-005.md:114`).

### Menores (observaciones sobre COR-005)

**H-48. `invariantes.md` recoge las decisiones de COR-005 sin un registro escrito de esa edición.** El informe 3-nov-b
§14 dice: «Ninguna decisión de COR-005 quedó como invariante: solo figuran como pendientes de aplicar»
(`conformidad-correcciones-2026-11-03-b.md:586`). También dice que el archivo pasó a 57 líneas (`:566`). Hoy tiene 56,
y `invariantes.md:38` y `:45-48` presentan a, b, c, d, e y f como decisiones, con su NC en `:55-56`. El contenido
coincide con COR-005 1.5 y con los specs, y el encabezado (`inv:3-5`) autoriza a la sesión principal a editarlo. Solo
falta el registro. Propuesta: anotar quién la hizo y cuándo, junto con la sección 9 de COR-005.

**H-49. La aprobación de COR-005 está registrada como inferencia.** `COR-005.md:445`: «Jairo pidió «cerremos COR-005»
sin nombrar letra ni responder las cinco preguntas; la sesión principal registra la opción A (la recomendada) y estos
valores por defecto». Los valores por defecto son cuatro: una sola corrección, «v4» en NFR-000-12 y SC-000-12,
«detalle» en lugar de «ficha» y P2 para US-001-5. Son de redacción (COR-005 3.3) y no cambian reglas, pero los
eligió la sesión principal. Propuesta: que usted los ratifique en la misma sección 6.

**H-50. La tabla de anclas no recoge el nuevo uso del prefijo «No aplica».** `contrato:131` dice que el ancla
«Prefijo no aplicable» se usa solo en la regla 8. Con COR-005, ese prefijo decide también qué estudios van a «Sin
nivel» (`contrato:326`, FR-002-12, `002:210`), y la tabla de impacto de COR-005 (sección 4) no lo menciona. Si el
equipo renombrara ese valor, un nivel «No aplica…» dejaría de ir a «Sin nivel». El hallazgo amplía H-33.

**H-51. FR-001-29 no dice si la carga rechazada termina la sesión.** NFR-000-17 (`000:90`) enumera tres formas de
terminar: descartar, cerrar la pestaña e inactividad. FR-001-29 (`001:403`) manda «limpiar todo», pero no dice si eso
termina la sesión ni si queda abierta sin archivo. Ninguno de los tres NC de FR-001-29 lo trata. El caso afecta a
SC-000-17, que busca marcadores tras el fin de la sesión. Propuesta: registrarlo como NC por el flujo de corrección,
sin decidirlo.

**H-52. Cobertura parcial de FR-001-29.** «Una carga nueva con solo advertencias **o notas** MUST aceptarse»
(`001:403`). US-001-4.8 (`001:211-214`) solo prueba una advertencia. Ningún escenario prueba una carga con solo una
nota, como «columnas no usadas» de FR-001-21. El hallazgo amplía H-30.

**H-53. `trazabilidad.md` no muestra los NC ni la marca «provisional» de los requisitos nuevos o cambiados.**
`traz:54` (FR-001-29, tres NC), `:66` (FR-002-12, NC y «decisión provisional») y `:73` (FR-002-19, NC) muestran solo
la fuente. Es lo que pedía COR-005 5.6, así que no es una desviación del corrector. El hallazgo amplía H-40.

### Menores (documentos y skills)

**H-55. `README_KIT.md:50-56` lista como pendientes cosas ya decididas.**
- `:54`: dónde queda la discrepancia de la tabla 3, decidido el 2-nov-2026 (F6d, `contrato:419`). Sigue abierto solo
  si se comunica al equipo (`contrato:424`).
- `:53`: la métrica de avance por fila (`000:50`).
- `:56`: la versión de Python (`000:135`).
- `:50-51`: en parte, los datos del colofón (NFR-000-11, `000:84`). Sigue pendiente el nombre y el rol de usted
  (`pie-de-pagina.md:21`).

`README.md:17-18` («Los specs están en versión v0») **no** está desactualizado: coincide con `000:4` y con el estado
de los cinco specs, que siguen en v0 hasta el acuerdo de alcance.

**H-56. `calidad-python/SKILL.md:24` conserva el NC de la versión de Python**, resuelto por `000:135`. Ya lo
señalaba `fase-1-resumen.md:184`.

## 6. Estado de los hallazgos que el informe 3-nov-b dejó abiertos (pregunta 7)

| ID | Estado al 21-nov | Evidencia |
|---|---|---|
| H-04 | Abierto | FR-001-12 (`001:386`) sigue pidiendo «N.º, columna y valor» para toda advertencia; las de archivo no los tienen. SC-001-04 (`001:424`), igual |
| H-05 | Abierto | `000:134` se sigue apoyando en «el plan aprobado de la fase», que no está en `docs/fuentes/` ni en `docs/planes/` |
| H-08 | **Cerrado** (COR-005 d) | `contrato:326` (fila de §9, «No aplica» definido); FR-002-12 (`002:230`); US-002-4.11, 4.12. Provisional por decisión suya |
| H-18 | Abierto | `000:137` cita $N_{min}$ en «§6.1» |
| H-21 | Abierto | `003:11` («con el mapa a la vista»); US-003-1.4 depende de US-003-2; US-001-4.6 («todas las vistas») depende de 002 y 003 |
| H-28 | Abierto | `contrato:265-268` solo explica dos causas; los espacios en los extremos (`:88`) quedarían «sin explicar» |
| H-29 | Abierto, **mayor** | Sección 5 |
| H-30 | Abierto en parte | Cerrada la fila NFR-000-17 (SC-000-17, `000:114`; US-001-5.3 a 5.6). Siguen NFR-000-11 (SC-000-11), FR-001-25 (US-001-3.7, `001:259-262`), FR-002-08 (US-002-3.1, 3.2, `002:172-180`) y FR-002-18 (US-002-4.6, `002:125-128`). Se suma H-52 |
| H-31 | Abierto | `000:138`: «solo faltar un encabezado de rol detiene el proceso» |
| H-32 | Abierto, **pasa a mayor** | Sección 5 |
| H-33 | Abierto, ampliado | `contrato:127-139`; ver H-50 |
| H-34 | Abierto | «Celda vacía» como celda de la hoja (`contrato:96`, `:205`; FR-002-12) y «celdas con estudios» del mapa (`003:22`, FR-003-01). COR-005 agregó dos usos en el sentido de la hoja |
| H-35 | **Cerrado** (COR-005 f) | SC-000-09 (`000:106`) y `000:134` dicen «indica»; NFR-000-17 (`000:90`): mostrar el nombre no es un registro |
| H-36 | Cerrado en la parte de la sesión | US-001-4.1 y 4.2 (`001:176-183`). Los filtros tras otra carga pasaron a NC (`001:403`, NC 5) |
| H-37 | Abierto | FR-003-21 (`003:248`) sigue en MUST |
| H-38 | Abierto | US-001-2 (`001:74`) sigue dirigida a Jairo, y el actor «Equipo» (`000:26`) carga la matriz |
| H-39 | Abierto | `contrato:66-74`, sin regla para un bloque de dimensiones degenerado |
| H-40 | Abierto en parte | La marca de FR-002-01 y el NC de NFR-000-12 ya no existen. Siguen sin mostrarse los NC de FR-002-12, FR-002-19 y FR-001-29 (H-53), y SC-001-02 sigue sin enlazarse a FR-001-22 (`traz:143`) |
| H-41 | Abierto | SC-003-06 (`003:268`) frente a FR-003-11, FR-003-16 y FR-003-22 |
| H-46, H-47 | Cerrados | `COR-004.md:310`; `COR-005.md:12`; `COR-007.md:173` |

**Documentos desactualizados.**
- `fase-1-resumen.md` está desactualizado, con la línea de 10 MB en `:137` y otras más (H-54).
- `README_KIT.md:54` (H-55).
- `README.md` está conforme (H-55).

## 7. Plantillas de plan (pregunta 8; solo descripción)

| Aspecto | `_plantilla-plan.md` (versionada, 49 líneas, del commit inicial) | `_plantilla-plan-spec.md` (sin seguimiento, 262 líneas, 4-nov-2026) |
|---|---|---|
| Unidad | Un plan por **módulo** de la arquitectura | Un plan por **spec** (feature); su comentario (`:9`) se declara complemento de la anterior |
| Ubicación | `docs/planes/<modulo>/plan.md` | `docs/planes/NNN-<feature>/plan.md` (`:6`) |
| ID de tareas y pruebas | `T-[modulo]-nn`, `P-[modulo]-nn` | `T-NNN-nn` y `P-NNN-nn`, con `[P]` (paralelo) y `[US-xxx-n]` |
| Estructura | Propósito, alcance, interfaces (consume y expone), pruebas, tareas, dependencias, riesgos y terminado | Resumen, contexto técnico, requisitos con historia y módulo, estructura del proyecto, fases (preparación, base, una por historia, cierre), dependencias, riesgos, terminado y notas |
| Pruebas primero | Sección de pruebas antes de la de tareas | Pruebas antes de la implementación dentro de cada historia |
| Interfaces | Sección propia | Sin sección propia; «Dependencias con otros módulos o specs» (`:229`) |
| Otros | — | Pide «hacer commit después de cada tarea» (notas al final); usa un emoji en `:114` |

Quién cita cada plantilla:
- `_plantilla-plan.md`: `CLAUDE.md:60` («`_plantilla-plan.md`, `<modulo>/plan.md`»; también «plan.md por módulo» en
  `:45`), la skill `plan-modulo/SKILL.md:11-12`, `prompts/PROMPT_FASE_3_planes.md:8-9` y `README_KIT.md:17`. La skill
  `trazabilidad` da como ejemplo `T-lectura-04`, con el formato por módulo.
- `_plantilla-plan-spec.md`: solo la cita `prompts/RETOMAR_2026-11-21.md:14` y `:57`, que tampoco está versionado.
  Ella cita la skill `plan-modulo` como regla (`:10`).

La decisión sobre cuál rige es suya.

## 8. Huecos, excesos y contradicciones

- **Huecos.** Ningún requisito queda sin fuente, salvo la propuesta conocida FR-002-18, ni sin escenario o SC. Las
  coberturas parciales están en H-30 y H-52.
- **Excesos.** No hay componentes, tareas ni código. «Vista tabular de la matriz» se agregó a «Fuera de alcance»
  (`000:58`), así que no amplía el alcance.
- **Contradicciones.** No hay ninguna nueva entre los specs. Fuera de ellos: H-32 (la guía de diseño frente a
  NFR-000-12) y H-48 (un registro frente a `invariantes.md`).

## 9. Resultado para la sección 9 de cada propuesta

| COR | Resultado | Fecha | Motivo |
|---|---|---|---|
| COR-001 a COR-004, COR-006 a COR-008 | `verificada` (sin cambio) | 2026-11-21 | COR-005 no modifica nada de lo que dejaron (sección 3) |
| COR-005 | **`verificada`, con observaciones** | 2026-11-21 | Ver el texto propuesto abajo |

**Texto propuesto para la sección 9 de COR-005:**

> **Verificada con observaciones** el 21-nov-2026 (`docs/informes/conformidad-plan-correccion-2026-11-21.md`),
> en la auditoría única de cierre del plan COR-001 a COR-008. Aplicación literal de 5.1 a 5.7: los 24 textos
> citados están en su spec carácter por carácter. Solo se editaron los ocho archivos de la sección 5, y cada bloque
> del commit b954d30 se atribuye a esta corrección o a COR-004, COR-006, COR-007 y COR-008, sin solaparse. Se
> cumplen todas las búsquedas de 5.8. `trazabilidad.md` tiene 191 líneas, todas CRLF; 89 requisitos en cada tabla y
> fuente igual a la del spec. Requisitos: 89; escenarios: 112; SC: 35; ID únicos, sin huecos ni referencias
> colgantes. 10 NC en 8 líneas. Matriz intacta (SHA-256 `7E1714DE…C3A1`), `docs/fuentes/` sin cambios, reglas 7 y 9
> conformes. El apéndice A no cambia: ninguna fila de $E$ en la v4 tiene solo la secundaria y el estudio del mapa
> tiene nivel. Cierra H-08, H-16, H-20, H-35, la fila NFR-000-17 de H-30 y la parte de la sesión de H-36.
> Observaciones menores, que no invalidan la aplicación: H-48 (`invariantes.md` editado sin registro), H-49
> (aprobación inferida; ratificar los cuatro valores por defecto de la sección 6), H-50 (tabla de anclas), H-51 (si
> la carga rechazada termina la sesión), H-52 (escenario de «solo notas») y H-53 (NC no visibles en
> `trazabilidad.md`). Estado: `verificada`.
