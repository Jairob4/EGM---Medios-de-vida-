# ADR-001: Fuente de verdad del mapa y semántica de conteo

**Fecha**: 2026-11-21 · **Estado**: aceptado, 2026-11-21 [Fuente: decisión de Jairo, 21-nov-2026]
**Requisitos que la motivan**: NFR-000-01, NFR-000-02, NFR-000-06, NFR-000-09, FR-001-01, FR-001-05, FR-001-06,
FR-001-07, FR-001-08, FR-001-09, FR-001-11, FR-001-13, FR-002-01, FR-002-03, FR-003-18, SC-001-01, SC-001-03,
SC-002-01, SC-003-01

## Contexto

- La hoja «Matriz bibliográfica» es la fuente de verdad: una fila por documento (contrato §2). La hoja EGM solo sirve
  para verificar y nunca es fuente (contrato §2 y §7; decisión de Jairo, 1-nov-2026).
- El contrato §5 define la semántica: $E$, $M$, $P$, $I_r = \{G_r, H_r\} \cap \mathcal{I}$, $J_r$, y el conteo de la
  herramienta en **estudios distintos**
  $S(i,j) = \bigl|\{ r \in E : i \in I_r,\ j \in J_r \}\bigr|$. La hoja suma principal y secundaria ($T_1$) y cuenta
  doble las filas con $G_r = H_r$.
- Todo número debe descomponerse en su lista de N.º (NFR-000-02, FR-001-11) y la lista debe reproducir el número
  (SC-002-01, SC-003-01).
- Categorías desde el archivo, sin cambios de código (NFR-000-06); listas desde las validaciones (FR-001-05); todas las
  filas (FR-001-06); orden del archivo (contrato §4 regla 3).
- Hecho técnico: la biblioteca habitual de Python para `.xlsx` (`openpyxl`) no expone las validaciones de datos en su
  modo de solo lectura en flujo, y descarta con un aviso las validaciones guardadas como extensión del formato (el tipo
  que Excel usa a veces para listas que remiten a otra hoja).
- Evidencia sobre la v4 (21-nov-2026): la sesión principal abrió la v4 en modo lectura (huella SHA-256 sin cambios). La
  hoja «Matriz bibliográfica» tiene 7 validaciones de datos estándar y 0 validaciones de extensión
  (`x14:dataValidation`). `openpyxl.load_workbook` las lee todas, sin advertencias: D2:D36, F2:F36, G2:G36, H2:H36,
  I2:I36 y J2:J36 de tipo lista, y L2:S36 con la lista «1,0». Las demás hojas no tienen validaciones.

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| A. Conteo desde las filas, con el número **derivado** de una lista de filas (`Conteo.filas`, `valor = len(filas)`) | La trazabilidad es imposible de romper: no existe un número sin su lista. SC-002-01 y SC-003-01 se cumplen por construcción. Un solo cálculo sirve a mapa, tablero y exportación | Algo más de memoria que guardar enteros (irrelevante con cientos de filas) |
| B. Conteo desde las filas como enteros, y listas calculadas aparte para el detalle | Sencillo | Dos cálculos que pueden divergir; SC-002-01 dependería de pruebas, no del diseño |
| C. Leer los conteos de la hoja EGM | Ninguno | Prohibido por el contrato (la hoja nunca es fuente); la v4 no trae valores guardados; cuenta doble $G_r = H_r$ |
| D. Contar con la semántica de la hoja ($T_1$) para coincidir con ella | Coincide con la hoja | Contradice FR-001-08 y FR-001-09 (estudios distintos) |

Para leer las validaciones:

| Opción | A favor | En contra |
|---|---|---|
| L1. `openpyxl` en modo normal, desde bytes en memoria, sin guardar nunca | Lee validaciones estándar con su rango; valores guardados y fórmulas disponibles | Puede descartar validaciones de extensión |
| L2. L1 más lectura directa del XML de la hoja dentro del paquete (en memoria) para las validaciones de extensión | Cubre ambos tipos | Un lector pequeño adicional, con pruebas propias |
| L3. Lector propio completo del XML | Control total | Más trabajo; reinventa lo que la biblioteca ya hace |

