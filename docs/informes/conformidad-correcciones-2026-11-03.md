# Informe de conformidad: cierre del plan de corrección de la fase 1 (COR-001 a COR-004)

**Fecha**: 2026-11-03  
**Auditor**: `verificador`, que no participó en producir lo auditado  
**Encargo**: Jairo, 3-nov-2026  
**Destinatario**: Jairo. Es de uso interno: la observación reservada del apéndice B se menciona aquí sin describirla.  
**Alcance**: COR-001 a COR-004 (estado `aplicada`), auditadas en una sola pasada. Se revisa la aplicación de cada una
contra su sección 5, la opción elegida y su sección 6, y el efecto conjunto sobre `docs/specs/`. COR-005 no existe
todavía. COR-006 está en `propuesta` y no se audita como corrección: solo se señalan sus riesgos frente al estado
actual (sección 7).  
**Punto de partida**: `conformidad-fase-1-2026-11-02.md` (H-24 a H-41). Ese informe no se modifica.

Este informe reporta hallazgos y no corrige ninguno. Las referencias `contrato:N`, `000:N`, `001:N`, `002:N`, `003:N`
y `traz:N` remiten a líneas de los archivos de `docs/specs/` en el árbol de trabajo actual.

## 1. Resumen

| Medida | Resultado |
|---|---|
| Veredicto por corrección | COR-001 `verificada`; COR-002 `verificada`; COR-003 `verificada`; COR-004 **no verificada** (H-44) |
| Requisitos | 86 (67 FR + 19 NFR): FR-001: 27, FR-002: 18, FR-003: 22, NFR-000: 19 |
| Otros identificadores | 35 SC y 98 escenarios. 0 duplicados y 0 referencias colgantes en `docs/specs/` |
| Con fuente o propuesta marcada | 86 de 86. Solo con propuesta: FR-002-18 (P4). Propuesta dentro del contrato: F3 (`contrato:208`) |
| Con escenario o SC | 86 de 86 en la tabla de cobertura, sin referencias colgantes |
| `trazabilidad.md` | 86 + 86 filas, CRLF en 185 de 185 líneas. **Dos fuentes difieren de los specs** (H-44) |
| SHA-256 de `data/raw/` | Coincide antes y después de abrir la matriz |
| `docs/fuentes/` y `data/raw/` | Sin cambios respecto de `HEAD` |
| `invariantes.md` | Igual a `HEAD`. La línea 14 tiene los nombres autorizados (ver 2.3) |
| Apéndice A | Todos los valores coinciden con el recálculo |
| Reglas inviolables | Se cumplen. Las reglas 7 y 9 están conformes |
| Hallazgos nuevos | 2 medios (H-42, H-44) y 2 menores (H-43, H-45) |
| H-28 a H-41 y residuos | Todos siguen abiertos. Quedan parcialmente resueltos H-40 y el residuo de H-08 (sección 6) |

**Dictamen.** COR-001, COR-002 y COR-003 están aplicadas al pie de la letra y encajan entre sí y con el resto del
sistema. COR-004 aplicó tal cual las claves que usted confirmó, pero dejó `trazabilidad.md` con fechas que no
coinciden con los specs en NFR-000-17 y FR-001-20. Ese es un control obligatorio del cierre, así que COR-004 queda
como no verificada mientras no se corrija. La causa está en el texto de la propuesta (su sección 5.9), no en el
corrector. Además, la opción B de COR-004 deja dos textos en contradicción con decisiones suyas (H-42), y COR-006 ya
los trata.

## 2. Comprobaciones obligatorias

### 2.1 Integridad

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA-256 de `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx` | `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1` | Calculado con `certutil` antes de abrir la matriz y con Python antes y después de cada lectura. Es igual a `contrato:365` |
| `git status` / `git diff HEAD -- docs/fuentes data/raw` | Vacío | Los 5 archivos están versionados. Entre `57a14f1` y `63bf5eb` solo se agregó `Documento_tecnico_herramienta_EGM.pdf` |
| Archivos modificados frente a `HEAD` | 6 y 1 nuevo | `COR-004.md`, `000`, `001`, `002`, `contrato-datos.md` y `trazabilidad.md`; nuevo: `COR-006.md` (sin seguimiento en git). Coincide con la lista de la sección 5 de COR-004, opción B |
| Código | No aplica | `src/`, `app/`, `tests/` y `data/fixtures/` solo tienen `.gitkeep`, así que no se ejecutan `ruff`, `mypy` ni `pytest` |

