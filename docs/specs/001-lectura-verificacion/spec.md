# Feature Specification: Lectura y verificación de la matriz

**Created**: 2026-11-01  
**Estado**: v0 — propuesta, alcance por acordar

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Leer y contar una matriz (Priority: P1)

Con una versión de la matriz ya cargada, la herramienta descubre su estructura, lee sus
documentos y calcula cuántos estudios distintos hay en cada cruce de intervención y dimensión.

**Why this priority**: sin esta lectura no existen el mapa ni las conclusiones.

**Independent Test**: se comprueba con la matriz vigente y con matrices sintéticas, comparando los conteos con
los esperados de `contrato-datos.md`, sin ninguna interfaz.

**Acceptance Scenarios**:

1. **Scenario**: US-001-1.1 Conteo sobre la matriz vigente
   - **Given** la instancia de ejemplo del apéndice A del contrato
   - **When** la herramienta la procesa
   - **Then** informa 27 documentos, 7 estudios empíricos registrados y 1 estudio en el mapa (N.º 7), con 6 de 48 celdas en 1 y 42 en 0

2. **Scenario**: US-001-1.2 Un estudio en cuatro celdas
   - **Given** una matriz sintética con un estudio empírico, dos intervenciones distintas y dos dimensiones en 1
   - **When** la herramienta la procesa
   - **Then** el estudio aparece en 4 celdas y el número de estudios del mapa es 1

3. **Scenario**: US-001-1.3 Una intervención agregada
   - **Given** una matriz sintética con una intervención más en la lista y un estudio que la usa
   - **When** la herramienta la procesa
   - **Then** esa intervención aparece como fila del mapa con su conteo, sin ningún cambio en la herramienta

4. **Scenario**: US-001-1.4 Una dimensión agregada
   - **Given** una matriz sintética con una columna nueva entre los dos encabezados delimitadores, con lista `1,0`
   - **When** la herramienta la procesa
   - **Then** esa columna aparece como dimensión, con el nombre de su encabezado

5. **Scenario**: US-001-1.5 Más filas que las previstas
   - **Given** una matriz sintética con 250 documentos
   - **When** la herramienta la procesa
   - **Then** cuenta los 250 documentos y advierte que la hoja EGM abarca menos filas

6. **Scenario**: US-001-1.6 Clasificación del enfoque diferencial
   - **Given** una matriz sintética con textos «No desarrolla…», «Nota: …», «Sí, aborda…», «Parcial: …», «Si bien…» y una celda vacía
   - **When** la herramienta los clasifica
   - **Then** quedan en No, Sin clasificar con advertencia, Sí, Parcial, Sin clasificar con advertencia, y Sin diligenciar

7. **Scenario**: US-001-1.7 Identificación y filas de cada conteo
   - **Given** la instancia de ejemplo del apéndice A
   - **When** la herramienta la procesa
   - **Then** indica el nombre del archivo y la fecha de lectura, y cada celda en 1 conserva la lista con el N.º 7

8. **Scenario**: US-001-1.8 Columnas y hojas en otro orden
   - **Given** una matriz sintética con las hojas reordenadas y las columnas de rol en otra posición, con el bloque de dimensiones entre sus dos delimitadores
   - **When** la herramienta la procesa
   - **Then** los conteos son los mismos que con el orden original

9. **Scenario**: US-001-1.9 Estado de cada documento
   - **Given** la instancia de ejemplo del apéndice A
   - **When** la herramienta la procesa
   - **Then** informa 1 documento en el mapa, 6 empíricos pendientes, 20 no empíricos y 0 sin tipo de documento válido

---

### User Story 2 - Recibir advertencias legibles (Priority: P1)

Jairo quiere saber qué filas no se pudieron usar y por qué, en palabras claras, para decidir qué hacer. La
herramienta nunca corrige la matriz.

**Why this priority**: un dato mal leído en silencio invalidaría cualquier conclusión.

**Independent Test**: se comprueba con una matriz sintética que contiene cada caso borde del contrato.

**Acceptance Scenarios**:

1. **Scenario**: US-001-2.1 Valor fuera de lista
   - **Given** una matriz sintética con el N.º 3 con una intervención que no está en la lista
   - **When** la herramienta la procesa
   - **Then** emite una advertencia con N.º, columna y valor, y no cuenta ese valor

