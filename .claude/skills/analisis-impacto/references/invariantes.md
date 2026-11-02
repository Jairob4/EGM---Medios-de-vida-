# Invariantes del sistema EGM

Lista de lo que ninguna corrección puede alterar. Se actualiza solo cuando Jairo toma una
decisión nueva, con su fecha; ni el analista ni el corrector la editan. Las reglas
permanentes están en `CLAUDE.md`; aquí se recogen las decisiones fechadas.

## Decisiones del 31-oct-2026
- Aplicación web. El análisis de datos y el tablero con filtros se implementan en Python.
- El módulo de aprendizaje no supervisado y la vista de red quedan fuera del alcance actual.
- El pie de página muestra información del grupo de investigación. Diseño no genérico, acorde con la formalidad académica.

## Decisiones del 1-nov-2026
- **Dimensiones**: columnas entre «Dimensiones evaluadas / propuestas» e «Indicadores o categorías analíticas», excluidos ambos. Una columna del bloque sin lista `1,0`, o con lista `1,0` fuera del bloque: advertencia, nunca error. Si falta uno de los dos encabezados que delimitan el bloque: error de contrato.
- **Hoja EGM**: solo verificación, nunca fuente. Tablas localizadas por título y filas por nombre, sin coordenadas fijas. Estados de verificación: «coincide», «difiere», «no verificable» (nombres fijados por Jairo el 2-nov-2026). Nunca produce error de contrato. `None` no es 0.
- **Porcentajes**: esta versión muestra solo conteos. Capacidad inactiva por defecto, con interruptor y `n_min = 100` configurables. Un porcentaje se muestra solo si el interruptor está encendido y el denominador de ese porcentaje cumple $n \ge n_{\min}$. El denominador nunca es el total de documentos.
- **Filtros**: los mismos cuatro en mapa y tablero (tipo de fuente, metodología, nivel de evidencia, año), con estado compartido. Con filtro activo: siempre visible, se muestra «n de N», una celda en 0 se rotula «ningún estudio registrado con los filtros activos» y nunca «brecha», y una conclusión con subconjunto vacío dice «ningún estudio cumple estos filtros».
- **Mapa**: el filtro por nivel de evidencia y el mostrar/ocultar de la leyenda son un solo control. El filtro de año es por rango.
- Los escenarios se redactan en términos generales; ningún spec menciona «v4» como requisito ni compara versiones; los esperados salen de la matriz real o de fixtures descritos; nunca de la lámina 7.

## Decisiones del 2-nov-2026
- **Errores de contrato posibles**: falta la hoja «Matriz bibliográfica»; falta un encabezado esperado; falta alguno de los dos delimitadores del bloque de dimensiones; falta el valor ancla de estudio empírico; una columna de intervenciones o nivel de evidencia pierde su lista de validación. Cualquier otra anomalía es advertencia o nota. La ausencia del ancla de evaluación de impacto es advertencia y la conclusión 2 queda «no disponible».
- Columnas ajenas fuera del bloque: se ignoran con nota informativa, salvo que tengan lista `1,0` (advertencia).
- **Carga de la matriz**: desde el navegador. El archivo vive solo durante la sesión; no se guarda en base de datos, disco del servidor ni registros. Cada sesión es independiente. El archivo cargado nunca se modifica.
- La primera versión es local, para la demostración. El despliegue es decisión futura del equipo.
- **Colofón**: código Minciencias COL0016423, correo de contacto ogarciav@unimagdalena.edu.co y logos de Minciencias y de la Universidad del Magdalena sin recolorear. Se omiten categoría y línea de investigación. El nombre y el rol de Jairo no se publican hasta que él lo indique.
- La versión de Python la elige Claude Code, en un entorno aislado del proyecto.
- No hay métrica de avance por fila («diligenciado por completo»). Las definiciones de filas y columnas vienen de un archivo de texto aparte; si no existen, «definición no disponible».
- Selección de varios valores en tipo de fuente y metodología.
- **Interno**: la discrepancia de la tabla 3 queda solo en registros internos y la interfaz no la muestra; los N.º 2 y 7 se muestran «Sin clasificar».

## Pendientes de Jairo (no resolver por cuenta propia)
- Si se comunica al equipo la observación de la tabla 3.
- H-08: estado «sin nivel» en el control único de la leyenda.
- H-16: intervención principal vacía con secundaria diligenciada.
- Regla de «versión de la matriz» (H-20), propuesta.
