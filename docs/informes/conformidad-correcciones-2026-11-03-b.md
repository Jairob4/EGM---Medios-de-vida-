# Informe de conformidad: cierre del plan de corrección de la fase 1 (COR-004, COR-006, COR-007 y COR-008) y coherencia de `invariantes.md`

**Fecha**: 2026-11-03  
**Auditor**: `verificador`, que no participó en producir lo auditado  
**Encargo**: Jairo, 3-nov-2026  
**Destinatario**: Jairo. Es de uso interno: la observación reservada del apéndice B se nombra aquí sin describirla.  
**Alcance**:
- Parte 1: COR-004 (no verificada el 3-nov por H-44 y H-43), COR-006, COR-007 y COR-008 (las tres en `aplicada`),
  auditadas en una sola pasada, y su efecto conjunto sobre el sistema completo. COR-005 sigue en `propuesta` y no se
  audita como aplicada: solo se señala su relación con lo aplicado.
- Parte 2: coherencia de `.claude/skills/analisis-impacto/references/invariantes.md` con las secciones 6 de COR-001 a
  COR-008, los specs vigentes, `CLAUDE.md` y `000-vision-alcance.md`.

**Punto de partida**: `conformidad-correcciones-2026-11-03.md` (H-42 a H-45). Ese informe no se modifica.

Este informe reporta hallazgos y no corrige ninguno. Las referencias `contrato:N`, `000:N`, `001:N`, `002:N`, `003:N`,
`traz:N`, `skill:N` e `inv:N` remiten a líneas del árbol de trabajo actual de `docs/specs/contrato-datos.md`, los
specs 000 a 003, `docs/specs/trazabilidad.md`, `.claude/skills/contrato-matriz/SKILL.md` e `invariantes.md`.

## 1. Resumen

| Medida | Resultado |
|---|---|
| Veredicto por corrección | COR-004 `verificada`; COR-006 `verificada`; COR-007 `verificada`; COR-008 `verificada` |
| Requisitos | 86 (67 FR + 19 NFR): FR-001: 27, FR-002: 18, FR-003: 22, NFR-000: 19 |
| Otros identificadores | 35 SC y 98 escenarios. 0 duplicados y 0 referencias colgantes |
| Con fuente o propuesta marcada | 86 de 86. Solo con propuesta: FR-002-18 (P4). Propuesta dentro del contrato: F3 (`contrato:206`) |
| Con escenario o SC | 86 de 86 |
| Fuente de `trazabilidad.md` = fuente del spec | **86 de 86** (antes 84 de 86) |
| `trazabilidad.md` | 185 líneas, todas con CRLF. Los demás specs, la skill y las COR, solo LF, como en `HEAD` |
| SHA-256 de `data/raw/` | `7E1714DE…C3A1`, igual a `contrato:363`. La matriz no se abrió en esta auditoría |
| `docs/fuentes/` | Sin cambios respecto de `HEAD` |
| Reglas 7 y 9 | Conformes |
| NC-2 de COR-008 | Confirmado: ningún texto de `docs/fuentes/` fija un tamaño de archivo |
| Hallazgos nuevos | 2 menores (H-46, H-47). Ninguno bloquea |
| H-42, H-43, H-44 | Cerrados por COR-006 y COR-007. H-45 se trata en la parte 2 |
| `invariantes.md` | 19 hallazgos de coherencia (INV-01 a INV-19): 13 faltas, 4 imprecisiones y 2 obsoletos. Ninguna contradicción directa con un spec |

**Dictamen.** Las tres correcciones nuevas están aplicadas al pie de la letra, solo en los archivos de su lista
cerrada, y encajan entre sí y con COR-001 a COR-004. COR-007 corrige la causa por la que COR-004 no quedó verificada:
la trazabilidad coincide ahora con los specs en los 86 requisitos, y las fechas de COR-004, sección 6, quedan
trazadas. COR-006 cierra H-42 completo. COR-008 fija el valor en un solo sitio y deja marcado lo que la decisión no
cubre. Por eso las cuatro quedan verificadas. Los dos hallazgos nuevos son textos de registro que quedaron atrás
(COR-004, sección 9, y COR-005, que todavía es propuesta). `invariantes.md` no registra ninguna decisión posterior al
2-nov-2026 y le faltan varias del 2-nov aprobadas en las correcciones.

---

# Parte 1. Correcciones

## 2. Comprobaciones obligatorias

### 2.1 Integridad

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA-256 de `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1` | `sha256sum`; igual a `contrato:363` y al valor del encargo |
| `docs/fuentes/` | Sin cambios | `git status --short docs/fuentes` vacío; último commit que lo toca: `63bf5eb` |
| Archivos modificados frente a `HEAD` | 10, y 5 sin seguimiento | `SKILL.md` de `contrato-matriz`; COR-001 a COR-004; `000`, `001`, `002`, `contrato-datos.md`, `trazabilidad.md`. Sin seguimiento: COR-005 a COR-008 y el informe anterior |
| Cada cambio tiene su COR | Sí | Ver 2.2 |
| `invariantes.md` | Igual a `HEAD` | No aparece en `git status`. Es objeto de la parte 2 |
| Código | No aplica | `src/`, `app/`, `tests/` y `data/fixtures/` siguen sin contenido; no se ejecutan `ruff`, `mypy` ni `pytest` |

### 2.2 Atribución de cada diferencia con `HEAD`