## Decisión

**Opción A con lector L2.**

1. **Fuente.** Solo las filas de la hoja «Matriz bibliográfica». Ningún conteo se toma de la hoja EGM.
2. **Unidad de trazabilidad.** `RefFila(numero, fila)`: el N.º tal como está y el número de fila del archivo, porque el
   N.º puede faltar o repetirse (contrato §9).
3. **Número = lista.** Todo conteo es un `Conteo` con sus filas en el orden del archivo y sin repetidos; su valor es la
   longitud. Las cifras del tablero, las celdas del mapa, el desglose por nivel y las conclusiones se construyen así.
4. **Semántica.** Estudios distintos según el contrato §5: $S$, $S^{IE}$, $S_\varphi$, $u$, $u^{IE}$, $T_4$, con $M$
   como regla de inclusión (FR-001-07), incluida la fila con solo la secundaria. El número de estudios del mapa es
   $|\{r \in M : \varphi(r)\}|$, nunca una suma de celdas (FR-001-09). El desglose de una celda por nivel reparte sus
   estudios en una sola entrada cada uno (un estudio tiene un nivel, o «Sin nivel»), de modo que la suma del desglose
   es $S(i,j)$.
5. **Semántica de la hoja aparte.** $T_1$, $T_2$, $t$, $t^{IE}$ se calculan solo dentro de `egm.conteo.semantica_hoja`
   y solo los usa `egm.verificacion` para explicar diferencias (ADR-002). Nunca se muestran como conteo.
6. **Lectura.** `egm.libro` abre los bytes en memoria con L1 y, si el paquete contiene validaciones de extensión, las
   lee del XML (L2). Nunca guarda ni escribe (NFR-000-01). Con la v4, L1 basta (ver Contexto); L2 se mantiene como
   respaldo para versiones futuras en las que alguna validación llegue como extensión `x14`.
7. **Determinismo.** Categorías como tuplas en el orden del archivo; ningún resultado itera un conjunto sin orden; la
   fecha de lectura entra como parámetro (NFR-000-09).

## Consecuencias

- Positivas:
  - SC-002-01, SC-003-01 y SC-000-02 se cumplen por diseño y se comprueban con una propiedad simple
    ($valor = |filas|$ en todos los números de todas las vistas).
  - Los invariantes del contrato §5 se prueban sobre `Conteo` con matrices al azar (SC-001-03).
  - Mapa, tablero y exportación comparten un solo cálculo (SC-002-05).
- Negativas / deuda aceptada:
  - Los conteos se recalculan por petición; con matrices de este proyecto el costo es despreciable. Si la matriz
    creciera a miles de filas, se puede guardar el cálculo por (sesión, filtro) sin cambiar la interfaz.
  - **Riesgo de las validaciones de extensión**: descartado para la v4 por la comprobación del 21-nov-2026 (7
    validaciones estándar, 0 `x14:dataValidation`, todas leídas por `openpyxl.load_workbook` sin advertencias). Para
    versiones futuras se mantiene L2 como respaldo: si el paquete trae validaciones `x14`, se leen del XML de la hoja.
    El plan 001 incluye fixtures del constructor (M23) con validaciones de extensión para probar ese respaldo.
- Requisitos afectados y cómo se verifican:
  - NFR-000-02, FR-001-11: propiedad «toda cifra es la longitud de su lista» (SC-000-02, SC-002-01, SC-003-01).
  - FR-001-07 a FR-001-09: US-001-1.1, US-001-1.2, US-001-1.10 y SC-001-01 con el apéndice A.
  - NFR-000-06, FR-001-05: SC-000-06 con tres matrices sintéticas del constructor (M23).
  - NFR-000-01: SC-000-01 (huella antes y después) y prueba de que `egm.libro` no expone ninguna operación de escritura.
  - NFR-000-09: SC-000-09 (dos lecturas con la misma fecha inyectada dan salidas idénticas).
