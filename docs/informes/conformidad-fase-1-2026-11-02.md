# Informe de conformidad: fase 1 (specs), reauditoría

**Fecha**: 2026-11-02  
**Auditor**: `verificador`, sin participación en la producción de lo auditado  
**Destinatario**: Jairo. Uso interno: la observación reservada del apéndice B se referencia aquí sin describirla.  
**Alcance**: `docs/specs/contrato-datos.md`, `000-vision-alcance.md`, `00{1,2,3}-*/spec.md`, `trazabilidad.md`,
`.claude/skills/sistema-diseno-egm/references/pie-de-pagina.md` y `README.md`.  
**Punto de partida**: `conformidad-fase-1-2026-11-01.md` (H-01 a H-23), que no se modifica.

Este informe reporta hallazgos; no corrige ninguno. Las referencias `contrato:N`, `000:N`, `001:N`, `002:N`, `003:N`,
`traz:N` y `pie:N` son líneas de esos archivos.

## 1. Resumen

| Medida | Resultado |
|---|---|
| Requisitos totales | 84 (65 FR + 19 NFR): FR-001: 25, FR-002: 18, FR-003: 22, NFR-000: 19 |
| Otros identificadores | 35 SC (19, 5, 5, 6), 88 escenarios (37, 24, 27), 14 historias (4, 5, 5) |
| Unicidad y huecos | 0 duplicados, 0 huecos |
| Con fuente | 82 de 84; de ellos, FR-002-01 lleva además una propuesta sin fuente |
| Solo propuesta sin fuente, marcada | 2 de 84 (FR-001-24, FR-002-18) |
| Con escenario o SC vinculado | 84 de 84 |
| Cobertura completa | 79 de 84 |
| Cobertura parcial | 5 de 84 (H-30) |
| Sin cubrir | 0 |
| Reglas inviolables de `CLAUDE.md` incumplidas | 1: regla 3 (H-29), dato que se publicaría en el colofón |
| Apéndice A del contrato | Todos los valores coinciden con el recálculo |
| Hallazgos nuevos | 1 mayor, 6 medios, 11 menores (H-24 a H-41) |
| Estado de H-01 a H-23 | 18 cerrados, 5 cerrados con residuo (H-04, H-05, H-08, H-18, H-21) |

**Dictamen.** Las correcciones cumplen lo pedido: las 12 decisiones están reflejadas, los controles de integridad
pasan y ningún requisito quedó sin cubrir. No conviene aprobar la fase todavía: H-24 deja la verificación sin un
resultado definido en el caso que el contrato promete soportar (una categoría nueva en la matriz), y H-29 y H-25
afectan datos que se publican o se muestran. Los demás se resuelven con ajustes de texto o con su aprobación.

## 2. Comprobaciones superadas

| Comprobación | Resultado | Evidencia |
|---|---|---|
| SHA-256 de `data/raw/` | Coincide | `7E1714DE…52C3A1` antes y después de abrir la matriz, y con dos herramientas; igual a `contrato:324` |
| `data/raw/` y `docs/fuentes/` versionados | Sin cambios | `git diff HEAD` vacío. `Documento_tecnico_herramienta_EGM.pdf` sigue sin versionar, así que git no puede atestiguarlo |
| IDs y `trazabilidad.md` | Conforme | 84 filas en cada tabla; fuentes idénticas a las de los specs; 0 referencias inexistentes; todos los SC y escenarios enlazados; estado `especificado` |
| Lámina 7 | Conforme | Ninguna mención ni uso en el alcance. Los esperados salen del apéndice A o de matrices sintéticas |
| Regla 9 | Conforme | La observación reservada solo está en `contrato:360-382`. Búsqueda sin resultados en los demás specs, `trazabilidad.md`, `README.md` y `pie-de-pagina.md`. §7 y US-001-3.7 usan el rótulo que usted decidió |
| Nombres de tecnología | Conforme | Solo la restricción de Python (`000:62`) y la nota de versión (`000:134`). WCAG es una norma. `.xlsx` es el formato de entrada (`contrato:31`) y el nombre del archivo (`contrato:323`) |
| Sin cambios propuestos en la matriz | Conforme | Las propuestas son del lado de la herramienta |
| Textos de interfaz | Conforme | Rótulos literales neutros; sin tuteo ni preguntas |
| Sin código | Conforme | `src/`, `app/` y `tests/` solo contienen `.gitkeep`. `ruff`, `mypy` y `pytest` no aplican |
| Terminología | Conforme | 0 apariciones de «aviso» y «casilla» en el alcance. Ver H-34 sobre el efecto en «celda» |
| Casos borde obligatorios | Conforme | Los 13 de `contrato-matriz` están en `contrato:286-316` |
| Orden de historias | Conforme | 001: P1, P1, P1, P2; 002: P1, P2, P2, P3, P3; 003: P1, P1, P1, P2, P3 |