| Lugar | Cambio | Corrección |
|---|---|---|
| `contrato:83` | Marca de P1 y «El» con mayúscula | COR-004 (P1) y COR-007 (5.2) |
| `contrato:85-86` | Marca de F5a; frase sobre la skill eliminada | COR-004 (F5a) y COR-006 (5.3) |
| `contrato:99-101` | Marca de P2 | COR-004 |
| `contrato:106-107` | Marca de P3 y «El» con mayúscula | COR-004 (P3) y COR-007 (5.2) |
| `contrato:206` | Marca de propuesta de F3 | COR-004 |
| `contrato:256`, `:269` | Marcas de F1 y F2 | COR-004 |
| `contrato:418` | Marca de F6b y F6d | COR-004 |
| `000:89` | Fuente de NFR-000-17 | COR-004 (F7, F8) |
| `000:91`, `000:119` | Valor de 15 MB y NC nuevo | COR-008 (5.1, 5.2) |
| `001:334`, `001:338` | Fuentes de FR-001-20 y FR-001-24 | COR-004 (F9, P3) |
| `002:204` | Fuente de FR-002-01 | COR-004 (P1) |
| `traz:23`, `:45` | Fecha del 3-nov | COR-007 (5.1) |
| `traz:25` | Fecha del 3-nov | COR-008 (5.3) |
| `traz:49`, `:53` | Fuentes de FR-001-24 y FR-002-01 | COR-004 |
| `skill:27-28` | Regla 3, fila vacía | COR-006 (5.1) |
| `skill:66-71` | Observación interna, última oración | COR-006 (5.2) |
| COR-001 a COR-004 | Estado y sección 9 | Sesión principal, con el informe anterior |

No hay ninguna diferencia sin corrección que la explique.

### 2.3 Identificadores, fuentes y cobertura

Se comprobó con un script propio sobre `docs/specs/`, sin la plantilla.

| Comprobación | Resultado |
|---|---|
| IDs únicos | 0 duplicados entre 86 requisitos, 35 SC y 98 escenarios |
| Referencias colgantes | 0 en los specs, en `trazabilidad.md` y en la tabla de cobertura |
| FR/NFR con fuente o propuesta | 86 de 86 |
| FR/NFR con escenario o SC | 86 de 86 |
| Filas de `trazabilidad.md` | 86 en la tabla principal y 86 en la de cobertura, sin ID ajenos a los specs |
| Fuente de `trazabilidad.md` = fuente del spec | 86 de 86 |
| `NEEDS CLARIFICATION` | 6 en los specs: contrato 2, 000 3, 002 1. Igual que antes de COR-008, que reemplazó uno por otro |
| «Propuesta sin fuente» | contrato 1 (F3), 002 1 (FR-002-18), `trazabilidad.md` 1 (FR-002-18) |

### 2.4 Fines de línea

| Archivo | Líneas | Con CRLF |
|---|---|---|
| `trazabilidad.md` | 185 | 185 (índice `i/lf`, árbol `w/crlf`) |
| `contrato-datos.md`, `000`, `001`, `002`, `003` | 423, 137, 363, 239, 258 | 0 |
| `contrato-matriz/SKILL.md` | 85 | 0 (índice y árbol `lf`) |
| COR-001 a COR-008 | — | 0 |

### 2.5 Fechas de decisión

| COR | Sección 6 | Specs y skill | `trazabilidad.md` |
|---|---|---|---|
| COR-004, F1, F2 con P2, F5a, F6d | 2-nov-2026 | `contrato:256`, `:269`, `:99`, `:85`, `:418` | Sin fila propia |
| COR-004, F7 (2-nov) y F8 (3-nov) | 2-nov y 3-nov-2026 | NFR-000-17 (`000:89`) con las dos fechas | `traz:23` con las dos fechas |
| COR-004, F9 | 3-nov-2026 | FR-001-20 (`001:334`) con 2-nov y 3-nov | `traz:45` con las dos fechas |
| COR-004, P1 | 3-nov-2026 | `contrato:83`; FR-002-01 (`002:204`) | `traz:53` |
| COR-004, P3 | 3-nov-2026 | `contrato:106`; FR-001-24 (`001:338`) | `traz:49` |
| COR-006 | 3-nov-2026 (aprobación) | La skill cita «decisión de Jairo, 2-nov-2026» (`skill:28`) y «decisiones de Jairo del 2-nov-2026» (`skill:70`). Son las fechas de F5a y F6d en COR-004, sección 6, que es lo que la skill aplica. La fecha de aprobación no se escribe en ningún texto, como preveía 5.1 y 5.2 | Sin cambio, como preveía la propuesta |
| COR-007 | 3-nov-2026 | Sin fechas nuevas: copia a la tabla las de COR-004 | `traz:23`, `:45` |
| COR-008 | 3-nov-2026 | NFR-000-19 (`000:91`): «decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026» | `traz:25`, igual |

Todas las fechas coinciden con la sección 6 de su corrección.

### 2.6 Reglas inviolables

| Regla | Resultado | Evidencia |
|---|---|---|
| 1. Matriz de solo lectura | Conforme | Hash sin cambios. La matriz no se abrió |
| 2. Sin cambios en el área del equipo | Conforme | Ningún texto nuevo pide cambios en la matriz |
| 3. No afirmar lo no verificado | Conforme | COR-008 marca como NC lo que la decisión no fija (`000:119`). F3 y P4 siguen marcadas. La atribución falsa de `contrato:86-88` ya no existe |
| 4. Trazabilidad numérica | Conforme | El único número nuevo es el límite de 15 MB, que no es un dato de la matriz |
| 5 y 6 | Conforme | Sin cambios en esos textos |
| 7. Lámina 7 | Conforme | Ninguna mención en `docs/specs/` ni en la skill. En `.claude/` solo aparece en reglas que la prohíben (`verificador.md:18`, `especificacion-srs/SKILL.md:41`, `inv:18`). El valor 15 no procede de la tabla de esa lámina (`presentacion_equipo_2026-10_texto.md:98-108`) |
| 8. Textos de usted, sin preguntas | Conforme | El NC nuevo de `000:119` va dirigido a usted y no tiene preguntas: ofrece opciones |
| 9. Observación de la tabla 3 | Conforme | En `docs/specs/` solo está en el apéndice B (`contrato:406`, `:423`). En `.claude/` solo en la skill `contrato-matriz` (`skill:64-71`) y en `inv:29`, `:32`, que son internos. Entre las COR nuevas solo la nombra COR-006, que es interna y lo declara (COR-006:15). No hay contenido en `docs/interfaz/`, `app/` ni `src/` |
| 10. Sin red ni no supervisado | Conforme | Sin cambios |
| 11. Flujo de corrección | Conforme | COR-006, COR-007 y COR-008 tienen la sección 6 marcada y fechada antes de su sección 7. Esta es la única auditoría del cierre |

