# Plan de implementación: 002-mapa-interactivo

**Creado**: 2026-11-22 · **Estado**: aprobado por Jairo el 2026-11-22 (COR-013 verificada)
**Spec**: [`docs/specs/002-mapa-interactivo/spec.md`](../../specs/002-mapa-interactivo/spec.md)
**Arquitectura**: `docs/arquitectura/arquitectura.md` (aprobada el 22-nov-2026) §4, §5, §5.1, §6 (M01 a M23), §6.4, §8 · **ADR relacionados**: ADR-001, ADR-003 (puntos 2, 6, 7 y 8), ADR-004 (punto 4), ADR-005
**Interfaz**: `docs/interfaz/flujos.md` (F-002-1 a F-002-5, estados E5 y E6, §7 y §9), `docs/interfaz/tokens.css`, bocetos `mapa.html`, `estudio.html`, `colofon.html`
**Ubicación de este plan**: `docs/planes/002-mapa-interactivo/plan.md`

Documento interno, para Jairo y los subagentes. No es texto de interfaz. No contiene código.

## Resumen

El spec 002 pide el mapa de evidencias y brechas: intervenciones en filas y dimensiones en columnas, en el orden del
archivo; en cada cajón, una burbuja por nivel de evidencia con área proporcional al número de estudios
($r \propto \sqrt{n}$) y el número escrito; el detalle trazable de cada cajón hasta sus N.º y la ficha de cada estudio;
las definiciones de filas y columnas; cuatro filtros que se aplican solo con «Actualizar vista» y se quitan de
inmediato con «Restablecer», con estado compartido con el tablero; y la exportación del mapa visible.

Enfoque, tomado de la arquitectura y los ADR: el cálculo vive en el núcleo (`egm.filtros` M06, que este plan crea;
`egm.conteo` M07, que este plan amplía con el filtro y el desglose por nivel; `egm.definiciones` M12, que este plan
crea). La capa web (FastAPI + Jinja2 + htmx, ADR-003) solo orquesta: `app.presentacion` (M17) convierte el resultado
del núcleo en modelos de vista; `app.plantillas` (M18) los dibuja sin calcular, sin estilos en línea, con el radio como
atributo del SVG y el ancho de la cajonera derivado del número de dimensiones; `app.exportacion` (M20) entrega el SVG
del mapa y la tabla de conteos en `.xlsx`, y `app.cliente` (M19) convierte ese SVG en PNG en el navegador. Los conteos
no se guardan: se recalculan en cada petición desde el corpus con el filtro aplicado de la sesión (arquitectura §5), y
así un mismo cálculo sirve al mapa, al tablero y a la exportación (SC-002-05).

Prioridad por el plazo (entrega el 6-dic-2026): primero el mapa con filtros de punta a punta (fases 3 y 4), luego el
detalle de los cajones (fase 5), las definiciones (fase 6) y, al final, la exportación (fase 7).

## Contexto técnico

**Lenguaje/versión**: Python 3.13 en `.venv` (arquitectura §3; ADR-003). Las versiones exactas de las dependencias las
fija el plan 001 (ADR-003, punto 1).
**Dependencias principales**: núcleo con `openpyxl` solo en `egm.libro` (regla 3 del núcleo, arquitectura §4.1); capa
web FastAPI (Starlette) + Jinja2 con autoescape + Uvicorn, un solo proceso; htmx y guion propio servidos localmente;
tipografías Alegreya y Alegreya Sans servidas localmente (ADR-003, punto 6; COR-012). La escritura del `.xlsx` de
conteos (M20) es de la capa web y no pasa por `egm.libro`; la biblioteca la fija el plan 001 con las demás dependencias.
**Almacenamiento**: ninguno. Resultado y filtro aplicado en la memoria de la sesión (M15); exportaciones generadas en
memoria y entregadas como descarga, sin escribir en disco (NFR-000-17; ADR-003, punto 7). `data/raw/` solo se abre en
modo lectura en las pruebas de integración, con control de huella antes y después.
**Pruebas**: `pytest`, `hypothesis` y cliente de pruebas de la aplicación (skill `calidad-python`); navegador
automatizado con revisión automática de accesibilidad para los escenarios de interfaz (ADR-003, punto 8). Las
herramientas exactas de navegador y de accesibilidad las fija el plan 001; este plan las usa.
**Plataforma objetivo**: navegador en el mismo equipo, servidor local en 127.0.0.1 (ADR-004).
**Tipo de proyecto**: núcleo Python (`src/egm/`) + capa web (`app/`).
**Metas de desempeño**: el spec 002 no fija ninguna; los conteos se recalculan por petición (arquitectura §5).
**Restricciones**: conteos y nunca porcentajes (NFR-000-07; M11 sigue inactivo); cada número es la longitud de su lista
de N.º (`Conteo`, M01; NFR-000-02); celda en 0 = «ningún estudio registrado», brecha provisional; con filtros activos,
«ningún estudio registrado con los filtros activos» y nunca «brecha»; categorías leídas del archivo, ninguna escrita
en el código (NFR-000-06); sin estilos en línea (ADR-003, punto 6); URL sin texto de la matriz, por posición (M14).
**Escala/alcance**: las filas de la matriz vigente y de sus versiones futuras que cumplan el contrato, sin límite de
filas (M05); una vista de mapa, un cajón abierto en el margen, una ficha de estudio, una definición, un bloque de
filtros y leyenda, tres descargas.

## Requisitos que cubre este plan

| Requisito | Resumen | Historia | Escenario / criterio que lo verifica | Módulo(s) de la arquitectura |
|---|---|---|---|---|
| FR-002-01 | Filas = intervenciones, columnas = dimensiones, en el orden del archivo | US-002-1 | US-002-1.1, 1.4, 1.7 | M04 (usa), M07, M17, M18 |
| FR-002-02 | Burbuja que crece con $n$, con el número escrito | US-002-1 | US-002-1.2, SC-002-01 | M17, M18 |
| FR-002-03 | Color = nivel; conteo por nivel distinguible en la celda | US-002-1 | US-002-1.3 | M07, M17, M18 |
| FR-002-04 | Celda en 0: «ningún estudio registrado» y su nota | US-002-1, US-002-2 | US-002-1.1, US-002-2.3 | M10, M17 |
| FR-002-05 | Estudios de la celda con N.º, referencia, año y nivel | US-002-2 | US-002-2.1, SC-002-02 | M07, M17, M18 |
| FR-002-06 | Enlace si la referencia contiene DOI o URL | US-002-2 | US-002-2.2 | M17 |
| FR-002-07 | Textos del estudio tal cual | US-002-2 | US-002-2.4 | M05 (usa), M17, M18 |
| FR-002-08 | Definición del equipo o «definición no disponible» | US-002-3 | US-002-3.1, 3.2, 3.3 | M12, M22, M17, M18 |
| FR-002-09 | Cuatro filtros; valores de la lista o, sin lista, los presentes | US-002-4 | US-002-4.1, 4.9 | M06, M17 |
| FR-002-10 | Año por rango, extremos incluidos | US-002-4 | US-002-4.4 | M06 |
| FR-002-11 | Conjunción; varios valores por filtro | US-002-4 | US-002-4.3, 4.8 | M06 |
| FR-002-12 | Leyenda = filtro de nivel; espera a «Actualizar vista»; «Sin nivel» común al mapa y al tablero, con 0 en el mapa si solo hay no empíricos | US-002-4 | US-002-4.5, 4.11, 4.12, 4.14 | M06, M17, M18 |
| FR-002-13 | Filtro activo siempre visible y «n de N» | US-002-4 | US-002-4.1, SC-002-03 | M06, M07, M17 |
| FR-002-14 | Celda en 0 con filtros: rótulo propio, nunca «brecha» | US-002-4 | US-002-4.2 | M10, M17 |
| FR-002-15 | Estado de filtros compartido entre mapa y tablero | US-002-4 | US-002-4.7 (la parte del tablero, US-003-3.4, 5.1 y 5.2, es del plan 003) | M15, M14 |
| FR-002-16 | Descargar imagen (PNG y SVG) y tabla (`.xlsx`) con filtros, archivo y fecha | US-002-5 | US-002-5.1, 5.2, SC-002-05 | M20, M19, M14, M18 |
| FR-002-17 | Advertencias de lectura y verificación en el mapa | US-002-1 | US-002-1.5, 1.6 | M10 (usa lo del 001), M17 |
| FR-002-18 | Quitar los filtros en una acción: «Restablecer» | US-002-4 | US-002-4.6 | M06, M14, M15 |
| FR-002-19 | Activo solo al aplicar con «Actualizar vista» y si deja fuera algo; un solo par de botones; «Restablecer» inmediato | US-002-4 | US-002-4.6, 4.10, 4.13 (US-003-5.4 y 5.5 son del plan 003) | M06, M14, M15, M17 |
| NFR-000-04 | WCAG 2.2 AA en el mapa; todo con teclado | transversal | SC-000-04, SC-002-04 | M18, M19 |
| NFR-000-05 | Desde 360 px sin desplazamiento horizontal de la página | transversal | SC-000-05 | M18 |
| NFR-000-08 | Celda en 0 = «ningún estudio registrado»; brecha provisional | US-002-1 | SC-000-08 | M10, M17 |
| NFR-000-09 | Exportaciones deterministas, con archivo y fecha de lectura | US-002-5 | SC-000-09 (en la exportación) | M20 |
| NFR-000-10 | La celda no depende solo del color | US-002-1 | SC-000-10 | M17, M18 |
| NFR-000-13 | Diseño «Fichero», no genérico | transversal | SC-000-13 | M18 |
| NFR-000-16 | 3ie solo como referencia de diseño | transversal | SC-000-16 (en la vista del mapa) | M18 (usa M21 del 001) |
| SC-002-01 | Número de cada celda = $S(i,j)$ o $S_\varphi(i,j)$ = longitud de su lista | US-002-1, US-002-4 | P-002-02, P-002-14, P-002-37 | M07, M17 |
| SC-002-02 | De la celda a la referencia en dos acciones como máximo | US-002-2 | P-002-46 | M17, M18, M19 |
| SC-002-03 | «n de N» y conteos = recálculo independiente en todas las combinaciones | US-002-4 | P-002-37 | M06, M07 |
| SC-002-04 | Todas las funciones del mapa solo con teclado | US-002-1, transversal | P-002-17, P-002-68 | M18, M19 |
| SC-002-05 | Tabla exportada = mapa visible, con y sin filtros | US-002-5 | P-002-60 | M20, M17 |