**Límite de la evidencia.** COR-001 a COR-003 se aplicaron antes del commit `63bf5eb`, que es el primero que
contiene los specs. Git no puede mostrar su aplicación como diferencia. Por eso se comprobaron por contenido: cada
texto de su sección 5 está en el lugar indicado y no se hallaron rastros suyos fuera de los archivos de su lista.

### 2.2 Fines de línea

| Archivo | Resultado |
|---|---|
| `trazabilidad.md` | 185 líneas con CRLF, 0 con LF solo. El índice lo guarda normalizado (`i/lf w/crlf`) |
| Demás specs y COR | Solo LF, como en `HEAD` |

Los avisos «LF will be replaced by CRLF» de git se deben a `core.autocrlf=true` y no indican ningún cambio de
contenido.

### 2.3 `invariantes.md`

- `git diff HEAD` está vacío. El archivo entró al historial en `63bf5eb` con la línea 14 ya modificada, y no hay
  ninguna versión anterior en git. Por eso git no puede demostrar que el único cambio fue la línea 14.
- **Evidencia indirecta.** COR-001:128 cita en `invariantes.md:14` los nombres anteriores «verificado»,
  «no verificable» y «discrepancia». Las demás líneas citadas por las COR (`:21`, `:23`, `:27`, `:29`, `:33`)
  conservan el número y el contenido que les atribuyen, y el archivo tiene 35 líneas. Esto concuerda con una
  edición de una sola línea, hecha en su lugar.
- La línea 14 dice: «Estados de verificación: «coincide», «difiere», «no verificable» (nombres fijados por Jairo
  el 2-nov-2026)». Coincide con lo que usted autorizó, con `contrato:268`, `:300-302`, FR-001-14 y FR-001-27.

### 2.4 Identificadores, fuentes y cobertura

Se comprobó con un script propio sobre `docs/specs/`, excluida la plantilla.

| Comprobación | Resultado |
|---|---|
| IDs únicos | 0 duplicados entre 86 requisitos, 35 SC y 98 escenarios |
| Referencias colgantes | 0 en specs, `trazabilidad.md` y la tabla de cobertura |
| FR/NFR con fuente o propuesta | 86 de 86 |
| FR/NFR con escenario o SC | 86 de 86 |
| Fuente de `trazabilidad.md` = fuente del spec | 84 de 86. Difieren NFR-000-17 (`traz:23` frente a `000:89`) y FR-001-20 (`traz:45` frente a `001:334`): H-44 |

### 2.5 Fechas de decisión

| COR | Sección 6 | Specs | `trazabilidad.md` |
|---|---|---|---|
| COR-001 | 2026-11-02 | `contrato:258`, `:283`, `:295`, `:308`; `001:309`, FR-001-26 y FR-001-27: 2-nov-2026 | FR-001-26 y FR-001-27: 2-nov-2026 |
| COR-002 | 2026-11-02 | `contrato:121`: 2-nov-2026 | Sin cambios de fuente, como preveía la propuesta |
| COR-003 | 2026-11-02 | `contrato:112`, `:123`; FR-001-13: 2-nov-2026 | FR-001-13: 2-nov-2026 |
| COR-004, F1, F2, P2, F5a, F6d | 2-nov-2026 | `contrato:258`, `:271`, `:101`, `:85`, `:420` | No tienen fila propia |
| COR-004, F7 (2-nov) y F8 (3-nov) | 2-nov-2026 y 3-nov-2026 | NFR-000-17 con ambas fechas | **Solo 2-nov-2026** (H-44) |
| COR-004, F9 | 3-nov-2026 | FR-001-20 con 2-nov y 3-nov-2026 | **Solo 2-nov-2026** (H-44) |
| COR-004, P1 | 3-nov-2026 | `contrato:83`; FR-002-01 | FR-002-01: 3-nov-2026 |
| COR-004, P3 | 3-nov-2026 | `contrato:108`; FR-001-24 | FR-001-24: 3-nov-2026 |

