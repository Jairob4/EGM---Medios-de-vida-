# Feature Specification: Tablero analítico y conclusiones

**Created**: 2026-11-01  
**Estado**: v0 — propuesta, alcance por acordar

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver las cifras clave (Priority: P1)

Una persona del equipo abre el tablero y ve cuántos documentos hay, cuántos estudios empíricos y cuántas celdas
tienen estudios, con el mapa a la vista.

**Why this priority**: resume el estado de la matriz y da el contexto de todas las conclusiones.

**Independent Test**: se comprueba con la instancia de ejemplo, comparando con el apéndice A del contrato.

**Acceptance Scenarios**:

1. **Scenario**: US-003-1.1 Cifras de la matriz vigente
   - **Given** la instancia de ejemplo del apéndice A del contrato
   - **When** la persona abre el tablero
   - **Then** ve 27 documentos, 7 estudios empíricos registrados, 1 estudio en el mapa, 6 celdas con estudios y 42 celdas vacías

2. **Scenario**: US-003-1.2 Rastrear una cifra
   - **Given** el tablero abierto con la instancia de ejemplo
   - **When** la persona selecciona «7 estudios empíricos registrados»
   - **Then** ve los N.º 7, 10, 11, 13, 15, 16 y 24 con su referencia

3. **Scenario**: US-003-1.3 Celdas según el archivo
   - **Given** una matriz sintética con 7 intervenciones y 9 dimensiones
   - **When** la persona abre el tablero
   - **Then** el total de celdas es 63, sin ningún cambio en la herramienta

4. **Scenario**: US-003-1.4 Cifras junto a las conclusiones
   - **Given** el tablero abierto
   - **When** la persona lo recorre
   - **Then** encuentra juntas las cifras clave y las conclusiones

5. **Scenario**: US-003-1.5 Estudios que aún no entran al mapa
   - **Given** el tablero abierto con la instancia de ejemplo
   - **When** la persona selecciona «6 estudios empíricos que aún no entran al mapa»
   - **Then** ve los N.º 10, 11, 13, 15, 16 y 24 con su referencia

---

### User Story 2 - Leer las conclusiones (Priority: P1)

La persona lee en lenguaje llano lo que los datos permiten decir, y cada frase indica cuántos estudios la
sostienen y cuáles son.

**Why this priority**: es el valor añadido sobre el mapa de referencia.

**Independent Test**: se comprueba conclusión por conclusión, con matrices sintéticas de resultado conocido.

**Acceptance Scenarios**:

1. **Scenario**: US-003-2.1 Conclusión 1, brechas
   - **Given** la instancia de ejemplo
   - **When** la persona lee las brechas
   - **Then** ve que 42 de 48 cruces no tienen ningún estudio registrado, con la fecha de lectura y la aclaración de que la brecha es provisional

2. **Scenario**: US-003-2.2 Conclusión 2, sin evaluación de impacto
   - **Given** una matriz sintética con una celda de 3 estudios: 2 estudios de caso y 1 informe de proyecto
   - **When** la persona lee la conclusión
   - **Then** indica que hay 3 estudios, ninguno es evaluación de impacto, 2 son estudios de caso y 1 es informe de proyecto

3. **Scenario**: US-003-2.3 Conclusión 2 sin casos
   - **Given** la instancia de ejemplo, cuyo único estudio del mapa es evaluación de impacto
   - **When** la persona lee la conclusión
   - **Then** indica que no hay cruces en esa situación y cuántos estudios se revisaron

4. **Scenario**: US-003-2.4 Conclusión 3, enfoque diferencial
   - **Given** la instancia de ejemplo
   - **When** la persona lee la conclusión para Acompañamiento técnico
   - **Then** de 1 estudio ve 0 que lo incorporan, 0 de forma parcial, 0 que no lo incorporan y 1 sin clasificar (N.º 7)

5. **Scenario**: US-003-2.5 Conclusión 4, qué aparece junto
   - **Given** la instancia de ejemplo
   - **When** la persona lee la conclusión
   - **Then** ve que 1 estudio analiza Acompañamiento técnico junto con Transferencia de activos, y que Vulnerabilidad, Humano y Financiero se miden juntas en 1 estudio

6. **Scenario**: US-003-2.6 Conclusión 5, composición de las fuentes
   - **Given** la instancia de ejemplo
   - **When** la persona lee la conclusión
   - **Then** ve 27 documentos, 0 de fuente territorial, 20 sin tipo de fuente diligenciado, y que el más reciente es de 2026