2. **Scenario**: US-001-2.2 Misma intervención en principal y secundaria
   - **Given** una matriz sintética con un estudio con igual intervención en ambas columnas
   - **When** la herramienta la procesa
   - **Then** lo cuenta una vez y advierte que la hoja EGM lo cuenta dos

3. **Scenario**: US-001-2.3 Estudios empíricos pendientes
   - **Given** la instancia de ejemplo del apéndice A
   - **When** la herramienta la procesa
   - **Then** lista como pendientes los N.º 10, 11, 13, 15, 16 y 24

4. **Scenario**: US-001-2.4 Encabezado de rol ausente
   - **Given** una matriz sintética sin el encabezado «Nivel de evidencia»
   - **When** la herramienta la procesa
   - **Then** se detiene con un error de contrato que nombra ese encabezado, y no muestra resultados parciales

5. **Scenario**: US-001-2.5 Falta un delimitador del bloque
   - **Given** una matriz sintética sin el encabezado «Indicadores o categorías analíticas»
   - **When** la herramienta la procesa
   - **Then** se detiene con un error de contrato que nombra ese encabezado

6. **Scenario**: US-001-2.6 Columna del bloque sin lista
   - **Given** una matriz sintética con una columna del bloque sin lista `1,0`, y otra con lista `1,0` fuera del bloque
   - **When** la herramienta la procesa
   - **Then** emite una advertencia por cada una y continúa

7. **Scenario**: US-001-2.7 Hoja de la matriz faltante
   - **Given** una matriz sintética sin la hoja «Matriz bibliográfica»
   - **When** la herramienta la procesa
   - **Then** se detiene con un error de contrato que nombra esa hoja, y no muestra resultados parciales

8. **Scenario**: US-001-2.8 Columna no usada
   - **Given** una matriz sintética con una columna «Observaciones», sin lista, fuera del bloque de dimensiones
   - **When** la herramienta la procesa
   - **Then** la ignora y muestra la nota informativa «columnas no usadas: Observaciones», sin advertencia

9. **Scenario**: US-001-2.9 Sin valor ancla de estudio empírico
   - **Given** una matriz sintética cuya lista de tipo de documento no tiene ningún valor que empiece por «Estudio empírico»
   - **When** la herramienta la procesa
   - **Then** se detiene con un error de contrato que nombra el valor esperado y los encontrados

10. **Scenario**: US-001-2.10 Sin valor ancla de evaluación de impacto
    - **Given** una matriz sintética cuya lista de nivel no incluye «Evaluación de impacto»
    - **When** la herramienta la procesa
    - **Then** emite una advertencia, calcula el mapa y deja «no verificable» la tabla de evaluación de impacto

11. **Scenario**: US-001-2.11 Intervenciones o nivel sin lista
    - **Given** una matriz sintética sin lista de validación en la columna de nivel de evidencia
    - **When** la herramienta la procesa
    - **Then** se detiene con un error de contrato que nombra esa columna

12. **Scenario**: US-001-2.12 Otra columna categórica sin lista
    - **Given** una matriz sintética sin lista de validación en tipo de fuente
    - **When** la herramienta la procesa
    - **Then** emite una advertencia y usa los valores presentes en esa columna

13. **Scenario**: US-001-2.13 Año no reconocido
    - **Given** una matriz sintética con el N.º 4 con «s. f.» en la columna de año
    - **When** la herramienta la procesa
    - **Then** emite una advertencia con N.º, columna y valor, y lo cuenta como documento con año no reconocido

14. **Scenario**: US-001-2.14 Enfoque que no sigue la regla
    - **Given** la instancia de ejemplo del apéndice A
    - **When** la herramienta la procesa
    - **Then** los N.º 2 y 7 quedan «Sin clasificar», cada uno con una advertencia que cita la regla de la hoja Instrucciones

15. **Scenario**: US-001-2.15 Tipo de documento sin lista
    - **Given** una matriz sintética sin lista de validación en tipo de documento, con cuatro documentos: un estudio empírico que cumple la regla de inclusión y cuyo tipo empieza por «Estudio empírico», uno de tipo «Marco teórico», uno de tipo «Estudio empirico» sin tilde y uno con el tipo vacío
    - **When** la herramienta la procesa
    - **Then** emite una advertencia que nombra la columna e indica los valores presentes, y los documentos quedan, en ese orden, en el mapa, no empírico, no empírico y sin tipo de documento válido