Escenarios de otros specs que este plan ejecuta porque dependen del mapa (arquitectura §6.4; spec 001, historias 4 y
5): US-001-4.10 (parte del mapa), US-001-5.4, US-001-5.5 y US-001-5.6. Ver NC-P002-1.

NFR-000 que este plan respeta sin ser su dueño (arquitectura §6.4): NFR-000-02 (cada número con su lista), NFR-000-03
(textos de usted, sin jerga), NFR-000-06 (la cajonera sigue las dimensiones leídas), NFR-000-07 (ningún porcentaje),
NFR-000-12 (cabecera corrida y colofón «Datos»), NFR-000-17 (nada en disco ni en registros). Sus pruebas propias son
de los planes 001 y 003; aquí se comprueban solo en las vistas del mapa.

Fuera de alcance de este plan:
- El tablero (V8), las cifras clave, las conclusiones y la lista de N.º de una cifra (V9): plan 003. También la parte
  del tablero de US-002-4.6 («Restablecer» en el tablero) y de US-002-4.14 (cifra de documentos «2 de 3»), y el
  predicado de documentos `cumple_documento` de M06 (FR-003-14), que el plan 003 agrega.
- Lectura, verificación, carga, sesión, actividad, cabecera corrida, avisos de lectura y colofón: plan 001.
- Filtros por intervención, dimensión o enfoque; zoom del mapa; vistas por enfoque (spec 000, «Fuera de alcance»;
  invariantes del 1-nov-2026).
- Vista de red y módulo no supervisado (regla 10 de `CLAUDE.md`). `egm.conteo.coocurrencias` es del plan 003.
- Porcentajes: M11 sigue inactivo; ninguna vista del mapa los pide.

## Estructura del proyecto

### Documentación (esta feature)

```text
docs/specs/002-mapa-interactivo/
└── spec.md              # Spec aprobado (fuente de este plan)

docs/planes/002-mapa-interactivo/
└── plan.md              # Este archivo
```

### Código fuente (raíz del repositorio)

La forma de cada módulo (archivo o paquete) del núcleo sigue la convención que fije el plan 001 al conciliar el
andamiaje (arquitectura §6). Las rutas de abajo usan la forma de archivo; si el plan 001 elige paquete, se respeta.

```text
src/egm/
├── filtros.py           # M06 egm.filtros (crea)
├── conteo.py            # M07 egm.conteo (amplía: filtro y desglose por nivel)
├── textos.py            # M10 egm.textos (amplía: rótulos del mapa, resumen de filtros)
└── definiciones.py      # M12 egm.definiciones (crea)

app/
├── servidor.py          # M14 app.servidor (amplía: rutas del mapa)
├── sesiones.py          # M15 app.sesiones (amplía: filtro aplicado)
├── presentacion.py      # M17 app.presentacion (amplía: vista_mapa, vista_cajon, vista_ficha, vista_definicion, filtros)
├── exportacion.py       # M20 app.exportacion (crea)
├── configuracion.py     # M22 app.configuracion (amplía: ruta del archivo de definiciones)
├── plantillas/          # M18 app.plantillas (amplía: mapa, cajonera, filtros, cajón, ficha, definición, descargar)
├── estaticos/           # M18 (amplía: CSS)
└── cliente/             # M19 app.cliente (amplía: teclado, foco y PNG)

tests/
├── constructor.py       # M23 tests.constructor (amplía)
├── unit/
├── integracion/
├── propiedades/
└── navegador/           # pruebas en navegador automatizado (marca `navegador`, plan 001)

data/fixtures/
└── 002_*.xlsx, 002_definiciones.txt   # generados por M23
```

**Decisión de estructura**: el plan usa solo módulos de la lista cerrada de la arquitectura §6 y la tabla §6.4: crea
M06, M12 y M20; amplía M07, M10, M14, M15, M17, M18, M19, M22 y M23; usa M01, M04, M05 y M13. No toca M02, M03, M08,
M09, M11, M16 ni M21. La carpeta `tests/navegador/` no es un módulo; la fijó el plan 001.

### Quién hace cada tarea

- **[IMP]** `implementador`: núcleo, modelos de vista, rutas, sesión, exportación, conversión a PNG y todas las pruebas
  automáticas.
- **[DF]** `disenador-front`: plantillas, CSS, comportamiento de teclado y foco de la cajonera, revisión visual y
  revisión manual de accesibilidad. Las plantillas no calculan: solo dibujan el modelo de vista (M18).
- Una tarea [DF] que necesita datos nuevos del modelo de vista se detiene y lo pide al [IMP]; nunca calcula en la
  plantilla ni en el guion.

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: preparar lo que la feature necesita y aún no existe. Supone cerrado el plan 001 hasta su historia de
carga y sesión (ver «Dependencias con otros planes»).

- [ ] T-002-01 [IMP] Crear los archivos vacíos de los módulos que el plan crea (M06, M12, M20) y las carpetas de
  plantillas y pruebas que el plan agrega, con la forma que fijó el plan 001. Requisitos: —. Módulos: M06, M12, M20. Archivos:
  `src/egm/filtros.py`, `src/egm/definiciones.py`, `app/exportacion.py`, `tests/unit/`, `tests/integracion/`,
  `tests/propiedades/`, `tests/navegador/`.
