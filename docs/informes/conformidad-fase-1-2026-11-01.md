# Informe de conformidad: fase 1 (specs)

**Fecha**: 2026-11-01  
**Auditor**: `verificador`, sin participación en la producción de lo auditado  
**Destinatario**: Jairo. Uso interno: la observación reservada de `contrato-datos.md` se referencia aquí sin
describirla.  
**Alcance**: `docs/specs/contrato-datos.md`, `000-vision-alcance.md`, `00{1,2,3}-*/spec.md`, `trazabilidad.md`,
`README.md` y estructura de carpetas.

Este informe reporta hallazgos; no corrige ninguno.

## 1. Resumen

| Medida | Resultado |
|---|---|
| Requisitos totales | 72 (56 FR + 16 NFR): FR-001: 19, FR-002: 17, FR-003: 20, NFR-000: 16 |
| Con fuente citada | 72 de 72 |
| Con escenario o SC vinculado | 72 de 72 |
| Cobertura completa | 62 de 72 |
| Cobertura parcial o no ejecutable | 10 de 72 (H-06, H-07, H-09) |
| Sin cubrir | 0 |
| Reglas inviolables de `CLAUDE.md` incumplidas | 0 |
| Apéndice A del contrato | Todos los valores coinciden con el recálculo |
| Hallazgos | 3 mayores, 5 medios, 15 menores |

**Dictamen.** Los controles de integridad pasan. Los tres hallazgos mayores están en la verificación cruzada
(contrato §7 y spec 001, historia 3): como están escritos, no dejan implementar esa historia sin decidir
primero algo que los specs no resuelven. Conviene cerrarlos antes de la arquitectura.

## 2. Comprobaciones superadas

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA-256 del xlsx | Coincide | `7E1714DE…52C3A1`, calculado con dos herramientas; igual a `contrato-datos.md:236` |
| `data/raw/` y `docs/fuentes/` sin modificar | Conforme | `git status` limpio para los archivos versionados; solo se agregó `Documento_tecnico_herramienta_EGM.pdf`, sin versionar |
| Apéndice A, recálculo propio | Conforme | Ver sección 3 |
| IDs únicos y sin huecos | Conforme | FR, NFR, SC y escenarios: 0 duplicados, 0 huecos |
| `trazabilidad.md` | Conforme | 72 filas en cada tabla; fuentes idénticas a las de los specs; estado `especificado`; 0 referencias inexistentes |
| Cifras de la lámina 7 | Ausentes | Ninguna mención ni uso; los esperados salen del apéndice A o de matrices sintéticas |
| Nombres de tecnología | Conforme | Solo Python como restricción citada (`000:59`) y su versión como punto abierto (`000:112`); `.xlsx` solo como nombre del archivo de datos (`contrato:235`) |
| Observación reservada | Conforme | Solo en el Apéndice B (`contrato:269-285`); no aparece en los demás specs, en `trazabilidad.md` ni en `README.md` |
| Sin cambios propuestos en la matriz | Conforme | Las propuestas de los `[NEEDS CLARIFICATION]` son del lado de la herramienta; la de `FR-002-08` es un texto aparte, no un cambio en la matriz |
| Textos de interfaz | Conforme | Los rótulos literales son neutros, sin tuteo ni preguntas; los resultados de búsqueda de formas verbales son tercera persona en escenarios |
| Sin código de aplicación | Conforme | `src/`, `app/` y `tests/` solo contienen `.gitkeep` |
| Estructura (T1 del prompt) | Conforme | Todas las carpetas existen; `README.md` y `.gitignore` presentes |
| Plantilla de spec | Conforme en estructura | Secciones y orden respetados; `**Estado**` bajo `**Created**`. Ver H-21 sobre orden de historias |
| Decisiones (a) a (f) reflejadas | Conforme | `contrato §1, §3.1, §7, §8`; `000:48`; FR-001-03, 04, 15, 16; FR-002-10, 12 a 15; FR-003-13 a 16; NFR-000-07 |
| Casos borde obligatorios | Conforme | Los 13 de `contrato-matriz` están en `contrato §9` |
| Citas de fuente | Las secciones citadas existen | Las que no dicen lo que el requisito afirma: H-05, H-11, H-12, H-13 |
| Extracción de texto de los PDF | Fiable | Mi reextracción da 10 y 22 páginas, y el mismo número de palabras que `general.txt` y `tecnico.txt` |
| `ruff`, `mypy`, `pytest --cov` | No aplica | No hay código en esta fase |

## 3. Recálculo del apéndice A

Hecho con un script propio, escrito sin consultar los del scratchpad, desde las celdas y con la matriz abierta
sin guardar. El hash se repitió al terminar.

