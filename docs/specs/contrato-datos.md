# Contrato de datos con la matriz bibliográfica

**Created**: 2026-11-01  
**Estado**: v0 — propuesta, alcance por acordar

## 1. Propósito y principio rector

La matriz es la **interfaz de entrada** del sistema. La herramienta la lee tal como el equipo la
diligencia; nunca la modifica ni exige cambiarla. `[Fuente: doc. general §4]`

El contrato vale para **cualquier versión de la matriz del estado del arte de este proyecto**: ya pasó de
v3 a v4 y puede actualizarse otra vez. Por escalabilidad, define **roles y reglas de descubrimiento**, no
una lista fija de categorías, filas o columnas. La herramienta no compara una matriz con otra versión ni
guarda valores de referencia. Las matrices de otros proyectos quedan fuera de alcance.
`[Fuente: decisión de Jairo, 1-nov-2026]`

El apéndice A describe la v4 solo como **instancia de ejemplo verificada**, para pruebas y fixtures. No es
parte de la definición.

## 2. Hojas

| Hoja | Rol | Si falta |
|---|---|---|
| `Matriz bibliográfica` | Fuente de verdad: una fila por documento | Error de contrato |
| `EGM` | Solo verificación cruzada; nunca es fuente | Verificación «no verificable» con advertencia; nunca error de contrato |
| `Instrucciones`, `Guía por tipo de documento` | Definiciones y reglas de diligenciamiento, para consulta del mantenedor | Sin efecto en el procesamiento |

### 2.1 Carga del archivo

La matriz llega por carga desde el navegador y vive solo durante la sesión. Antes de leerla, la herramienta
comprueba su tipo y su tamaño: debe ser un libro de hoja de cálculo `.xlsx`, comprobado por su contenido y no solo
por su extensión, y no superar el límite de tamaño de `000-vision-alcance.md`. Si no cumple, lo rechaza con un
mensaje legible y sin resultados parciales. El archivo cargado nunca se modifica.
`[Fuente: decisión de Jairo, 2-nov-2026]`

## 3. Roles de columna

Las columnas se identifican por el **texto del encabezado** en la fila 1, nunca por su letra. Faltar un
encabezado de esta tabla es un **error de contrato**: la herramienta se detiene y dice cuál falta. Renombrar
un encabezado equivale a que falte. `[Fuente: doc. técnico §5.1]`

| Rol | Encabezado | Símbolo | Uso |
|---|---|---|---|
| Identificador | `N°` | $A_r$ | Trazabilidad |
| Referencia | `Referencia APA` | $B_r$ | Detalle; enlace si contiene DOI o URL |
| Año | `Año` | $C_r$ | Filtro y composición |
| Tipo de documento | `Tipo de documento` | $D_r$ | Inclusión al mapa y composición |
| País y población | `País y población` | $E'_r$ | Solo se muestra |
| Tipo de fuente | `Tipo de fuente` | $F_r$ | Filtro y composición |
| Intervención principal | `Tipo de intervención (EGM)` | $G_r$ | Filas del mapa |
| Intervención secundaria | `Intervención secundaria (opcional)` | $H_r$ | Filas del mapa |
| Metodología | `Metodología` | $M'_r$ | Filtro y composición |
| Nivel de evidencia | `Nivel de evidencia` | $L_r$ | Color, filtro y conteos |
| Delimitador inicial | `Dimensiones evaluadas / propuestas` | — | Inicia el bloque; solo se muestra |
| Delimitador final | `Indicadores o categorías analíticas` | $T_r$ | Cierra el bloque; indicadores |
| Enfoque diferencial | `Enfoque de género/diferencial` | $U_r$ | Clasificación por prefijo |
| Hallazgos | `Principales hallazgos / tesis central` | $V_r$ | Solo se muestra |
| Vacío | `Vacío de conocimiento identificado` | $W_r$ | Listado por celda |
| Limitaciones | `Limitaciones` | $X_r$ | Listado por celda |
| Aporte | `Aporte al proyecto` | $Y_r$ | Solo se muestra |

Una columna de otro encabezado, fuera del bloque de dimensiones, se ignora y se informa en una **nota
informativa** («columnas no usadas: …»), que no es una advertencia. Solo es advertencia si tiene lista `1,0`
(sección 3.1). `[Fuente: decisión de Jairo, 2-nov-2026]`

### 3.1 Bloque de dimensiones