- [ ] T-002-02 [P] [IMP] Ampliar el constructor M23 con los fixtures del plan, cada uno con su tabla de esperados escrita
  a mano en su docstring a partir del contrato, y generarlos en `data/fixtures/`. Ningún fixture copia cifras de la
  lámina 7 ni toca `data/raw/`. Requisitos: NFR-000-06 (soporte), SC-002-01, SC-002-03. Módulos: M23. Archivos: `tests/constructor.py`,
  `data/fixtures/002_*.xlsx`.

  | Fixture | Contenido (sintético) | Escenarios |
  |---|---|---|
  | FX-01 `002_burbujas.xlsx` | Una celda con 1 estudio y otra con 5 | US-002-1.2 |
  | FX-02 `002_niveles_celda.xlsx` | Una celda con 3 estudios: 2 de evaluación de impacto y 1 estudio de caso | US-002-1.3 |
  | FX-03 `002_7x9.xlsx` | 7 intervenciones y 9 dimensiones, con nombres largos | US-002-1.4, NFR-000-05, NFR-000-06 |
  | FX-04 `002_orden.xlsx` | Lista de intervenciones y columnas de dimensión en orden no alfabético | US-002-1.7 |
  | FX-05 `002_sin_estudios.xlsx` | Matriz aceptada sin ningún estudio en el mapa | caso borde «ningún estudio en el mapa» |
  | FX-06 `002_fuentes.xlsx` | 3 estudios del mapa: 2 Territorial y 1 Académica; lista de 3 tipos de fuente | US-002-4.1, 4.2, 4.6, caso borde «0 de N» |
  | FX-07 `002_fuentes_metodologias.xlsx` | Estudios de fuente Académica, Institucional y Territorial y de tres metodologías, con combinaciones conocidas | US-002-4.3, 4.8 |
  | FX-08 `002_anios.xlsx` | Estudios de 2010, 2015 y 2020, y uno con año no reconocido | US-002-4.4, caso borde de año |
  | FX-09 `002_niveles_sin_nivel.xlsx` | Estudios del mapa de dos niveles y uno sin nivel | US-002-4.5, 4.11 |
  | FX-10 `002_no_aplica.xlsx` | Un estudio del mapa con un nivel que empieza por «No aplica» | US-002-4.12 |
  | FX-11 `002_fuente_vacia.xlsx` | 3 estudios del mapa, 2 con tipo de fuente y 1 con esa celda vacía | US-002-4.13, caso borde de campo vacío |
  | FX-12 `002_no_empiricos.xlsx` | 2 estudios del mapa de nivel «Estudio de caso» y 1 documento no empírico | US-002-4.14 |
  | FX-13 `002_fuente_sin_lista.xlsx` | Columna de tipo de fuente sin lista de validación | US-002-4.9 |
  | FX-14 `002_referencias.xlsx` | Referencias con DOI, con URL y sin ninguno; textos de país y población, dimensiones evaluadas, indicadores, hallazgos, vacío, limitaciones y aporte con marcadores, saltos de línea y caracteres que exigen escape | US-002-2.1, 2.2, 2.4 |
  | FX-15 `002_dos_intervenciones.xlsx` | Un estudio con intervención principal y secundaria distintas | caso borde «estudio con dos intervenciones» |
  | FX-16 `002_nivel_nuevo.xlsx` | Un quinto nivel agregado a la lista | caso borde «nivel nuevo», NFR-000-06 |
  | FX-17 `002_definiciones.txt` | Archivo de definiciones sintético en el formato de ADR-004, punto 4, con una intervención y una dimensión definidas y otras sin definición | US-002-3.1, 3.2 |

- [ ] T-002-03 [P] [IMP] Ampliar las estrategias de propiedades de M23: matrices al azar con categorías conocidas
  (tipos de fuente, metodologías, niveles con y sin «Sin nivel», años con extremos y no reconocidos, campos vacíos) y
  selecciones de filtro al azar sobre las opciones de cada control. Requisitos: SC-002-01, SC-002-03. Módulos: M23. Archivos:
  `tests/constructor.py`.
- [ ] T-002-04 [IMP] Comprobar que el navegador automatizado y la revisión automática de accesibilidad que fijó el
  plan 001 corren contra la aplicación local; si no están, detenerse y reportarlo. Requisitos: NFR-000-04, SC-002-04.
  Módulos: — (entorno). Archivos: ninguno nuevo.

---

## Fase 2: Base (prerrequisitos que bloquean)

**Propósito**: el filtro como tipo del dominio, el mapa con filtro y desglose por nivel en el núcleo, y el filtro
aplicado en la sesión. Todas las historias lo usan.

**Crítico**: ninguna historia empieza antes de cerrar esta fase.

### Pruebas de la base (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-01 | unit | FR-002-03, SC-002-01 | FX-02 | La celda tiene conteo 3 y desglose por nivel en el orden de la lista: evaluación de impacto con 2 N.º y estudio de caso con 1 N.º; cada valor es la longitud de su lista |
| P-002-02 | propiedades | SC-002-01; invariantes del contrato §5 | estrategias de T-002-03 | Para toda celda, la suma del desglose por nivel es igual a su conteo; $S_\varphi(i,j) \le S(i,j)$; $\sum_{i,j} S(i,j) \ge N$; con `SIN_FILTRO`, `mapa`, `conjuntos` y `evaluacion_impacto` dan lo mismo que en el plan 001; con cualquier filtro, $\lvert M_\varphi \rvert \le \lvert M \rvert$ y $S^{IE}_\varphi(i,j) \le S^{IE}(i,j)$ |
| P-002-03 | unit | FR-002-15, FR-002-19 | FX-06 | Una sesión nueva tiene el filtro aplicado `SIN_FILTRO`; `aplicar_filtro` lo guarda y otra sesión no lo ve |

- [ ] T-002-05 [IMP] Escribir P-002-01 y P-002-02 en `tests/unit/test_conteo_mapa.py` y
  `tests/propiedades/test_mapa_filtro.py`, y P-002-03 en `tests/unit/test_sesiones_filtro.py`.

### Implementación de la base

- [ ] T-002-06 [IMP] Crear en M06 el tipo `Filtro` (cuatro controles, `None` = no activo) y `SIN_FILTRO`, con la
  interfaz pública de la arquitectura. Requisitos: FR-002-11, FR-002-19. Pruebas: P-002-02. Módulos: M06. Archivos: `src/egm/filtros.py`.
- [ ] T-002-07 [IMP] Ampliar M07 para que `conjuntos`, `mapa` y `evaluacion_impacto` reciban `filtro: Filtro = SIN_FILTRO` (arquitectura §6.1; el plan 001 las deja sin ese parámetro) y para que `mapa` entregue, por celda, el desglose por nivel en el orden de la lista de niveles con «Sin nivel» al final, y `estudios` ($n$) y `total` ($N$) como `Conteo`. Con `SIN_FILTRO`, las tres dan lo mismo que en el plan 001. Requisitos: FR-002-03, FR-002-13, SC-002-01; soporte de FR-003-06 y FR-003-14 (plan 003). Pruebas: P-002-01, P-002-02. Módulos: M07. Archivos: `src/egm/conteo.py`.
- [ ] T-002-08 [IMP] Ampliar M15 con el filtro aplicado por sesión (`aplicar_filtro`), con `SIN_FILTRO` al crear o
  reemplazar la sesión. Requisitos: FR-002-15, FR-002-19. Pruebas: P-002-03. Módulos: M15. Archivos: `app/sesiones.py`.

**Punto de control**: base lista; pruebas P-002-01 a P-002-03 en verde. El implementador se detiene y resume.

---

## Fase 3: Historia 1 — Ver el mapa (prioridad: P1) (mínimo entregable)

**Objetivo**: la cajonera con filas, columnas, burbujas por nivel, números escritos, rótulos de cajón vacío y avisos de
lectura, navegable con teclado.

**Prueba independiente**: cargar FX-01 a FX-05 y la matriz vigente, y leer el mapa contra los conteos del contrato.