| Medida | Contrato | Recálculo |
|---|---|---|
| Rangos de hoja | A1:Y36, A1:J41, A1:B20, A1:F17 | Iguales |
| Validaciones y fórmulas | Filas 2 a 36; filas 2 a 200 | Iguales; las 166 fórmulas de `EGM` usan solo 2:200 |
| Valores calculados | 0 | 0 numéricos en `EGM` |
| Listas | 6, 3, 6 + No aplica, 7, 4 + No aplica | Iguales |
| Dimensiones | 8, en ese orden | Iguales |
| $\lvert R\rvert$ | 27 (N.º 1 a 27, filas 2 a 28; 29 a 36 vacías) | Igual |
| Por tipo de documento | 9, 7, 4, 3, 3, 1 | Igual |
| $\lvert E\rvert$ | 7 (N.º 7, 10, 11, 13, 15, 16, 24) | Igual |
| $N$ | 1 (N.º 7) | Igual |
| Celdas en 1 | 6 de 48: 2 intervenciones × 3 dimensiones | Igual |
| $T_4$ | 1, 0, 0, 0 | Igual |
| $t(i)$ | 1 en dos intervenciones; 0 en las demás | Igual |
| Tipo de fuente | 6, 1, 0, 20 sin diligenciar | Igual |
| Metodología | 6, 1, 20 sin diligenciar | Igual |
| Años | 1992 a 2026 | Igual |
| Enfoque | 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar | Igual |

Los 25 encabezados coinciden literalmente, incluido el carácter de `N°` (U+00B0). En la v4 no hay valores fuera
de lista, filas con igual intervención en ambas columnas, `N°` repetidos ni dimensiones escritas como texto.
Tampoco encontré diferencias de datos con `referencia-v4.md`.

## 4. Contradicciones

### Mayores

**H-01. La comparación definida no puede producir el resultado que espera el escenario.**
`contrato-datos.md:189` manda comparar $T_1$ con el valor guardado en la hoja, y $T_1$ (`:135`) es la semántica
de la propia hoja, con la misma doble cuenta. Con una fila de igual intervención en ambas columnas, $T_1$ y la
hoja coinciden. Pero US-001-3.2 (`001:116-119`) espera «difiere», con las celdas y la explicación, y US-001-3.1
(`001:112`) excluye esas filas para obtener «coincide», lo que solo tiene sentido si se compara $S$. FR-001-14
dice «sus conteos» y FR-001-18 pide explicar esa diferencia. Ambas lecturas producen resultados opuestos.
Requisitos afectados: FR-001-14, FR-001-18, US-001-3.1, US-001-3.2.

**H-02. La columna «Total estudios» de la tabla de evaluación de impacto no tiene definición.**
`contrato-datos.md:187` la declara comparable, pero `:189` solo compara $T_1$, $T_2$, $t$ y $T_4$, y $t(i)$
(`:143`) no lleva la condición de nivel. En el archivo, `EGM!J16` sí la lleva (`$J$2:$J$200,"Evaluación de
impacto"`), y las otras cinco filas de esa columna también, como indica `doc. técnico §3.2`. Comparar con $t$
daría «difiere» en falso en cuanto exista un empírico con intervención de otro nivel. Requisitos afectados:
FR-001-14, US-001-3.1.

**H-03. No se define qué títulos identifican cada tabla de la hoja `EGM`.**
`contrato-datos.md:186` y FR-001-15 localizan las tablas «por su título», pero ni §7 ni el apéndice A dan esos
títulos o una regla para reconocerlos. Los de la v4 son `EGM!A4`, `A14` y `A34`. Dos títulos empiezan igual
(«De ellos, con…», `A14` y `A24`), y uno de ellos no es comparable, de modo que una regla laxa puede confundirlos.
US-001-3.5 y US-001-3.6 dependen de esta definición para distinguir «reconocida» de «no reconocida».

### Medios

**H-04. FR-001-12 pide más de lo que indica el contrato.**
`001:169` exige advertencia «con N.º, columna y valor» por **cada** caso borde. Pero `contrato:175` y `:218`
clasifican sin advertencia el enfoque sin prefijo, `contrato:225` trata las categorías agregadas «sin más
cambios», y los casos de archivo (`:219`, `:222`, `:224`) no tienen N.º ni columna. US-001-1.6 confirma que solo
«Si bien…» advierte. SC-001-04 mide «todos los tipos de advertencia», sin lista cerrada de tipos.

**H-05. Dos requisitos se apartan de la fuente citada sin registrarlo.**
- NFR-000-09 (`000:77`) cita `doc. técnico §4.2 RNF2`, que pide registrar la **huella** del archivo y la fecha
  de corte. El requisito pide nombre y fecha de lectura. `contrato:238` dice que el hash no es función de la
  herramienta, y eso no está en las decisiones (a) a (f) ni en las «Notas sobre las fuentes» (`000:115-118`).
