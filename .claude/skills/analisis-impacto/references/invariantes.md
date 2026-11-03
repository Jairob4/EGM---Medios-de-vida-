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
- **Filtros y sesión** (F3 y F7, COR-005): un filtro está activo solo cuando se aplica con «Actualizar vista»; hay un solo «Actualizar vista» y un solo «Restablecer», comunes a mapa y tablero, y con selecciones sin aplicar ambas vistas muestran lo último aplicado. Un estudio con la celda vacía en el campo filtrado no cumple el filtro. No hay vista tabular de la matriz. La sesión empieza al cargar el archivo y termina al descartarlo, al cerrar la pestaña o tras 45 minutos de inactividad; actividad es cualquier interacción con la página.
- **Interno**: la tabla 3 de la hoja EGM no es comparable: la herramienta no la compara ni la calcula, y la interfaz no muestra esa comparación. La discrepancia queda solo en los registros internos del proyecto (apéndice B del contrato e informes para Jairo) y no se anota en los registros de ejecución de la herramienta (F6d, COR-004). Los N.º 2 y 7 se muestran «Sin clasificar».

## Decisiones del 3-nov-2026
- **Orden del archivo** (P1, COR-004): las dimensiones van en el orden de sus columnas. Las intervenciones y los niveles van en el orden de su lista de validación, y las que solo están en la lista de secundaria van al final. No se toma el orden de la hoja EGM.
- **Año no reconocido** (P3, COR-004): un año que no sea número entero es advertencia. El documento se cuenta, no cumple un filtro de año activo y en la composición por año aparece como «año no reconocido», separado de «sin diligenciar».
- Los registros de la herramienta no contienen el nombre del archivo cargado (F8, COR-004).
- Una carga nueva reemplaza a la anterior dentro de la sesión (F9, COR-004). Si la carga nueva tiene un error de contrato, se limpia todo y se muestra un mensaje de error sin el nombre del archivo ni datos de la matriz; una carga con solo advertencias o notas se acepta (COR-005).
- **Nivel de evidencia** (H-08, COR-005, provisional): la leyenda agrega «Sin nivel» como una entrada más cuando existan esos estudios; un nivel «No aplica…» se trata como «Sin nivel».
- **Intervención secundaria** (H-16, COR-005): la fila con la principal vacía y la secundaria diligenciada queda en $M$ por su secundaria, sin advertencia.
- **Colofón** (H-20, COR-005): «Matriz: <nombre del archivo tal como llegó>, leída el <fecha de la carga>, <n> documentos»; no se deduce ninguna versión. Mostrar el nombre en pantalla no es un registro.
- **Límite de tamaño** (COR-008): 15 MB. Un archivo de ese tamaño se acepta y uno mayor se rechaza. El valor vive solo en NFR-000-19; los demás textos remiten a él.

## Pendientes de Jairo (no resolver por cuenta propia)
- Si se comunica al equipo la observación de la tabla 3 (apéndice B del contrato).
- Límite de tamaño: si 15 MB son 15 000 000 o 15 728 640 bytes (`000-vision-alcance.md`, «Puntos abiertos»; COR-008).
- Tiempo de inactividad y límite de tamaño: si son fijos o configurables.
- Filtros (marcas abiertas en COR-005): si un filtro aplicado que no deja fuera nada cuenta como activo; si «Restablecer» aplica de inmediato (choca con P4, FR-002-18, propuesta sin aprobar); si la leyenda espera a «Actualizar vista»; si «Sin nivel» vale para los documentos no empíricos del tablero.
- Carga nueva: qué pasa con los filtros tras una carga válida; si el mensaje de error omite lo que nombran los errores de contrato y vale para la primera carga; qué pasa con la matriz anterior si la carga se rechaza por tipo o tamaño.
