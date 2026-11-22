# Invariantes del sistema EGM

Lista de lo que ninguna corrección puede alterar. Recoge las decisiones fechadas de Jairo, incluidas las aprobadas
en la sección 6 de cada corrección (`docs/correcciones/COR-NNN.md`). Se actualiza cuando Jairo toma una decisión
nueva, con su fecha. La edita la sesión principal, por autorización de Jairo (3-nov-2026); ni el analista ni el
corrector la editan. Las reglas permanentes están en `CLAUDE.md`.

## Decisiones del 31-oct-2026
- Aplicación web. El análisis de datos y el tablero con filtros se implementan en Python.
- El módulo de aprendizaje no supervisado y la vista de red quedan fuera del alcance actual.
- El pie de página muestra información del grupo de investigación. Diseño no genérico, acorde con la formalidad académica.

## Decisiones del 1-nov-2026
- **Dimensiones**: columnas entre «Dimensiones evaluadas / propuestas» e «Indicadores o categorías analíticas», excluidos ambos. Una columna del bloque sin lista `1,0`, o con lista `1,0` fuera del bloque: advertencia, nunca error. Si falta uno de los dos encabezados que delimitan el bloque: error de contrato.
- **Hoja EGM**: solo verificación, nunca fuente. Tablas localizadas por título y filas por nombre, sin coordenadas fijas. Estados de verificación: «coincide», «difiere», «no verificable» (nombres fijados por Jairo el 2-nov-2026). Nunca produce error de contrato. `None` no es 0.
- **Porcentajes**: esta versión muestra solo conteos. Capacidad inactiva por defecto, con interruptor y `n_min = 100` configurables. Un porcentaje se muestra solo si el interruptor está encendido y el denominador de ese porcentaje cumple $n \ge n_{\min}$. El denominador nunca es el total de documentos.
- **Filtros**: los mismos cuatro en mapa y tablero (tipo de fuente, metodología, nivel de evidencia, año), con estado compartido. Con filtro activo: siempre visible, se muestra «n de N», una celda en 0 se rotula «ningún estudio registrado con los filtros activos» y nunca «brecha», y una conclusión con subconjunto vacío dice «ningún estudio cumple estos filtros».
- **Mapa**: el filtro por nivel de evidencia y el mostrar/ocultar de la leyenda son un solo control. El filtro de año es por rango, desde y hasta, con ambos extremos incluidos.
- Filtros por intervención, dimensión o enfoque diferencial: mejora futura, fuera de esta versión.
- **Escalabilidad**: la herramienta procesa las versiones presentes y futuras de la matriz del estado del arte de este proyecto que cumplan el contrato, sin reconstruirse. No compara una matriz con otra versión ni guarda valores de referencia. Las matrices de otros proyectos quedan fuera de alcance.
- Los escenarios se redactan en términos generales; ningún spec menciona «v4» como requisito ni compara versiones; los esperados salen de la matriz real o de fixtures descritos; nunca de la lámina 7.