## 3. Recálculo del apéndice A

Script propio, escrito sin usar los del redactor, desde las celdas y sin guardar el libro.

| Medida | Contrato | Recálculo |
|---|---|---|
| Rangos de hoja | A1:Y36, A1:J41, A1:B20, A1:F17 | Iguales |
| Validaciones y fórmulas | Filas 2 a 36; filas 2 a 200 | Iguales; las 166 fórmulas de `EGM` usan solo 2:200 |
| Valores calculados | 0 | 0 numéricos |
| Listas | 6, 3, 6 + No aplica, 7, 4 + No aplica | Iguales |
| Dimensiones | 8, en ese orden | Iguales, y en el mismo orden en `EGM` fila 5 |
| $\lvert R\rvert$ | 27 (filas 2 a 28; 29 a 36 vacías) | Igual |
| Por tipo de documento | 9, 7, 4, 3, 3, 1 | Igual |
| $\lvert E\rvert$ | 7 (N.º 7, 10, 11, 13, 15, 16, 24) | Igual |
| $N$ | 1 (N.º 7) | Igual |
| $\lvert P\rvert$ | 6 (N.º 10, 11, 13, 15, 16, 24) | Igual |
| Estados de documento | 1, 6, 20, 0 | Igual |
| Celdas | 6 en 1 y 42 en 0, de 48 | Igual, con las mismas 2 × 3 |
| $T_4$ | 1, 0, 0, 0 | Igual |
| $t(i)$ | 1 en dos intervenciones; 0 en las demás | Igual |
| Tipo de fuente | 6, 1, 0, 20 sin diligenciar | Igual |
| Metodología | 6, 1, 20 sin diligenciar | Igual |
| Años | 1992 a 2026 (27 enteros) | Igual |
| Enfoque | 5 No, 2 Sin clasificar (N.º 2 y 7), 20 sin diligenciar; en $M$: 1 Sin clasificar | Igual |

Sin diferencias de datos con `referencia-v4.md`. Las afirmaciones de `contrato:365-367` también se comprueban en las
54 fórmulas del bloque correspondiente. El orden de intervenciones de la lista coincide con el de `EGM`
(`contrato:84`). El límite propuesto se compara con un archivo de 27 439 bytes, como dice `000:119`.

## 4. Decisiones del 2-nov-2026