### 2.7 NC-2 de COR-008: tamaño de archivo en `docs/fuentes/`

| Fuente | Método | Resultado |
|---|---|---|
| `Documento_tecnico_herramienta_EGM.pdf` (22 páginas) | Texto extraído completo, con `pdftotext` y con `pypdf`; ninguna página quedó sin texto | 0 coincidencias de `MB`, `KB`, `GB`, `MiB`, `megas`, `bytes`, «tamaño máximo», «tamaño del archivo» o «límite de tamaño». «Tamaño» solo aparece referido a la burbuja o a efectos (líneas 155, 163, 492 y 1009 del texto extraído) |
| `propuesta_herramienta_general.pdf` (10 páginas) | Igual | 0 coincidencias. «Tamaño» solo se refiere a la burbuja (línea 128 del texto extraído) |
| `estado_proyecto_2026-10-31.md`, `presentacion_equipo_2026-10_texto.md` | Búsqueda | 0 coincidencias |

**Confirmado.** Ninguna fuente fija un tamaño de archivo. La única fuente del valor es su decisión del 3-nov-2026,
y no hace falta ninguna nota en «Notas sobre las fuentes» de `000`.

## 3. Auditoría de cada corrección

### COR-004: atribución de origen (H-27), opción B. **Verificada**

| Motivo del «no verificada» del 3-nov | Estado actual | Resuelto |
|---|---|---|
| H-44: `traz:23` y `:45` sin la fecha del 3-nov | `traz:23` y `traz:45` dicen «decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026», igual que `000:89` y `001:334` | Sí, por COR-007 |
| H-43: minúscula en las reglas 3 y 12 | `contrato:83` y `:107` dicen «El doc. técnico». El patrón `-20\d\d\.\s+[a-záéíóúñ]` da 0 casos en `docs/specs/` y en `.claude/` | Sí, por COR-007 |
| H-42: la skill y `contrato:86-88` frente a F5a y F6d | La skill coincide con F5a y F6d, y la frase se eliminó | Sí, por COR-006 |

Las demás claves (F1, F2 con P2, F3 como propuesta, F5a, F6b, F6d, F7, F8, F9, P1, P3 y P4 sin tocar) conservan el texto
que el informe anterior dio por conforme. COR-006 y COR-007 no movieron ninguna marca de decisión, solo quitaron una
frase vecina y cambiaron una letra. Los NC-1 y NC-2 de COR-004 se confirmaron el 3-nov (informe anterior, sección 3).

**Motivo del veredicto.** Ya se cumple el control que faltaba: la trazabilidad coincide con los specs y las fechas
coinciden con la sección 6. Queda un texto desactualizado en su sección 9, que no afecta a la aplicación (H-46).

### COR-006: skill `contrato-matriz` y regla 4 del contrato, opción A. **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, regla 3 de la skill | `skill:27-28`, literal. Se conserva «pendiente de codificación» | Sí |
| 5.2, observación interna | `skill:66-71`, literal. La oración anterior («La herramienta aplica la regla documentada…») no cambió | Sí |
| 5.3, `contrato` regla 4 | `contrato:85-86` queda igual al texto de 5.3, con las dos marcas intactas | Sí |
| 5.4 (solo opción C) | No se aplicó | Sí |
| Lista cerrada | Solo la skill, el contrato y COR-006. El frontmatter de la skill y `referencia-v4.md` no cambiaron | Sí |
| Sección 6 | Opción A, 3-nov-2026, con autorización expresa para editar la skill | Sí |

**Comprobación de 5.5** (recontada en esta auditoría):

| Patrón | Esperado | Actual |
|---|---|---|
| `columna A vacía` en skill y contrato | 0 y 0 | 0 y 0 (tampoco en el resto del repositorio fuera de informes y COR) |
| `debe registrarse` en la skill | 0 | 0 |
| `todas sus celdas vacías` y `registros de ejecución` en la skill | 1 y 1 | 1 y 1 |
| `pendiente de codificación` en la skill | 1 | 1 |
| `` `contrato-matriz` `` en el contrato | 2 | 2 (`contrato:121`, `:243`) |
| `tabla 3` en `docs/specs/` | 2 líneas del apéndice B | `contrato:406`, `:423` |

**Efecto en el sistema.** La skill dice ahora lo mismo que `contrato:85`, el apéndice B (`contrato:416-418`), la
sección 7, punto 6, FR-001-25 y NFR-000-17. Las frases del contrato que describen la skill (`contrato:121` y `:243`)
siguen siendo ciertas. Quedan las diferencias que COR-006 3.3 solo señaló, sin proponerlas: recalcular frente a valor
guardado (`skill:76-78`), letras de columna y la notación $J_r$. No son defectos de esta corrección.

### COR-007: H-44 y H-43, opción A. **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, `traz:23` (NFR-000-17) | Literal, con CRLF | Sí |
| 5.1, `traz:45` (FR-001-20) | Literal, con CRLF | Sí |
| 5.2, regla 3 (`contrato:83`) | «3-nov-2026. El doc. técnico §2.4» | Sí |
| 5.2, regla 12 (`contrato:107`) | «El doc. técnico §6.9», con la sangría de cuatro espacios | Sí |
| 5.3, búsquedas | Las siete se cumplen: dos filas nuevas, 185 líneas con CRLF, 0 casos del patrón, las dos frases con mayúscula y 86 de 86 | Sí |
| Lista cerrada | Solo `trazabilidad.md`, el contrato y COR-007 | Sí |
| Sección 6 | Opción A, 3-nov-2026 | Sí |