## Decisiones del 2-nov-2026
- **Errores de contrato posibles**: falta la hoja «Matriz bibliográfica»; falta un encabezado esperado; falta alguno de los dos delimitadores del bloque de dimensiones; falta el valor ancla de estudio empírico; una columna de intervenciones o nivel de evidencia pierde su lista de validación. Cualquier otra anomalía es advertencia o nota. La ausencia del ancla de evaluación de impacto es advertencia y la conclusión 2 queda «no disponible».
- Columnas ajenas fuera del bloque: se ignoran con nota informativa, salvo que tengan lista `1,0` (advertencia).
- **Carga de la matriz**: desde el navegador. Antes de leerlo, se validan el tipo y el tamaño del archivo; el que no cumpla se rechaza con un mensaje legible y sin resultados parciales. El archivo vive solo durante la sesión; no se guarda en base de datos, disco del servidor ni registros, y los registros no contienen datos de la matriz. Una sesión va desde que se carga la matriz hasta que quien la usa cierra la herramienta o vence el tiempo de inactividad (F7, COR-004). Cada sesión es independiente y empieza sin datos. El archivo cargado nunca se modifica.
- La primera versión es local, para la demostración. El despliegue es decisión futura del equipo.
- **Colofón**: código Minciencias COL0016423, correo de contacto ogarciav@unimagdalena.edu.co y logos de Minciencias y de la Universidad del Magdalena sin recolorear. Se omiten categoría y línea de investigación. El nombre y el rol de Jairo no se publican hasta que él lo indique.
- La versión de Python la elige Claude Code, en un entorno aislado del proyecto.
- No hay métrica de avance por fila («diligenciado por completo»). Las definiciones de filas y columnas vienen de un archivo de texto aparte; si no existen, «definición no disponible».
- Selección de varios valores en tipo de fuente y metodología. En nivel de evidencia, varios valores se eligen con el control único de la leyenda (FR-002-11).
- La advertencia de enfoque diferencial cita la regla de la hoja Instrucciones (B14) y no agrega nada más.
- **Verificación cruzada** (COR-001): solo se comparan e informan las tablas comparables de total de estudios, evaluación de impacto y nivel de evidencia, cada una por el número inicial de su título. Las demás tablas de la hoja no se leen ni generan advertencias. Cada tabla se delimita y sus filas y columnas, incluida «Total estudios», se emparejan solo dentro de ella. «Coincide» exige comparar todos los valores esperados. Si algún valor comparado es distinto, «difiere». En los demás casos, incluida una comparación incompleta sin diferencias, «no verificable». Si no se compara todo, una advertencia indica lo no comparado y no pide cambios en la matriz. Lo no comparado nunca es 0.
- Una tabla comparable se reconoce por una celda que empieza por un número seguido de punto y contiene su frase propia, sin distinguir mayúsculas. Si ninguna celda lo cumple, o lo cumple más de una, la tabla no se reconoce (F1, COR-004).
- Un valor de dimensión escrito como texto (por ejemplo, «1» como texto) es advertencia y no marca la dimensión, a diferencia del número 1 (P2). Cuando la hoja EGM difiere de la herramienta, la diferencia se explica primero por las filas con la misma intervención en principal y secundaria y, si persiste, por las filas con dimensión escrita como texto, que se listan (F2). Ambas en COR-004.
- **Estados de documento** (COR-002 y COR-003): cada documento queda en uno solo de estos estados: «En el mapa», «Empírico pendiente», «No empírico» o «Sin tipo de documento válido». «No empírico» no se lista como pendiente ni genera advertencia por esa razón. El rótulo es «Sin tipo de documento válido» y no «pendiente de codificación», que la skill `contrato-matriz` conserva. Si el tipo de documento no tiene lista, todo valor no vacío distinto del valor ancla es no empírico, y la advertencia de la columna indica los valores presentes. Tipo de documento, tipo de fuente y metodología sin lista generan advertencia y usan los valores presentes. No hay métrica de avance por fila.
- **Fila vacía**: todas sus celdas están vacías. Una fila con `N°` vacío y con contenido no es vacía: se procesa con advertencia y se identifica por su número de fila del archivo (F5a, COR-004).
- **Filtros y sesión** (F3 y F7, COR-005): un filtro está activo solo cuando se aplica con «Actualizar vista»; hay un solo «Actualizar vista» y un solo «Restablecer», comunes a mapa y tablero, y con selecciones sin aplicar ambas vistas muestran lo último aplicado. Un estudio con la celda vacía en el campo filtrado no cumple el filtro. No hay vista tabular de la matriz. La sesión empieza al cargar el archivo y termina al descartarlo, al cerrar la pestaña o tras 45 minutos de inactividad; actividad es cualquier interacción con la página. (Precisado el 21-nov-2026: ver «Decisiones del 21-nov-2026», que prevalecen.)
- **Interno**: la tabla 3 de la hoja EGM no es comparable: la herramienta no la compara ni la calcula, y la interfaz no muestra esa comparación. La discrepancia es grupo B de la regla 9 de `CLAUDE.md`: queda en los registros internos del proyecto (`docs/informes/interno-tabla3-hoja-egm.md`, informes para Jairo y `hallazgos-matriz-para-equipo.md`) y se comunica al equipo solo en el informe final de fase, como nota del grupo B, nunca en la interfaz ni en otro texto (21-nov-2026). No se anota en los registros de ejecución de la herramienta (F6d, COR-004). Los N.º 2 y 7 se muestran «Sin clasificar».