`contrato:258` lleva la marca de F1, que es de COR-004, y se encuentra dentro del punto 2 de la sección 7, que
COR-001 también modificó.

### 2.6 Reglas inviolables

| Regla | Resultado | Evidencia |
|---|---|---|
| 1. Matriz de solo lectura | Conforme | Hash sin cambios. Se abrió con `openpyxl`, sin llamar nunca a `save()` |
| 2. Sin cambios en el área del equipo | Conforme | Ningún texto nuevo pide cambios en la matriz ni en la hoja. Por ejemplo, `contrato:305` dice que la advertencia «no pide cambios» |
| 3. No afirmar lo no verificado | Conforme, con H-42 | Las reglas no confirmadas siguen marcadas: F3 (`contrato:208`) y P4 (FR-002-18). `contrato:86-88` atribuye mal una prevalencia (H-42) |
| 4. Trazabilidad numérica | Conforme | Los textos nuevos no agregan cifras sin lista de N.º. La nota de lectura (`contrato:401`) se declara aclaración y no valor esperado |
| 5. Brechas provisionales | Conforme | Sin cambios en esos textos |
| 6. Conteos, no porcentajes | Conforme | `contrato` §8 sin cambios |
| 7. Lámina 7 | Conforme | No hay ninguna mención en `docs/specs/`. COR-003:35 la nombra solo para excluirla. Los esperados con cifras pequeñas de `002:31`, `:101`, `003:63` y `:157` son matrices sintéticas descritas en su *Given* y no coinciden con la tabla de esa lámina |
| 8. Textos de usted, sin preguntas | Conforme | Los rótulos nuevos son neutros. No hay tuteo en los textos para el equipo |
| 9. Observación de la tabla 3 | Conforme | En `docs/specs/` solo aparece en el apéndice B (`contrato:403-425`). En `.claude/` está en la skill `contrato-matriz` y en `invariantes.md:29` y `:32`, que es interno. Fuera de eso, solo se menciona en documentos internos para usted (COR-004, COR-006, informes) y en `docs/fuentes/` (ver sección 9) |
| 10. Sin red ni aprendizaje no supervisado | Conforme | Sin cambios |
| 11. Flujo de corrección | Conforme | Cada COR tiene sección 6 marcada y fechada antes de la sección 7. Esta auditoría es la única del plan |

### 2.7 Apéndice A recalculado

Se recalculó con un script propio y `.venv/Scripts/python`. La matriz se abrió con valores, y una segunda vez con
fórmulas, sin guardar. El hash es el mismo antes y después.