- FR-001-19 (`001:176`) cita `doc. técnico §6.1`, cuyo principio 4 habla del $N$ de corte y de la fecha de la
  matriz; no del nombre del archivo ni de la fecha de lectura.

**H-06. SC-000-07 no se puede ejecutar.**
`000:96` prueba denominadores 99 y 100 con el interruptor encendido, pero ningún FR define qué porcentaje existe,
sobre qué denominador ni dónde aparece. `000:53` lo pone fuera de alcance y NFR-000-07 exige la capacidad. La parte
verificable hoy es la de la configuración por defecto.

**H-07. Cobertura parcial en cuatro FR: `trazabilidad.md` indica más de lo que el escenario comprueba.**

| Requisito | Vinculado a | Qué no se comprueba |
|---|---|---|
| FR-001-01 | US-001-3.5, SC-001-05 (`trazabilidad:102`) | US-001-3.5 mueve tablas de la hoja `EGM`. Ningún escenario reordena columnas ni hojas de la matriz |
| FR-002-11 | US-002-4.3 (`:131`) | Más de un valor dentro de un filtro: el escenario activa «un valor en cada filtro» |
| FR-002-16 | US-002-5.1, 5.2 (`:136`) | Que la **imagen** indique filtros, archivo y fecha; solo se pide para la tabla |
| FR-003-12 | SC-003-04 (`:149`) | Ese criterio revisa porcentajes, «brecha» y afirmaciones; no el uso de plantillas |

**H-08. La semántica de los filtros está incompleta.**
- `contrato:148-151` define la conjunción entre filtros, pero no qué pasa con varios valores dentro de uno, que
  FR-002-11 admite. SC-002-03 y SC-003-03 exigen un recálculo independiente que necesita esa definición.
- No se define cuándo un filtro está «activo», y de eso dependen el rótulo de FR-002-14 y «n de N».
- `002:171` saca del conjunto a quien tenga vacío el campo filtrado, y `002:175` admite estudios «sin nivel».
  Como el filtro y la leyenda son un solo control (FR-002-12), ocultar un nivel cualquiera también retira los
  «sin nivel», aunque nadie los haya ocultado. Ningún escenario lo cubre, y «sin nivel» no está en `contrato §9`
  ni en `001`.
- $S_\varphi$ se define sobre $E$, pero FR-003-14 recalcula también cifras de documentos. $n$ y $N$ de «n de N»
  no tienen definición formal; solo la frase de `003:163`.

### Menores

| ID | Hallazgo | Evidencia |
|---|---|---|
| H-10 | No hay regla para un `Año` no numérico; solo para el vacío. La v4 no tiene ninguno (27 enteros) | `contrato §4`, `§9`; `002:171`; FR-002-10 |
| H-11 | `doc. técnico §6.6`, paso 2, elimina tildes («Si bien» sería Sí); el contrato hace lo contrario, como pide la skill `contrato-matriz`. La regla es válida, pero la cita no la sustenta y falta en las notas de fuentes | `contrato:174`; FR-001-10; `000:115-118` |
| H-12 | La regla 10 afirma que el texto `"1"` no marca la dimensión y cita §9.2, que solo dice «se informa como advertencia» y que su tratamiento se documenta y contrasta | `contrato:87-88` |
| H-13 | «En el orden del archivo» no está en las fuentes citadas. Tampoco se aclara si es el de la validación o el de la hoja `EGM`; `doc. técnico §2.4` usa este último | FR-002-01; `contrato:72` |
| H-14 | Atribuidos a la decisión del 1-nov, pero no están en las decisiones (a) a (f) que recibí: ignorar columnas ajenas con aviso, admitir varios valores por filtro y calcular casillas desde el archivo. FR-003-02 se deduce de la decisión (a). Los otros dos deben confirmarse | `contrato:54-55`; FR-002-11; FR-003-02 |
| H-15 | La skill define fila vacía como columna A vacía; el contrato, como todas las celdas vacías, y cita §9.2, que no lo define. Además, los N.º 8 a 27 tienen cuatro campos, de modo que «solo con referencia» no los cubre literalmente: 14 filas no empíricas quedan sin estado definido | `contrato:73-75`, `:211`; `contrato-matriz`, regla 3; `doc. técnico §3.3` |
| H-16 | `Instrucciones!B20` exige «Tipo de intervención diligenciado». $I_r$ también admite principal vacía con secundaria diligenciada, y ese caso no está en §9 | `contrato:118-123`; FR-001-07 |
| H-17 | $S(i,j) \le T_1(i,j)$ falla si $T_1$ se restringe al rango de fórmulas, como manda §7, y hay filas fuera de él. SC-001-03 prueba invariantes con matrices al azar | `contrato:157`, `:189` |
| H-18 | Omisiones de fuente sin registrar en «Fuera de alcance»: acercar la vista (`doc. general §3`; `doc. técnico §4.1`, tabla 4), mapas derivados (RF3) y precondición $N_{min}$ con activación por umbral (`§6.2` a `§6.4`, `§12.2`) | `000:41-54` |
| H-19 | `estado §8` deja pendiente una decisión sobre la nota de la columna de enfoque (`estado §4`). No hay `[NEEDS CLARIFICATION]`, y US-003-2.4 muestra al equipo «1 sin clasificar (N.º 7)». La skill autoriza mostrar la categoría; falta registrar el pendiente | `000:107-113`; `003:70` |
| H-20 | NFR-000-12 toma la «versión de la matriz» del archivo, pero ninguna regla dice cómo obtenerla y SC-000-12 solo comprueba número y nombre del archivo | `000:80`, `:101`; `FR-001-19` |
| H-21 | Historias no ordenadas por importancia (002: P1, P2, P3, P2, P3; 003: P1, P2, P2, P1). US-002-4.7, US-003-3.4 y US-003-1.4 no se demuestran sin la otra feature, contra la regla 4 de `especificacion-srs` | `002:101`, `:142`; `003:119`, `:126`, `:34` |
| H-22 | Términos sin unificar: «aviso» y «advertencia» se usan sin distinción, y «casilla» y «celda» conviven, aunque la entidad es «Celda del mapa» | `contrato:54`, `:63`; `003:22`, `:184` |