## Decisiones del 3-nov-2026
- **Orden del archivo** (P1, COR-004): las dimensiones van en el orden de sus columnas. Las intervenciones y los niveles van en el orden de su lista de validación, y las que solo están en la lista de secundaria van al final. No se toma el orden de la hoja EGM.
- **Año no reconocido** (P3, COR-004): un año que no sea número entero es advertencia. El documento se cuenta, no cumple un filtro de año activo y en la composición por año aparece como «año no reconocido», separado de «sin diligenciar».
- Los registros de la herramienta no contienen el nombre del archivo cargado (F8, COR-004).
- Una carga nueva reemplaza a la anterior dentro de la sesión (F9, COR-004). Si la carga nueva tiene un error de contrato, se limpia todo y se muestra un mensaje de error con lo esperado y lo encontrado, sin el nombre del archivo ni filas de datos (21-nov-2026); una carga con solo advertencias o notas se acepta (COR-005).
- **Nivel de evidencia** (H-08, COR-005, provisional): la leyenda agrega «Sin nivel» como una entrada más cuando existan esos estudios; un nivel «No aplica…» se trata como «Sin nivel». (Ampliado el 21-nov-2026: ver «Decisiones del 21-nov-2026».)
- **Intervención secundaria** (H-16, COR-005): la fila con la principal vacía y la secundaria diligenciada queda en $M$ por su secundaria, sin advertencia.
- **Colofón** (H-20, COR-005): «Matriz: <nombre del archivo tal como llegó>, leída el <fecha de la carga>, <n> documentos»; no se deduce ninguna versión. Mostrar el nombre en pantalla no es un registro.
- **Límite de tamaño** (COR-008): 15 MiB = 15 728 640 bytes, fijo (21-nov-2026). Un archivo de ese tamaño se acepta y uno mayor se rechaza. El valor vive solo en NFR-000-19; los demás textos remiten a él.

## Decisiones del 21-nov-2026 (COR-009)
- Un filtro está activo solo si, aplicado con «Actualizar vista», deja fuera algún valor de su control o estrecha el rango de años.
- Ocultar o mostrar una entrada de la leyenda de nivel espera a «Actualizar vista».
- «Restablecer» aplica de inmediato la vista sin filtros; FR-002-18 queda aprobado y lo cumple «Restablecer».
- En las cifras de documentos del tablero, los documentos no empíricos se tratan como «Sin nivel» y solo salen al ocultar esa entrada. La entrada «Sin nivel» aparece también cuando solo hay documentos no empíricos sin nivel (Q8).
- Tras una carga nueva válida se borran todos los filtros aplicados.
- El mensaje de error de contrato muestra lo esperado y lo encontrado (hoja, encabezado, valor ancla esperado y valores encontrados), sin el nombre del archivo ni filas de datos, también en la primera carga.
- Si una carga nueva se rechaza antes de leerla, por tipo o tamaño, se conservan la matriz anterior y sus resultados, con el mensaje del rechazo.
- Una carga nueva con error de contrato limpia todo y termina la sesión; la siguiente carga válida empieza otra (Q7).
- Tiempo de inactividad: 45 minutos, fijo.
- La huella SHA-256 es un control del proceso del proyecto, no una función de la herramienta (Q1).
- Ningún valor de lista que empiece por «No aplica», o varios tipos de documento que empiecen por «Estudio empírico»: advertencia y seguir (Q4). Bloque de dimensiones degenerado o con columna de rol dentro: advertencia y seguir (Q6). La lista cerrada de errores de contrato del 2-nov-2026 no cambia.
- Una diferencia con la hoja EGM se explica también por filas con espacios en los extremos de un valor (Q2).
- FR-003-21 (empíricos pendientes en el tablero) es obligatorio (Q5).
- Colofón: nombre completo del grupo (Organización y Empresa, GIOE), Santa Marta y director del grupo Óscar García Vargas, confirmados por Jairo (Q3).
- Inconsistencias de la matriz: grupos A y B, solo en el informe final de fase (regla 9 de `CLAUDE.md`). La tabla 3 de la hoja EGM es grupo B.
- La Fase 3 usa `docs/planes/_plantilla-plan-spec.md`, un plan por spec; `_plantilla-plan.md` se eliminó (Q10). El constructor de fixtures va en la preparación del plan 001 y cada NFR-000 en los planes cuyas historias afecta (Q11). Los commits los hace Jairo (Q9).
- COR-005 ratificada.