| N.º | Decisión | Estado | Evidencia |
|---|---|---|---|
| 1 | Ancla renombrada | Conforme | `contrato:131-136`; FR-001-23; FR-003-22; US-001-2.9, 2.10; US-003-2.10 |
| 2 | Columna categórica sin lista | Conforme, con H-25 | `contrato:143-148`; FR-001-22; US-001-2.11, 2.12; US-002-4.9 |
| 3 | Columna ajena | Conforme | `contrato:62-64`, `:303-304`; FR-001-21; US-001-2.8; US-001-2.6 |
| 4 | Discrepancia interna | Conforme | `contrato:270-273`, `:373-377`, `:382`; FR-001-25; US-001-3.7 |
| 5 | N.º 2 y 7 | Conforme | `contrato:238-239`, `:379-380`; FR-001-10; US-001-2.14 |
| 6 | Carga y sesión | Conforme, con H-30, H-35 y H-36 | `contrato:28-34`; NFR-000-01, 17, 18, 19; FR-001-20; historia US-001-4; SC-000-17 a 19 |
| 6b | H-20: regla propuesta | Conforme, con H-32 | `000:84`, `pie:23-26` |
| 7 | Primera versión local | Conforme | `000:67`, `:124` |
| 8 | Colofón | Conforme, con H-29 y H-30 | NFR-000-11; SC-000-11; `pie:15`, `:21`, `:32`, `:34-42`. `docs/interfaz/logos/` aún no existe, de modo que SC-000-11 no se podrá ejecutar hasta recibirlos |
| 9 | Versión de Python | Conforme en specs | `000:134`. Falta registrarla en el resumen: ver sección 11 |
| 10 | Sin métrica por fila | Conforme, con H-37 | `000:50`, `:135`; FR-003-21; US-003-1.5 |
| 11 | Definiciones | Conforme, con H-30 | FR-002-08; `000:128` |
| 12 | Varios valores | Conforme | FR-002-11; US-002-4.8; `contrato:202-203` |

## 5. Cambios por iniciativa del redactor

| Cambio | Juicio | Razón |
|---|---|---|
| Regla de títulos (`contrato:251-254`) | **Correcta contra el archivo; falta marcarla** | Sin el número, la frase coincide en A14 y A36, y en A34 y A35; las tablas 2 y 4 no se reconocerían, como dijo el redactor. Con el número queda una sola celda por frase: A4, A14 y A34. La columna J y el título A24 no interfieren. No tiene marca de propuesta (H-27) y no resuelve el alcance de cada tabla (H-24) |
| «Registros internos» como registros del proyecto (`contrato:375-377`) | **Razonable; pida confirmación** | Es la única lectura compatible con NFR-000-17 y con la skill, que pide registrarla como discrepancia conocida. Pero es una interpretación, y agrega «no la calcula», y se cita como decisión suya (H-27) |
| Historias reordenadas | **Válido** | ID conservados, sin duplicados ni huecos, y estructura de plantilla intacta. Queda un residuo (H-21) |
| US-003-2 a P1 | **Válido** | Es el valor añadido que define `doc. general §5` |
| US-003-5 | **Válido, incompleto** | `003:10-11` aún promete «con el mapa a la vista» en una historia P1 |
| NC de límite e inactividad (`000:119-120`) | **Válidos** | Hacían falta para NFR-000-17 y NFR-000-19; preguntas concretas con propuesta. Hasta resolverlos, SC-000-19 y US-001-4.4 no tienen valor de prueba |
| US-001-3.8 y `contrato:266-267` | **Coherente; falta marcarlo** | Se apoya en `doc. técnico §9.2`, que pide contrastar el tratamiento con la hoja. Depende de la regla 10, que aún es propuesta: si no se aprueba, el escenario cambia. No se comprobó en una hoja de cálculo que la fórmula cuente el texto «1»; el escenario no depende de ello, porque el dato llega por su *Given*. Ver H-27 y H-28 |
| FR-002-18 | **Válido** | Bien marcado como propuesta y cierra H-23. «Una sola acción» no se comprueba (H-30) |

## 6. Hallazgos nuevos

### Mayores

**H-24. La verificación no define el alcance de cada tabla ni qué ocurre con filas o columnas sin pareja.**
`contrato:250-254` localiza el título y empareja filas y columnas «por nombre con las categorías de la matriz», pero
no dice dónde termina cada tabla ni cómo tratar lo que no empareja.

- Los mismos nombres de fila se repiten en cada tabla (`EGM!A6`, `A16`, `A26`), así que el nombre no basta sin un
  límite de tabla.
- `EGM!J5` («Total estudios») no es una categoría de la matriz, y no hay regla para reconocer esa columna, aunque
  `contrato:258-259` la compara mediante $u$ y $t$.
- Si la matriz agrega una intervención y la hoja no se actualiza, el resultado queda sin definir: puede ser
  «difiere», «no verificable» o una comparación parcial. Ese caso es el que `contrato:313` declara soportado sin
  más cambios, y `estado §3` muestra que las listas ya cambiaron entre versiones. Lo mismo vale para una categoría
  que siga en la hoja y ya no esté en la lista.