El corrector no recontó el total de 86 (COR-007:166). Esta auditoría lo recontó: 86 de 86. Hay una remisión de COR-007
a un texto que no existe (H-47).

### COR-008: límite de 15 MB, opción A. **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, NFR-000-19 | `000:91`, literal. El texto anterior se conserva y se agrega una oración | Sí |
| 5.2, «Puntos abiertos» | `000:119`, literal. El NC de inactividad (`000:120`) no se tocó | Sí |
| 5.3, `traz:25` | Literal, con CRLF | Sí |
| 5.4, búsquedas | `10 MB` 0; `15 MB` 1; `27 KB` 0; NC en `000` 3; NC en los specs 6; fila de NFR-000-19 1; CRLF 185 | Sí |
| No se tocan el contrato, 001, SC-000-19 | `contrato:32` sigue remitiendo al límite de `000`; `contrato:335` dice «mayor que el límite»; US-001-4.4 (`001:186-189`) y SC-000-19 (`000:115`) sin cambios | Sí |
| Sección 6 | Opción A, 3-nov-2026 | Sí |
| NC-2 | Confirmado (2.7) | Sí |

**Efecto en el sistema.** SC-000-19 y US-001-4.4 ya tienen un valor contra el cual probar, salvo el borde exacto, que
depende del NC de `000:119` (MB o MiB). El invariante «ningún spec menciona v4» se respeta: el NC nuevo ya no dice «la
v4 pesa 27 KB». El valor está en un solo sitio, y las remisiones del contrato y de US-001-4.4 lo alcanzan sin
repetirlo.

## 4. Efecto conjunto

- **Superposición.** COR-004, COR-006 y COR-007 tocan la sección 4 del contrato en reglas distintas (3, 4, 10 y 12).
  Cada texto final coincide con la última corrección que lo tocó, y no se pisan entre ellas. COR-007 y COR-008 tocan
  filas distintas de `trazabilidad.md` (23, 45 y 25) y conservan CRLF.
- **Totales.** Siguen 86 requisitos, 35 SC, 98 escenarios, 6 NC y 185 líneas de trazabilidad. Ninguna corrección
  creó ni eliminó un ID.
- **Skill frente a contrato.** En fila vacía y registros, la skill dice ahora lo mismo que el contrato. Las demás
  diferencias son las conocidas (COR-006 3.3).
- **Apéndice A.** Ninguna corrección del plan cambia un valor. $\lvert R\rvert = 27$ sigue igual con la definición
  de F5a, como se comprobó el 3-nov.
- **COR-005 (propuesta).** Se escribió antes de que se aplicaran COR-006, COR-007 y COR-008. No choca con el texto
  que dejaron:
  - su 5.2 (g) reemplaza la línea de inactividad, que sigue en `000:120`;
  - su cuenta de NC (6 → 10) sigue valiendo, porque COR-008 reemplazó un NC por otro;
  - su 5.2 (c) reemplaza NFR-000-17 completa, con la misma fuente doble.

  Pero contiene partes que ya se aplicaron o que quedaron atrás (H-47).

## 5. Hallazgos nuevos

### Menores

**H-46. La sección 9 de COR-004 dice que COR-005 corrige H-44, pero lo corrigió COR-007.**
`COR-004.md:310`: «COR-005, sección 5.6, corrige H-44. Sigue en `aplicada`.» H-44 y H-43 los corrigió COR-007
(`COR-007.md:3-4`, `:155-156`). Es un texto de registro que escribió la sesión principal y no afecta a los specs.
Propuesta: al pasar el resultado de este informe a la sección 9, que el texto nuevo reemplace esa frase y cite
COR-007.

**H-47. COR-005, todavía en propuesta, conserva texto que ya quedó atrás por COR-006, COR-007 y COR-008.**
- `COR-005.md:10` dice que COR-006 está en `propuesta`. Está `aplicada`.
- `COR-005.md:22`, `:33` y `:53`, y su 5.6 (`:408`, `:410`, `:413`), presentan como pendiente la fuente de
  NFR-000-17 y FR-001-20 en `trazabilidad.md`. COR-007 ya la corrigió. Esas filas de 5.6 reemplazarían el texto por
  otro idéntico. No tendría efecto, pero la evidencia de 1.2 y la comprobación de su sección 8 serían falsas.
- `COR-007.md:57` y `:99` remiten a una «nota final del analista» sobre COR-005, que no existe en COR-007 ni en
  COR-005.

No afecta a ninguna corrección aplicada. Si COR-005 se aprueba tal como está, el corrector partiría de una evidencia
desactualizada. Propuesta: que el `analista-impacto` revise COR-005 antes de que usted la apruebe (sus secciones 1,
4 y 5.6) contra el estado actual. Al hacerlo, que quite la parte de H-44 y actualice el estado de COR-006.

## 6. Estado de hallazgos anteriores afectados por este plan

| ID | Estado | Evidencia |
|---|---|---|
| H-42 | Cerrado | COR-006 (sección 3) |
| H-43 | Cerrado | COR-007 (sección 3) |
| H-44 | Cerrado | COR-007; 86 de 86 (2.3) |
| H-45 | Se trata en la parte 2 | `invariantes.md` sigue igual a `HEAD` |
| H-30 | Abierto, en parte | SC-000-19 ya tiene valor. El borde exacto depende del NC de `000:119`. La fila de NFR-000-17 depende de COR-005 |
| H-40 | Abierto, en parte | Se cerró la desalineación de NFR-000-17 y FR-001-20. Siguen ocultos el NC de FR-002-12 (`traz:64`) y el de NFR-000-12 (`traz:18`), y SC-001-02 sigue sin enlazarse a FR-001-22 |
| H-04, H-05, H-08, H-18, H-21, H-28, H-29, H-31 a H-39, H-41 | Sin cambios | No los trató ninguna corrección de este plan |