### Pruebas de la historia 1 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-04 | integración | US-002-1.1, FR-002-01, FR-002-04 | matriz vigente de `data/raw/`, abierta en modo lectura y entregada como bytes a `procesar`; huella SHA-256 comprobada antes y después | 6 filas y 8 columnas; 6 celdas con 1 estudio cada una ({Transferencia de activos, Acompañamiento técnico} × {Vulnerabilidad, Humano, Financiero}, N.º 7); 42 celdas con «ningún estudio registrado»; huella sin cambios (contrato, apéndice A) |
| P-002-05 | unit | US-002-1.2, FR-002-02 | FX-01 | El radio de la burbuja de 5 es mayor que el de 1 y su razón es $\sqrt{5}$; ambas celdas llevan su número escrito («5» y «1») |
| P-002-06 | unit | US-002-1.3, FR-002-03, NFR-000-10 | FX-02 | Dos burbujas en la celda, con clases de nivel distintas (tono y borde) y los números «2» y «1» escritos; etiqueta accesible con ambos conteos |
| P-002-07 | integración | US-002-1.4, FR-002-01, NFR-000-06 | FX-03 | 7 encabezados de fila y 9 de columna en el HTML; el modelo de vista entrega 9 dimensiones; la hoja de estilo no contiene un número fijo de columnas |
| P-002-08 | unit | US-002-1.7, FR-002-01 | FX-04 | Filas en el orden de la lista de intervenciones y columnas en el orden de la matriz, no alfabético |
| P-002-09 | integración | US-002-1.5, FR-002-17 | fixture «no verificable» del plan 001 (US-001-3) | La página del mapa muestra el aviso «no verificable» en lenguaje llano, antes de la cajonera |
| P-002-10 | integración | US-002-1.6, FR-002-17 | fixture «difiere» del plan 001 (US-001-3) | La página nombra solo las tablas de `Verificacion.verificadas` que difieren, con su explicación conocida; ningún número de tabla fuera de esa lista aparece en la página |
| P-002-11 | integración | caso borde «ningún estudio en el mapa», NFR-000-08 | FX-05 | Todas las filas y columnas, cada cajón con «ningún estudio registrado» y el aviso de que aún no hay estudios codificados (estado E5) |
| P-002-12 | unit | caso borde «estudio con dos intervenciones» | FX-15 | El estudio aparece en ambas filas; el número de estudios del mapa es 1, no la suma de celdas |
| P-002-13 | unit | caso borde «nivel nuevo», NFR-000-06 | FX-16 | El quinto nivel aparece en la leyenda con la clase derivada, sin cambios de código |
| P-002-14 | propiedades | SC-002-01, SC-000-02 | estrategias de T-002-03 | En el 100 % de las celdas del modelo de vista, el número escrito es igual a $S(i,j)$ recalculado en la prueba desde la fórmula del contrato y a la longitud de su lista de N.º |
| P-002-15 | unit | FR-002-04, NFR-000-08, SC-000-08 | FX-05, FX-06 | Ninguna vista del mapa contiene «no investigado»; toda celda en 0 usa el rótulo del catálogo; la nota de cajón vacío dice que la brecha es provisional |
| P-002-16 | unit | ADR-003 punto 6, NFR-000-06 | FX-03 | El HTML del mapa no tiene ningún atributo `style`; cada burbuja lleva el radio como atributo `r` del SVG |
| P-002-17 | navegador | SC-002-04 (cajonera), NFR-000-04 | FX-03 | Un solo Tab entra a la cajonera; las flechas mueven el foco; Inicio y Fin van al extremo de la fila; Ctrl+Inicio y Ctrl+Fin, al de la tabla; Intro o Espacio abren el cajón |
| P-002-18 | integración | NFR-000-12, NFR-000-16, SC-000-16, ADR-005, NC-INT-3 | FX-06 | La página muestra la cabecera «Evidencias sobre medios de vida» con la línea de datos del plan 001, el título de vista «Mapa de evidencias», y con la configuración por defecto el colofón solo con «Datos» y la referencia a 3ie; ningún dato ni marca de 3ie en la cajonera |
| P-002-19 | navegador | US-001-5.4 (NC-P002-1) | FX-06 | Con el reloj de sesión del plan 001 a 44 minutos sin interacción, pasar el cursor sobre una burbuja reinicia la cuenta y la sesión no termina a los 45 |

- [ ] T-002-09 [P] [US-002-1] [IMP] Escribir P-002-04, P-002-07, P-002-09 a P-002-11 y P-002-18 en `tests/integracion/test_mapa.py`.
- [ ] T-002-10 [P] [US-002-1] [IMP] Escribir P-002-05, P-002-06, P-002-08, P-002-12, P-002-13, P-002-15 y P-002-16 en
  `tests/unit/test_vista_mapa.py`, y P-002-14 en `tests/propiedades/test_vista_mapa.py`.
- [ ] T-002-11 [P] [US-002-1] [IMP] Escribir P-002-17 y P-002-19 en `tests/navegador/test_mapa_teclado.py`.

### Implementación de la historia 1

- [ ] T-002-12 [US-002-1] [IMP] Ampliar M10 con los rótulos del mapa: «ningún estudio registrado», su nota («nadie ha estudiado
  ese cruce o no se ha encontrado», brecha provisional), «ningún estudio registrado con los filtros activos», «Sin
  nivel», el aviso de mapa sin estudios y la plantilla de la etiqueta accesible de cada cajón, de usted y sin jerga.
  Requisitos: FR-002-04, FR-002-14, NFR-000-08. Pruebas: P-002-11, P-002-15. Módulos: M10. Archivos: `src/egm/textos.py`.
- [ ] T-002-13 [US-002-1] [IMP] Implementar `vista_mapa` en M17: filas y columnas en el orden del esquema; por celda, una burbuja
  por nivel presente con su número, su clase de nivel por posición en la lista (derivada para un nivel nuevo, propia
  para «Sin nivel») y su radio como número con $r \propto \sqrt{n}$; número de dimensiones para el ancho; rótulos y
  etiqueta accesible; avisos de lectura del plan 001 antes de la cajonera. Reemplaza el modelo de vista provisional de resultado de T-001-66 (NC-P001-1), que se retira. Requisitos: FR-002-01 a FR-002-04,
  FR-002-17, NFR-000-06, NFR-000-10. Pruebas: P-002-04 a P-002-14, P-002-16. Módulos: M17. Archivos: `app/presentacion.py`.
- [ ] T-002-14 [US-002-1] [DF] Escribir la plantilla de la página del mapa y el fragmento de la cajonera en M18, desde
  `mapa.html` y `tokens.css`: SVG con el radio como atributo, patrón `grid` de WAI-ARIA, contorno discontinuo del cajón
  vacío (`--contorno-vacio`), «Sin nivel» con borde doble, nivel nuevo con la trama derivada, columna de intervenciones
  fija y desplazamiento lateral dentro del recuadro a 360 px, modo claro y oscuro; sin estilos en línea y sin número fijo
  de columnas: el ancho sale del número de dimensiones. Requisitos: FR-002-02, FR-002-03, NFR-000-05, NFR-000-10,
  NFR-000-13. Pruebas: P-002-06, P-002-07, P-002-16. Módulos: M18. Archivos: `app/plantillas/`, `app/estaticos/`.
- [ ] T-002-15 [US-002-1] [DF] Implementar en M19 el teclado de la cajonera (foco itinerante, flechas, Inicio, Fin, Ctrl+Inicio,
  Ctrl+Fin, Intro y Espacio) con atributos `data-egm-*`. Requisitos: NFR-000-04, SC-002-04. Pruebas: P-002-17. Módulos: M19. Archivos:
  `app/cliente/`.
- [ ] T-002-16 [US-002-1] [IMP] Convertir en M14 la ruta `GET /vista/resultado` del plan 001 en la ruta del mapa (plan 001, R-2 y
  NC-P001-1): toma de la sesión el resultado y el filtro aplicado y devuelve la página del mapa con la cabecera, los
  avisos y el colofón del plan 001. Desde esta tarea, una carga aceptada (`POST /carga`), la recuperación de la sesión
  al recargar (`GET /`, E9) y «Volver al mapa» de E2, E3 y E10 con matriz previa llevan al mapa; no queda ninguna vista
  provisional ni otra ruta de resultado. P-001-72, P-001-87 y P-001-90 del plan 001 no cambian y siguen en verde.
  Requisitos: FR-002-01, FR-002-15, NFR-000-16. Pruebas:
  P-002-04, P-002-09 a P-002-11, P-002-18, P-002-19. Módulos: M14. Archivos: `app/servidor.py`.

**Punto de control**: la historia 1 funciona y se prueba de forma independiente. El implementador se detiene y resume.

---

## Fase 4: Historia 4 — Filtrar el mapa (prioridad: P2) (mínimo entregable)

**Objetivo**: los cuatro filtros con la leyenda como control de nivel, «Actualizar vista», «Restablecer», resumen
legible y «n de N».

**Prueba independiente**: con FX-06 a FX-13, aplicar y quitar filtros y comparar los conteos con los esperados.