| Medida | Contrato | Recálculo |
|---|---|---|
| Rangos de hoja | A1:Y36, A1:J41, A1:B20, A1:F17 | Iguales |
| Validaciones y fórmulas | Filas 2 a 36; filas 2 a 200 | Iguales; 166 fórmulas, todas con rango 2:200 |
| Valores calculados en `EGM` | 0 | 0 numéricos |
| Listas | 6, 3, 6 + No aplica, 7, 4 + No aplica | Iguales |
| Dimensiones | 8, en ese orden | Iguales |
| $\lvert R\rvert$ | 27 | 27 (N.º 1 a 27) |
| Por tipo de documento | 9, 7, 4, 3, 3, 1 | Igual |
| $\lvert E\rvert$, $N$, $\lvert P\rvert$ | 7; 1 (N.º 7); 6 | Igual, con los mismos N.º |
| Estados | 1, 6, 20, 0 | Igual. Los no empíricos son los N.º 1 a 6, 8, 9, 12, 14, 17 a 23 y 25 a 27 |
| Celdas | 6 en 1 y 42 en 0 | Igual, {Transferencia de activos, Acompañamiento técnico} × {Vulnerabilidad, Humano, Financiero} |
| $T_4$ y $t(i)$ | 1, 0, 0, 0; 1 en dos intervenciones | Igual |
| Tipo de fuente y metodología | 6/1/0/20; 6/1/20 | Igual |
| Años | 1992 a 2026 | Igual, todos enteros |
| Enfoque | 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar; en $M$, 1 | Igual |
| Nota de lectura (`contrato:401`) | Los N.º 8 a 27 tienen solo cuatro campos, y son 6 empíricos pendientes y 14 no empíricos | Igual: hay 20 filas con 4 o menos celdas con contenido, que coinciden con las 20 de tipo de fuente vacío |
| Comprobaciones C1 a C5 de COR-001:290-294 | Las cinco se cumplen | Se confirman: `J5`, `J15` y `J25` dicen «Total estudios», `J35` está vacía, `B35` dice «N° de estudios», y `A36:A39` coinciden con la lista de nivel |
| Orden de P1 (`contrato:84`) | «En la v4 ambos órdenes coinciden» | Se confirma: `EGM!A6:A11` sigue el orden de la lista de la columna G |

## 3. Confirmación de los puntos abiertos que las COR dejaron al verificador

| Punto | Resultado |
|---|---|
| COR-001, NC-3: ¿doc. técnico §3.2 y §9.1 fijan alguna regla de alcance o resultado? | No. §9.1 solo excluye una tabla y da «no disponible» sin valores en caché. Las dos secciones son compatibles con la opción A |
| COR-002, NC-1: ¿`Instrucciones` o `Guía…` fijan el estado sin lista? | No. `Instrucciones!A2` dice que la columna D tiene lista desplegable, y `B6` enumera los valores. Ninguna celda fija un tratamiento para cuando falta la lista |
| COR-003: ¿alguna hoja define estados de documento? | No. En la matriz no hay ninguna regla de estados |
| COR-004, NC-1: ¿esas hojas definen fila vacía o el reconocimiento de títulos? | No |
| COR-004, NC-2: ¿otra sección de los PDF fija F1 a F9, P1 o P3? | No. En los dos PDF no aparecen «sesión», «inactividad», «reemplazo de carga», «nombre del archivo» ni «fila vacía». Doc. técnico §2.4 usa el orden de la hoja EGM, y la marca de P1 ya lo registra. §6.9 solo trata la celda vacía de año, como dice la marca de P3 |

## 4. Auditoría de cada corrección

### COR-001: alcance de las tablas de `EGM` y resultado de una comparación incompleta. **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, punto 2 | `contrato:257-258` remite a los puntos 7 y 8 | Sí |
| 5.1, punto 4 | `contrato:268`, «según el punto 9» | Sí |
| 5.1, punto 5 | `contrato:272` agrega «comparación incompleta sin diferencias» | Sí |
| 5.1, puntos 7 a 9 | `contrato:278-308`, literal, con la marca del 2-nov-2026 | Sí |
| 5.2, §9 | Filas nuevas en `contrato:349-353`. `:354` y `:356` tienen el tratamiento nuevo | Sí |
| 5.3, spec 001 | *Given* de US-001-3.1 y 3.5; US-001-3.9 a 3.16; Edge Case `001:309`; FR-001-26 y FR-001-27; Key Entities `001:353` | Sí |
| 5.4, `trazabilidad.md` | `traz:51-52` y `:105`, `:133`, `:135`, `:144`, `:145` | Sí |
| Sección 6 | Opción A, 2026-11-02, marca convertida en decisión | Sí |

El apéndice B no cambió, y su remisión a la «sección 7, punto 6» (`contrato:417`) sigue siendo válida. COR-004 F1
agregó una marca en el punto 2 sin alterar el texto de COR-001. No se encontraron efectos no previstos.