Las dimensiones son las columnas situadas **entre** «Dimensiones evaluadas / propuestas» e «Indicadores o
categorías analíticas», ambos excluidos, en el orden del archivo. Su nombre es el texto de su encabezado.
`[Fuente: decisión de Jairo, 1-nov-2026]`

- Columna del bloque sin lista `1,0`, o columna con lista `1,0` fuera del bloque: **advertencia**, nunca
  error.
- Falta alguno de los dos encabezados que delimitan el bloque: **error de contrato**.

## 4. Reglas de lectura

1. Abrir siempre en modo lectura; el archivo original nunca se escribe. `[Fuente: doc. técnico §4.2 RNF1]`
2. Las listas de valores válidos se leen de las **validaciones de datos** del archivo, sean listas escritas
   en la validación o referencias a un rango. No se codifican a mano. `[Fuente: doc. técnico §12.2]`
3. **Orden del archivo.** Las dimensiones van en el orden de sus columnas. Las intervenciones y los niveles van
   en el orden de su lista de validación; las intervenciones que solo estén en la lista de secundaria van al
   final, en su orden. `[Fuente: decisión de Jairo, 3-nov-2026. El doc. técnico §2.4 usa el orden de la
   hoja EGM, pero esa hoja nunca es fuente y puede faltar. En la v4 ambos órdenes coinciden.]`
4. **Fila vacía:** todas sus celdas están vacías. `[Fuente: decisión de Jairo, 2-nov-2026]` Fila con `N°` vacío pero con contenido: se procesa con
   advertencia y se identifica por su número de fila del archivo. `[Fuente: doc. técnico §9.2]`
5. Se leen **todas** las filas, sin límite fijo.
6. Comparación de textos: exacta tras quitar espacios en los extremos. Si hubo que quitarlos, advertencia,
   porque la hoja `EGM` podría no contar ese valor. No se corrigen errores de escritura.
   `[Fuente: doc. técnico §9.2]`
7. Un valor fuera de su lista es una **advertencia** con `N°`, columna y valor, y no se cuenta. Se comprueba
   en todas las filas, también en las que no tengan validación. `[Fuente: doc. técnico §3.1, §9.2]`
8. **Valores «No aplica»:** cualquier valor de lista que empiece por `No aplica` no es una categoría. No
   genera fila de mapa ni nivel. La comparación es por prefijo porque el texto real incluye un paréntesis.
   `[Fuente: Matriz Instrucciones B9, B11]`
9. Una celda vacía nunca equivale a 0. En el mapa ambas dan «no marcada», pero en las advertencias vacía es «sin
   diligenciar» y 0 es «no evaluada». `[Fuente: doc. técnico §6.12, §9.2]`
10. Un valor en la columna de una dimensión distinto de 1 numérico, 0 numérico o vacío (incluido el texto
    `"1"`) es advertencia `[Fuente: doc. técnico §9.2]` y no marca la dimensión. `[Fuente: decisión de Jairo, 2-nov-2026.
    §9.2 pide documentar el tratamiento y contrastarlo con la hoja, sin fijarlo. Se elige no marcar
    porque la herramienta no corrige valores; el contraste queda en la sección 7.]`
11. Guiones, `N/A` y marcadores en texto libre son contenido: se muestran tal cual.
    `[Fuente: doc. técnico §9.2]`
12. **Año no reconocido.** Un valor de `Año` que no sea un número entero (incluido un año escrito como texto) es
    advertencia con `N°`, columna y valor. El documento se cuenta en $R$, no cumple un filtro de año activo y en la
    composición por año aparece como «año no reconocido», separado de «sin diligenciar». `[Fuente: decisión de Jairo, 3-nov-2026.
    El doc. técnico §6.9 solo trata la celda vacía.]`

**Estado de cada documento.** Todo documento de $R$ queda en uno solo de estos estados, derivados de los conjuntos
de la sección 5 `[Fuente: Matriz Instrucciones B20, para «En el mapa»; doc. técnico §9.2, para «Empírico pendiente»; decisión de Jairo, 2-nov-2026, para los otros dos estados]`:

| Estado | Condición | Trato |
|---|---|---|
| En el mapa | $r \in M$ | Se cuenta en sus celdas |
| Empírico pendiente | $r \in P$ | Se lista como pendiente |
| No empírico | Tipo de documento no vacío, distinto de $v_{\text{emp}}$ y, si la columna tiene lista, dentro de ella | No se espera en el mapa: no se lista como empírico pendiente ni genera advertencia por esa razón, aunque solo tenga N.º, referencia, año y tipo |
| Sin tipo de documento válido | Tipo de documento vacío o, si la columna tiene lista, fuera de ella | Se cuenta en $R$; incluye la fila solo con referencia, que no tiene tipo de documento |

