# Visión y alcance: herramienta EGM · Medios de vida

**Created**: 2026-11-01  
**Estado**: v0 — propuesta, alcance por acordar

## Propósito

El proyecto «Marco de evaluación de las medidas de reparación orientadas al restablecimiento de los medios de
vida de la población víctima en Colombia» mantiene una matriz bibliográfica del estado del arte. La hoja EGM de
esa matriz cuenta estudios, pero no permite explorarlos ni extraer conclusiones.

La herramienta es una aplicación web de solo lectura que recibe la matriz y presenta el mapa de evidencias y
brechas interactivo y un tablero analítico con conclusiones calculadas, cada número trazable hasta las filas que
lo producen. `[Fuente: doc. general §3, §4; decisión de Jairo, 31-oct-2026]`

Es **escalable**: procesa las versiones presentes y futuras de la matriz del estado del arte de este proyecto
que cumplan `contrato-datos.md`, sin reconstruirse ni compararlas con otra versión. Otras matrices quedan fuera
de alcance. `[Fuente: decisión de Jairo, 1-nov-2026]`

El mapa no dice qué ayuda funciona: dice dónde hay evidencia y dónde falta. `[Fuente: doc. general §2.3]`

## Actores

| Actor | Interés |
|---|---|
| Equipo de investigación | Cargar la matriz en su sesión, consultar el mapa, el detalle y las conclusiones, y comprobar cada número. Es dueño de la matriz, las categorías y la metodología |
| Investigadora principal | Lo anterior, y acordar el alcance |
| Jairo (mantenedor) | Atender errores de contrato y advertencias, y mantener la herramienta |

## Alcance

| Fase de la propuesta | Contenido | Spec |
|---|---|---|
| F2 | Leer, validar, contar y verificar contra la hoja EGM | `001-lectura-verificacion` |
| F3 | Mapa interactivo con detalle, definiciones, filtros y exportación | `002-mapa-interactivo` |
| F4 | Tablero con cifras clave y conclusiones trazables, con filtros | `003-tablero-conclusiones` |

`[Fuente: doc. general §10]` La fase F1 (acordar el alcance con la investigadora principal) no es construcción;
por eso todos los specs están en v0.

## Fuera de alcance

- Vista de red (F5). `[Fuente: doc. general §8]`
- Módulo de aprendizaje no supervisado: escala futura. El núcleo queda extensible para ambos.
  `[Fuente: decisión de Jairo, 31-oct-2026]`
- Edición de la matriz. `[Fuente: doc. general §4.2]`
- Autenticación: ninguna fuente la pide.
- Conservar la matriz o sus resultados entre sesiones: cada sesión empieza sin datos.
  `[Fuente: decisión de Jairo, 2-nov-2026]`
- Métrica de avance por fila («diligenciado por completo»): no se incluye. `[Fuente: decisión de Jairo, 2-nov-2026]`
- Filtros por intervención, dimensión o enfoque diferencial: mejora futura.
  `[Fuente: decisión de Jairo, 1-nov-2026]`
- Filtros por región, país o población, ámbito o implementador: la matriz no los ofrece como categorías.
  `[Fuente: doc. técnico §4.1]`
- Matrices de otros proyectos. `[Fuente: decisión de Jairo, 1-nov-2026]`
- Mostrar porcentajes en esta versión: la capacidad existe, pero inactiva. `[Fuente: decisión de Jairo, 1-nov-2026]`
- Inferencia estadística: todo es descriptivo. `[Fuente: doc. técnico §7]`

## Restricciones

1. La herramienta se construye como aplicación web. `[Fuente: decisión de Jairo, 31-oct-2026]`
2. El análisis de datos y el dashboard con filtros se implementan en Python.
   `[Fuente: decisión de Jairo, 31-oct-2026]`
3. La matriz es del equipo y de solo lectura; la herramienta se adapta a ella, no al revés.
   `[Fuente: doc. general §4]`
4. Ningún cambio en el área del equipo es necesario para que funcione. `[Fuente: doc. técnico §11]`
5. La primera versión terminada es local, para la demostración. `[Fuente: decisión de Jairo, 2-nov-2026]`

## Requirements

### Non-Functional Requirements