### COR-002: estados de documento sin lista de tipo de documento. **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, condiciones | `contrato:118-119`, condicionadas a que haya lista | Sí |
| 5.1, párrafo nuevo | `contrato:121`, con la marca del 2-nov-2026 | Sí |
| 5.2, §9 | `contrato:344` agregada; `:346` reemplazada. El rótulo actual viene de COR-003 | Sí |
| 5.3, spec 001 | US-001-2.15 y 2.16; Edge Case `001:307` | Sí. Los *Then* llevan el rótulo de COR-003, como esa corrección preveía |
| 5.4, cobertura | `traz:131`, `:140` | Sí |

Los estados forman una partición de $R$ con lista y sin lista. Con la matriz real, el resultado sigue siendo
1, 6, 20 y 0 (sección 2.7).

### COR-003: rótulo «Pendiente de codificación». **Verificada**

| Sección 5 | Estado actual | Conforme |
|---|---|---|
| 5.1, marca de `contrato:111-112` | Fuente dividida por estado, con 2-nov-2026 | Sí |
| 5.1, trato de «No empírico» y fila renombrada | `contrato:118-119` | Sí |
| 5.1, párrafo sobre avance | `contrato:123` | Sí |
| 5.2, §9 | `contrato:325`, `:346` | Sí |
| 5.3, apéndice A | `contrato:387` y nota de lectura `:401`. La nota es correcta frente a la matriz (2.7) | Sí |
| 5.4, spec 001 | US-001-1.9, 2.15 y 2.16; `001:298`, `:299`, `:307`; FR-001-13; Key Entities `001:345` | Sí |
| 5.5, `traz:38` | Fuente igual a la del spec | Sí |
| Sección 6 | La skill no se editó: `contrato-matriz` no tiene cambios desde `57a14f1` | Sí |

En `docs/specs/` queda una sola aparición de «pendiente de codificación», la deliberada de `contrato:123`, y sigue
siendo cierta porque la skill conserva esa frase (`SKILL.md:27`).

### COR-004: atribución de origen (H-27), opción B. **No verificada**

| Sección 5 / 5.9 | Estado actual | Conforme |
|---|---|---|
| F1 | `contrato:258`, 2-nov-2026 | Sí |
| F2 y P2 | `contrato:271` y `:101-103`, 2-nov-2026 | Sí |
| F3 (no confirmada; marca de A) | `contrato:208`, texto de 5.3. La marca de `:216` no cambió | Sí |
| F5a | `contrato:85`, 2-nov-2026; F5b conserva su cita en `:86` | Sí, con H-42 |
| F6b y F6d | `contrato:420`, con la cita de doc. técnico §9.1 y «Decisión de Jairo, 2-nov-2026: entender» | Sí |
| F7 y F8 | NFR-000-17 (`000:89`): «decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026», como pide la fila F7–F9 de 5.9. El texto no cambió | Sí en el spec; **no** en `traz:23` (H-44) |
| F9 | FR-001-20 (`001:334`), con el mismo formato | Sí en el spec; **no** en `traz:45` (H-44) |
| P1 | `contrato:83`; FR-002-01; `traz:53` | Sí, con H-43 |
| P3 | `contrato:108`; FR-001-24; `traz:49` | Sí, con H-43 |
| P4 (no confirmada) | FR-002-18 y `traz:70` sin tocar | Sí |
| Solo los archivos de la sección 5 | `git diff` confirma que no se tocó nada más | Sí |
| Ninguna palabra fuera de las marcas | `git diff` solo muestra marcas | Sí |

**Motivo del veredicto.** La aplicación respeta la letra de la sección 5.9 y de la sección 6. Pero deja
`trazabilidad.md` sin el 3-nov-2026 en NFR-000-17 y FR-001-20, mientras sus specs sí lo tienen. Así falla un control
obligatorio de cierre: que la trazabilidad coincida con los specs y que las fechas coincidan con la sección 6 (H-44).
El defecto viene de la propuesta: su tabla de impacto (COR-004:139) dice que en B cambia `trazabilidad.md`, pero la
fila F7–F9 de 5.9 no lo nombra. El corrector debe tocar la trazabilidad «solo en lo que la propuesta indica»
(`corrector.md`, paso 4). La sección 8 de COR-004 declara «`trazabilidad.md` al día» con esa salvedad explícita.
Además, H-43 y H-42 son efectos de esta misma aplicación. No bloquean por sí solos, pero conviene tratarlos junto con
H-44.