## 5. Huecos

Son los de H-03, H-06, H-07 y H-08, más este:

**H-09 (menor). Cobertura parcial en otros cinco requisitos.**

| Requisito | Qué no se comprueba |
|---|---|
| FR-001-18 | Que el aviso aparezca **antes** de presentar resultados |
| FR-002-17, FR-003-20 | La presentación al equipo de un resultado «difiere»; solo se prueba «no verificable» (US-002-1.5, US-003-4.4) |
| FR-003-08 | «Nunca juntas»; US-003-2.5 solo prueba lo que aparece junto |
| NFR-000-06 | Categorías **renombradas** e intervenciones o niveles retirados; SC-000-06 prueba agregados y una dimensión retirada. Además, un ancla renombrada sigue abierta en `contrato:102` |

## 6. Excesos

**H-23 (menor). Elementos sin vínculo a requisito.**
- US-002-4.6 (quitar los filtros, `002:137`) no tiene FR que lo pida.
- SC-002-02 (máximo dos acciones) no tiene FR de origen.
- `trazabilidad.md` no vincula SC-001-01, SC-001-03, SC-002-01 a 05, SC-003-01, 02, 03 y 05. Varios cubren
  requisitos reales; por ejemplo, SC-001-02 también debería figurar en FR-001-02, cuya hoja faltante no prueba
  US-001-2.4, y SC-002-04 podría figurar en NFR-000-04.

No encontré componentes, código ni funciones fuera de alcance.

## 7. Observaciones sobre las fuentes

No son hallazgos contra los specs ni piden cambios en `docs/fuentes/`.

- `doc. técnico §6.2` dice $\lvert B\rvert = 34$. El recálculo da 42, igual que `doc. técnico §6.4`
  ($\delta = 6/48$) y US-003-2.1. El spec es correcto, pero esa diferencia no está registrada.
- El prompt fecha la versión técnica el 21-oct-2026; el PDF dice 20 de octubre de 2026, aunque contiene datos
  «al 21 de octubre». El nombre del archivo también difiere del prompt, como ya se sabía.
- NFR-000-04 y NFR-000-05 citan «prompt de la fase 1, T3», que no está en la tabla de fuentes válidas de ese
  prompt, aunque el mismo T3 los ordena.

## 8. `[NEEDS CLARIFICATION]` abiertos

Hay 9, y todos con redacción concreta.

| Ubicación | Asunto |
|---|---|
| `contrato-datos.md:102` | Qué hacer si una versión futura renombra un valor ancla |
| `contrato-datos.md:104` | Qué hacer si una columna categórica pierde su lista |
| `contrato-datos.md:285` | Destino de la discrepancia reservada del Apéndice B |
| `000-vision-alcance.md:109` | Cómo llega la matriz a la herramienta |
| `000-vision-alcance.md:110` | Quiénes consultan y dónde se publica |
| `000-vision-alcance.md:111` | Datos pendientes del colofón |
| `000-vision-alcance.md:112` | Versión de Python |
| `000-vision-alcance.md:113` | Métrica de avance por fila |
| `002-mapa-interactivo/spec.md:190` | Origen de las definiciones de filas y columnas |

Pendiente del prompt, no incumplimiento: `docs/informes/fase-1-resumen.md` (T6) todavía no existe, porque va
después de esta auditoría. Debe listar estos 9 puntos y los huecos abiertos.