- **NFR-000-01**: La herramienta MUST abrir la matriz en modo lectura y nunca escribir en ella: el archivo cargado nunca se modifica. [Fuente: doc. técnico §4.2 RNF1; decisión de Jairo, 2-nov-2026]
- **NFR-000-02**: Todo número mostrado MUST poder descomponerse en la lista de filas (N.º de la matriz) que lo producen. [Fuente: doc. general §4.2; doc. técnico §4.2 RNF4]
- **NFR-000-03**: Todo texto de la interfaz MUST estar en español, de usted, sin jerga técnica ni fórmulas, y sin preguntas al equipo. [Fuente: estado §5]
- **NFR-000-04**: La interfaz MUST cumplir WCAG 2.2 nivel AA. [Fuente: prompt de la fase 1, T3]
- **NFR-000-05**: La interfaz MUST funcionar desde 360 px de ancho sin desplazamiento horizontal de la página. [Fuente: prompt de la fase 1, T3]
- **NFR-000-06**: La herramienta MUST adaptarse sin cambios de código a intervenciones, dimensiones y niveles nuevos, retirados o renombrados en la matriz, tomándolos del propio archivo; los valores ancla siguen la sección 4.1 del contrato. [Fuente: doc. general §9; decisión de Jairo, 1-nov-2026; decisión de Jairo, 2-nov-2026]
- **NFR-000-07**: La herramienta MUST mostrar conteos, nunca porcentajes, en esta versión; la capacidad de porcentajes MUST quedar inactiva por defecto, con interruptor configurable y $n_{min} = 100$ configurable, evaluado sobre el denominador de cada porcentaje. [Fuente: doc. general §7; decisión de Jairo, 1-nov-2026]
- **NFR-000-08**: Una celda en 0 MUST comunicarse como «ningún estudio registrado», nunca como «no investigado», y toda brecha MUST presentarse como provisional. [Fuente: doc. general §7; lámina 5]
- **NFR-000-09**: La misma matriz MUST producir exactamente las mismas salidas, y cada salida MUST indicar el nombre del archivo y la fecha de lectura. [Fuente: doc. técnico §4.2 RNF2]
- **NFR-000-10**: La información de una celda MUST no depender solo del color: cada celda muestra su número. [Fuente: doc. técnico §4.2 RNF5]
- **NFR-000-11**: El pie de página MUST mostrar la información del grupo de investigación como colofón, con el código Minciencias COL0016423, el correo de contacto ogarciav@unimagdalena.edu.co y los logos de Minciencias y de la Universidad del Magdalena. MUST omitir la categoría y la línea de investigación, y MUST NOT publicar ningún dato pendiente de confirmación: mientras no se confirme, se omite la línea completa. Los logos MUST NOT recolorearse ni deformarse, MUST llevar texto alternativo y MUST ser legibles en modo claro y oscuro, sobre una placa clara si hace falta, y desde 360 px de ancho. [Fuente: decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026]
- **NFR-000-12**: El pie de página MUST tomar el nombre del archivo, el número de documentos y la fecha de lectura en tiempo de ejecución, nunca de un texto escrito a mano. [Fuente: decisión de Jairo, 31-oct-2026; decisión de Jairo, 2-nov-2026] [NEEDS CLARIFICATION: la matriz llega como archivo cargado y no declara su versión en ninguna celda. Propuesta: el colofón dice «Matriz: <nombre del archivo tal como llegó>, leída el <fecha de la carga>, <n> documentos»; la herramienta no deduce ninguna versión, ni siquiera de un «v4» en el nombre. Pendiente de Jairo.]
- **NFR-000-13**: El diseño MUST ser no genérico y acorde con la formalidad académica del proyecto, conforme a la guía de diseño del proyecto. [Fuente: decisión de Jairo, 31-oct-2026]
- **NFR-000-14**: El núcleo de análisis MUST no depender de la capa web, para poder agregar la vista de red o el módulo no supervisado sin rehacerlo. [Fuente: decisión de Jairo, 31-oct-2026]
- **NFR-000-15**: La herramienta MUST usarse desde un navegador de internet. [Fuente: doc. general §4.2; decisión de Jairo, 31-oct-2026]
- **NFR-000-16**: El mapa de 3ie MUST usarse solo como referencia de diseño, citado y sin copiar su contenido ni su marca. [Fuente: doc. general §3]
- **NFR-000-17**: El archivo cargado MUST vivir solo durante la sesión: MUST NOT guardarse en base de datos, en disco del servidor ni en registros; al terminar la sesión MUST NOT quedar copia del archivo ni de su contenido, y los registros MUST NOT contener datos de la matriz, ni siquiera el nombre del archivo. Una sesión va desde que se carga la matriz hasta que quien la usa cierra la herramienta o vence el tiempo de inactividad. [Fuente: decisión de Jairo, 2-nov-2026]
- **NFR-000-18**: Cada sesión MUST ser independiente de las demás: ninguna ve el archivo, los resultados ni los filtros de otra. [Fuente: decisión de Jairo, 2-nov-2026]
- **NFR-000-19**: La herramienta MUST validar el tipo y el tamaño del archivo antes de leerlo, y MUST rechazar con un mensaje legible y sin resultados parciales el que no cumpla. [Fuente: decisión de Jairo, 2-nov-2026]

## Success Criteria

### Measurable Outcomes