Si la columna de tipo de documento no tiene lista (sección 4.2), no hay lista contra la cual comprobar sus valores: todo valor no vacío distinto de $v_{\text{emp}}$ se toma como no empírico, y una celda con solo espacios cuenta como vacía. La advertencia de esa columna indica los valores presentes, para que una variante de escritura sea visible. La herramienta no la corrige. `[Fuente: decisión de Jairo, 2-nov-2026]`

Estos estados indican la relación de cada documento con el mapa. No miden cuánto falta por leer o codificar: un documento no empírico con pocos datos sigue siendo no empírico, y «Sin tipo de documento válido» solo describe esa columna. La herramienta no calcula avance por fila (`000-vision-alcance.md`, «Fuera de alcance»). La skill `contrato-matriz` llama «pendiente de codificación» a la fila solo con referencia; prevalece el nombre de esta tabla, porque esa expresión se confunde con las referencias que el equipo tiene por leer. `[Fuente: decisión de Jairo, 2-nov-2026]`

### 4.1 Valores ancla

Tres reglas dependen del significado de un valor concreto:

| Ancla | Valor | Se usa en |
|---|---|---|
| Estudio empírico | El valor de la lista de tipo de documento que empieza por `Estudio empírico` | Conjunto $E$ |
| Evaluación de impacto | El valor de la lista de nivel igual a `Evaluación de impacto` | $S^{IE}$, conclusión 2 |
| Prefijo no aplicable | `No aplica` | Regla 8 |

Se espera que estos valores no cambien. Si una versión los renombra `[Fuente: decisión de Jairo, 2-nov-2026]`:

- Sin ancla de estudio empírico: **error de contrato** que nombra el valor esperado y los encontrados, porque el
  mapa no se puede construir.
- Sin ancla de evaluación de impacto: **advertencia**. La conclusión 2 queda «no disponible», $S^{IE}$ no se
  calcula y la tabla comparable de evaluación de impacto queda «no verificable».

El ancla se busca en la lista de la columna o, si esa columna no tiene lista (sección 4.2), en sus valores
presentes.

### 4.2 Columnas categóricas sin lista de validación

| Columna sin lista | Tratamiento |
|---|---|
| Intervención principal, intervención secundaria o nivel de evidencia | Error de contrato que nombra la columna |
| Tipo de documento, tipo de fuente o metodología | Advertencia; los filtros y la composición usan los valores presentes, y no se comprueban valores fuera de lista |

`[Fuente: decisión de Jairo, 2-nov-2026]`

## 5. Definiciones formales

Sea $R$ el conjunto de filas no vacías (documentos). Sean $\mathcal{I}$ las intervenciones (valores de las
listas de principal y secundaria, sin «No aplica»), $\mathcal{J}$ las dimensiones del bloque y
$\mathcal{L}$ los niveles de evidencia (valores de la lista, sin «No aplica»). Todos se leen del archivo.

Estudios empíricos registrados:

$$E = \{\, r \in R : D_r = v_{\text{emp}} \,\}.$$

Para la fila $r$:

$$I_r = \{G_r, H_r\} \cap \mathcal{I}, \qquad J_r = \{\, j \in \mathcal{J} : d_{r,j} = 1 \,\},$$

donde $d_{r,j}$ es la marca de la dimensión $j$. La regla de inclusión es la del equipo: tipo de documento
empírico, intervención diligenciada y al menos una dimensión en 1 `[Fuente: Matriz Instrucciones B20]`:

$$M = \{\, r \in E : I_r \neq \varnothing,\ J_r \neq \varnothing \,\}, \qquad N = |M|, \qquad P = E \setminus M.$$

$P$ son los estudios empíricos que aún no entran al mapa.

Una fila de $E$ con la intervención principal vacía y la secundaria diligenciada está en $M$ por su secundaria, si tiene al menos una dimensión en 1, y no genera advertencia por esa razón. La regla sigue la fórmula de la hoja `EGM`, que cuenta esa fila por la columna de la secundaria (segundo sumando de $T_1$); la hoja sigue siendo solo verificación y nunca fuente de datos. Instrucciones B20 dice «Tipo de intervención diligenciado»; la herramienta lo trata distinto, porque le basta la secundaria. `[Fuente: decisión de Jairo, 3-nov-2026]`