7. **Scenario**: US-003-2.7 Conclusión 6, reunidos por celda
   - **Given** la instancia de ejemplo
   - **When** la persona consulta Acompañamiento técnico × Humano
   - **Then** ve tal cual el texto de indicadores, vacío y limitaciones del N.º 7

8. **Scenario**: US-003-2.8 Toda conclusión con su lista
   - **Given** cualquier conclusión visible
   - **When** la persona pide sus estudios
   - **Then** ve la lista de N.º que la sostienen, y su longitud coincide con el conteo indicado

9. **Scenario**: US-003-2.9 Conclusión 4, nunca juntas
   - **Given** una matriz sintética con dos dimensiones marcadas en estudios distintos y nunca en el mismo
   - **When** la persona lee la conclusión
   - **Then** ve que esas dos dimensiones nunca se miden juntas, con la aclaración de que es sobre los estudios registrados

10. **Scenario**: US-003-2.10 Conclusión 2 no disponible
    - **Given** una matriz sintética cuya lista de nivel no incluye «Evaluación de impacto»
    - **When** la persona lee las conclusiones
    - **Then** la conclusión 2 indica «no disponible» y las demás se muestran

---

### User Story 4 - Confiar en lo que se lee (Priority: P1)

La persona no debe sacar de una frase más de lo que los datos permiten.

**Why this priority**: con pocos estudios, una conclusión mal presentada puede engañar.

**Independent Test**: se comprueba revisando los textos del tablero con la instancia de ejemplo.

**Acceptance Scenarios**:

1. **Scenario**: US-003-4.1 Sin porcentajes
   - **Given** la configuración por defecto
   - **When** la persona recorre el tablero
   - **Then** todas las cifras son conteos

2. **Scenario**: US-003-4.2 Un estudio en varias celdas
   - **Given** la instancia de ejemplo
   - **When** la persona ve 6 celdas con estudios
   - **Then** se le aclara que todas provienen de 1 estudio

3. **Scenario**: US-003-4.3 Lo que el mapa no dice
   - **Given** el tablero abierto
   - **When** la persona lee las conclusiones
   - **Then** ve la aclaración de que el mapa indica dónde hay evidencia, no qué ayuda funciona

4. **Scenario**: US-003-4.4 Resultado de la verificación
   - **Given** la instancia de ejemplo, que no trae valores calculados
   - **When** la persona abre el tablero
   - **Then** ve en lenguaje llano que los conteos no se pudieron contrastar con la hoja EGM

5. **Scenario**: US-003-4.5 Verificación con diferencias
   - **Given** una matriz sintética cuya verificación quedó «difiere»
   - **When** la persona abre el tablero
   - **Then** ve en lenguaje llano qué tablas verificadas difieren y la explicación conocida, sin mencionar ninguna tabla no comparable

---

### User Story 3 - Filtrar el tablero (Priority: P2)

La persona aplica al tablero los mismos filtros del mapa para ser específica.

**Why this priority**: permite responder preguntas sobre una parte de los estudios.

**Independent Test**: se comprueba con una matriz sintética, comparando con y sin filtros.

**Acceptance Scenarios**:

1. **Scenario**: US-003-3.1 Recalcular con filtros
   - **Given** una matriz sintética con 4 estudios del mapa, 1 de fuente Territorial
   - **When** la persona deja seleccionada solo Territorial y pulsa «Actualizar vista»
   - **Then** cifras, conclusiones y listas de N.º se recalculan, el filtro queda visible y se muestra «1 de 4»

2. **Scenario**: US-003-3.2 Conclusión sin estudios
   - **Given** filtros que no dejan ningún estudio para una conclusión
   - **When** la persona la lee
   - **Then** dice «ningún estudio cumple estos filtros»

3. **Scenario**: US-003-3.3 Sin hablar de brechas con filtros
   - **Given** un filtro activo
   - **When** la persona lee la conclusión 1
   - **Then** las celdas en 0 se rotulan «ningún estudio registrado con los filtros activos» y no se usa «brecha»

4. **Scenario**: US-003-3.4 Filtro conservado
   - **Given** un filtro activado en el tablero
   - **When** la persona abre la lista de N.º de una conclusión y vuelve al tablero
   - **Then** el mismo filtro sigue activo

---

### User Story 5 - Recorrer el mapa y el tablero (Priority: P3)

La persona pasa del mapa al tablero sin perder lo que estaba mirando. Esta historia depende de la feature 002.