- Una tabla con solo algunos valores calculados tampoco tiene resultado definido (`contrato:268-269`).

Ningún escenario cubre estos casos. Requisitos afectados: FR-001-14, FR-001-15, NFR-000-06.

### Medios

**H-25. Sin lista de tipo de documento, los estados de documento dejan de funcionar.**
`contrato:118-119` define «No empírico» como valor *en la lista* y manda a «Pendiente de codificación» el valor
*fuera de lista*. Sin lista, `contrato:146` permite continuar con los valores presentes, pero entonces ningún valor
está en la lista: todos los documentos no empíricos caerían en «pendiente», en contra de la intención de
`contrato:146`. El caso `contrato:310` repite el problema. La decisión 2 está bien aplicada; falta ajustar la tabla
de estados. Requisito afectado: FR-001-13.

**H-26. El estado «Pendiente de codificación» da 0 donde el equipo dice 20.**
`contrato:346` y US-001-1.9 informan 0 pendientes de codificación en la v4. El cálculo es correcto según la regla,
pero la lámina 8 dice «20 solo con referencia», la lámina 10 dice «las 20 referencias pendientes con lectura y
codificación», y la skill dice que una fila con solo referencia está pendiente de codificación. Quien conozca esas
láminas leerá una contradicción con sus datos. Además, `contrato:118` dice «ni pendiente ni advertencia» para los 14
no empíricos de los N.º 8 a 27, y `doc. técnico §3.3` y `§9.2`, citados como fuente en `contrato:112`, solo describen
esas filas y tratan los empíricos: no fijan ese trato. La regla es defendible y resuelve H-15, pero debe marcarse como
propuesta y revisar el rótulo. Requisito afectado: FR-001-13.

**H-27. Reglas del redactor citadas como fuente o decisión, sin marca de propuesta.**
Usted pidió marcar lo que no tenga fuente. Estas reglas no están en la fuente citada:

| Regla | Ubicación | Lo que cita | Lo que no dice esa fuente |
|---|---|---|---|
| Número inicial y frase de cada título | `contrato:251-254` | Decisión del 1-nov (`:248`) | La regla de reconocimiento |
| Explicación por texto en una dimensión | `contrato:266-267`; US-001-3.8 | Decisión del 1-nov (`:248`) | Esa explicación; `§9.2` solo pide contrastar |
| Filtro «activo»; celda vacía no cumple | `contrato:202-205` | `doc. técnico §2.4`, RF2 (`:212`) | Ambas definiciones; solo definen el vector y el producto |
| «No empírico»: ni pendiente ni advertencia | `contrato:118` | `doc. técnico §3.3`, `§9.2` | Ese trato |
| Fila vacía como todas las celdas vacías | `contrato:85-86` | `doc. técnico §9.2` | La definición; solo es una inferencia razonable |
| «No la calcula» y lectura de «registros» | `contrato:375-377` | Decisión del 2-nov | Es interpretación del redactor |
| Definición de sesión y fin por inactividad | NFR-000-17 (`000:89`) | Decisión del 2-nov | Cuándo termina; lo reconoce el NC de `000:120` |
| Nombre del archivo excluido de registros | NFR-000-17 | Decisión del 2-nov | Extensión prudente de «sin datos de la matriz» |
| Una carga nueva reemplaza la anterior | FR-001-20 | Decisión del 2-nov | Ese comportamiento |

Ninguna parece equivocada. El problema es de trazabilidad: quien las lea creerá que usted o las fuentes las fijaron.

**H-28. Una causa de diferencia que el contrato conoce se reportaría como «sin explicar».**
`contrato:90-91` advierte que un valor con espacios en los extremos puede no contarse en la hoja, y la herramienta sí
lo cuenta. `contrato:265-267` solo explica dos causas, y esta acabaría como «diferencia sin explicar», contra
FR-001-18 («explicar las que tengan causa conocida»). Tampoco se define qué se lista cuando coinciden una fila con
igual intervención y una con texto en una dimensión: «si persiste» deja fuera las primeras.

