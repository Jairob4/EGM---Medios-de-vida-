# Hallazgos sobre la matriz del equipo — archivo de trabajo

> **Documento de trabajo interno, para Jairo.** No es el texto para el equipo ni se comparte con él.
> Sirve de insumo para la sección dirigida al equipo del informe final de la fase. Mientras ese informe no
> esté aprobado, la tabla 3 de la hoja `EGM` no aparece en ningún texto para el equipo.
> `[Fuente: decisión de Jairo, 21-nov-2026]`

**Matriz revisada:** `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx`, abierta en modo lectura el
21-nov-2026. SHA-256 `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`, el mismo del
contrato (apéndice A).

**Clasificación** `[Fuente: decisión de Jairo, 21-nov-2026]`:

- **Grupo A, «Afecta a la herramienta»**: cambia lo que la herramienta lee, calcula o muestra, o hace que
  rechace, advierta o excluya.
- **Grupo B, «No afecta a la herramienta»**: observación sobre la matriz que la herramienta no usa ni
  calcula.

**Estado de la construcción** (26-nov-2026). El plan 001 está implementado y verificado (`docs/informes/conformidad-plan-001-2026-11-26.md`).
«Especificado en» indica el requisito o la sección que lo fija. A-03 queda en parte para los planes 002 y 003.

## Grupo A · Afecta a la herramienta

| ID | Hallazgo | Ubicación en la matriz | Regla de «Instrucciones» | Tratamiento de la herramienta | Estado |
|---|---|---|---|---|---|
| A-01 | La celda de enfoque de género/diferencial no empieza por «Sí», «No» ni «Parcial» («Lo incluye…», «El estudio se hizo…») | `Matriz bibliográfica`, columna U, N.º 2 (U3) y N.º 7 (U8) | B14: «Sí / No / Parcial + una frase» | Muestra el documento como «Sin clasificar» en enfoque, con una advertencia que cita B14. El N.º 7 está en el mapa, así que también cuenta como «Sin clasificar» en las cifras de enfoque del mapa | Implementada en `egm.lectura` (enfoque) y `egm.textos` (P-001-20, P-001-39); con la v4 da dos advertencias, N.º 2 y N.º 7. Verificada en `conformidad-plan-001-2026-11-26.md`. Especificado en `contrato-datos.md` §6, §9 (fila «Columna de enfoque sin prefijo válido») y apéndice A (filas «Enfoque») |
| A-02 | Estudios empíricos con el resto de la fila sin diligenciar: sin intervención y sin ninguna dimensión en 1 | `Matriz bibliográfica`, N.º 10, 11, 13, 15, 16 y 24 (columnas F a S vacías) | B20: para aparecer en la hoja EGM hace falta «Tipo de intervención diligenciado y al menos una dimensión en 1». B9 y B12 | No entran al mapa. Se listan como «estudios empíricos pendientes» | Implementada en `egm.lectura` (estados) y `egm.conteo` (conjunto $P$) (P-001-13, P-001-28); con la v4, N.º 10, 11, 13, 15, 16 y 24. Verificada en `conformidad-plan-001-2026-11-26.md`. Especificado en FR-001-13; `contrato-datos.md`, apéndice A (fila «Estado de los documentos») |
| A-03 | Documentos con solo N.º, referencia, año y tipo de documento: tipo de fuente, metodología, enfoque, intervención y nivel vacíos | `Matriz bibliográfica`, N.º 8 a 27 (filas 9 a 28; columnas F a J, U y siguientes) | B8 (tipo de fuente), B10 (metodología), B14 (enfoque). Para los documentos no empíricos, B9 y B11 piden «No aplica» en intervención y nivel | Se cuentan como «sin diligenciar», en una categoría visible (FR-003-09). Una celda vacía no cumple un filtro activo, así que el documento sale de la vista mientras haya un filtro activo en ese campo. En el filtro de nivel, por decisión de Jairo del 21-nov-2026 (COR-009), los no empíricos se tratan como «Sin nivel» y solo salen al ocultar esa entrada. Los empíricos pendientes de este grupo (N.º 10, 11, 13, 15, 16 y 24), con el nivel vacío, sí salen mientras el filtro de nivel esté activo | Implementada en parte: la lectura de vacíos en `egm.lectura` (P-001-14); los filtros y la categoría «sin diligenciar» visibles quedan para los planes 002 y 003. Especificado en FR-003-09, FR-003-14, FR-002-12, `contrato-datos.md` §5 (filtros) y §9 (fila de documentos no empíricos y «Sin nivel»); apéndice A (filas de tipo de fuente, metodología y enfoque) |
| A-04 | La hoja `EGM` no guarda resultados calculados: tiene las fórmulas, pero ninguna celda numérica con su valor | `EGM`, bloques 1 a 4 (A5:J11, A15:J21, A25:J31, A35:B39) | B20: «Se calcula sola con fórmulas desde la matriz» | La verificación cruzada con la hoja `EGM` da «no verificable», con advertencia y sin error. Esto pasa con el archivo tal como está guardado | Implementada en `egm.verificacion` (P-001-46); con la v4, las tablas 1, 2 y 4 dan «no verificable». Verificada en `conformidad-plan-001-2026-11-26.md`. Especificado en FR-001-16 y FR-001-27; `contrato-datos.md`, apéndice A (fila «Verificación cruzada») |