**Why this priority**: mejora el recorrido, pero cada vista funciona sola.

**Independent Test**: se comprueba con ambas vistas construidas, activando filtros en una y revisando la otra.

**Acceptance Scenarios**:

1. **Scenario**: US-003-5.1 Del mapa al tablero
   - **Given** un filtro activado en el mapa
   - **When** la persona pasa al tablero
   - **Then** el mismo filtro sigue activo

2. **Scenario**: US-003-5.2 Del tablero al mapa
   - **Given** un filtro activado en el tablero
   - **When** la persona pasa al mapa
   - **Then** el mismo filtro sigue activo

3. **Scenario**: US-003-5.3 Todo a la vista
   - **Given** el tablero abierto
   - **When** la persona lo recorre
   - **Then** encuentra juntos las cifras clave, el mapa y las conclusiones

4. **Scenario**: US-003-5.4 Selección sin aplicar
   - **Given** un filtro aplicado en el mapa
   - **When** la persona cambia la selección de un filtro sin pulsar «Actualizar vista» y pasa al tablero
   - **Then** el mapa y el tablero muestran lo último aplicado

5. **Scenario**: US-003-5.5 Botones comunes a ambas vistas
   - **Given** filtros aplicados
   - **When** la persona pulsa «Restablecer» o «Actualizar vista» desde el tablero
   - **Then** el mapa y el tablero quedan con el mismo estado de filtros

### Edge Cases

- ¿Qué pasa con una conclusión de la que no hay casos? Dice que no hay casos e indica cuántos estudios se revisaron; nunca desaparece en silencio.
- ¿Qué pasa si ningún estudio está en el mapa? Las cifras muestran 0 y cada conclusión lo indica; no se presenta como hallazgo.
- ¿Qué pasa con filas de enfoque sin clasificar? Se cuentan aparte, con su N.º y su texto, sin inferir categoría.
- ¿Qué pasa con documentos sin el campo de un filtro? Quedan fuera mientras el filtro esté activo, y en la composición aparecen como «sin diligenciar». En el nivel de evidencia rige, para los estudios del mapa, la excepción de «Sin nivel» de FR-002-12.
- ¿Qué valores de nivel se ofrecen en el filtro? Los de la lista, sin «No aplica», más la entrada «Sin nivel» cuando existan esos estudios (FR-002-12). Los documentos no empíricos quedan fuera mientras ese filtro esté activo. [NEEDS CLARIFICATION: FR-002-12 trata como «Sin nivel» a los estudios del mapa sin nivel o con un nivel que empieza por «No aplica», y solo salen al ocultar esa entrada. No está decidido si eso vale también para los documentos no empíricos en las cifras de documentos del tablero, que hoy quedan fuera con el filtro de nivel activo. Pendiente de Jairo; no se aplica.]
- ¿Qué es «N» en «n de N»? Cuenta el mismo tipo de elemento que la cifra: documentos en las cifras de documentos, estudios en las de estudios.
- ¿Qué pasa si falta el ancla de evaluación de impacto? La conclusión 2 queda «no disponible»; ver `contrato-datos.md` §4.1.
- ¿Qué pasa con un documento con año no reconocido? En la composición por año aparece como «año no reconocido», separado de «sin diligenciar».

## Requirements *(mandatory)*

### Functional Requirements