**H-29. El colofón publicaría datos que no están verificados en las fuentes (regla 3).**
`pie:13-14` da «Organización y Empresa (GIOE)», «Santa Marta» y «Director del grupo: Óscar García Vargas», y `pie:46`
cita el formato de vinculación. Ese archivo (`Jairo Blanco.pdf`, `estado §1`) no está en `docs/fuentes/`. Una búsqueda
en `docs/fuentes/`, incluidos los dos PDF, y en `CLAUDE.md` no encuentra ninguno de esos datos, y no están en las
decisiones del 2-nov. Tampoco llevan `[POR CONFIRMAR]`. El texto ya estaba en el commit inicial y puede ser cierto, pero
no se puede comprobar. `pie:46` menciona además una tutora que no figura en el contenido.

**H-30. Cobertura parcial en cinco requisitos.**

| Requisito | Vinculado a | Qué no se comprueba |
|---|---|---|
| NFR-000-11 | SC-000-11 | Que no aparezcan el nombre ni el rol de Jairo (`pie:21`); revisa categoría, línea y marcadores |
| NFR-000-17 | SC-000-17 | Que la sesión termine por inactividad; solo dice «terminar la sesión» |
| FR-001-25 | US-001-3.7 | «Si ninguna se pudo comparar, “no verificable”, sin lista» (`contrato:272`) |
| FR-002-08 | US-002-3.1, 3.2 | El caso «mientras no exista el archivo» y el texto literal «definición no disponible» |
| FR-002-18 | US-002-4.6 | Que se haga «en una sola acción» |

### Menores

| ID | Hallazgo | Evidencia |
|---|---|---|
| H-31 | Nota desactualizada: dice que «solo faltar un encabezado de rol detiene el proceso», pero la hoja faltante, el ancla empírica y la falta de lista también lo detienen | `000:137`; `contrato:24`, `:133`, `:145`; FR-001-22, FR-001-23 |
| H-32 | La guía de diseño, fuera del alcance auditado, aún indica mostrar «Matriz v4, 27 documentos»: un valor fijo y una versión que NFR-000-12 y la propuesta de H-20 no admiten. También dice que un cajón vacío «es una brecha». Lo tomará quien diseñe | `sistema-diseno-egm/SKILL.md:21`, `:44`; `000:84` |
| H-33 | Anclas incompletas: `contrato:129` declara tres, pero `:131-136` solo trata dos. Si «No aplica» cambia de nombre, ese valor se volvería fila del mapa o nivel. No se dice qué pasa si dos valores empiezan por `Estudio empírico`. La alternativa de `:138` no aplica a nivel, que sin lista es error (`:145`). $v_{\text{emp}}$ y $v_{\text{IE}}$ se usan sin definirse | `contrato:125-139`, `:118`, `:158`, `:179` |
| H-34 | Al unificar términos, «celda» quedó con dos sentidos: la de la hoja de cálculo y la del mapa. «Celda vacía» significa sin dato en `contrato:98`, `:203` y `:230`, y conteo en 0 en FR-003-01 y US-003-1.1, donde además compite con el rótulo de NFR-000-08 | Las citadas; `003:22`, `:218` |
| H-35 | SC-000-09 pide que cada lectura «registre» el archivo, y NFR-000-17 prohíbe el nombre del archivo en los registros. NFR-000-09 dice «indicar», que es lo correcto | `000:81`, `:89`, `:105` |
| H-36 | La sesión empieza con la carga, según NFR-000-17, pero US-001-4.1 y 4.2 hablan de «sesión sin matriz» y «sesión nueva». Tampoco se define qué pasa con filtros activos al cargar otro archivo, cuyos valores pueden ser otros | `000:89`; `001:162`, `:167`, `:184`; FR-002-15 |
| H-37 | Usted dejó como opcional el dato «estudios empíricos que aún no entran al mapa»; FR-003-21 lo vuelve MUST sin indicarlo | `003:238`; `000:135` |
| H-38 | Con la carga desde el navegador, quien recibe errores y advertencias es quien carga, pero la historia y los actores siguen dirigidos a Jairo. NFR-000-03 ya exige lenguaje llano, y los escenarios hablan de «error de contrato» | `001:69`; `000:26-28` |
| H-39 | Bloque de dimensiones degenerado sin regla: delimitadores invertidos, ninguna columna entre ellos, o una columna de rol dentro del bloque, que sería rol y dimensión a la vez. US-001-1.8 permite mover columnas | `contrato:68-74` |
| H-40 | `trazabilidad.md` no muestra las propuestas o NC dentro de requisitos con fuente: FR-002-01, FR-002-12 y NFR-000-12. Tampoco enlaza SC-001-02 a FR-001-22, cuyos casos de intervenciones, tipo de documento y metodología solo cubre ese criterio | `traz:18`, `:51`, `:62`, `:138`; `contrato:307-308` |
| H-41 | SC-003-06 exige «la misma frase» con datos distintos, pero FR-003-11, FR-003-16 y FR-003-22 piden frases distintas según el caso | `003:228`, `:233`, `:239`, `:258` |