### Pruebas de la historia 4 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-20 | integración | US-002-4.1, FR-002-09, FR-002-13 | FX-06 | Solo Territorial y «Actualizar vista»: 2 estudios en el mapa, el filtro visible en el resumen y «2 de 3» |
| P-002-21 | integración | US-002-4.2, FR-002-14 | FX-06 | Una celda con estudios que el filtro deja en 0 dice «ningún estudio registrado con los filtros activos»; la página no contiene «brecha» mientras el filtro está activo |
| P-002-22 | integración | caso borde «0 de N» | FX-06 | Solo Institucional: «0 de 3» y el rótulo con filtros en todas las celdas, con el mensaje que orienta a quitar ese filtro |
| P-002-23 | unit | US-002-4.3, FR-002-11 | FX-07 | Un valor en cada filtro: cuenta solo los estudios que cumplen ambos (esperado en el docstring del fixture) |
| P-002-24 | unit | US-002-4.4, FR-002-10, caso borde de año | FX-08 | Desde 2012 hasta 2020: cuenta 2015 y 2020; el estudio con año no reconocido no cumple el filtro activo y sí se cuenta sin él |
| P-002-25 | navegador | US-002-4.5, FR-002-12 | FX-09 | Ocultar un nivel en la leyenda no cambia cifras ni notas; tras «Actualizar vista», el control de nivel refleja el cambio y cifras y notas se recalculan sin ese nivel |
| P-002-26 | integración | US-002-4.6, FR-002-18, FR-002-19 (parte del mapa) | FX-06 | Con un filtro activo, «Restablecer» deja el filtro de la sesión en `SIN_FILTRO` y la respuesta trae el mapa sin filtrar (3 estudios, sin «n de N») y los controles sin filtros, sin pasar por «Actualizar vista» |
| P-002-27 | integración | US-002-4.8, FR-002-11 | FX-07 | Académica y Territorial: cuenta los estudios con cualquiera de las dos; luego dos metodologías: solo los que además tienen una de ellas |
| P-002-28 | unit | US-002-4.9, FR-002-09 | FX-13 | Las opciones de tipo de fuente son los valores presentes en esa columna (orden según NC-P002-5) |
| P-002-29 | navegador | US-002-4.10, FR-002-19 | FX-06 | Dejar una sola fuente sin pulsar «Actualizar vista»: el mapa conserva sus conteos sin filtrar y no sale ninguna petición de filtrado |
| P-002-30 | unit | US-002-4.11, FR-002-12 | FX-09 | La leyenda tiene la entrada «Sin nivel»; ocultar uno de los dos niveles deja contado al estudio sin nivel; solo sale al ocultar «Sin nivel» |
| P-002-31 | unit | US-002-4.12, FR-002-12 | FX-10 | El estudio con nivel «No aplica…» se cuenta en «Sin nivel» y la leyenda muestra esa entrada |
| P-002-32 | unit | US-002-4.13, FR-002-19 | FX-11 | Todos los valores de tipo de fuente seleccionados: el filtro no queda activo, se cuentan los 3 estudios y no se muestra «n de N» |
| P-002-33 | unit | caso borde de campo vacío | FX-11 | Con un solo tipo de fuente seleccionado, el estudio con la celda vacía no cumple y «n de N» lo refleja |
| P-002-34 | integración | US-002-4.14, FR-002-12 (parte del mapa) | FX-12 | Antes de ocultarla, la leyenda del mapa muestra «Sin nivel» con 0 estudios en el mapa; tras ocultarla y «Actualizar vista», el mapa sigue contando los 2 estudios. La cifra de documentos «2 de 3» del tablero la prueba el plan 003 (P-003-58) |
| P-002-35 | unit | FR-002-19, contrato §5 (regla de activo) | FX-08, FX-11 | `normalizar` devuelve `None` en un control que no deja fuera ningún valor o que cubre el rango completo de años, y el conjunto o el rango cuando deja fuera algo; `activos` nombra solo los controles activos |
| P-002-36 | integración | US-001-4.10, parte del mapa (NC-P002-1) | FX-06 y FX-07 | Con un filtro aplicado, una carga nueva válida deja el mapa del archivo nuevo sin filtros y ningún filtro activo; la parte del tablero la prueba el plan 003 (P-003-66) |
| P-002-37 | propiedades | SC-002-03, SC-002-01 | estrategias de T-002-03 | En todas las combinaciones de filtros de una matriz sintética, «n de N» y cada celda coinciden con un recálculo independiente escrito en la prueba desde las fórmulas del contrato §5 ($S_\varphi$, $n$ sobre $M$, $N = \lvert M \rvert$) |
| P-002-38 | navegador | US-001-5.5 (NC-P002-1) | FX-06 | A 44 minutos sin interacción, pulsar un filtro reinicia la cuenta y la sesión no termina a los 45 |

- [ ] T-002-17 [P] [US-002-4] [IMP] Escribir P-002-23, P-002-24, P-002-28, P-002-30 a P-002-33 y P-002-35 en
  `tests/unit/test_filtros.py`, y P-002-37 en `tests/propiedades/test_filtros.py`.
- [ ] T-002-18 [P] [US-002-4] [IMP] Escribir P-002-20 a P-002-22, P-002-26, P-002-27, P-002-34 y P-002-36 en
  `tests/integracion/test_filtros_mapa.py`.
- [ ] T-002-19 [P] [US-002-4] [IMP] Escribir P-002-25, P-002-29 y P-002-38 en `tests/navegador/test_filtros.py`.

### Implementación de la historia 4

- [ ] T-002-20 [US-002-4] [IMP] Implementar en M06 `opciones`, `normalizar`, `cumple_estudio` y `activos`: valores de la lista o,
  sin lista, los presentes; nivel con «Sin nivel» cuando haya estudios del mapa sin nivel o con nivel «No aplica…», o
  documentos no empíricos (FR-002-12, decisión del 21-nov-2026); rango de años con los años reconocidos de la matriz;
  regla de activo del contrato §5; celda vacía que no cumple un filtro activo, salvo «Sin nivel»; conjunción. Un estudio
  empírico pendiente sin nivel no se trata como «Sin nivel» (NC-INT-2). Requisitos: FR-002-09 a FR-002-13, FR-002-19.
  Pruebas: P-002-23, P-002-24, P-002-28, P-002-30 a P-002-33, P-002-35, P-002-37. Módulos: M06. Archivos: `src/egm/filtros.py`.
- [ ] T-002-21 [US-002-4] [IMP] Ampliar M10 con el resumen legible de los filtros aplicados («Mostrando solo …: n de N estudios
  del mapa»), el mensaje de mapa vacío por filtros y el texto fijo de E6 junto a los botones. Requisitos: FR-002-13,
  FR-002-14, FR-002-19. Pruebas: P-002-20 a P-002-22. Módulos: M10. Archivos: `src/egm/textos.py`.
- [ ] T-002-22 [US-002-4] [IMP] Ampliar M17 con el modelo de vista de filtros y leyenda: controles marcados con lo aplicado,
  leyenda = control de nivel con muestra y cuenta en el mapa, entrada «Sin nivel» y su nota sobre el tablero, resumen
  y «n de N» solo con filtros activos; los valores de cada control se envían por posición, nunca por su texto. La
  leyenda muestra siempre lo último aplicado. Requisitos: FR-002-09, FR-002-12, FR-002-13, FR-002-14. Pruebas:
  P-002-20, P-002-21, P-002-30, P-002-34. Módulos: M17. Archivos: `app/presentacion.py`.
- [ ] T-002-23 [US-002-4] [IMP] Agregar en M14 las rutas «Actualizar vista» (normaliza la selección con M06, la guarda en M15 y
  devuelve en una sola respuesta mapa, avisos, resumen y filtros) y «Restablecer» (guarda `SIN_FILTRO` y devuelve de
  inmediato la vista sin filtros), ambas por envío de formulario, comunes al mapa y al tablero. Requisitos: FR-002-15,
  FR-002-18, FR-002-19. Pruebas: P-002-20, P-002-26, P-002-27, P-002-36. Módulos: M14 (consume M06, M15). Archivos: `app/servidor.py`.
- [ ] T-002-24 [US-002-4] [DF] Escribir en M18 el fragmento «Filtros y leyenda» con los cuatro controles, la leyenda con muestra de
  tono y borde, «Desde» y «Hasta», un solo «Actualizar vista» y un solo «Restablecer», el texto de E6 y la frase de
  resumen siempre visible; usa formularios y botones reales de HTML que htmx envía con la ficha de sesión, sin recargar la página (ADR-003, puntos 2 y 4). Requisitos: FR-002-12,
  FR-002-13, FR-002-19, NFR-000-04. Pruebas: P-002-25, P-002-29. Módulos: M18. Archivos: `app/plantillas/`, `app/estaticos/`.
- [ ] T-002-25 [US-002-4] [DF] Implementar en M19 el paso del foco a la frase de resumen y su anuncio tras cada «Actualizar vista»
  o «Restablecer». Requisitos: NFR-000-04. Pruebas: P-002-25 (P-002-68, de la fase 8, lo vuelve a comprobar). Módulos: M19. Archivos: `app/cliente/`.

**Punto de control**: mapa con filtros de punta a punta. El implementador se detiene y resume.

---

## Fase 5: Historia 2 — Ver los estudios de una celda (prioridad: P2)

**Objetivo**: abrir un cajón y ver sus fichas en el margen; abrir la ficha completa de un estudio; volver al mapa con
el mismo filtro.

**Prueba independiente**: seleccionar cajones y comparar su lista con los N.º esperados.