**Conteo de la herramienta (estudios distintos):**

$$S(i,j) = \bigl|\{\, r \in E : i \in I_r,\ j \in J_r \,\}\bigr|.$$

Restringido a evaluaciones de impacto:

$$S^{IE}(i,j) = \bigl|\{\, r \in E : i \in I_r,\ j \in J_r,\ L_r = v_{\text{IE}} \,\}\bigr|.$$

**Semántica de la hoja `EGM`** (suma dos conteos, principal y secundaria), usada solo para comparar:

$$T_1(i,j) = |\{r\in E : G_r=i,\ d_{r,j}=1\}| + |\{r\in E : H_r=i,\ d_{r,j}=1\}|.$$

$$T_2(i,j) = |\{r\in E : G_r=i,\ d_{r,j}=1,\ L_r=v_{\text{IE}}\}| + |\{r\in E : H_r=i,\ d_{r,j}=1,\ L_r=v_{\text{IE}}\}|.$$

$$T_4(\ell) = |\{\, r\in E : L_r = \ell \,\}|, \quad \ell \in \mathcal{L}.$$

Columna «Total estudios», que no exige dimensiones marcadas:

$$t(i) = |\{r\in E : G_r=i\}| + |\{r\in E : H_r=i\}|.$$

$$t^{IE}(i) = |\{r\in E : G_r=i,\ L_r=v_{\text{IE}}\}| + |\{r\in E : H_r=i,\ L_r=v_{\text{IE}}\}|.$$

Sus equivalentes en estudios distintos, que son los de la herramienta:

$$u(i) = |\{r\in E : i \in I_r\}|, \qquad u^{IE}(i) = |\{r\in E : i \in I_r,\ L_r=v_{\text{IE}}\}|.$$

Se cumple $T_1(i,j) = S(i,j)$ salvo en filas con $G_r = H_r$, donde la hoja cuenta doble. La herramienta cuenta
**estudios distintos** y la verificación explica esa diferencia, no la oculta.

**Filtros.** Un filtro es un predicado sobre las filas. Dentro de un filtro de lista, una fila lo cumple si su
valor es uno de los seleccionados; en el de año, si su año está en el rango. Una celda vacía no cumple un filtro activo, y el estudio no aparece; la única excepción es la entrada «Sin nivel» del filtro de nivel de evidencia (FR-002-12). Un filtro está **activo** cuando se aplica con el botón «Actualizar vista»; mover un control no lo activa. `[Fuente: decisión de Jairo, 2-nov-2026; decisión de Jairo, 3-nov-2026, para la excepción de «Sin nivel». Doc. técnico §2.4 y §4.1 RF2 definen el vector y el producto, no estas reglas.]` `[NEEDS CLARIFICATION: no está decidido si un filtro aplicado sin dejar fuera ningún valor de su lista, o con el rango completo de años, cuenta como activo. Si cuenta, deja fuera los estudios con la celda vacía en ese campo. Opciones: (a) cuenta como activo; (b) solo cuenta si deja fuera algún valor o estrecha el rango de años. Pendiente de Jairo; no se aplica.]` Varios
filtros se combinan por conjunción en $\varphi$:

$$S_\varphi(i,j) = \bigl|\{\, r \in E : \varphi(r),\ i \in I_r,\ j \in J_r \,\}\bigr|.$$

En «n de N», $N$ es el total sin filtrar del elemento que se cuenta y $n$ el total con $\varphi$: para estudios
del mapa, $n = |\{r \in M : \varphi(r)\}|$ y $N = |M|$; para documentos, lo mismo sobre $R$.

`[Fuente: doc. técnico §2.4, §4.1 RF2]`

**Invariantes para pruebas de propiedades**, calculados sobre el mismo conjunto de filas: todas las filas leídas,
o solo las que abarcan las fórmulas de la hoja cuando se comparan con ella (sección 7), nunca una mezcla de ambas:

- $T_2(i,j) \le T_1(i,j)$, $\quad S(i,j) \le T_1(i,j)$, $\quad S^{IE}(i,j) \le S(i,j)$.
- $S_\varphi(i,j) \le S(i,j)$.
- $\sum_{\ell} T_4(\ell) \le |E|$.
- $\sum_{i,j} S(i,j) = \sum_{r \in M} |I_r|\,|J_r| \ge N$: la suma de celdas no es el número de estudios.
- $\sum_{\kappa} S_\kappa(i,j) = S(i,j)$, con $\kappa$ en las categorías de la sección 6.