## 7. Estado de H-01 a H-23

| ID | Estado | Evidencia y residuo |
|---|---|---|
| H-01 | Cerrado | `contrato:262-267`; US-001-3.1, 3.2 |
| H-02 | Cerrado | `contrato:193-197`, `:258-259` |
| H-03 | Cerrado | `contrato:251-260`, comprobado contra el archivo. Lo pendiente es nuevo: H-24 |
| H-04 | Cerrado con residuo | FR-001-12 se limitó a lo que el contrato llama advertencia, y el enfoque ya advierte. Pero aún pide «N.º, columna y valor» a todas, y las de archivo no los tienen (`contrato:25`, `:312`). SC-001-04 igual. La entidad de `001:297` ya admite variantes |
| H-05 | Cerrado con residuo | FR-001-19 cambió de fuente y la omisión consta en `000:133`, pero se apoya en un «plan aprobado de la fase» que no está en `docs/fuentes/` ni en `docs/planes/`. Tampoco está entre las decisiones que recibí |
| H-06 | Cerrado | SC-000-07 ya es ejecutable |
| H-07 | Cerrado | US-001-1.8, US-002-4.8, US-002-5.1 y SC-003-06 |
| H-08 | Cerrado con residuo | Partes formales en `contrato:202-210`. «Sin nivel» quedó como NC con propuesta sin aplicar, como se pidió (`002:215`; `contrato:203` no cambió). Sigue sin estar en `contrato §9`, y no se define un estudio con nivel «No aplica…», distinto de vacío |
| H-09 | Cerrado | US-001-3.2, US-002-1.6, US-003-4.5, US-003-2.9 y SC-000-06 |
| H-10 | Cerrado | Regla 12, FR-001-24, US-001-2.13; marcado como propuesta |
| H-11 | Cerrado | `contrato:241-242` |
| H-12 | Cerrado | `contrato:100-103`; marcado como propuesta |
| H-13 | Cerrado | `contrato:81-84`, FR-002-01, US-002-1.7; marcado como propuesta |
| H-14 | Cerrado | Decisiones 3 y 12. FR-003-02 sigue deducido de la decisión del 1-nov |
| H-15 | Cerrado | `contrato:85-88`, `:111-119`; US-001-1.9. Efectos nuevos: H-25, H-26 y H-27 |
| H-16 | Cerrado | NC con propuesta sin aplicar (`contrato:171`). Aclaración: la fórmula de $M$ ya incluye esa fila, de modo que el comportamiento actual coincide con la propuesta, salvo la advertencia |
| H-17 | Cerrado | `contrato:214-215` |
| H-18 | Cerrado con residuo | `000:136`. $N_{min}$ se cita en `§6.1`, pero está en `§6.2` a `§6.4`, y no se nombran los mapas derivados ni la activación por umbral de `§12.2` |
| H-19 | Cerrado | Decisión 5 |
| H-20 | Cerrado | NC con propuesta (`000:84`; `pie:23-26`). Ver H-32 |
| H-21 | Cerrado con residuo | Orden correcto; US-003-3.4 y la parte del mapa pasaron a la feature o a US-003-5. Quedan: `003:10-11` («con el mapa a la vista»), US-003-1.4, que requiere US-003-2, y US-001-4.6 («todas las vistas»), que requiere 002 y 003 |
| H-22 | Cerrado | Búsqueda sin resultados. Efecto nuevo: H-34 |
| H-23 | Cerrado | FR-002-18; SC-002-02 y demás SC enlazados |