## 7. Huecos, excesos y contradicciones

- **Huecos.** Ningún requisito queda sin fuente ni sin escenario o SC. Siguen las coberturas parciales de H-30.
- **Excesos.** No hay componentes, tareas ni código. Siguen sin decisión F3 (`contrato:206`) y FR-002-18 (P4).
- **Contradicciones.** Ninguna nueva entre specs, trazabilidad y skill. Las de H-42 y H-44 quedaron resueltas.

### `[NEEDS CLARIFICATION]` abiertos en `docs/specs/` (6)

| Ubicación | Asunto |
|---|---|
| `contrato-datos.md:173` | Fila con la intervención principal vacía y la secundaria diligenciada (H-16) |
| `contrato-datos.md:423` | *(Interno)* Si se comunica al equipo la observación del apéndice B |
| `000-vision-alcance.md:84` | Texto del colofón y versión de la matriz (NFR-000-12, H-20) |
| `000-vision-alcance.md:119` | **Nuevo (COR-008).** Si 15 MB son 15 000 000 o 15 728 640 bytes, y si el límite es fijo o configurable |
| `000-vision-alcance.md:120` | Tiempo de inactividad que termina la sesión |
| `002-mapa-interactivo/spec.md:215` | «Sin nivel» en el control único (FR-002-12, H-08) |

Cuatro de ellos (H-16, H-20, inactividad y H-08) tienen ya una decisión suya que COR-005 aplicaría.

## 8. Observaciones fuera de lo auditado

No son hallazgos contra las correcciones.

- `README_KIT.md:54` todavía plantea como abierta si la discrepancia reservada «se muestra en la interfaz o queda solo
  en registros internos». Usted lo decidió el 2-nov-2026 (F6d y `contrato:418`).
- `docs/informes/fase-1-resumen.md` sigue sin actualizar desde el 1-nov-2026, y su línea 137 conserva la propuesta de
  10 MB.

## 9. Resultado para la sección 9 de cada propuesta

| COR | Resultado | Fecha | Motivo |
|---|---|---|---|
| COR-004 | `verificada` | 2026-11-03 | H-44 y H-43 corregidos por COR-007 y H-42 por COR-006. La trazabilidad coincide con los specs en 86 de 86, y las fechas con la sección 6. La frase de su sección 9 sobre COR-005 queda desactualizada (H-46) |
| COR-006 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 a 5.3, sin 5.4. Las búsquedas de 5.5 se cumplen. La skill coincide con F5a, F6d y el contrato. Regla 9 conforme |
| COR-007 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 y 5.2. Las búsquedas de 5.3 se cumplen. CRLF conservado; 86 de 86 |
| COR-008 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 a 5.3. Las búsquedas de 5.4 se cumplen. NC-2 confirmado: ninguna fuente fija un tamaño |

---

# Parte 2. Coherencia de `invariantes.md`

## 10. Método

Se comparó `invariantes.md` (35 líneas, igual a `HEAD`), línea por línea, con:
- las secciones 6 de COR-001 a COR-004 y COR-006 a COR-008;
- los specs vigentes y `trazabilidad.md`;
- `CLAUDE.md`;
- `000-vision-alcance.md`.

COR-005 no está aprobada, así que sus decisiones no se proponen como invariantes. La sección 12 solo las lista como
pendientes de aplicar.

Clases de hallazgo:
- **Falta**: una decisión aprobada y aplicada que no figura.
- **Contradice**: el texto se opone a un spec o a una decisión posterior.
- **Obsoleto**: dice pendiente lo que ya está decidido.
- **Impreciso**: dice menos que el spec, o puede leerse de otra forma.

No se encontró ninguna contradicción directa. Todas las líneas actuales son compatibles con los specs.

Formato de las propuestas:
- Cada propuesta da el texto exacto que se agregaría o que reemplazaría al actual, con la fecha de la decisión.
- Se conserva la estructura por fechas del archivo y se agrega una sección para el 3-nov-2026.
- La observación reservada sigue solo en este archivo interno (regla 9).

## 11. Hallazgos INV

### Encabezado

**INV-01 (obsoleto). `inv:3-5`: quién edita el archivo.**
Dice que el archivo «se actualiza solo cuando Jairo toma una decisión nueva» y que ni el analista ni el corrector lo
editan. Usted autorizó a la sesión principal a editarlo (encargo del 3-nov-2026), y COR-008:100 ya lo da por hecho.
Además, el archivo no dice que recoge las decisiones aprobadas en las secciones 6 de las COR, que son hoy la mayor
parte. Reemplazo de las líneas 3-5:

> Lista de lo que ninguna corrección puede alterar. Recoge las decisiones fechadas de Jairo, incluidas las aprobadas
> en la sección 6 de cada corrección (`docs/correcciones/COR-NNN.md`). Se actualiza cuando Jairo toma una decisión
> nueva, con su fecha. La edita la sesión principal, por autorización de Jairo (3-nov-2026); ni el analista ni el
> corrector la editan. Las reglas permanentes están en `CLAUDE.md`.

### Decisiones del 1-nov-2026

**INV-02 (falta). Escalabilidad y matrices de otros proyectos.**
Origen: `000:16-18`, `000:55` y `contrato:11-15`, todos con «decisión de Jairo, 1-nov-2026». `inv:18` solo dice que
ningún spec compara versiones, y no recoge el alcance. Adición en «Decisiones del 1-nov-2026»:

> - **Escalabilidad**: la herramienta procesa las versiones presentes y futuras de la matriz del estado del arte de
>   este proyecto que cumplan el contrato, sin reconstruirse. No compara una matriz con otra versión ni guarda valores
>   de referencia. Las matrices de otros proyectos quedan fuera de alcance.

**INV-03 (falta). Filtros que quedan como mejora futura.**
Origen: `000:51-52`, «decisión de Jairo, 1-nov-2026». Adición en «Decisiones del 1-nov-2026»:

> - Filtros por intervención, dimensión o enfoque diferencial: mejora futura, fuera de esta versión.

**INV-04 (impreciso). `inv:17`: el filtro de año.**
FR-002-10 (`002:213`, 1-nov-2026) fija además los extremos. Reemplazo de la línea 17:

> - **Mapa**: el filtro por nivel de evidencia y el mostrar/ocultar de la leyenda son un solo control. El filtro de
>   año es por rango, desde y hasta, con ambos extremos incluidos.

### Decisiones del 2-nov-2026

**INV-05 (falta). Verificación cruzada: tablas comparables, alcance, emparejamiento y resultado (COR-001, opción A,
2-nov-2026).**
Origen: `contrato:270-306`, FR-001-25, FR-001-26 y FR-001-27. `inv:14` solo trae los nombres de los estados.
Adición en «Decisiones del 2-nov-2026»:

> - **Verificación cruzada** (COR-001): solo se comparan e informan las tablas comparables de total de estudios,
>   evaluación de impacto y nivel de evidencia, cada una por el número inicial de su título. Las demás tablas de la
>   hoja no se leen ni generan advertencias. Cada tabla se delimita y sus filas y columnas, incluida «Total
>   estudios», se emparejan solo dentro de ella. «Coincide» exige comparar todos los valores esperados. Si algún
>   valor comparado es distinto, «difiere». En los demás casos, incluida una comparación incompleta sin diferencias,
>   «no verificable». Si no se compara todo, una advertencia indica lo no comparado y no pide cambios en la matriz.
>   Lo no comparado nunca es 0.

**INV-06 (falta). Reconocimiento del título de una tabla comparable (F1, COR-004, 2-nov-2026).**
Origen: `contrato:253-256`. Adición:

> - Una tabla comparable se reconoce por una celda que empieza por un número seguido de punto y contiene su frase
>   propia, sin distinguir mayúsculas. Si ninguna celda lo cumple, o lo cumple más de una, la tabla no se reconoce
>   (F1, COR-004).

**INV-07 (falta). Dimensión escrita como texto y explicación de diferencias (F2 con P2, COR-004, 2-nov-2026).**
Origen: `contrato:98-101` y `:266-269`, y COR-004:260. Adición:

> - Un valor de dimensión escrito como texto (por ejemplo, «1» como texto) es advertencia y no marca la dimensión, a
>   diferencia del número 1 (P2). Cuando la hoja EGM difiere de la herramienta, la diferencia se explica primero por
>   las filas con la misma intervención en principal y secundaria y, si persiste, por las filas con dimensión escrita
>   como texto, que se listan (F2). Ambas en COR-004.

**INV-08 (falta). Estados de documento, partición sin lista y rótulo (COR-002 y COR-003, opción A, 2-nov-2026).**
Origen: `contrato:109-121` y `:143-150`, y FR-001-13. Adición:

> - **Estados de documento** (COR-002 y COR-003): cada documento queda en uno solo de estos estados: «En el mapa»,
>   «Empírico pendiente», «No empírico» o «Sin tipo de documento válido». «No empírico» no se lista como pendiente ni
>   genera advertencia por esa razón. El rótulo es «Sin tipo de documento válido» y no «pendiente de codificación»,
>   que la skill `contrato-matriz` conserva. Si el tipo de documento no tiene lista, todo valor no vacío distinto
>   del valor ancla es no empírico, y la advertencia de la columna indica los valores presentes. Tipo de documento,
>   tipo de fuente y metodología sin lista generan advertencia y usan los valores presentes. No hay métrica de
>   avance por fila.

**INV-09 (falta). Fila vacía (F5a, COR-004, 2-nov-2026; aplicada también en la skill por COR-006).**
Origen: `contrato:85-86`, `skill:27-28` y COR-004:261. Adición:

> - **Fila vacía**: todas sus celdas están vacías. Una fila con `N°` vacío y con contenido no es vacía: se procesa con
>   advertencia y se identifica por su número de fila del archivo (F5a, COR-004).

**INV-10 (impreciso). `inv:23`: carga y sesión.**
La línea no dice:
- cuándo empieza y termina la sesión (F7, confirmada el 2-nov-2026 con el texto de NFR-000-17, COR-004:263);
- que el tipo y el tamaño se validan antes de leer (NFR-000-19 y `contrato:30-34`, 2-nov-2026);
- que cada sesión empieza sin datos (`000:48`, 2-nov-2026).

Reemplazo de la línea 23:

> - **Carga de la matriz**: desde el navegador. Antes de leerlo, se validan el tipo y el tamaño del archivo; el que
>   no cumpla se rechaza con un mensaje legible y sin resultados parciales. El archivo vive solo durante la sesión;
>   no se guarda en base de datos, disco del servidor ni registros, y los registros no contienen datos de la matriz.
>   Una sesión va desde que se carga la matriz hasta que quien la usa cierra la herramienta o vence el tiempo de
>   inactividad (F7, COR-004). Cada sesión es independiente y empieza sin datos. El archivo cargado nunca se
>   modifica.

**INV-11 (falta). Advertencia de enfoque diferencial (2-nov-2026).**
Origen: `contrato:240-241` y FR-001-10. `inv:29` solo recoge el caso de los N.º 2 y 7. Adición:

> - La advertencia de enfoque diferencial cita la regla de la hoja Instrucciones (B14) y no agrega nada más.

**INV-12 (impreciso). `inv:28`: selección múltiple.**
FR-002-11 (`002:214`), con fuente «doc. técnico §4.1 RF2; decisión de Jairo, 2-nov-2026», admite varios valores
también en nivel de evidencia. Allí la selección múltiple se ejerce con el control único de la leyenda, que es una
decisión del 1-nov-2026. Reemplazo de la línea 28:

> - Selección de varios valores en tipo de fuente y metodología. En nivel de evidencia, varios valores se eligen con
>   el control único de la leyenda (FR-002-11).

Si su decisión del 2-nov-2026 cubría solo los dos primeros filtros, lo que habría que revisar es FR-002-11 y no este
archivo. En ese caso basta con dejar la línea 28 como está.

**INV-13 (impreciso). `inv:29`: dónde queda la discrepancia interna (F6d, COR-004, 2-nov-2026; skill alineada por
COR-006).**
«Registros internos» puede leerse como registros de ejecución, que es justo la lectura que usted descartó.
Origen: `contrato:414-418`, `skill:66-71` y COR-004:262. Reemplazo de la línea 29:

> - **Interno**: la tabla 3 de la hoja EGM no es comparable: la herramienta no la compara ni la calcula, y la interfaz
>   no muestra esa comparación. La discrepancia queda solo en los registros internos del proyecto (apéndice B del
>   contrato e informes para Jairo) y no se anota en los registros de ejecución de la herramienta (F6d, COR-004).
>   Los N.º 2 y 7 se muestran «Sin clasificar».

### Decisiones del 3-nov-2026 (sección nueva)

**INV-14 (falta). Orden del archivo (P1, COR-004, 3-nov-2026).**
Origen: `contrato:81-84` y FR-002-01. Adición en una sección nueva «## Decisiones del 3-nov-2026», a continuación de la
del 2-nov:

> - **Orden del archivo** (P1, COR-004): las dimensiones van en el orden de sus columnas. Las intervenciones y los
>   niveles van en el orden de su lista de validación, y las que solo están en la lista de secundaria van al final.
>   No se toma el orden de la hoja EGM.

**INV-15 (falta). Año no reconocido (P3, COR-004, 3-nov-2026).**
Origen: `contrato:104-107` y FR-001-24. Adición:

> - **Año no reconocido** (P3, COR-004): un año que no sea número entero es advertencia. El documento se cuenta, no
>   cumple un filtro de año activo y en la composición por año aparece como «año no reconocido», separado de «sin
>   diligenciar».

**INV-16 (falta). Nombre del archivo fuera de los registros (F8, COR-004, 3-nov-2026).**
Origen: NFR-000-17 (`000:89`). Adición:

> - Los registros de la herramienta no contienen el nombre del archivo cargado (F8, COR-004).

**INV-17 (falta). Carga nueva (F9, COR-004, 3-nov-2026).**
Origen: FR-001-20 (`001:334`) y COR-004:265. Adición:

> - Una carga nueva reemplaza a la anterior dentro de la sesión (F9, COR-004). Lo que pasa si la carga nueva falla
>   no está aplicado (ver pendientes).

**INV-18 (falta). Límite de tamaño (COR-008, opción A, 3-nov-2026).**
Origen: NFR-000-19 (`000:91`). Adición:

> - **Límite de tamaño** (COR-008): 15 MB. Un archivo de ese tamaño se acepta y uno mayor se rechaza. El valor vive
>   solo en NFR-000-19; los demás textos remiten a él.

### Pendientes

**INV-19 (obsoleto e incompleto). `inv:31-35`: «Pendientes de Jairo».**
- Obsoleto: H-08, H-16 y H-20 (`inv:33-35`) ya tienen decisión suya (COR-005, 1.5, filas d, e y f; 3-nov-2026). Esa
  decisión no está aplicada, porque COR-005 sigue en `propuesta`, así que deben seguir como pendientes, pero de
  aplicar y no de decidir.
- Faltan tres pendientes que siguen abiertos en los specs:
  - el NC de COR-008 (`000:119`);
  - las propuestas sin aprobar F3 (`contrato:206`) y P4 (FR-002-18);
  - el tiempo de inactividad (`000:120`).

Reemplazo de las líneas 31-35:

> ## Pendientes de Jairo (no resolver por cuenta propia)
> - Si se comunica al equipo la observación de la tabla 3 (apéndice B del contrato).
> - Límite de tamaño: si 15 MB son 15 000 000 o 15 728 640 bytes, y si el límite es fijo o configurable
>   (`000-vision-alcance.md`, «Puntos abiertos»; COR-008).
> - Propuestas sin aprobar: qué es un filtro activo y que una celda vacía no lo cumpla (F3, contrato §5); quitar los
>   filtros en una sola acción (P4, FR-002-18).
> - Decididos por Jairo, pendientes de aplicar en COR-005 (en `propuesta`; no rigen hasta que se aplique):
>   - F3: filtro activo y botones de los filtros (2-nov-2026).
>   - F7: inicio y fin de la sesión, actividad e inactividad, y su tiempo (2-nov-2026).
>   - F9: carga nueva con error de contrato (3-nov-2026).
>   - H-08: estado «sin nivel» en el control único de la leyenda (3-nov-2026, provisional).
>   - H-16: intervención principal vacía con secundaria diligenciada (3-nov-2026).
>   - H-20: texto del colofón y versión de la matriz (3-nov-2026).

## 12. Decisiones de COR-005 ya tomadas y pendientes de aplicar

Se listan solo para registrarlas como pendientes en INV-19. No se proponen como invariantes, porque COR-005 no está
aprobada. Fuente: COR-005, tabla 1.5.

