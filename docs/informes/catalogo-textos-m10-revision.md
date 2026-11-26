# Catálogo de textos de M10 — tabla para revisión (T-001-93)

Generada desde `egm.textos.CATALOGO`. Total: 97 textos.

| # | Código | Texto |
|---|---|---|
| 1 | `rechazo.tipo` | No se pudo cargar el archivo. El archivo elegido no es un archivo de Excel (.xlsx) que la herramienta pueda abrir, o está dañado. No se leyó y no se muestra ningún resultado. Elija la matriz bibliográfica en formato .xlsx. |
| 2 | `rechazo.tamano` | No se pudo cargar el archivo. El archivo pesa más de 15 MB (15 728 640 bytes), el máximo que admite la herramienta. No se leyó y no se muestra ningún resultado de ese archivo. |
| 3 | `rechazo.contenido` | No se pudo cargar el archivo. El contenido del libro es demasiado grande para abrirlo. No se leyó y no se muestra ningún resultado de ese archivo. |
| 4 | `advertencia.ref.numero` | N.º %(numero)s |
| 5 | `advertencia.ref.fila` | Fila %(fila)s |
| 6 | `advertencia.ref.columna` | , columna «%(columna)s» |
| 7 | `advertencia.ref.valor` | , valor «%(valor)s» |
| 8 | `advertencia.ref.cierre` | :  |
| 9 | `advertencia.valor_fuera_de_lista` | el valor no está en la lista de esa columna. La herramienta no lo cuenta y no lo corrige. |
| 10 | `advertencia.espacios_en_los_extremos` | el valor trae espacios al comienzo o al final. La herramienta los ignora al compararlo y no modifica la matriz. |
| 11 | `advertencia.dimension_valor_invalido.texto` | el número está escrito como texto y no como número. No marca la dimensión. |
| 12 | `advertencia.dimension_valor_invalido.fuera` | el valor no es 1 ni 0. No marca la dimensión. |
| 13 | `advertencia.anio_no_reconocido` | el año no se reconoce como número. El documento se cuenta igual y su año se muestra como año no reconocido. |
| 14 | `advertencia.numero_vacio` | la celda del N.º está vacía y la fila tiene contenido. El documento se lee y se identifica por su número de fila. |
| 15 | `advertencia.numero_repetido.una` | este N.º ya aparece en la fila %(anteriores)s. Este documento, en la fila %(fila)s, se lee aparte y se identifica también por su número de fila. |
| 16 | `advertencia.numero_repetido.varias` | este N.º ya aparece en las filas %(anteriores)s. Este documento, en la fila %(fila)s, se lee aparte y se identifica también por su número de fila. |
| 17 | `advertencia.principal_igual_secundaria` | la intervención «%(intervencion)s» está en la principal y también en la secundaria (columna «%(secundaria)s»). La hoja EGM la cuenta dos veces y esta herramienta, una. |
| 18 | `advertencia.no_empirico_con_intervencion` | el documento es de tipo «%(tipo)s» y trae una intervención. No es un estudio empírico, así que no cuenta en el mapa. |
| 19 | `advertencia.no_empirico_con_intervencion.sin_tipo` | el documento no es un estudio empírico y trae una intervención. No cuenta en el mapa. |
| 20 | `advertencia.tipo_documento_fuera_de_lista` | el tipo de documento no está en la lista de esa columna. El documento se cuenta entre los leídos, queda sin tipo válido y no cuenta como estudio empírico. |
| 21 | `advertencia.enfoque_sin_clasificar` | no empieza por Sí, No o Parcial, como pide la hoja Instrucciones. Queda como «Sin clasificar». |
| 22 | `advertencia.bloque_sin_dimensiones.vacio` | En la hoja «Matriz bibliográfica» no hay columnas de dimensiones entre las dos columnas que delimitan el bloque. Ningún estudio entra al mapa y los estudios empíricos quedan pendientes. |
| 23 | `advertencia.bloque_sin_dimensiones.invertido` | En la hoja «Matriz bibliográfica», la columna que cierra el bloque de dimensiones está antes de la que lo inicia, así que el bloque no tiene dimensiones. Ningún estudio entra al mapa y los estudios empíricos quedan pendientes. |
| 24 | `advertencia.rol_dentro_del_bloque` | La columna «%(columna)s» está dentro del bloque de dimensiones, pero es una columna propia de la matriz. La herramienta la lee con su función y no como dimensión. |
| 25 | `advertencia.lista_1_0_fuera_del_bloque` | La columna «%(columna)s» está fuera del bloque de dimensiones y tiene lista de valores 1 y 0. La herramienta no la toma como dimensión. |
| 26 | `advertencia.dimension_sin_lista_1_0` | La columna «%(columna)s», dentro del bloque de dimensiones, no tiene la lista de valores 1 y 0. La herramienta la toma como dimensión de todos modos. |
| 27 | `advertencia.lista_sin_no_aplica` | La lista de la columna «%(columna)s» no tiene ningún valor que empiece por «%(valor)s». La herramienta toma todos sus valores como categorías. |
| 28 | `advertencia.varios_empiricos` | La lista de la columna «%(columna)s» tiene más de un valor que empieza por «Estudio empírico»: %(valores)s. La herramienta toma todos como estudio empírico. |
| 29 | `advertencia.sin_ancla_evaluacion_impacto` | La lista de la columna «%(columna)s» no tiene el valor «%(valor)s». La herramienta calcula el mapa, pero lo que depende de ese nivel queda como no disponible. |
| 30 | `advertencia.sin_ancla_evaluacion_impacto.niveles` |  Niveles de la lista: %(niveles)s. |
| 31 | `advertencia.columna_sin_lista` | La columna «%(columna)s» no tiene lista de valores. La herramienta toma los valores presentes en la matriz: %(valores)s. |
| 32 | `nota.columnas_no_usadas` | Columnas no usadas: %(columnas)s. |
| 33 | `error.inicio` | No se pudo leer la matriz. |
| 34 | `error.hoja_ausente` | Se esperaba la hoja %(esperado)s, y %(encontrado)s. |
| 35 | `error.encabezado_ausente` | Se esperaba la columna %(esperado)s, y %(encontrado)s. |
| 36 | `error.encabezado_ausente.varios` | Se esperaban las columnas %(esperado)s, y %(encontrado)s. |
| 37 | `error.ancla_empirica_ausente` | Se esperaba un valor que empiece por %(esperado)s en la lista de la columna de tipo de documento, y %(encontrado)s. |
| 38 | `error.lista_obligatoria_ausente` | Se esperaba una lista de valores en la columna %(esperado)s, y %(encontrado)s. |
| 39 | `error.lista_obligatoria_ausente.varios` | Se esperaba una lista de valores en cada una de las columnas %(esperado)s, y %(encontrado)s. |
| 40 | `error.encontrado.ninguno` | no se encontró |
| 41 | `error.encontrado.ninguno.varios` | no se encontraron |
| 42 | `error.encontrado.uno` | se encontró: %(valores)s |
| 43 | `error.encontrado.varios` | se encontraron: %(valores)s |
| 44 | `error.cierre` | No se muestra ninguna cifra. Revise que el archivo sea la matriz bibliográfica del proyecto y vuelva a cargarlo. |
| 45 | `advertencia.hoja_egm_ausente` | El archivo no trae la hoja «%(hoja)s». Los conteos no se pueden contrastar con ella; el mapa se calcula igual desde la hoja «Matriz bibliográfica». |
| 46 | `advertencia.tabla_no_reconocida` | En la hoja «%(hoja)s» no se reconoció una única tabla cuyo título tenga un número y la frase «%(frase)s». Esa tabla no se contrasta con los conteos. |
| 47 | `advertencia.comparacion_incompleta.sin_pareja` | Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudieron comparar %(faltantes)s valores. Sin pareja: %(nombres)s. Un valor que falta no se toma como cero. |
| 48 | `advertencia.comparacion_incompleta.sin_numero.uno` | Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudo comparar 1 valor, porque la hoja no trae un número guardado en esa celda. Un valor que falta no se toma como cero. |
| 49 | `advertencia.comparacion_incompleta.sin_numero.varios` | Tabla %(tabla)s de la hoja «%(hoja)s»: no se pudieron comparar %(faltantes)s valores, porque la hoja no trae un número guardado en esas celdas. Un valor que falta no se toma como cero. |
| 50 | `advertencia.tabla_difiere.uno` | Tabla %(tabla)s de la hoja «%(hoja)s»: 1 valor difiere del conteo de esta herramienta. |
| 51 | `advertencia.tabla_difiere.varios` | Tabla %(tabla)s de la hoja «%(hoja)s»: %(celdas)s valores difieren de los conteos de esta herramienta. |
| 52 | `advertencia.hoja_abarca_menos_filas` | Las fórmulas de la hoja «%(hoja)s» abarcan de la fila %(desde)s a la fila %(hasta)s de la hoja «Matriz bibliográfica», y la herramienta leyó hasta la fila %(leida)s. La comparación se hace solo con las filas que abarca la hoja. |
| 53 | `verificacion.coincide` | Los conteos coinciden con la hoja EGM del archivo. |
| 54 | `verificacion.difiere` | Los conteos difieren de la hoja EGM en la tabla %(tabla)s: %(celdas)s. |
| 55 | `verificacion.sin_causa` | No se identificó la causa de la diferencia en %(celdas)s. |
| 56 | `verificacion.celda` | «%(fila)s» con «%(columna)s» |
| 57 | `verificacion.mas_celdas` | %(celdas)s y otras %(cuantas)s celdas |
| 58 | `verificacion.causa.principal_igual_secundaria.una` | Causa conocida: %(sujeto)s tiene la misma intervención como principal y como secundaria; la hoja lo cuenta dos veces y esta herramienta, una. |
| 59 | `verificacion.causa.principal_igual_secundaria.varias` | Causa conocida: %(sujeto)s tienen la misma intervención como principal y como secundaria; la hoja los cuenta dos veces y esta herramienta, una. |
| 60 | `verificacion.causa.dimension_valor_invalido.una` | Causa conocida: %(sujeto)s tiene una dimensión con el número 1 escrito como texto; la hoja lo cuenta y esta herramienta, no. |
| 61 | `verificacion.causa.dimension_valor_invalido.varias` | Causa conocida: %(sujeto)s tienen una dimensión con el número 1 escrito como texto; la hoja los cuenta y esta herramienta, no. |
| 62 | `verificacion.causa.espacios_en_los_extremos.una` | Causa conocida: %(sujeto)s tiene espacios al comienzo o al final de un valor; la hoja los toma en cuenta y esta herramienta los ignora. |
| 63 | `verificacion.causa.espacios_en_los_extremos.varias` | Causa conocida: %(sujeto)s tienen espacios al comienzo o al final de un valor; la hoja los toma en cuenta y esta herramienta los ignora. |
| 64 | `verificacion.sujeto.numero` | el N.º %(numero)s |
| 65 | `verificacion.sujeto.fila` | el documento de la fila %(fila)s |
| 66 | `verificacion.sujeto.varios` | los documentos %(filas)s |
| 67 | `verificacion.referencia.numero` | N.º %(numero)s |
| 68 | `verificacion.referencia.fila` | fila %(fila)s |
| 69 | `verificacion.tablas_verificadas` | Tablas verificadas: %(tablas)s. |
| 70 | `verificacion.parcial` | Una o más tablas no se pudieron contrastar por completo; las advertencias de lectura dicen por qué. |
| 71 | `verificacion.no_verificable.sin_valores` | No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo no trae guardados los resultados de esa hoja. Los conteos de esta herramienta se calculan directamente de la hoja «Matriz bibliográfica». |
| 72 | `verificacion.no_verificable.sin_hoja` | No se pudieron contrastar los conteos con la hoja EGM del archivo, porque el archivo no trae esa hoja. Los conteos de esta herramienta se calculan directamente de la hoja «Matriz bibliográfica». |
| 73 | `verificacion.no_verificable.sin_tablas` | No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en esa hoja no se reconocieron las tablas que se contrastan. Los conteos de esta herramienta se calculan directamente de la hoja «Matriz bibliográfica». |
| 74 | `verificacion.no_verificable.incompleta` | No se pudieron contrastar los conteos con la hoja EGM del archivo, porque en sus tablas faltan valores o categorías. Los conteos de esta herramienta se calculan directamente de la hoja «Matriz bibliográfica». |
| 75 | `mensaje.rechazo.titulo` | No se pudo cargar el archivo |
| 76 | `mensaje.e4.titulo` | No se pudo leer la matriz |
| 77 | `mensaje.e4.titulo.previa` | No se pudo leer la matriz y la sesión terminó |
| 78 | `mensaje.e4.borro_todo` | La herramienta borró todo: la matriz que tenía cargada y sus resultados ya no están disponibles. Para volver a verlos, cárguela otra vez. |
| 79 | `mensaje.sigue_disponible` | La matriz que tenía cargada sigue disponible con sus resultados: %(cabecera)s. |
| 80 | `mensaje.volver` | Volver al mapa |
| 81 | `carga.sin_nombre` | archivo sin nombre |
| 82 | `mensaje.problema` | No se pudo completar la operación. No se muestra ningún resultado nuevo. Vuelva a intentarlo. |
| 83 | `sesion.e7.aviso` | Su sesión se cerrará en %(minutos)s minutos por falta de actividad. Al cerrarse, la matriz deja de estar disponible. |
| 84 | `sesion.e7.tiempo` | Tiempo restante: |
| 85 | `sesion.e7.boton` | Seguir con la sesión |
| 86 | `sesion.e8.descarte` | Descartó el archivo. La sesión terminó y la herramienta no guarda ninguna copia del archivo ni de sus resultados. |
| 87 | `sesion.e8.inactividad` | La sesión terminó porque pasaron 45 minutos sin actividad. La herramienta no guarda ninguna copia del archivo. Para seguir, cargue de nuevo la matriz. |
| 88 | `sesion.e9.recuperando` | Recuperando su sesión. |
| 89 | `cabecera.sesion` | La sesión se cierra sola tras 45 minutos sin actividad. El archivo solo se lee: no se modifica ni se guarda. |
| 90 | `cabecera.corte` | Matriz: %(nombre)s, leída el %(fecha)s, %(n)s documentos |
| 91 | `resultado.titulo` | Resultado de la lectura |
| 92 | `avisos.advertencias.una` | 1 advertencia de lectura |
| 93 | `avisos.advertencias.varias` | %(n)s advertencias de lectura |
| 94 | `colofon.datos.rotulo` | Datos |
| 95 | `colofon.datos.sin_matriz` | Aún no se ha cargado ninguna matriz. |
| 96 | `colofon.referencia.rotulo` | Referencia de diseño |
| 97 | `colofon.referencia.texto` | International Initiative for Impact Evaluation (3ie). Building Peaceful Societies Evidence Gap Map (2019). Licencia CC BY-NC-SA 4.0. Se toma solo como referencia de diseño; no se reproduce su contenido. |