## 6. Enfoque de género/diferencial

El equipo pide que el texto empiece por «Sí / No / Parcial» más una frase. `[Fuente: Matriz Instrucciones B14]`
La herramienta clasifica cada fila así:

| Condición | Categoría $\gamma(r)$ |
|---|---|
| Celda vacía o solo espacios | Sin diligenciar |
| Primera palabra completa, sin distinguir mayúsculas, igual a `Sí` | Sí |
| Primera palabra completa igual a `No` | No |
| Primera palabra completa igual a `Parcial` | Parcial |
| `Si` sin tilde («Si bien…») | Sin clasificar, con advertencia |
| Cualquier otro comienzo («Nota:…», «El estudio…») | Sin clasificar, con advertencia |

Nunca se infiere la categoría a partir del resto del texto, y el texto completo se muestra junto a la
categoría. `[Fuente: doc. técnico §6.6]` La advertencia cita la regla de la hoja Instrucciones (B14) y no agrega
nada más. `[Fuente: decisión de Jairo, 2-nov-2026]`

El trato de `Si` sin tilde viene de la skill `contrato-matriz` y se aparta del doc. técnico §6.6, que quita las
tildes y lo clasificaría como Sí. Prevalece la skill: «Si bien…» no es una afirmación.

$$S_\kappa(i,j) = \bigl|\{\, r \in E : i \in I_r,\ j \in J_r,\ \gamma(r)=\kappa \,\}\bigr|.$$

## 7. Verificación cruzada con la hoja `EGM`

Se aplica solo cuando la hoja se reconoce. `[Fuente: decisión de Jairo, 1-nov-2026]`

1. Las tablas se localizan **por su título** y las filas **por su nombre**, sin coordenadas fijas.
2. Una tabla comparable se reconoce por una celda que empieza por un número seguido de punto y cuyo texto
   restante, sin distinguir mayúsculas, contiene su frase propia. Exigir el número evita confundir el título con
   un encabezado o un nombre de fila que repita la frase. Las filas y columnas se emparejan como indican los
   puntos 7 y 8. Si ninguna celda cumple la condición, o la cumple más de una, la tabla no se reconoce. `[Fuente: decisión de Jairo, 2-nov-2026]`

   | Tabla comparable | Frase del título | Conteos de la herramienta | Semántica de la hoja |
   |---|---|---|---|
   | Total de estudios | `Número total de estudios` | $S$, $u$ | $T_1$, $t$ |
   | Evaluación de impacto | `Evaluación de impacto` | $S^{IE}$, $u^{IE}$ | $T_2$, $t^{IE}$ |
   | Por nivel de evidencia | `nivel de evidencia` | $T_4$ | $T_4$ |

3. Cada valor calculado guardado en la hoja se compara con el **conteo de la herramienta**, sobre las filas que
   abarcan las fórmulas de la hoja.
4. Resultado de cada tabla, según el punto 9: **coincide**; **difiere**, con las celdas y su explicación; o **no verificable**, con
   advertencia. Si la hoja difiere de la herramienta y coincide con su semántica, la diferencia se explica por las filas
   con $G_r = H_r$, que se listan. Si persiste y hay filas con la dimensión escrita como texto (regla 10), se
   explica por ellas, que también se listan. `[Fuente: decisión de Jairo, 2-nov-2026. Depende de la regla 10 y la comprueba US-001-3.8.]` Si no, se informa como diferencia sin explicar.
5. Son «no verificable»: hoja ausente, tabla no reconocida, archivo sin valores calculados o una comparación incompleta sin diferencias (punto 9). Nunca producen
   error de contrato. Un valor calculado ausente nunca se trata como 0.
6. La interfaz informa solo las tablas comparables de esta sección, cada una por el número inicial de su título.
   Una tabla entra en la lista si quedó en «coincide» o «difiere»: en una matriz como la v4 con valores
   calculados, «tablas verificadas: 1, 2 y 4». Si ninguna se pudo comparar, se muestra «no verificable», sin lista.
   `[Fuente: decisión de Jairo, 2-nov-2026]`