| Clave | Asunto | Fecha que registra COR-005 | Texto vigente en los specs |
|---|---|---|---|
| a, F3 | Filtro activo con «Actualizar vista» y «Restablecer», estado común y celda vacía | 2-nov-2026 | `contrato:206`, como propuesta |
| b, F7 | Sesión: descartar, cerrar la pestaña, inactividad y su tiempo | 2-nov-2026 | `000:89` y NC de `000:120` |
| c, F9 | Carga nueva con error de contrato | 3-nov-2026 | Sin regla |
| d, H-08 | «Sin nivel» en la leyenda, provisional | 3-nov-2026 | NC de `002:215` |
| e, H-16 | Principal vacía y secundaria diligenciada | 3-nov-2026 | NC de `contrato:173` |
| f, H-20 | Texto del colofón sin versión deducida | 3-nov-2026 | NC de `000:84` |

## 13. Comprobación de lo que no requiere cambio

| Líneas | Contenido | Resultado |
|---|---|---|
| `inv:8-10` | Decisiones del 31-oct-2026 | Coinciden con `CLAUDE.md` (reglas 10 y Convenciones), `000:43-45`, `000:61-63`, NFR-000-11 y NFR-000-13 |
| `inv:13` | Dimensiones | Coincide con `contrato:66-74`, FR-001-03 y FR-001-04 |
| `inv:14` | Hoja EGM | Coincide con `contrato:25`, `:250-252`, `:266-271`, FR-001-15 y FR-001-16. Lleva la fecha del 2-nov-2026 para los nombres, dentro de la sección del 1-nov, y lo dice expresamente |
| `inv:15` | Porcentajes | Coincide con NFR-000-07, `contrato:308-317` y la regla 6 de `CLAUDE.md` |
| `inv:16` | Filtros | Coincide con FR-002-13 a FR-002-15 y FR-003-13 a FR-003-16 |
| `inv:18` | Escenarios y lámina 7 | Coincide con la regla 7 de `CLAUDE.md` y `especificacion-srs` |
| `inv:21-22` | Errores de contrato y columnas ajenas | Coinciden con `contrato:38-40`, `:62-64`, `:133-150`, FR-001-21 a FR-001-23 y FR-003-22 |
| `inv:24` | Primera versión local | Coincide con `000:67` y `000:124` |
| `inv:25` | Colofón | Compatible con NFR-000-11, que lo generaliza: no publica ningún dato pendiente de confirmación |
| `inv:26` | Versión de Python | Coincide con `000:134` |
| `inv:27` | Sin avance por fila; definiciones aparte | Coincide con `000:50`, `000:128` y FR-002-08 |

## 14. Cambios aplicados por la sesión principal en invariantes.md

Aplicados el 3-nov-2026 por la sesión principal, con la autorización de Jairo del mismo día («corrígelo sin
preguntarme»). Se usó el texto exacto de la sección 11, sin cambios de redacción; solo se unió cada viñeta en una
línea, como el resto del archivo. `invariantes.md` pasa de 35 a 57 líneas.

| INV | Clase | Cambio aplicado |
|---|---|---|
| INV-01 | Obsoleto | Encabezado reemplazado: recoge las secciones 6 de las COR y lo edita la sesión principal por autorización de Jairo |
| INV-02 | Falta | Agregada «Escalabilidad» en las decisiones del 1-nov-2026 |
| INV-03 | Falta | Agregados los filtros que son mejora futura (1-nov-2026) |
| INV-04 | Impreciso | Línea «Mapa»: el rango de años es desde y hasta, con ambos extremos incluidos |
| INV-05 | Falta | Agregada «Verificación cruzada» (COR-001) en el 2-nov-2026 |
| INV-06 | Falta | Agregado el reconocimiento del título de una tabla comparable (F1) |
| INV-07 | Falta | Agregadas la dimensión escrita como texto (P2) y la explicación de diferencias (F2) |
| INV-08 | Falta | Agregados los estados de documento (COR-002 y COR-003) |
| INV-09 | Falta | Agregada la definición de fila vacía (F5a) |
| INV-10 | Impreciso | Línea «Carga de la matriz» reemplazada: validación previa de tipo y tamaño, sesión (F7) y sesión sin datos al empezar |
| INV-11 | Falta | Agregada la advertencia de enfoque diferencial (B14) |
| INV-12 | Impreciso | Línea de selección múltiple ampliada al nivel de evidencia mediante la leyenda (FR-002-11). Queda en pie la salvedad de la sección 11: si la decisión del 2-nov-2026 cubría solo dos filtros, lo que se revisa es FR-002-11 |
| INV-13 | Impreciso | Línea «Interno» reemplazada: la tabla 3 no se compara ni se calcula y la discrepancia no va a los registros de ejecución (F6d) |
| INV-14 a INV-18 | Falta | Nueva sección «Decisiones del 3-nov-2026»: orden del archivo (P1), año no reconocido (P3), nombre fuera de los registros (F8), carga nueva (F9) y límite de 15 MB (COR-008) |
| INV-19 | Obsoleto | «Pendientes de Jairo» reescrita: observación de la tabla 3; NC del límite de tamaño; F3 y P4 sin aprobar; F3, F7, F9, H-08, H-16 y H-20 como decididos y pendientes de aplicar en COR-005 |

Ninguna decisión de COR-005 quedó como invariante: solo figuran como pendientes de aplicar.

Otros registros hechos por la sesión principal con este informe:
- Sección 9 y estado `verificada` en COR-004, COR-006, COR-007 y COR-008.
- H-46: en la sección 9 de COR-004, la frase sobre COR-005 queda precisada (la corrigió COR-007).
- H-47: COR-005 ya fue revisada por el `analista-impacto` el 3-nov-2026 y no trata H-44; en COR-007 queda una nota
  en su sección 9 sobre la «nota final del analista».
