# ADR-002: Verificación cruzada con la hoja EGM cuando el archivo no trae valores calculados

**Fecha**: 2026-11-21 · **Estado**: aceptado, 2026-11-21 [Fuente: decisión de Jairo, 21-nov-2026]
**Requisitos que la motivan**: FR-001-14, FR-001-15, FR-001-16, FR-001-17, FR-001-18, FR-001-25, FR-001-26,
FR-001-27, FR-003-20, NFR-000-01, NFR-000-17

## Contexto

- El contrato §7 define qué se compara (solo las tablas comparables de total de estudios, evaluación de impacto y nivel
  de evidencia, reconocidas por el número y la frase de su título), cómo se delimita y empareja cada tabla, y el
  resultado: «coincide», «difiere» o «no verificable». La tabla 3 de la hoja no es comparable: no se lee ni se compara,
  y la herramienta no la calcula (contrato §7.7).
- El contrato §7.5 dice que un archivo **sin valores calculados** queda «no verificable», con advertencia, y que un
  valor ausente nunca es 0 (FR-001-16, FR-001-17).
- La v4 no trae valores calculados guardados: 0 celdas numéricas en la hoja EGM (apéndice A). Su verificación esperada
  es «no verificable» (US-001-3.3).
- La skill `contrato-matriz` dice que la verificación «requiere recalcular» y deja la decisión a este ADR; COR-001
  (NC-2) lo dejó abierto para aquí.
- Recalcular fórmulas exige un motor de cálculo. Las vías conocidas son LibreOffice sin interfaz (que trabaja sobre un
  archivo en disco) o una biblioteca de evaluación de fórmulas en Python.
- El archivo no se guarda en disco del servidor (NFR-000-17) y nunca se modifica (NFR-000-01).

## Opciones consideradas

| Opción | A favor | En contra |
|---|---|---|
| A. No recalcular. Comparar solo valores numéricos guardados; sin ellos, «no verificable» con advertencia | Es exactamente el contrato §7.5 y US-001-3.3. Sin disco, sin dependencias nativas. Determinista | Con la v4, la verificación nunca compara nada dentro de la herramienta |
| B. Recalcular con LibreOffice sin interfaz | Daría valores para comparar | Escribe una copia en disco: viola NFR-000-17. Dependencia externa pesada. Cambiaría el resultado esperado de US-001-3.3, que el spec fija como «no verificable» |
| C. Recalcular en memoria con una biblioteca de evaluación de fórmulas | Sin disco | Cobertura incompleta de funciones; un fallo del motor se confundiría con una diferencia; también contradice US-001-3.3. Sería una ampliación de alcance |
| D. Emular la semántica de la hoja con los conteos de la herramienta ($T_1$, $T_2$, $t$, $t^{IE}$) y presentarla como «valores de la hoja» | Sin disco | No es verificación: compara la herramienta consigo misma. Engañaría al equipo |

## Decisión

**Opción A.** La herramienta no recalcula fórmulas. El «recálculo» que pide la skill queda como **control del proceso
del proyecto**, fuera de la herramienta: para producir esperados de prueba, Jairo o el `implementador` recalculan una
copia en su propio equipo (como se hizo con la v4, estado §3) y el constructor de fixtures (M23) escribe matrices
sintéticas con valores guardados controlados. Esto cierra COR-001 NC-2 sin cambiar el contrato.

Reglas de implementación en `egm.verificacion` (M08), dentro del contrato §7:

1. **Valor comparable.** Solo un valor numérico guardado en la celda (el valor en caché de una fórmula o un número
   escrito). `None`, texto o error se tratan como valor ausente (contrato §7.9), nunca como 0.
2. **Filas que abarcan las fórmulas** (contrato §7.3). Para cada celda con fórmula se toman las filas de la hoja de la
   matriz a las que remiten sus rangos; si varios rangos de la misma fórmula difieren, la intersección. Una celda con
   número escrito y sin fórmula se compara sobre todas las filas leídas. El conteo de la herramienta para esa celda se
   calcula sobre ese mismo conjunto de filas (los invariantes del contrato §5 exigen no mezclar conjuntos). Si alguna
   fórmula abarca menos filas que las leídas, se emite la advertencia de US-001-1.5. Esta regla interpreta el contrato
   §7.3 para celdas sin fórmula y para rangos distintos; aprobada tal como está [Fuente: decisión de Jairo,
   21-nov-2026].
3. **Explicación de diferencias** (contrato §7.4), en este orden y de forma acumulativa, comparando el valor de la hoja
   con variantes de la semántica de la hoja calculadas sobre las mismas filas:
   1. si el valor es igual a $T_1$ (o $T_2$, $t$, $t^{IE}$), se explica por las filas con $G_r = H_r$, que se listan;
   2. si persiste y es igual a esa semántica contando además el texto «1» como marca, se explica por las filas con la
      dimensión escrita como texto, que se listan;
   3. si persiste y es igual a esa semántica sin quitar espacios en los extremos, se explica por las filas con espacios,
      que se listan;
   4. si no, diferencia sin explicar.
4. **Resultado por tabla** según el contrato §7.9 ($D_k$, $V_k$). La lista «tablas verificadas» contiene los números de
   título de las tablas en «coincide» o «difiere» (FR-001-25).
5. **Orden de presentación.** Las advertencias de verificación van antes de los resultados (FR-001-18): `egm.procesamiento`
   las coloca primero y `app.presentacion` las dibuja antes del mapa y del tablero.
6. **Nada sobre la tabla 3.** El módulo no la localiza, no la lee y no produce advertencias ni registros sobre ella.

## Consecuencias

- Positivas:
  - Cumple el contrato tal como está; ningún archivo toca el disco; sin dependencias nativas.
  - La verificación es determinista y se prueba entera con matrices sintéticas.
- Negativas / deuda aceptada:
  - Con matrices sin valores guardados, como la v4, la herramienta informa «no verificable». La razón queda dicha en
    lenguaje llano (US-001-3.3, US-003-4.4).
  - Si en el futuro se quisiera verificar archivos sin valores guardados, haría falta una corrección del spec y una
    opción B o C. No se propone ahora.
- Requisitos afectados y cómo se verifican:
  - FR-001-14 a FR-001-18, FR-001-25 a FR-001-27: US-001-3.1 a US-001-3.17 con fixtures del constructor (M23) que
    escriben fórmulas con su valor guardado, solo números, o nada.
  - FR-001-17: prueba de propiedad: ninguna celda ausente produce «coincide» ni se compara como 0 (US-001-3.13).
  - FR-003-20: US-003-4.4 y US-003-4.5.
  - NFR-000-17: la verificación no abre archivos ni procesos externos (prueba de que el módulo no usa el sistema de
    archivos).