7. **Alcance de una tabla comparable.** La columna de nombres es la del título. La fila de encabezados es la
   primera fila con contenido debajo del título. El cuerpo empieza en la fila siguiente y termina antes de la
   primera fila cuya celda en la columna de nombres esté vacía o empiece por un número seguido de punto, o donde
   termine la hoja. Cada tabla se lee solo dentro de su alcance, de modo que un nombre repetido en otra tabla no
   interfiere. Las tablas que no sean comparables no se leen ni generan advertencias.
   `[Fuente: decisión de Jairo, 2-nov-2026]`
8. **Emparejamiento.** Los nombres se comparan de forma exacta tras quitar espacios en los extremos.
   - En las tablas de total y de evaluación de impacto, las filas se emparejan con $\mathcal{I}$ y las columnas
     con $\mathcal{J}$. La columna cuyo encabezado sea `Total estudios`, tras quitar espacios en los extremos y
     sin distinguir mayúsculas, se compara con $u$ o $u^{IE}$. Si una dimensión se llama igual, prevalece la
     dimensión.
   - En la tabla por nivel, las filas se emparejan con $\mathcal{L}$, y sus valores están en la única columna con
     encabezado además de la de nombres. Si hay más de una o ninguna, esos valores quedan sin pareja.
   - Queda sin pareja: una categoría de la matriz que no esté en la tabla; una fila o columna de la tabla que no
     sea una categoría ni `Total estudios`; `Total estudios` si falta o se repite en las tablas donde se espera;
     y todo nombre repetido dentro del alcance.

   `[Fuente: decisión de Jairo, 2-nov-2026]`
9. **Resultado de una tabla.** Sea $D_k$ el conjunto de comparaciones que la tabla $k$ debería permitir: una por
   cada par de fila y columna, contando las categorías de la matriz y también las filas y columnas de la tabla
   que queden sin pareja. Sea $V_k \subseteq D_k$ el de las que tienen pareja en ambos lados y un valor numérico
   guardado. Cualquier otro contenido se trata como valor ausente.
   - **Difiere:** algún valor de $V_k$ es distinto del conteo de la herramienta.
   - **Coincide:** ninguno difiere y $V_k = D_k \neq \varnothing$.
   - **No verificable:** ninguno difiere y $V_k \neq D_k$, incluido $V_k = \varnothing$.

   Si $V_k \neq D_k$, una advertencia indica la tabla, los nombres sin pareja y cuántos valores faltaron, también
   cuando el resultado sea «difiere». La advertencia informa y no pide cambios en la matriz ni en la hoja. Lo que
   no se compara nunca se trata como 0. Los casos del punto 5 que impiden comparar la tabla, y la falta del ancla
   de evaluación de impacto (sección 4.1), dan «no verificable» sin aplicar este punto.
   `[Fuente: decisión de Jairo, 2-nov-2026]`

## 8. Porcentajes

Esta versión muestra **solo conteos**. La capacidad de porcentajes queda inactiva por defecto, con un
interruptor configurable, apagado, y $n_{min} = 100$ configurable. El umbral se evalúa sobre el denominador de
cada porcentaje. El criterio es que el semiancho del intervalo del 95 % en el peor caso ($p = 0.5$) no supere
$0.10$:

$$1.96\sqrt{\frac{0.25}{100}} \approx 0.098 \le 0.10.$$

`[Fuente: decisión de Jairo, 1-nov-2026]`

## 9. Casos borde

