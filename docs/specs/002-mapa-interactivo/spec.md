# Feature Specification: Mapa interactivo de evidencias y brechas

**Created**: 2026-11-01  
**Estado**: v0 — propuesta, alcance por acordar

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver el mapa (Priority: P1)

Una persona del equipo abre el mapa y ve, de un vistazo, dónde hay estudios y dónde no: intervenciones en filas,
dimensiones en columnas, y en cada cruce una burbuja con su número.

**Why this priority**: es el producto del Objetivo 2 del proyecto y la pieza central de la herramienta.

**Independent Test**: se comprueba con la instancia de ejemplo y con matrices sintéticas, leyendo el mapa contra
los conteos del contrato.

**Acceptance Scenarios**:

1. **Scenario**: US-002-1.1 Mapa de la matriz vigente
   - **Given** la instancia de ejemplo del apéndice A del contrato
   - **When** la persona abre el mapa
   - **Then** ve 6 filas y 8 columnas, 6 celdas con 1 estudio cada una y 42 celdas con el rótulo «ningún estudio registrado»

2. **Scenario**: US-002-1.2 Tamaño de burbuja
   - **Given** una matriz sintética con una celda de 1 estudio y otra de 5
   - **When** la persona abre el mapa
   - **Then** la burbuja de 5 es mayor y cada celda muestra su número escrito

3. **Scenario**: US-002-1.3 Niveles dentro de una celda
   - **Given** una matriz sintética con una celda de 3 estudios: 2 evaluaciones de impacto y 1 estudio de caso
   - **When** la persona abre el mapa
   - **Then** la celda deja distinguir los 2 y el 1, por color y por texto

4. **Scenario**: US-002-1.4 Filas y columnas del archivo
   - **Given** una matriz sintética con 7 intervenciones y 9 dimensiones
   - **When** la persona abre el mapa
   - **Then** ve 7 filas y 9 columnas, sin ningún cambio en la herramienta

5. **Scenario**: US-002-1.5 Advertencias de la lectura
   - **Given** una matriz cuya verificación quedó «no verificable»
   - **When** la persona abre el mapa
   - **Then** ve una advertencia que lo indica, en lenguaje llano

6. **Scenario**: US-002-1.6 Verificación con diferencias
   - **Given** una matriz sintética cuya verificación quedó «difiere»
   - **When** la persona abre el mapa
   - **Then** ve, en lenguaje llano, qué tablas verificadas difieren y la explicación conocida, sin mencionar ninguna tabla no comparable

7. **Scenario**: US-002-1.7 Orden de filas y columnas
   - **Given** una matriz sintética cuya lista de intervenciones y cuyas columnas de dimensión tienen un orden distinto del alfabético
   - **When** la persona abre el mapa
   - **Then** las filas siguen el orden de la lista y las columnas, el de la matriz

---

### User Story 2 - Ver los estudios de una celda (Priority: P2)

Al seleccionar una celda, la persona ve qué estudios la componen y puede comprobar el número.

**Why this priority**: sin esto, el mapa no es trazable.

**Independent Test**: se comprueba seleccionando celdas y comparando su lista con los N.º esperados.

**Acceptance Scenarios**:

1. **Scenario**: US-002-2.1 Detalle de una celda con estudios
   - **Given** la instancia de ejemplo
   - **When** la persona selecciona Acompañamiento técnico × Humano
   - **Then** ve 1 estudio: N.º 7, con su referencia, su año y su nivel de evidencia

2. **Scenario**: US-002-2.2 Enlace a la fuente
   - **Given** un estudio cuya referencia contiene un DOI o una URL
   - **When** la persona ve su detalle
   - **Then** la referencia ofrece un enlace

3. **Scenario**: US-002-2.3 Detalle de una celda en 0
   - **Given** la instancia de ejemplo
   - **When** la persona selecciona una celda sin estudios
   - **Then** ve «ningún estudio registrado», con la nota de que nadie ha estudiado ese cruce o no se ha encontrado

4. **Scenario**: US-002-2.4 Textos completos del estudio
   - **Given** la instancia de ejemplo
   - **When** la persona abre el N.º 7
   - **Then** ve tal cual sus textos de país y población, dimensiones evaluadas, indicadores, hallazgos, vacío, limitaciones y aporte

---

### User Story 4 - Filtrar el mapa (Priority: P2)

La persona restringe el mapa por tipo de fuente, metodología, nivel de evidencia o año, para ver una parte de
los estudios.

**Why this priority**: permite responder preguntas específicas.

**Independent Test**: se comprueba con una matriz sintética de categorías conocidas.

**Acceptance Scenarios**:

1. **Scenario**: US-002-4.1 Filtro por tipo de fuente
   - **Given** una matriz sintética con 3 estudios, 2 de fuente Territorial y 1 Académica
   - **When** la persona deja activa solo Territorial
   - **Then** el mapa recuenta con 2 estudios, el filtro queda visible y se muestra «2 de 3»

2. **Scenario**: US-002-4.2 Celda vacía por el filtro
   - **Given** una celda con estudios que el filtro deja en 0
   - **When** el filtro está activo
   - **Then** se rotula «ningún estudio registrado con los filtros activos», nunca «brecha»