16. **Scenario**: US-001-2.16 Tipo de documento fuera de lista
    - **Given** una matriz sintética con lista de validación en tipo de documento y el N.º 3 con un valor que no está en ella
    - **When** la herramienta la procesa
    - **Then** emite una advertencia con N.º, columna y valor, y ese documento queda sin tipo de documento válido

---

### User Story 4 - Cargar la matriz (Priority: P1)

Quien usa la herramienta carga el archivo de la matriz desde el navegador. La herramienta lo comprueba antes de
leerlo y lo conserva solo mientras dure la sesión.

**Why this priority**: es la única entrada de datos; sin ella no hay nada que mostrar.

**Independent Test**: se comprueba cargando archivos válidos y no válidos, sin revisar ningún conteo.

**Acceptance Scenarios**:

1. **Scenario**: US-001-4.1 Carga válida
   - **Given** una sesión sin matriz cargada
   - **When** la persona carga la instancia de ejemplo del apéndice A
   - **Then** ve el nombre del archivo y la fecha de lectura, y los resultados quedan disponibles

2. **Scenario**: US-001-4.2 Sin matriz cargada
   - **Given** una sesión nueva
   - **When** la persona abre la herramienta
   - **Then** ve la opción de cargar la matriz y ninguna cifra

3. **Scenario**: US-001-4.3 Tipo no admitido
   - **Given** un archivo de otro tipo, o uno con la extensión correcta y otro contenido
   - **When** la persona lo carga
   - **Then** ve un mensaje legible con el motivo, y ningún resultado

4. **Scenario**: US-001-4.4 Tamaño excedido
   - **Given** un archivo mayor que el límite de tamaño
   - **When** la persona lo carga
   - **Then** ve un mensaje legible que indica el límite, y ningún resultado

5. **Scenario**: US-001-4.5 Cargar otro archivo
   - **Given** una sesión con una matriz cargada
   - **When** la persona carga otro archivo válido
   - **Then** los resultados corresponden solo al archivo nuevo y el anterior deja de estar disponible

6. **Scenario**: US-001-4.6 El archivo no se modifica
   - **Given** un archivo con una huella conocida
   - **When** la persona lo carga y usa todas las vistas
   - **Then** la huella del archivo original no cambia

---

### User Story 3 - Verificar contra la hoja EGM (Priority: P2)

Antes de presentar resultados, la herramienta contrasta sus conteos con los de la hoja EGM y advierte si no
coinciden o si no se puede comprobar.

**Why this priority**: da confianza en la lectura, pero el mapa se puede calcular sin ella.

**Independent Test**: se comprueba con matrices sintéticas que traen valores calculados guardados.

**Acceptance Scenarios**:

1. **Scenario**: US-001-3.1 Conteos que coinciden
   - **Given** una matriz sintética cuya hoja EGM incluye todas las categorías, con valores calculados guardados, correctos, y sin filas con igual intervención en ambas columnas
   - **When** la herramienta verifica
   - **Then** cada tabla comparable queda como «coincide»

2. **Scenario**: US-001-3.2 Diferencia explicada
   - **Given** una matriz sintética con valores calculados guardados y un estudio con igual intervención en ambas columnas
   - **When** la herramienta verifica
   - **Then** la tabla queda como «difiere», indica las celdas y explica que se debe a esa fila, y la advertencia aparece antes de presentar los resultados

3. **Scenario**: US-001-3.3 Archivo sin valores calculados
   - **Given** la instancia de ejemplo del apéndice A, que no trae valores calculados
   - **When** la herramienta verifica
   - **Then** el resultado es «no verificable» con una advertencia, y ningún valor ausente se toma como 0

4. **Scenario**: US-001-3.4 Hoja EGM ausente
   - **Given** una matriz sintética sin hoja EGM
   - **When** la herramienta la procesa
   - **Then** el mapa se calcula igual y la verificación queda «no verificable» con advertencia, sin error de contrato

5. **Scenario**: US-001-3.5 Tablas en otra posición
   - **Given** una matriz sintética con filas vacías adicionales antes de cada tabla de la hoja EGM, y valores calculados correctos
   - **When** la herramienta verifica
   - **Then** localiza las tablas por su título y el resultado es «coincide»