| Caso | Tratamiento |
|---|---|
| Fila solo con referencia | Sin tipo de documento válido; se cuenta en $R$, no en $M$ |
| Empírico sin intervención | En $E$, no en $M$; se lista como pendiente |
| Empírico con intervención y sin dimensiones | En $E$, no en $M$; la columna «Total estudios» de la hoja sí lo cuenta |
| Empírico con la intervención principal vacía y la secundaria diligenciada | En $M$ por su secundaria si tiene al menos una dimensión en 1; sin advertencia por esa razón |
| Estudio del mapa sin nivel de evidencia o con un nivel que empieza por `No aplica` | Se muestra como «Sin nivel», con entrada propia en la leyenda; con el filtro de nivel activo, solo sale al ocultar esa entrada (FR-002-12). Provisional |
| $G_r = H_r$ | Advertencia; la herramienta lo cuenta una vez y la hoja dos |
| No empírico con intervención distinta de «No aplica» | No entra en $E$; advertencia |
| Dimensión con valor fuera de $\{0, 1, \varnothing\}$ | Advertencia; no marca la dimensión |
| Valor fuera de lista | Advertencia; no se cuenta |
| Columna de enfoque sin prefijo válido | Sin clasificar, con advertencia que cita Instrucciones B14 |
| Más filas que el rango de las fórmulas de la hoja | Se leen todas; advertencia; la comparación usa solo ese rango |
| `N°` vacío con contenido, o `N°` repetido | Advertencia; la trazabilidad usa también el número de fila |
| Encabezado de rol renombrado o ausente | Error de contrato |
| Hoja de la matriz faltante | Error de contrato |
| Archivo de otro tipo, dañado o mayor que el límite | Se rechaza antes de leerlo; sin resultados parciales |
| Columna de otro encabezado fuera del bloque, sin lista `1,0` | Se ignora; nota informativa «columnas no usadas: …» |
| Columna de otro encabezado fuera del bloque, con lista `1,0` | Advertencia |
| Valor ancla de estudio empírico ausente | Error de contrato con el valor esperado y los encontrados |
| Valor ancla de evaluación de impacto ausente | Advertencia; conclusión 2 «no disponible»; tabla «no verificable» |
| Intervenciones o nivel sin lista de validación | Error de contrato |
| Tipo de documento, tipo de fuente o metodología sin lista | Advertencia; se usan los valores presentes |
| Tipo de documento sin lista, con un valor no vacío distinto del valor ancla | No empírico; la advertencia de la columna indica los valores presentes |
| `Año` no numérico | Advertencia; «año no reconocido» |
| Tipo de documento vacío o, si la columna tiene lista, fuera de ella | Sin tipo de documento válido; en $R$, no en $E$ |
| Hoja `EGM` faltante o irreconocible | No verificable, con advertencia |
| Archivo sin valores calculados | No verificable, con advertencia |
| Categoría de la matriz sin fila o columna en una tabla comparable | Sin pareja; no verificable con advertencia, salvo que otro valor difiera |
| Fila o columna de una tabla comparable que no sea categoría de la matriz | Sin pareja; mismo tratamiento |
| Tabla comparable con solo algunos valores calculados | Se comparan los presentes; no verificable con advertencia, salvo que alguno difiera. El ausente nunca es 0 |
| Falta o se repite `Total estudios` en una tabla donde se espera | Sin pareja; mismo tratamiento |
| Nombre repetido dentro de una tabla comparable | Sin pareja; mismo tratamiento |
| Intervención o nivel agregado a la lista | Se toma sin cambios en la herramienta; la verificación sigue la sección 7, punto 9 |
| Columna agregada dentro del bloque de dimensiones | Se toma como dimensión; advertencia si no tiene lista `1,0` |
| Categoría o dimensión retirada | Desaparece del mapa; las filas que aún usen el valor generan advertencia; la verificación sigue la sección 7, punto 9 |
| Número escrito como texto | Advertencia; no marca la dimensión |

## Apéndice A. Instancia de ejemplo verificada (v4)

Extraída del archivo vigente el 1-nov-2026, leído en modo lectura y recalculada desde las celdas. No define
el comportamiento de la herramienta; solo sirve de esperado en pruebas y escenarios.

**Archivo:** `data/raw/matriz_bibliografica_estado_del_arte_v4.xlsx`  
**SHA-256:** `7E1714DE871883818532BF6307C0E4093FB3B62F9B54662C3AC17A7C1952C3A1`

El hash es un control del proceso del proyecto: permite comprobar que el archivo nunca se modificó. No es una
función de la herramienta.

- **Hojas:** `Matriz bibliográfica` (A1:Y36), `EGM` (A1:J41), `Instrucciones` (A1:B20), `Guía por tipo de
  documento` (A1:F17).
- **Validaciones:** filas 2 a 36. Fórmulas de `EGM`: filas 2 a 200. Sin valores calculados guardados: 0
  celdas numéricas en la hoja `EGM`.
- **Listas:** 6 tipos de documento, 3 tipos de fuente, 6 intervenciones más «No aplica (documento
  teórico/metodológico/normativo)», 7 metodologías, 4 niveles más «No aplica (marco
  conceptual/normativo/metodológico)».
- **Dimensiones descubiertas (8):** Vulnerabilidad, Humano, Social, Natural, Físico, Financiero, Estructuras y
  procesos, Sostenibilidad.

