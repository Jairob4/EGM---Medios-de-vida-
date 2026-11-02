---
name: contrato-matriz
description: Contrato de datos con la matriz bibliográfica (xlsx) del EGM — columnas, listas, reglas de inclusión al mapa, fórmulas de conteo y casos borde. Usar al escribir specs o código que lea, valide o cuente datos de la matriz, y al crear fixtures de prueba.
---

# Contrato de datos con la matriz bibliográfica

La matriz es la **interfaz de entrada** del sistema. La herramienta la lee tal como el equipo la
diligencia; nunca la modifica ni exige cambiarla. Los valores verificados de la versión v4 están en
`references/referencia-v4.md`. Antes de usarlos, **vuelva a extraerlos del archivo en `data/raw/`**
(puede existir una versión posterior) y reporte cualquier diferencia.

## Hojas

| Hoja | Uso por la herramienta |
|---|---|
| `Matriz bibliográfica` | Fuente de verdad: una fila por documento, columnas A–Y |
| `EGM` | Solo para **verificación cruzada** de conteos; nunca como fuente |
| `Instrucciones`, `Guía por tipo de documento` | Fuente de definiciones y reglas de diligenciamiento |

## Reglas de lectura

1. Abrir en modo lectura. Identificar las columnas **por el texto del encabezado** (fila 1), no solo por
   la letra; si un encabezado esperado falta o cambia, error de contrato explícito.
2. Las listas de valores válidos (intervenciones, niveles, tipos) se leen de las **validaciones de datos**
   del archivo, no se codifican a mano. Si se agrega una intervención o dimensión, la herramienta la toma.
3. Fila vacía = columna A vacía. Una fila con solo referencia está **pendiente de codificación**.
4. Comparación de textos: exacta tras normalizar espacios en los extremos. No corregir errores de
   escritura; un valor fuera de la lista es una **advertencia** y no se cuenta (la hoja tampoco lo cuenta).

## Conjuntos y conteos (semántica de la herramienta)

Sea $R$ el conjunto de filas no vacías y

$$E = \{\, r \in R : D_r = \text{«Estudio empírico (evaluación/caso)»} \,\}.$$

Para la fila $r$, sea $I_r = \{G_r, H_r\} \setminus \{\varnothing,\ \text{No aplica}\}$ y $d_{r,j} \in \{0,1\}$
la marca de la dimensión $j$ (columnas L–S). Para la intervención $i$ y la dimensión $j$:

$$S(i,j) = \bigl|\{\, r \in E : i \in I_r,\ d_{r,j} = 1 \,\}\bigr| \quad \text{(estudios distintos)}.$$

La hoja `EGM` suma dos `COUNTIFS` (principal + secundaria):

$$T_1(i,j) = |\{r\in E : G_r=i,\ d_{r,j}=1\}| + |\{r\in E : H_r=i,\ d_{r,j}=1\}|.$$

Se cumple $T_1(i,j) = S(i,j)$ salvo filas con $G_r = H_r$, donde la hoja cuenta doble. La herramienta
cuenta **estudios distintos** y la verificación cruzada debe explicar esa diferencia, no ocultarla.

- Tabla 2 (evaluación de impacto): igual que $T_1$ con la condición adicional $J_r = \text{«Evaluación de impacto»}$.
- Tabla 4 (por nivel): $T_4(\ell) = |\{ r\in E : J_r = \ell \}|$.
- Columna «Total estudios» de la hoja: cuenta por intervención **sin** exigir dimensiones marcadas.
- Invariantes útiles para pruebas de propiedades: $T_2(i,j) \le T_1(i,j)$; $S(i,j) \le T_1(i,j)$;
  $\sum_\ell T_4(\ell) \le |E|$.

## Enfoque de género/diferencial (columna U)

Regla del equipo (hoja `Instrucciones` y nota de la hoja `EGM`): el texto empieza por **Sí**, **No** o
**Parcial**. La herramienta clasifica por ese prefijo como **palabra completa**, sin distinguir
mayúsculas («No desarrolla…» → No; «Nota:…» no es No). «Si» sin tilde no cuenta como Sí (puede ser
«Si bien…»): queda sin clasificar con advertencia. Si no hay prefijo válido, la categoría es **«Sin clasificar»**
y se muestra así. Nunca inferir la categoría a partir del resto del texto.

**Observación interna (no comunicar al equipo sin autorización de Jairo):** la tabla 3 de la hoja `EGM`
aplica el criterio `"Sí*"` sobre la columna M (Humano, valores 1/0) en lugar de la U, por lo que vale 0
en todas sus celdas. La herramienta aplica la regla documentada (prefijo de la columna U). La verificación
cruzada de la tabla 3 debe registrarse como discrepancia conocida, no como error de lectura.

## Valores calculados

El archivo puede no traer valores calculados guardados (la v4 no los trae). Leer con valores en caché
devuelve `None` en la hoja `EGM`. La verificación cruzada requiere recalcular (decisión de arquitectura:
ADR sobre verificación). Nunca tratar `None` como 0.

## Casos borde obligatorios en los fixtures

Fila solo con referencia · empírico sin intervención · empírico con intervención y sin dimensiones ·
$G_r = H_r$ · no empírico con intervención distinta de «No aplica» · dimensión con valor fuera de
$\{0,1,\varnothing\}$ · valor fuera de lista · columna U sin prefijo · más filas que el rango de las
fórmulas (2:200) · encabezado renombrado · hoja faltante · archivo sin valores en caché · nueva
intervención agregada a la lista.