- **SC-000-01**: La huella del archivo de la matriz es idéntica antes y después de usar la herramienta.
- **SC-000-02**: En una muestra de números tomados de cada vista, el 100 % se abre en su lista de N.º, y esa lista reproduce el número.
- **SC-000-03**: Una revisión de los textos de la interfaz no encuentra tuteo, fórmulas ni preguntas dirigidas al equipo.
- **SC-000-04**: Una auditoría contra WCAG 2.2 AA no deja hallazgos de ese nivel en ninguna vista.
- **SC-000-05**: Todas las vistas se usan por completo con 360 px de ancho, sin desplazamiento horizontal de la página.
- **SC-000-06**: Tres matrices sintéticas se procesan sin cambios de código y muestran las categorías del archivo: una con una intervención, una dimensión y un nivel agregados; otra con una intervención, una dimensión y un nivel retirados; y otra con una intervención y un nivel renombrados, que no sean valores ancla.
- **SC-000-07**: Con la configuración por defecto no aparece ningún porcentaje en ninguna vista; con el interruptor encendido, la regla de umbral rechaza un denominador de 99 y acepta uno de 100.
- **SC-000-08**: Ninguna vista contiene la expresión «no investigado» y toda celda en 0 usa el rótulo definido.
- **SC-000-09**: Dos lecturas del mismo archivo producen salidas idénticas, salvo la fecha de lectura, y cada una registra archivo y fecha.
- **SC-000-10**: Con la vista en escala de grises se leen el conteo de cada celda y el nivel de evidencia.
- **SC-000-11**: El colofón muestra el código, el correo y los dos logos, no contiene categoría, línea de investigación ni marcador de dato pendiente, y una revisión comprueba en modo claro y oscuro y a 360 px que cada logo conserva sus colores y proporciones, se lee y tiene texto alternativo.
- **SC-000-12**: Al cargar una matriz sintética con otro número de documentos y otro nombre de archivo, el colofón muestra ese número, ese nombre y la fecha de lectura sin ningún cambio en la herramienta.
- **SC-000-13**: Jairo aprueba cada vista contra la guía de diseño del proyecto.
- **SC-000-14**: Los conteos y las conclusiones se obtienen sin arrancar la capa web.
- **SC-000-15**: Las vistas se abren y usan en un navegador. En la versión local, quien consulta usa el equipo donde corre la herramienta y no instala nada más.
- **SC-000-16**: La referencia a 3ie aparece citada en el colofón, y ninguna vista reproduce datos, textos ni marca de 3ie.
- **SC-000-17**: Tras procesar una matriz sintética con marcadores únicos en su nombre y en sus celdas y terminar la sesión, una búsqueda de esos marcadores en el almacenamiento y en los registros de la herramienta no encuentra ninguno, y esa sesión ya no se puede abrir.
- **SC-000-18**: Dos sesiones simultáneas con matrices sintéticas distintas muestran cada una sus propios resultados, y un filtro activado en una no aparece en la otra.
- **SC-000-19**: Un archivo de otro tipo, uno con la extensión correcta y otro contenido, y uno mayor que el límite se rechazan con un mensaje legible, sin mostrar resultados; un archivo en el límite se acepta.

## Puntos abiertos

- `[NEEDS CLARIFICATION: ¿cuál es el límite de tamaño del archivo? Propuesta: 10 MB, configurable; la v4 pesa 27 KB.]`
- `[NEEDS CLARIFICATION: ¿cuánto tiempo de inactividad termina una sesión? Hace falta para quien cierra el navegador sin salir de la herramienta. Propuesta: 30 minutos, configurable.]`

## Decisiones futuras

- **Despliegue.** Si la herramienta se despliega, y dónde, lo decide el equipo después de la demostración. Los destinatarios que el doc. técnico §10 deja por definir se resuelven con esa decisión. `[Fuente: decisión de Jairo, 2-nov-2026]`

## Temas por definir con el equipo

- **Definiciones de filas y columnas.** Salen de un archivo de texto aparte. Mientras no exista, la interfaz indica «definición no disponible». `[Fuente: decisión de Jairo, 2-nov-2026]`

## Notas sobre las fuentes

- El doc. técnico §4.2 RNF3 y §5.2 proponían un archivo autocontenido sin servidor y descartaban una aplicación con servidor. La decisión de Jairo del 31-oct-2026 pide una aplicación web; cómo se sirve se decide en la arquitectura.
- El doc. técnico §4.2 RNF2 pide registrar la huella del archivo en cada salida. NFR-000-09 registra el nombre y la fecha de lectura; la huella queda como control del proceso, según el plan aprobado de la fase.
- La versión de Python no es requisito: se elige para el entorno de construcción y se registra en el resumen de la fase. `[Fuente: decisión de Jairo, 2-nov-2026]`
- El doc. técnico §6.12 define una métrica de avance por fila; queda fuera por decisión de Jairo del 2-nov-2026. Se conserva el dato derivado de la regla del equipo: estudios empíricos que aún no entran al mapa (FR-003-21).
- Se omiten por no estar en el alcance de la fase: el zoom sobre el mapa y las vistas por enfoque del doc. técnico §4.1, y el umbral $N_{min}$ de §6.1, porque el doc. general §7 pide mostrar siempre las conclusiones con su conteo.
- El doc. técnico §5.3 proponía detenerse ante cualquier cambio de esquema. Prevalece la decisión de Jairo del 1-nov-2026: las categorías se adaptan solas y solo faltar un encabezado de rol detiene el proceso.