### Pruebas de la historia 2 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-39 | integración | US-002-2.1, FR-002-05 | matriz vigente de `data/raw/` en modo lectura, con huella comprobada | Acompañamiento técnico × Humano: 1 estudio, N.º 7, nivel evaluación de impacto (apéndice A); la ficha del cajón trae referencia y año no vacíos; la huella no cambia |
| P-002-40 | unit | US-002-2.1, FR-002-05, SC-000-02 | FX-14 | Cada estudio del cajón con N.º, referencia, año y nivel escritos a mano en el docstring del fixture, en el orden del archivo |
| P-002-41 | unit | US-002-2.2, FR-002-06 | FX-14 | La referencia con DOI y la que tiene URL ofrecen un enlace; la que no tiene ninguno, no (destino del DOI según NC-P002-4) |
| P-002-42 | integración | US-002-2.3, FR-002-04, FR-002-14 | FX-06 | Un cajón sin estudios dice «ningún estudio registrado» con la nota de brecha provisional; con un filtro activo, el rótulo con filtros y nunca «brecha» |
| P-002-43 | unit | US-002-2.4, FR-002-07 | FX-14 | La ficha muestra tal cual país y población, dimensiones evaluadas, indicadores, hallazgos, vacío, limitaciones y aporte; los caracteres especiales llegan escapados y sin alteración visible |
| P-002-44 | integración | US-002-2.4, FR-002-07 | `instancia_ejemplo.xlsx` (FX-A del plan 001) | Al abrir el N.º 7 se ven, tal cual, los siete textos escritos a mano en el docstring de FX-A |
| P-002-45 | integración | US-002-4.7, FR-002-15 | FX-06 | Con un filtro activo, abrir un cajón, abrir la ficha y volver al mapa: el mismo filtro sigue activo y el mismo cajón seleccionado |
| P-002-46 | navegador | SC-002-02 | FX-14 | Desde el mapa, seleccionar un cajón muestra la referencia; abrir la fuente es la segunda acción |
| P-002-47 | integración | regla de M14 (URL por posición), NFR-000-17 | FX-14 | Las URL del cajón y de la ficha solo llevan posiciones numéricas, ningún texto de la matriz |
| P-002-48 | navegador | US-001-5.6 (NC-P002-1) | FX-14 | A 44 minutos sin interacción, abrir el detalle de un estudio reinicia la cuenta y la sesión no termina a los 45 |

- [ ] T-002-26 [P] [US-002-2] [IMP] Escribir P-002-40, P-002-41 y P-002-43 en `tests/unit/test_vista_cajon.py`.
- [ ] T-002-27 [P] [US-002-2] [IMP] Escribir P-002-39, P-002-42, P-002-44, P-002-45 y P-002-47 en `tests/integracion/test_cajon.py`.
- [ ] T-002-28 [P] [US-002-2] [IMP] Escribir P-002-46 y P-002-48 en `tests/navegador/test_cajon.py`.

### Implementación de la historia 2

- [ ] T-002-29 [US-002-2] [IMP] Implementar `vista_cajon` y `vista_ficha` en M17: estudios de la celda por posición $(i, j)$ con
  el filtro aplicado (la lista de la celda de M07), con N.º, referencia, año, nivel y tipo de fuente; enlace cuando la
  referencia contiene un DOI o una URL; textos tal cual de `Documento.textos`; rótulos de cajón vacío con y sin
  filtros. Requisitos: FR-002-04 a FR-002-07, FR-002-14. Pruebas: P-002-39 a P-002-44. Módulos: M17. Archivos: `app/presentacion.py`.
- [ ] T-002-30 [US-002-2] [IMP] Agregar en M14 las rutas de abrir cajón y de ficha de estudio, por posición, que devuelven el
  fragmento del margen o la página de la ficha y conservan el filtro aplicado. Requisitos: FR-002-05, FR-002-15.
  Pruebas: P-002-45, P-002-47. Módulos: M14. Archivos: `app/servidor.py`.
- [ ] T-002-31 [US-002-2] [DF] Escribir en M18 el fragmento del margen con las fichas (rayado de ficha, línea roja de selección
  en el cajón, único movimiento desde el margen con `prefers-reduced-motion`, margen bajo la cajonera en móvil) y la
  página de la ficha desde `estudio.html`, con «Volver al mapa». Requisitos: FR-002-05, FR-002-07, SC-002-02, NFR-000-05,
  NFR-000-13. Pruebas: P-002-46. Módulos: M18. Archivos: `app/plantillas/`, `app/estaticos/`.
- [ ] T-002-32 [US-002-2] [DF] Implementar en M19 el paso del foco al título del margen y su anuncio al abrir un cajón, y el
  regreso del foco al cajón al volver al mapa. Requisitos: NFR-000-04. Pruebas: P-002-46 (P-002-68, de la fase 8, lo vuelve a comprobar). Módulos: M19. Archivos:
  `app/cliente/`.

**Punto de control**: las historias 1, 4 y 2 funcionan cada una por separado. El implementador se detiene y resume.

---

## Fase 6: Historia 3 — Consultar definiciones (prioridad: P3)

**Objetivo**: al seleccionar el nombre de una fila o columna, el margen muestra la definición del equipo o
«definición no disponible».

**Prueba independiente**: seleccionar cada encabezado con y sin archivo de definiciones.

### Pruebas de la historia 3 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-49 | unit | US-002-3.1, FR-002-08 | FX-17 | La definición de una intervención y la de una dimensión se devuelven tal cual; el nombre se empareja tras quitar espacios en los extremos (ADR-004, punto 4) |
| P-002-50 | unit | US-002-3.2, FR-002-08 | FX-17 y FX-03 | Una categoría sin encabezado en el archivo devuelve «no disponible» y el mapa se dibuja completo |
| P-002-51 | integración | US-002-3.3, FR-002-08 | sin archivo de definiciones | Todo encabezado muestra «definición no disponible» y el mapa sigue funcionando; la configuración sin ruta de definiciones no falla |
| P-002-52 | integración | US-002-3.1, FR-002-08 | FX-17 | Seleccionar el nombre de una fila muestra en el margen su texto, sin alteraciones |

- [ ] T-002-33 [P] [US-002-3] [IMP] Escribir P-002-49 y P-002-50 en `tests/unit/test_definiciones.py`, y P-002-51 y P-002-52 en
  `tests/integracion/test_definiciones.py`.

### Implementación de la historia 3

- [ ] T-002-34 [US-002-3] [IMP] Implementar M12 `cargar` y `Definiciones.de` según ADR-004, punto 4 (sintaxis del encabezado según
  NC-P002-3). Requisitos: FR-002-08. Pruebas: P-002-49, P-002-50. Módulos: M12. Archivos: `src/egm/definiciones.py`.
- [ ] T-002-35 [US-002-3] [IMP] Ampliar M22 con la ruta del archivo de definiciones, leída al arrancar y opcional. Requisitos:
  FR-002-08. Pruebas: P-002-51. Módulos: M22. Archivos: `app/configuracion.py`.
- [ ] T-002-36 [US-002-3] [IMP] Implementar `vista_definicion` en M17 y su ruta en M14, por posición de fila o columna.
  Requisitos: FR-002-08. Pruebas: P-002-51, P-002-52. Módulos: M17, M14. Archivos: `app/presentacion.py`, `app/servidor.py`.
- [ ] T-002-37 [US-002-3] [DF] Convertir en M18 los nombres de filas y columnas en botones (subrayado punteado) que abren la
  definición en el margen, sin romper el patrón `grid`. Requisitos: FR-002-08, NFR-000-04. Pruebas: P-002-52 (P-002-68, de la fase 8, lo vuelve a comprobar).
  Módulos: M18. Archivos: `app/plantillas/`, `app/estaticos/`.

**Punto de control**: la historia 3 funciona de forma independiente. El implementador se detiene y resume.

---

## Fase 7: Historia 5 — Exportar (prioridad: P3)

**Objetivo**: descargar el mapa visible como imagen PNG (y SVG adicional) y los conteos como `.xlsx`, con los filtros
aplicados, el archivo y la fecha de lectura.

**Prueba independiente**: descargar los tres formatos con y sin filtros y compararlos con el mapa visible.