## Decisiones del 21-nov-2026 (COR-010)
- Cuando solo hay documentos no empíricos sin nivel, la entrada «Sin nivel» aparece en la leyenda del mapa y en la del tablero, porque el control es el mismo, y en el mapa cuenta 0 estudios (H-59).
- La observación de la tabla 3 de la hoja EGM sale del contrato y queda en `docs/informes/interno-tabla3-hoja-egm.md`. El contrato solo dice que esa tabla no es comparable, no se lee ni se compara (§7), sin describir la discrepancia (H-69).
- En los planes, «plan» designa la unidad de plan y «módulo», la de la arquitectura; en cada historia, las pruebas van antes que su implementación (H-62).

## Decisiones del 21-nov-2026 (después de cerrar la Fase 1)
- Jairo aprueba la Fase 1 y pide seguir con la arquitectura.
- Colofón: nada de la Universidad del Magdalena (logos ni nombres) se publica hasta que Jairo tenga autorización. Los specs no cambian; cada bloque institucional del colofón se activa por configuración y viene apagado por defecto.
- Stack web: lo propone el ADR-003; Jairo lo aprueba.
- `prompts/RETOMAR_2026-11-21.md` se eliminó (cumplió su propósito; cierra H-72).

## Decisiones del 21-nov-2026 (Fase 2, arquitectura)
- ADR-001 a ADR-005 aceptados. Stack: FastAPI + Jinja2 + htmx, HTML y CSS propios, Uvicorn local (ADR-003).
- Exportación: mapa en PNG con SVG adicional; conteos en .xlsx con filtros activos, archivo y fecha de lectura.
- Recargar la página no termina la sesión (10 s de gracia); cerrar la pestaña sí.
- Definiciones de filas y columnas: texto UTF-8 junto a la instalación, leído al arrancar.
- **Límite de contenido descomprimido** (COR-011): 256 MiB = 268 435 456 bytes, fijo, sobre la suma de los tamaños descomprimidos que declara el paquete (21-nov-2026). Un libro con ese contenido declarado se acepta y uno mayor se rechaza antes de leerlo, como archivo que no se puede abrir, con un mensaje propio sin cifras («El contenido del libro es demasiado grande para abrirlo»); si había una matriz cargada, se conservan ella y sus resultados. No es error de contrato. El valor vive solo en NFR-000-19; los demás textos remiten a él.
- Colofón: seis bloques apagados por defecto (grupo, código Minciencias, contacto, los dos logos, línea «Herramienta»); «Datos» y la referencia a 3ie siempre visibles (ADR-005).
- ADR-002, punto 2 (filas que abarcan las fórmulas) aprobado.
- El despliegue posterior a la demostración lo decide el equipo (NC-ADR004-1, abierto a propósito).

## Decisiones del 21-nov-2026 (Fase 2, interfaz)
- Colofón: hasta la autorización solo quedan visibles «Datos» y la referencia a 3ie; también se apagan por defecto «Proyecto», «Semillero» y «Equipo» (NC-INT-1; modifica ADR-005).
- Los estudios empíricos pendientes sin nivel siguen fuera de las cifras de documentos del tablero mientras el filtro de nivel esté activo; no se tratan como «Sin nivel» (NC-INT-2; sin corrección de spec).
- Título de la cabecera: «Evidencias sobre medios de vida», sin la palabra «brechas» (NC-INT-3).
- Exportación del mapa: M20 entrega el SVG y M19 (cliente) lo convierte en PNG en el navegador (NC-INT-4).
- Jairo autorizó al arquitecto a completar las listas «Cubre» de M08 (FR-001-12) y M09 (NFR-000-02) en el borrador de la arquitectura.