| Medida | Valor |
|---|---|
| $\lvert R\rvert$ documentos | 27 (N.º 1 a 27; filas 2 a 28; filas 29 a 36 vacías) |
| Por tipo de documento | 9 metodológico, 7 empírico, 4 teórico, 3 normativo, 3 crítico-contextual, 1 comparativo internacional |
| $\lvert E\rvert$ | 7 (N.º 7, 10, 11, 13, 15, 16, 24) |
| $N = \lvert M\rvert$ | 1 (N.º 7) |
| $\lvert P\rvert$ | 6 (N.º 10, 11, 13, 15, 16, 24) |
| Estado de los documentos | 1 en el mapa, 6 empíricos pendientes, 20 no empíricos, 0 sin tipo de documento válido |
| Celdas con $S(i,j) > 0$ | 6 de 48, todas en 1 |
| Celdas en 0 | 42 de 48 |
| Celdas en 1 | {Transferencia de activos, Acompañamiento técnico} × {Vulnerabilidad, Humano, Financiero} |
| $T_4$ | Evaluación de impacto 1; Estudio de caso 0; Informe de proyecto 0; Informe descriptivo/opinión 0 |
| $t(i)$ | 1 en Transferencia de activos y Acompañamiento técnico; 0 en las demás |
| Tipo de fuente | 6 Académica, 1 Institucional, 0 Territorial, 20 sin diligenciar |
| Metodología | 6 Conceptual/teórica, 1 Evaluación de impacto, 20 sin diligenciar |
| Años | 1992 a 2026 |
| Enfoque (todo el corpus) | 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar |
| Enfoque (en $M$) | 1 Sin clasificar (N.º 7) |
| Advertencias de enfoque | N.º 2 y 7, por no empezar por Sí, No o Parcial |
| Verificación cruzada | No verificable: el archivo no trae valores calculados |

**Nota de lectura.** Los estados no reproducen el avance que informa la presentación del equipo (láminas 8 y 10: 27 documentos, 7 diligenciados por completo y 20 solo con referencia), porque miden otra cosa. Las láminas no indican qué filas son esas 20 referencias. En el archivo, los N.º 8 a 27 son las 20 filas con solo N.º, referencia, año y tipo: 6 son empíricos pendientes y 14 no empíricos. Los 20 no empíricos de la tabla son otro conjunto (N.º 1 a 6, 8, 9, 12, 14, 17 a 23 y 25 a 27), que comparte 14 documentos con el anterior. Los N.º 8 a 27 también son los 20 de tipo de fuente sin diligenciar. Esta nota es una aclaración: no es un valor esperado, una regla ni un cálculo de la herramienta.

## Apéndice B. Interna — no publicar

> Información interna para Jairo y el mantenedor. No se reproduce en ningún texto o interfaz para el equipo sin
> autorización explícita de Jairo.

La tabla 3 de la hoja `EGM` aplica el criterio `"Sí*"` sobre `$M$2:$M$200` (columna «Humano», valores 1/0) en
lugar de la columna de enfoque de género/diferencial. Por eso vale 0 en todas sus celdas con cualquier dato que
respete la lista. Comprobado en B26 y J26 del archivo vigente. La nota A41 de la hoja describe el bloque en
términos de la columna de enfoque.

Consecuencias para la herramienta:

- Calcula el enfoque desde su columna (sección 6) y no necesita esa tabla para funcionar.
- La tabla queda fuera de las comparables de la sección 7, y la interfaz no muestra esa comparación
  (sección 7, punto 6).
- La discrepancia conocida queda solo en registros internos del proyecto: este apéndice y los informes para
  Jairo. La herramienta no la calcula ni la anota en sus registros de ejecución, que no contienen datos de la
  matriz (`NFR-000-17`). `[Fuente: decisión de Jairo, 2-nov-2026, para «queda solo en registros internos» y para que los registros de ejecución no contengan datos de la matriz; doc. técnico §9.1, para «no la calcula», porque excluye esa tabla de la comparación. Decisión de Jairo, 2-nov-2026: entender «registros internos» como los del proyecto (este apéndice y los informes para Jairo) y no anotar la discrepancia en los registros de ejecución.]`

Los N.º 2 y 7 se muestran «Sin clasificar», con la advertencia de la sección 6; nada más.
`[Fuente: decisión de Jairo, 2-nov-2026]`

`[NEEDS CLARIFICATION: ¿se comunica al equipo la discrepancia de la tabla 3? Pendiente de Jairo; mientras no indique otra cosa, se mantiene lo anterior.]`