6. **Scenario**: US-001-3.6 Tabla no reconocida
   - **Given** una matriz sintética con el título de una tabla de la hoja EGM cambiado
   - **When** la herramienta verifica
   - **Then** esa tabla queda «no verificable» con advertencia y las demás se comparan

7. **Scenario**: US-001-3.7 Tablas verificadas
   - **Given** una matriz sintética con valores calculados guardados, con títulos numerados 1, 2 y 4 en las tablas comparables
   - **When** la herramienta verifica
   - **Then** informa «tablas verificadas: 1, 2 y 4» y ninguna otra tabla de la hoja

8. **Scenario**: US-001-3.8 Dimensión escrita como texto
   - **Given** una matriz sintética con el texto «1» en una dimensión de un estudio, y una hoja EGM que guarda ese estudio como contado
   - **When** la herramienta verifica
   - **Then** la tabla queda como «difiere», indica las celdas y explica que se debe a esa fila

9. **Scenario**: US-001-3.9 Nombres repetidos entre tablas
   - **Given** una matriz sintética cuyas tablas comparables repiten los mismos nombres de fila, con valores correctos y distintos en cada tabla
   - **When** la herramienta verifica
   - **Then** cada valor se compara dentro de su tabla, incluida la tabla por nivel, y cada tabla queda como «coincide»

10. **Scenario**: US-001-3.10 Total estudios en otra posición
    - **Given** una matriz sintética con «Total estudios» entre dos dimensiones, con valores correctos y un estudio con intervención y sin dimensiones
    - **When** la herramienta verifica
    - **Then** esa columna se compara con los estudios por intervención y la tabla queda como «coincide»

11. **Scenario**: US-001-3.11 Categoría nueva que la hoja no tiene
    - **Given** una matriz sintética con una intervención en la lista, ausente de las tablas de la hoja, y los demás valores correctos
    - **When** la herramienta verifica
    - **Then** esas tablas quedan «no verificable», la advertencia nombra la intervención y el mapa la muestra

12. **Scenario**: US-001-3.12 Categoría que sigue en la hoja
    - **Given** una matriz sintética con una fila de la hoja cuya intervención ya no está en la lista, y los demás valores correctos
    - **When** la herramienta verifica
    - **Then** esas tablas quedan «no verificable» y la advertencia nombra esa fila

13. **Scenario**: US-001-3.13 Valores parciales sin diferencias
    - **Given** una matriz sintética con una tabla que solo trae algunos valores calculados, todos correctos
    - **When** la herramienta verifica
    - **Then** la tabla queda «no verificable», la advertencia indica cuántos faltaron y ningún valor ausente se toma como 0

14. **Scenario**: US-001-3.14 Valores parciales con una diferencia
    - **Given** una matriz sintética con una tabla que solo trae algunos valores calculados, uno de ellos distinto del conteo
    - **When** la herramienta verifica
    - **Then** la tabla queda como «difiere», indica ese valor y advierte lo que no se comparó

15. **Scenario**: US-001-3.15 Nombre repetido dentro de una tabla
    - **Given** una matriz sintética con dos filas del mismo nombre en una tabla comparable, y los demás valores correctos
    - **When** la herramienta verifica
    - **Then** la tabla queda «no verificable» y la advertencia nombra esa fila

16. **Scenario**: US-001-3.16 Tabla sin Total estudios
    - **Given** una matriz sintética sin la columna «Total estudios» en una tabla donde se espera, y los demás valores correctos
    - **When** la herramienta verifica
    - **Then** la tabla queda «no verificable» y la advertencia lo indica

### Edge Cases

Los casos borde se tratan como indica la sección 9 de `contrato-datos.md`. En particular:

- ¿Qué pasa con una fila que solo tiene referencia, sin tipo de documento? Queda sin tipo de documento válido: cuenta como documento, no como estudio del mapa.
- ¿Y con un documento no empírico que solo tiene N.º, referencia, año y tipo? Queda como no empírico: no se espera en el mapa, no se lista como empírico pendiente y no genera advertencia por esa razón.
- ¿Y con un estudio empírico con intervención, sin dimensiones? No entra al mapa y se lista como pendiente.
- ¿Y con un documento no empírico con intervención? No entra al conjunto de estudios empíricos y genera advertencia.
- ¿Y con una dimensión con valor fuera de 1, 0 o vacío, incluido el texto «1»? Advertencia, y no marca la dimensión.
- ¿Y con un N.º vacío o repetido? Advertencia; la trazabilidad usa además el número de fila del archivo.
- ¿Y con espacios en los extremos de un valor? Se comparan sin ellos y se advierte.
- ¿Y si se retira una categoría que algunas filas aún usan? Desaparece del mapa y esas filas generan advertencia.
- ¿Y si cambia un valor ancla o una columna pierde su lista? Se trata según `contrato-datos.md` §4.1 y §4.2.
- ¿Y si tipo de documento no tiene lista? Todo valor no vacío distinto del valor ancla queda como no empírico, la celda vacía queda sin tipo de documento válido y la advertencia de la columna indica los valores presentes. Se trata como indica la sección 4 de `contrato-datos.md`.
- ¿Y si el archivo está dañado o no se puede abrir? Se rechaza como un tipo no admitido, sin resultados parciales.
- ¿Y si una categoría está solo en la matriz o solo en la hoja EGM, o una tabla trae valores parciales? Si lo comparado no difiere, la tabla queda «no verificable» con advertencia; si algo difiere, queda como «difiere» y se advierte lo no comparado. Se trata como indica la sección 7 de `contrato-datos.md`. [Fuente: decisión de Jairo, 2-nov-2026]

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001-01**: La herramienta MUST identificar las hojas y columnas por su texto, no por su posición. [Fuente: doc. técnico §5.1]
- **FR-001-02**: La herramienta MUST detenerse con un error de contrato explícito cuando falte la hoja de la matriz o un encabezado de rol, nombrando lo que falta. [Fuente: doc. técnico §5.1, §5.3]
- **FR-001-03**: La herramienta MUST reconocer como dimensiones las columnas situadas entre «Dimensiones evaluadas / propuestas» e «Indicadores o categorías analíticas», ambos excluidos, y emitir error de contrato si falta uno de los dos. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-001-04**: La herramienta MUST emitir advertencia, nunca error, ante una columna del bloque sin lista `1,0` o una columna con lista `1,0` fuera del bloque. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-001-05**: La herramienta MUST tomar intervenciones, niveles y demás listas de las validaciones de datos del archivo; sin lista, MUST seguir FR-001-22. [Fuente: doc. técnico §12.2]
- **FR-001-06**: La herramienta MUST leer todas las filas no vacías, sin límite fijo. [Fuente: doc. técnico §9.2]
- **FR-001-07**: La herramienta MUST incluir en el mapa solo los estudios empíricos con intervención diligenciada y al menos una dimensión en 1. [Fuente: Matriz Instrucciones B20; lámina 6]
- **FR-001-08**: La herramienta MUST calcular el conteo de cada celda como estudios distintos, conforme a $S(i,j)$ del contrato. [Fuente: doc. general §7]
- **FR-001-09**: La herramienta MUST calcular el número de estudios del mapa sobre estudios distintos, nunca sumando celdas. [Fuente: doc. técnico §2.4]
- **FR-001-10**: La herramienta MUST clasificar el enfoque diferencial por el prefijo de la columna, conforme a la sección 6 del contrato, sin inferir categorías del resto del texto, y advertir, citando la regla de la hoja Instrucciones, cuando el texto no siga esa regla. [Fuente: Matriz Instrucciones B14; doc. técnico §6.6; decisión de Jairo, 2-nov-2026]
- **FR-001-11**: La herramienta MUST conservar, para cada conteo, la lista de N.º que lo producen. [Fuente: doc. general §4.2]
- **FR-001-12**: La herramienta MUST emitir una advertencia legible, con N.º, columna y valor, por cada caso que el contrato trate como advertencia, y MUST NOT corregir ningún valor. [Fuente: doc. técnico §9.2]
- **FR-001-13**: La herramienta MUST asignar a cada documento uno de los estados del contrato y listar los estudios empíricos pendientes. [Fuente: doc. técnico §9.2; decisión de Jairo, 2-nov-2026]
- **FR-001-14**: La herramienta MUST comparar sus conteos con las tablas comparables de la hoja EGM definidas en el contrato, celda a celda, y clasificar cada tabla como coincide, difiere o no verificable. [Fuente: doc. general §4.1; doc. técnico §9.1]
- **FR-001-15**: La herramienta MUST localizar las tablas de la hoja EGM por su título y sus filas por su nombre, sin coordenadas fijas. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-001-16**: La herramienta MUST reportar «no verificable» con advertencia, sin error de contrato, si la hoja falta, una tabla no se reconoce o no hay valores calculados. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-001-17**: La herramienta MUST NOT tratar un valor calculado ausente como 0. [Fuente: doc. técnico §9.1]
- **FR-001-18**: Si hay diferencias, la herramienta MUST advertir antes de presentar los resultados y explicar las que tengan causa conocida, como las filas con igual intervención en ambas columnas. [Fuente: doc. general §4.1; doc. técnico §3.2]
- **FR-001-19**: La herramienta MUST identificar la matriz procesada por el nombre de su archivo e indicar la fecha de lectura. [Fuente: doc. técnico §4.2 RNF2]
- **FR-001-20**: La herramienta MUST recibir la matriz por carga desde el navegador, y una carga nueva MUST reemplazar a la anterior dentro de la sesión. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-21**: La herramienta MUST ignorar una columna de otro encabezado fuera del bloque de dimensiones e informarla en la nota «columnas no usadas: …», sin advertencia, salvo que tenga lista `1,0`. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-22**: La herramienta MUST emitir error de contrato si las intervenciones o el nivel de evidencia no tienen lista de validación; en las demás columnas categóricas MUST emitir advertencia y usar los valores presentes. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-23**: Sin valor ancla de estudio empírico, la herramienta MUST emitir un error de contrato que nombre el valor esperado y los encontrados; sin valor ancla de evaluación de impacto, MUST emitir advertencia y continuar. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-24**: La herramienta MUST emitir advertencia ante un año que no sea un número entero, y tratarlo como «año no reconocido». [Propuesta sin fuente, pendiente de aprobación: doc. técnico §6.9 solo trata la celda vacía]
- **FR-001-25**: La herramienta MUST informar la verificación solo sobre las tablas comparables del contrato, cada una por el número de su título. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-26**: La herramienta MUST delimitar cada tabla comparable de la hoja EGM y emparejar sus filas y columnas, incluida «Total estudios», solo dentro de esa tabla, conforme a la sección 7 del contrato y sin coordenadas fijas. [Fuente: decisión de Jairo, 2-nov-2026]
- **FR-001-27**: La herramienta MUST clasificar una tabla como «coincide» solo si compara todos los valores esperados; como «difiere» si algún valor comparado es distinto; y en los demás casos como «no verificable». Si no compara todos, MUST emitir una advertencia que indique lo no comparado. [Fuente: decisión de Jairo, 2-nov-2026]