## 5. Hallazgos nuevos

### Medios

**H-42. Tras COR-004 (opción B), dos textos contradicen decisiones que usted confirmó.**

- `.claude/skills/contrato-matriz/SKILL.md:27` define fila vacía como «columna A vacía», contra F5a (`contrato:85`,
  COR-004:261).
- `SKILL.md:65-66` dice que la comparación de la tabla reservada «debe registrarse como discrepancia conocida».
  Eso contradice F6d (`contrato:420`, COR-004:262), la sección 7, punto 6, y `invariantes.md:29`.
- `contrato:86-88` dice que «prevalece el doc. técnico §9.2» sobre la definición de la skill. La definición ya no
  se atribuye a §9.2 sino a su decisión (`contrato:85`), y §9.2 no define fila vacía (sección 3).

La skill se carga en los agentes de las fases siguientes, que podrían tomar la regla de la columna A o anotar la
discrepancia en los registros de ejecución. El conteo actual no cambia, porque las filas 29 a 36 están vacías en
todas sus celdas. **COR-006 trata exactamente estos tres puntos** con sus opciones A o C. La opción B dejaría
`contrato:86-88` sin resolver.

**H-44. `trazabilidad.md` no refleja la decisión del 3-nov-2026 en NFR-000-17 ni en FR-001-20 (desviación conocida 2).**

| Requisito | Spec | `trazabilidad.md` |
|---|---|---|
| NFR-000-17 | `000:89`: «decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026» | `traz:23`: «decisión de Jairo, 2-nov-2026» |
| FR-001-20 | `001:334`: igual | `traz:45`: «decisión de Jairo, 2-nov-2026» |

Clasificación: es medio porque rompe un control de integridad que los informes del 1 y del 2-nov daban por superado
(«fuentes idénticas a las de los specs») y porque la fecha de F8 y F9 no queda trazada. No cambia ningún
comportamiento. El origen está en el texto de COR-004 (5.9 frente a la tabla de impacto, COR-004:139), y su
corrección requiere el flujo de la regla 11. Propuesta: una corrección de riesgo bajo que agregue
«; decisión de Jairo, 3-nov-2026» en `traz:23` y `:45`, conservando CRLF.

### Menores

**H-43. Minúscula después del punto en dos marcas del contrato (desviación conocida 1).**
`contrato:83` dice «decisión de Jairo, 3-nov-2026. el doc. técnico §2.4…», y `contrato:108-109` dice «…3-nov-2026.
el doc. técnico §6.9…». Es un error de forma, sin efecto en el significado. Viene del reemplazo literal de 5.9
(P1 y P3), que COR-004:284 declara. En P2 (`contrato:101-102`) no ocurre, porque el texto sigue con «§9.2».
Propuesta: corregirlo en la misma corrección que H-44.

**H-45. `invariantes.md` no registra las decisiones aprobadas en COR-001 a COR-004.**
Su encabezado (`invariantes.md:3-4`) dice que el archivo se actualiza cuando usted toma una decisión nueva, con su
fecha. Sin embargo, no contiene las decisiones aprobadas al cerrar este plan:

- las reglas de alcance, emparejamiento y resultado de la verificación (COR-001);
- los estados sin lista y el rótulo «Sin tipo de documento válido» (COR-002 y COR-003);
- las claves F1, F2 con P2, F5a, F6d, F7, F8, F9, P1 y P3 (COR-004).

El analista usa ese archivo para detectar conflictos, y COR-006:4 tuvo que citar COR-004 como fuente de F5a y F6d.
No es un defecto de los specs, y el archivo solo lo edita usted. Propuesta: que usted decida si incorpora esas
decisiones fechadas antes de la fase de arquitectura.

## 6. Estado de los hallazgos pendientes

Ninguna COR del plan trató estos hallazgos de forma directa. Se indica su estado actual sin volver a auditarlos a
fondo.