## Decisiones del 21-nov-2026 (cierre de la Fase 2)
- Jairo ratifica los cambios del 21-nov-2026 a ADR-003 (puntos 6 y 7) y ADR-005 (nota de revisión), hechos después de quedar «aceptados» (F2-04).
- **Regla desde el 21-nov-2026**: un ADR en estado «aceptado» solo cambia por una corrección `COR-NNN` (flujo de la regla 11) o por un ADR nuevo que lo reemplace.
- COR-012 recoge los hallazgos F2-01 a F2-11 de `docs/informes/conformidad-fase-2-2026-11-21.md`. Jairo aprueba `arquitectura.md` después de aplicarla y verificarla.

## Decisiones del 22-nov-2026
- COR-012 aprobada: opción A en todos los hallazgos (F2-01 a F2-03 y F2-05 a F2-11) y P1 (a): las tipografías se sirven localmente (ADR-003, punto 6), sin Google Fonts. Verificada en `docs/informes/conformidad-fase-2-cierre-2026-11-22.md`.
- Jairo aprueba `docs/arquitectura/arquitectura.md`: la Fase 2 queda cerrada. Empieza la Fase 3 (un plan por spec, con `_plantilla-plan-spec.md`).
- F2-13 (fecha de la nota de revisión de ADR-003) y F2-14 (`pie-de-pagina.md` da por confirmados todos los datos aunque «Herramienta» sigue [POR CONFIRMAR]) van a COR-013, junto con lo que aparezca al preparar el plan 001.

## Decisiones del 22-nov-2026 (Fase 3, planes)
- Jairo autoriza las descargas del plan 001 (F3-09): dependencias de Python en `.venv` (FastAPI, Jinja2, Uvicorn, openpyxl, pytest, hypothesis, ruff, mypy y las que fije `pyproject.toml`), el navegador de pruebas de Playwright, axe-core, htmx y las tipografías servidas localmente. Nada de eso toca `data/raw/`.
- Las correcciones de los planes y pendientes (F3-01 a F3-06, F3-10 a F3-17, O-1 a O-4, F2-13, F2-14) van en una sola COR-013, antes de aprobar los planes.
- Los NC de los planes (NC-P001-*, NC-P002-*, NC-P003-*) los decide Jairo uno a uno.
- Alcance: se ejecuta el camino crítico de `docs/planes/README.md` y se revisa el avance al cerrar el hito N1 del plan 001; ahí Jairo decide si recorta.

- NC de los planes, decididos por Jairo el 22-nov-2026 (todos con la propuesta del plan):
  - NC-P001-1: mientras no exista el mapa, una carga aceptada lleva a una vista provisional `/vista/resultado` (verificación, advertencias y cifras básicas); con el plan 002 la carga lleva al mapa.
  - NC-P001-2: la revisión visual de SC-000-11 con los logos encendidos espera a que Jairo tenga la autorización y los archivos; no bloquea la demostración.
  - NC-P002-1: las pruebas de US-001-4.10 y US-001-5.4 a 5.6 viven solo en el plan 002.
  - NC-P002-2: revisión manual con NVDA en Windows.
  - NC-P002-3: en el archivo de definiciones, cada encabezado es una línea que empieza por «# » seguida del nombre exacto; el texto va hasta el siguiente encabezado.
  - NC-P002-4: una referencia con DOI y sin URL enlaza a https://doi.org/ seguido del DOI; una URL escrita se enlaza tal cual.
  - NC-P002-5: los valores presentes de un filtro sin lista salen en el orden de su primera aparición en el archivo.
  - NC-P003-1: la conclusión 3 toma como base los estudios del mapa y muestra «sin diligenciar» como quinta categoría, para que la suma dé el total (requiere ajustar FR-003-07 por COR-013).
  - NC-P003-2: cada cifra de celdas lleva la lista de cruces y los N.º de los estudios que los ocupan; para las celdas sin estudios, los estudios revisados.
  - NC-P003-3: conclusión 4 según la propuesta del plan (agrupación por el conjunto de dimensiones de cada estudio; «nunca juntas» = pares con estudios propios y ninguno en común; dimensiones sin estudios, aparte).
  - NC-P003-4: en la conclusión 6, un campo de texto vacío muestra el rótulo «sin diligenciar», sin otro texto.
  - NC-P003-5: Jairo coordina la comprobación manual de SC-003-05 con la matriz vigente y el resultado se registra en el informe de la fase.