- **FR-003-01**: El tablero MUST mostrar como cifras clave los documentos, los estudios empíricos registrados, los estudios del mapa, las celdas con estudios y las celdas vacías. [Fuente: doc. general §9]
- **FR-003-02**: El total de celdas MUST calcularse a partir de las categorías del archivo. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-003-03**: El mapa, las cifras clave y las conclusiones MUST presentarse juntos en el tablero. [Fuente: doc. general §9]
- **FR-003-04**: Cada conclusión MUST decir cuántos estudios o documentos la sostienen y permitir ver cuáles son, con su N.º y su referencia. [Fuente: doc. general §5, §7]
- **FR-003-05**: La conclusión 1 MUST listar los cruces sin ningún estudio registrado, con la fecha de lectura y la aclaración de que es una brecha provisional. [Fuente: doc. general §5.1]
- **FR-003-06**: La conclusión 2 MUST listar los cruces con estudios sin ninguna evaluación de impacto, con el conteo por nivel de evidencia. [Fuente: doc. general §5.2]
- **FR-003-07**: La conclusión 3 MUST indicar, por intervención, cuántos estudios incorporan el enfoque de género o diferencial, cuántos de forma parcial, cuántos no y cuántos quedan sin clasificar. [Fuente: doc. general §5.3; doc. técnico §6.6]
- **FR-003-08**: La conclusión 4 MUST indicar qué intervenciones se estudian combinadas y qué dimensiones se miden en los mismos estudios o nunca juntas. [Fuente: doc. general §5.4]
- **FR-003-09**: La conclusión 5 MUST mostrar cómo se reparten los documentos por tipo de documento, tipo de fuente, metodología y año, con «sin diligenciar» como categoría visible. [Fuente: doc. general §5.5; doc. técnico §6.9]
- **FR-003-10**: La conclusión 6 MUST reunir por celda, tal cual, los indicadores, los vacíos y las limitaciones de sus estudios, sin resumirlos ni interpretarlos. [Fuente: doc. general §5.6; doc. técnico §6.11]
- **FR-003-11**: Cuando una conclusión no tenga casos, MUST decirlo e indicar cuántos estudios se revisaron. [Fuente: doc. general §7]
- **FR-003-12**: Las conclusiones MUST escribirse en lenguaje llano a partir de plantillas, llenando solo los datos calculados. [Fuente: doc. general §5]
- **FR-003-13**: El tablero MUST ofrecer los mismos cuatro filtros del mapa (tipo de fuente, metodología, nivel de evidencia y año), con estado compartido. [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-003-14**: Con un filtro activo, cifras, conclusiones y listas de N.º MUST recalcularse, el filtro MUST quedar siempre visible y MUST mostrarse «n de N». [Fuente: decisión de Jairo, 1-nov-2026; doc. general §9]
- **FR-003-15**: Con un filtro activo, una celda en 0 MUST rotularse «ningún estudio registrado con los filtros activos», nunca «brecha». [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-003-16**: Una conclusión cuyo subconjunto quede vacío MUST decir «ningún estudio cumple estos filtros». [Fuente: decisión de Jairo, 1-nov-2026]
- **FR-003-17**: El tablero MUST mostrar conteos y no porcentajes, y ninguna conclusión MUST depender de un porcentaje. [Fuente: doc. general §7; decisión de Jairo, 1-nov-2026]
- **FR-003-18**: El tablero MUST contar estudios distintos cuando diga cuántos estudios hay, y aclarar que un estudio puede ocupar varias celdas. [Fuente: doc. general §7]
- **FR-003-19**: El tablero MUST aclarar que el mapa indica dónde hay evidencia y dónde falta, no qué ayuda funciona. [Fuente: doc. general §2.3]
- **FR-003-20**: El tablero MUST mostrar el resultado de la verificación contra la hoja EGM, en lenguaje llano. [Fuente: doc. general §7]
- **FR-003-21**: El tablero MUST mostrar el número de estudios empíricos que aún no entran al mapa, derivado de la regla de inclusión del equipo, con su lista de N.º. [Fuente: Matriz Instrucciones B20; decisión de Jairo, 2-nov-2026]
- **FR-003-22**: Sin valor ancla de evaluación de impacto, la conclusión 2 MUST indicar «no disponible», y las demás conclusiones MUST mostrarse. [Fuente: decisión de Jairo, 2-nov-2026]

### Key Entities

- **Cifra clave**: número del tablero con su lista de N.º.
- **Conclusión**: frase en lenguaje llano, generada por plantilla, con su conteo y su lista de N.º.
- **Documento**: base de la conclusión 5.
- **Estudio empírico**: base de las conclusiones 1 a 4 y 6.
- **Filtro**: selección activa compartida con el mapa.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-003-01**: Las seis conclusiones se muestran con su conteo y su lista de N.º, y en el 100 % de los casos la lista reproduce el conteo.
- **SC-003-02**: Todas las cifras del tablero coinciden con el apéndice A del contrato al procesar la instancia de ejemplo.
- **SC-003-03**: En todas las combinaciones de filtros de una matriz sintética, cifras y conclusiones coinciden con un recálculo independiente.
- **SC-003-04**: Una revisión de los textos no encuentra porcentajes, «brecha» con filtros activos, ni afirmaciones sobre si una ayuda funciona.
- **SC-003-05**: Una persona del equipo comprueba cualquier conclusión con la matriz abierta, usando solo los N.º que muestra el tablero.
- **SC-003-06**: Dos matrices sintéticas con datos distintos producen, en cada conclusión, la misma frase, y solo cambian los datos calculados.