## Grupo B · No afecta a la herramienta

| ID | Hallazgo | Ubicación en la matriz | Regla de «Instrucciones» | Tratamiento de la herramienta | Estado |
|---|---|---|---|---|---|
| B-01 | La tabla 3 de la hoja `EGM` («con enfoque de género/diferencial = Sí») aplica el criterio «empieza por Sí» sobre la columna «Humano» (M, valores 1/0) en lugar de la columna de enfoque (U). Por eso da 0 en todas sus celdas con cualquier dato que respete la lista. Su propia nota (A41) la describe en términos de la columna de enfoque | `EGM`, A25:J31; comprobado en las fórmulas de B26 y J26 | B14 (enfoque) y la nota A41 de la hoja `EGM` | La herramienta calcula el enfoque desde su columna (U), no usa esta tabla y no la compara. La interfaz no muestra esa comparación | Implementada en `egm.verificacion`, que no localiza esa tabla (P-001-50); solo se informan las tablas 1, 2 y 4. Verificada en `conformidad-plan-001-2026-11-26.md`. Especificado en `contrato-datos.md` §7 (puntos 6 y 7); detalle interno en `docs/informes/interno-tabla3-hoja-egm.md`. Por decisión de Jairo del 21-nov-2026 se comunica solo en el informe final, como nota del grupo B |
| B-02 | La hoja «Instrucciones» dice que tienen lista desplegable las columnas D, F, G, H e I. El archivo también tiene lista en J (nivel de evidencia) y en las 8 columnas de dimensiones (L a S, `1,0`), como reconoce la misma hoja en B20 para las dimensiones | `Instrucciones`, A2 (frente a B20 y a las validaciones de las filas 2 a 36) | A2 y B20 | Ninguno: la herramienta lee las listas de las validaciones del archivo, no de este texto | Implementada en `egm.libro` y `egm.esquema` (listas desde las validaciones; P-001-05, P-001-14, P-001-36, P-001-37, P-001-40). Verificada en `conformidad-plan-001-2026-11-26.md` |
| B-03 | Los documentos no empíricos tienen vacías las 8 columnas de dimensiones, aunque «Instrucciones» pide marcarlas con 1/0 sin limitarlo a los estudios empíricos | `Matriz bibliográfica`, columnas L a S de los N.º 1 a 6 y 8 a 27 | B12 | Ninguno: todos los conteos con dimensiones se limitan a estudios empíricos (`contrato-datos.md`, conjuntos $E$ y $M$, $S$, $T_1$, $T_2$). Una celda vacía no activa la advertencia de valor no válido. Si alguna de esas celdas tuviera un valor distinto de 1, 0 o vacío, la herramienta sí advertiría y el caso sería del grupo A | Implementada en `egm.conteo` (dimensiones solo en $E$; P-001-11, P-001-25); con la v4, ninguna advertencia de dimensión. Verificada en `conformidad-plan-001-2026-11-26.md` |

## Pendientes de este archivo

- La redacción para el equipo (de usted, sin jerga, sin preguntas, como condiciones de lectura) se hace
  después, con la aprobación de Jairo a este archivo.