### Pruebas de la historia 5 (se escriben primero y deben fallar)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-53 | unit | US-002-5.1, FR-002-16 | FX-02 | `imagen_mapa` devuelve un SVG en UTF-8 con las mismas filas, columnas, burbujas, números y rótulos que el modelo de vista, y una cabecera con los filtros, el nombre del archivo y la fecha de lectura |
| P-002-54 | unit | US-002-5.2, FR-002-16 | FX-06 con un filtro aplicado | `tabla_conteos` devuelve un `.xlsx` nuevo con, encima de la tabla, los filtros activos, el nombre del archivo y la fecha de lectura, y una fila por cajón con su conteo y su desglose por nivel |
| P-002-55 | unit | NFR-000-09 | FX-06 | Dos exportaciones de la misma vista dan el mismo SVG byte a byte y el mismo contenido de libro, con los metadatos del libro tomados de la fecha de lectura y no del reloj |
| P-002-56 | integración | FR-002-16, E6 | FX-06 | Con selecciones sin aplicar, las descargas llevan lo último aplicado |
| P-002-57 | navegador | US-002-5.1, FR-002-16, NC-INT-4 | FX-02 | «Descargar el mapa como imagen (PNG)» produce un PNG dibujado desde el SVG de M20, con la única petición de obtener ese SVG y sin otra petición de datos |
| P-002-58 | integración | NFR-000-17, NFR-000-01 | FX-06 | Las exportaciones no crean archivos en la carpeta temporal del sistema ni en la de la aplicación, y la matriz cargada no se escribe |
| P-002-59 | unit | NFR-000-07 | FX-06 | Ni el SVG ni el `.xlsx` contienen porcentajes |
| P-002-60 | propiedades | SC-002-05 | estrategias de T-002-03 | Con y sin filtros, la tabla exportada coincide celda a celda con el mapa visible: mismo número por cajón y por nivel |

- [ ] T-002-38 [P] [US-002-5] [IMP] Escribir P-002-53 a P-002-55 y P-002-59 en `tests/unit/test_exportacion.py`, P-002-56 y
  P-002-58 en `tests/integracion/test_exportacion.py`, P-002-60 en `tests/propiedades/test_exportacion.py` y P-002-57 en
  `tests/navegador/test_exportacion.py`.

### Implementación de la historia 5

- [ ] T-002-39 [US-002-5] [IMP] Implementar M20 `imagen_mapa` y `tabla_conteos` desde el mismo `VistaMapa` del mapa visible, en
  memoria; el libro es nuevo y nunca la matriz cargada. Requisitos: FR-002-16, NFR-000-09, SC-002-05. Pruebas: P-002-53 a P-002-55,
  P-002-58 a P-002-60. Módulos: M20. Archivos: `app/exportacion.py`.
- [ ] T-002-40 [US-002-5] [IMP] Agregar en M14 las rutas de descarga del SVG y del `.xlsx`, que toman el filtro aplicado de la
  sesión. Requisitos: FR-002-16. Pruebas: P-002-56. Módulos: M14. Archivos: `app/servidor.py`.
- [ ] T-002-41 [US-002-5] [IMP] Implementar en M19 el control «descargar imagen»: pide el SVG de M20, lo dibuja tal cual y descarga
  el PNG, sin recalcular ni componer datos. Requisitos: FR-002-16. Pruebas: P-002-57. Módulos: M19. Archivos: `app/cliente/`.
- [ ] T-002-42 [US-002-5] [DF] Escribir en M18 la sección «Descargar» con los tres botones, su texto y el estado «Preparando la
  descarga.», y el estilo interno del SVG exportado con los tokens «Fichero». Requisitos: FR-002-16, NFR-000-13.
  Pruebas: P-002-57. Módulos: M18. Archivos: `app/plantillas/`, `app/estaticos/`.

**Punto de control**: todas las historias funcionan de forma independiente. El implementador se detiene y resume.

---

## Fase 8: Accesibilidad y diseño del mapa (transversal)

**Propósito**: las pruebas completas con teclado y con lector de pantalla que el `disenador-front` dejó para este plan
(`flujos.md` §8), la auditoría WCAG 2.2 AA, 360 px, escala de grises y la aprobación visual de Jairo.

### Pruebas (se escriben primero y deben fallar donde haya hallazgos)

| ID prueba | Tipo | Verifica | Fixture | Esperado |
|---|---|---|---|---|
| P-002-61 | navegador | SC-000-04, NFR-000-04 | FX-02, FX-05, FX-06 con filtro | La revisión automática de accesibilidad no deja hallazgos de nivel AA en el mapa, el cajón abierto, la ficha, la definición, el mapa vacío y el mapa con filtros, en claro y oscuro |
| P-002-62 | navegador | SC-000-05, NFR-000-05 | FX-03 | A 360 px la página no se desplaza en horizontal; la cajonera se recorre dentro de su recuadro con la columna de intervenciones fija |
| P-002-63 | navegador | SC-000-10, NFR-000-10 | FX-02, FX-09 | En escala de grises se leen el número de cada celda y el nivel (por borde y número), en claro y oscuro |
| P-002-64 | navegador | NFR-000-04 (movimiento) | FX-02 | Con `prefers-reduced-motion`, el cajón se abre sin desplazamiento |
| P-002-65 | manual (lector de pantalla, NC-P002-2) | NFR-000-04 | FX-02, FX-06 | Se anuncian la etiqueta de cada cajón («Acompañamiento técnico por Humano: 1 estudio, de evaluación de impacto» en la forma del catálogo), el resumen tras «Actualizar vista» y «Restablecer», la apertura del margen y la definición |
| P-002-66 | manual | SC-000-13, NFR-000-13 | FX-02, FX-06 | Capturas a 360 px y 1440 px, en claro y oscuro, de cada vista del mapa; Jairo aprueba cada una |
| P-002-67 | navegador | NFR-000-04 (foco visible) | FX-06 | Todo elemento que recibe foco lo muestra de forma visible y no queda tapado |
| P-002-68 | navegador | SC-002-04 | FX-06, FX-14, FX-17 | Solo con teclado: aplicar y quitar cada filtro, ocultar un nivel en la leyenda, «Actualizar vista», «Restablecer», abrir un cajón, abrir y cerrar una ficha, abrir una definición y las tres descargas |

- [ ] T-002-43 [IMP] Escribir P-002-61 a P-002-64, P-002-67 y P-002-68 en `tests/navegador/test_accesibilidad_mapa.py`.
- [ ] T-002-44 [DF] Escribir el guion de revisión manual de P-002-65 y P-002-66 (lista de pasos y vistas),
  ejecutarlo y registrar los hallazgos. Requisitos: NFR-000-04, NFR-000-13, SC-000-13. Módulos: M18. Archivos:
  `docs/interfaz/revision-manual-mapa.md`.
- [ ] T-002-45 [DF] Corregir en M18 y M19 los hallazgos de P-002-61 a P-002-68 sin cambiar el modelo de vista; si un
  hallazgo exige datos nuevos, detenerse y pedirlo al [IMP]. Requisitos: NFR-000-04, NFR-000-05, NFR-000-10,
  NFR-000-13. Pruebas: P-002-61 a P-002-68. Módulos: M18, M19. Archivos: `app/plantillas/`, `app/estaticos/`, `app/cliente/`.

**Punto de control**: accesibilidad y diseño aprobados. El implementador se detiene y resume.

---

## Fase 9: Cierre y aspectos transversales

- [ ] T-002-46 [IMP] Actualizar la columna «Prueba» y el estado `implementado` (regla de estados de `trazabilidad.md`) de `docs/specs/trazabilidad.md` para FR-002-01 a
  FR-002-19, SC-002-01 a SC-002-05 y las NFR-000 de este plan. La columna «Tarea» ya está llena desde la Fase 3. Requisitos: todos los del plan.
- [ ] T-002-47 [IMP] Limpieza sin cambiar comportamiento; `ruff` y `mypy --strict` sin errores; cobertura ≥ 90 % en
  `src/egm/`. Requisitos: —.
- [ ] T-002-48 [P] [IMP] Agregar la prueba de importaciones de M06 y M12 (ninguna importa `app` ni bibliotecas web,
  arquitectura §4.1). Requisitos: NFR-000-14 (apoyo). Módulos: M06, M12. Archivos: la prueba de importaciones del plan 001.
- [ ] T-002-49 [DF] Revisar todos los textos fijos y del catálogo que muestra el mapa: de usted, sin jerga ni fórmulas,
  sin preguntas, sin «no investigado», sin «brecha» con filtros activos, sin porcentajes, ninguna tabla no comparable
  nombrada. Requisitos: NFR-000-03 (apoyo), NFR-000-08, FR-002-14. Módulos: M10, M18.
- [ ] T-002-50 [IMP] Solicitar la verificación al subagente `verificador`. No marcar el plan como terminado con
  hallazgos abiertos.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)**: depende del plan 001 (ver abajo).
- **Base (fase 2)**: depende de la fase 1; bloquea todas las historias.
- **Historias**: en este orden por el plazo: historia 1 (fase 3) → historia 4 (fase 4) → historia 2 (fase 5) →
  historia 3 (fase 6) → historia 5 (fase 7), una a la vez. Las fases 3 y 4 son el mínimo entregable (mapa con filtros
  de punta a punta).