3. **Scenario**: US-002-4.3 Filtros combinados
   - **Given** una matriz sintética con estudios de varias fuentes y metodologías
   - **When** la persona activa un valor en cada filtro
   - **Then** el mapa cuenta solo los estudios que cumplen ambos

4. **Scenario**: US-002-4.4 Rango de años
   - **Given** una matriz sintética con estudios de 2010, 2015 y 2020
   - **When** la persona elige desde 2012 hasta 2020
   - **Then** cuenta los estudios de 2015 y 2020, ambos extremos incluidos

5. **Scenario**: US-002-4.5 Ocultar un nivel desde la leyenda
   - **Given** una matriz sintética con estudios de dos niveles
   - **When** la persona oculta un nivel en la leyenda
   - **Then** el filtro de nivel refleja el cambio, y cifras y notas se recalculan sin ese nivel

6. **Scenario**: US-002-4.6 Quitar los filtros
   - **Given** filtros activos
   - **When** la persona los quita
   - **Then** el mapa vuelve a sus conteos sin filtrar

7. **Scenario**: US-002-4.7 Filtro conservado
   - **Given** un filtro activado en el mapa
   - **When** la persona abre el detalle de una celda y vuelve al mapa
   - **Then** el mismo filtro sigue activo

8. **Scenario**: US-002-4.8 Varios valores en un filtro
   - **Given** una matriz sintética con estudios de fuente Académica, Institucional y Territorial, y de tres metodologías
   - **When** la persona deja activas Académica y Territorial, y luego dos metodologías
   - **Then** el mapa cuenta primero los estudios con cualquiera de las dos fuentes, y luego solo los que además tienen una de las dos metodologías

9. **Scenario**: US-002-4.9 Filtro sin lista en el archivo
   - **Given** una matriz sintética sin lista de validación en tipo de fuente
   - **When** la persona abre ese filtro
   - **Then** ve los valores presentes en esa columna

---

### User Story 3 - Consultar definiciones (Priority: P3)

Al seleccionar el nombre de una fila o columna, la persona ve qué significa.

**Why this priority**: ayuda a leer el mapa, pero el mapa funciona sin ella.

**Independent Test**: se comprueba seleccionando cada encabezado.

**Acceptance Scenarios**:

1. **Scenario**: US-002-3.1 Definición disponible
   - **Given** una fila o columna con definición suministrada por el equipo
   - **When** la persona selecciona su nombre
   - **Then** ve ese texto, sin alteraciones

2. **Scenario**: US-002-3.2 Categoría sin definición
   - **Given** una categoría nueva de la matriz sin definición suministrada
   - **When** la persona selecciona su nombre
   - **Then** ve que la definición no está disponible, y el mapa sigue funcionando

---

### User Story 5 - Exportar (Priority: P3)

La persona descarga el mapa para llevarlo a un documento o presentación.

**Why this priority**: es útil para reportar, pero no cambia el análisis.

**Independent Test**: se comprueba descargando ambos formatos.

**Acceptance Scenarios**:

1. **Scenario**: US-002-5.1 Exportar imagen
   - **Given** el mapa visible
   - **When** la persona pide la imagen
   - **Then** descarga una imagen con el mapa tal como lo ve, que indica los filtros, el archivo y la fecha de lectura

2. **Scenario**: US-002-5.2 Exportar conteos
   - **Given** el mapa con un filtro activo
   - **When** la persona pide la tabla de conteos
   - **Then** descarga la tabla con esos conteos, y la exportación indica los filtros, el archivo y la fecha de lectura

### Edge Cases