| ID | Estado | Evidencia actual |
|---|---|---|
| H-04 (residuo) | Abierto, ampliado | FR-001-12 (`001:326`) y SC-001-04 siguen pidiendo «N.º, columna y valor» para todas las advertencias. Ahora hay más advertencias que no tienen esos datos: las de tabla de COR-001 (`contrato:304`) y las de columna de COR-002 (`contrato:121`). COR-001:104 y COR-002:104 lo previeron |
| H-05 (residuo) | Abierto | `000:133` sigue apoyándose en un «plan aprobado de la fase», que no está en `docs/fuentes/` ni en `docs/planes/` |
| H-08 (residuo) | Abierto, en parte aclarado | El NC de «sin nivel» sigue en FR-002-12 (`002:215`) y `invariantes.md:33`. COR-004 marcó como propuesta la regla de celda vacía y filtro activo (F3, `contrato:208`), que según COR-004 sección 6 tratará COR-005. Siguen sin entrada en §9 el nivel vacío y el nivel «No aplica…» |
| H-18 (residuo) | Abierto | `000:136` sigue citando $N_{min}$ en «§6.1» |
| H-21 (residuo) | Abierto | `003:10-11` todavía dice «con el mapa a la vista» |
| H-28 | Abierto | `contrato:268-271` explica dos causas. Los espacios en los extremos (`contrato:90-91`) siguen sin explicación, y «si persiste» sigue sin definir qué se lista cuando hay causas combinadas. F2 ya es decisión suya, pero no resuelve H-28 |
| H-29 | Abierto | `pie-de-pagina.md:13-14` y `:46` no han cambiado |
| H-30 | Abierto | La cobertura de NFR-000-11, NFR-000-17, FR-001-25, FR-002-08 y FR-002-18 no cambió. En NFR-000-17, F7 confirma el texto, pero SC-000-17 sigue sin comprobar el fin por inactividad. COR-005 la tratará |
| H-31 | Abierto | `000:137` sin cambio |
| H-32 | Abierto | `sistema-diseno-egm/SKILL.md:21` y `:44` sin cambio |
| H-33 | Abierto | `contrato:127-143` sin cambio. COR-002:119 registró que sin lista el riesgo de dos anclas aumenta |
| H-34 | Abierto | «Celda» con dos sentidos. COR-001 usó «valor» para no agravarlo |
| H-35 | Abierto | SC-000-09 (`000:105`) sigue diciendo «registra», y F8 confirma que el nombre del archivo no va en los registros. La tensión sigue y ahora la respalda una decisión |
| H-36 | Abierto | Sin cambio. Según COR-004 sección 6, COR-005 tratará la carga fallida y la definición de sesión |
| H-37 | Abierto | FR-003-21 (`003:238`) sigue con MUST |
| H-38 | Abierto | `001:69` sigue dirigida a Jairo |
| H-39 | Abierto | `contrato:66-74` sin cambio |
| H-40 | Parcialmente resuelto | FR-002-01 ya no oculta una propuesta: P1 fue confirmada y `traz:53` coincide. Siguen ocultos el NC de FR-002-12 (`traz:64`) y el de NFR-000-12 (`traz:18`). SC-001-02 sigue sin enlazarse a FR-001-22 (`traz:140`). Las marcas de NFR-000-17 y FR-001-20 ya son decisiones, pero quedan desalineadas (H-44) |
| H-41 | Abierto | SC-003-06 (`003:258`) sin cambio |

## 7. COR-006 frente al estado actual (propuesta, no evaluada como corrección)

- **Cobertura.** Sus opciones A y C cierran H-42 completo. La B deja `contrato:86-88` con una atribución que no se
  sostiene.
- **Textos citados.** Coinciden con el árbol actual: `SKILL.md:27`, `:65-66` y `:76`, y `contrato:85-88`. La
  condición de 3.4 («COR-004 en `aplicada`») se cumple. Sin embargo, COR-004 no está verificada (H-44). Si la
  corrección de H-43 y H-44 se aplica antes, no hay solapamiento de texto: toca `contrato:83`, `:108` y
  `traz:23`, `:45`, y COR-006 toca `contrato:86-88` y la skill.