## 8. Huecos

H-24 (verificación) y H-30 (cinco requisitos). Quedan bloqueados en parte por un punto abierto: FR-002-12, NFR-000-12,
NFR-000-17 y NFR-000-19, con SC-000-17, SC-000-19 y US-001-4.4.

## 9. Excesos

No hay componentes, código ni funciones fuera de alcance. Dos elementos sin decisión: FR-002-18, marcado como propuesta,
y la exigencia MUST de FR-003-21 (H-37).

## 10. Puntos abiertos

### `[NEEDS CLARIFICATION]` (6)

| Ubicación | Asunto | Propuesta |
|---|---|---|
| `contrato-datos.md:171` | Fila con principal vacía y secundaria diligenciada | Mantenerla en $M$ con advertencia; sin aplicar |
| `contrato-datos.md:382` | *(Interno)* Si se comunica al equipo la discrepancia del apéndice B | Ninguna; se mantiene lo actual |
| `000-vision-alcance.md:84` | Texto de identificación de la matriz en el colofón (NFR-000-12) | Nombre y fecha de lectura, sin versión |
| `000-vision-alcance.md:119` | Límite de tamaño del archivo | 10 MB, configurable |
| `000-vision-alcance.md:120` | Tiempo de inactividad que termina la sesión | 30 minutos, configurable |
| `002-mapa-interactivo/spec.md:215` | Estado «sin nivel» en el control único (FR-002-12) | Entrada «Sin nivel» en la leyenda; sin aplicar |

### `[POR CONFIRMAR]` (1)

| Ubicación | Asunto |
|---|---|
| `pie-de-pagina.md:21` | Si se incluye Jairo en el colofón y con qué rol. `pie:4` solo explica la convención |

### Propuestas sin fuente, pendientes de aprobación (6)

| Ubicación | Asunto |
|---|---|
| `contrato-datos.md:83` | Regla de orden del archivo |
| `contrato-datos.md:101` | Valor no válido en una dimensión: no marca |
| `contrato-datos.md:108` | Año no reconocido |
| `001-lectura-verificacion/spec.md:286` | FR-001-24 |
| `002-mapa-interactivo/spec.md:204` | FR-002-01, regla de orden |
| `002-mapa-interactivo/spec.md:221` | FR-002-18 |

`pie-de-pagina.md:25` repite la propuesta de `000:84`.

### Temas sin marca, ya registrados

`000:124` (despliegue, decisión futura) y `000:128` (definiciones, tema por definir con el equipo).

## 11. Observaciones fuera de lo auditado

No son hallazgos contra el alcance.

- `docs/informes/fase-1-resumen.md` sigue con fecha del 1-nov: 72 requisitos, 12 NC y puntos ya decididos. Tampoco
  contiene la versión de Python, que según `000:134` y la decisión 9 va allí.
- `.claude/skills/calidad-python/SKILL.md:24` conserva un NC sobre la versión de Python y un mínimo de versión, que la
  decisión 9 deja libre.
- `.claude/skills/contrato-matriz/SKILL.md`, regla 3, sigue definiendo fila vacía por la columna A; el contrato
  registra la diferencia en `contrato:86-88`.
- NFR-000-04 y NFR-000-05 siguen citando el prompt de la fase, que no es un archivo de fuentes.
- `doc. técnico §6.2` sigue diciendo $\lvert B\rvert = 34$; el recálculo da 42, y esa diferencia no consta en
  `000:130-137`.
- `contrato-datos.md` contiene el apéndice B. Si los specs v0 se comparten con la investigadora principal en la fase
  F1, ese apéndice debe quedar fuera del material compartido, según la regla 9.