- **Accesibilidad (fase 8)**: depende de las historias entregadas; P-002-17 ya cubre la cajonera desde la fase 3.
- **Cierre (fase 9)**: depende de las fases anteriores.

### Dependencias entre historias

- Historia 1: empieza tras la fase 2.
- Historia 4: empieza tras la historia 1 (filtra la cajonera); se prueba sola con sus fixtures.
- Historia 2: empieza tras la fase 2; P-002-45 (US-002-4.7) integra con la historia 4.
- Historia 3: independiente; usa la cajonera de la historia 1.
- Historia 5: usa el `VistaMapa` de las historias 1 y 4.

### Dependencias con otros planes y módulos (por la interfaz pública de la arquitectura)

Del **plan 001** (se ejecuta antes que este, un plan a la vez; este plan no lo replanifica):

- M23 `tests.constructor`: `MatrizSintetica` (constructor fluido), `.a_bytes()` y las estrategias de propiedades; este
  plan solo agrega casos (T-002-02, T-002-03). También los fixtures «no verificable» y «difiere» de US-001-3, y FX-A (`instancia_ejemplo.xlsx`). · pendiente
- M01 `egm.modelo`: `RefFila`, `Conteo`, `Documento`, `Corpus`, `Esquema`, `ResultadoLectura`, `Identificacion`,
  `SIN_NIVEL`, `EstadoDocumento`. · pendiente
- M04 `egm.esquema`: `Esquema` con `dimensiones`, `intervenciones`, `niveles`, `tipos_fuente` y `metodologias`
  (`Lista` con su origen). · pendiente
- M05 `egm.lectura`: `Documento` con `anio`, `tipo_fuente`, `metodologia`, `intervenciones`, `dimensiones`, `nivel`,
  `estado` y `textos`. · pendiente
- M07 `egm.conteo`: `conjuntos`, `mapa` y `evaluacion_impacto`, sin el parámetro de filtro. Este plan les agrega
  `filtro: Filtro = SIN_FILTRO` y el desglose por nivel (T-002-07). · pendiente
- M13 `egm.procesamiento.procesar`. · pendiente
- M10 `egm.textos`: textos de advertencias y de verificación, `fecha`, `ROTULOS`. · pendiente
- M14, M15, M17, M18, M19, M22: aplicación, rutas base y convención de URL por posición; almacén de sesiones con
  `crear`, `reemplazar`, `obtener` y reloj inyectable para la inactividad; plantilla base, cabecera corrida, avisos y
  colofón; guion de carga, ficha de sesión y actividad; configuración. · pendiente
- Herramientas de pruebas en navegador y de accesibilidad, y versiones de dependencias (ADR-003, puntos 1 y 8). ·
  pendiente
- Política de contenido de M14: debe permitir que M19 dibuje en el navegador el SVG obtenido del propio servidor para
  producir el PNG, sin recursos externos (riesgo R-3). · pendiente

Con el **plan 003** (depende de este):

- El 003 consume M06 (`Filtro`, `opciones`, `normalizar`, `cumple_estudio`, `activos`) y lo amplía con
  `cumple_documento` (FR-003-14); consume el filtro aplicado de M15, las rutas «Actualizar vista» y «Restablecer» de M14
  (comunes a las dos vistas) y el fragmento de cajonera y de filtros de M18 para el mapa del tablero.
- Quedan para el 003: la parte del tablero de US-002-4.6 (P-003-65) y de US-002-4.14 (P-003-58), y US-003-3.4, 5.1, 5.2, 5.4 y 5.5.

### Dentro de cada historia

- Pruebas primero: se escriben y se comprueba que fallan.
- Núcleo antes que modelo de vista; modelo de vista antes que plantilla.
- Historia en verde antes de la siguiente.

## Riesgos y decisiones abiertas

- **R-1. Interfaces del plan 001.** Si una interfaz del 001 difiere de la arquitectura, este plan no se adapta por su
  cuenta: el implementador se detiene y lo reporta (regla 11 de `CLAUDE.md`).
- **R-2. Frontera 002/003 en «Sin nivel».** La arquitectura dice que el 003 amplía M06 «con documentos y “Sin nivel” de
  no empíricos». Este plan hace aparecer la entrada en `opciones` cuando solo hay documentos no empíricos, porque lo pide
  FR-002-12 (US-002-4.14, parte del mapa), y deja `cumple_documento` al 003. Si Jairo prefiere otra frontera, se mueve
  T-002-20 en esa parte y P-002-34 al 003.
- **R-3. Política de contenido y PNG.** Dibujar el SVG en el navegador puede chocar con la política sin recursos
  externos que fija M14 (plan 001). Mitigación: el SVG se obtiene del propio servidor y se dibuja sin recursos externos;
  si la política lo impide, detenerse y reportarlo (ADR-003, punto 7).
- **R-4. Determinismo del `.xlsx`.** Las bibliotecas de hojas de cálculo suelen escribir la hora del reloj en los
  metadatos del libro. Mitigación: tomar los metadatos de la fecha de lectura (P-002-55; NFR-000-09).
- **R-5. Escala del radio.** $r \propto \sqrt{n}$ exige una constante de escala que quepa en el cajón. Propuesta: el
  `disenador-front` fija el radio máximo del cajón y M17 entrega $r = r_{\max} \sqrt{n / n_{\max}}$, con $n_{\max}$ el
  mayor conteo por nivel de la vista; se respeta la proporción entre burbujas de la misma vista (P-002-05).
- **R-6. Nombre del archivo del constructor.** Resuelto por COR-013: `tests/constructor.py` (M23 `tests.constructor`) en todos los documentos.
- **R-7. Plazo del 6-dic-2026.** Si el tiempo no alcanza, se entrega hasta la fase 5 con su accesibilidad (P-002-17 y
  la parte de la fase 8 que toca esas vistas) y la exportación queda para después, con aviso a Jairo.
- **NC-P002-1, decidido por Jairo el 22-nov-2026**: las pruebas de US-001-4.10 y US-001-5.4 a 5.6 viven solo en el plan 002.
- **NC-P002-2, decidido por Jairo el 22-nov-2026**: revisión manual con NVDA en Windows.
- **NC-P002-3, decidido por Jairo el 22-nov-2026**: en el archivo de definiciones, cada encabezado es una línea que empieza por «# » seguida del nombre exacto; el texto va hasta el siguiente encabezado.
- **NC-P002-4, decidido por Jairo el 22-nov-2026**: una referencia con DOI y sin URL enlaza a https://doi.org/ seguido del DOI; una URL escrita se enlaza tal cual.
- **NC-P002-5, decidido por Jairo el 22-nov-2026**: los valores presentes de un filtro sin lista salen en el orden de su primera aparición en el archivo.

## Definición de terminado

- [ ] Todas las pruebas del plan en verde; cobertura ≥ 90 % en `src/egm/` (`calidad-python`).
- [ ] `ruff` y `mypy --strict` sin errores.
- [ ] Cada requisito del apartado «Requisitos que cubre este plan» tiene tarea y prueba en `trazabilidad.md`.
- [ ] Cada número del mapa, del cajón y de las exportaciones es la longitud de su lista de N.º de la matriz.
- [ ] Ningún archivo de `data/raw/` ni `docs/fuentes/` modificado; la huella de la matriz vigente no cambia en P-002-04
  y P-002-39.
- [ ] Informe del `verificador` sin huecos ni excesos abiertos.
- [ ] Ninguna cifra de la lámina 7 en fixtures, esperados ni textos; ninguna mención de tablas no comparables en la
  interfaz.
- [ ] Conteos y nunca porcentajes en el mapa y en las exportaciones.
- [ ] Ningún atributo `style` en el HTML; ningún número fijo de columnas en la hoja de estilo.
- [ ] Con la configuración por defecto, el colofón de la página del mapa muestra solo «Datos» y la referencia a 3ie.
- [ ] Jairo aprueba cada vista del mapa (SC-000-13) y queda registrada la revisión con teclado y lector de pantalla.

## Notas

- La etiqueta [US-002-n] de cada tarea la vincula con su historia; las tareas [IMP] y [DF] indican
  quién las hace.
- Los commits los hace Jairo. Al terminar cada historia, el implementador se detiene y resume lo hecho.
- Si una tarea exige algo fuera del plan, detenerse y reportarlo; no ampliar el alcance.
- Las pruebas usan `data/fixtures/`; solo P-002-04 y P-002-39 abren `data/raw/`, en modo lectura y con control
  de huella, como pide `calidad-python`.
- Guion de revisión manual (T-002-44): `docs/interfaz/revision-manual-mapa.md`, fase 8.