- **COR-005 desconocida.** COR-006:168 lo reconoce. Según COR-004 sección 6, COR-005 tocará F3 (`contrato:208`),
  NFR-000-17 y FR-001-20. Si además toca la regla 4 o la skill, tendrá que partir del texto que deje COR-006.
- **Archivo fuera de `docs/specs/`.** COR-006 edita una skill. Cumple la condición de COR-003:102, que exige que
  usted nombre el archivo al aprobar. `corrector.md` no prohíbe ese archivo.
- **Regla 9.** El texto nuevo de 5.2 mantiene la observación solo en la skill y remite al apéndice B. No la lleva a
  otro archivo.
- **Diferencias que quedan.** La skill seguirá distinta del contrato en lo señalado en COR-006 3.3: recalcular frente
  a valor guardado, letras de columna, el símbolo $J_r$ y «No aplica» exacto. COR-006 no las trata. La más relevante
  para la arquitectura es la de recalcular, que sigue a cargo del futuro ADR de verificación (COR-001, NC-2).

## 8. Huecos, excesos y contradicciones

- **Huecos.** Ningún requisito queda sin fuente ni sin escenario o SC. Siguen las coberturas parciales de H-30.
- **Excesos.** No hay componentes, tareas ni código. Siguen sin decisión dos elementos: FR-002-18 (P4) y F3.
- **Contradicciones.** H-42 (skill y contrato frente a F5a y F6d) y H-44 (trazabilidad frente a specs).

### `[NEEDS CLARIFICATION]` abiertos en `docs/specs/` (6, sin cambios)

| Ubicación | Asunto |
|---|---|
| `contrato-datos.md:175` | Fila con la intervención principal vacía y la secundaria diligenciada |
| `contrato-datos.md:425` | *(Interno)* Si se comunica al equipo la observación del apéndice B |
| `000-vision-alcance.md:84` | Identificación de la matriz en el colofón (NFR-000-12) |
| `000-vision-alcance.md:119` | Límite de tamaño del archivo |
| `000-vision-alcance.md:120` | Tiempo de inactividad que termina la sesión |
| `002-mapa-interactivo/spec.md:215` | Estado «sin nivel» en el control único (FR-002-12) |

### Propuestas sin fuente, pendientes de aprobación (2)

`contrato-datos.md:208` (F3, que según COR-004 sección 6 reemplazará COR-005) y FR-002-18 (`002:221`, `traz:70`; P4).

## 9. Observaciones fuera de lo auditado

No son hallazgos contra las correcciones.

- La observación reservada también aparece en `docs/fuentes/`: doc. técnico §3.4(a) y §9.1, y
  `estado_proyecto_2026-10-31.md:31` y `:57`. Son fuentes suyas, de solo lectura. Si comparte el doc. técnico con
  el equipo, la regla 9 aplica también a ese documento.
- Doc. técnico §5.3 propone detenerse ante cualquier cambio de lista. `000:137` ya registra que prevalece su decisión
  del 1-nov-2026. La nota sigue incompleta (H-31).
- `docs/informes/fase-1-resumen.md` sigue sin actualizar desde el 1-nov.

## 10. Resultado para la sección 9 de cada propuesta

| COR | Resultado | Fecha | Motivo |
|---|---|---|---|
| COR-001 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 a 5.4. Opción A y fecha coherentes. Sin efectos no previstos. NC-3 confirmado |
| COR-002 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 a 5.4. Partición de estados correcta. NC-1 confirmado en la matriz |
| COR-003 | `verificada` | 2026-11-03 | Aplicación literal de 5.1 a 5.5. Apéndice A y nota de lectura correctos frente a la matriz |
| COR-004 | no verificada | 2026-11-03 | H-44: `trazabilidad.md` no coincide con los specs en NFR-000-17 y FR-001-20 (fecha 3-nov-2026). También son efecto de esta aplicación H-43 (forma) y H-42, que trata COR-006 |