### Key Entities

- **Documento**: una fila no vacía de la matriz, identificada por su N.º. Puede no tener un tipo de documento válido.
- **Estudio empírico**: documento cuyo tipo es el valor ancla de estudio empírico. Entra al mapa si cumple la regla de inclusión.
- **Intervención**: categoría de la lista de principal o secundaria, sin los valores «No aplica». Fila del mapa.
- **Dimensión**: columna del bloque de dimensiones. Columna del mapa.
- **Nivel de evidencia**: categoría de la lista de nivel, sin los valores «No aplica».
- **Celda del mapa**: cruce de una intervención y una dimensión, con su conteo y su lista de N.º.
- **Advertencia de validación**: mensaje con tipo, N.º o fila, columna, valor y texto legible.
- **Nota informativa**: mensaje que no señala ningún problema, como «columnas no usadas: …».
- **Resultado de verificación**: por tabla, coincide, difiere o no verificable, con su explicación y lo que no se pudo comparar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001-01**: Con la instancia de ejemplo, todos los valores del apéndice A del contrato se reproducen exactamente.
- **SC-001-02**: Cada caso borde del contrato tiene una matriz sintética, y en el 100 % de ellos la herramienta da el tratamiento indicado.
- **SC-001-03**: Los invariantes de la sección 5 del contrato se cumplen en todas las matrices sintéticas generadas al azar.
- **SC-001-04**: Una persona que no conoce el código identifica, solo con el texto de la advertencia, qué fila y qué columna debe revisar, en todos los tipos de advertencia.
- **SC-001-05**: Procesar una matriz nueva con categorías distintas no requiere ningún cambio de código ni de configuración.