- ¿Qué pasa si un estudio tiene vacío el campo que se filtra? No cumple ningún valor de ese filtro y queda fuera mientras el filtro esté activo; «n de N» lo refleja.
- ¿Qué pasa si no hay ningún estudio en el mapa? Se muestran todas las filas y columnas con el rótulo de celda en 0 y una advertencia de que aún no hay estudios codificados.
- ¿Qué pasa si los filtros dejan el mapa sin estudios? Se muestra «0 de N» y el rótulo con filtros activos en todas las celdas.
- ¿Qué pasa si un nivel de evidencia nuevo se agrega a la lista? Aparece en la leyenda y en el filtro, con su propio color.
- ¿Qué pasa si un estudio del mapa no tiene nivel de evidencia? Se cuenta y se muestra como «sin nivel», sin asignarle ningún nivel.
- ¿Qué pasa con un estudio con año no reconocido? No cumple un filtro de año activo; sin ese filtro, se cuenta normalmente.
- ¿Y con muchas filas y pantallas de 360 px? El mapa conserva sus nombres legibles y se puede recorrer dentro de su propio contenedor.
- ¿Qué pasa con un estudio con dos intervenciones? Aparece en ambas filas, y el número de estudios no suma celdas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-002-01**: El mapa MUST mostrar las intervenciones en filas y las dimensiones en columnas, en el orden del archivo que define el contrato. [Fuente: lámina 5; doc. general §2.2] [Propuesta sin fuente, pendiente de aprobación: la regla de orden del contrato, sección 4]
- **FR-002-02**: Cada cruce MUST mostrar una burbuja cuyo tamaño crece con el número de estudios, con el número escrito. [Fuente: doc. general §3; doc. técnico §4.1]
- **FR-002-03**: El color MUST representar el nivel de evidencia, y una celda con varios niveles MUST permitir distinguir el conteo de cada uno. [Fuente: lámina 5; doc. general §2.2]
- **FR-002-04**: Una celda en 0 MUST rotularse «ningún estudio registrado», con la nota de que nadie ha estudiado ese cruce o no se ha encontrado. [Fuente: doc. general §7; lámina 5]
- **FR-002-05**: Al seleccionar una celda, la herramienta MUST mostrar sus estudios con N.º, referencia, año y nivel de evidencia. [Fuente: doc. general §4.2; doc. técnico §4.1]
- **FR-002-06**: La herramienta MUST ofrecer un enlace cuando la referencia contenga un DOI o una URL. [Fuente: doc. técnico §4.1]
- **FR-002-07**: El detalle de un estudio MUST mostrar tal cual sus textos de país y población, dimensiones evaluadas, indicadores, hallazgos, vacío, limitaciones y aporte. [Fuente: doc. técnico §4.1 RF4]
- **FR-002-08**: Al seleccionar el nombre de una fila o columna, la herramienta MUST mostrar su definición con el texto que indique el equipo, y si no existe, MUST indicar que no está disponible. Las definiciones salen de un archivo de texto aparte; mientras no exista, se indica «definición no disponible». [Fuente: doc. general §3; decisión de Jairo, 2-nov-2026]
- **FR-002-09**: El mapa MUST poder filtrarse por tipo de fuente, metodología, nivel de evidencia y año, tomando los valores de las listas del archivo o, sin lista, los valores presentes. [Fuente: doc. general §4.3; decisión de Jairo, 2-nov-2026]
- **FR-002-10**: El filtro de año MUST ser por rango, desde y hasta, con ambos extremos incluidos. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-002-11**: Varios filtros MUST combinarse por conjunción, y los filtros de tipo de fuente, metodología y nivel de evidencia MUST admitir más de un valor. [Fuente: doc. técnico §4.1 RF2; decisión de Jairo, 2-nov-2026]
- **FR-002-12**: El filtro por nivel de evidencia y el mostrar u ocultar de la leyenda MUST ser un solo control; ocultar un nivel MUST recalcular cifras y notas. [Fuente: decisión de Jairo, 1-nov-2026] [NEEDS CLARIFICATION: ocultar cualquier nivel activa el filtro, y un filtro activo saca a los estudios sin nivel aunque nadie los haya ocultado. ¿Cómo actúa el estado «sin nivel» en este control? Propuesta: la leyenda agrega «Sin nivel» como una entrada más cuando existan esos estudios, y solo salen al ocultar esa entrada; es una excepción, solo para este filtro, a la regla de que una celda vacía no cumple un filtro activo. Pendiente de Jairo; no se aplica.]
- **FR-002-13**: Con un filtro activo, la herramienta MUST mantenerlo siempre visible y mostrar «n de N» estudios. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-002-14**: Con un filtro activo, una celda en 0 MUST rotularse «ningún estudio registrado con los filtros activos», nunca «brecha». [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-002-15**: El estado de los filtros MUST compartirse entre el mapa y el tablero. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-002-16**: La herramienta MUST permitir descargar el mapa como imagen y los conteos como tabla, indicando los filtros activos, el archivo y la fecha de lectura. [Fuente: doc. general §3; doc. técnico §4.1]
- **FR-002-17**: La herramienta MUST mostrar las advertencias de lectura y verificación que afecten a la confianza en el mapa. [Fuente: doc. general §4.1]
- **FR-002-18**: La herramienta MUST permitir quitar los filtros activos en una sola acción y volver a los conteos sin filtrar. [Propuesta sin fuente, pendiente de aprobación: complemento de FR-002-13]

### Key Entities

- **Celda del mapa**: cruce de una intervención y una dimensión, con su conteo total, su conteo por nivel y su lista de N.º.
- **Estudio empírico**: estudio del mapa, con sus datos y textos para el detalle.
- **Nivel de evidencia**: categoría de la leyenda, con su color y su estado visible u oculto.
- **Filtro**: selección de valores o rango de años activa, compartida con el tablero.
- **Definición**: texto de una intervención o dimensión, tomado de un archivo de texto aparte.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-002-01**: En el 100 % de las celdas, el número mostrado coincide con $S(i,j)$ o $S_\varphi(i,j)$ del contrato, y con la longitud de su lista de N.º.
- **SC-002-02**: Una persona del equipo llega desde una celda a la referencia de un estudio en un máximo de dos acciones.
- **SC-002-03**: En todas las combinaciones de filtros de una matriz sintética, «n de N» y los conteos coinciden con un recálculo independiente.
- **SC-002-04**: Todas las funciones del mapa se pueden usar solo con teclado.
- **SC-002-05**: La tabla exportada coincide celda a celda con el mapa visible, con y sin filtros.