- COR-013 aprobada (22-nov-2026): opción A, P1 (a) y P2 (a). ADR-003 punto 2 se aclara: los controles son elementos reales de HTML que htmx envía con la ficha de sesión, y la herramienta necesita el guion activo (sin aviso para navegador sin guion). Las «cifras básicas» de la vista provisional `/vista/resultado` son las de la cabecera corrida. FR-003-07 pasa a cinco categorías sobre los estudios del mapa (NC-P003-1). El constructor es `tests/constructor.py` (M23) en todos los documentos. Los estados de `trazabilidad.md` pasan a «diseñado» y la regla de quién cambia cada estado queda escrita en `trazabilidad.md`.
- COR-013 verificada (22-nov-2026): conforme, 0 NC, 6 observaciones (`docs/informes/conformidad-cor-013-2026-11-22.md`).
- Planes 001, 002 y 003 aprobados por Jairo (22-nov-2026). Las 89 filas de `trazabilidad.md` pasan a «planificado». Se ejecutan uno a la vez: 001 → 002 → 003.
- Observaciones de la auditoría de COR-013 (22-nov-2026): OBS-2 a OBS-6 van en una COR-014 pequeña antes del plan 001. OBS-1 («especificado» en el párrafo de estados) queda como está.
- COR-014 aprobada (22-nov-2026): OBS-2 A, OBS-3 B, OBS-4 A, OBS-5 A, OBS-6 B y P1 (a). `GET /vista/resultado` pasa a ser la ruta del mapa en el plan 002 (R-2 y NC-P001-1); la recuperación de la sesión (`GET /`, E9) siempre abre el mapa. Los tres hallazgos extra (README de planes, regla de `data/raw/` y columna «Tarea» en la plantilla) van en una COR-015 aparte.
- COR-015 aprobada (22-nov-2026): punto 1 A, P1 (a), punto 2 B, punto 3 B y P2 (a). El `implementador` (paso 2) y la skill `plan-modulo` (paso 4) dejan de actualizar la columna «Tarea» de `trazabilidad.md`: solo anotan «Prueba», y el estado `implementado` se pone en la tarea de cierre del plan. Una sola auditoría del `verificador` cubre COR-014 y COR-015 antes del plan 001. La estructura de pruebas de `calidad-python/SKILL.md:41` y la marca `raw` en los planes 002 y 003 van en una COR-016 aparte.
- COR-016 aprobada (22-nov-2026): punto 1 B, punto 2 A, punto 3 A, P1 (a), P2 (a) y P3 (a). La skill `calidad-python` se alinea con `CLAUDE.md` y la arquitectura: estructura de pruebas con `constructor.py` y `navegador/`, marcas `raw` y `navegador` por comportamiento, núcleo sin E/S (solo `egm.libro` usa la biblioteca de lectura), errores de contrato como valor `FalloContrato` (texto en `egm.textos`) y `load_workbook` sobre bytes. El árbol del plan 003 suma `tests/navegador/`. Una sola auditoría del `verificador` cubre COR-014, COR-015 y COR-016 antes del plan 001; `planes/README.md` no se toca (dice «COR-014 y COR-015») y el alcance conjunto queda en el informe y aquí.
- COR-014, COR-015 y COR-016 verificadas (22-nov-2026): conforme, 0 NC, 5 observaciones no bloqueantes (`docs/informes/conformidad-cor-014-016-2026-11-22.md`). Quedan abiertos NC-ARQ-1 (se resuelve en T-001-09) y el uso previsto de la marca `raw` (no bloquea). Siguiente: Fase 4, plan 001.

## Pendientes de Jairo (no resolver por cuenta propia)
- Ninguno a 21-nov-2026.
